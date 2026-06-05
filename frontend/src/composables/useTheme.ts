import { computed, watchEffect } from 'vue'
import { usePreferredDark, useStorage } from '@vueuse/core'

export type ThemeMode = 'light' | 'dark' | 'system'

// Must match the themes registered via @plugin "daisyui" in style.css.
const LIGHT_THEME = 'lofi'
const DARK_THEME = 'dracula'

const mode = useStorage<ThemeMode>('theme_mode', 'system')

export function useTheme() {
  const prefersDark = usePreferredDark()

  const resolved = computed(() => {
    if (mode.value === 'light') return LIGHT_THEME
    if (mode.value === 'dark') return DARK_THEME
    return prefersDark.value ? DARK_THEME : LIGHT_THEME
  })

  watchEffect(() => {
    if (typeof document === 'undefined') return
    document.documentElement.setAttribute('data-theme', resolved.value)
  })

  function setMode(next: ThemeMode) {
    mode.value = next
  }

  return { mode, resolved, setMode }
}
