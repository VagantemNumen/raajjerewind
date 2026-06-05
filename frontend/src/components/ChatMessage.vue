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
        class="mt-3 flex flex-wrap gap-1.5"
      >
        <span
          v-for="src in message.sources"
          :key="src"
          class="badge badge-sm badge-ghost"
        >
          {{ src }}
        </span>
      </div>
    </div>
  </div>
</template>
