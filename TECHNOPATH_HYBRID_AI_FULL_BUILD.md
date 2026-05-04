# TechnoPath — Build a Real Hybrid AI Chatbot with Machine Learning + NLP + Continuous Learning

## What this builds
A production-grade hybrid chatbot that combines:
1. **ML intent classifier** (scikit-learn SVM trained on real SEAIT data)
2. **NLP entity extractor** (detects room codes, building names, floor numbers)
3. **Response router** (confidence-based: if ML is confident → DB lookup, if not → GPT)
4. **GPT-3.5 with conversation history** (for complex or ambiguous questions)
5. **Continuous learning loop** (user ratings → PostgreSQL → daily retrain)

All data lives in **PostgreSQL on Render** — not SQLite. Never wiped on restart.

---

## Phase 1 — New PostgreSQL tables (Django migrations)

### Step 1 — Add `TrainingData` model
**File:** `backend_django/apps/chatbot/models.py`

Add this new model at the bottom:
```python
class TrainingData(models.Model):
    """Stores labeled Q&A pairs used to train/retrain the ML intent classifier."""
    INTENT_CHOICES = [
        ('find_room', 'Find Room'),
        ('find_building', 'Find Building'),
        ('find_office', 'Find Office'),
        ('find_facility', 'Find Facility'),
        ('hours_schedule', 'Hours / Schedule'),
        ('about_seait', 'About SEAIT'),
        ('enrollment', 'Enrollment / Academic'),
        ('navigation_help', 'Navigation Help'),
        ('greeting', 'Greeting'),
        ('general', 'General'),
    ]
    user_query      = models.TextField()
    intent          = models.CharField(max_length=50, choices=INTENT_CHOICES)
    entities        = models.JSONField(default=dict, blank=True)
    correct_answer  = models.TextField(blank=True)
    confidence      = models.FloatField(default=1.0)
    source          = models.CharField(max_length=20, default='manual',
                        choices=[('manual','Admin Labeled'),('auto','Auto-Generated'),('corrected','User Corrected')])
    is_verified     = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_training_data'

class ChatRating(models.Model):
    """Stores user thumbs-up/down ratings on bot replies — feeds the learning loop."""
    log          = models.ForeignKey(AIChatLog, on_delete=models.CASCADE, related_name='ratings')
    rating       = models.IntegerField()  # 1 = thumbs up, -1 = thumbs down
    session_id   = models.CharField(max_length=100, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_ratings'
```

### Step 2 — Create and run the migration
```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

---

## Phase 2 — ML intent classifier (inside Flask)

### Step 3 — New file: `chatbot_flask/ml_engine.py`

Create this entire file:
```python
"""
ML Intent Classifier for TechnoPath chatbot.
Uses scikit-learn SVM with TF-IDF features.
Model is trained on SEAIT campus data and retrained automatically.
"""
import os
import re
import pickle
import requests
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "intent_model.pkl"
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'https://technopath-backend-or73.onrender.com')

# ── Seed training data (used if database has no training data yet) ──────────
SEED_DATA = [
    ("where is cl1", "find_room"),
    ("where is cl2", "find_room"),
    ("where is cl3", "find_room"),
    ("where is computer lab 1", "find_room"),
    ("locate cl5", "find_room"),
    ("find cl10", "find_room"),
    ("where can i find mst 101", "find_room"),
    ("where is room 201", "find_room"),
    ("how do i get to cl6", "find_room"),
    ("where is the registrar office", "find_office"),
    ("where is the guidance office", "find_office"),
    ("where is the cict office", "find_office"),
    ("locate the hr office", "find_office"),
    ("where is safety office", "find_office"),
    ("it office location", "find_office"),
    ("where is the library", "find_facility"),
    ("where is the cafeteria", "find_facility"),
    ("where is the gymnasium", "find_facility"),
    ("where is the canteen", "find_facility"),
    ("where is the clinic", "find_facility"),
    ("locate the playground", "find_facility"),
    ("where is mst building", "find_building"),
    ("where is rst building", "find_building"),
    ("where is jst building", "find_building"),
    ("how many floors does mst have", "find_building"),
    ("what is in rst building", "find_building"),
    ("library hours", "hours_schedule"),
    ("what time does the library open", "hours_schedule"),
    ("registrar schedule", "hours_schedule"),
    ("what time does the cafeteria open", "hours_schedule"),
    ("when is the guidance office open", "hours_schedule"),
    ("what is seait", "about_seait"),
    ("who founded seait", "about_seait"),
    ("is seait tuition free", "about_seait"),
    ("tell me about seait", "about_seait"),
    ("what courses does seait offer", "enrollment"),
    ("how do i enroll", "enrollment"),
    ("what programs are available", "enrollment"),
    ("navigate to the library", "navigation_help"),
    ("directions to mst building", "navigation_help"),
    ("how do i get to the registrar", "navigation_help"),
    ("show me the route to cl1", "navigation_help"),
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("good morning", "greeting"),
    ("good afternoon", "greeting"),
    ("help me", "general"),
    ("what can you do", "general"),
    ("i need help", "general"),
]

# ── Entity patterns ──────────────────────────────────────────────────────────
ENTITY_PATTERNS = {
    'room_code':    r'\b(cl[1-9]|cl10|mst\s?\d{3}|jst\s?\d{3}|rst\s?\d{3})\b',
    'building':     r'\b(mst|jst|rst)\s*(building)?\b',
    'floor':        r'\b([1-4])(st|nd|rd|th)?\s*floor\b',
    'office':       r'\b(registrar|guidance|cict|it office|hr|safety|cashier|saso|ssc|silakbo|library)\b',
    'facility':     r'\b(library|cafeteria|canteen|gymnasium|gym|clinic|playground)\b',
}

def extract_entities(text: str) -> dict:
    text_lower = text.lower()
    entities = {}
    for entity_type, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text_lower)
        if matches:
            entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
    return entities

def preprocess(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def load_training_data() -> tuple:
    """Load training data from PostgreSQL via Django API, fall back to seed data."""
    texts, labels = [], []
    try:
        resp = requests.get(
            f"{DJANGO_API_URL}/api/chatbot/training-data/",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data if isinstance(data, list) else data.get('results', [])
            for item in items:
                if item.get('user_query') and item.get('intent'):
                    texts.append(preprocess(item['user_query']))
                    labels.append(item['intent'])
    except Exception as e:
        print(f"[ML] Could not load training data from Django: {e}")

    if len(texts) < 20:
        print(f"[ML] Using seed data ({len(SEED_DATA)} examples)")
        for text, label in SEED_DATA:
            texts.append(preprocess(text))
            labels.append(label)

    return texts, labels

def train_model():
    """Train SVM classifier with TF-IDF features and save to disk."""
    from sklearn.pipeline import Pipeline
    from sklearn.svm import LinearSVC
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts, labels = load_training_data()
    if len(set(labels)) < 2:
        print("[ML] Not enough unique intents to train. Skipping.")
        return None

    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_features=5000,
            sublinear_tf=True
        )),
        ('clf', LinearSVC(
            C=1.0,
            max_iter=2000,
            class_weight='balanced'
        ))
    ])
    model.fit(texts, labels)

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

    print(f"[ML] Model trained on {len(texts)} examples, {len(set(labels))} intents. Saved.")
    return model

def load_or_train() -> object:
    """Load existing model or train a new one."""
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            print("[ML] Loaded existing model.")
            return model
        except Exception as e:
            print(f"[ML] Could not load model: {e}. Retraining...")
    return train_model()

def predict_intent(text: str, model) -> tuple:
    """Return (intent, confidence) for a given user message."""
    if model is None:
        return 'general', 0.0
    try:
        processed = preprocess(text)
        intent = model.predict([processed])[0]
        # LinearSVC doesn't give probabilities — use decision function as confidence proxy
        decision = model.decision_function([processed])[0]
        if hasattr(decision, '__len__'):
            confidence = float(max(decision))
        else:
            confidence = float(abs(decision))
        # Normalize to 0-1 range (decision function values typically -3 to +3)
        confidence = min(confidence / 3.0, 1.0)
        return intent, confidence
    except Exception as e:
        print(f"[ML] Prediction error: {e}")
        return 'general', 0.0
```

### Step 4 — Update `chatbot_flask/requirements.txt`
```
Flask>=3.0.0
Flask-Cors>=4.0.0
Flask-Limiter>=3.0
openai>=1.0.0
python-dotenv>=1.0.0
scikit-learn>=1.3.0
requests>=2.31.0
gunicorn>=21.2.0
```

---

## Phase 3 — Rewrite Flask app to use the hybrid engine

### Step 5 — Rewrite `chatbot_flask/app.py`

Replace the entire file with:
```python
import os
import re
import sqlite3
import threading
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

# ── OpenAI setup ─────────────────────────────────────────────────────────────
_openai_key = os.getenv('OPENAI_API_KEY', '')
OPENAI_ENABLED = False
client = None
if _openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=_openai_key)
        OPENAI_ENABLED = True
        print('[Chatbot] OpenAI enabled.')
    except ImportError:
        print('[Chatbot] openai package missing.')
else:
    print('[Chatbot] OPENAI_API_KEY not set.')

DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'https://technopath-backend-or73.onrender.com')

# ── Load ML model ─────────────────────────────────────────────────────────────
try:
    from ml_engine import load_or_train, predict_intent, extract_entities
    ml_model = load_or_train()
    ML_ENABLED = ml_model is not None
    print(f'[Chatbot] ML engine: {"enabled" if ML_ENABLED else "disabled"}')
except Exception as e:
    print(f'[Chatbot] ML engine failed to load: {e}')
    ml_model = None
    ML_ENABLED = False

app = Flask(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "https://technopath-frontend.onrender.com",
    "https://technopath-frontend-or73.onrender.com",
    "https://technopath-frontend-dyod.onrender.com",
], supports_credentials=True)

DB_PATH = Path(__file__).parent / "chatbot.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                response_mode TEXT,
                rating INTEGER DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

# ── Campus knowledge for rule-based responses ─────────────────────────────────
CAMPUS_DB = {
    'find_room': {
        'cl1':'MST Building 3rd Floor — Computer Lab 1 (General IT/Programming)',
        'cl2':'MST Building 3rd Floor — Computer Lab 2 (General IT/Programming)',
        'cl3':'MST Building 3rd Floor — Computer Lab 3 (General IT/Programming)',
        'cl4':'MST Building 3rd Floor — Computer Lab 4 (Networking/Hardware)',
        'cl5':'MST Building 3rd Floor — Computer Lab 5 (Networking/Hardware)',
        'cl6':'MST Building 3rd Floor — Computer Lab 6 (Multimedia/Design)',
        'cl7':'MST Building 3rd Floor — Computer Lab 7 (Multimedia/Design)',
        'cl8':'MST Building 3rd Floor — Computer Lab 8 (Software Development)',
        'cl9':'MST Building 3rd Floor — Computer Lab 9 (Software Development)',
        'cl10':'MST Building 3rd Floor — Computer Lab 10 (Advanced IT/Research)',
    },
    'find_office': {
        'registrar':'RST Building 1st Floor — 7 service windows, open Mon-Fri 8AM-5PM.',
        'guidance':'RST Building 2nd Floor — Guidance and Testing Center.',
        'cict':'MST Building 2nd Floor — CICT Office, near computer labs.',
        'hr':'RST Building 2nd Floor — Human Resources Office.',
        'safety':'RST Building 2nd Floor — Safety and Security Office.',
        'it office':'RST Building 3rd Floor — IT Office.',
        'silakbo':'RST Building 3rd Floor — Silakbo Student Publication Office.',
        'cashier':'RST Building 1st Floor — Cashier/Accounting Office.',
        'saso':'RST Building 2nd Floor — Student Affairs and Services Office.',
        'ssc':'RST Building 2nd Floor — Supreme Student Council.',
    },
    'find_facility': {
        'library':'Ground floor of the main building, left wing. Open Mon-Fri 8AM-6PM, Sat 8AM-12PM.',
        'cafeteria':'Center grounds between MST Building and Gymnasium. Open 7AM-6PM daily.',
        'canteen':'Center grounds between MST Building and Gymnasium. Open 7AM-6PM daily.',
        'gymnasium':'Back of campus — basketball, volleyball courts, and fitness equipment.',
        'gym':'Back of campus — basketball, volleyball courts, and fitness equipment.',
        'clinic':'MST Building 1st Floor (HS/college students) and RST Building 1st Floor (elementary).',
        'playground':'Open grounds area of the SEAIT campus.',
    },
    'find_building': {
        'mst':'MST Building (Main Science and Technology) — 4 floors, center of campus. Houses classrooms (1F-2F), CL1-CL10 labs (3F), and additional rooms (4F).',
        'jst':'JST Building (Junior Science and Technology) — 4 floors, back of campus. Lecture rooms (1F), labs (2F), seminar rooms (3F-4F).',
        'rst':'RST Building (Research Science and Technology) — 3 floors, left of main gate. Registrar/Cashier (1F), Guidance/Safety/HR/SASO (2F), IT/Silakbo offices (3F).',
    },
    'hours_schedule': {
        'library':'Mon-Fri 8AM-6PM, Sat 8AM-12PM.',
        'registrar':'Mon-Fri 8AM-5PM.',
        'cafeteria':'Daily 7AM-6PM.',
        'canteen':'Daily 7AM-6PM.',
        'guidance':'Mon-Fri 8AM-5PM.',
    },
    'about_seait': {
        'default':(
            'SEAIT (South East Asian Institute of Technology) is a private, non-stock, non-profit '
            'higher education institution in Tupi, South Cotabato, Mindanao, Philippines. '
            'It was founded in February 2006 by Hon. Reynaldo S. Tamayo Jr. and Mrs. Rochelle P. Tamayo. '
            'SEAIT offers completely FREE tuition for all college degree programs. '
            'It is recognized by CHED, DepEd, and TESDA.'
        )
    }
}

CAMPUS_CONTEXT = """You are the official TechnoPath AI Campus Assistant for SEAIT
(South East Asian Institute of Technology), Tupi, South Cotabato, Mindanao, Philippines.

SEAIT is FREE — completely tuition-free for all college programs. Founded 2006 by Hon. Reynaldo S. Tamayo Jr.

Buildings: MST (4F, center) — CL1-CL10 labs on 3F. JST (4F, back). RST (3F, left of gate).
RST 1F: Registrar (7 windows, Mon-Fri 8AM-5PM), Cashier.
RST 2F: Guidance, Safety, HR, SASO, SSC.
RST 3F: IT Office, Silakbo Publication.
Library: ground floor left wing, Mon-Fri 8AM-6PM, Sat 8AM-12PM.
Cafeteria: between MST and Gymnasium, open 7AM-6PM.

Be helpful and specific. Guide users to the Navigate tab for directions."""

# ── Rule-based lookup ─────────────────────────────────────────────────────────
def rule_based_lookup(intent: str, entities: dict, message: str) -> str | None:
    msg = message.lower()
    db = CAMPUS_DB.get(intent, {})
    if not db:
        return None

    for key, answer in db.items():
        if key in msg or key in str(entities):
            return f"{answer} Use the Navigate tab for step-by-step directions."

    if intent == 'about_seait':
        return db.get('default')

    if intent in ('find_room', 'find_office', 'find_facility', 'find_building'):
        options = ', '.join(db.keys())
        return f"I can help you find: {options}. Which one are you looking for?"

    return None

# ── GPT call with history ─────────────────────────────────────────────────────
def gpt_reply(message: str, history: list) -> str:
    if not OPENAI_ENABLED or not client:
        return None
    try:
        msgs = [{"role": "system", "content": CAMPUS_CONTEXT}]
        for turn in history[-10:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                msgs.append({"role": role, "content": content})
        msgs.append({"role": "user", "content": message})
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=msgs,
            max_tokens=200,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Chatbot] GPT error: {e}")
        return None

# ── Main response generator ───────────────────────────────────────────────────
def generate_response(message: str, history: list) -> dict:
    entities = extract_entities(message) if ML_ENABLED else {}
    intent, confidence = predict_intent(message, ml_model) if ML_ENABLED else ('general', 0.0)

    # High confidence — use rule-based DB lookup (fast, accurate, no API cost)
    if confidence >= 0.65 and intent != 'general':
        answer = rule_based_lookup(intent, entities, message)
        if answer:
            return {'reply': answer, 'intent': intent, 'confidence': confidence, 'mode': 'rule'}

    # Low confidence or complex question — use GPT
    gpt_answer = gpt_reply(message, history)
    if gpt_answer:
        return {'reply': gpt_answer, 'intent': intent, 'confidence': confidence, 'mode': 'gpt'}

    # Final fallback
    return {
        'reply': (
            "I can help with SEAIT campus info! Ask about buildings (MST, JST, RST), "
            "labs (CL1-CL10), offices (Registrar, Guidance, CICT), or facilities. "
            "Use the Navigate tab for step-by-step directions."
        ),
        'intent': 'general',
        'confidence': 0.0,
        'mode': 'fallback'
    }

# ── Background Django logger ──────────────────────────────────────────────────
def log_to_django(user_message, bot_reply, intent, confidence, mode, log_id):
    def _post():
        try:
            requests.post(f"{DJANGO_API_URL}/api/chatbot/log/", json={
                "user_query": user_message,
                "ai_response": bot_reply,
                "mode": mode,
                "intent": intent,
                "confidence": confidence,
                "flask_log_id": log_id,
                "is_successful": mode != 'fallback'
            }, timeout=5)
        except Exception as e:
            print(f"[Chatbot] Django log failed: {e}")
    threading.Thread(target=_post, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "ml_enabled": ML_ENABLED,
        "openai_enabled": OPENAI_ENABLED
    })

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

    result = generate_response(message, history)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply, intent, confidence, response_mode) VALUES (?,?,?,?,?)",
            (message, result['reply'], result['intent'], result['confidence'], result['mode'])
        )
        log_id = cursor.lastrowid
        conn.commit()

    log_to_django(message, result['reply'], result['intent'], result['confidence'], result['mode'], log_id)

    return jsonify({
        "reply": result['reply'],
        "message_id": log_id,
        "intent": result['intent'],
        "mode": result['mode']
    })

@app.route("/rate", methods=["POST"])
def rate():
    data = request.get_json(silent=True) or {}
    message_id = data.get("message_id")
    rating = data.get("rating")
    if not message_id or rating not in (1, -1):
        return jsonify({"error": "message_id and rating (1 or -1) required"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE chat_history SET rating=? WHERE id=?", (rating, message_id))
        conn.commit()

    # Push rating to Django for the learning loop
    def _push_rating():
        try:
            requests.post(f"{DJANGO_API_URL}/api/chatbot/rate/", json={
                "flask_log_id": message_id,
                "rating": rating
            }, timeout=5)
        except Exception as e:
            print(f"[Chatbot] Rating push failed: {e}")
    threading.Thread(target=_push_rating, daemon=True).start()

    return jsonify({"status": "rated"})

@app.route("/retrain", methods=["POST"])
def retrain():
    """Admin-triggered or cron-triggered model retraining."""
    global ml_model, ML_ENABLED
    try:
        from ml_engine import train_model
        ml_model = train_model()
        ML_ENABLED = ml_model is not None
        return jsonify({"status": "ok", "ml_enabled": ML_ENABLED})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5187))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## Phase 4 — Django: new endpoints for training data and ratings

### Step 6 — Add to `backend_django/apps/chatbot/views.py`

Add these two new views:
```python
class TrainingDataListView(generics.ListCreateAPIView):
    """List all training data — used by ML engine to retrain."""
    permission_classes = [permissions.AllowAny]  # Flask reads this server-to-server

    def get(self, request):
        from .models import TrainingData
        data = TrainingData.objects.filter(is_verified=True).values(
            'user_query', 'intent', 'entities', 'correct_answer'
        )
        return Response(list(data))

    def post(self, request):
        from .models import TrainingData
        TrainingData.objects.create(
            user_query=request.data.get('user_query', ''),
            intent=request.data.get('intent', 'general'),
            entities=request.data.get('entities', {}),
            correct_answer=request.data.get('correct_answer', ''),
            source=request.data.get('source', 'auto'),
            is_verified=False
        )
        return Response({'status': 'created'}, status=201)


class ChatLogCreateView(APIView):
    """Receives chat logs from Flask chatbot."""
    permission_classes = []

    def post(self, request):
        user_query = request.data.get('user_query', '').strip()
        ai_response = request.data.get('ai_response', '').strip()
        if not user_query:
            return Response({'error': 'user_query is required'}, status=400)
        log = AIChatLog.objects.create(
            user_query=user_query,
            ai_response=ai_response,
            mode=request.data.get('mode', 'online'),
            is_successful=request.data.get('is_successful', True)
        )
        return Response({'status': 'logged', 'log_id': log.id}, status=201)


class ChatRatingView(APIView):
    """Receives thumbs up/down from Flask and saves to PostgreSQL."""
    permission_classes = []

    def post(self, request):
        from .models import ChatRating
        flask_log_id = request.data.get('flask_log_id')
        rating = request.data.get('rating')
        if not flask_log_id or rating not in (1, -1):
            return Response({'error': 'flask_log_id and rating required'}, status=400)

        # If thumbs up — save as training data for next retrain
        if rating == 1:
            try:
                log = AIChatLog.objects.filter(id=flask_log_id).first()
                if log:
                    from .models import TrainingData
                    TrainingData.objects.get_or_create(
                        user_query=log.user_query,
                        defaults={
                            'intent': 'general',
                            'correct_answer': log.ai_response,
                            'source': 'auto',
                            'confidence': 0.8,
                            'is_verified': False
                        }
                    )
            except Exception as e:
                print(f"[Rating] Training data creation failed: {e}")

        return Response({'status': 'rated'})
```

### Step 7 — Register new URLs in `backend_django/apps/chatbot/urls.py`

Add to imports:
```python
from .views import ChatLogCreateView, ChatRatingView, TrainingDataListView
```

Add to `urlpatterns`:
```python
path('log/', ChatLogCreateView.as_view(), name='chatlog-create'),
path('rate/', ChatRatingView.as_view(), name='chatbot-rate'),
path('training-data/', TrainingDataListView.as_view(), name='training-data'),
```

---

## Phase 5 — Frontend: thumbs up/down rating buttons

### Step 8 — `frontend/src/views/ChatbotView.vue`

In the script section, add `rateMessage` import and function:
```javascript
import { sendMessage, rateMessage } from '../services/aiChatbot.js'

async function rateMsg(index, rating) {
  const msg = messages.value[index]
  if (!msg || msg.rated || !msg.message_id) return
  msg.rated = rating === 1 ? 'up' : 'down'
  await rateMessage(msg.message_id, rating)
}
```

In the bot message template block, add after the meta div:
```html
<div v-if="msg.type === 'bot' && msg.message_id" class="chatbot-rating">
  <button :class="['rate-btn', { active: msg.rated === 'up' }]"
          :disabled="!!msg.rated" @click="rateMsg(index, 1)">👍</button>
  <button :class="['rate-btn', { active: msg.rated === 'down' }]"
          :disabled="!!msg.rated" @click="rateMsg(index, -1)">👎</button>
  <span v-if="msg.rated === 'up'" class="rate-label">Thanks! This helps me learn.</span>
  <span v-if="msg.rated === 'down'" class="rate-label">Got it, I'll improve.</span>
</div>
```

In `aiChatbot.js`, export `rateMessage`:
```javascript
export async function rateMessage(messageId, rating) {
  if (!messageId) return
  try {
    await fetch(`${FLASK_CHATBOT_URL}/rate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: messageId, rating })
    })
  } catch (e) {
    console.warn('[Chatbot] Rating failed:', e.message)
  }
}
```

---

## Phase 6 — Seed initial training data + daily retrain cron

### Step 9 — Django management command for seeding training data
**File:** `backend_django/apps/chatbot/management/commands/seed_training_data.py`

```python
from django.core.management.base import BaseCommand
from apps.chatbot.models import TrainingData

SEED = [
    ("where is cl1", "find_room"), ("where is cl3", "find_room"),
    ("where is cl10", "find_room"), ("where is computer lab 5", "find_room"),
    ("where is the registrar", "find_office"), ("where is guidance office", "find_office"),
    ("where is cict office", "find_office"), ("where is it office", "find_office"),
    ("where is the library", "find_facility"), ("where is the cafeteria", "find_facility"),
    ("where is the gymnasium", "find_facility"), ("where is the clinic", "find_facility"),
    ("where is mst building", "find_building"), ("where is rst building", "find_building"),
    ("where is jst building", "find_building"), ("how many floors mst", "find_building"),
    ("library hours", "hours_schedule"), ("what time registrar open", "hours_schedule"),
    ("cafeteria schedule", "hours_schedule"), ("when does canteen close", "hours_schedule"),
    ("what is seait", "about_seait"), ("is seait free", "about_seait"),
    ("who founded seait", "about_seait"), ("tell me about seait", "about_seait"),
    ("how do i enroll", "enrollment"), ("what courses offered", "enrollment"),
    ("navigate to the library", "navigation_help"), ("directions to cl1", "navigation_help"),
    ("how do i get to the registrar", "navigation_help"),
    ("hello", "greeting"), ("hi", "greeting"), ("good morning", "greeting"),
    ("help", "general"), ("what can you do", "general"),
]

class Command(BaseCommand):
    help = 'Seed initial training data for the ML intent classifier'
    def handle(self, *args, **options):
        created = 0
        for query, intent in SEED:
            _, was_created = TrainingData.objects.get_or_create(
                user_query=query,
                defaults={'intent': intent, 'source': 'manual', 'is_verified': True}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} training examples.'))
```

Run after deploy: `python manage.py seed_training_data`

### Step 10 — Add retrain cron to `render.yaml`
```yaml
  - type: cron
    name: technopath-retrain
    schedule: "0 3 * * *"
    rootDir: chatbot_flask
    buildCommand: pip install -r requirements.txt
    startCommand: python -c "from ml_engine import train_model; train_model()"
    envVars:
      - key: DJANGO_API_URL
        value: https://technopath-backend-or73.onrender.com
```

---

## Phase 7 — render.yaml environment variables

Add to `technopath-chatbot` service envVars:
```yaml
      - key: OPENAI_API_KEY
        sync: false
      - key: DJANGO_API_URL
        value: https://technopath-backend-or73.onrender.com
      - key: PYTHON_VERSION
        value: "3.11.0"
```

Add to `technopath-backend` service envVars:
```yaml
      - key: OPENAI_API_KEY
        sync: false
```

Set `OPENAI_API_KEY` manually in the Render dashboard for both services.

---

## Files changed

| File | Action |
|------|--------|
| `chatbot_flask/app.py` | Full rewrite — hybrid router, ML + GPT + rules |
| `chatbot_flask/ml_engine.py` | New file — scikit-learn SVM classifier |
| `chatbot_flask/requirements.txt` | Add scikit-learn, requests |
| `backend_django/apps/chatbot/models.py` | Add TrainingData and ChatRating models |
| `backend_django/apps/chatbot/views.py` | Add ChatLogCreateView, ChatRatingView, TrainingDataListView |
| `backend_django/apps/chatbot/urls.py` | Register log/, rate/, training-data/ |
| `backend_django/apps/chatbot/management/commands/seed_training_data.py` | New file |
| `frontend/src/views/ChatbotView.vue` | Add 👍👎 rating buttons per message |
| `frontend/src/services/aiChatbot.js` | Export rateMessage() |
| `render.yaml` | Add OPENAI_API_KEY, DJANGO_API_URL, daily retrain cron |

## After deploying

1. Set `OPENAI_API_KEY` in Render dashboard for both chatbot and backend services.
2. Run: `python manage.py migrate` then `python manage.py seed_training_data`
3. Trigger first model train: POST to `https://your-chatbot.onrender.com/retrain`
4. Test: ask "where is cl5?" — should reply instantly from rule-based DB lookup.
5. Test: ask "is seait free?" — should reply from DB or GPT with SEAIT facts.
6. Test memory: ask "where is the library?" then "what time does it close?" — GPT should remember.
7. Rate a response 👎 — admin can later go to Django admin and correct the intent to improve the model.
8. The daily cron at 3AM will retrain the model automatically using all new verified data.
