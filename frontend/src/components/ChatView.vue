<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import ChatPanel from './ChatPanel.vue'
</script>

<template>
  <div class="drawer h-dvh lg:drawer-open">
    <input id="sidebar-toggle" type="checkbox" class="drawer-toggle" />

    <div class="drawer-content !overflow-hidden">
      <ChatPanel />
    </div>

    <div class="drawer-side !overflow-hidden z-20">
      <label
        for="sidebar-toggle"
        aria-label="Close sidebar"
        class="drawer-overlay"
      />
      <Sidebar />
    </div>
  </div>
</template>
