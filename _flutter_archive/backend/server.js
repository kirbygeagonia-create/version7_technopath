const express = require('express');
const cors = require('cors');
const { dbAsync } = require('./database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// ========== USERS ROUTES ==========
// Get all users
app.get('/api/users', async (req, res) => {
  try {
    const users = await dbAsync.all('SELECT id, username, role, created_at FROM users ORDER BY id');
    res.json({ success: true, data: users });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get single user
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await dbAsync.get('SELECT id, username, role, created_at FROM users WHERE id = ?', [req.params.id]);
    if (!user) return res.status(404).json({ success: false, error: 'User not found' });
    res.json({ success: true, data: user });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Login
app.post('/api/users/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await dbAsync.get('SELECT * FROM users WHERE username = ? AND password = ?', [username, password]);
    if (!user) return res.status(401).json({ success: false, error: 'Invalid credentials' });
    res.json({ success: true, data: { id: user.id, username: user.username, role: user.role } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create user
app.post('/api/users', async (req, res) => {
  try {
    const { username, password, role = 'user' } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
      [username, password, role]
    );
    res.status(201).json({ success: true, data: { id: result.id, username, role } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Update user
app.put('/api/users/:id', async (req, res) => {
  try {
    const { username, password, role } = req.body;
    let sql = 'UPDATE users SET ';
    let params = [];
    let updates = [];
    
    if (username) { updates.push('username = ?'); params.push(username); }
    if (password) { updates.push('password = ?'); params.push(password); }
    if (role) { updates.push('role = ?'); params.push(role); }
    
    if (updates.length === 0) return res.status(400).json({ success: false, error: 'No fields to update' });
    
    sql += updates.join(', ') + ' WHERE id = ?';
    params.push(req.params.id);
    
    await dbAsync.run(sql, params);
    res.json({ success: true, message: 'User updated' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete user
app.delete('/api/users/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM users WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'User deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== FACILITIES ROUTES ==========
// Get all facilities
app.get('/api/facilities', async (req, res) => {
  try {
    const facilities = await dbAsync.all('SELECT * FROM facilities ORDER BY name');
    res.json({ success: true, data: facilities });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get single facility
app.get('/api/facilities/:id', async (req, res) => {
  try {
    const facility = await dbAsync.get('SELECT * FROM facilities WHERE id = ?', [req.params.id]);
    if (!facility) return res.status(404).json({ success: false, error: 'Facility not found' });
    res.json({ success: true, data: facility });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create facility
app.post('/api/facilities', async (req, res) => {
  try {
    const { name, description } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO facilities (name, description) VALUES (?, ?)',
      [name, description]
    );
    res.status(201).json({ success: true, data: { id: result.id, name, description } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Update facility
app.put('/api/facilities/:id', async (req, res) => {
  try {
    const { name, description } = req.body;
    await dbAsync.run(
      'UPDATE facilities SET name = ?, description = ? WHERE id = ?',
      [name, description, req.params.id]
    );
    res.json({ success: true, message: 'Facility updated' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete facility
app.delete('/api/facilities/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM facilities WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Facility deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== ROOMS ROUTES ==========
// Get all rooms
app.get('/api/rooms', async (req, res) => {
  try {
    const rooms = await dbAsync.all(`
      SELECT r.*, f.name as facility_name 
      FROM rooms r 
      LEFT JOIN facilities f ON r.facility_id = f.id 
      ORDER BY r.name
    `);
    res.json({ success: true, data: rooms });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get rooms by facility
app.get('/api/facilities/:id/rooms', async (req, res) => {
  try {
    const rooms = await dbAsync.all('SELECT * FROM rooms WHERE facility_id = ? ORDER BY name', [req.params.id]);
    res.json({ success: true, data: rooms });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get single room
app.get('/api/rooms/:id', async (req, res) => {
  try {
    const room = await dbAsync.get('SELECT * FROM rooms WHERE id = ?', [req.params.id]);
    if (!room) return res.status(404).json({ success: false, error: 'Room not found' });
    res.json({ success: true, data: room });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create room
app.post('/api/rooms', async (req, res) => {
  try {
    const { name, facility_id, description } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO rooms (name, facility_id, description) VALUES (?, ?, ?)',
      [name, facility_id, description]
    );
    res.status(201).json({ success: true, data: { id: result.id, name, facility_id, description } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Update room
app.put('/api/rooms/:id', async (req, res) => {
  try {
    const { name, facility_id, description } = req.body;
    await dbAsync.run(
      'UPDATE rooms SET name = ?, facility_id = ?, description = ? WHERE id = ?',
      [name, facility_id, description, req.params.id]
    );
    res.json({ success: true, message: 'Room updated' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete room
app.delete('/api/rooms/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM rooms WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Room deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== MAP MARKERS ROUTES ==========
// Get all markers
app.get('/api/map-markers', async (req, res) => {
  try {
    const markers = await dbAsync.all('SELECT * FROM map_markers ORDER BY name');
    res.json({ success: true, data: markers });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get single marker
app.get('/api/map-markers/:id', async (req, res) => {
  try {
    const marker = await dbAsync.get('SELECT * FROM map_markers WHERE id = ?', [req.params.id]);
    if (!marker) return res.status(404).json({ success: false, error: 'Marker not found' });
    res.json({ success: true, data: marker });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create marker
app.post('/api/map-markers', async (req, res) => {
  try {
    const { name, x_position, y_position, type } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO map_markers (name, x_position, y_position, type) VALUES (?, ?, ?, ?)',
      [name, x_position, y_position, type]
    );
    res.status(201).json({ success: true, data: { id: result.id, name, x_position, y_position, type } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Update marker
app.put('/api/map-markers/:id', async (req, res) => {
  try {
    const { name, x_position, y_position, type } = req.body;
    await dbAsync.run(
      'UPDATE map_markers SET name = ?, x_position = ?, y_position = ?, type = ? WHERE id = ?',
      [name, x_position, y_position, type, req.params.id]
    );
    res.json({ success: true, message: 'Marker updated' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete marker
app.delete('/api/map-markers/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM map_markers WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Marker deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== RATINGS ROUTES ==========
// Get all ratings
app.get('/api/ratings', async (req, res) => {
  try {
    const ratings = await dbAsync.all(`
      SELECT r.*, u.username 
      FROM ratings r 
      LEFT JOIN users u ON r.user_id = u.id 
      ORDER BY r.created_at DESC
    `);
    res.json({ success: true, data: ratings });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get average rating
app.get('/api/ratings/average', async (req, res) => {
  try {
    const result = await dbAsync.get('SELECT AVG(rating) as average FROM ratings');
    res.json({ success: true, data: { average: result.average || 0 } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create rating
app.post('/api/ratings', async (req, res) => {
  try {
    const { user_id, rating, comment } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO ratings (user_id, rating, comment) VALUES (?, ?, ?)',
      [user_id, rating, comment]
    );
    res.status(201).json({ success: true, data: { id: result.id, user_id, rating, comment } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete rating
app.delete('/api/ratings/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM ratings WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Rating deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== NOTIFICATIONS ROUTES ==========
// Get all notifications
app.get('/api/notifications', async (req, res) => {
  try {
    const notifications = await dbAsync.all('SELECT * FROM notifications ORDER BY created_at DESC');
    res.json({ success: true, data: notifications });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get unread count
app.get('/api/notifications/unread/count', async (req, res) => {
  try {
    const result = await dbAsync.get('SELECT COUNT(*) as count FROM notifications WHERE is_read = 0');
    res.json({ success: true, data: { count: result.count } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create notification
app.post('/api/notifications', async (req, res) => {
  try {
    const { title, message } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO notifications (title, message) VALUES (?, ?)',
      [title, message]
    );
    res.status(201).json({ success: true, data: { id: result.id, title, message, is_read: 0 } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Mark as read
app.put('/api/notifications/:id/read', async (req, res) => {
  try {
    await dbAsync.run('UPDATE notifications SET is_read = 1 WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Notification marked as read' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Delete notification
app.delete('/api/notifications/:id', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM notifications WHERE id = ?', [req.params.id]);
    res.json({ success: true, message: 'Notification deleted' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== CHAT HISTORY ROUTES ==========
// Get all chat history
app.get('/api/chat-history', async (req, res) => {
  try {
    const limit = req.query.limit || 50;
    const chats = await dbAsync.all(
      'SELECT * FROM chat_history ORDER BY created_at DESC LIMIT ?',
      [limit]
    );
    res.json({ success: true, data: chats });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Create chat entry
app.post('/api/chat-history', async (req, res) => {
  try {
    const { message, reply } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO chat_history (message, reply) VALUES (?, ?)',
      [message, reply]
    );
    res.status(201).json({ success: true, data: { id: result.id, message, reply } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Clear chat history
app.delete('/api/chat-history', async (req, res) => {
  try {
    await dbAsync.run('DELETE FROM chat_history');
    res.json({ success: true, message: 'Chat history cleared' });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== APP USAGE / DASHBOARD ROUTES ==========
// Get weekly usage stats
app.get('/api/app-usage/weekly', async (req, res) => {
  try {
    const stats = await dbAsync.all(`
      SELECT session_date, COUNT(DISTINCT user_id) as user_count, SUM(session_duration) as total_duration
      FROM app_usage
      WHERE session_date >= date('now', '-7 days')
      GROUP BY session_date
      ORDER BY session_date DESC
    `);
    res.json({ success: true, data: stats });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Get total active users
app.get('/api/app-usage/active-users', async (req, res) => {
  try {
    const result = await dbAsync.get(`
      SELECT COUNT(DISTINCT user_id) as count 
      FROM app_usage 
      WHERE session_date >= date('now', '-7 days')
    `);
    res.json({ success: true, data: { count: result.count } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Record app usage
app.post('/api/app-usage', async (req, res) => {
  try {
    const { user_id, session_date, session_duration } = req.body;
    const result = await dbAsync.run(
      'INSERT INTO app_usage (user_id, session_date, session_duration) VALUES (?, ?, ?)',
      [user_id, session_date, session_duration]
    );
    res.status(201).json({ success: true, data: { id: result.id } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ========== DASHBOARD SUMMARY ==========
app.get('/api/dashboard/stats', async (req, res) => {
  try {
    const users = await dbAsync.get('SELECT COUNT(*) as count FROM users');
    const facilities = await dbAsync.get('SELECT COUNT(*) as count FROM facilities');
    const rooms = await dbAsync.get('SELECT COUNT(*) as count FROM rooms');
    const markers = await dbAsync.get('SELECT COUNT(*) as count FROM map_markers');
    const ratings = await dbAsync.get('SELECT AVG(rating) as average FROM ratings');
    const activeUsers = await dbAsync.get(`
      SELECT COUNT(DISTINCT user_id) as count 
      FROM app_usage 
      WHERE session_date >= date('now', '-7 days')
    `);
    const chats = await dbAsync.get('SELECT COUNT(*) as count FROM chat_history');
    
    res.json({
      success: true,
      data: {
        totalUsers: users.count,
        totalFacilities: facilities.count,
        totalRooms: rooms.count,
        totalMapMarkers: markers.count,
        averageRating: ratings.average || 0,
        activeUsers: activeUsers.count,
        totalChatInteractions: chats.count
      }
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ success: true, message: 'API is running' });
});

// Start server
app.listen(PORT, () => {
  console.log(`SEAIT Admin Backend running on port ${PORT}`);
  console.log(`API available at http://localhost:${PORT}/api`);
});

module.exports = app;
