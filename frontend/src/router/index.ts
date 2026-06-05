import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../components/ChatView.vue'
import AdminView from '../components/AdminView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'chat', component: ChatView },
    { path: '/admin', name: 'admin', component: AdminView },
  ],
})
