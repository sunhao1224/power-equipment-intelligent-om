import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const currentPageTitle = ref('可视化大屏')

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setPageTitle(title: string) {
    currentPageTitle.value = title
  }

  return {
    sidebarCollapsed,
    currentPageTitle,
    toggleSidebar,
    setPageTitle
  }
})
