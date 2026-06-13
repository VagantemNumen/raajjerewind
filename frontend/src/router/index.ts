import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../components/LandingView.vue'
import ChatView from '../components/ChatView.vue'
import AdminView from '../components/AdminView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: LandingView },
    // Same splash, but always reachable (e.g. from Settings) — the guard below
    // only redirects the first-run '/' entry, never '/welcome'.
    { path: '/welcome', name: 'welcome', component: LandingView },
    { path: '/chat', name: 'chat', component: ChatView },
    { path: '/admin', name: 'admin', component: AdminView },
  ],
})

// Returning visitors who've already started skip the splash and go to the chat.
router.beforeEach((to) => {
  if (to.name === 'landing' && localStorage.getItem('seen_welcome') === 'true') {
    return { name: 'chat' }
  }
})
