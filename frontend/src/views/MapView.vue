<template>
  <div class="mapview-view">
    <header class="mapview-top-bar">
      <h1>Campus Map</h1>
    </header>

    <div class="mapview-map-container">
      <div class="mapview-map-content">
        <p>Full Interactive Map</p>
        <p>Pan, zoom, and explore buildings</p>
      </div>
    </div>

    <nav class="mapview-bottom-nav">
      <router-link to="/" class="mapview-nav-item">
        <span class="material-icons mapview-icon">home</span>
        <span class="mapview-label">Home</span>
      </router-link>
      <router-link to="/navigate" class="mapview-nav-item">
        <span class="material-icons mapview-icon">explore</span>
        <span class="mapview-label">Navigate</span>
      </router-link>
      <router-link to="/map" class="mapview-nav-item mapview-active">
        <span class="material-icons mapview-icon">map</span>
        <span class="mapview-label">Map</span>
      </router-link>
      <router-link to="/chatbot" class="mapview-nav-item">
        <span class="material-icons mapview-icon">smart_toy</span>
        <span class="mapview-label">Chat</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
/* Styles moved to external file: src/assets/mapview.css */
@import '../assets/mapview.css';
</style>
