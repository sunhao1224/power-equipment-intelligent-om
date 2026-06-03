<template>
  <div class="agent-pipeline">
    <div v-for="agent in agents" :key="agent.agent_id" class="agent-step" :class="agent.status">
      <div class="agent-head">
        <span class="agent-light"></span>
        <span>{{ agent.name }}</span>
        <small>{{ agent.progress }}%</small>
      </div>
      <div class="agent-role">{{ agent.role }}</div>
      <div class="progress-track"><span :style="{ width: `${agent.progress}%` }"></span></div>
      <p>{{ agent.summary || '等待 Hermes Orchestrator 分配上下文' }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgentNode } from '@/types'

defineProps<{ agents: AgentNode[] }>()
</script>
