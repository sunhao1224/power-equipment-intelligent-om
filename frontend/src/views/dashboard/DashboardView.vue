<template>
  <div class="dashboard-view">
    <!-- 顶部标题栏 -->
    <div class="dashboard-header">
      <div class="header-title">
        <h1>电力设备智能运维分析与决策支持系统</h1>
        <div class="header-subtitle">Power Equipment Intelligent O&M Analysis and Decision Support System</div>
      </div>
      <div class="header-time">
        <el-icon :size="16"><Clock /></el-icon>
        <span>{{ currentTime }}</span>
      </div>
    </div>

    <!-- 主体网格布局 -->
    <div class="dashboard-grid">
      <!-- 左列 -->
      <div class="grid-col grid-col--left">
        <!-- 设备统计卡片 -->
        <div class="panel stat-panel">
          <div class="panel-title">设备运行概览</div>
          <div class="stat-cards">
            <StatCard icon="Monitor" :value="stats.total" label="设备总数" color="primary" suffix="台" />
            <StatCard icon="CircleCheck" :value="stats.online" label="在线运行" color="success" suffix="台" />
            <StatCard icon="WarningFilled" :value="stats.warning" label="告警设备" color="warning" suffix="台" />
            <StatCard icon="CircleClose" :value="stats.offline" label="离线设备" color="danger" suffix="台" />
          </div>
        </div>

        <!-- 设备类型分布 -->
        <div class="panel chart-panel">
          <div class="panel-title">设备类型分布</div>
          <div ref="typeChartRef" class="chart-container" />
        </div>

        <!-- 告警趋势 -->
        <div class="panel chart-panel">
          <div class="panel-title">近7天告警趋势</div>
          <div ref="trendChartRef" class="chart-container" />
        </div>
      </div>

      <!-- 中列 -->
      <div class="grid-col grid-col--center">
        <!-- 健康状态分布 -->
        <div class="panel health-panel">
          <div class="panel-title">设备健康状态分布</div>
          <div class="health-content">
            <div ref="healthChartRef" class="chart-container chart-container--large" />
            <div class="health-legend">
              <div class="legend-item" v-for="item in healthLegendData" :key="item.label">
                <span class="legend-dot" :style="{ background: item.color }" />
                <span class="legend-label">{{ item.label }}</span>
                <span class="legend-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统指标 -->
        <div class="panel metrics-panel">
          <div class="panel-title">系统运行指标</div>
          <div class="metrics-grid">
            <div class="metric-item">
              <div class="metric-ring" style="--progress: 96; --color: #26C6DA;">
                <span class="metric-value">96%</span>
              </div>
              <div class="metric-label">数据采集率</div>
            </div>
            <div class="metric-item">
              <div class="metric-ring" style="--progress: 89; --color: #791CB5;">
                <span class="metric-value">89%</span>
              </div>
              <div class="metric-label">诊断准确率</div>
            </div>
            <div class="metric-item">
              <div class="metric-ring" style="--progress: 92; --color: #FF8C38;">
                <span class="metric-value">92%</span>
              </div>
              <div class="metric-label">预警及时率</div>
            </div>
            <div class="metric-item">
              <div class="metric-ring" style="--progress: 85; --color: #FFB300;">
                <span class="metric-value">85%</span>
              </div>
              <div class="metric-label">维护执行率</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右列 -->
      <div class="grid-col grid-col--right">
        <!-- 最新告警列表 -->
        <div class="panel alarm-panel">
          <div class="panel-title">
            <span>最新告警</span>
            <span class="alarm-count">{{ alarms.length }} 条未处理</span>
          </div>
          <div class="alarm-list">
            <div
              v-for="alarm in alarms"
              :key="alarm.id"
              class="alarm-item"
              :class="{ 'alarm-item--new': alarm.status === 'active' }"
            >
              <StatusBadge :type="alarmLevelToType(alarm.level)" :dot="true" />
              <div class="alarm-content">
                <div class="alarm-name">{{ alarm.equipmentName }}</div>
                <div class="alarm-message">{{ alarm.message }}</div>
              </div>
              <div class="alarm-time">{{ formatTime(alarm.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- 知识检索 -->
        <div class="panel knowledge-panel">
          <div class="panel-title">知识检索</div>
          <div class="search-wrapper">
            <el-input
              v-model="searchQuery"
              placeholder="输入关键词检索运维知识库..."
              size="large"
              clearable
              class="knowledge-search"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button type="primary" class="search-btn">
                  检索
                </el-button>
              </template>
            </el-input>
          </div>
          <div class="quick-tags">
            <span
              v-for="tag in quickTags"
              :key="tag"
              class="quick-tag"
              @click="searchQuery = tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { Clock, Search } from '@element-plus/icons-vue'
import StatCard from '@/components/common/StatCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useEquipmentStore } from '@/stores/equipment'

const equipmentStore = useEquipmentStore()
const stats = computed(() => equipmentStore.stats)
const alarms = computed(() => equipmentStore.alarms.filter(a => a.status === 'active').slice(0, 6))

const currentTime = ref('')
const searchQuery = ref('')
let timeTimer: number

const typeChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const healthChartRef = ref<HTMLElement>()

let typeChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let healthChart: echarts.ECharts | null = null

const quickTags = ['变压器DGA分析', 'GIS局放检测', '断路器操作机构', '绝缘电阻标准', '油温异常处理']

const healthLegendData = computed(() => [
  { label: '健康', value: equipmentStore.healthDistribution.healthy, color: '#26C6DA' },
  { label: '注意', value: equipmentStore.healthDistribution.attention, color: '#FFB300' },
  { label: '异常', value: equipmentStore.healthDistribution.abnormal, color: '#FF8C38' },
  { label: '紧急', value: equipmentStore.healthDistribution.critical, color: '#E53935' }
])

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false
  })
}

function alarmLevelToType(level: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    info: 'info',
    warning: 'warning',
    danger: 'danger',
    critical: 'danger'
  }
  return map[level] || 'info'
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

function initTypeChart() {
  if (!typeChartRef.value) return
  typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(26,5,51,0.9)', borderColor: '#791CB5', textStyle: { color: '#fff' } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#1a0533', borderWidth: 3 },
      label: { show: true, color: 'rgba(255,255,255,0.8)', fontSize: 12, formatter: '{b}\n{d}%' },
      labelLine: { lineStyle: { color: 'rgba(255,255,255,0.3)' } },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
        itemStyle: { shadowBlur: 20, shadowColor: 'rgba(123,28,181,0.5)' }
      },
      data: [
        { value: 5, name: '变压器', itemStyle: { color: '#791CB5' } },
        { value: 3, name: '断路器', itemStyle: { color: '#FF8C38' } },
        { value: 2, name: 'GIS', itemStyle: { color: '#26C6DA' } }
      ]
    }]
  })
}

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const dates = []
  const values = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
    values.push(Math.floor(Math.random() * 8) + 2)
  }
  values[values.length - 1] = alarms.value.length

  trendChart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(26,5,51,0.9)', borderColor: '#791CB5', textStyle: { color: '#fff' } },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: '#FF8C38', width: 3 },
      itemStyle: { color: '#FF8C38', borderColor: '#1a0533', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(255,140,56,0.35)' },
          { offset: 1, color: 'rgba(255,140,56,0.02)' }
        ])
      }
    }]
  })
}

function initHealthChart() {
  if (!healthChartRef.value) return
  healthChart = echarts.init(healthChartRef.value)
  const hd = equipmentStore.healthDistribution

  healthChart.setOption({
    series: [
      {
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#1a0533', borderWidth: 3 },
        label: { show: false },
        emphasis: {
          scaleSize: 8,
          itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,0,0,0.5)' }
        },
        data: [
          { value: hd.healthy, name: '健康', itemStyle: { color: '#26C6DA' } },
          { value: hd.attention, name: '注意', itemStyle: { color: '#FFB300' } },
          { value: hd.abnormal, name: '异常', itemStyle: { color: '#FF8C38' } },
          { value: hd.critical, name: '紧急', itemStyle: { color: '#E53935' } }
        ]
      },
      {
        type: 'pie',
        radius: ['0%', '40%'],
        center: ['50%', '50%'],
        silent: true,
        label: {
          show: true,
          position: 'center',
          formatter: () => `{total|${stats.value.total}}\n{label|设备总数}`,
          rich: {
            total: { fontSize: 36, fontWeight: 'bold', color: '#ffffff', lineHeight: 44 },
            label: { fontSize: 13, color: 'rgba(255,255,255,0.5)', lineHeight: 22 }
          }
        },
        data: [{ value: 1, itemStyle: { color: 'transparent' } }]
      }
    ]
  })
}

function handleResize() {
  typeChart?.resize()
  trendChart?.resize()
  healthChart?.resize()
}

onMounted(() => {
  updateTime()
  timeTimer = window.setInterval(updateTime, 1000)

  setTimeout(() => {
    initTypeChart()
    initTrendChart()
    initHealthChart()
  }, 100)

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timeTimer)
  window.removeEventListener('resize', handleResize)
  typeChart?.dispose()
  trendChart?.dispose()
  healthChart?.dispose()
})
</script>

<style lang="scss" scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  animation: fadeIn 0.5s ease;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(123,28,181,0.2), rgba(45,16,84,0.4));
  border: 1px solid $border-color;
  border-radius: $border-radius;
  flex-shrink: 0;

  h1 {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #d4a5f5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
  }

  .header-subtitle {
    font-size: 11px;
    color: $text-muted;
    margin-top: 2px;
    letter-spacing: 0.5px;
  }

  .header-time {
    display: flex;
    align-items: center;
    gap: 8px;
    color: $text-secondary;
    font-size: 14px;
    font-variant-numeric: tabular-nums;
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.grid-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.panel {
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid $border-color;
  border-radius: $border-radius;
  padding: 16px;
  overflow: hidden;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid $primary-color;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// 统计面板
.stat-panel {
  flex-shrink: 0;

  .stat-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
}

// 图表面板
.chart-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  min-height: 150px;

  &--large {
    min-height: 200px;
  }
}

// 健康状态面板
.health-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.health-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.health-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 120px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  font-size: 13px;
  color: $text-secondary;
  flex: 1;
}

.legend-value {
  font-size: 16px;
  font-weight: 700;
  color: $text-primary;
}

// 指标面板
.metrics-panel {
  flex-shrink: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.metric-ring {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: conic-gradient(
    var(--color) calc(var(--progress) * 1%),
    rgba(255,255,255,0.08) calc(var(--progress) * 1%)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #1a0533;
  }
}

.metric-value {
  position: relative;
  z-index: 1;
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
}

.metric-label {
  font-size: 12px;
  color: $text-secondary;
}

// 告警面板
.alarm-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;

  .alarm-count {
    font-size: 12px;
    font-weight: 400;
    color: $danger-color;
    background: rgba(229, 57, 53, 0.15);
    padding: 2px 8px;
    border-radius: 10px;
  }
}

.alarm-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alarm-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  transition: background 0.2s ease;

  &:hover {
    background: rgba(123, 28, 181, 0.12);
  }

  &--new {
    border-left: 2px solid $danger-color;
  }
}

.alarm-content {
  flex: 1;
  min-width: 0;

  .alarm-name {
    font-size: 13px;
    font-weight: 500;
    color: $text-primary;
  }

  .alarm-message {
    font-size: 11px;
    color: $text-muted;
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.alarm-time {
  font-size: 11px;
  color: $text-muted;
  flex-shrink: 0;
}

// 知识检索面板
.knowledge-panel {
  flex-shrink: 0;
}

.search-wrapper {
  :deep(.knowledge-search) {
    .el-input__wrapper {
      background: rgba(123, 28, 181, 0.1) !important;
      border: 1px solid $border-color !important;
      box-shadow: none !important;
      border-radius: $border-radius-sm !important;

      .el-input__inner {
        color: $text-primary;
      }

      .el-input__prefix {
        color: $text-muted;
      }
    }

    .el-input-group__append {
      background: $primary-color !important;
      border: none !important;
      box-shadow: none !important;
      border-radius: 0 $border-radius-sm $border-radius-sm 0 !important;

      .search-btn {
        color: white !important;
      }
    }
  }
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.quick-tag {
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 12px;
  color: $text-secondary;
  background: rgba(123, 28, 181, 0.12);
  border: 1px solid rgba(123, 28, 181, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(123, 28, 181, 0.25);
    color: $text-primary;
    border-color: $primary-color;
  }
}
</style>
