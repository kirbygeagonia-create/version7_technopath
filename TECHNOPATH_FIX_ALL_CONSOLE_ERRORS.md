# TechnoPath — Fix All Console Errors (Chatbot + FAQ AI)

## 7 errors to fix across 3 files. Work through them in order.

---

## Fix 1 — CORS blocked (Error 1) — most critical
**File:** `chatbot_flask/app.py`

Find the CORS block and replace it with this (adds ALL possible Render frontend URLs):
```python
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "https://technopath-frontend.onrender.com",
    "https://technopath-frontend-or73.onrender.com",
    "https://technopath-frontend-dyod.onrender.com",
    "https://technopath-backend.onrender.com",
    "https://technopath-backend-or73.onrender.com",
    "https://technopath-backend-dyod.onrender.com",
], supports_credentials=True)
```

---

## Fix 2 — Add OPENAI_API_KEY to render.yaml (Error 2)
**File:** `render.yaml`

Under the `technopath-chatbot` service `envVars` section, add:
```yaml
      - key: OPENAI_API_KEY
        sync: false
```

Then go to the Render dashboard → technopath-chatbot service → Environment → add
`OPENAI_API_KEY` with your actual OpenAI key value manually.
Also add it to `technopath-backend` service the same way for FAQ AI answers.

---

## Fix 3 — Re-enable rate limiter (Error 3)
**File:** `chatbot_flask/app.py`

Find the commented-out limiter block and replace it with:
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)
```

Then on the `/chat` route, add the decorator:
```python
@app.route("/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
```

---

## Fix 4 — Pass history to OpenAI (Error 4)
**File:** `chatbot_flask/app.py`

Replace the entire `generate_reply` function:
```python
def generate_reply(message: str, history: list = None) -> str:
    if history is None:
        history = []
    if not OPENAI_ENABLED or not client:
        return generate_rule_based_reply(message)
    try:
        messages = [{"role": "system", "content": CAMPUS_CONTEXT}]
        for turn in history[-10:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return generate_rule_based_reply(message)
```

Then update the `/chat` route to read and pass history:
```python
@app.route("/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])          # ← read history
    if not message:
        return jsonify({"error": "message is required"}), 400
    if len(message) > 1000:
        return jsonify({"error": "Message too long"}), 400

    reply = generate_reply(message, history)   # ← pass history

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply) VALUES (?, ?)",
            (message, reply),
        )
        conn.commit()

    # Log to Django in background (for FAQ learning)
    log_to_django(message, reply)

    return jsonify({"reply": reply, "mode": "online" if OPENAI_ENABLED else "offline"})
```

---

## Fix 5 — Flask logs to Django (Errors 5 & 7 — breaks learning loop)
**File:** `chatbot_flask/app.py`

Add these imports at the top of the file (after existing imports):
```python
import requests
import threading
```

Add `DJANGO_API_URL` config after `load_dotenv()`:
```python
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'https://technopath-backend-or73.onrender.com')
```

Add this function before the `/chat` route:
```python
def log_to_django(user_message: str, bot_reply: str):
    """Send chat log to Django in background thread — non-blocking."""
    def _post():
        try:
            requests.post(
                f"{DJANGO_API_URL}/api/chatbot/log/",
                json={
                    "user_query": user_message,
                    "ai_response": bot_reply,
                    "mode": "online" if OPENAI_ENABLED else "offline",
                    "is_successful": not any(
                        p in bot_reply.lower()
                        for p in ["try asking", "i'm here to help", "open the navigate"]
                    )
                },
                timeout=5
            )
        except Exception as e:
            print(f"[Chatbot] Django log failed: {e}")
    threading.Thread(target=_post, daemon=True).start()
```

Add `requests>=2.31.0` to `chatbot_flask/requirements.txt` if not already there.

Add `DJANGO_API_URL` to `render.yaml` under the chatbot service:
```yaml
      - key: DJANGO_API_URL
        value: https://technopath-backend-or73.onrender.com
```

---

## Fix 6 — Add Django log endpoint (needed for Fix 5)
**File:** `backend_django/apps/chatbot/views.py`

Add this new class anywhere before `FAQMakerAnalyzeView`:
```python
class ChatLogCreateView(APIView):
    """Receives chat logs from Flask — public endpoint (server-to-server)."""
    permission_classes = []

    def post(self, request):
        user_query = request.data.get('user_query', '').strip()
        ai_response = request.data.get('ai_response', '').strip()
        mode = request.data.get('mode', 'online')
        is_successful = request.data.get('is_successful', True)
        if not user_query:
            return Response({'error': 'user_query is required'}, status=400)
        AIChatLog.objects.create(
            user_query=user_query,
            ai_response=ai_response,
            mode=mode,
            is_successful=is_successful
        )
        return Response({'status': 'logged'}, status=201)
```

**File:** `backend_django/apps/chatbot/urls.py`

Add to imports:
```python
from .views import ChatLogCreateView
```

Add to `urlpatterns`:
```python
path('log/', ChatLogCreateView.as_view(), name='chatlog-create'),
```

---

## Fix 7 — Replace fake FAQ answers with real OpenAI (Error 6)
**File:** `backend_django/apps/chatbot/views.py`

Replace the entire `_generate_answer_template` method with:
```python
def _generate_answer_template(self, category, question):
    import os
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if not openai_key:
        return f"[Please write an answer for: {question}]"
    try:
        from openai import OpenAI
        ai = OpenAI(api_key=openai_key)
        campus = """You write FAQ answers for TechnoPath, the campus guide app for SEAIT
(South East Asian Institute of Technology), Tupi, South Cotabato, Philippines.
SEAIT is FREE — tuition-free for all college programs.
Buildings: MST (4F, center) — CL1-CL10 labs on 3F. JST (4F, back). RST (3F, near gate) — Registrar on 1F, Guidance/Safety/HR on 2F, IT on 3F.
Library: ground floor left wing, Mon-Fri 8AM-6PM, Sat 8AM-12PM.
Cafeteria between MST and Gymnasium, open 7AM-6PM.
Write a clear, specific 2-3 sentence answer. No placeholders. No [Admin:...] text."""
        resp = ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": campus},
                {"role": "user", "content": f"Write an FAQ answer: {question}"}
            ],
            max_tokens=120,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[FAQMaker] OpenAI error: {e}")
        return f"[Please write an answer for: {question}]"
```

Add `openai>=1.0.0` to `backend_django/requirements.txt` if not already there.

---

## Files changed

| File | Fixes |
|------|-------|
| `chatbot_flask/app.py` | Fix 1 (CORS), Fix 3 (limiter), Fix 4 (history), Fix 5 (Django logging) |
| `chatbot_flask/requirements.txt` | Add `requests>=2.31.0` |
| `render.yaml` | Fix 2 (OPENAI_API_KEY), Fix 5 (DJANGO_API_URL) |
| `backend_django/apps/chatbot/views.py` | Fix 6 (log endpoint), Fix 7 (real AI answers) |
| `backend_django/apps/chatbot/urls.py` | Fix 6 (register log/ URL) |

## After deploying

1. Set `OPENAI_API_KEY` manually in Render dashboard for both `technopath-chatbot`
   and `technopath-backend` services (never commit the key to the repo).
2. Test: open the chatbot, ask a question — header should show "AI Powered (GPT)".
3. Test memory: ask "where is the library?" then ask "what time does it close?" —
   the AI should remember the context from the first message.
4. Test learning: ask the bot a question it cannot answer well, go to Admin → FAQ Maker
   → click Analyze — real AI-generated suggestions should appear within seconds.
