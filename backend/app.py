import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend (Netlify / localhost) to call this API

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama").strip().lower()
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1").strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if MODEL_PROVIDER == "gemini" and not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set for Gemini provider.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "/api/chat").strip()
OLLAMA_CF_ACCESS_CLIENT_ID = os.getenv("OLLAMA_CF_ACCESS_CLIENT_ID", "").strip()
OLLAMA_NGROK_SKIP_WARNING = os.getenv("OLLAMA_NGROK_SKIP_WARNING", "").strip()
OLLAMA_USER_AGENT = os.getenv("OLLAMA_USER_AGENT", "").strip()

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant called Chatbot. "
    "Answer clearly and concisely. Use simple language and avoid very long paragraphs."
)

@app.route("/")
def home():
    # Just to test backend is up
    return jsonify(
        {
            "status": "ok",
            "message": f"Backend running with provider '{MODEL_PROVIDER}'",
            "model": MODEL_NAME,
        }
    )

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        conversation_text = SYSTEM_PROMPT + "\n\n"
        for turn in history:
            role = turn.get("role", "user")
            text = (turn.get("text") or "").strip()
            if not text:
                continue
            if role == "user":
                conversation_text += f"User: {text}\n"
            else:
                conversation_text += f"Assistant: {text}\n"
        conversation_text += f"User: {user_message}\nAssistant:"

        if MODEL_PROVIDER == "gemini":
            if not GEMINI_API_KEY or gemini_client is None:
                return jsonify({"error": "Server configuration error: GEMINI_API_KEY missing"}), 500

            response = gemini_client.models.generate_content(
                model=MODEL_NAME,
                contents=conversation_text,
            )
            bot_reply = (getattr(response, "text", "") or "").strip()
        elif MODEL_PROVIDER == "ollama":
            headers = {"Content-Type": "application/json"}
            if OLLAMA_API_KEY:
                headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
            if OLLAMA_CF_ACCESS_CLIENT_ID:
                headers["CF-Access-Client-Id"] = OLLAMA_CF_ACCESS_CLIENT_ID
            if OLLAMA_NGROK_SKIP_WARNING:
                headers["ngrok-skip-browser-warning"] = OLLAMA_NGROK_SKIP_WARNING
            if OLLAMA_USER_AGENT:
                headers["User-Agent"] = OLLAMA_USER_AGENT

            endpoint = OLLAMA_ENDPOINT if OLLAMA_ENDPOINT.startswith("/") else f"/{OLLAMA_ENDPOINT}"
            url = f"{OLLAMA_BASE_URL}{endpoint}"

            if endpoint.endswith("/api/generate"):
                response = requests.post(
                    url,
                    json={
                        "model": MODEL_NAME,
                        "prompt": conversation_text,
                        "stream": False,
                    },
                    headers=headers,
                    timeout=120,
                )
            else:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for turn in history:
                    role = turn.get("role", "user")
                    text = (turn.get("text") or "").strip()
                    if not text:
                        continue
                    if role not in ("user", "assistant"):
                        role = "user"
                    messages.append({"role": role, "content": text})
                messages.append({"role": "user", "content": user_message})

                response = requests.post(
                    url,
                    json={
                        "model": MODEL_NAME,
                        "messages": messages,
                        "stream": False,
                    },
                    headers=headers,
                    timeout=120,
                )

            response.raise_for_status()
            response_data = response.json()
            if endpoint.endswith("/api/generate"):
                bot_reply = (response_data.get("response", "") or "").strip()
            else:
                bot_reply = (
                    response_data.get("message", {}).get("content", "") or ""
                ).strip()
        else:
            return jsonify({"error": f"Unsupported MODEL_PROVIDER: {MODEL_PROVIDER}"}), 500

        if not bot_reply:
            bot_reply = "Sorry, I couldn't generate a reply."

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Error calling model API:", repr(e))
        return jsonify({"error": "Error contacting model API"}), 500


if __name__ == "__main__":
    app.run(debug=True)
