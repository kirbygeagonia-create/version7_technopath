# TechnoPath: SEAIT Guide Map and Navigation System

A Progressive Web App (PWA) campus guide and navigation system for
South East Asian Institute of Technology, Inc. (SEAIT).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python Django + Django REST Framework |
| AI Chatbot | Python Flask |
| Frontend | Vue.js 3 + Vite (PWA) |
| 2D Map | Leaflet.js + SVG |
| Offline Storage | IndexedDB (Dexie.js) |
| Pathfinding | Dijkstra (JavaScript, client-side) |
| GPS | Web Geolocation API |
| QR Scanning | jsQR (browser-based) |
| Database | SQLite (dev) / PostgreSQL (prod) |

## Project Structure

```
version4_technopath/
├── backend_django/     ← Django REST API (Python)
├── frontend/           ← Vue.js PWA
├── chatbot_flask/      ← Flask AI Chatbot (Python)
├── assets/             ← Map images and static assets
└── _flutter_archive/   ← Original Flutter app (reference only)
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### Start Backend (Django)
```bash
cd backend_django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Runs at http://localhost:8000
```

### Start Frontend (Vue.js PWA)
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

### Start Chatbot (Flask)
```bash
cd chatbot_flask
python app.py
# Runs at http://localhost:5000
```

## Admin Panel
Access the Django admin at: http://localhost:8000/admin/

Role-based access:
- **Safety and Security Office** — full system control
- **Program Head** — department rooms and announcements
- **Dean** — oversight and validation

