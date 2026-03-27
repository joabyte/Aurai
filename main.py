
import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_KEY"))

@app.route('/')
def home(): return render_template('index.html')

@app.route('/status')
def status(): return jsonify({"api_key_configured": bool(os.environ.get("CLAUDE_KEY"))})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system="Eres AURA, un asistente avanzado. Llamas al usuario señor.",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"res": response.content[0].text})
    except Exception as e:
        return jsonify({"res": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
