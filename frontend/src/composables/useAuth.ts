import { computed } from 'vue'
import { useStorage } from '@vueuse/core'

const token = useStorage<string | null>('admin_token', null)

export function useAuth() {
  async function login(password: string): Promise<{ ok: true } | { ok: false; error: string }> {
    try {
      const res = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })
      if (res.status === 401) return { ok: false, error: 'Wrong password.' }
      if (!res.ok) {
        const detail = await res.json().then((d) => d?.detail).catch(() => null)
        return { ok: false, error: detail || `Server error (${res.status}).` }
      }
      const data = (await res.json()) as { token: string }
      token.value = data.token
      return { ok: true }
    } catch {
      return { ok: false, error: 'Could not reach the server.' }
    }
  }

  async function logout() {
    if (token.value) {
      try {
        await fetch('/api/admin/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token.value}` },
        })
      } catch {
        /* ignore — we clear the local token regardless */
      }
    }
    token.value = null
  }

  function authHeaders(): Record<string, string> {
    return token.value ? { Authorization: `Bearer ${token.value}` } : {}
  }

  return {
    token,
    isAuthed: computed(() => !!token.value),
    login,
    logout,
    authHeaders,
  }
}
