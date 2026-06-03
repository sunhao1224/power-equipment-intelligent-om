<template>
  <main class="page-grid">
    <section class="panel hero-panel">
      <div>
        <div class="eyebrow">Cloud AI Loop</div>
        <h2>云端知识融合 + Hermes Agent 会诊闭环</h2>
        <p>本学期聚焦 Mock 异常事件、历史样本回放、RAG 证据、Agent Trace 和白盒诊断报告，不依赖边端硬件实机集成。</p>
      </div>
      <button class="primary-action" @click="$router.push('/diagnosis')">启动诊断</button>
    </section>

    <section class="metric-grid">
      <MetricCard v-for="metric in store.overview?.metrics || []" :key="metric.label" v-bind="metric" />
    </section>

    <section class="panel span-2">
      <div class="section-head">
        <h3>设备健康趋势</h3>
        <span>Transformer fleet / 7 days</span>
      </div>
      <div ref="trendRef" class="chart"></div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h3>高关注设备</h3>
        <span>{{ store.equipment.length }} assets</span>
      </div>
      <div class="compact-list">
        <div v-for="item in store.equipment" :key="item.equipment_id" class="list-row">
          <div>
            <strong>{{ item.name }}</strong>
            <small>{{ item.location }} · {{ item.model }}</small>
          </div>
          <RiskBadge :level="item.risk_level" />
        </div>
      </div>
    </section>

    <section class="panel span-2">
      <div class="section-head">
        <h3>Agent 平均耗时</h3>
        <span>mock runtime</span>
      </div>
      <div ref="agentRef" class="chart"></div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import MetricCard from '@/components/ui/MetricCard.vue'
import RiskBadge from '@/components/ui/RiskBadge.vue'
import { useHermesStore } from '@/stores/hermes'

const store = useHermesStore()
const trendRef = ref<HTMLDivElement>()
const agentRef = ref<HTMLDivElement>()

function renderCharts() {
  if (trendRef.value && store.overview?.health_trend) {
    echarts.init(trendRef.value).setOption({
      grid: { left: 28, right: 12, top: 24, bottom: 24 },
      xAxis: { type: 'category', data: store.overview.health_trend.map((i: any) => i.day), axisLine: { lineStyle: { color: '#30323a' } } },
      yAxis: { type: 'value', min: 60, max: 90, splitLine: { lineStyle: { color: '#24262d' } } },
      series: [{ type: 'line', smooth: true, data: store.overview.health_trend.map((i: any) => i.score), lineStyle: { color: '#7dd3fc', width: 3 }, areaStyle: { color: 'rgba(125,211,252,.12)' } }]
    })
  }
  if (agentRef.value && store.overview?.agent_stats) {
    echarts.init(agentRef.value).setOption({
      grid: { left: 40, right: 12, top: 12, bottom: 28 },
      xAxis: { type: 'category', data: store.overview.agent_stats.map((i: any) => i.name), axisLabel: { color: '#8b909c', rotate: 18 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#24262d' } } },
      series: [{ type: 'bar', data: store.overview.agent_stats.map((i: any) => i.avg_ms), itemStyle: { color: '#a78bfa', borderRadius: [4, 4, 0, 0] } }]
    })
  }
}

onMounted(async () => {
  await store.bootstrap()
  await nextTick()
  renderCharts()
})
</script>
