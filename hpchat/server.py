from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
import time
import code
from runtime import Runtime
from pathlib import Path
from hpchat import db

app = Flask(__name__)
runtime = Runtime()
convo = runtime.create_convo()
CORS(app)

# Load events data from JSON file
def load_events():
    try:
        with open(Path(__file__).parent.parent / 'harborpoint_events.json', 'r') as f:
            events_data = json.load(f)
            return events_data["events"]
    except Exception as e:
        print(f"Error loading events: {e}")
        return []

# Get the 3 most recent events (those with nearest upcoming dates)
def get_recent_events(events, count=3):
    import re
    from datetime import datetime
    
    # Helper function to extract month and year from date string
    def parse_event_date(date_str):
        if not date_str:
            return None
        
        try:
            # For single date events like "26 April 2025"
            if "–" not in date_str and "‑" not in date_str:
                # Try to parse single date format
                for fmt in ["%d %B %Y", "%B %d %Y", "%d %b %Y"]:
                    try:
                        return datetime.strptime(date_str.strip(), fmt)
                    except ValueError:
                        continue
            
            # For date range events like "30 April – 18 June 2025"
            else:
                # Extract the start date (first part before the dash)
                start_date = re.split(r'–|‑', date_str)[0].strip()
                
                # If year is missing in the start date but present in the end date
                if re.search(r'\d{4}', start_date) is None and re.search(r'\d{4}', date_str) is not None:
                    year_match = re.search(r'\d{4}', date_str)
                    if year_match:
                        year = year_match.group(0)
                        start_date = f"{start_date} {year}"
                
                # Try different date formats
                for fmt in ["%d %B %Y", "%B %d %Y", "%d %b %Y"]:
                    try:
                        return datetime.strptime(start_date, fmt)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
        
        return None
    
    # Current date for comparison
    now = datetime.now()
    
    # Process events
    upcoming_events = []
    other_events = []
    
    for event in events:
        date_str = event.get("date")
        event_date = parse_event_date(date_str)
        
        if event_date and event_date >= now:
            # This is an upcoming event with a valid date
            upcoming_events.append((event, event_date))
        else:
            # This is either a past event or one without a parseable date
            other_events.append(event)
    
    # Sort upcoming events by date (soonest first)
    upcoming_events.sort(key=lambda x: x[1])
    
    # Extract just the event data from the sorted list
    sorted_upcoming = [event for event, _ in upcoming_events]
    
    # Prepare final result
    result = sorted_upcoming[:count]
    
    # If we don't have enough upcoming events, add other events
    if len(result) < count:
        result.extend(other_events[:count - len(result)])
    
    return result[:count]

@app.route('/')
def index():
    events = load_events()
    recent_events = get_recent_events(events)
    return render_template('index.html', sermons=db.listall(), events=recent_events)

@app.route('/sermons/<slug>')
def sermon(slug):
    sermon = db.get(url_slug=slug)
    return render_template('sermon.html', slug=slug, sermon=sermon)

# @app.route('/sermons_v2/<slug>')
# def sermon(slug):
#     sermon = db.get(url_slug=slug)
#     return render_template('sermon_v2.html', slug=slug, sermon=sermon)

@app.route('/chat', methods=['POST'])
def chat():
    print("----")
    data = request.get_json()
    text = data.get('text', None)
    print(data["slug"])
    if not text:
        raise Exception("You must ask for SOMETHING")
    
    # TODO: We need to take the slug from the data, and then lookup the right sermon
    sermon = db.get(url_slug=data["slug"])
    # print(sermon["file_path"])
    
    # sermon = "/Users/paulgustafson/working/hpchat/sermons/August 11, 2024 ｜ Harbor Point 10AM-segment.txt"
    print(f"Sermon: {sermon=}")
    formatted_system_prompt = runtime.system_prompt.format(sermon=sermon["transcript"])
    
    # print(f"formatted_system_prompt: {formatted_system_prompt=}")
    response = convo.prompt(text, system=formatted_system_prompt, stream=True)
    # print(response)
    # code.interact(local=locals())
    print("----")
    print("Streaming response:")
    chunks = []
    for chunk in response:
        # print(chunk)
        chunks.append(chunk)

    return jsonify({"response": "".join(chunks)})

@app.route('/search-events', methods=['POST'])
def search_events():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({"response": "Please enter a search term."})
    
    # Load all events
    all_events = load_events()
    
    # Create system instructions for events search
    system_prompt = """You are an events search assistant for Harbor Point Church.
    Your task is to search through the provided events data based on the user's query.
    
    INSTRUCTIONS:
    1. Analyze the user's query and find matching events.
    2. For each matching event, include:
       - The event title
       - The event date (if available)
       - A brief description (if relevant)
       - The event URL (always include this)
    3. Format your response as HTML that can be displayed directly on the website.
    4. Use <div>, <p>, <a>, and other HTML tags to create a clean, readable layout.
    5. Make links open in a new tab using target="_blank".
    6. If no events match the query, politely inform the user and suggest trying different keywords.
    7. Always provide the complete URL for any events you find.
    8. Only return events that are relevant to the query.
    9. IMPORTANT: Return ONLY the raw HTML. Do NOT wrap your response in markdown code blocks (```html). The output will be inserted directly into a webpage.
    10. STYLING: Format all links to events with this exact style: '<a href="[URL]" target="_blank" class="mt-1 text-xs text-primary hover:text-secondary">View Event</a>'. This will match the styling of the links in the main UI."""
    
    # Create a prompt with the query and all events data
    user_prompt = f"""Search query: "{query}"

Events data:
{json.dumps(all_events, indent=2)}

Please find events that match this search query. Format your response with raw HTML (no markdown code blocks), including links to the events that open in a new tab. Your HTML will be inserted directly into a webpage.

IMPORTANT STYLING: All links to events should use this exact HTML format:
'<a href="[EVENT_URL]" target="_blank" class="mt-1 text-xs text-primary hover:text-secondary">View Event</a>'
This ensures consistent styling with the rest of the page."""
    
    try:
        # Create a new conversation instance for this request
        search_convo = runtime.create_convo()
        
        # Get response from the model using non-streaming mode
        # We're collecting the entire response at once, not streaming
        result_text = ""
        for text in search_convo.prompt(user_prompt, system=system_prompt, stream=False):
            result_text += text
            
        # Remove markdown code block markers if present
        result_text = result_text.replace("```html", "").replace("```", "").strip()
        
        return jsonify({"response": result_text})
    except Exception as e:
        print(f"Error in search_events: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"<p>An error occurred while searching events. Please try again later.</p>"})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
