<template>
  <main class="page-grid">
    <section class="panel span-2">
      <div class="section-head">
        <h3>批次寿命预测</h3>
        <button class="secondary-action" @click="load">重新评估</button>
      </div>
      <div ref="chartRef" class="chart tall"></div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h3>风险设备排序</h3>
        <span>{{ store.batch.length }} assets</span>
      </div>
      <div class="compact-list">
        <div v-for="item in store.batch" :key="item.equipment_id" class="list-row">
          <div>
            <strong>{{ item.equipment_name }}</strong>
            <small>{{ item.location }} · 12M {{ Math.round(item.probability_12m * 100) }}%</small>
          </div>
          <RiskBadge :level="item.risk_level" />
        </div>
      </div>
    </section>

    <section class="panel span-all">
      <div class="section-head">
        <h3>共性缺陷判断</h3>
        <span>TR-2021-A17</span>
      </div>
      <p class="body-copy">同批次设备在高负荷场景下出现 DGA 与油温趋势聚集性异常。建议建立专项监测列表，并把 12 个月风险超过 20% 的设备纳入优先复核。</p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import RiskBadge from '@/components/ui/RiskBadge.vue'
import { useHermesStore } from '@/stores/hermes'

const store = useHermesStore()
const chartRef = ref<HTMLDivElement>()

async function load() {
  await store.loadBatch()
  await nextTick()
  if (!chartRef.value) return
  echarts.init(chartRef.value).setOption({
    legend: { textStyle: { color: '#8b909c' } },
    grid: { left: 42, right: 18, top: 36, bottom: 38 },
    xAxis: { type: 'category', data: store.batch.map((i) => i.equipment_name), axisLabel: { color: '#8b909c', rotate: 18 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => `${v * 100}%` }, splitLine: { lineStyle: { color: '#24262d' } } },
    series: [
      { name: '6M', type: 'bar', data: store.batch.map((i) => i.probability_6m), itemStyle: { color: '#67e8f9' } },
      { name: '12M', type: 'bar', data: store.batch.map((i) => i.probability_12m), itemStyle: { color: '#a78bfa' } },
      { name: '24M', type: 'bar', data: store.batch.map((i) => i.probability_24m), itemStyle: { color: '#fb7185' } }
    ]
  })
}

onMounted(load)
</script>
