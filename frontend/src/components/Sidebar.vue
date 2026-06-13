<script setup lang="ts">
import { useChats } from '../composables/useChats'
import { useTheme, type ThemeMode } from '../composables/useTheme'

const { chats, activeId, newChat, switchChat, deleteChat } = useChats()
const { mode, setMode } = useTheme()

const themeOptions: { value: ThemeMode; label: string; icon: string }[] = [
  { value: 'light', label: 'Light', icon: '☀' },
  { value: 'dark', label: 'Dark', icon: '☾' },
  { value: 'system', label: 'System', icon: '✦' },
]

function onDelete(e: Event, id: string) {
  e.stopPropagation()
  if (window.confirm('Delete this chat?')) deleteChat(id)
}
</script>

<template>
  <aside class="flex h-full w-72 flex-col border-r border-base-300 bg-base-200">
    <div class="flex-none flex items-center gap-3 border-b border-base-300 px-4 py-3">
      <img
        src="/logo.jpg"
        alt="Raajje Rewind"
        class="size-10 shrink-0 rounded-full object-cover ring-1 ring-base-300"
      />
      <div class="min-w-0">
        <h1 class="text-sm font-semibold tracking-tight">Raajje Rewind</h1>
        <p class="text-xs opacity-60 leading-snug">
          Ask questions about Maldives and its history.
        </p>
      </div>
    </div>

    <div class="flex-none px-3 pt-3">
      <button
        type="button"
        class="btn btn-primary btn-sm w-full justify-start gap-2"
        @click="newChat"
      >
        <span class="text-base leading-none">+</span>
        New chat
      </button>
    </div>

    <nav class="mt-3 flex-1 min-h-0 overflow-y-auto px-2 pb-3">
      <p v-if="!chats.length" class="px-3 py-6 text-center text-xs opacity-50">
        Your chats will appear here.
      </p>

      <ul class="flex flex-col gap-0.5">
        <li v-for="chat in chats" :key="chat.id">
          <button
            type="button"
            class="group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition"
            :class="
              chat.id === activeId
                ? 'bg-base-300 text-base-content'
                : 'text-base-content/80 hover:bg-base-300/60'
            "
            @click="switchChat(chat.id)"
          >
            <span class="truncate flex-1">{{ chat.title || 'New chat' }}</span>
            <span
              class="opacity-0 group-hover:opacity-60 hover:!opacity-100 text-xs"
              role="button"
              tabindex="0"
              aria-label="Delete chat"
              @click="onDelete($event, chat.id)"
              @keydown.enter="onDelete($event, chat.id)"
            >
              ×
            </span>
          </button>
        </li>
      </ul>
    </nav>

    <div class="flex-none border-t border-base-300 px-3 py-3">
      <div class="dropdown dropdown-top w-full">
        <div
          tabindex="0"
          role="button"
          class="btn btn-ghost btn-sm w-full justify-between"
        >
          <span class="flex items-center gap-2">
            <span class="text-base leading-none">⚙</span>
            Settings
          </span>
          <span class="text-xs opacity-60 capitalize">{{ mode }}</span>
        </div>
        <ul
          tabindex="0"
          class="dropdown-content menu bg-base-100 rounded-box z-10 mb-1 w-full gap-0.5 p-2 shadow"
        >
          <li class="menu-title px-2 pb-1 text-xs">Theme</li>
          <li v-for="opt in themeOptions" :key="opt.value">
            <button
              type="button"
              class="flex items-center justify-between"
              :class="{ 'menu-active': mode === opt.value }"
              @click="setMode(opt.value)"
            >
              <span class="flex items-center gap-2">
                <span aria-hidden="true">{{ opt.icon }}</span>
                {{ opt.label }}
              </span>
              <span v-if="mode === opt.value" class="text-xs">✓</span>
            </button>
          </li>
          <li class="menu-title px-2 pb-1 pt-2 text-xs">About</li>
          <li>
            <RouterLink to="/welcome" class="flex items-center gap-2">
              <span aria-hidden="true">✦</span>
              Welcome screen
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </aside>
</template>
