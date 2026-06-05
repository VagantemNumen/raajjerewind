<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useChats } from '../composables/useChats'
import ChatMessage from './ChatMessage.vue'

const { activeChat, pending, ask } = useChats()
const input = ref('')
const scrollRef = ref<HTMLElement | null>(null)

async function scrollLastIntoView(behavior: ScrollBehavior = 'smooth') {
  await nextTick()
  const container = scrollRef.value
  if (!container) return
  const last = container.querySelector<HTMLElement>('[data-message]:last-of-type')
  if (last) {
    last.scrollIntoView({ block: 'start', behavior })
  } else {
    container.scrollTo({ top: container.scrollHeight, behavior })
  }
}

watch(() => activeChat.value?.messages.length, () => scrollLastIntoView('smooth'))
watch(() => activeChat.value?.id, () => scrollLastIntoView('auto'))

async function submit() {
  const q = input.value
  input.value = ''
  await ask(q)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="flex h-full flex-col bg-base-100 text-base-content">
    <header class="flex-none flex items-center gap-2 border-b border-base-300 px-4 py-3 sm:px-6 sm:py-4">
      <label
        for="sidebar-toggle"
        class="btn btn-ghost btn-sm lg:hidden"
        aria-label="Open chats"
      >
        ☰
      </label>
      <h1 class="flex-1 min-w-0 truncate text-lg font-semibold tracking-tight">
        {{ activeChat?.title || 'New chat' }}
      </h1>
      <RouterLink
        to="/admin"
        class="link link-hover text-xs opacity-40 hover:opacity-80"
      >
        admin
      </RouterLink>
    </header>

    <main
      ref="scrollRef"
      class="flex-1 min-h-0 overflow-y-auto px-4 py-6 sm:px-6"
    >
      <div class="mx-auto flex max-w-2xl flex-col gap-4">
        <div
          v-if="!activeChat || !activeChat.messages.length"
          class="mt-12 text-center opacity-60"
        >
          <p class="text-sm">Try asking something like</p>
          <p class="mt-1 text-base">"Who was Sultan Mohamed Thakurufaanu?"</p>
        </div>

        <TransitionGroup name="msg" tag="div" class="flex flex-col gap-4">
          <ChatMessage
            v-for="m in activeChat?.messages ?? []"
            :key="m.id"
            :message="m"
          />
        </TransitionGroup>

        <div
          v-if="pending"
          class="flex items-center gap-1.5 px-2 opacity-60"
        >
          <span class="size-2 animate-bounce rounded-full bg-base-content [animation-delay:-0.3s]" />
          <span class="size-2 animate-bounce rounded-full bg-base-content [animation-delay:-0.15s]" />
          <span class="size-2 animate-bounce rounded-full bg-base-content" />
        </div>
      </div>
    </main>

    <footer class="flex-none border-t border-base-300 bg-base-100/90 backdrop-blur px-4 py-4 sm:px-6">
      <div class="mx-auto flex max-w-2xl items-end gap-2">
        <textarea
          v-model="input"
          name="question"
          rows="1"
          placeholder="Ask a question…"
          class="textarea textarea-bordered flex-1 resize-none rounded-2xl"
          :disabled="pending"
          @keydown="onKeydown"
        />
        <button
          type="button"
          class="btn btn-primary rounded-2xl"
          :disabled="pending || !input.trim()"
          @click="submit"
        >
          Send
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.msg-enter-active {
  transition: opacity 200ms ease, transform 200ms ease;
}
.msg-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
</style>
