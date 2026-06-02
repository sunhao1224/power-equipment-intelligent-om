<template>
  <span class="status-badge" :class="[`status-badge--${type}`, { 'status-badge--dot': dot }]">
    <span v-if="dot" class="status-dot" />
    <span class="status-text">{{ displayText }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  type: 'success' | 'warning' | 'danger' | 'info' | 'primary'
  text?: string
  dot?: boolean
}>()

const textMap: Record<string, string> = {
  success: '正常',
  warning: '注意',
  danger: '异常',
  info: '信息',
  primary: '在线'
}

const displayText = computed(() => props.text || textMap[props.type] || '')
</script>

<style lang="scss" scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;

  &--success {
    background: rgba(38, 198, 218, 0.15);
    color: $success-color;
    border: 1px solid rgba(38, 198, 218, 0.3);
    .status-dot { background: $success-color; }
  }

  &--warning {
    background: rgba(255, 179, 0, 0.15);
    color: $warning-color;
    border: 1px solid rgba(255, 179, 0, 0.3);
    .status-dot { background: $warning-color; }
  }

  &--danger {
    background: rgba(229, 57, 53, 0.15);
    color: $danger-color;
    border: 1px solid rgba(229, 57, 53, 0.3);
    .status-dot { background: $danger-color; }
  }

  &--info {
    background: rgba(155, 77, 202, 0.15);
    color: $primary-light;
    border: 1px solid rgba(155, 77, 202, 0.3);
    .status-dot { background: $primary-light; }
  }

  &--primary {
    background: rgba(123, 28, 181, 0.15);
    color: $primary-light;
    border: 1px solid rgba(123, 28, 181, 0.3);
    .status-dot { background: $primary-light; }
  }

  &--dot {
    padding-left: 8px;
  }
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-text {
  line-height: 1;
}
</style>
