<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useTheme } from './composables/useTheme'

// Apply data-theme on every route, including the landing page (which doesn't
// mount the sidebar that otherwise initializes the theme).
useTheme()
</script>

<template>
  <RouterView />
</template>
