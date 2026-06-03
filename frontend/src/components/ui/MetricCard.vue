<template>
  <article class="metric-card">
    <div class="metric-label">{{ label }}</div>
    <div class="metric-row">
      <strong>{{ value }}</strong>
      <span :class="['metric-delta', tone]">{{ delta }}</span>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  delta: string
  tone?: string
}>()
</script>
