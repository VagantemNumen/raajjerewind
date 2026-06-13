<script setup lang="ts">
import { useStorage } from '@vueuse/core'
import { useRouter } from 'vue-router'

const seen = useStorage('seen_welcome', false)
const router = useRouter()

function start() {
  seen.value = true
  router.push('/chat')
}

const features = [
  {
    title: 'Reliable information',
    description: 'Answers grounded in the Social Studies textbooks.',
    path: 'M9 12l2 2 4-4M12 3l7 4v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V7z',
  },
  {
    title: 'Easy to understand',
    description: 'Clear, simple language made for students.',
    path: 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z',
  },
  {
    title: 'Saves time',
    description: 'Instant answers for studying and revision.',
    path: 'M12 8v4l3 2M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z',
  },
  {
    title: 'Anytime, anywhere',
    description: 'Works on any device — even installed like an app.',
    path: 'M5 4h14v12H5zM2 20h20M9 8h6',
  },
]
</script>

<template>
  <div
    class="min-h-dvh flex flex-col items-center justify-center bg-gradient-to-b from-base-200 to-base-100 px-6 py-12 text-base-content"
  >
    <main class="flex w-full max-w-md flex-col items-center text-center">
      <img
        src="/logo.jpg"
        alt="Raajje Rewind"
        class="size-24 shrink-0 rounded-full object-cover shadow-md ring-1 ring-base-300"
      />

      <h1 class="mt-6 text-3xl font-bold tracking-tight">Raajje Rewind</h1>
      <p class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
        Our past, our pride
      </p>

      <ul class="mt-8 grid w-full grid-cols-1 gap-3 text-left sm:grid-cols-2">
        <li
          v-for="feature in features"
          :key="feature.title"
          class="flex items-start gap-3 rounded-xl border border-base-300 bg-base-100/60 p-3"
        >
          <span
            class="flex size-9 flex-none items-center justify-center rounded-lg bg-primary/10 text-primary"
          >
            <svg
              class="size-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path :d="feature.path" />
            </svg>
          </span>
          <span class="min-w-0">
            <span class="block text-sm font-semibold">{{ feature.title }}</span>
            <span class="block text-xs leading-snug opacity-60">{{ feature.description }}</span>
          </span>
        </li>
      </ul>

      <button
        type="button"
        class="btn btn-primary mt-8 w-full max-w-xs gap-2"
        @click="start"
      >
        Start using
        <svg
          class="size-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </button>
    </main>
  </div>
</template>
