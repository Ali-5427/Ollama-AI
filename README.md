# Ollama AI Chatbot

A simple full-stack chatbot application:

- `frontend`: HTML/CSS/JS chat UI
- `backend`: Flask API that connects to either Ollama or Gemini

The frontend sends messages to `POST /api/chat` on the backend. The backend then calls your configured AI provider and returns the reply.

## Features

- Clean chat interface with conversation history
- Supports two model providers:
- `ollama` (local or cloud)
- `gemini` (Google GenAI)
- Supports both Ollama endpoints:
- `/api/chat` (messages format)
- `/api/generate` (prompt format)
- Optional Cloudflare/ngrok-compatible request headers for remote Ollama tunnels

## Project Structure

```text
chatbot1-main/
  backend/
    app.py
    requirements.txt
    .env            # create this locally (not committed)
  frontend/
    index.html
    static/
      css/style.css
      js/chat.js
```

## Backend Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Create `backend/.env` and set variables.
4. Run backend:

```bash
python backend/app.py
```

Backend runs at `http://127.0.0.1:5000` by default.

## Environment Variables

### Common

- `MODEL_PROVIDER` = `ollama` or `gemini`
- `MODEL_NAME` = model name for selected provider

### Ollama

- `OLLAMA_BASE_URL` (example: `http://127.0.0.1:11434` or your public tunnel URL)
- `OLLAMA_ENDPOINT` (`/api/chat` or `/api/generate`)
- `OLLAMA_API_KEY` (optional, if your endpoint requires bearer token)
- `OLLAMA_CF_ACCESS_CLIENT_ID` (optional, for Cloudflare tunnel bypass if needed)
- `OLLAMA_NGROK_SKIP_WARNING` (optional, usually `true` for ngrok setups)
- `OLLAMA_USER_AGENT` (optional, example `curl/7.68.0`)

### Gemini

- `GEMINI_API_KEY` (required when `MODEL_PROVIDER=gemini`)

## Example `.env` for Cloud Ollama (`/api/generate`)

```env
MODEL_PROVIDER=ollama
MODEL_NAME=qwen2.5:7b
OLLAMA_BASE_URL=https://your-public-url.trycloudflare.com
OLLAMA_ENDPOINT=/api/generate
OLLAMA_CF_ACCESS_CLIENT_ID=bypass
OLLAMA_NGROK_SKIP_WARNING=true
OLLAMA_USER_AGENT=curl/7.68.0
```

## Example `.env` for Local Ollama (`/api/chat`)

```env
MODEL_PROVIDER=ollama
MODEL_NAME=llama3.1
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_ENDPOINT=/api/chat
```

## Frontend Setup

The frontend is static. Open `frontend/index.html` in a browser or host it with any static server.

The API base URL is set in:

- `frontend/static/js/chat.js`

Current behavior:

- On `localhost` or `127.0.0.1`, it uses `http://127.0.0.1:5000`
- Otherwise, it uses the deployed backend URL currently in the file

If your backend URL changes, update `API_BASE_URL` in `chat.js`.

You can also override API URL at runtime from browser console:

```js
localStorage.setItem("CHAT_API_BASE_URL", "https://your-backend-url")
```

Reload the page after setting it.

## Deploy on Vercel (Frontend)

This repo includes `vercel.json` at project root to serve the frontend correctly:

- `/` -> `frontend/index.html`
- `/static/*` -> `frontend/static/*`

Notes:

- This Vercel setup deploys the static frontend.
- The Flask backend should be deployed separately (for example Render/Railway/VM), then point frontend to that backend URL.

## API Contract

Frontend sends:

```json
{
  "message": "user text",
  "history": [
    {"role": "user", "text": "Hi"},
    {"role": "assistant", "text": "Hello"}
  ]
}
```

Backend returns:

```json
{
  "reply": "model response"
}
```

## Troubleshooting

- `Error contacting model API`
- Check `OLLAMA_BASE_URL` and `OLLAMA_ENDPOINT`
- Check tunnel URL is still active
- Verify model exists on Ollama server
- `Server configuration error: GEMINI_API_KEY missing`
- Set `GEMINI_API_KEY` or switch to `MODEL_PROVIDER=ollama`
- Frontend shows network error
- Confirm backend is running and CORS is enabled
- Confirm `API_BASE_URL` in `chat.js` points to correct backend

## Security Notes

- Do not commit `.env` files.
- Keep API keys and private tunnel details in environment variables.
- Restrict public exposure of Ollama endpoints when possible.
