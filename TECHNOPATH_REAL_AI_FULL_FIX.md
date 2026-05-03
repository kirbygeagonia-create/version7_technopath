# TechnoPath — Make Chatbot + FAQ 100% Real AI with User Learning

## What needs to be fixed (6 broken things)

1. `generate_reply(message)` ignores conversation history — no memory
2. Flask never fetches FAQs from Django — approved FAQs have zero effect on AI
3. Flask never logs conversations back to Django — `AIChatLog` is always empty
4. `FAQMakerAnalyzeView` calls `http://localhost:5187` — always fails on Render
5. `_generate_answer_template()` returns fake placeholder text — not real AI answers
6. CORS production domains are commented out — Flask blocks the live frontend

---

## File 1 — `chatbot_flask/app.py` (full rewrite of key functions)

### Step 1 — Add `requests` import and DJANGO_API_URL config at the top

After the existing imports, add:
```python
import requests
import threading

DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'https://technopath-backend.onrender.com')
```

### Step 2 — Fix CORS (uncomment production domains)

Replace the entire CORS block with:
```python
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "https://technopath-frontend.onrender.com",
    "https://technopath-frontend-or73.onrender.com",
], supports_credentials=True)
```

### Step 3 — Re-enable the rate limiter

Replace the commented-out limiter block with:
```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)
```

### Step 4 — Add FAQ cache (fetches approved FAQs from Django every 5 minutes)

Add this after the `CAMPUS_CONTEXT` string:
```python
_faq_cache = {'data': [], 'fetched_at': 0}

def get_live_faqs():
    import time
    now = time.time()
    if now - _faq_cache['fetched_at'] < 300:
        return _faq_cache['data']
    try:
        r = requests.get(f"{DJANGO_API_URL}/api/chatbot/faq/", timeout=5)
        if r.status_code == 200:
            data = r.json()
            _faq_cache['data'] = data if isinstance(data, list) else data.get('results', [])
            _faq_cache['fetched_at'] = now
    except Exception as e:
        print(f"[Chatbot] FAQ fetch failed: {e}")
    return _faq_cache['data']

def build_faq_block():
    faqs = get_live_faqs()
    if not faqs:
        return ''
    lines = ['\nAPPROVED CAMPUS FAQs (use these answers for matching questions):']
    for faq in faqs[:25]:
        q = faq.get('question', '').strip()
        a = faq.get('answer', '').strip()
        if q and a:
            lines.append(f"Q: {q}\nA: {a}")
    return '\n'.join(lines)
```

### Step 5 — Rewrite `generate_reply` to accept history and inject FAQs

Replace the entire `generate_reply` function:
```python
def generate_reply(message: str, history: list = None) -> str:
    if history is None:
        history = []
    if not OPENAI_ENABLED or not client:
        return generate_rule_based_reply(message)
    try:
        system_prompt = CAMPUS_CONTEXT + build_faq_block()
        messages = [{"role": "system", "content": system_prompt}]
        for turn in history[-10:]:
            role = turn.get('role', '')
            content = turn.get('content', '')
            if role in ('user', 'assistant') and content:
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
        print(f"[Chatbot] OpenAI error: {e}")
        return generate_rule_based_reply(message)
```

### Step 6 — Add background logger to Django

Add this function (runs in a background thread, never blocks the chat response):
```python
def log_to_django(user_message: str, bot_reply: str, is_successful: bool):
    def _post():
        try:
            requests.post(
                f"{DJANGO_API_URL}/api/chatbot/log/",
                json={
                    "user_query": user_message,
                    "ai_response": bot_reply,
                    "mode": "online" if OPENAI_ENABLED else "offline",
                    "is_successful": is_successful
                },
                timeout=5
            )
        except Exception as e:
            print(f"[Chatbot] Log failed: {e}")
    threading.Thread(target=_post, daemon=True).start()
```

### Step 7 — Update the `/chat` endpoint to use history and log to Django

Replace the entire `/chat` route:
```python
@app.route("/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "message is required"}), 400
    if len(message) > 1000:
        return jsonify({"error": "Message too long"}), 400

    reply = generate_reply(message, history)

    fallback_phrases = ["try asking", "i'm here to help", "contact the", "open the navigate"]
    is_successful = not any(p in reply.lower() for p in fallback_phrases)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply) VALUES (?, ?)",
            (message, reply),
        )
        conn.commit()

    log_to_django(message, reply, is_successful)

    return jsonify({"reply": reply, "mode": "online" if OPENAI_ENABLED else "offline"})
```

### Step 8 — Add `requests` to `chatbot_flask/requirements.txt`
```
requests>=2.31.0
```

---

## File 2 — `backend_django/apps/chatbot/views.py`

### Step 9 — Add a public chat log POST endpoint

Add this new class anywhere before `FAQMakerAnalyzeView`:
```python
class ChatLogCreateView(APIView):
    """Receives chat logs from Flask chatbot — no auth required (server-to-server)."""
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

### Step 10 — Fix `FAQMakerAnalyzeView` to use `FLASK_CHATBOT_URL` env var

In `FAQMakerAnalyzeView.post()`, find this line:
```python
flask_url = f"http://localhost:5187/analytics?days={days}"
```

Replace with:
```python
flask_base = os.environ.get('FLASK_CHATBOT_URL', 'https://technopath-chatbot-dyod.onrender.com')
flask_url = f"{flask_base}/analytics?days={days}"
```

Add `import os` at the top of the file if not already there.

### Step 11 — Replace `_generate_answer_template` with real OpenAI answer generation

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
        ctx = """You write FAQ answers for TechnoPath, a campus guide app for SEAIT (South East Asian Institute of Technology), Tupi, South Cotabato.
Campus facts: MST Building (4F, center) — CL1-CL10 labs on 3F. JST Building (4F, back). RST Building (3F, left of gate) — Registrar on 1F, Guidance/HR/Safety on 2F, IT on 3F. Library: ground floor left wing, Mon-Fri 8AM-6PM, Sat 8AM-12PM. Cafeteria between MST and Gymnasium, open 7AM-6PM.
Write a clear, specific 2-3 sentence answer. No placeholders. No [Admin:...] text. Write a complete, usable answer."""
        resp = ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ctx},
                {"role": "user", "content": f"Write an FAQ answer for this student question: {question}"}
            ],
            max_tokens=120,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[FAQMaker] OpenAI error: {e}")
        return f"[Please write an answer for: {question}]"
```

---

## File 3 — `backend_django/apps/chatbot/urls.py`

### Step 12 — Register the new log endpoint

Add to imports:
```python
from .views import ChatLogCreateView
```

Add to `urlpatterns`:
```python
path('log/', ChatLogCreateView.as_view(), name='chatlog-create'),
```

---

## File 4 — `render.yaml`

### Step 13 — Add `OPENAI_API_KEY` and `FLASK_CHATBOT_URL` to Django backend envVars

Under the `technopath-backend` service `envVars` section, add:
```yaml
- key: OPENAI_API_KEY
  sync: false
- key: FLASK_CHATBOT_URL
  value: https://technopath-chatbot-dyod.onrender.com
```

### Step 14 — Add chatbot Flask service with all required env vars

Add a new service block (if not already present):
```yaml
  - type: web
    name: technopath-chatbot
    runtime: python
    plan: free
    rootDir: chatbot_flask
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: DJANGO_API_URL
        value: https://technopath-backend.onrender.com
      - key: PYTHON_VERSION
        value: "3.11.0"
```

Also add `gunicorn` to `chatbot_flask/requirements.txt`:
```
gunicorn>=21.2.0
```

---

## How the learning loop works after these changes

```
User sends a message
      ↓
Flask receives message + conversation history
      ↓
Flask fetches approved FAQs from Django (cached 5 min)
      ↓
Flask calls OpenAI GPT with: system prompt + campus facts + approved FAQs + full history
      ↓
OpenAI replies with a real, context-aware answer
      ↓
Flask logs the conversation to Django in a background thread (non-blocking)
      ↓
AIChatLog table fills up with real data
      ↓
Admin clicks "Analyze" in FAQ Maker → FAQMakerAnalyzeView reads real logs
      ↓
OpenAI generates real suggested answers (no more placeholder text)
      ↓
Admin approves good suggestions → becomes a FAQEntry in the database
      ↓
Next time Flask fetches FAQs → new answer is in the AI prompt
      ↓
All future users get the correct answer automatically ✓
```

## After deploying

1. Set `OPENAI_API_KEY` manually in the Render dashboard for both `technopath-backend` and `technopath-chatbot` services.
2. Test: ask the chatbot "where is the library?" then follow up with "what time does it close?" — the AI should remember the context.
3. Test learning: ask a question the bot can't answer well, then go to Admin → FAQ Maker → Analyze. A real AI-generated suggestion should appear within seconds.
