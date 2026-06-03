<template>
  <span :class="['risk-badge', level]">{{ label }}</span>
</template>

<script setup lang="ts">
const props = defineProps<{ level: string }>()
const labelMap: Record<string, string> = {
  normal: '正常',
  low: '低',
  medium: '中',
  important: '重要',
  high: '高',
  urgent: '紧急',
  critical: '关键'
}
const label = labelMap[props.level] ?? props.level
</script>
