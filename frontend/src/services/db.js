import Dexie from 'dexie'

const db = new Dexie('TechnoPathDB')

// Version 2: Full schema matching all 22 Flutter tables
db.version(2).stores({
  // Core entities
  facilities:        '++id, code, map_svg_id, is_deleted, is_active',
  rooms:             '++id, facility_id, code, map_svg_id, floor, is_deleted, is_active',
  departments:       '++id, code, is_active',
  
  // Navigation
  navigation_nodes:  '++id, map_svg_id, node_type, floor, is_deleted, is_active',
  navigation_edges:    '++id, from_node_id, to_node_id, is_deleted',
  
  // Map
  map_markers:       '++id, facility_id, room_id, marker_type, is_active',
  map_labels:        '++id, is_active',
  
  // Chatbot
  faq_entries:       '++id, category, keywords, is_deleted',
  ai_chat_logs:      '++id, mode, created_at',
  
  // Notifications
  notifications:     '++id, type, is_read, created_at',
  notification_types: '++id, name, is_active',
  notification_preferences: '++id, user_id, notification_type_id',
  
  // Feedback & Ratings
  feedback:          '++id, category, synced, created_at',
  ratings:           '++id, facility_id, room_id, category, is_active, created_at',
  feedback_flags:    '++id, rating_id, status, created_at',
  
  // Analytics & Audit
  search_history:    '++id, query, created_at',
  app_usage:         '++id, user_id, session_date',
  usage_analytics:   '++id, event_type, screen_name, created_at',
  admin_audit_log:   '++id, action, entity_type, created_at',
  
  // User & Device
  users:             '++id, username, user_type, is_active',
  device_preferences: '++id, user_id, device_id',
  
  // Config & Connectivity
  app_config:        '++id, config_key',
  connectivity_log:  '++id, is_online, created_at',
  
  // Sync metadata
  sync_meta:         'key'
})

export default db
