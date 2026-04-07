---
description: How to run and test the Technopath SEAIT Campus Guide application
---

## Prerequisites
- Flutter SDK installed
- Android Studio or VS Code with Flutter extension
- Android emulator or physical device configured

## Run the Application

1. **Navigate to project directory**
   ```bash
   cd c:\Users\User\Desktop\Version4_System\version4_technopath
   ```

2. **Get dependencies**
   // turbo
   ```bash
   flutter pub get
   ```

3. **Run the app**
   // turbo
   ```bash
   flutter run
   ```

## Access Admin Panel

1. **Navigate to Settings tab**
   - Tap the Settings icon in bottom navigation

2. **Login as Admin**
   - Tap "Login Admin" option
   - Enter credentials (default: check DatabaseHelper for seeded admin user)

3. **Admin Dashboard Features**
   - View statistics (Total Users, Facilities, Rooms, Ratings)
   - Manage Facilities: Add, edit, delete campus facilities
   - Manage Rooms: Add, edit, delete rooms by building
   - Manage Admin Users: Create/modify admin accounts
   - View Ratings: See user feedback and ratings
   - Send Notifications: Broadcast messages to all users

## Test Database Functionality

### Facilities Management
1. Go to **Admin Panel > Facilities** tab
2. Tap **+** button to add new facility
3. Fill in:
   - Name (e.g., "New Building")
   - Description (e.g., "Academic building for engineering")
4. Tap **Save**
5. Verify facility appears in list

### Rooms Management
1. Go to **Admin Panel > Rooms** tab
2. Tap **+** button to add new room
3. Fill in:
   - Name (e.g., "MST105")
   - Description (e.g., "Computer Laboratory")
   - Select Facility from dropdown (e.g., "MST Building")
4. Tap **Save**
5. Verify room appears in list

### User Management
1. Go to **Admin Panel > Admin** tab
2. Add new admin user with username and password
3. Assign role (admin/user)
4. Test login with new credentials

### Notifications
1. From **Dashboard** tab, tap "Send Notification"
2. Enter:
   - Title: "Test Notification"
   - Message: "This is a test broadcast message"
3. Tap **Send**
4. Verify notification appears in app (check Notifications screen)

## Test Campus Guide Features

### Search Functionality
1. On **Home** screen, use search bar
2. Type building/room name (e.g., "MST", "CL1")
3. Tap search button or press Enter
4. Select result to highlight on map

### Chatbot (Offline Mode)
1. Tap **Chatbot** icon from Home screen
2. Try quick question chips:
   - "Where is CL1?"
   - "MST Building info"
   - "Library location"
3. Or type custom questions about campus
4. Verify offline responses work without internet

### Navigation
1. Go to **Navigate** tab
2. Set origin (From) and destination (To)
3. Select floor if applicable
4. Tap **Start Navigate**
5. Verify route guidance displays

## Troubleshooting

- **App won't build**: Run `flutter clean` then `flutter pub get`
- **Database issues**: Clear app data in emulator settings
- **Map not loading**: Verify `assets/maps/Example1.jpg` exists
- **Login fails**: Check that admin user exists in database (seeded on first run)

## Development Notes

- Database: SQLite via sqflite package
- State Management: setState (StatefulWidget)
- Offline functionality: Rule-based AI for chatbot (no API required)
- Assets: Images in `assets/maps/`, Logo in `lib/map/`
