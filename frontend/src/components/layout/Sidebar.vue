<template>
  <div class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <!-- Logo区域 -->
    <div class="logo-area">
      <div class="logo-icon">
        <el-icon :size="28"><DataAnalysis /></el-icon>
      </div>
      <transition name="fade">
        <span v-if="!appStore.sidebarCollapsed" class="logo-text">
          电力智能运维
        </span>
      </transition>
    </div>

    <!-- 导航菜单 -->
    <nav class="nav-menu">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <div class="nav-icon-wrapper">
          <el-icon :size="22">
            <component :is="item.icon" />
          </el-icon>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </div>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed" class="nav-label">
            {{ item.label }}
          </span>
        </transition>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed && isActive(item.path)" class="active-indicator" />
        </transition>
      </router-link>
    </nav>

    <!-- 底部折叠按钮 -->
    <div class="sidebar-footer">
      <button class="collapse-btn" @click="appStore.toggleSidebar">
        <el-icon :size="18">
          <Fold v-if="!appStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed">收起菜单</span>
        </transition>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useEquipmentStore } from '@/stores/equipment'
import {
  DataAnalysis,
  ChatDotRound,
  FirstAidKit,
  SetUp,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const equipmentStore = useEquipmentStore()

const menuItems = computed(() => [
  { path: '/dashboard', label: '可视化大屏', icon: 'DataAnalysis' },
  { path: '/chat', label: '运维问答', icon: 'ChatDotRound', badge: null },
  { path: '/diagnosis', label: '故障诊断', icon: 'FirstAidKit', badge: equipmentStore.stats.warning > 0 ? equipmentStore.stats.warning : null },
  { path: '/maintenance', label: '维护决策', icon: 'SetUp' }
])

function isActive(path: string): boolean {
  return route.path === path
}
</script>

<style lang="scss" scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: $sidebar-width;
  background: linear-gradient(180deg, #1a0533 0%, #2d1054 100%);
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width 0.3s ease;
  overflow: hidden;

  &.collapsed {
    width: $sidebar-collapsed-width;
  }
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  border-bottom: 1px solid $border-color;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, $primary-color, $accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
  white-space: nowrap;
  letter-spacing: 1px;
}

.nav-menu {
  flex: 1;
  padding: 16px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 10px;
  border-radius: $border-radius-sm;
  color: $text-secondary;
  text-decoration: none;
  transition: all 0.25s ease;
  position: relative;
  cursor: pointer;

  &:hover {
    background: rgba(123, 28, 181, 0.2);
    color: $text-primary;
  }

  &.active {
    background: linear-gradient(135deg, rgba(123, 28, 181, 0.35), rgba(123, 28, 181, 0.15));
    color: $text-primary;
    box-shadow: inset 0 0 0 1px rgba(123, 28, 181, 0.3);
  }
}

.nav-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.nav-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: $danger-color;
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.active-indicator {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 3px 0 0 3px;
  background: $accent-color;
}

.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid $border-color;
  flex-shrink: 0;
}

.collapse-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: none;
  background: transparent;
  color: $text-secondary;
  border-radius: $border-radius-sm;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(123, 28, 181, 0.2);
    color: $text-primary;
  }
}
</style>
