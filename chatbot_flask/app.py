import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins
DB_PATH = Path(__file__).parent / "chatbot.db"


def init_db() -> None:
    """Initialize SQLite tables used by chatbot."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL
            )
            """
        )
        conn.commit()


def generate_reply(message: str) -> str:
    """Full SEAIT campus knowledge base reply function."""
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

    if any(w in msg for w in ['qr', 'qr code', 'scan', 'scanner']):
        return ("You can scan QR codes posted at SEAIT campus buildings. "
                "The main gate QR code opens TechnoPath directly without needing to download or install anything. "
                "Use the QR Scanner button in the app to scan room and building QR codes.")

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
    'rst': {'name': 'RST Building', 'location': 'right side of campus from the main gate', 'floors': 3},
    'mst': {'name': 'MST Building', 'location': 'center of SEAIT campus — the main academic building', 'floors': 3},
    'jst': {'name': 'JST Building', 'location': 'left side of the campus', 'floors': 3},
    'library': {'name': 'Library', 'location': 'ground floor of the main building, left wing'},
    'registrar': {'name': "Registrar's Office", 'location': 'ground floor of the main building near the main entrance'},
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
    'cl3': 'RST Building', 'cl4': 'RST Building',
    'cl5': 'JST Building', 'cl6': 'JST Building',
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
