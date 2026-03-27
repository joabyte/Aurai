import os
import logging
from flask import Flask, render_template, request, jsonify
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración limpia del cliente
CLAUDE_API_KEY = os.environ.get("CLAUDE_KEY")

def get_client():
    if not CLAUDE_API_KEY:
        return None
    return anthropic.Anthropic(api_key=CLAUDE_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify({
        "api_key_configured": bool(CLAUDE_API_KEY),
        "system": "AURA_ONLINE" if CLAUDE_API_KEY else "AURA_OFFLINE"
    })

@app.route('/chat', methods=['POST'])
def chat():
    client = get_client()
    if not client:
        return jsonify({"res": "⚠️ Error: Configure CLAUDE_KEY en Render"}), 500
    
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "").strip()
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system="Eres AURA, un asistente avanzado. Llamas al usuario señor.",
            messages=[{"role": "user", "content": user_prompt}]
        )
        return jsonify({"res": response.content[0].text})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"res": "Error de conexión con el núcleo."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
