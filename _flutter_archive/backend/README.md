# SEAIT Admin Panel Backend

Node.js/Express backend API for the SEAIT Campus Guide Admin Panel.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/health` - Health check

### Users
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users/login` - Login
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Facilities
- `GET /api/facilities` - Get all facilities
- `GET /api/facilities/:id` - Get facility by ID
- `POST /api/facilities` - Create facility
- `PUT /api/facilities/:id` - Update facility
- `DELETE /api/facilities/:id` - Delete facility

### Rooms
- `GET /api/rooms` - Get all rooms
- `GET /api/facilities/:id/rooms` - Get rooms by facility
- `GET /api/rooms/:id` - Get room by ID
- `POST /api/rooms` - Create room
- `PUT /api/rooms/:id` - Update room
- `DELETE /api/rooms/:id` - Delete room

### Map Markers
- `GET /api/map-markers` - Get all markers
- `GET /api/map-markers/:id` - Get marker by ID
- `POST /api/map-markers` - Create marker
- `PUT /api/map-markers/:id` - Update marker
- `DELETE /api/map-markers/:id` - Delete marker

### Ratings
- `GET /api/ratings` - Get all ratings
- `GET /api/ratings/average` - Get average rating
- `POST /api/ratings` - Create rating
- `DELETE /api/ratings/:id` - Delete rating

### Notifications
- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/unread/count` - Get unread count
- `POST /api/notifications` - Create notification
- `PUT /api/notifications/:id/read` - Mark as read
- `DELETE /api/notifications/:id` - Delete notification

### Chat History
- `GET /api/chat-history` - Get chat history
- `POST /api/chat-history` - Add chat entry
- `DELETE /api/chat-history` - Clear chat history

### App Usage
- `GET /api/app-usage/weekly` - Get weekly usage
- `GET /api/app-usage/active-users` - Get active users count
- `POST /api/app-usage` - Record app usage

## Database

SQLite database is automatically created in `database/guidemap.db`

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

## Port

Server runs on port 3000 by default (configurable via PORT env variable)
