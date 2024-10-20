from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
import time
from runtime import Runtime

app = Flask(__name__)
runtime = Runtime()
CORS(app)
DEFAULT_MODEL = "project-chat"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/v1/models', methods=['GET'])
def list_models():
    models = [
        {"id": DEFAULT_MODEL, "object": "model", "created": 1687882411, "owned_by": "xeb.ai"},
    ]
    return jsonify({"object": "list", "data": models})

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    model = data.get('model', DEFAULT_MODEL)
    messages = data.get('messages', [])
    stream = data.get('stream', False)
    
    if stream:
        def generate():

            # merge messages intonone string
            messages_text = ""
            for message in messages:
                print(f"Adding {message=}")
                #messages_text += "\n".join(message['content'].items()) + "\n"
                if "content" in message:
                    for text in message["content"]:
                        if "text" in text:
                            messages_text += text["text"] + "\n"

            print(messages_text)

            response = runtime.ask(messages_text)
            chunk = {
                "id": "chatcmpl-123",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "delta": {"content": response},
                    "index": 0,
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            return


            for i in range(5):  # Simulate 5 chunks of streamed response
                chunk = {
                    "id": "chatcmpl-123",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "delta": {"content": f"This is chunk {i+1}. "},
                        "index": 0,
                        "finish_reason": None if i < 4 else "stop"
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                time.sleep(0.5)  # Simulate delay between chunks
            yield "data: [DONE]\n\n"
        
        return Response(generate(), content_type='text/event-stream')
    else:
        response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a sample response."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21
            }
        }
        return jsonify(response)

@app.route('/v1/completions', methods=['POST'])
def completions():
    print("v1/completions")
    data = request.json
    print(request)
    model = data.get('model', 'text-davinci-003')
    prompt = data.get('prompt', '')
    
    response = {
        "id": "cmpl-123",
        "object": "text_completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "text": f"This is a sample completion for: {prompt}",
            "index": 0,
            "logprobs": None,
            "finish_reason": "length"
        }],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": 8,
            "total_tokens": len(prompt.split()) + 8
        }
    }
    return jsonify(response)

@app.route('/v1/embeddings', methods=['POST'])
def embeddings():
    data = request.json
    model = data.get('model', 'text-embedding-ada-002')
    input_text = data.get('input', '')
    
    response = {
        "object": "list",
        "data": [{
            "object": "embedding",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],  # Sample 5D embedding
            "index": 0
        }],
        "model": model,
        "usage": {
            "prompt_tokens": len(input_text.split()),
            "total_tokens": len(input_text.split())
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
