import os
import logging
from flask import Flask, render_template, request, jsonify
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cargamos la llave desde el entorno de Render
CLAUDE_API_KEY = os.environ.get("CLAUDE_KEY")

if not CLAUDE_API_KEY:
    logger.error("❌ CLAUDE_KEY no encontrada")
else:
    logger.info("✅ CLAUDE_KEY cargada correctamente")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify({
        "api_key_configured": bool(CLAUDE_API_KEY),
        "client_ready": client is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "").strip() if data else ""
        
        if not user_prompt:
            return jsonify({"res": "Escribe un mensaje, señor."})
            
        if client is None:
            return jsonify({"res": "⚠️ Error: La llave CLAUDE_KEY no está vinculada en Render."}), 500

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system="Eres AURA, un asistente profesional y elegante. Siempre llamas al usuario 'señor'.",
            messages=[{"role": "user", "content": user_prompt}]
        )
        return jsonify({"res": response.content[0].text})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"res": "Error interno del sistema"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)