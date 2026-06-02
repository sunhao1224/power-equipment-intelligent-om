<template>
  <div class="maintenance-view">
    <!-- 顶部健康评分概览 -->
    <div class="health-overview">
      <div class="health-gauge-section">
        <div class="panel gauge-panel">
          <div class="panel-title">设备综合健康指数</div>
          <div class="gauge-wrapper">
            <div ref="gaugeChartRef" class="gauge-chart" />
            <div class="gauge-info">
              <div class="gauge-score" :style="{ color: getHealthColor(averageHealthScore) }">
                {{ averageHealthScore }}
              </div>
              <div class="gauge-label">综合健康评分</div>
              <div class="gauge-status" :style="{ color: getHealthColor(averageHealthScore) }">
                {{ getHealthLevelText(averageHealthScore) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="health-stats-section">
        <div class="panel stats-panel">
          <div class="panel-title">健康分布统计</div>
          <div class="health-bars">
            <div class="health-bar-item" v-for="item in healthBarData" :key="item.label">
              <div class="bar-header">
                <span class="bar-label">{{ item.label }}</span>
                <span class="bar-count">{{ item.count }} 台</span>
              </div>
              <el-progress
                :percentage="item.percentage"
                :stroke-width="10"
                :color="item.color"
                :show-text="false"
                class="health-bar"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 下部主体 -->
    <div class="maintenance-body">
      <!-- 左侧设备健康列表 -->
      <div class="body-left">
        <div class="panel equipment-panel">
          <div class="panel-title-row">
            <div class="panel-title" style="margin-bottom: 0;">设备健康列表</div>
            <div class="filter-group">
              <el-select v-model="statusFilter" placeholder="状态筛选" size="small" clearable class="filter-select">
                <el-option label="全部" value="" />
                <el-option label="健康" value="healthy" />
                <el-option label="注意" value="attention" />
                <el-option label="异常" value="abnormal" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </div>
          </div>

          <el-table
            :data="filteredEquipment"
            class="equipment-table"
            :header-cell-style="tableHeaderStyle"
            :cell-style="tableCellStyle"
            highlight-current-row
            @current-change="handleEquipmentSelect"
            size="small"
          >
            <el-table-column prop="name" label="设备名称" min-width="120">
              <template #default="{ row }">
                <div class="eq-name-cell">
                  <el-icon :size="14" :color="getEquipmentTypeColor(row.type)">
                    <component :is="getEquipmentIcon(row.type)" />
                  </el-icon>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="healthScore" label="健康评分" width="100" align="center">
              <template #default="{ row }">
                <div class="score-cell">
                  <span class="score-value" :style="{ color: getHealthColor(row.healthScore) }">
                    {{ row.healthScore }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="healthLevel" label="状态" width="80" align="center">
              <template #default="{ row }">
                <StatusBadge :type="getHealthBadgeType(row.healthLevel)" :dot="true" />
              </template>
            </el-table-column>
            <el-table-column prop="location" label="位置" width="90" />
            <el-table-column label="建议措施" min-width="140">
              <template #default="{ row }">
                <span class="action-hint">{{ getActionHint(row.healthLevel) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 右侧维护计划 -->
      <div class="body-right">
        <div class="panel plan-panel">
          <div class="panel-title-row">
            <div class="panel-title" style="margin-bottom: 0;">维护计划与工单</div>
            <el-button
              type="primary"
              size="small"
              :disabled="!selectedEquipment"
              @click="handleGeneratePlan"
            >
              <el-icon><MagicStick /></el-icon> 生成计划
            </el-button>
          </div>

          <div v-if="selectedEquipment" class="selected-equipment-info">
            <span class="selected-label">当前设备：</span>
            <span class="selected-name">{{ selectedEquipment.name }}</span>
            <span class="selected-score" :style="{ color: getHealthColor(selectedEquipment.healthScore) }">
              健康评分: {{ selectedEquipment.healthScore }}
            </span>
          </div>

          <!-- 工单列表 -->
          <div class="work-order-list">
            <div
              v-for="wo in equipmentStore.workOrders"
              :key="wo.id"
              class="work-order-item"
              :class="{ expanded: expandedOrders.includes(wo.id) }"
            >
              <div class="wo-header" @click="toggleOrder(wo.id)">
                <div class="wo-left">
                  <span class="wo-status" :class="`wo-status--${wo.status}`">
                    {{ getWorkOrderStatusText(wo.status) }}
                  </span>
                  <span class="wo-title">{{ wo.title }}</span>
                </div>
                <div class="wo-right">
                  <span class="wo-priority" :class="`wo-priority--${wo.priority}`">
                    {{ getPriorityText(wo.priority) }}
                  </span>
                  <el-icon :size="14" class="expand-icon" :class="{ rotated: expandedOrders.includes(wo.id) }">
                    <ArrowDown />
                  </el-icon>
                </div>
              </div>

              <transition name="expand">
                <div v-if="expandedOrders.includes(wo.id)" class="wo-detail">
                  <div class="wo-info-grid">
                    <div class="wo-info-item">
                      <span class="wo-info-label">设备</span>
                      <span class="wo-info-value">{{ wo.equipmentName }}</span>
                    </div>
                    <div class="wo-info-item">
                      <span class="wo-info-label">负责人</span>
                      <span class="wo-info-value">{{ wo.assignedTo }}</span>
                    </div>
                    <div class="wo-info-item">
                      <span class="wo-info-label">计划日期</span>
                      <span class="wo-info-value">{{ wo.scheduledDate }}</span>
                    </div>
                    <div class="wo-info-item">
                      <span class="wo-info-label">预估费用</span>
                      <span class="wo-info-value">{{ wo.estimatedCost }}</span>
                    </div>
                  </div>

                  <div class="wo-description">{{ wo.description }}</div>

                  <div class="wo-actions-list">
                    <div class="wo-actions-title">执行项目</div>
                    <div v-for="(action, i) in wo.actions" :key="i" class="wo-action-item">
                      <el-icon :size="12" color="#26C6DA"><CircleCheck /></el-icon>
                      {{ action }}
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>

          <div v-if="equipmentStore.workOrders.length === 0" class="empty-orders">
            <el-icon :size="36" color="rgba(123,28,181,0.3)"><Tickets /></el-icon>
            <p>暂无维护工单</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useEquipmentStore } from '@/stores/equipment'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { Equipment } from '@/types'
import {
  MagicStick, ArrowDown, CircleCheck, Tickets
} from '@element-plus/icons-vue'

const equipmentStore = useEquipmentStore()

const gaugeChartRef = ref<HTMLElement>()
const statusFilter = ref('')
const selectedEquipment = ref<Equipment | null>(null)
const expandedOrders = ref<string[]>(['WO001'])

let gaugeChart: echarts.ECharts | null = null

const averageHealthScore = computed(() => {
  const list = equipmentStore.equipmentList
  if (list.length === 0) return 0
  return Math.round(list.reduce((sum, eq) => sum + eq.healthScore, 0) / list.length)
})

const healthBarData = computed(() => {
  const hd = equipmentStore.healthDistribution
  const total = equipmentStore.equipmentList.length || 1
  return [
    { label: '健康', count: hd.healthy, percentage: Math.round((hd.healthy / total) * 100), color: '#26C6DA' },
    { label: '注意', count: hd.attention, percentage: Math.round((hd.attention / total) * 100), color: '#FFB300' },
    { label: '异常', count: hd.abnormal, percentage: Math.round((hd.abnormal / total) * 100), color: '#FF8C38' },
    { label: '紧急', count: hd.critical, percentage: Math.round((hd.critical / total) * 100), color: '#E53935' }
  ]
})

const filteredEquipment = computed(() => {
  if (!statusFilter.value) return equipmentStore.equipmentList
  return equipmentStore.equipmentList.filter(eq => eq.healthLevel === statusFilter.value)
})

function getHealthColor(score: number): string {
  if (score > 85) return '#26C6DA'
  if (score > 60) return '#FFB300'
  if (score > 40) return '#FF8C38'
  return '#E53935'
}

function getHealthLevelText(score: number): string {
  if (score > 85) return '状态优良'
  if (score > 60) return '需要关注'
  if (score > 40) return '状态异常'
  return '紧急处理'
}

function getHealthBadgeType(level: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    healthy: 'success', attention: 'warning', abnormal: 'danger', critical: 'danger'
  }
  return map[level] || 'info'
}

function getEquipmentTypeColor(type: string): string {
  const map: Record<string, string> = { transformer: '#791CB5', breaker: '#FF8C38', gis: '#26C6DA' }
  return map[type] || '#791CB5'
}

function getEquipmentIcon(type: string): string {
  const map: Record<string, string> = { transformer: 'Odometer', breaker: 'Switch', gis: 'SetUp' }
  return map[type] || 'Monitor'
}

function getActionHint(level: string): string {
  const map: Record<string, string> = {
    healthy: '保持正常维护周期',
    attention: '建议缩短巡检周期',
    abnormal: '需安排专项检查',
    critical: '立即安排停电检修'
  }
  return map[level] || ''
}

function getWorkOrderStatusText(status: string): string {
  const map: Record<string, string> = {
    pending_review: '待审核',
    approved: '已批准',
    in_progress: '执行中',
    completed: '已完成'
  }
  return map[status] || status
}

function getPriorityText(priority: string): string {
  const map: Record<string, string> = { low: '低', medium: '中', high: '高', urgent: '紧急' }
  return map[priority] || priority
}

function toggleOrder(id: string) {
  const index = expandedOrders.value.indexOf(id)
  if (index === -1) {
    expandedOrders.value.push(id)
  } else {
    expandedOrders.value.splice(index, 1)
  }
}

function handleEquipmentSelect(row: Equipment | null) {
  selectedEquipment.value = row
}

function handleGeneratePlan() {
  if (selectedEquipment.value) {
    // 模拟生成维护计划
    const newOrder = {
      id: `WO${Date.now()}`,
      title: `${selectedEquipment.value.name}维护计划`,
      equipmentId: selectedEquipment.value.id,
      equipmentName: selectedEquipment.value.name,
      status: 'pending_review' as const,
      priority: selectedEquipment.value.healthScore > 60 ? 'medium' as const : 'high' as const,
      createdAt: new Date().toISOString().split('T')[0],
      scheduledDate: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
      description: `基于设备健康评分(${selectedEquipment.value.healthScore}分)自动生成的维护计划`,
      actions: ['设备全面巡检', '在线监测数据分析', '绝缘性能测试'],
      estimatedCost: '3-5万元',
      assignedTo: '系统分配'
    }
    equipmentStore.workOrders.unshift(newOrder)
    expandedOrders.value.unshift(newOrder.id)
  }
}

const tableHeaderStyle = {
  background: 'rgba(123, 28, 181, 0.15)',
  color: '#ffffff',
  borderBottom: '1px solid rgba(123, 28, 181, 0.3)',
  fontSize: '13px',
  fontWeight: '600'
}

const tableCellStyle = {
  background: 'transparent',
  color: 'rgba(255, 255, 255, 0.85)',
  borderBottom: '1px solid rgba(123, 28, 181, 0.1)'
}

function initGaugeChart() {
  if (!gaugeChartRef.value) return
  gaugeChart = echarts.init(gaugeChartRef.value)

  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      startAngle: 220,
      endAngle: -40,
      min: 0,
      max: 100,
      radius: '90%',
      progress: {
        show: true,
        width: 16,
        roundCap: true,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#E53935' },
              { offset: 0.4, color: '#FF8C38' },
              { offset: 0.6, color: '#FFB300' },
              { offset: 0.85, color: '#26C6DA' },
              { offset: 1, color: '#26C6DA' }
            ]
          }
        }
      },
      axisLine: {
        lineStyle: {
          width: 16,
          color: [[1, 'rgba(255,255,255,0.06)']]
        }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: { show: false }
    }]
  })

  // 动态设置数据
  gaugeChart.setOption({
    series: [{ data: [{ value: averageHealthScore.value }] }]
  })
}

function handleResize() {
  gaugeChart?.resize()
}

onMounted(() => {
  setTimeout(initGaugeChart, 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  gaugeChart?.dispose()
})
</script>

<style lang="scss" scoped>
.maintenance-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  animation: fadeIn 0.4s ease;
}

// 顶部概览
.health-overview {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 16px;
  flex-shrink: 0;
}

.panel {
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid $border-color;
  border-radius: $border-radius;
  padding: 16px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid $primary-color;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

// 仪表盘
.gauge-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.gauge-chart {
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.gauge-info {
  text-align: center;
}

.gauge-score {
  font-size: 48px;
  font-weight: 800;
  line-height: 1;
}

.gauge-label {
  font-size: 13px;
  color: $text-secondary;
  margin-top: 4px;
}

.gauge-status {
  font-size: 14px;
  font-weight: 600;
  margin-top: 6px;
}

// 健康条
.health-bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.health-bar-item {
  .bar-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
  }

  .bar-label {
    font-size: 13px;
    color: $text-secondary;
  }

  .bar-count {
    font-size: 13px;
    color: $text-primary;
    font-weight: 600;
  }
}

// 主体
.maintenance-body {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

// 设备表格
.equipment-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.filter-select {
  width: 120px;

  :deep(.el-input__wrapper) {
    background: rgba(123, 28, 181, 0.1) !important;
    border: 1px solid $border-color !important;
    box-shadow: none !important;
    border-radius: 6px !important;
  }

  :deep(.el-input__inner) {
    color: $text-primary !important;
    font-size: 12px;
  }
}

.equipment-table {
  flex: 1;

  :deep(.el-table__body-wrapper) {
    &::-webkit-scrollbar {
      width: 4px;
    }
  }

  :deep(.el-table__row) {
    &:hover > td {
      background: rgba(123, 28, 181, 0.12) !important;
    }

    &.current-row > td {
      background: rgba(123, 28, 181, 0.2) !important;
    }
  }

  :deep(.el-table__empty-block) {
    background: transparent;
    color: $text-muted;
  }
}

.eq-name-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-cell {
  .score-value {
    font-size: 18px;
    font-weight: 700;
  }
}

.action-hint {
  font-size: 12px;
  color: $text-secondary;
}

// 维护计划
.plan-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.selected-equipment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: $border-radius-sm;
  background: rgba(123, 28, 181, 0.1);
  border: 1px solid rgba(123, 28, 181, 0.2);

  .selected-label {
    font-size: 12px;
    color: $text-secondary;
  }

  .selected-name {
    font-size: 13px;
    font-weight: 600;
    color: $text-primary;
  }

  .selected-score {
    margin-left: auto;
    font-size: 13px;
    font-weight: 600;
  }
}

.work-order-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.work-order-item {
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(123, 28, 181, 0.3);
  }

  &.expanded {
    background: rgba(123, 28, 181, 0.06);
  }
}

.wo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  cursor: pointer;
}

.wo-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.wo-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wo-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &--pending_review { background: rgba(255, 179, 0, 0.15); color: $warning-color; }
  &--approved { background: rgba(38, 198, 218, 0.15); color: $success-color; }
  &--in_progress { background: rgba(123, 28, 181, 0.15); color: $primary-light; }
  &--completed { background: rgba(255, 255, 255, 0.08); color: $text-muted; }
}

.wo-title {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
}

.wo-priority {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;

  &--low { background: rgba(38, 198, 218, 0.1); color: $success-color; }
  &--medium { background: rgba(255, 179, 0, 0.1); color: $warning-color; }
  &--high { background: rgba(255, 140, 56, 0.15); color: $accent-color; }
  &--urgent { background: rgba(229, 57, 53, 0.15); color: $danger-color; }
}

.expand-icon {
  color: $text-muted;
  transition: transform 0.2s ease;

  &.rotated {
    transform: rotate(180deg);
  }
}

.wo-detail {
  padding: 0 14px 14px;
  border-top: 1px solid rgba(123, 28, 181, 0.1);
}

.wo-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 10px 0;
}

.wo-info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;

  .wo-info-label {
    font-size: 11px;
    color: $text-muted;
  }

  .wo-info-value {
    font-size: 13px;
    color: $text-primary;
  }
}

.wo-description {
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: 10px;
}

.wo-actions-list {
  .wo-actions-title {
    font-size: 12px;
    font-weight: 600;
    color: $text-secondary;
    margin-bottom: 6px;
  }
}

.wo-action-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 12px;
  color: $text-secondary;
}

.empty-orders {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $text-muted;

  p {
    margin-top: 10px;
    font-size: 13px;
  }
}

// 过渡动画
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 400px;
}
</style>
