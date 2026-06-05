import { computed, ref } from 'vue'
import { useStorage } from '@vueuse/core'

export type ChatMessage =
  | { id: string; role: 'user'; content: string }
  | { id: string; role: 'assistant'; content: string; sources: string[] }
  | { id: string; role: 'error'; content: string }

export interface Conversation {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
}

interface AskResponse {
  answer: string
  sources: string[]
  chunks_used?: number
}

const GENERIC_ERROR = "Something went wrong on our end. Please try again in a moment."
const HISTORY_TURNS = 6  // matches backend cap; trimming client-side saves bytes on the wire

const chats = useStorage<Conversation[]>('chats', [])
const activeId = useStorage<string | null>('active_chat_id', null)
const pending = ref(false)

function uid(): string {
  return (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`)
}

function deriveTitle(question: string): string {
  const trimmed = question.trim().replace(/\s+/g, ' ')
  return trimmed.length > 48 ? trimmed.slice(0, 45) + '…' : trimmed
}

function ensureActive(): Conversation {
  const existing = chats.value.find((c) => c.id === activeId.value)
  if (existing) return existing
  const fresh = createChat()
  return fresh
}

function createChat(): Conversation {
  const fresh: Conversation = {
    id: uid(),
    title: 'New chat',
    messages: [],
    createdAt: Date.now(),
  }
  chats.value = [fresh, ...chats.value]
  activeId.value = fresh.id
  // Return the reactive proxy from chats.value, not the plain `fresh` object —
  // otherwise the first push() on its messages array bypasses Vue's tracking
  // and the first answer only shows up after the next question triggers a
  // separate reactive mutation.
  return chats.value[0]!
}

function findChat(id: string): Conversation | undefined {
  return chats.value.find((c) => c.id === id)
}

export function useChats() {
  const activeChat = computed<Conversation | null>(
    () => chats.value.find((c) => c.id === activeId.value) ?? null,
  )

  function newChat() {
    // Reuse an existing empty "New chat" rather than piling them up.
    const reusable = chats.value.find((c) => c.messages.length === 0)
    if (reusable) {
      activeId.value = reusable.id
      return
    }
    createChat()
  }

  function switchChat(id: string) {
    if (findChat(id)) activeId.value = id
  }

  function deleteChat(id: string) {
    chats.value = chats.value.filter((c) => c.id !== id)
    if (activeId.value === id) {
      activeId.value = chats.value[0]?.id ?? null
    }
  }

  async function ask(question: string) {
    const trimmed = question.trim()
    if (!trimmed || pending.value) return

    const chat = ensureActive()
    const isFirstMessage = chat.messages.length === 0

    // Build the history snapshot BEFORE pushing the new user turn — error
    // messages are excluded since they aren't part of the real conversation.
    const history = chat.messages
      .filter((m) => m.role !== 'error')
      .slice(-HISTORY_TURNS)
      .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }))

    chat.messages.push({ id: uid(), role: 'user', content: trimmed })
    if (isFirstMessage) chat.title = deriveTitle(trimmed)
    pending.value = true

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed, history }),
      })

      if (!res.ok) {
        chat.messages.push({ id: uid(), role: 'error', content: GENERIC_ERROR })
        return
      }

      const data = (await res.json()) as AskResponse
      chat.messages.push({
        id: uid(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources ?? [],
      })
    } catch {
      chat.messages.push({ id: uid(), role: 'error', content: GENERIC_ERROR })
    } finally {
      pending.value = false
    }
  }

  return {
    chats,
    activeChat,
    activeId,
    pending,
    newChat,
    switchChat,
    deleteChat,
    ask,
  }
}
