<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../composables/useChats'
import { renderMarkdown } from '../lib/markdown'

const props = defineProps<{ message: ChatMessage }>()

const rendered = computed(() =>
  props.message.role === 'assistant' ? renderMarkdown(props.message.content) : '',
)
</script>

<template>
  <div
    data-message
    class="flex w-full scroll-mt-4"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[85%] rounded-2xl px-4 py-3 text-[15px] leading-relaxed shadow-sm"
      :class="{
        'bg-primary text-primary-content rounded-br-md': message.role === 'user',
        'bg-base-200 text-base-content rounded-bl-md': message.role === 'assistant',
        'bg-error/15 text-error border border-error/30': message.role === 'error',
      }"
    >
      <div
        v-if="message.role === 'assistant'"
        class="prose prose-sm dark:prose-invert max-w-none prose-p:my-2 prose-headings:my-3 prose-pre:my-2 prose-ul:my-2 prose-ol:my-2"
        v-html="rendered"
      />
      <p v-else class="whitespace-pre-wrap">{{ message.content }}</p>

      <div
        v-if="message.role === 'assistant' && message.sources.length"
        class="mt-3 border-t border-base-300 pt-2.5"
      >
        <p class="text-xs font-semibold uppercase tracking-wide opacity-50">
          {{ message.sources.length === 1 ? 'Source' : 'Sources' }}
        </p>
        <ul class="mt-1.5 flex flex-col gap-1">
          <li
            v-for="src in message.sources"
            :key="src"
            class="flex items-start gap-2 text-sm opacity-80"
          >
            <svg
              class="mt-0.5 size-3.5 flex-none opacity-60"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6" />
            </svg>
            <span class="break-words">{{ src }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
