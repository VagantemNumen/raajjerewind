<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useAdmin } from '../composables/useAdmin'

const { isAuthed, login, logout } = useAuth()
const { documents, loading, uploading, error, refresh, deleteDocument, uploadDocument } = useAdmin()

const password = ref('')
const loginError = ref<string | null>(null)
const submitting = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(() => {
  if (isAuthed.value) void refresh()
})

async function submitLogin() {
  if (!password.value || submitting.value) return
  submitting.value = true
  loginError.value = null
  const result = await login(password.value)
  submitting.value = false
  password.value = ''
  if (!result.ok) {
    loginError.value = result.error
    return
  }
  await refresh()
}

async function onFile(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  await uploadDocument(file)
  if (fileInput.value) fileInput.value.value = ''
}

async function confirmDelete(source: string) {
  if (!window.confirm(`Delete "${source}" and all its chunks? This can't be undone.`)) return
  await deleteDocument(source)
}

async function doLogout() {
  await logout()
  documents.value = []
}
</script>

<template>
  <div class="min-h-full bg-base-100 text-base-content">
    <header class="border-b border-base-300 px-6 py-4 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold tracking-tight">Admin</h1>
        <p class="text-xs opacity-60">Manage ingested documents.</p>
      </div>
      <div class="flex items-center gap-2">
        <RouterLink to="/chat" class="link link-hover text-sm opacity-70">← Back to chat</RouterLink>
        <button
          v-if="isAuthed"
          type="button"
          class="btn btn-sm btn-ghost"
          @click="doLogout"
        >
          Sign out
        </button>
      </div>
    </header>

    <main class="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <!-- Login -->
      <form
        v-if="!isAuthed"
        class="card bg-base-200 shadow-sm"
        @submit.prevent="submitLogin"
      >
        <div class="card-body gap-3">
          <h2 class="card-title text-base">Sign in</h2>
          <input
            v-model="password"
            type="password"
            name="password"
            placeholder="Admin password"
            class="input input-bordered w-full"
            autocomplete="current-password"
            autofocus
          />
          <p v-if="loginError" class="text-sm text-error">{{ loginError }}</p>
          <button
            type="submit"
            class="btn btn-primary self-end"
            :disabled="!password || submitting"
          >
            {{ submitting ? 'Signing in…' : 'Sign in' }}
          </button>
        </div>
      </form>

      <!-- Admin panel -->
      <div v-else class="flex flex-col gap-6">
        <section class="card bg-base-200 shadow-sm">
          <div class="card-body gap-3">
            <h2 class="card-title text-base">Add a document</h2>
            <p class="text-sm opacity-70">
              Upload a PDF. If a document with the same filename already exists, its chunks will be replaced.
            </p>
            <div class="flex items-center gap-2">
              <input
                ref="fileInput"
                type="file"
                name="pdf"
                accept="application/pdf"
                class="file-input file-input-bordered flex-1"
                :disabled="uploading"
                @change="onFile"
              />
              <span v-if="uploading" class="loading loading-spinner loading-sm" />
            </div>
            <p v-if="uploading" class="text-xs opacity-60">
              Embedding chunks — this can take a minute for large PDFs.
            </p>
          </div>
        </section>

        <section class="card bg-base-200 shadow-sm">
          <div class="card-body gap-3">
            <div class="flex items-center justify-between">
              <h2 class="card-title text-base">Documents</h2>
              <button
                type="button"
                class="btn btn-sm btn-ghost"
                :disabled="loading"
                @click="refresh"
              >
                Refresh
              </button>
            </div>

            <p v-if="error" class="text-sm text-error">{{ error }}</p>

            <div v-if="loading" class="flex items-center gap-2 opacity-70">
              <span class="loading loading-spinner loading-sm" />
              <span class="text-sm">Loading…</span>
            </div>

            <div
              v-else-if="!documents.length"
              class="rounded-lg border border-base-300 px-4 py-6 text-center text-sm opacity-60"
            >
              No documents yet. Upload one above.
            </div>

            <ul v-else class="divide-y divide-base-300">
              <li
                v-for="doc in documents"
                :key="doc.source"
                class="flex items-center justify-between gap-3 py-2"
              >
                <span class="truncate text-sm">{{ doc.source }}</span>
                <button
                  type="button"
                  class="btn btn-xs btn-ghost text-error"
                  @click="confirmDelete(doc.source)"
                >
                  Delete
                </button>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>
