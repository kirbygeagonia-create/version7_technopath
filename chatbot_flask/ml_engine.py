"""
Hybrid AI Chatbot Engine (Phase 2 of HYBRID AI BUILD)
Components:
- ML Intent Classifier (SVM with TF-IDF)
- NLP Entity Extractor (spaCy/Regex)
- Response Router (Confidence-based)
- GPT-3.5 Integration (with history)
- Continuous Learning Loop (via ratings + retraining)
"""

import os
import re
import json
import random
import requests
import openai
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

# Simple NLP without heavy dependencies
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    nlp = None

# ML dependencies
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    import joblib
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: Dict[str, str]
    requires_clarification: bool


@dataclass
class ChatResponse:
    text: str
    source: str  # 'ml', 'faq', 'gpt', 'clarification'
    intent: Optional[str]
    confidence: float
    suggested_followups: List[str]
    entity_data: Dict[str, str]


class EntityExtractor:
    """Extract entities like rooms, buildings, times from queries."""

    # Room patterns
    ROOM_PATTERNS = [
        r'(?:room|lab|classroom|laboratory)\s*(?:number)?\s*(\d+[a-z]?)',
        r'\b(cl|cr|lab)\s*(\d+[a-z]?)\b',
        r'\b(\d{3,4}[a-z]?)\b',  # Room numbers like 301, 302A
    ]

    # Building patterns
    BUILDING_KEYWORDS = {
        'mst': ['mst', 'main science', 'science building', 'm.s.t'],
        'jst': ['jst', 'junior science', 'j.s.t'],
        'rst': ['rst', 'registrar', 'r.s.t', 'admin building'],
        'library': ['library', 'learning resource', 'lrc'],
        'gym': ['gym', 'gymnasium', 'sports'],
        'cafeteria': ['cafeteria', 'canteen', 'food court', 'tambayan'],
    }

    # Time patterns
    TIME_PATTERNS = [
        r'(\d{1,2}):?(\d{2})?\s*(am|pm)',
        r'(morning|afternoon|evening|lunch|dinner)',
    ]

    # Academic terms
    ACADEMIC_TERMS = {
        'semester': ['semester', 'term', 'academic year', 'school year'],
        'course': ['course', 'subject', 'class', 'program'],
        'enrollment': ['enrollment', 'registration', 'admission', 'enroll'],
        'grade': ['grade', 'grades', 'transcript', 'gpa'],
    }

    def extract(self, query: str) -> Dict[str, str]:
        """Extract all entities from a query."""
        query_lower = query.lower()
        entities = {}

        # Extract room
        for pattern in self.ROOM_PATTERNS:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                entities['room'] = match.group(1) if len(match.groups()) == 1 else match.group(2)
                break

        # Extract building
        for building, keywords in self.BUILDING_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entities['building'] = building.upper()
                    break
            if 'building' in entities:
                break

        # Extract time
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                entities['time'] = match.group(0)
                break

        # Extract academic terms
        for term_type, keywords in self.ACADEMIC_TERMS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entities['academic_term'] = term_type
                    break
            if 'academic_term' in entities:
                break

        # Use spaCy if available for NER
        if SPACY_AVAILABLE and nlp:
            doc = nlp(query)
            for ent in doc.ents:
                if ent.label_ == 'TIME':
                    entities['time_spacy'] = ent.text
                elif ent.label_ == 'DATE':
                    entities['date'] = ent.text
                elif ent.label_ == 'ORG':
                    entities['organization'] = ent.text

        return entities


class MLIntentClassifier:
    """SVM-based intent classifier with TF-IDF features."""

    INTENT_LABELS = [
        'library_hours', 'registrar', 'dean_office', 'room_location',
        'schedule', 'admission', 'scholarship', 'it_support',
        'safety_security', 'general'
    ]

    CONFIDENCE_THRESHOLD_HIGH = 0.75
    CONFIDENCE_THRESHOLD_LOW = 0.40

    def __init__(self, model_path: str = 'intent_model.pkl'):
        self.model_path = model_path
        self.pipeline = None
        self.is_trained = False
        self.training_data = []
        self._load_model()

    def _load_model(self):
        """Load pre-trained model if available."""
        if not SKLEARN_AVAILABLE:
            return

        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                self.is_trained = True
                print(f"[ML] Loaded intent classifier from {self.model_path}")
            except Exception as e:
                print(f"[ML] Error loading model: {e}")
                self._init_model()
        else:
            self._init_model()

    def _init_model(self):
        """Initialize model with default pipeline."""
        if not SKLEARN_AVAILABLE:
            return

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )),
            ('svm', SVC(
                kernel='linear',
                probability=True,
                C=1.0,
                class_weight='balanced'
            ))
        ])
        self.is_trained = False

    def train(self, training_data: List[Dict]):
        """Train the classifier on labeled data."""
        if not SKLEARN_AVAILABLE:
            print("[ML] scikit-learn not available, skipping training")
            return False

        if len(training_data) < 10:
            print(f"[ML] Not enough training data ({len(training_data)} samples)")
            return False

        texts = [item['query_text'] for item in training_data]
        labels = [item['intent_label'] for item in training_data]

        try:
            self.pipeline.fit(texts, labels)
            self.is_trained = True

            # Save model
            joblib.dump(self.pipeline, self.model_path)
            print(f"[ML] Trained on {len(texts)} samples, saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"[ML] Training error: {e}")
            return False

    def predict(self, query: str) -> Tuple[str, float]:
        """Predict intent and return (label, confidence)."""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return 'general', 0.0

        try:
            # Get prediction and probabilities
            prediction = self.pipeline.predict([query])[0]
            probabilities = self.pipeline.predict_proba([query])[0]
            confidence = max(probabilities)

            return prediction, confidence
        except Exception as e:
            print(f"[ML] Prediction error: {e}")
            return 'general', 0.0


class FAQMatcher:
    """Keyword-based FAQ matching as fallback."""

    def __init__(self, faq_entries: List[Dict] = None):
        self.faq_entries = faq_entries or []

    def load_from_db(self, db_connection_func):
        """Load FAQs from database."""
        try:
            conn = db_connection_func()
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, answer, keywords FROM faq_entries WHERE is_deleted = false")
            rows = cursor.fetchall()

            self.faq_entries = []
            for row in rows:
                self.faq_entries.append({
                    'id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'keywords': row[3].lower().split(',') if row[3] else []
                })
            conn.close()
            print(f"[FAQ] Loaded {len(self.faq_entries)} entries")
        except Exception as e:
            print(f"[FAQ] Error loading: {e}")

    def find_match(self, query: str) -> Optional[Tuple[Dict, float]]:
        """Find best matching FAQ entry."""
        query_lower = query.lower()
        words = set(query_lower.split())

        best_match = None
        best_score = 0

        for entry in self.faq_entries:
            score = 0

            # Keyword match
            for keyword in entry['keywords']:
                if keyword.strip() in query_lower:
                    score += 2

            # Word overlap
            entry_words = set(entry['question'].lower().split())
            overlap = len(words & entry_words)
            score += overlap

            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= 2:
            confidence = min(best_score / 5, 0.8)  # Cap at 0.8
            return best_match, confidence

        return None, 0.0


class GPTIntegration:
    """GPT-3.5 integration with conversation history."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(self, query: str, conversation_history: List[Dict] = None,
                         context: Dict = None) -> str:
        """Generate response using GPT-3.5 with context."""
        if not self.client:
            return "[OpenAI API key not configured]"

        # Build system context
        system_msg = """You are TechnoPath AI, a helpful campus guide for SEAIT (South East Asian Institute of Technology) in Tupi, South Cotabato, Philippines.

Campus Facts:
- MST Building: 4 floors, center of campus. CL1-CL10 computer labs on 3rd floor.
- JST Building: 4 floors, behind MST.
- RST Building: 3 floors, left of gate. Registrar on 1F, Guidance/HR/Safety on 2F, IT on 3F.
- Library: Ground floor left wing. Mon-Fri 8AM-6PM, Sat 8AM-12PM.
- Cafeteria: Between MST and Gymnasium, open 7AM-6PM.
- Registrar hours: Mon-Fri 8AM-5PM, Sat 8AM-12PM.

Instructions:
- Give specific, accurate information based on campus facts.
- Be friendly and helpful.
- If you don't know something specific, say so honestly.
- Keep responses concise (2-4 sentences)."""

        # Add context if available
        if context:
            context_str = "\nCurrent context:\n"
            if 'building' in context:
                context_str += f"- User is asking about: {context['building']} building\n"
            if 'room' in context:
                context_str += f"- Room mentioned: {context['room']}\n"
            if 'intent' in context:
                context_str += f"- Detected intent: {context['intent']}\n"
            system_msg += context_str

        # Build messages
        messages = [{"role": "system", "content": system_msg}]

        # Add conversation history (last 5 messages)
        if conversation_history:
            for msg in conversation_history[-5:]:
                role = "user" if msg.get('is_user') else "assistant"
                messages.append({"role": role, "content": msg.get('text', '')})

        # Add current query
        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                top_p=0.9
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[GPT] Error: {e}")
            return "[Error generating AI response]"


class HybridAIEngine:
    """Main hybrid engine combining ML, FAQ, and GPT."""

    def __init__(self, db_connection_func=None, openai_key: str = None):
        self.db_connection_func = db_connection_func
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = MLIntentClassifier()
        self.faq_matcher = FAQMatcher()
        self.gpt = GPTIntegration(openai_key)

        # Load initial data
        self._load_training_data()
        if db_connection_func:
            self.faq_matcher.load_from_db(db_connection_func)

        # Intent-to-followup mapping
        self.followup_suggestions = {
            'library_hours': ["Can I borrow books?", "Library rules?", "Do you have computers?"],
            'registrar': ["Enrollment requirements?", "Transcript of records?", "How to pay tuition?"],
            'room_location': ["What's inside that room?", "Who uses that room?", "Other rooms nearby?"],
            'admission': ["Scholarships available?", "Tuition fees?", "Required documents?"],
            'general': ["Tell me about SEAIT", "Campus map", "Contact information"]
        }

    def _load_training_data(self):
        """Load training data from database if available."""
        if not self.db_connection_func:
            return

        try:
            conn = self.db_connection_func()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT query_text, intent_label
                FROM training_data
                WHERE used_for_training = false OR used_for_training = true
            """)
            rows = cursor.fetchall()

            training_data = [{'query_text': row[0], 'intent_label': row[1]} for row in rows]

            if training_data:
                self.intent_classifier.train(training_data)

                # Mark as used
                cursor.execute("UPDATE training_data SET used_for_training = true")
                conn.commit()

            conn.close()
        except Exception as e:
            print(f"[Engine] Error loading training data: {e}")

    def process_query(self, query: str, conversation_history: List[Dict] = None,
                      session_id: str = None) -> ChatResponse:
        """
        Main entry point: process user query through hybrid pipeline.

        Pipeline:
        1. Extract entities
        2. ML intent classification
        3. Route based on confidence:
           - High (>0.75): FAQ lookup → GPT if needed
           - Medium (0.40-0.75): GPT with intent context
           - Low (<0.40): GPT with clarification
        4. Return response with follow-up suggestions
        """
        conversation_history = conversation_history or []

        # Step 1: Extract entities
        entities = self.entity_extractor.extract(query)

        # Step 2: ML Intent Classification
        intent, confidence = self.intent_classifier.predict(query)

        # Step 3: Route based on confidence
        if confidence >= self.intent_classifier.CONFIDENCE_THRESHOLD_HIGH:
            # High confidence - try FAQ first, then GPT
            faq_match, faq_confidence = self.faq_matcher.find_match(query)

            if faq_match and faq_confidence >= 0.6:
                # Use FAQ answer
                response_text = faq_match['answer']
                source = 'faq'
            else:
                # Use GPT with high-confidence context
                context = {
                    'intent': intent,
                    'confidence': confidence,
                    **entities
                }
                response_text = self.gpt.generate_response(
                    query, conversation_history, context
                )
                source = 'gpt'

        elif confidence >= self.intent_classifier.CONFIDENCE_THRESHOLD_LOW:
            # Medium confidence - GPT with intent guidance
            context = {
                'intent': intent,
                'confidence': confidence,
                **entities
            }
            response_text = self.gpt.generate_response(
                query, conversation_history, context
            )
            source = 'gpt'

        else:
            # Low confidence - GPT with clarification request
            context = {
                'intent': 'unclear',
                'confidence': confidence,
                **entities
            }
            clarification_msg = f"I'm not entirely sure what you're asking about. "
            gpt_response = self.gpt.generate_response(
                query, conversation_history, context
            )
            response_text = f"{clarification_msg}{gpt_response}"
            source = 'clarification'

        # Step 4: Generate follow-up suggestions
        followups = self._generate_followups(intent, entities)

        return ChatResponse(
            text=response_text,
            source=source,
            intent=intent,
            confidence=confidence,
            suggested_followups=followups,
            entity_data=entities
        )

    def _generate_followups(self, intent: str, entities: Dict) -> List[str]:
        """Generate follow-up question suggestions."""
        followups = self.followup_suggestions.get(intent, [])

        # Add entity-based followups
        if 'room' in entities and 'building' in entities:
            followups.append(f"What's inside {entities['building']} {entities['room']}?")

        if 'building' in entities and 'room' not in entities:
            followups.append(f"What rooms are in {entities['building']} building?")

        # Return top 3
        return followups[:3] if followups else ["Can you tell me more?", "What else can I help with?"]

    def submit_rating(self, query: str, response: str, intent: str,
                     rating: str, note: str = None, session_id: str = None) -> bool:
        """
        Submit user rating (thumbs up/down) for continuous learning.
        This gets logged to Django via API for later retraining.
        """
        try:
            django_url = os.getenv('DJANGO_API_URL', 'http://localhost:8000')
            api_url = f"{django_url}/api/chatbot/ratings/"

            data = {
                'query_text': query,
                'response_text': response,
                'intent_detected': intent,
                'rating': rating,
                'rating_note': note,
                'session_id': session_id
            }

            response = requests.post(api_url, json=data, timeout=5)
            return response.status_code == 201
        except Exception as e:
            print(f"[Rating] Error submitting rating: {e}")
            return False

    def retrain_from_ratings(self):
        """
        Retrain the ML model using new ratings data.
        Called periodically (e.g., daily via cron) or after accumulating N new ratings.
        """
        if not self.db_connection_func:
            return False

        try:
            conn = self.db_connection_func()
            cursor = conn.cursor()

            # Get thumbs-down ratings (indicate wrong intent)
            cursor.execute("""
                SELECT query_text, intent_detected
                FROM chat_ratings
                WHERE rating = 'thumbs_down'
                AND created_at > datetime('now', '-7 days')
            """)

            negative_examples = []
            for row in cursor.fetchall():
                # Invert the intent for negative examples
                wrong_intent = row[1]
                # Use 'general' or alternate intent for negative
                negative_examples.append({
                    'query_text': row[0],
                    'intent_label': 'general'  # Reclassify as general
                })

            # Get thumbs-up ratings (confirm correct intent)
            cursor.execute("""
                SELECT query_text, intent_detected
                FROM chat_ratings
                WHERE rating = 'thumbs_up'
                AND created_at > datetime('now', '-7 days')
            """)

            positive_examples = [
                {'query_text': row[0], 'intent_label': row[1]}
                for row in cursor.fetchall()
            ]

            conn.close()

            # Combine with existing training data
            all_training = positive_examples + negative_examples

            if len(all_training) >= 10:
                success = self.intent_classifier.train(all_training)
                if success:
                    print(f"[Retrain] Successfully retrained on {len(all_training)} ratings")
                return success
            else:
                print(f"[Retrain] Not enough new ratings ({len(all_training)})")
                return False

        except Exception as e:
            print(f"[Retrain] Error: {e}")
            return False


# Convenience function for backward compatibility
def generate_response(user_input: str, session_id: str = "default",
                     conversation_history: List[Dict] = None,
                     db_connection_func=None, openai_key: str = None) -> Dict:
    """
    Backward-compatible wrapper for the hybrid engine.
    Returns a dict with the response and metadata.
    """
    engine = HybridAIEngine(db_connection_func, openai_key)
    result = engine.process_query(user_input, conversation_history, session_id)

    return {
        'response': result.text,
        'source': result.source,
        'intent': result.intent,
        'confidence': result.confidence,
        'entities': result.entity_data,
        'suggestions': result.suggested_followups
    }
