import { create } from 'zustand'

interface ThemeStore {
  isDark: boolean
  toggleTheme: () => void
  setTheme: (isDark: boolean) => void
}

export const useThemeStore = create<ThemeStore>((set) => ({
  isDark: false,
  toggleTheme: () => {
    set((state) => {
      const newIsDark = !state.isDark
      // Save to localStorage
      localStorage.setItem('theme', newIsDark ? 'dark' : 'light')
      // Update DOM
      if (newIsDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      return { isDark: newIsDark }
    })
  },
  setTheme: (isDark: boolean) => {
    set(() => {
      // Save to localStorage
      localStorage.setItem('theme', isDark ? 'dark' : 'light')
      // Update DOM
      if (isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
      return { isDark }
    })
  },
}))
