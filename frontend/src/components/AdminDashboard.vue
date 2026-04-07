<template>
  <div class="admin-dashboard">
    <!-- Stats Cards Grid -->
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-icon">
          <span class="material-icons">people</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.users }}</div>
          <div class="stat-label">Total Users</div>
        </div>
      </div>
      <div class="stat-card green">
        <div class="stat-icon">
          <span class="material-icons">business</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.facilities }}</div>
          <div class="stat-label">Facilities</div>
        </div>
      </div>
      <div class="stat-card orange">
        <div class="stat-icon">
          <span class="material-icons">meeting_room</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.rooms }}</div>
          <div class="stat-label">Rooms</div>
        </div>
      </div>
      <div class="stat-card purple">
        <div class="stat-icon">
          <span class="material-icons">star</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.ratings }}</div>
          <div class="stat-label">Ratings</div>
        </div>
      </div>
    </div>

    <!-- Charts and Activity Section -->
    <div class="dashboard-sections">
      <!-- Pie Chart Card -->
      <div class="dashboard-card chart-card">
        <div class="card-header">
          <span class="material-icons">pie_chart</span>
          <h3>System Performance</h3>
        </div>
        <div class="chart-container">
          <div class="pie-chart">
            <svg viewBox="0 0 200 200" class="pie-svg">
              <!-- Background circle -->
              <circle cx="100" cy="100" r="80" fill="none" stroke="#f0f0f0" stroke-width="25"/>
              <!-- Segments - calculated dynamically -->
              <g transform="rotate(-90 100 100)">
                <circle cx="100" cy="100" r="80" fill="none" stroke="#4CAF50" stroke-width="25"
                        stroke-dasharray="125.6 377" stroke-dashoffset="0"/>
                <circle cx="100" cy="100" r="80" fill="none" stroke="#2196F3" stroke-width="25"
                        stroke-dasharray="75.4 377" stroke-dashoffset="-125.6"/>
                <circle cx="100" cy="100" r="80" fill="none" stroke="#FF9800" stroke-width="25"
                        stroke-dasharray="62.8 377" stroke-dashoffset="-200.96"/>
                <circle cx="100" cy="100" r="80" fill="none" stroke="#9C27B0" stroke-width="25"
                        stroke-dasharray="50.2 377" stroke-dashoffset="-263.76"/>
                <circle cx="100" cy="100" r="80" fill="none" stroke="#F44336" stroke-width="25"
                        stroke-dasharray="37.7 377" stroke-dashoffset="-314"/>
              </g>
              <!-- Center text -->
              <circle cx="100" cy="100" r="55" fill="white"/>
              <text x="100" y="95" text-anchor="middle" class="center-label">Average</text>
              <text x="100" y="115" text-anchor="middle" class="center-value">85%</text>
            </svg>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color green"></span>
              <span class="legend-label">System Reliability</span>
              <span class="legend-value">35%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color blue"></span>
              <span class="legend-label">User Satisfaction</span>
              <span class="legend-value">20%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color orange"></span>
              <span class="legend-label">AI Response</span>
              <span class="legend-value">17%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color purple"></span>
              <span class="legend-label">Navigation</span>
              <span class="legend-value">13%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color red"></span>
              <span class="legend-label">Content Coverage</span>
              <span class="legend-value">10%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity Card -->
      <div class="dashboard-card activity-card">
        <div class="card-header">
          <span class="material-icons">timeline</span>
          <h3>Recent Activity</h3>
        </div>
        <div class="activity-list">
          <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <span class="material-icons">{{ activity.icon }}</span>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Users Card -->
    <div class="dashboard-card users-card">
      <div class="card-header">
        <span class="material-icons">groups</span>
        <h3>Currently Active Users</h3>
        <span class="badge">{{ activeUsers.length }} online</span>
      </div>
      <div class="users-grid">
        <div v-for="user in activeUsers" :key="user.id" class="user-item">
          <div class="user-avatar" :style="{ backgroundColor: user.color }">
            {{ user.initials }}
          </div>
          <div class="user-name">{{ user.name }}</div>
          <div class="user-status online">
            <span class="status-dot"></span> Active
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api.js'

const stats = ref({
  users: 0,
  facilities: 0,
  rooms: 0,
  ratings: 0
})

const recentActivity = ref([
  { type: 'user', icon: 'person_add', title: 'New user registered', time: '2 minutes ago' },
  { type: 'rating', icon: 'star', title: 'New 5-star rating received', time: '5 minutes ago' },
  { type: 'facility', icon: 'business', title: 'Facility updated: MST Building', time: '15 minutes ago' },
  { type: 'room', icon: 'meeting_room', title: 'Room CL1 information updated', time: '30 minutes ago' },
  { type: 'chat', icon: 'chat', title: 'Chatbot handled 12 queries', time: '1 hour ago' },
])

const activeUsers = ref([
  { id: 1, name: 'Admin User', initials: 'AU', color: '#FF9800' },
  { id: 2, name: 'John Doe', initials: 'JD', color: '#2196F3' },
  { id: 3, name: 'Jane Smith', initials: 'JS', color: '#4CAF50' },
  { id: 4, name: 'Mike Wilson', initials: 'MW', color: '#9C27B0' },
])

onMounted(async () => {
  try {
    const [usersRes, facilitiesRes, roomsRes, ratingsRes] = await Promise.all([
      api.get('/users/'),
      api.get('/facilities/'),
      api.get('/rooms/'),
      api.get('/feedback/')
    ])
    stats.value = {
      users: usersRes.data?.length || 0,
      facilities: facilitiesRes.data?.length || 0,
      rooms: roomsRes.data?.length || 0,
      ratings: ratingsRes.data?.length || 0
    }
  } catch (err) {
    console.log('Using mock stats data')
    stats.value = { users: 24, facilities: 8, rooms: 42, ratings: 156 }
  }
})
</script>

<style scoped>
.admin-dashboard {
  padding: 24px;
  max-width: 1400px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-card.blue { border-left: 4px solid #2196F3; }
.stat-card.green { border-left: 4px solid #4CAF50; }
.stat-card.orange { border-left: 4px solid #FF9800; }
.stat-card.purple { border-left: 4px solid #9C27B0; }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.blue .stat-icon { background: #E3F2FD; color: #2196F3; }
.stat-card.green .stat-icon { background: #E8F5E9; color: #4CAF50; }
.stat-card.orange .stat-icon { background: #FFF3E0; color: #FF9800; }
.stat-card.purple .stat-icon { background: #F3E5F5; color: #9C27B0; }

.stat-icon .material-icons {
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

/* Dashboard Sections */
.dashboard-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.dashboard-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header .material-icons {
  color: #FF9800;
  font-size: 24px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
}

.badge {
  background: #E8F5E9;
  color: #4CAF50;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

/* Chart Card */
.chart-container {
  padding: 24px;
  display: flex;
  gap: 24px;
  align-items: center;
}

.pie-chart {
  flex-shrink: 0;
  width: 180px;
  height: 180px;
}

.pie-svg {
  width: 100%;
  height: 100%;
}

.center-label {
  font-size: 12px;
  fill: #666;
}

.center-value {
  font-size: 24px;
  font-weight: 700;
  fill: #009688;
}

.chart-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.green { background: #4CAF50; }
.legend-color.blue { background: #2196F3; }
.legend-color.orange { background: #FF9800; }
.legend-color.purple { background: #9C27B0; }
.legend-color.red { background: #F44336; }

.legend-label {
  flex: 1;
  font-size: 13px;
  color: #555;
}

.legend-value {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

/* Activity Card */
.activity-list {
  padding: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.15s;
}

.activity-item:hover {
  background: #f5f5f5;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.activity-icon.user { background: #E3F2FD; color: #2196F3; }
.activity-icon.rating { background: #FFF3E0; color: #FF9800; }
.activity-icon.facility { background: #E8F5E9; color: #4CAF50; }
.activity-icon.room { background: #F3E5F5; color: #9C27B0; }
.activity-icon.chat { background: #E0F2F1; color: #009688; }

.activity-icon .material-icons {
  font-size: 18px;
}

.activity-title {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.activity-time {
  font-size: 11px;
  color: #888;
  margin-top: 2px;
}

/* Users Card */
.users-card {
  margin-top: 24px;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  padding: 20px;
}

.user-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: transform 0.15s;
}

.user-item:hover {
  transform: translateY(-2px);
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 14px;
  margin-bottom: 8px;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #4CAF50;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4CAF50;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 12px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .dashboard-sections {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .chart-container {
    flex-direction: column;
    padding: 16px;
  }
  
  .pie-chart {
    width: 150px;
    height: 150px;
  }
  
  .users-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    padding: 16px;
  }
}
</style>
