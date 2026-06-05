import { ref } from 'vue'
import { useAuth } from './useAuth'

export interface DocumentEntry {
  source: string
}

export function useAdmin() {
  const { authHeaders, logout } = useAuth()
  const documents = ref<DocumentEntry[]>([])
  const loading = ref(false)
  const uploading = ref(false)
  const error = ref<string | null>(null)

  async function call(url: string, opts: RequestInit = {}): Promise<Response> {
    const res = await fetch(`/api${url}`, {
      ...opts,
      headers: { ...authHeaders(), ...(opts.headers || {}) },
    })
    if (res.status === 401) {
      await logout()
      throw new Error('Session expired. Please log in again.')
    }
    return res
  }

  async function refresh() {
    loading.value = true
    error.value = null
    try {
      const res = await call('/admin/documents')
      if (!res.ok) throw new Error('Could not load documents.')
      const data = (await res.json()) as { documents: DocumentEntry[] }
      documents.value = data.documents
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(source: string) {
    error.value = null
    const res = await call(`/admin/documents/${encodeURIComponent(source)}`, { method: 'DELETE' })
    if (!res.ok) {
      error.value = 'Delete failed.'
      return
    }
    await refresh()
  }

  async function uploadDocument(file: File) {
    error.value = null
    uploading.value = true
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await call('/upload', { method: 'POST', body: fd })
      if (!res.ok) {
        error.value = 'Upload failed.'
        return
      }
      await refresh()
    } finally {
      uploading.value = false
    }
  }

  return { documents, loading, uploading, error, refresh, deleteDocument, uploadDocument }
}
