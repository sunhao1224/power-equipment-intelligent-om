<template>
  <main class="page-grid">
    <section class="panel span-2">
      <div class="section-head">
        <h3>决策报告中心</h3>
        <button class="secondary-action" @click="store.loadReports()">刷新</button>
      </div>
      <div v-if="!store.reports.length" class="empty-state">
        <strong>暂无报告</strong>
        <span>请先在 Hermes 诊断中心触发一次 Agent 会诊。</span>
      </div>
      <article v-for="report in store.reports" :key="report.report_id" class="report-card">
        <div class="section-head">
          <h4>{{ report.title }}</h4>
          <RiskBadge :level="report.risk_level" />
        </div>
        <p>根因：{{ report.root_causes[0]?.name }} · 置信度 {{ Math.round((report.root_causes[0]?.confidence || 0) * 100) }}%</p>
        <div class="path-line">
          <span v-for="node in report.component_path" :key="node">{{ node }}</span>
        </div>
      </article>
    </section>

    <section class="panel">
      <div class="section-head">
        <h3>Review 标准</h3>
        <span>white-box</span>
      </div>
      <div class="review-list">
        <div>事实性：结论必须绑定 evidence_id</div>
        <div>完整性：覆盖数据、图谱、规程、案例</div>
        <div>一致性：多 Agent 输出不得矛盾</div>
        <div>可执行性：工单动作、角色、备件清晰</div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import RiskBadge from '@/components/ui/RiskBadge.vue'
import { useHermesStore } from '@/stores/hermes'

const store = useHermesStore()
onMounted(() => store.loadReports())
</script>
