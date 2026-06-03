<template>
  <main class="diagnosis-layout">
    <section class="panel command-panel">
      <div class="section-head">
        <h3>异常样本输入</h3>
        <span>mock_event / historical_replay / manual_upload</span>
      </div>
      <div class="event-grid">
        <button v-for="event in store.events" :key="event.event_id" class="event-card" :class="{ active: selectedEvent === event.event_id }" @click="selectedEvent = event.event_id">
          <strong>{{ event.title }}</strong>
          <small>{{ event.summary }}</small>
        </button>
      </div>
      <button class="primary-action full" :disabled="store.running" @click="runDiagnosis">
        {{ store.running ? 'Hermes 会诊中...' : '触发 Hermes Agent 会诊' }}
      </button>
    </section>

    <section class="panel main-diagnosis">
      <div class="section-head">
        <h3>Agent 协同流水线</h3>
        <span>{{ store.completedAgents }}/7 completed</span>
      </div>
      <AgentPipeline :agents="store.agents" />
    </section>

    <aside class="panel trace-panel">
      <div class="section-head">
        <h3>实时 Trace</h3>
        <span>{{ store.wsEvents.length }} events</span>
      </div>
      <div class="trace-feed">
        <div v-for="event in store.wsEvents" :key="event.timestamp + event.event_type" class="trace-row">
          <span>{{ event.event_type }}</span>
          <small>{{ new Date(event.timestamp).toLocaleTimeString() }}</small>
        </div>
      </div>
    </aside>

    <section v-if="store.selectedReport" class="panel span-all report-panel">
      <div class="section-head">
        <h3>{{ store.selectedReport.title }}</h3>
        <RiskBadge :level="store.selectedReport.risk_level" />
      </div>
      <div class="report-grid">
        <div>
          <h4>Top 根因</h4>
          <div v-for="cause in store.selectedReport.root_causes" :key="cause.name" class="cause-row">
            <span>{{ cause.name }}</span>
            <strong>{{ Math.round(cause.confidence * 100) }}%</strong>
          </div>
        </div>
        <div>
          <h4>元器件路径</h4>
          <div class="path-line">
            <span v-for="node in store.selectedReport.component_path" :key="node">{{ node }}</span>
          </div>
        </div>
        <div>
          <h4>工单草稿</h4>
          <p>{{ store.selectedReport.work_order.title }}</p>
          <small>预计 {{ store.selectedReport.work_order.estimated_hours }} 小时 · {{ store.selectedReport.work_order.required_roles.join(' / ') }}</small>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AgentPipeline from '@/components/ui/AgentPipeline.vue'
import RiskBadge from '@/components/ui/RiskBadge.vue'
import { useHermesStore } from '@/stores/hermes'

const store = useHermesStore()
const selectedEvent = ref('')

onMounted(async () => {
  if (!store.events.length) await store.bootstrap()
  selectedEvent.value = store.events[0]?.event_id ?? ''
})

async function runDiagnosis() {
  await store.triggerDiagnosis(selectedEvent.value)
}
</script>
