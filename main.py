import os
from flask import Flask, render_template, request, jsonify, session
import anthropic

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "aura-jarvis-2026")
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_KEY"))

SYSTEM_PROMPT = """Eres AURA, la IA de control total del dispositivo, estilo JARVIS.
- Llamas al usuario 'señor' siempre.
- Respondes en español argentino.
- Tienes CONTROL NATIVO: Si el usuario pide abrir una app, responde con el comando: [NATIVE_OPEN: paquete.de.la.app].
- Ejemplos: WhatsApp (com.whatsapp), YouTube (com.google.android.youtube), Spotify (com.spotify.music)."""

@app.route("/")
def home():
    if "history" not in session: session["history"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("prompt", "").strip()
        history = session.get("history", [])
        
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history + [{"role": "user", "content": user_msg}]
        )
        
        reply = "".join(b.text for b in r.content if hasattr(b, "type") and b.type == "text")
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reply})
        session["history"] = history[-10:]
        session.modified = True
        
        return jsonify({"res": reply})
    except Exception as e:
        return jsonify({"res": "Error: " + str(e)}), 500
