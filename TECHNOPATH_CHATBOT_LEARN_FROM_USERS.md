# TechnoPath — Make Chatbot Learn From Users

## What's broken
The thumbs 👍👎 shown in the screenshot are **text inside the bot's reply** — they
are NOT real buttons. No rating system exists. Nothing is ever sent back to improve
the AI. Fix all of this with the 4 changes below.

---

## Change 1 — `chatbot_flask/app.py`

### 1a — Upgrade the SQLite table to track ratings
Replace `init_db()` with this version that adds a `rating` column and a
`learned_faqs` table:
```python
def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_reply    TEXT NOT NULL,
                rating       INTEGER DEFAULT NULL,  -- 1=thumbs up, -1=thumbs down, NULL=no rating
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learned_faqs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                question     TEXT NOT NULL,
                answer       TEXT NOT NULL,
                thumbs_up    INTEGER DEFAULT 0,
                thumbs_down  INTEGER DEFAULT 0,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
```

### 1b — Add conversation history + learned FAQs into the AI prompt

Replace `generate_reply(message)` with this version:
```python
def generate_reply(message: str, history: list = None) -> str:
    if history is None:
        history = []
    if not OPENAI_ENABLED or not client:
        return generate_rule_based_reply(message)
    try:
        # Load highly-rated learned FAQs from SQLite
        learned_context = ""
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT question, answer FROM learned_faqs WHERE thumbs_up > thumbs_down ORDER BY thumbs_up DESC LIMIT 20"
            ).fetchall()
            if rows:
                learned_context = "\n\nLEARNED FROM USER FEEDBACK (prioritize these answers):\n"
                for q, a in rows:
                    learned_context += f"Q: {q}\nA: {a}\n"

        messages = [{"role": "system", "content": CAMPUS_CONTEXT + learned_context}]
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

### 1c — Update the `/chat` endpoint to save the message ID and accept history

Replace the `/chat` route:
```python
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])
    if not message:
        return jsonify({"error": "message is required"}), 400
    if len(message) > 1000:
        return jsonify({"error": "Message too long"}), 400

    reply = generate_reply(message, history)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply) VALUES (?, ?)",
            (message, reply),
        )
        message_id = cursor.lastrowid
        conn.commit()

    return jsonify({"reply": reply, "message_id": message_id})
```

### 1d — Add a `/rate` endpoint that saves the user's thumbs up/down

Add this new route after the `/chat` route:
```python
@app.route("/rate", methods=["POST"])
def rate():
    """Save user rating for a bot reply and auto-learn from thumbs-up answers."""
    data = request.get_json(silent=True) or {}
    message_id = data.get("message_id")
    rating = data.get("rating")  # 1 = thumbs up, -1 = thumbs down

    if not message_id or rating not in (1, -1):
        return jsonify({"error": "message_id and rating (1 or -1) required"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE chat_history SET rating = ? WHERE id = ?",
            (rating, message_id)
        )
        # If thumbs up — save this Q&A as a learned FAQ
        if rating == 1:
            row = conn.execute(
                "SELECT user_message, bot_reply FROM chat_history WHERE id = ?",
                (message_id,)
            ).fetchone()
            if row:
                question, answer = row
                existing = conn.execute(
                    "SELECT id, thumbs_up FROM learned_faqs WHERE question = ?",
                    (question,)
                ).fetchone()
                if existing:
                    conn.execute(
                        "UPDATE learned_faqs SET thumbs_up = thumbs_up + 1 WHERE id = ?",
                        (existing[0],)
                    )
                else:
                    conn.execute(
                        "INSERT INTO learned_faqs (question, answer, thumbs_up) VALUES (?, ?, 1)",
                        (question, answer)
                    )
        # If thumbs down — mark it as bad so it's not learned
        elif rating == -1:
            conn.execute(
                """UPDATE learned_faqs SET thumbs_down = thumbs_down + 1
                   WHERE question = (SELECT user_message FROM chat_history WHERE id = ?)""",
                (message_id,)
            )
        conn.commit()

    return jsonify({"status": "rated", "rating": rating})
```

---

## Change 2 — `frontend/src/services/aiChatbot.js`

### 2a — Store `message_id` from Flask response

In the `generateFlaskResponse` function, return both `reply` and `message_id`:
```javascript
async function generateFlaskResponse(userMessage) {
  const response = await fetch(`${FLASK_CHATBOT_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userMessage,
      history: conversationHistory.slice(-MAX_HISTORY)
    })
  })
  if (!response.ok) throw new Error(`Flask chatbot error: ${response.status}`)
  const data = await response.json()
  return { reply: data.reply, message_id: data.message_id || null }
}
```

### 2b — Return `message_id` from `sendMessage()`

In the `sendMessage` function, update the Flask branch and return:
```javascript
if (isOnline()) {
  try {
    const result = await generateFlaskResponse(userMessage)
    response = result.reply
    messageId = result.message_id   // save for rating
    source = 'flask'
  } catch (flaskErr) {
    console.warn('[Chatbot] Flask unavailable:', flaskErr.message)
    response = await generateRuleBasedResponse(userMessage)
    source = 'fallback'
  }
} else {
  response = await generateRuleBasedResponse(userMessage)
  source = 'offline'
}
// Add messageId to the return value
return { reply: response, source, isOffline: !isOnline(), message_id: messageId || null }
```

Add `let messageId = null` near the top of `sendMessage()`.

### 2c — Add a `rateMessage()` export function

Add this new exported function at the bottom of the file:
```javascript
export async function rateMessage(messageId, rating) {
  if (!messageId || !isOnline()) return
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

## Change 3 — `frontend/src/views/ChatbotView.vue`

### 3a — Store `message_id` on each bot message

In the `sendMessage` handler, update how bot messages are pushed to the `messages` array:
```javascript
const result = await sendMessage(userInput.value.trim())
messages.value.push({
  type: 'bot',
  text: result.reply,
  timestamp: new Date(),
  source: sourceLabel,
  message_id: result.message_id || null,   // ← add this
  rated: null                               // ← add this (null, 'up', or 'down')
})
```

### 3b — Add thumbs up/down buttons to every bot message in the template

Find this block in the template (the bot message div):
```html
<div :class="['chatbot-message', msg.type]">
  <div class="chatbot-message-content">{{ msg.text }}</div>
  <div class="chatbot-message-meta">
    <span class="chatbot-message-time">{{ formatTime(msg.timestamp) }}</span>
    <span v-if="msg.source" class="chatbot-message-source">{{ msg.source }}</span>
  </div>
</div>
```

Replace with:
```html
<div :class="['chatbot-message', msg.type]">
  <div class="chatbot-message-content">{{ msg.text }}</div>
  <div class="chatbot-message-meta">
    <span class="chatbot-message-time">{{ formatTime(msg.timestamp) }}</span>
    <span v-if="msg.source" class="chatbot-message-source">{{ msg.source }}</span>
  </div>
  <!-- Rating buttons — only on bot messages that came from Flask -->
  <div v-if="msg.type === 'bot' && msg.message_id" class="chatbot-rating">
    <button
      :class="['chatbot-rate-btn', { active: msg.rated === 'up' }]"
      :disabled="!!msg.rated"
      @click="rateMsg(index, 1)"
      title="This was helpful"
    >👍</button>
    <button
      :class="['chatbot-rate-btn', { active: msg.rated === 'down' }]"
      :disabled="!!msg.rated"
      @click="rateMsg(index, -1)"
      title="This was not helpful"
    >👎</button>
    <span v-if="msg.rated === 'up'" class="chatbot-rated-label">Thanks for the feedback!</span>
    <span v-if="msg.rated === 'down'" class="chatbot-rated-label">Got it, we'll improve!</span>
  </div>
</div>
```

### 3c — Add the `rateMsg` function in the script section

Import `rateMessage` at the top:
```javascript
import { sendMessage, rateMessage } from '../services/aiChatbot.js'
```

Add the function in the `setup` / `script setup` block:
```javascript
async function rateMsg(index, rating) {
  const msg = messages.value[index]
  if (!msg || msg.rated || !msg.message_id) return
  msg.rated = rating === 1 ? 'up' : 'down'
  await rateMessage(msg.message_id, rating)
}
```

### 3d — Add CSS for the rating buttons

In the `<style>` section of `ChatbotView.vue`:
```css
.chatbot-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}
.chatbot-rate-btn {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.15s;
}
.chatbot-rate-btn:hover:not(:disabled) { opacity: 1; background: #f5f5f5; }
.chatbot-rate-btn.active { opacity: 1; border-color: #FF9800; background: #fff3e0; }
.chatbot-rate-btn:disabled { cursor: default; }
.chatbot-rated-label { font-size: 11px; color: #888; }
```

---

## How learning works after these changes

```
User asks a question → Flask replies → message_id returned to frontend
        ↓
User taps 👍 → frontend calls /rate with rating=1
        ↓
Flask saves Q&A to learned_faqs table with thumbs_up = thumbs_up + 1
        ↓
User taps 👎 → Flask increments thumbs_down, marks answer as bad
        ↓
Next time ANY user asks a similar question:
Flask loads top-rated learned_faqs → injects into OpenAI system prompt
        ↓
OpenAI uses the community-approved answer ✓
```

## Files changed
| File | Change |
|------|--------|
| `chatbot_flask/app.py` | Add `rating` column + `learned_faqs` table, pass history to OpenAI, inject learned FAQs into prompt, return `message_id` from `/chat`, add `/rate` endpoint |
| `frontend/src/services/aiChatbot.js` | Return `message_id` from `sendMessage()`, add `rateMessage()` export |
| `frontend/src/views/ChatbotView.vue` | Store `message_id` on messages, add real 👍👎 buttons, add `rateMsg()` function, add CSS |
