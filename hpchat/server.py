from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
import time
from runtime import Runtime
from pathlib import Path

app = Flask(__name__)
runtime = Runtime()
convo = runtime.create_convo()
CORS(app)

@app.route('/')
def index():
    parent_dir = Path(__file__).parent.parent
    output_dir = parent_dir / 'output'
    txt_files = list(output_dir.glob('*.txt')) 


    return render_template('index.html', sermons=txt_files)
    selected_file = txt_files[selected_index]    
    return str(selected_file.resolve())

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', None)
    if not text:
        raise Exception("You must ask for SOMETHING")
    response = convo.prompt(text)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
