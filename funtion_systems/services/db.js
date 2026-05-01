import Dexie from 'dexie'

const db = new Dexie('TechnoPathDB')

// Version 5: Remove all unused IndexedDB tables
// Removed: search_history, device_preferences, ratings, feedback_flags,
//          notification_types, notification_preferences, users, admin_audit_log
// These were defined but never read or written in frontend code.
db.version(5).stores({
  // Core entities
  facilities:        '++id, code, map_svg_id, is_deleted',
  rooms:             '++id, facility_id, code, map_svg_id, floor, is_deleted',
  departments:       '++id, code, is_active',

  // Navigation
  navigation_nodes:  '++id, map_svg_id, node_type, floor, is_deleted',
  navigation_edges:  '++id, from_node_id, to_node_id, is_deleted',

  // Map
  map_markers:       '++id, facility_id, room_id, marker_type, is_deleted',
  map_labels:        '++id, is_deleted',

  // Chatbot
  faq_entries:       '++id, category, keywords, is_deleted',
  ai_chat_logs:      '++id, mode, created_at',

  // Notifications
  notifications:     '++id, type, is_read, source_color, created_at',

  // Feedback (offline queue only — synced to Django when back online)
  feedback:          '++id, category, synced, created_at',

  // Config & sync
  app_config:        '++id, config_key',
  sync_meta:         'key',
}).upgrade(tx => {
  // Drop leftover data from removed tables if they exist
  // Dexie handles table removal automatically; this is a no-op safety guard
  return Promise.resolve()
})

export default db
