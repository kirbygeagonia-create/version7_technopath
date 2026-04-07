# SEAIT Campus Guide System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Frontend (Flutter App)](#frontend-flutter-app)
4. [Backend Services](#backend-services)
5. [Database Structure](#database-structure)
6. [Key Features](#key-features)
7. [File Structure](#file-structure)
8. [Setup & Installation](#setup--installation)
9. [API Reference](#api-reference)
10. [Dependencies](#dependencies)

---

## System Overview

**SEAIT Campus Guide** is a comprehensive mobile navigation application designed for the South East Asian Institute of Technology (SEAIT) campus. The system helps students, faculty, and visitors navigate the campus efficiently through an interactive map, QR code scanning, AI-powered chatbot assistance, and real-time notifications.

### Purpose
- Provide indoor and outdoor campus navigation
- Help users locate buildings, classrooms, and facilities
- Offer AI-assisted guidance through a chatbot
- Enable QR code-based quick location access
- Support administrative functions for campus management

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SEAIT Campus Guide                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Flutter    │  │   Flutter    │  │   Flutter    │         │
│  │   Mobile App │  │   Web App    │  │  Desktop App │         │
│  │  (Android/iOS│  │   (Future)   │  │   (Future)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
│         └─────────────────┴─────────────────┘                  │
│                         │                                       │
│              ┌──────────▼──────────┐                           │
│              │    API Service    │                           │
│              │   (HTTP Client)   │                           │
│              └──────────┬────────┘                           │
│                         │                                       │
│         ┌───────────────┼───────────────┐                    │
│         │               │               │                    │
│    ┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐                │
│    │ Node.js │    │   Dart    │   │ Flask   │                │
│    │Backend  │    │  Backend  │   │Chatbot  │                │
│    │(Port    │    │ (Port     │   │(Port    │                │
│    │ 3000)   │    │  8080)    │   │ 5000)   │                │
│    └────┬────┘    └─────┬─────┘   └────┬────┘                │
│         │               │               │                    │
│    ┌────▼────┐    ┌─────▼─────┐   ┌────▼────┐                │
│    │ SQLite  │    │  SQLite   │   │ SQLite  │                │
│    │ (Main)  │    │ (Guide)   │   │(Chatbot)│                │
│    └─────────┘    └───────────┘   └─────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Flutter (Dart) |
| **Backend API** | Node.js + Express |
| **Chatbot Service** | Python + Flask |
| **Alternative Backend** | Dart + SQLite |
| **Databases** | SQLite |
| **HTTP Client** | `http` package |
| **QR Scanning** | `mobile_scanner` |
| **Local Storage** | `sqflite` |

---

## Frontend (Flutter App)

### Main Entry Point
**File**: `lib/main.dart`

The application uses a Material Design 3 (Material You) theme with an orange color scheme (`Color(0xFFFF9800)`).

### Core Screens

#### 1. Splash Screen (`SplashScreen`)
- Displays SEAIT logo with fade and scale animations
- 3-second duration before navigating to main app
- Orange background theme

#### 2. Home Screen (`HomeScreen`)
- **Interactive Map**: Full-screen map with zoom/pan capabilities
- **Facility Selector**: Dropdown for buildings (Building, RST Building, JST Building, MST Building)
- **Room Selector**: Dropdown for classrooms (CL1, CL2, CL3, CL4, etc.)
- **Search Bar**: Location search with autocomplete
- **Floating Action Buttons**:
  - Menu (building/room/instructor info)
  - Locate (set current position)
  - Rate (app rating)
  - Notifications (with unread badge)
  - Chatbot (AI assistant)
  - QR Scanner

#### 3. Navigate Screen (`NavigateScreen`)
- Turn-by-turn navigation interface
- Route visualization on map
- Building and room selection for navigation

#### 4. Settings Screen (`SettingsScreen`)
- **Login Admin**: Admin authentication
- **Dark Mode**: Theme toggle
- **About Us**: Application information
- **Version Info**: Current version display
- **Check for Updates**: Update checker

### Additional Screens

| Screen | Description |
|--------|-------------|
| `BuildingInfoScreen` | Detailed building information |
| `AdminInfoScreen` | Room administration panel |
| `InstructorInfoScreen` | Faculty directory |
| `EmployeesScreen` | Staff directory |
| `NotificationsScreen` | Push notification history |
| `ChatbotScreen` | AI conversation interface |
| `QRScannerScreen` | QR code scanner |
| `CampusMapScreen` | Full-screen interactive map |

### Navigation Structure

```dart
MainNavigationShell (StatefulWidget)
├── HomeScreen (index: 0)
├── NavigateScreen (index: 1)
└── SettingsScreen (index: 2)
```

---

## Backend Services

### 1. Node.js Backend (`backend/`)

**Main File**: `backend/server.js`

**Purpose**: Primary REST API server for the application

**Endpoints**:
- `/health` - Service health check
- `/api/dashboard/stats` - Dashboard statistics
- `/api/users` - User management (CRUD)
- `/api/facilities` - Facility management
- `/api/rooms` - Room management
- `/api/map-markers` - Map marker positions
- `/api/ratings` - User ratings
- `/api/notifications` - Push notifications
- `/api/chat-history` - Chatbot conversation history
- `/api/app-usage` - Usage analytics

**Database**: `backend/database.js` - SQLite database handler

### 2. Dart Backend (`backend_dart/`)

**Main File**: `backend_dart/bin/server.dart`

**Purpose**: Alternative backend implementation in Dart

**Endpoints**:
- `/health` - Health check
- `/dashboard` - User count statistics
- `/locations` - GET/POST for building-room records

**Database**: `guide_map.db`

**Run Command**:
```bash
cd backend_dart
dart pub get
dart run bin/server.dart
```

### 3. Flask Chatbot Backend (`chatbot_flask/`)

**Main File**: `chatbot_flask/app.py`

**Purpose**: AI-powered chatbot service

**Features**:
- Rule-based response generation (extensible to AI models)
- Chat history storage in SQLite
- CORS enabled for cross-origin requests

**Endpoints**:
- `/health` - Service health check
- `/chat` - POST endpoint for chat messages

**Response Patterns**:
| Input Pattern | Response |
|--------------|----------|
| "hello", "hi" | Greeting + help offer |
| "cl1", "cl2", etc. | Classroom location guidance |
| "building" | Building information |
| Default | Acknowledgment + capability list |

**Run Command**:
```bash
cd chatbot_flask
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## Database Structure

### Local SQLite Database (`DatabaseHelperV2`)

**Tables**:

1. **facilities** - Campus buildings
   - `id` (INTEGER PRIMARY KEY)
   - `name` (TEXT)
   - `description` (TEXT)
   - `image_path` (TEXT)

2. **rooms** - Classrooms and labs
   - `id` (INTEGER PRIMARY KEY)
   - `facility_id` (INTEGER, FOREIGN KEY)
   - `name` (TEXT)
   - `description` (TEXT)
   - `floor` (INTEGER)

3. **map_markers** - Map coordinates
   - `id` (INTEGER PRIMARY KEY)
   - `name` (TEXT)
   - `x` (REAL) - Horizontal position (0-1)
   - `y` (REAL) - Vertical position (0-1)
   - `type` (TEXT) - 'facility' or 'room'

4. **ratings** - User feedback
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (INTEGER)
   - `rating` (INTEGER)
   - `comment` (TEXT)
   - `created_at` (TEXT)

5. **notifications** - Push notifications
   - `id` (INTEGER PRIMARY KEY)
   - `title` (TEXT)
   - `message` (TEXT)
   - `is_read` (INTEGER)
   - `created_at` (TEXT)

6. **chat_history** - Local chat backup
   - `id` (INTEGER PRIMARY KEY)
   - `user_message` (TEXT)
   - `bot_reply` (TEXT)
   - `timestamp` (TEXT)

7. **app_usage** - Analytics
   - `id` (INTEGER PRIMARY KEY)
   - `user_id` (INTEGER)
   - `session_start` (TEXT)
   - `session_end` (TEXT)

8. **users** - User accounts
   - `id` (INTEGER PRIMARY KEY)
   - `username` (TEXT)
   - `password` (TEXT) - Hashed
   - `role` (TEXT) - 'admin' or 'user'
   - `created_at` (TEXT)

---

## Key Features

### 1. Interactive Campus Map
- **Image**: `assets/maps/Example1.jpg`
- **Zoom**: 0.8x to 4.0x with pinch gestures
- **Pan**: Full drag navigation
- **Markers**: Dynamic markers for buildings and rooms
- **Filter**: Show/hide by facility or room type

### 2. QR Code Navigation
- **Scanner**: `mobile_scanner` package
- **Purpose**: Quick location access via QR codes
- **Action**: Scan → Open map at specific entry point

### 3. AI Chatbot
- **Backend**: Flask server (Python)
- **Pattern Matching**: Keyword-based responses
- **History**: SQLite storage for conversation logs
- **Extensibility**: Ready for LLM integration

### 4. Search Functionality
- **Type**: Full-text search across all locations
- **Scope**: Facilities, rooms, descriptions
- **Results**: Filtered list with icons and details

### 5. Rating System
- **Scale**: 1-5 stars
- **Feedback**: Optional text comments
- **Storage**: Local and server-side
- **Admin View**: Dashboard statistics

### 6. Notifications
- **Badge**: Unread count on home screen
- **Types**: System updates, navigation alerts
- **Storage**: Persistent in SQLite

### 7. Admin Panel
- **Authentication**: Secure login
- **Dashboard**: User statistics, ratings, usage
- **Management**: Edit buildings, rooms, markers
- **Reports**: Export usage data

---

## File Structure

```
version4_technopath/
├── android/                 # Android platform files
├── ios/                     # iOS platform files
├── lib/
│   ├── main.dart           # Main application entry
│   ├── api_service.dart     # HTTP client for backend
│   ├── database_helper.dart # SQLite utilities
│   ├── database_helper_v2.dart # Enhanced database handler
│   ├── chatbot_database_helper.dart # Chatbot DB handler
│   ├── feedback/
│   │   └── feedback_screen.dart
│   ├── map/
│   │   ├── campus_map_screen.dart
│   │   ├── SEAITlogo.png
│   │   └── Example1.jpg
│   ├── navigation/
│   │   └── pathfinder.dart  # A* pathfinding algorithm
│   ├── qr/
│   │   └── qr_scanner_screen.dart
│   └── search/
│       └── search_delegate.dart
├── backend/                 # Node.js backend
│   ├── server.js
│   ├── database.js
│   └── database/
│       └── guide_map.db
├── backend_dart/            # Dart backend (alternative)
│   └── bin/
│       └── server.dart
├── chatbot_flask/           # Python chatbot service
│   ├── app.py
│   └── chatbot.db
├── assets/
│   └── maps/               # Map images
├── test/                   # Unit tests
├── pubspec.yaml            # Flutter dependencies
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Flutter SDK 3.11.1+
- Dart SDK 3.0+
- Node.js 18+ (for backend)
- Python 3.9+ (for chatbot)

### Frontend Setup

```bash
# 1. Navigate to project
cd version4_technopath

# 2. Install Flutter dependencies
flutter pub get

# 3. Run the app
flutter run
```

### Backend Setup

**Node.js Backend**:
```bash
cd backend
npm install
npm start
```

**Flask Chatbot**:
```bash
cd chatbot_flask
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

**Dart Backend** (Alternative):
```bash
cd backend_dart
dart pub get
dart run bin/server.dart
```

### Platform-Specific Notes

**Android**:
- Uses `http://10.0.2.2` for localhost access
- Update `AndroidManifest.xml` for internet permission

**iOS**:
- Update `Info.plist` for camera permissions (QR scanning)
- Uses `http://localhost` for backend

**Physical Device**:
- Replace backend URLs with computer's LAN IP
- Ensure devices are on same network

---

## API Reference

### ApiService Class (`lib/api_service.dart`)

Base URL: `http://10.0.2.2:3000/api` (Android emulator)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service status |
| GET | `/dashboard/stats` | Dashboard data |
| GET | `/users` | List all users |
| POST | `/users` | Create user |
| POST | `/users/login` | Authenticate |
| GET | `/facilities` | List facilities |
| POST | `/facilities` | Create facility |
| GET | `/rooms` | List rooms |
| GET | `/facilities/{id}/rooms` | Rooms by facility |
| GET | `/map-markers` | All markers |
| GET | `/ratings` | All ratings |
| GET | `/ratings/average` | Average rating |
| GET | `/notifications` | All notifications |
| GET | `/notifications/unread/count` | Unread count |
| POST | `/chat-history` | Save chat |
| GET | `/app-usage/weekly` | Weekly stats |
| GET | `/app-usage/active-users` | Active user count |

---

## Dependencies

### Flutter Dependencies (`pubspec.yaml`)

| Package | Version | Purpose |
|---------|---------|---------|
| `flutter` | SDK | Core framework |
| `cupertino_icons` | ^1.0.8 | iOS-style icons |
| `http` | ^1.2.2 | HTTP client |
| `sqflite` | ^2.3.2 | SQLite database |
| `path` | ^1.9.0 | File path utilities |
| `crypto` | ^3.0.3 | Cryptographic functions |
| `mobile_scanner` | ^3.5.5 | QR code scanning |
| `flutter_svg` | ^2.0.9 | SVG image support |
| `vector_math` | ^2.1.4 | Mathematical operations |

### Python Dependencies (`chatbot_flask/requirements.txt`)

```
flask
flask-cors
```

### Node.js Dependencies (`backend/package.json`)

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6",
    "cors": "^2.8.5"
  }
}
```

---

## Development Guidelines

### Adding New Features
1. Update database schema in `database_helper_v2.dart`
2. Add API endpoints in `api_service.dart`
3. Create UI components in appropriate screen files
4. Update navigation in `main.dart`

### Theme Customization
Primary color: `Color(0xFFFF9800)` (Orange)
- Update in `ThemeData` in `main.dart`
- Affects all UI components automatically

### Database Migrations
1. Increment version in `database_helper_v2.dart`
2. Add migration logic in `onUpgrade` callback
3. Test on clean installation and upgrade paths

---

## Future Enhancements

- **Real-time Navigation**: GPS integration for outdoor navigation
- **Augmented Reality**: AR waypoints for indoor navigation
- **Voice Commands**: Speech-to-text for accessibility
- **Multi-language Support**: Localization for international students
- **Offline Mode**: Full functionality without internet
- **Push Notifications**: Firebase Cloud Messaging integration
- **Building 3D Models**: Three.js integration for web view

---

## Support & Contact

For technical support or feature requests, contact the SEAIT IT Department.

**Version**: 1.0.0+1  
**Last Updated**: March 2026  
**License**: Private (SEAIT Internal Use)

---

*This documentation is maintained by the SEAIT Campus Guide Development Team.*
