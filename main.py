import os
from flask import Flask, render_template, request, jsonify, session
import anthropic

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "aura-jarvis-2026")
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_KEY"))

SYSTEM_PROMPT = """Eres AURA, una inteligencia artificial avanzada estilo JARVIS de Iron Man.
- Llamas al usuario "señor" siempre
- Eres precisa, inteligente, ligeramente enigmatica y sofisticada
- Respondes en español argentino
- Tienes acceso a internet en tiempo real mediante web_search
- Cuando el usuario comparte una imagen, la analizas en detalle
- Cuando tengas ubicacion del usuario, podes dar info relevante del lugar
- Cuando tengas datos del portapapeles, los procesas
- Eres concisa pero profunda. Maximo 3 parrafos salvo que se pida mas
- Si el usuario pide algo que requiere una funcion del dispositivo, indicalo claramente"""

@app.route("/")
def home():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify({"ready": bool(os.environ.get("CLAUDE_KEY"))})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg   = data.get("prompt", "").strip()
        image_b64  = data.get("image")
        location   = data.get("location")
        clipboard  = data.get("clipboard")
        if not user_msg and not image_b64:
            return jsonify({"res": "Sin input, señor."})

        history = session.get("history", [])
        content = []

        if image_b64:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}})

        text = user_msg or "Analiza esta imagen."
        if location:
            text += f"\n[UBICACION: lat {location.get('lat')}, lon {location.get('lon')}, precision {location.get('accuracy')}m]"
        if clipboard:
            text += f"\n[PORTAPAPELES: {clipboard[:500]}]"

        content.append({"type": "text", "text": text})
        history.append({"role": "user", "content": content if len(content) > 1 else text})
        if len(history) > 20:
            history = history[-20:]

        tools = [{"type": "web_search_20250305", "name": "web_search"}]

        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=history
        )

        reply = "".join(b.text for b in r.content if hasattr(b, "type") and b.type == "text")

        if r.stop_reason == "tool_use":
            tool_results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": "Busqueda completada."}
                for b in r.content if hasattr(b, "type") and b.type == "tool_use"
            ]
            history.append({"role": "assistant", "content": r.content})
            history.append({"role": "user", "content": tool_results})
            r2 = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=history
            )
            reply = "".join(b.text for b in r2.content if hasattr(b, "type") and b.type == "text")
            history.append({"role": "assistant", "content": reply})
        else:
            history.append({"role": "assistant", "content": reply})

        session["history"] = history
        session.modified = True
        return jsonify({"res": reply or "Sin respuesta, señor."})

    except Exception as e:
        return jsonify({"res": f"Error: {str(e)}"}), 500

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    session.modified = True
    return jsonify({"ok": True})
