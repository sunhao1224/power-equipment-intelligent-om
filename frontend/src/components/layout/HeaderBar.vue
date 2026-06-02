<template>
  <header class="header-bar">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">系统首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{ appStore.currentPageTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <!-- 搜索框 -->
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索设备或知识..."
          :prefix-icon="Search"
          size="small"
          clearable
          class="header-search"
        />
      </div>

      <!-- 通知铃铛 -->
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
        <el-button circle size="small" class="icon-btn">
          <el-icon :size="18"><Bell /></el-icon>
        </el-button>
      </el-badge>

      <!-- 用户信息 -->
      <div class="user-info">
        <el-avatar :size="32" class="user-avatar">
          <el-icon><User /></el-icon>
        </el-avatar>
        <span class="user-name">管理员</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useEquipmentStore } from '@/stores/equipment'
import { Search, Bell, User } from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const equipmentStore = useEquipmentStore()

const searchQuery = ref('')
const unreadCount = ref(3)

const titleMap: Record<string, string> = {
  '/dashboard': '可视化大屏',
  '/chat': '运维问答',
  '/diagnosis': '故障诊断',
  '/maintenance': '维护决策'
}

watch(() => route.path, (path) => {
  appStore.setPageTitle(titleMap[path] || '系统首页')
}, { immediate: true })
</script>

<style lang="scss" scoped>
.header-bar {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: rgba(26, 5, 51, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid $border-color;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;

  :deep(.el-breadcrumb__inner) {
    color: $text-secondary !important;
  }

  :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
    color: $text-primary !important;
  }

  :deep(.el-breadcrumb__separator) {
    color: $text-muted !important;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  .header-search {
    width: 200px;

    :deep(.el-input__wrapper) {
      background: rgba(123, 28, 181, 0.1);
      border: 1px solid $border-color;
      box-shadow: none;
      border-radius: 20px;

      .el-input__inner {
        color: $text-primary;
      }

      .el-input__prefix {
        color: $text-muted;
      }
    }
  }
}

.icon-btn {
  background: rgba(123, 28, 181, 0.15) !important;
  border: 1px solid $border-color !important;
  color: $text-secondary !important;

  &:hover {
    background: rgba(123, 28, 181, 0.3) !important;
    color: $text-primary !important;
  }
}

.notification-badge {
  :deep(.el-badge__content) {
    background: $danger-color;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, $primary-color, $primary-light);
  color: white;
}

.user-name {
  font-size: 13px;
  color: $text-secondary;
}
</style>
