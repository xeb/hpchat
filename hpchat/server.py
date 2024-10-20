from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
import time
import code
from runtime import Runtime

app = Flask(__name__)
runtime = Runtime()
convo = runtime.create_convo()
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', None)
    if not text:
        raise Exception("You must ask for SOMETHING")
    
    sermon = "/Users/xeb/projects/hpchat/output/June 16, 2024 ｜ Jeff Maguire ｜ Harbor Point Church-segment.txt"
    print(f"Sermon: {sermon=}")
    formatted_system_prompt = runtime.format_system_prompt(sermon)
    print(f"formatted_system_prompt: {formatted_system_prompt=}")
    response = convo.prompt(text, system=formatted_system_prompt, stream=True)
    # print(response)
    # code.interact(local=locals())
    print("----")
    print("Streaming response:")
    chunks = []
    for chunk in response:
        print(chunk)
        chunks.append(chunk)

    return jsonify({"response": "".join(chunks)})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
