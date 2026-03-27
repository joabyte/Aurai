import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
# Aquí le decimos que busque la llave en el sistema, no en el texto
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_KEY"))

@app.route('/')
def home(): return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    p = request.json.get("prompt")
    try:
        r = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system="Eres AURA, una IA elegante. Llamas al usuario señor.",
            messages=[{"role": "user", "content": p}]
        )
        return jsonify({"res": r.content[0].text})
    except Exception as e:
        return jsonify({"res": "Error: Configure CLAUDE_KEY en Render"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)