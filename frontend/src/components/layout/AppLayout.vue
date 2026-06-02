<template>
  <div class="app-layout">
    <Sidebar />
    <div class="main-area" :class="{ collapsed: appStore.sidebarCollapsed }">
      <HeaderBar />
      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useEquipmentStore } from '@/stores/equipment'
import { useChatStore } from '@/stores/chat'
import Sidebar from './Sidebar.vue'
import HeaderBar from './HeaderBar.vue'

const appStore = useAppStore()
const equipmentStore = useEquipmentStore()
const chatStore = useChatStore()

onMounted(() => {
  equipmentStore.initMockData()
  chatStore.initMockData()
})
</script>

<style lang="scss" scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100%;
  background: $dark-bg-solid;
  overflow: hidden;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: $sidebar-width;
  transition: margin-left 0.3s ease;
  overflow: hidden;

  &.collapsed {
    margin-left: $sidebar-collapsed-width;
  }
}

.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  background: $dark-bg;
}
</style>
