import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


import os

# OpenAI client — key stays server-side, never sent to browser
try:
    import openai
    _openai_key = os.environ.get('OPENAI_API_KEY', '')
    if _openai_key:
        openai.api_key = _openai_key
        OPENAI_ENABLED = True
    else:
        OPENAI_ENABLED = False
except ImportError:
    OPENAI_ENABLED = False

app = Flask(__name__)
# Restrict CORS to known origins for security
CORS(app, origins=[
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4173",  # Vite preview
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    # Production domains - add your deployed URLs here
    # "https://yourdomain.com",
], supports_credentials=True)
DB_PATH = Path(__file__).parent / "chatbot.db"


def init_db() -> None:
    """Initialize SQLite tables used by chatbot."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


CAMPUS_CONTEXT = """You are the SEAIT Campus Assistant for TechnoPath, a campus guide app.

CAMPUS INFORMATION:
- MST Building (Main Science and Technology): 4 floors, center of campus. Houses MST 101-120 (1F), MST 201-221 (2F), Computer Labs CL1-CL10 (3F), MST 301-420 (4F)
- JST Building (Junior Science and Technology): 4 floors at back of campus. JST101-102 (1F), JST201-202 labs (2F), seminar rooms (3F)
- RST Building (Research Science and Technology): 3 floors, left-bottom from main gate. Registrar & Accounting (1F), Guidance/Safety/HR/SSC/Student Affairs (2F), IT/Silakbo/Laboratory offices (3F)
- Library: 2 floors, ground floor left wing. Open Mon-Fri 8AM-6PM, Sat 8AM-12PM
- Cafeteria: Center grounds between MST and Gymnasium. Open 7AM-6PM daily
- Gymnasium: Back of campus with basketball/volleyball courts, fitness equipment
- Computer Labs CL1-CL6: All on 3rd floor of MST Building
- Registrar Office: 1st floor RST Building, 7 windows, Mon-Fri 8AM-5PM
- CICT Office: 2nd floor MST Building, near computer labs
- Comfort rooms available on every floor of all buildings, near stairwells

INSTRUCTIONS:
- Be helpful, concise, and friendly (2-3 sentences max)
- Guide users to use the Navigate tab for directions
- If unsure, direct them to the Registrar office
- Always mention the specific building location
- For classrooms like CL1-CL10, mention they're in MST Building 3rd floor"""

def generate_reply(message: str) -> str:
    """Generate AI-powered response using OpenAI GPT."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CAMPUS_CONTEXT},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to rule-based if OpenAI fails
        print(f"OpenAI error: {e}. Falling back to rule-based.")
        return generate_rule_based_reply(message)

def generate_rule_based_reply(message: str) -> str:
    """Fallback rule-based reply function."""
    msg = message.lower().strip()

    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'kumusta', 'musta', 'magandang']
    if any(g in msg for g in greetings):
        return ("Hello! Welcome to TechnoPath, your SEAIT campus guide. "
                "I can help you find buildings, classrooms, offices, and facilities. "
                "What are you looking for today?")

    # Classroom lookup
    for cl, building in CLASSROOM_BUILDINGS.items():
        if cl in msg:
            return (f"{cl.upper()} is located in the {building}. "
                    "Open the Map tab and select that building to see the exact room on the floor plan.")

    # Navigation intent
    nav_words = ['where is', 'how to get to', 'locate', 'find', 'location of',
                 'direction', 'navigate to', 'go to', 'paano pumunta', 'nasaan']
    if any(w in msg for w in nav_words) or '?' in msg:
        for key, data in CAMPUS_KNOWLEDGE.items():
            if key in msg:
                reply = f"The {data['name']} is located at the {data['location']}."
                if 'floors' in data:
                    reply += f" It has {data['floors']} floors."
                reply += " Use the Navigate tab in TechnoPath for a visual route from your current position."
                return reply

    # Direct name mention without nav words
    for key, data in CAMPUS_KNOWLEDGE.items():
        if key in msg:
            return (f"The {data['name']} is at the {data['location']}. "
                    "Open the Map tab to see its location on the campus layout.")

    if any(w in msg for w in ['offline', 'no internet', 'without wifi']):
        return ("TechnoPath works offline! Once you've loaded the app while online, "
                "you can use the map, navigation, and room info without internet. "
                "Your feedback will sync when you reconnect.")

    if any(w in msg for w in ['navigate', 'route', 'path', 'direction', 'shortest']):
        return ("Use the Navigate tab at the bottom of the screen. "
                "Select your destination and TechnoPath will calculate the shortest route from your current GPS position.")

    if any(w in msg for w in ['map', 'floor', 'layout', 'building map']):
        return ("Open the Map tab to see the interactive 2D campus layout. "
                "Tap any building to see its floor plan with labeled rooms and offices. "
                "Use the floor selector to switch between Ground Floor, 1st Floor, 2nd Floor, and 3rd Floor.")

    if any(w in msg for w in ['help', 'what can you do', 'features', 'commands']):
        return ("I can help you find: buildings (RST, MST, JST), classrooms (CL1-CL6), "
                "offices (Registrar, Library, Guidance, OSA, Cashier, Safety Office), "
                "and facilities (Gymnasium, Canteen, Playground). "
                "Just ask 'Where is [place]?' or use the Navigate tab for step-by-step directions.")

    if any(w in msg for w in ['thank', 'thanks', 'salamat', 'ok', 'noted']):
        return "You're welcome! Feel free to ask if you need help finding anything on campus."

    return ("I'm here to help you navigate SEAIT campus. "
            "Try asking: 'Where is the RST building?', 'How do I get to the library?', or 'Where is CL3?' "
            "For visual navigation, open the Navigate tab.")


CAMPUS_KNOWLEDGE = {
    'rst': {'name': 'RST Building', 'location': 'left-bottom of campus from the main gate', 'floors': 3},
    'mst': {'name': 'MST Building', 'location': 'center of SEAIT campus — the main academic building', 'floors': 4},
    'jst': {'name': 'JST Building', 'location': 'back of the campus', 'floors': 4},
    'library': {'name': 'Library', 'location': 'ground floor of the main building, left wing'},
    'registrar': {'name': "Registrar's Office", 'location': '1st floor of the RST Building'},
    'gymnasium': {'name': 'Gymnasium', 'location': 'back of the campus'},
    'canteen': {'name': 'Canteen', 'location': 'center grounds area between the main buildings'},
    'cafeteria': {'name': 'Canteen', 'location': 'center grounds area between the main buildings'},
    'safety': {'name': 'Safety and Security Office', 'location': 'near the main gate'},
    'security': {'name': 'Safety and Security Office', 'location': 'near the main gate'},
    'main gate': {'name': 'Main Gate', 'location': 'National Highway, Barangay Crossing Rubber, Tupi, South Cotabato'},
    'gate': {'name': 'Main Gate', 'location': 'National Highway, Barangay Crossing Rubber, Tupi, South Cotabato'},
    'playground': {'name': 'Playground', 'location': 'open grounds area of the campus'},
    'basic education': {'name': 'Basic Education Building', 'location': 'K-12 section of the campus'},
    'k12': {'name': 'Basic Education Building', 'location': 'K-12 section of the campus'},
    'clinic': {'name': 'School Clinic', 'location': 'main building ground floor'},
    'guidance': {'name': 'Guidance Office', 'location': 'main building near the administrative area'},
    'cashier': {'name': "Cashier's Office", 'location': 'ground floor of the main building near the Registrar'},
    'admission': {'name': 'Admissions Office', 'location': 'main building ground floor'},
    'osa': {'name': 'Office of Student Affairs (OSA)', 'location': 'main building'},
    'cr1': {'name': 'CR1 (Comfort Room 1)', 'location': 'ground floor of the main building'},
    'cr2': {'name': 'CR2 (Comfort Room 2)', 'location': 'second floor of the main building'},
}

CLASSROOM_BUILDINGS = {
    'cl1': 'MST Building', 'cl2': 'MST Building',
    'cl3': 'MST Building', 'cl4': 'MST Building',
    'cl5': 'MST Building', 'cl6': 'MST Building',
    'cl7': 'MST Building', 'cl8': 'MST Building',
    'cl9': 'MST Building', 'cl10': 'MST Building',
}


@app.route("/health", methods=["GET"])
def health():
    """Health endpoint for chatbot service."""
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint called from Flutter app."""
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    reply = generate_reply(message)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply) VALUES (?, ?)",
            (message, reply),
        )
        conn.commit()

    return jsonify({"reply": reply})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
