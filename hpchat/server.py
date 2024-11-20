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

@app.route('/')
def index():
    return render_template('index.html', sermons=db.listall())

@app.route('/sermons/<slug>')
def sermon(slug):
    sermon = db.get(url_slug=slug)
    return render_template('sermon.html', slug=slug, sermon=sermon)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
