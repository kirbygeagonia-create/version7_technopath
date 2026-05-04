import os
import psycopg2
import requests
import threading
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'https://technopath-backend-djanggo.onrender.com')

# Load environment variables
load_dotenv()

# Initialize OpenAI client — key stays server-side, never sent to browser
_openai_key = os.getenv('OPENAI_API_KEY', '')
OPENAI_ENABLED = False
client = None

if _openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=_openai_key)
        OPENAI_ENABLED = True
    except ImportError:
        print('[Chatbot] openai package not installed — falling back to rule-based replies')
else:
    print('[Chatbot] OPENAI_API_KEY not set — using rule-based replies only')

app = Flask(__name__)

# Rate limiter — prevent API abuse and runaway OpenAI costs
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)

# Restrict CORS to known origins for security
CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "https://techno-path-frontend.onrender.com",
    "https://technopath-frontend.onrender.com",
    "https://technopath-frontend-or73.onrender.com",
], supports_credentials=True)
DB_PATH = Path(__file__).parent / "chatbot.db"

# PostgreSQL Database URL (Render provides this as env var)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Get database connection - PostgreSQL in production, SQLite for local dev."""
    if DATABASE_URL:
        # Use PostgreSQL on Render
        return psycopg2.connect(DATABASE_URL)
    else:
        # Fallback to SQLite for local development
        import sqlite3
        return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Initialize database tables used by chatbot."""
    if DATABASE_URL:
        # PostgreSQL mode
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Chat history with ratings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_message TEXT NOT NULL,
                    bot_reply TEXT NOT NULL,
                    rating TEXT CHECK(rating IN ('up', 'down')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # Learned FAQs from user ratings and teaching with confidence scoring
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learned_faqs (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating_count INTEGER DEFAULT 1,
                    confidence INTEGER DEFAULT 75,
                    sources INTEGER DEFAULT 1,
                    source_type TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
    else:
        # SQLite mode for local dev
        import sqlite3
        with sqlite3.connect(DB_PATH) as conn:
            # Chat history with ratings
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    bot_reply TEXT NOT NULL,
                    rating TEXT CHECK(rating IN ('up', 'down', NULL)),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # Learned FAQs from user ratings and teaching with confidence scoring
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learned_faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating_count INTEGER DEFAULT 1,
                    confidence INTEGER DEFAULT 75,
                    sources INTEGER DEFAULT 1,
                    source_type TEXT DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()


CAMPUS_CONTEXT = """You are the official TechnoPath AI Campus Assistant for SEAIT
(South East Asian Institute of Technology), located at National Highway,
Crossing Rubber, Tupi, South Cotabato, Mindanao, Philippines 9505.

Be helpful, friendly, and concise (2-4 sentences). Always give specific locations.
If asked for directions, tell users to use the Navigate tab in TechnoPath.

=== ABOUT SEAIT ===
Full name: South East Asian Institute of Technology, Inc.
Type: Private, non-stock, non-profit Higher Education Institution
Founded: February 2006
Phone: (083) 226-1202 | Email: seaitinc@yahoo.com
Website: https://www.seait.edu.ph
Region: SOCCSKSARGEN (Region XII), Mindanao, Philippines

SEAIT IS FREE: Yes — SEAIT offers completely FREE tuition for ALL college degree
programs. It is one of the very few private schools in the Philippines to do this.
Funding comes from UNIFAST (since 2016), Tulong-Dunong grants from CHED, and the
founders' personal commitment to accessible education. Indigenous Peoples and
neighboring tribes are especially supported.

=== FOUNDERS & OWNERSHIP ===
Founder: Hon. Reynaldo S. Tamayo Jr. (born Feb 9, 1980, Tupi)
Co-founder: Mrs. Rochelle P. Tamayo (wife)
Both were DOST scholars in BS Information Technology at Cebu Institute of Technology.
They built SEAIT to give back to their community and make college education free for
the youth of Tupi and surrounding areas. Hon. Tamayo Jr. later became Governor of
South Cotabato. The school is run by the Tamayo family.
Key family members: Atty. Ghizelle Jean S. Tamayo-Jimenea (admin/legal),
Dr. Jeffrey S. Tamayo M.D. FPCP MCH (Board Member and School Physician).

School motto: "Committed to the Total Development of the Student"
Vision: A premier institution that provides quality education and produces globally
empowered individuals.
Mission: To produce competent, community-oriented, and globally competitive
individuals through holistic education.

=== HISTORY TIMELINE ===
2006 — Founded as a TESDA vocational school. First programs: Computer Programming
       NC-IV and Computer Hardware Servicing NC-II.
2007 — Added Hotel and Restaurant Management.
2008 — Upgraded to Higher Education Institution. Added BSIT.
2016 — UNIFAST adopted; tuition became FREE for all college students.
2021 — Awarded Gawad Parangal by CHED Region XII for advocacy of free education
       for Indigenous Peoples. Ceremony at South Cotabato Gymnasium, Koronadal City.
2025 — JY Corporation (Korea) awarded scholarships to SEAIT students.
       Tupi IT Park groundbreaking — SEAIT named key partner.
2026 — SEAIT Social Work Dept wins 3rd consecutive PASWI championship.
       Silakbo Publication wins CineMatutum 2026 Documentary Film Competition.

=== MAIN CAMPUS BUILDINGS ===

--- MST BUILDING (Main Science and Technology Building) ---
Location: CENTER of SEAIT campus — the main and largest academic building
Floors: 4 floors
1st Floor: Classrooms MST 101-120, School Clinic (college/HS students), admin areas
2nd Floor: Classrooms MST 201-221, CICT Office, faculty rooms
3rd Floor: Computer Laboratories CL1, CL2, CL3, CL4, CL5, CL6, CL7, CL8, CL9, CL10
           (ALL 10 computer labs are on this floor)
4th Floor: Classrooms MST 301-420, additional academic rooms
Notable: Houses the flagship CICT college and all computer laboratories.

--- JST BUILDING (Junior Science and Technology Building) ---
Location: BACK of the SEAIT campus
Floors: 4 floors
1st Floor: Classrooms JST 101-102, general lecture rooms
2nd Floor: Science and Engineering Laboratories JST 201-202
3rd Floor: Seminar rooms, multipurpose rooms
4th Floor: Additional academic and seminar areas
Notable: Houses science and engineering labs for Civil Engineering and Agriculture.

--- RST BUILDING (Research Science and Technology Building) ---
Location: LEFT-BOTTOM area of campus from the main gate (near the gate)
Floors: 3 floors
1st Floor: Registrar's Office (7 windows, Mon-Fri 8AM-5PM), Cashier/Accounting Office,
           School Clinic (for elementary students)
2nd Floor: Guidance and Testing Center, Safety and Security Office, Human Resources,
           Supreme Student Council (SSC), Student Affairs and Services Office (SASO)
3rd Floor: IT Office, Silakbo Student Publication Office, Laboratory offices
Notable: Main administrative building of SEAIT.

=== COMPUTER LABORATORIES (ALL ON MST 3RD FLOOR) ===
CL1 — MST Building 3rd Floor (General IT / Programming)
CL2 — MST Building 3rd Floor (General IT / Programming)
CL3 — MST Building 3rd Floor (General IT / Programming)
CL4 — MST Building 3rd Floor (Networking / Hardware)
CL5 — MST Building 3rd Floor (Networking / Hardware)
CL6 — MST Building 3rd Floor (Multimedia / Design)
CL7 — MST Building 3rd Floor (Multimedia / Design)
CL8 — MST Building 3rd Floor (Software Development)
CL9 — MST Building 3rd Floor (Software Development)
CL10 — MST Building 3rd Floor (Advanced IT / Research)
All labs have state-of-the-art desktops, updated software, and fast internet.

=== OTHER CAMPUS FACILITIES ===
Library: Ground floor of main building, left wing. 2 floors. Has textbooks, journals,
         e-books, multimedia, quiet study areas and group spaces.
         Hours: Mon-Fri 8AM-6PM, Saturday 8AM-12PM. Librarian: Noel P. Lacaba RL MLIS.
Cafeteria/Canteen: Center grounds between MST Building and Gymnasium. Open 7AM-6PM daily.
Gymnasium: Back of campus. Basketball courts, volleyball courts, fitness equipment.
Playground: Open grounds area for recreation.
Language Laboratory: Inside MST Building. Soundproof cubicles, headsets, audio-visual
                     devices, interactive software for language practice.
Culinary/HM Lab: Hospitality Management area. Modern culinary tools, simulated
                 real-world hospitality environment for hands-on training.
School Clinic: TWO locations — MST Building 1st Floor (for HS and college students)
               and RST Building 1st Floor (for elementary students).
               Staffed by 2 school nurses and 2 nursing assistants.
               School Physician: Dr. Jeffrey S. Tamayo M.D.
Agriculture Farm: Located at Tucalabong and MAPECON areas. Farm plots, demonstration
                  areas, and greenhouses for Agriculture program students.
Comfort Rooms: Available on EVERY FLOOR of ALL buildings (MST, JST, RST),
               located near stairwells.
Main Gate: National Highway, Barangay Crossing Rubber, Tupi, South Cotabato.

=== OFFICES & KEY PEOPLE ===
Registrar's Office — RST Bldg 1st Floor | 7 windows | Mon-Fri 8AM-5PM
Cashier/Accounting — RST Bldg 1st Floor
CICT Office — MST Bldg 2nd Floor | Jonathan L. Sucayan MIT
Guidance & Testing Center — RST Bldg 2nd Floor | Rovi D. Siloterio MAED RGC
Safety & Security Office — RST Bldg 2nd Floor | S03 Romel B. Maloloy-on CTP MBA
Student Affairs (SASO) — RST Bldg 2nd Floor
Human Resources (HR) — RST Bldg 2nd Floor
Library — Main Bldg Ground Floor Left Wing | Noel P. Lacaba RL MLIS
IT Office — RST Bldg 3rd Floor
Silakbo Student Publication — RST Bldg 3rd Floor
Supreme Student Council (SSC) — RST Bldg 2nd Floor

=== COLLEGES AND COURSES OFFERED ===

COLLEGE OF INFORMATION AND COMMUNICATION TECHNOLOGY (CICT) ⭐ Flagship
- Bachelor of Science in Information Technology (BSIT)
- SEAIT is best known for its IT programs

DEPARTMENT OF CIVIL ENGINEERING
- Bachelor of Science in Civil Engineering (BSCE)

COLLEGE OF TEACHER EDUCATION (CTE)
Dean: Dr. Fidel N. Braga / Dr. Rodolfo D. Juanillo
- Bachelor of Secondary Education (BSEd) major in Filipino
- Bachelor of Secondary Education (BSEd) major in General Science
- Bachelor of Secondary Education (BSEd) major in Social Studies
- Bachelor of Technology and Livelihood Education (BTLEd) major in ICT

COLLEGE OF AGRICULTURE AND FISHERIES
- Bachelor of Science in Agriculture (Animal and Crop Science)
- Bachelor of Agricultural Technology
Farm sites at Tucalabong and MAPECON.

COLLEGE OF BUSINESS AND GOOD GOVERNANCE
- Business Administration programs
- Tourism and Hospitality Management

COLLEGE OF CRIMINAL JUSTICE EDUCATION
- Bachelor of Science in Criminology (BSCrim)
Dean: Airah Shynne C. Cabizares MBA

COLLEGE OF SOCIAL WORK
- Bachelor of Science in Social Work (BSSW)
SEAIT Social Work Dept is 3-time PASWI champion (2024, 2025, 2026).

TESDA PROGRAMS (Technical-Vocational, free)
- Computer Programming NC-IV
- Computer Hardware Servicing NC-II
- Cookery NC-II
- Hotel and Restaurant Management
- Other TESDA-certified trades

K-12 BASIC EDUCATION (DepEd recognized)
- Complete Senior High School (Grades 11-12)
- Academic Track
- Technical-Vocational-Livelihood (TVL) Track

=== CAMPUS SUMMARY ===
Main buildings: 3 (MST 4F, JST 4F, RST 3F)
Computer labs: 10 (CL1-CL10, all on MST 3rd Floor)
Library: 1 (2-floor, ground floor left wing)
Gymnasium: 1 (back of campus)
School clinics: 2 offices (MST 1F and RST 1F)
Cafeteria: 1 (between MST and Gymnasium)
Comfort rooms: On every floor of all 3 buildings (near stairwells)
Agriculture farms: 2 external sites (Tucalabong, MAPECON)

=== HOW TO ANSWER QUESTIONS ===
- For directions: Always tell users to use the Navigate tab in TechnoPath for
  step-by-step visual routes.
- For room locations: Give the building name, floor number, and room number.
- For office hours: State the hours if known, otherwise direct to Registrar.
- For enrollment/tuition: Remind that ALL college programs are FREE (tuition-free).
- For courses: List the specific college and degree program.
- If unsure: Direct to the Registrar's Office (RST Bldg 1st Floor) or call (083) 226-1202.
"""

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

def search_faq_database(query: str) -> tuple:
    """Search FAQ database for similar questions using keyword matching.
    Returns (matched_answer, similarity_score) or (None, 0) if no match.
    """
    try:
        # Import difflib for sequence matching (simple similarity)
        import difflib
        
        with get_db_connection() as conn:
            # Get all FAQs from database
            cursor = conn.execute(
                "SELECT question, answer FROM faq_entries WHERE is_active = 1"
            )
            faqs = cursor.fetchall()
        
        if not faqs:
            return None, 0
        
        query_lower = query.lower().strip()
        best_match = None
        best_score = 0
        
        for question, answer in faqs:
            # Calculate similarity using SequenceMatcher
            similarity = difflib.SequenceMatcher(
                None, query_lower, question.lower().strip()
            ).ratio()
            
            # Also check for keyword containment (exact word match = higher score)
            query_words = set(query_lower.split())
            question_words = set(question.lower().split())
            word_overlap = len(query_words & question_words) / len(query_words | question_words)
            
            # Combined score: 60% sequence similarity + 40% word overlap
            combined_score = (similarity * 0.6) + (word_overlap * 0.4)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = answer
        
        # Return match only if score is above threshold (0.5 = 50% match)
        if best_score >= 0.5:
            return best_match, best_score
        
        return None, best_score
    except Exception as e:
        print(f"[RAG] FAQ search error: {e}")
        return None, 0


def get_learned_faqs(limit: int = 20) -> str:
    """Fetch all learned FAQs from database for OpenAI context."""
    try:
        init_db()
        with get_db_connection() as conn:
            # Return all facts with confidence >= 50 (includes all system facts at 100%)
            cursor = conn.execute(
                "SELECT question, answer, confidence, sources FROM learned_faqs WHERE confidence >= 50 ORDER BY confidence DESC, sources DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            if not rows:
                return ""
            lines = ["\n[LEARNED FROM USERS - Verified Facts (High Confidence):]"]
            for question, answer, confidence, sources in rows:
                lines.append(f"Q: {question}\nA: {answer} [Confidence: {confidence}%, Sources: {sources} users]")
            return "\n".join(lines)
    except Exception as e:
        print(f"[Learned FAQs] Error: {e}")
        return ""


def update_learned_faq(question: str, answer: str, source: str = "user", confidence_boost: int = 10) -> bool:
    """
    Add or update a learned fact with confidence scoring.
    - If fact exists: boost confidence
    - If new fact: add with base confidence
    """
    try:
        init_db()
        with get_db_connection() as conn:
            # Check if similar question exists
            cursor = conn.execute(
                "SELECT id, confidence, sources, answer FROM learned_faqs WHERE LOWER(question) = LOWER(?)",
                (question,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing fact - boost confidence
                fact_id, current_conf, current_sources, old_answer = existing
                new_conf = min(100, current_conf + confidence_boost)
                new_sources = current_sources + 1
                
                # If answer changed significantly, reduce confidence
                if old_answer.lower() != answer.lower():
                    new_conf = max(50, new_conf - 20)  # Penalty for conflicting info
                
                conn.execute(
                    "UPDATE learned_faqs SET confidence = ?, sources = ?, answer = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_conf, new_sources, answer, fact_id)
                )
                print(f"[Learning] Updated fact: '{question[:50]}...' (Confidence: {new_conf}%, Sources: {new_sources})")
            else:
                # Add new fact with base confidence
                base_confidence = 60 if source == "extracted" else 75  # User-taught = higher trust
                conn.execute(
                    "INSERT INTO learned_faqs (question, answer, confidence, sources, source_type, created_at, updated_at) VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (question, answer, base_confidence, source)
                )
                print(f"[Learning] New fact learned: '{question[:50]}...' (Confidence: {base_confidence}%)")
            
            conn.commit()
            return True
    except Exception as e:
        print(f"[Learning] Error: {e}")
        return False


def extract_teaching_from_message(message: str, bot_last_reply: str = None) -> dict:
    """
    Intelligent teaching pattern detection.
    Returns dict with 'question', 'answer', 'type' if teaching detected.
    ONLY detects explicit teaching statements, NOT questions.
    """
    import re
    msg_lower = message.lower().strip()
    
    # STRICT CHECK: If message ends with ? it's a QUESTION - don't treat as teaching
    if message.strip().endswith('?'):
        return None
    
    # STRICT CHECK: If it starts with question words + has question structure
    question_patterns = [
        r'^(who|what|where|when|why|how)\s+(is|are|was|were|does|do|did|can|could|would|will|should|has|have)',
        r'^(can|could|would|will|should|is|are|do|does|did)\s+(you|we|they|it|this|that|the|a|an|someone)',
        r'^(tell|explain|describe)\s+(me|us|about)',
        r'^(which|whose|whom)\s+',
    ]
    for pattern in question_patterns:
        if re.search(pattern, msg_lower):
            return None
    
    # Pattern 1: Explicit teaching "X is Y" - but NOT questions
    # Must be a STATEMENT (no question words at start, no question mark)
    patterns = [
        (r'^(?!who|what|where|when|why|how|can|could|would|will|is|are|do|does|did|has|have)(\w+(?:\s+\w+){0,5})\s+(?:is|are|means?|stands?\s+for|refers?\s+to)\s+(.+)$', 'definition'),
        (r'^(?:the\s+)?(?:meaning|definition)\s+of\s+(\w+(?:\s+\w+){0,4})\s+is\s+(.+)$', 'definition'),
        (r'(?:remember|note|add|learn|store|save)\s+(?:that\s+)?(.+?)\s+(?:is|are|means?)\s+(.+)', 'instruction'),
        (r'^(CL\d+)\s+(?:is\s+)?(?:located\s+)?(?:at|in|on)?\s*(.+)$', 'lab_location'),
        (r'^(MST|JST|RST)\s+Building\s+(?:is\s+)?(?:located\s+)?(?:at|in)?\s*(.+)$', 'building_location'),
    ]
    
    import re
    for pattern, ptype in patterns:
        match = re.search(pattern, msg_lower, re.IGNORECASE)
        if match:
            if ptype == 'lab_location':
                question = f"Where is CL{match.group(1)}?"
                answer = f"CL{match.group(1)} is located at {match.group(2)}"
            elif ptype == 'building_location':
                question = f"Where is the {match.group(1)} Building?"
                answer = f"The {match.group(1)} Building is located at {match.group(2)}"
            else:
                subject = match.group(1).strip()
                definition = match.group(2).strip()
                question = f"What is {subject}?"
                answer = f"{subject} is {definition}"
            
            return {'question': question, 'answer': answer, 'type': ptype}
    
    # Pattern 2: User correcting the bot
    if bot_last_reply:
        correction_patterns = [
            r"(?:wrong|incorrect|not right|that's not|you're wrong|actually)",
            r"(?:no[,.]?\s+(?:it|that|this)\s+(?:is|should be))",
            r"(?:the correct|correct|should be|actually is)",
        ]
        for pattern in correction_patterns:
            if re.search(pattern, msg_lower):
                # Extract what they said after the correction
                # Heuristic: The rest of the message is the correction
                correction_text = message
                question = extract_subject_from_context(bot_last_reply, message)
                if question:
                    return {
                        'question': question,
                        'answer': correction_text,
                        'type': 'correction',
                        'original_reply': bot_last_reply
                    }
    
    # Pattern 3: Implicit fact sharing (location, contact, hours)
    implicit_patterns = [
        (r'I\s+(?:have|attend|go\s+to)\s+(?:class|lab)\s+(?:in|at)\s+(CL\d+).*?(MST|JST|RST)\s+(\d+)[a-z]{2}\s+[Ff]loor', 'user_location_sharing'),
        (r'(?:contact|call|phone|reach)\s+(?:them|the\s+office)?\s+at\s+(\d{3}[-.]?\d{3}[-.]?\d{4})', 'contact_info'),
        (r'(?:open|hours|time).*?(\d{1,2}[:\d{2}]?\s*(?:AM|PM|am|pm)?)', 'hours_info'),
    ]
    
    for pattern, ptype in implicit_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            if ptype == 'user_location_sharing':
                lab = match.group(1)
                building = match.group(2)
                floor = match.group(3)
                return {
                    'question': f"Where is {lab}?",
                    'answer': f"{lab} is located in the {building} Building {floor}th Floor",
                    'type': 'extracted_location'
                }
    
    return None


def extract_subject_from_context(bot_reply: str, user_message: str) -> str:
    """Extract what the user was asking about from context."""
    # Try to find the subject in the bot's last reply
    import re
    
    # Look for building/lab mentions in bot reply
    patterns = [
        r'(CL\d+)',
        r'(MST|JST|RST)\s+Building',
        r'(?:the\s+)?([A-Z][a-z]+\s+Building)',
        r'(?:office|department)\s+(?:of\s+)?([A-Z][a-z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, bot_reply, re.IGNORECASE)
        if match:
            return f"Where is {match.group(1)}?"
    
    return None


def log_correction(original_question: str, wrong_answer: str, correct_answer: str, user_message: str):
    """Log when the bot was corrected by a user."""
    try:
        init_db()
        with get_db_connection() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS bot_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_question TEXT,
                    wrong_answer TEXT,
                    correct_answer TEXT,
                    user_correction TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            conn.execute(
                "INSERT INTO bot_corrections (original_question, wrong_answer, correct_answer, user_correction) VALUES (?, ?, ?, ?)",
                (original_question, wrong_answer, correct_answer, user_message)
            )
            conn.commit()
            print(f"[Learning] Correction logged: {original_question[:50]}...")
    except Exception as e:
        print(f"[Learning] Error logging correction: {e}")


def generate_reply(message: str, history: list = None) -> str:
    if history is None:
        history = []
    
    if not OPENAI_ENABLED or not client:
        return generate_rule_based_reply(message)
    try:
        system_prompt = CAMPUS_CONTEXT + build_faq_block() + get_learned_faqs()
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

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using word overlap and n-grams.
    Returns score between 0.0 and 1.0
    """
    import re
    
    # Clean and tokenize
    def clean(text):
        return set(re.findall(r'\b\w+\b', text.lower()))
    
    words1 = clean(text1)
    words2 = clean(text2)
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity (intersection / union)
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    jaccard = intersection / union if union > 0 else 0.0
    
    # Boost score if important keywords match
    important_keywords = {'seait', 'courses', 'buildings', 'labs', 'office', 'library', 
                         'registrar', 'clinic', 'gym', 'canteen', 'tuition', 'free',
                         'bsit', 'civil', 'engineering', 'criminology', 'education',
                         'mst', 'rst', 'jst', 'cl1', 'cl2', 'cl3', 'cl4', 'cl5'}
    
    kw_match1 = len(words1 & important_keywords & words2)
    kw_boost = min(kw_match1 * 0.15, 0.4)  # Max 0.4 boost for keyword matches
    
    return min(jaccard + kw_boost, 1.0)


def find_best_answer_ml(message: str) -> tuple:
    """
    Machine Learning-based answer finding using similarity matching.
    Returns (answer, confidence_score, source)
    """
    import sqlite3
    
    msg_lower = message.lower().strip()
    best_answer = None
    best_score = 0.0
    best_source = None
    
    # 1. Check learned_faqs database with ML similarity
    try:
        init_db()
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT question, answer, confidence, source_type FROM learned_faqs WHERE confidence >= 30")
            rows = cursor.fetchall()
            
            for question, answer, confidence, source in rows:
                similarity = calculate_similarity(msg_lower, question.lower())
                # Weight by stored confidence and similarity
                weighted_score = similarity * (confidence / 100)
                
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_answer = answer
                    best_source = f"learned_db (confidence: {confidence}%)"
    except Exception as e:
        print(f"[ML] Database lookup error: {e}")
    
    # 2. Check SEAIT_QA hardcoded knowledge
    for question, answer in SEAIT_QA.items():
        similarity = calculate_similarity(msg_lower, question)
        # Hardcoded answers have high confidence (0.95)
        weighted_score = similarity * 0.95
        
        if weighted_score > best_score:
            best_score = weighted_score
            best_answer = answer
            best_source = "hardcoded_knowledge"
    
    return best_answer, best_score, best_source


def generate_rule_based_reply(message: str) -> str:
    """ML-enhanced rule-based reply function."""
    import re
    
    msg = message.lower().strip()
    msg_clean = msg.replace('?', '').replace('the ', '').replace('that ', '').strip()
    
    # Use ML to find best answer
    best_answer, confidence, source = find_best_answer_ml(message)
    
    # If we have a good match (confidence >= 0.4), return it
    if best_answer and confidence >= 0.4:
        print(f"[ML Match] Confidence: {confidence:.2f}, Source: {source}")
        return best_answer
    
    # Handle greetings
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 
                 'kumusta', 'musta', 'magandang', 'good day']
    if any(g in msg for g in greetings):
        return ("Hello! Welcome to TechnoPath, your SEAIT campus guide. 🤖\n\n"
                "I can help you with:\n"
                "• Finding buildings and classrooms\n"
                "• Campus navigation directions\n"
                "• School offices and facilities\n"
                "• SEAIT information and history\n\n"
                "What would you like to know?")
    
    # Handle thanks
    thanks = ['thank', 'thanks', 'salamat', 'ty']
    if any(t in msg for t in thanks):
        return "You're welcome! 😊 Feel free to ask if you need anything else about SEAIT!"
    
    # Handle goodbye
    goodbye = ['bye', 'goodbye', 'see you', 'paalam']
    if any(g in msg for g in goodbye):
        return "Goodbye! Have a great day at SEAIT! 👋"
    
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

    # Conversational responses for non-campus questions (only if asking about the bot itself)
    if any(w in msg for w in ['who are you', 'what are you', 'chatbot', 'ai', 'robot', 'what kind of ai']) and 'seait' not in msg:
        return ("I'm TechnoPath's AI assistant! 🤖\n\n"
                "I'm a rule-based AI system with retrieval capabilities. Here's how I work:\n"
                "• I search our campus FAQ database first (RAG system)\n"
                "• I use pattern matching for campus navigation\n"
                "• Admins improve me by adding better FAQs\n\n"
                "I'm not a neural network AI like ChatGPT, but I'm designed specifically for SEAIT campus "
                "and I get smarter every day through user interactions!")
    
    # Definition/meaning questions - only if NOT about SEAIT (let OpenAI handle SEAIT)
    if any(w in msg for w in ['what is the meaning', 'what does', 'meaning of', 'stands for', 'definition']) and 'seait' not in msg:
        return ("I don't know the answer to that yet, but I'm learning! 🤔\n\n"
                "If you know the answer, please tell me and I'll add it to my knowledge base! "
                "Just say something like 'It stands for...' or 'The meaning is...'")
    
    if any(w in msg for w in ['how are you', 'how do you do']):
        return ("I'm doing great! Ready to help you navigate SEAIT campus. 😊 "
                "How can I assist you today?")
    
    if any(w in msg for w in ['how are you', 'how do you do']):
        return ("I'm doing great! Ready to help you navigate SEAIT campus. 😊 "
                "How can I assist you today?")
    
    if any(w in msg for w in ['thank', 'thanks', 'salamat']):
        return ("You're very welcome! 🎉 I'm always here to help. "
                "Feel free to ask me anything about the campus anytime!")
    
    if any(w in msg for w in ['help', 'what can you do', 'features', 'commands']):
        return ("I can help you find: buildings (RST, MST, JST), classrooms (CL1-CL6), "
                "offices (Registrar, Library, Guidance, OSA, Cashier, Safety Office), "
                "and facilities (Gymnasium, Canteen, Playground). "
                "Just ask 'Where is [place]?' or use the Navigate tab for step-by-step directions.")

    if any(w in msg for w in ['thank', 'thanks', 'salamat', 'ok', 'noted']):
        return "You're welcome! Feel free to ask if you need help finding anything on campus."
    
    # Check if user is providing an answer/correction
    answer_patterns = ['the meaning of', 'the meaning is', 'stands for', 'is located at', 'is found at', 
                       'seait is', 'seait stands for', 'it stands for', 'it is', 'that is']
    if any(pattern in msg for pattern in answer_patterns) and len(msg) > 10:
        # Extract the subject (what is being defined)
        subject = None
        if 'the meaning of' in msg:
            parts = msg.split('the meaning of')
            if len(parts) > 1:
                rest = parts[1].strip()
                words = rest.split()
                for w in words:
                    w = w.replace('?', '').replace('is', '').strip()
                    if w and w not in ('the', 'a', 'an'):
                        subject = w
                        break
        elif ' stands for ' in msg:
            subject = msg.split(' stands for ')[0].strip()
        elif ' is ' in msg:
            parts = msg.split(' is ')
            if len(parts) > 1:
                subject = parts[0].strip()
        
        if subject and len(subject) > 1:
            # Store multiple question variations for better matching
            questions = [
                f"What is {subject}?",
                f"Where is {subject}?",
                f"Tell me about {subject}",
                subject
            ]
            store_learning_opportunity(message, "user_provided_answer")
            for q in questions:
                store_learned_answer(q, message, 'up')
            return f"Thank you for teaching me about '{subject}'! 🎓 I've learned your answer and will use it for similar questions."
        else:
            store_learning_opportunity(message, "user_provided_answer")
            store_learned_answer("What is this?", message, 'up')

    # Unknown question - admit limitation and invite learning
    return ("I don't know the answer to that yet, but I'm learning! 🤔\n\n"
            "I can help you with:\n"
            "• Finding buildings and classrooms\n"
            "• Campus navigation directions\n"
            "• School offices and facilities\n\n"
            "Please rate this response 👎 and an admin will add the answer to my knowledge base. "
            "I get smarter every time someone teaches me something new!")


def store_learning_opportunity(message: str, source: str = "user_input"):
    """Store user-provided information as a learning opportunity for admin review."""
    try:
        init_db()
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learning_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_input TEXT NOT NULL,
                    source TEXT,
                    status TEXT DEFAULT 'pending',
                    suggested_answer TEXT,
                    created_at TEXT NOT NULL,
                    reviewed_by TEXT,
                    reviewed_at TEXT
                )
            ''')
            conn.execute(
                "INSERT INTO learning_opportunities (user_input, source, created_at) VALUES (?, ?, ?)",
                (message, source, datetime.now().isoformat())
            )
        print(f"[Learning] Stored opportunity: {message[:50]}...")
    except Exception as e:
        print(f"[Learning] Error storing opportunity: {e}")


CAMPUS_KNOWLEDGE = {
    # Buildings
    'rst': {'name': 'RST Building (Research Science and Technology)', 'location': 'left-bottom of campus from main gate — ADMIN BUILDING', 'floors': 3,
            'offices': {
                '1f': "Registrar's Office (7 windows, Mon-Fri 8AM-5PM), Cashier/Accounting, School Clinic (elementary)",
                '2f': 'Guidance and Testing Center, Safety & Security, HR, Supreme Student Council (SSC), SASO',
                '3f': 'IT Office, Silakbo Student Publication Office, Laboratory offices'
            }},
    'mst': {'name': 'MST Building (Main Science and Technology)', 'location': 'CENTER of SEAIT campus — MAIN ACADEMIC BUILDING', 'floors': 4,
            'rooms': {
                '1f': 'Classrooms MST 101-120, School Clinic (HS/college), admin areas',
                '2f': 'Classrooms MST 201-221, CICT Office, faculty rooms',
                '3f': 'ALL Computer Labs CL1-CL10 (CICT flagship college)',
                '4f': 'Classrooms MST 301-420'
            }},
    'jst': {'name': 'JST Building (Junior Science and Technology)', 'location': 'BACK of the SEAIT campus', 'floors': 4,
            'rooms': {
                '1f': 'Classrooms JST 101-102, general lecture rooms',
                '2f': 'Science and Engineering Laboratories JST 201-202',
                '3f': 'Seminar rooms, multipurpose rooms',
                '4f': 'Additional academic and seminar areas'
            }},

    # Main facilities
    'library': {'name': 'Library', 'location': 'Ground floor of main building, left wing (2 floors)',
                'hours': 'Mon-Fri 8AM-6PM, Sat 8AM-12PM', 'librarian': 'Noel P. Lacaba RL MLIS',
                'features': 'Textbooks, journals, e-books, multimedia, quiet study areas, group spaces'},
    'gymnasium': {'name': 'Gymnasium', 'location': 'Back of campus',
                  'features': 'Basketball courts, volleyball courts, fitness equipment, managed by Sports Office'},
    'canteen': {'name': 'Canteen/Cafeteria', 'location': 'Center grounds between MST Building and Gymnasium',
                'hours': 'Open 7AM-6PM daily'},
    'cafeteria': {'name': 'Canteen/Cafeteria', 'location': 'Center grounds between MST Building and Gymnasium',
                  'hours': 'Open 7AM-6PM daily'},

    # Offices
    'registrar': {'name': "Registrar's Office", 'location': 'RST Building 1st Floor', 'hours': 'Mon-Fri 8AM-5PM', 'windows': 7},
    'cashier': {'name': "Cashier's Office / Accounting", 'location': 'RST Building 1st Floor'},
    'accounting': {'name': "Cashier's Office / Accounting", 'location': 'RST Building 1st Floor'},
    'cict': {'name': 'CICT Office (College of Information and Communication Technology)', 'location': 'MST Building 2nd Floor',
             'head': 'Jonathan L. Sucayan MIT', 'notes': 'Flagship IT college, houses computer labs'},
    'guidance': {'name': 'Guidance and Testing Center', 'location': 'RST Building 2nd Floor', 'head': 'Rovi D. Siloterio MAED RGC'},
    'safety': {'name': 'Safety and Security Office', 'location': 'RST Building 2nd Floor', 'head': 'S03 Romel B. Maloloy-on CTP MBA'},
    'security': {'name': 'Safety and Security Office', 'location': 'RST Building 2nd Floor', 'head': 'S03 Romel B. Maloloy-on CTP MBA'},
    'hr': {'name': 'Human Resources (HR)', 'location': 'RST Building 2nd Floor'},
    'ssc': {'name': 'Supreme Student Council (SSC)', 'location': 'RST Building 2nd Floor'},
    'saso': {'name': 'Student Affairs and Services Office (SASO)', 'location': 'RST Building 2nd Floor'},
    'it office': {'name': 'IT Office', 'location': 'RST Building 3rd Floor'},
    'silakbo': {'name': 'Silakbo Student Publication Office', 'location': 'RST Building 3rd Floor'},

    # Clinics
    'clinic': {'name': 'School Clinic', 'location': 'TWO locations: MST Bldg 1st Floor (HS/college) and RST Bldg 1st Floor (elementary)',
               'staff': '2 school nurses, 2 nursing assistants', 'physician': 'Dr. Jeffrey S. Tamayo M.D.'},

    # Computer Labs (ALL on MST 3rd Floor)
    'cl1': {'name': 'Computer Laboratory 1 (CL1)', 'location': 'MST Building 3rd Floor', 'purpose': 'General IT / Programming'},
    'cl2': {'name': 'Computer Laboratory 2 (CL2)', 'location': 'MST Building 3rd Floor', 'purpose': 'General IT / Programming'},
    'cl3': {'name': 'Computer Laboratory 3 (CL3)', 'location': 'MST Building 3rd Floor', 'purpose': 'General IT / Programming'},
    'cl4': {'name': 'Computer Laboratory 4 (CL4)', 'location': 'MST Building 3rd Floor', 'purpose': 'Networking / Hardware'},
    'cl5': {'name': 'Computer Laboratory 5 (CL5)', 'location': 'MST Building 3rd Floor', 'purpose': 'Networking / Hardware'},
    'cl6': {'name': 'Computer Laboratory 6 (CL6)', 'location': 'MST Building 3rd Floor', 'purpose': 'Multimedia / Design'},
    'cl7': {'name': 'Computer Laboratory 7 (CL7)', 'location': 'MST Building 3rd Floor', 'purpose': 'Multimedia / Design'},
    'cl8': {'name': 'Computer Laboratory 8 (CL8)', 'location': 'MST Building 3rd Floor', 'purpose': 'Software Development'},
    'cl9': {'name': 'Computer Laboratory 9 (CL9)', 'location': 'MST Building 3rd Floor', 'purpose': 'Software Development'},
    'cl10': {'name': 'Computer Laboratory 10 (CL10)', 'location': 'MST Building 3rd Floor', 'purpose': 'Advanced IT / Research'},

    # Other facilities
    'playground': {'name': 'Playground', 'location': 'Open grounds area of the campus'},
    'basic education': {'name': 'Basic Education Building (K-12)', 'location': 'K-12 section of the campus'},
    'k12': {'name': 'Basic Education Building (K-12)', 'location': 'K-12 section of the campus'},
    'main gate': {'name': 'Main Gate', 'location': 'National Highway, Barangay Crossing Rubber, Tupi, South Cotabato 9505'},
    'gate': {'name': 'Main Gate', 'location': 'National Highway, Barangay Crossing Rubber, Tupi, South Cotabato 9505'},
    'language lab': {'name': 'Language Laboratory', 'location': 'Inside MST Building',
                     'features': 'Soundproof cubicles, headsets, audio-visual devices, interactive software'},
    'culinary lab': {'name': 'Culinary / HM Lab', 'location': 'Hospitality Management area',
                     'features': 'Modern culinary tools, simulated real-world hospitality environment'},
    'agriculture farm': {'name': 'Agriculture Farm', 'location': 'External sites at Tucalabong and MAPECON',
                         'features': 'Farm plots, demonstration areas, greenhouses for Agriculture students'},
}

CLASSROOM_BUILDINGS = {
    'cl1': 'MST Building', 'cl2': 'MST Building',
    'cl3': 'MST Building', 'cl4': 'MST Building',
    'cl5': 'MST Building', 'cl6': 'MST Building',
    'cl7': 'MST Building', 'cl8': 'MST Building',
    'cl9': 'MST Building', 'cl10': 'MST Building',
}

# HARDCODED SEAIT KNOWLEDGE BASE - Backup for when DB lookup fails
SEAIT_QA = {
    # ========== ABOUT SEAIT - ALL VARIATIONS ==========
    'what is seait': 'SEAIT is South East Asian Institute of Technology, Inc., a private non-stock, non-profit Higher Education Institution located at National Highway, Crossing Rubber, Tupi, South Cotabato, Philippines 9505.',
    'tell me about seait': 'SEAIT is South East Asian Institute of Technology, Inc., a private non-stock, non-profit Higher Education Institution located at National Highway, Crossing Rubber, Tupi, South Cotabato, Philippines 9505.',
    'what does seait stand for': 'SEAIT stands for South East Asian Institute of Technology.',
    'what does seait mean': 'SEAIT stands for South East Asian Institute of Technology.',
    'when was seait founded': 'SEAIT was founded in February 2006.',
    'when did seait start': 'SEAIT was founded in February 2006.',
    'who founded seait': 'SEAIT was founded by Hon. Reynaldo S. Tamayo Jr. and Mrs. Rochelle P. Tamayo. Both were DOST scholars in BS Information Technology at Cebu Institute of Technology.',
    'who started seait': 'SEAIT was founded by Hon. Reynaldo S. Tamayo Jr. and Mrs. Rochelle P. Tamayo in February 2006.',
    'who is the president of seait': 'SEAIT is led by the Tamayo family. Hon. Reynaldo S. Tamayo Jr. is the founder (former Governor of South Cotabato) and Mrs. Rochelle P. Tamayo is the co-founder.',
    'who is the president': 'SEAIT is led by the Tamayo family. Hon. Reynaldo S. Tamayo Jr. is the founder (former Governor of South Cotabato) and Mrs. Rochelle P. Tamayo is the co-founder.',
    'who is the founder of seait': 'SEAIT was founded by Hon. Reynaldo S. Tamayo Jr. and Mrs. Rochelle P. Tamayo.',
    'who runs seait': 'SEAIT is run by the Tamayo family, led by founder Hon. Reynaldo S. Tamayo Jr. and co-founder Mrs. Rochelle P. Tamayo.',
    'who owns seait': 'SEAIT is owned and operated by the Tamayo family.',
    'is seait free': 'Yes, SEAIT offers completely FREE tuition for ALL college degree programs through UNIFAST funding since 2016.',
    'is seait tuition free': 'Yes, SEAIT offers completely FREE tuition for ALL college degree programs.',
    'is tuition free at seait': 'Yes, SEAIT offers completely FREE tuition for all college programs through UNIFAST since 2016.',
    'how much is tuition at seait': 'Tuition at SEAIT is completely FREE for all college degree programs.',
    'where is seait located': 'SEAIT is located at National Highway, Crossing Rubber, Tupi, South Cotabato, Mindanao, Philippines 9505.',
    'where is seait': 'SEAIT is located at National Highway, Crossing Rubber, Tupi, South Cotabato, Philippines 9505.',
    'what is the address of seait': 'National Highway, Crossing Rubber, Tupi, South Cotabato, Philippines 9505.',
    'what is the contact number of seait': 'The SEAIT phone number is (083) 226-1202.',
    'what is the phone number of seait': 'The SEAIT phone number is (083) 226-1202.',
    
    # ========== BUILDINGS - ALL VARIATIONS ==========
    'how many buildings does seait have': 'SEAIT has 3 main buildings: MST (4 floors), JST (4 floors), and RST (3 floors).',
    'how many buildings': 'SEAIT has 3 main buildings: MST (4 floors), JST (4 floors), and RST (3 floors).',
    'what are the buildings at seait': 'SEAIT has 3 main buildings: MST (Main Science and Technology - 4 floors), JST (Junior Science and Technology - 4 floors), and RST (Research Science and Technology - 3 floors).',
    'where is the mst building': 'The MST Building (Main Science and Technology) is located at the CENTER of SEAIT campus with 4 floors.',
    'where is mst': 'The MST Building is at the CENTER of campus with 4 floors. All computer labs are on the 3rd floor.',
    'what is mst building': 'The MST Building (Main Science and Technology) is the main academic building at the center of campus with 4 floors.',
    'where is the rst building': 'The RST Building (Research Science and Technology) is located at the left-bottom area of campus from the main gate. It has 3 floors.',
    'where is rst': 'The RST Building is near the main gate (left-bottom area) with 3 floors. It houses the Registrar and admin offices.',
    'what is rst building': 'The RST Building (Research Science and Technology) is the admin building with 3 floors near the main gate.',
    'where is the jst building': 'The JST Building (Junior Science and Technology) is located at the BACK of the SEAIT campus with 4 floors.',
    'where is jst': 'The JST Building is at the BACK of campus with 4 floors, housing science and engineering labs.',
    'what is jst building': 'The JST Building (Junior Science and Technology) is at the back of campus with 4 floors for science and engineering.',
    
    # ========== COMPUTER LABS - ALL VARIATIONS ==========
    'where are the computer labs': 'All computer labs CL1-CL10 are located on the 3rd Floor of the MST Building.',
    'where are the computer laboratories': 'All computer labs CL1-CL10 are located on the 3rd Floor of the MST Building.',
    'how many computer labs': 'SEAIT has 10 computer labs (CL1-CL10) all located on the 3rd Floor of the MST Building.',
    'how many computer laboratories': 'SEAIT has 10 computer labs (CL1-CL10) all located on the 3rd Floor of the MST Building.',
    'which floor are the computer labs': 'All computer labs CL1-CL10 are on the 3rd Floor of the MST Building.',
    'where is cl1': 'CL1 is located in the MST Building on the 3rd Floor.',
    'where is cl2': 'CL2 is located in the MST Building on the 3rd Floor.',
    'where is cl3': 'CL3 is located in the MST Building on the 3rd Floor.',
    'where is cl4': 'CL4 is located in the MST Building on the 3rd Floor.',
    'where is cl5': 'CL5 is located in the MST Building on the 3rd Floor.',
    'where is cl6': 'CL6 is located in the MST Building on the 3rd Floor.',
    'where is cl7': 'CL7 is located in the MST Building on the 3rd Floor.',
    'where is cl8': 'CL8 is located in the MST Building on the 3rd Floor.',
    'where is cl9': 'CL9 is located in the MST Building on the 3rd Floor.',
    'where is cl10': 'CL10 is located in the MST Building on the 3rd Floor.',
    
    # ========== OFFICES - ALL VARIATIONS ==========
    'where is the registrar': 'The Registrar Office is located on the 1st Floor of the RST Building with 7 windows, open Mon-Fri 8AM-5PM.',
    'where is the registrar office': 'The Registrar Office is located on the 1st Floor of the RST Building.',
    'where is registrar': 'The Registrar Office is on the 1st Floor of the RST Building, open Mon-Fri 8AM-5PM.',
    'where is the library': 'The Library is located on the ground floor of the main building (left wing). It has 2 floors.',
    'where is library': 'The Library is on the ground floor of the main building (left wing), open Mon-Fri 8AM-6PM, Sat 8AM-12PM.',
    'where is the cict office': 'The CICT Office is located on the 2nd Floor of the MST Building.',
    'where is cict': 'The CICT Office is on the 2nd Floor of the MST Building, headed by Jonathan L. Sucayan MIT.',
    'where is the guidance office': 'The Guidance and Testing Center is located on the 2nd Floor of the RST Building.',
    'where is guidance': 'The Guidance and Testing Center is on the 2nd Floor of the RST Building, headed by Rovi D. Siloterio MAED RGC.',
    'where is the safety office': 'The Safety and Security Office is located on the 2nd Floor of the RST Building.',
    'where is security': 'The Safety and Security Office is on the 2nd Floor of the RST Building, headed by S03 Romel B. Maloloy-on.',
    'where is the cashier': 'The Cashier/Accounting Office is located on the 1st Floor of the RST Building.',
    'where is the accounting office': 'The Accounting Office is located on the 1st Floor of the RST Building.',
    'where is the clinic': 'There are two School Clinics: MST Building 1st Floor (for HS and college students) and RST Building 1st Floor (for elementary students).',
    'where is the school clinic': 'There are two clinics: MST 1st Floor (HS/college) and RST 1st Floor (elementary).',
    
    # ========== FACILITIES - ALL VARIATIONS ==========
    'where is the gymnasium': 'The Gymnasium is located at the back of the campus with basketball and volleyball courts.',
    'where is the gym': 'The Gymnasium is at the back of campus with basketball and volleyball courts.',
    'where is the canteen': 'The Canteen/Cafeteria is located in the center grounds between the MST Building and Gymnasium, open 7AM-6PM daily.',
    'where is the cafeteria': 'The Canteen is in the center grounds between MST Building and Gymnasium, open 7AM-6PM.',
    'where is the comfort room': 'Comfort rooms are available on EVERY FLOOR of ALL buildings (MST, JST, RST), located near stairwells.',
    'where are the restrooms': 'Restrooms are on every floor of all buildings near stairwells.',
    
    # ========== COURSES - ALL VARIATIONS ==========
    'what courses does seait offer': 'SEAIT offers 7 colleges: CICT (BSIT - flagship), Civil Engineering (BSCE), Teacher Education (BSEd), Agriculture, Business and Tourism, Criminology (BSCrim), and Social Work (BSSW).',
    'what courses does seait have': 'SEAIT offers 7 colleges: CICT (BSIT - flagship), Civil Engineering, Teacher Education, Agriculture, Business and Tourism, Criminology, and Social Work.',
    'how many courses does seait have': 'SEAIT has 7 colleges offering various degree programs. The flagship is BSIT.',
    'how many courses that seait have': 'SEAIT has 7 colleges offering various degree programs. The flagship is BSIT.',
    'how many courses': 'SEAIT has 7 colleges: CICT (flagship BSIT), Civil Engineering, Teacher Education, Agriculture, Business and Tourism, Criminology, and Social Work.',
    'what programs does seait offer': 'SEAIT offers 7 colleges with programs including BSIT (flagship), Civil Engineering, Education, Agriculture, Business, Criminology, and Social Work.',
    'what programs': 'SEAIT offers 7 colleges: CICT (BSIT flagship), Civil Engineering, Teacher Education, Agriculture, Business and Tourism, Criminology, and Social Work.',
    'what is the flagship course': 'The flagship course at SEAIT is Bachelor of Science in Information Technology (BSIT).',
    'what is the flagship program': 'The flagship program at SEAIT is BS Information Technology (BSIT).',
    'does seait offer bsit': 'Yes, BS Information Technology (BSIT) is the flagship program at SEAIT.',
    'does seait have bsit': 'Yes, BSIT is the flagship program at SEAIT under the CICT college.',
    'does seait offer criminology': 'Yes, SEAIT offers Bachelor of Science in Criminology (BSCrim).',
    'does seait offer engineering': 'Yes, SEAIT offers Bachelor of Science in Civil Engineering (BSCE).',
    'does seait offer education': 'Yes, SEAIT offers Bachelor of Secondary Education (BSEd) with various majors.',
    'does seait offer agriculture': 'Yes, SEAIT offers Agriculture programs including Animal Science and Crop Science.',
    
    # ========== HISTORY & AWARDS - ALL VARIATIONS ==========
    'what is the history of seait': 'SEAIT was founded in February 2006 as a TESDA vocational school. In 2008, it became a Higher Education Institution. In 2016, UNIFAST was adopted making tuition FREE. In 2021, SEAIT received the Gawad Parangal award.',
    'history of seait': 'SEAIT was founded in February 2006 as a TESDA vocational school. In 2008, it became a Higher Education Institution. In 2016, UNIFAST was adopted making tuition FREE. In 2021, SEAIT received the Gawad Parangal award.',
    'when did seait become free': 'SEAIT adopted UNIFAST in 2016, making tuition completely FREE for all college students.',
    'when did seait start free tuition': 'SEAIT adopted UNIFAST in 2016, making tuition completely FREE.',
    'what award did seait receive': 'In 2021, SEAIT was awarded the Gawad Parangal by CHED Region XII for advocacy of free education for Indigenous Peoples.',
    'what award': 'In 2021, SEAIT received the Gawad Parangal award from CHED Region XII for advocating free education for Indigenous Peoples.',
    
    # ========== VISION/MISSION - ALL VARIATIONS ==========
    'what is the seait vision': 'SEAIT vision is: A premier institution that provides quality education and produces globally empowered individuals.',
    'what is the vision': 'SEAIT vision is: A premier institution that provides quality education and produces globally empowered individuals.',
    'what is the seait mission': 'SEAIT mission is: To produce competent, community-oriented, and globally competitive individuals through holistic education.',
    'what is the mission': 'SEAIT mission is: To produce competent, community-oriented, and globally competitive individuals through holistic education.',
    'what is the seait motto': 'SEAIT motto is: Committed to the Total Development of the Student.',
    'what is the motto': 'SEAIT motto is: Committed to the Total Development of the Student.',
    'what are the core values': 'SEAIT core values are: Service, Excellence, Accountability, Innovation.',
    'what are the seait core values': 'SEAIT core values are Service, Excellence, Accountability, and Innovation (SEAIT).',
}


@app.route("/", methods=["GET"])
def root():
    """Root endpoint - welcome message."""
    return jsonify({
        "service": "TechnoPath Chatbot API",
        "status": "running",
        "version": "2.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "rate": "/rate (POST)",
            "feedback": "/feedback (POST)",
            "learned_facts": "/learned-facts (GET)",
            "learning_stats": "/learning-stats (GET)",
            "analytics": "/analytics (GET)"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Health endpoint for chatbot service."""
    return jsonify({"status": "ok"})


@app.route("/feedback", methods=["POST"])
def record_feedback():
    """Record user feedback for chatbot responses to enable learning."""
    try:
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        rating = data.get('rating')  # 'up' or 'down'
        timestamp = data.get('timestamp') or datetime.now().isoformat()
        
        # Store feedback in database for learning analysis
        init_db()
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating TEXT CHECK(rating IN ('up', 'down')),
                    created_at TEXT NOT NULL,
                    processed INTEGER DEFAULT 0
                )
            ''')
            conn.execute(
                "INSERT INTO feedback (question, answer, rating, created_at) VALUES (?, ?, ?, ?)",
                (question, answer, rating, timestamp)
            )
        
        print(f"[Learning] Feedback recorded: {rating} for question: {question[:50]}...")
        
        # Store as learned answer for ML training (if positive feedback)
        if rating == 'up' and answer:
            store_learned_answer(question, answer, rating)
        
        return jsonify({"status": "ok", "message": "Feedback recorded"})
    except Exception as e:
        print(f"[Learning] Error recording feedback: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def get_learned_answer(question: str, similarity_threshold: float = 0.7):
    """Get learned answer from feedback database using simple similarity matching."""
    try:
        init_db()
        with get_db_connection() as conn:
            # Create learned_answers table if not exists
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating_count INTEGER DEFAULT 0,
                    avg_rating REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Get all learned answers with positive feedback
            cursor = conn.execute(
                "SELECT question, answer, rating_count, avg_rating FROM learned_answers WHERE avg_rating >= 0.6 ORDER BY avg_rating DESC, rating_count DESC"
            )
            learned = cursor.fetchall()
        
        if not learned:
            return None
        
        # Simple similarity matching - check if question contains similar words
        question_words = set(question.lower().split())
        best_match = None
        best_score = 0
        
        for stored_q, stored_a, rating_count, avg_rating in learned:
            stored_words = set(stored_q.lower().split())
            if not stored_words:
                continue
            
            # Calculate Jaccard similarity
            intersection = len(question_words & stored_words)
            union = len(question_words | stored_words)
            score = intersection / union if union > 0 else 0
            
            # Boost score by rating quality
            score *= (0.5 + avg_rating * 0.5)
            
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match = {
                    'question': stored_q,
                    'answer': stored_a,
                    'confidence': round(score * 100, 1),
                    'learned_from': f"{rating_count} user ratings"
                }
        
        return best_match
    except Exception as e:
        print(f"[ML Learning] Error getting learned answer: {e}")
        return None


def store_learned_answer(question: str, answer: str, rating: str):
    """Store or update a learned answer from user feedback."""
    try:
        init_db()
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL UNIQUE,
                    answer TEXT NOT NULL,
                    rating_count INTEGER DEFAULT 0,
                    avg_rating REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Check if question already exists
            cursor = conn.execute("SELECT rating_count, avg_rating FROM learned_answers WHERE question = ?", (question,))
            existing = cursor.fetchone()
            
            rating_value = 1.0 if rating == 'up' else 0.0
            now = datetime.now().isoformat()
            
            if existing:
                count, avg = existing
                # Update with new rating using weighted average
                new_count = count + 1
                new_avg = (avg * count + rating_value) / new_count
                conn.execute(
                    "UPDATE learned_answers SET avg_rating = ?, rating_count = ?, updated_at = ? WHERE question = ?",
                    (new_avg, new_count, now, question)
                )
            else:
                # Insert new learned answer
                conn.execute(
                    "INSERT INTO learned_answers (question, answer, rating_count, avg_rating, created_at, updated_at) VALUES (?, ?, 1, ?, ?, ?)",
                    (question, answer, rating_value, now, now)
                )
                print(f"[ML Learning] New learned answer stored: {question[:50]}...")
        
        return True
    except Exception as e:
        print(f"[ML Learning] Error storing learned answer: {e}")
        return False


@app.route("/learned-answers", methods=["GET"])
def get_all_learned_answers():
    """Get all learned answers for admin review."""
    try:
        init_db()
        with get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating_count INTEGER DEFAULT 0,
                    avg_rating REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            cursor = conn.execute(
                "SELECT id, question, answer, rating_count, avg_rating, created_at FROM learned_answers ORDER BY avg_rating DESC, rating_count DESC"
            )
            answers = [
                {
                    'id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'rating_count': row[3],
                    'avg_rating': row[4],
                    'created_at': row[5]
                }
                for row in cursor.fetchall()
            ]
        return jsonify({'status': 'ok', 'answers': answers, 'count': len(answers)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/analytics", methods=["GET"])
def get_analytics():
    """Get chatbot analytics for the last N days."""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Calculate date threshold
        from datetime import timedelta
        date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Ensure DB is initialized
        init_db()
        
        with get_db_connection() as conn:
            # Total queries in period
            cursor = conn.execute(
                "SELECT COUNT(*) FROM chat_history WHERE created_at >= %s",
                (date_threshold,)
            )
            total_queries = cursor.fetchone()[0]
            
            # Get all queries for analysis
            cursor = conn.execute(
                "SELECT user_message, bot_reply FROM chat_history WHERE created_at >= %s ORDER BY created_at DESC",
                (date_threshold,)
            )
            queries = cursor.fetchall()
        
        # Calculate metrics
        successful = sum(1 for q in queries if not any(fail in q[1].lower() for fail in ['sorry', 'don\'t know', 'not sure', 'unable', 'error']))
        failed = len(queries) - successful
        
        # Get top unanswered/failed queries (for AI Suggestions)
        failed_queries = []
        seen = set()
        for msg, reply in queries:
            if any(fail in reply.lower() for fail in ['sorry', 'don\'t know', 'not sure']):
                key = msg.lower().strip()
                if key not in seen:
                    seen.add(key)
                    failed_queries.append({"user_query": msg, "count": 1})
        
        # Group similar queries
        from collections import Counter
        query_counts = Counter([q[0].lower().strip() for q in queries]) if queries else Counter()
        top_faqs = [{"question": q, "usage_count": c} for q, c in query_counts.most_common(10)]
        
        return jsonify({
            "total_queries": total_queries,
            "successful_queries": successful,
            "failed_queries": failed,
            "success_rate": round((successful / total_queries * 100), 1) if total_queries > 0 else 0,
            "suggestions": {"pending": len(failed_queries)},
            "mode_breakdown": {"online": successful, "offline": 0},
            "top_unanswered_queries": failed_queries[:5],
            "top_faqs": top_faqs,
            "days": days
        })
    except Exception as e:
        import traceback
        print(f"[Analytics Error] {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "success_rate": 0,
            "suggestions": {"pending": 0},
            "mode_breakdown": {"online": 0, "offline": 0},
            "top_unanswered_queries": [],
            "top_faqs": [],
            "days": request.args.get('days', 7, type=int),
            "error": str(e)
        }), 500


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

    # Get last bot reply from history for correction tracking
    last_bot_reply = None
    if history and len(history) >= 2:
        for turn in reversed(history):
            if turn.get('role') == 'assistant' and turn.get('content'):
                last_bot_reply = turn.get('content')
                break

    # Check if user is teaching us something BEFORE generating reply
    teaching = extract_teaching_from_message(message, last_bot_reply)
    learned_something = False
    
    if teaching:
        # Store the learned fact immediately
        if teaching['type'] == 'correction':
            update_learned_faq(teaching['question'], teaching['answer'], source='correction', confidence_boost=15)
            log_correction(teaching['question'], teaching.get('original_reply', ''), teaching['answer'], message)
            learned_something = True
            print(f"[Learning] Correction accepted: {teaching['question'][:50]}...")
        else:
            update_learned_faq(teaching['question'], teaching['answer'], source='user' if teaching['type'] == 'definition' else 'extracted')
            learned_something = True
            print(f"[Learning] New fact from user: {teaching['question'][:50]}...")

    reply = generate_reply(message, history)

    # If we learned something, acknowledge it in the reply
    if learned_something and teaching['type'] != 'correction':
        reply = f"Thank you for teaching me! I've learned: '{teaching['question']}'\n\n" + reply

    fallback_phrases = ["try asking", "i'm here to help", "contact the", "open the navigate"]
    is_successful = not any(p in reply.lower() for p in fallback_phrases)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO chat_history (user_message, bot_reply) VALUES (?, ?)",
            (message, reply),
        )
        message_id = cursor.lastrowid
        conn.commit()

    log_to_django(message, reply, is_successful)

    return jsonify({"reply": reply, "message_id": message_id, "mode": "online" if OPENAI_ENABLED else "offline"})


@app.route("/rate", methods=["POST"])
@limiter.limit("30 per minute")
def rate_message():
    """Rate a chatbot response (up/down) for learning."""
    data = request.get_json(silent=True) or {}
    message_id = data.get("message_id")
    rating = data.get("rating")

    if not message_id or rating not in ("up", "down"):
        return jsonify({"error": "message_id and rating (up/down) required"}), 400

    try:
        init_db()
        with get_db_connection() as conn:
            # Update the rating
            conn.execute(
                "UPDATE chat_history SET rating = ? WHERE id = ?",
                (rating, message_id)
            )

            # If thumbs up, store as learned FAQ
            if rating == "up":
                cursor = conn.execute(
                    "SELECT user_message, bot_reply FROM chat_history WHERE id = ?",
                    (message_id,)
                )
                row = cursor.fetchone()
                if row:
                    question, answer = row
                    # Check if similar question already exists
                    check_cursor = conn.execute(
                        "SELECT id, rating_count FROM learned_faqs WHERE question = ?",
                        (question,)
                    )
                    existing = check_cursor.fetchone()
                    if existing:
                        # Update rating count
                        conn.execute(
                            "UPDATE learned_faqs SET rating_count = rating_count + 1 WHERE id = ?",
                            (existing[0],)
                        )
                    else:
                        # Insert new learned FAQ
                        conn.execute(
                            "INSERT INTO learned_faqs (question, answer) VALUES (?, ?)",
                            (question, answer)
                        )
                        print(f"[Learning] New FAQ learned: {question[:50]}...")

            conn.commit()
        return jsonify({"status": "rated", "rating": rating})
    except Exception as e:
        print(f"[Rate] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/learned-facts", methods=["GET"])
def get_learned_facts():
    """Get all learned facts with confidence scores."""
    try:
        init_db()
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT question, answer, confidence, sources, source_type, created_at FROM learned_faqs ORDER BY confidence DESC, created_at DESC"
            )
            facts = []
            for row in cursor.fetchall():
                facts.append({
                    'question': row[0],
                    'answer': row[1],
                    'confidence': row[2],
                    'sources': row[3],
                    'source_type': row[4],
                    'learned_at': row[5]
                })
            return jsonify({
                'facts': facts,
                'total': len(facts),
                'high_confidence': len([f for f in facts if f['confidence'] >= 70])
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/learning-stats", methods=["GET"])
def get_learning_stats():
    """Get AI learning statistics."""
    try:
        init_db()
        with get_db_connection() as conn:
            # Total learned facts
            total_facts = conn.execute("SELECT COUNT(*) FROM learned_faqs").fetchone()[0]
            # By source type
            source_stats = conn.execute(
                "SELECT source_type, COUNT(*) FROM learned_faqs GROUP BY source_type"
            ).fetchall()
            # Confidence distribution
            high_conf = conn.execute("SELECT COUNT(*) FROM learned_faqs WHERE confidence >= 80").fetchone()[0]
            medium_conf = conn.execute("SELECT COUNT(*) FROM learned_faqs WHERE confidence BETWEEN 60 AND 79").fetchone()[0]
            low_conf = conn.execute("SELECT COUNT(*) FROM learned_faqs WHERE confidence < 60").fetchone()[0]
            # Corrections
            corrections = conn.execute("SELECT COUNT(*) FROM bot_corrections").fetchone()[0] if conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='bot_corrections'"
            ).fetchone() else 0
            
            return jsonify({
                'total_facts_learned': total_facts,
                'by_source': {row[0]: row[1] for row in source_stats},
                'confidence_distribution': {
                    'high_80_100': high_conf,
                    'medium_60_79': medium_conf,
                    'low_below_60': low_conf
                },
                'corrections_received': corrections,
                'ai_status': 'Active Learning Enabled'
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Initialize DB on startup
    init_db()
    _flask_debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5187, debug=_flask_debug)
