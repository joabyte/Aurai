import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify({"ready": bool(os.environ.get("CLAUDE_KEY"))})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        r = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system="Eres AURA. Llamas al usuario señor.",
            messages=[{"role": "user", "content": data.get("prompt")}]
        )
        return jsonify({"res": r.content[0].text})
    except Exception as e:
        return jsonify({"res": f"Error: {str(e)}"}), 500
