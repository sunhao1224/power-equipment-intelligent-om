<template>
  <div class="diagnosis-view">
    <!-- 顶部操作栏 -->
    <div class="diagnosis-toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedEquipmentId"
          placeholder="选择诊断设备"
          size="large"
          filterable
          class="equipment-select"
        >
          <el-option
            v-for="eq in equipmentStore.equipmentList"
            :key="eq.id"
            :label="`${eq.name} (${eq.location})`"
            :value="eq.id"
          >
            <div class="eq-option">
              <StatusBadge :type="getEquipmentStatusType(eq.status)" :dot="true" />
              <span>{{ eq.name }}</span>
              <span class="eq-location">{{ eq.location }}</span>
            </div>
          </el-option>
        </el-select>

        <el-button
          type="primary"
          size="large"
          :loading="diagnosisStore.isDiagnosing"
          :disabled="!selectedEquipmentId"
          @click="handleStartDiagnosis"
          class="start-btn"
        >
          <el-icon v-if="!diagnosisStore.isDiagnosing"><VideoPlay /></el-icon>
          {{ diagnosisStore.isDiagnosing ? '诊断中...' : '开始诊断' }}
        </el-button>
      </div>

      <div v-if="diagnosisStore.isDiagnosing || diagnosisStore.diagnosisProgress > 0" class="toolbar-progress">
        <span class="progress-label">诊断进度</span>
        <el-progress
          :percentage="diagnosisStore.diagnosisProgress"
          :stroke-width="10"
          :color="progressColor"
          class="diagnosis-progress-bar"
        />
      </div>
    </div>

    <!-- 三栏主体 -->
    <div class="diagnosis-body">
      <!-- 左侧：传感器数据 -->
      <div class="body-left">
        <div class="panel sensor-panel">
          <div class="panel-title">设备实时数据</div>
          <div class="sensor-grid">
            <div
              v-for="sensor in diagnosisStore.sensorData"
              :key="sensor.name"
              class="sensor-card"
              :class="[`sensor-card--${sensor.status}`]"
            >
              <div class="sensor-status-dot" />
              <div class="sensor-name">{{ sensor.name }}</div>
              <div class="sensor-value">
                {{ sensor.value }}
                <span class="sensor-unit">{{ sensor.unit }}</span>
              </div>
              <div v-if="sensor.threshold" class="sensor-threshold">
                阈值: {{ sensor.threshold.min }}-{{ sensor.threshold.max }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：Agent流程图 -->
      <div class="body-center">
        <div class="panel agent-panel">
          <div class="panel-title">多Agent协同诊断</div>

          <div class="agent-flow">
            <div
              v-for="(agent, index) in diagnosisStore.agents"
              :key="agent.id"
              class="agent-node-wrapper"
            >
              <!-- 连接线 -->
              <div v-if="index > 0" class="agent-connector" :class="{ active: agent.status !== 'pending' }">
                <div class="connector-line" />
              </div>

              <div class="agent-node" :class="[`agent-node--${agent.status}`]">
                <div class="agent-icon">
                  <el-icon v-if="agent.status === 'completed'" :size="20"><CircleCheckFilled /></el-icon>
                  <el-icon v-else-if="agent.status === 'running'" :size="20" class="spinning"><Loading /></el-icon>
                  <span v-else class="agent-number">{{ index + 1 }}</span>
                </div>

                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-name-en">{{ agent.nameEn }}</div>
                  <div class="agent-desc">{{ agent.description }}</div>
                </div>

                <div class="agent-status-indicator">
                  <el-progress
                    v-if="agent.status === 'running'"
                    type="circle"
                    :percentage="agent.progress"
                    :width="36"
                    :stroke-width="3"
                    color="#FF8C38"
                  />
                  <StatusBadge
                    v-else
                    :type="getAgentStatusType(agent.status)"
                    :text="getAgentStatusText(agent.status)"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 诊断总结 -->
          <div v-if="diagnosisStore.isComplete && diagnosisStore.diagnosisResult" class="diagnosis-summary">
            <el-icon :size="18"><SuccessFilled /></el-icon>
            <span>诊断完成 - 综合置信度: {{ Math.round(diagnosisStore.diagnosisResult.overallConfidence * 100) }}%</span>
          </div>
        </div>
      </div>

      <!-- 右侧：诊断报告 -->
      <div class="body-right">
        <div class="panel report-panel">
          <div class="panel-title">诊断报告</div>

          <el-tabs v-model="activeReportTab" class="report-tabs" v-if="diagnosisStore.diagnosisResult">
            <el-tab-pane label="基本信息" name="basic">
              <div class="report-section">
                <div class="info-row">
                  <span class="info-label">设备名称</span>
                  <span class="info-value">{{ diagnosisStore.diagnosisResult.equipmentName }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">诊断时间</span>
                  <span class="info-value">{{ formatDateTime(diagnosisStore.diagnosisResult.timestamp) }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">综合置信度</span>
                  <span class="info-value">
                    <span class="confidence-badge" :class="getConfidenceClass(diagnosisStore.diagnosisResult.overallConfidence)">
                      {{ Math.round(diagnosisStore.diagnosisResult.overallConfidence * 100) }}%
                    </span>
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-label">处置优先级</span>
                  <span class="info-value">
                    <span class="priority-badge" :class="`priority--${diagnosisStore.diagnosisResult.recommendation.priority}`">
                      {{ getPriorityText(diagnosisStore.diagnosisResult.recommendation.priority) }}
                    </span>
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-label">预估费用</span>
                  <span class="info-value">{{ diagnosisStore.diagnosisResult.recommendation.estimatedCost }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">预估工期</span>
                  <span class="info-value">{{ diagnosisStore.diagnosisResult.recommendation.estimatedDuration }}</span>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="根因分析" name="rca">
              <div class="report-section">
                <div class="rca-cause">
                  <div class="rca-label">根本原因</div>
                  <div class="rca-value">{{ diagnosisStore.diagnosisResult.rootCause.primaryCause }}</div>
                  <span class="confidence-badge" :class="getConfidenceClass(diagnosisStore.diagnosisResult.rootCause.confidence)">
                    置信度 {{ Math.round(diagnosisStore.diagnosisResult.rootCause.confidence * 100) }}%
                  </span>
                </div>

                <div class="evidence-chain">
                  <div class="rca-label">证据链</div>
                  <EvidenceTree :nodes="diagnosisStore.diagnosisResult.rootCause.evidenceChain" />
                </div>

                <div class="contributing-factors">
                  <div class="rca-label">关联因素</div>
                  <div v-for="(factor, i) in diagnosisStore.diagnosisResult.rootCause.contributingFactors" :key="i" class="factor-item">
                    <el-icon :size="14"><InfoFilled /></el-icon>
                    {{ factor }}
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="批次风险" name="batch">
              <div class="report-section">
                <div class="batch-risk-level">
                  <span class="rca-label">风险等级</span>
                  <span class="risk-badge" :class="`risk--${diagnosisStore.diagnosisResult.batchRisk.riskLevel}`">
                    {{ getRiskText(diagnosisStore.diagnosisResult.batchRisk.riskLevel) }}
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-label">共性缺陷</span>
                  <span class="info-value">{{ diagnosisStore.diagnosisResult.batchRisk.commonDefect }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">影响设备</span>
                  <span class="info-value">
                    <span v-for="eq in diagnosisStore.diagnosisResult.batchRisk.affectedEquipment" :key="eq" class="affected-tag">
                      {{ eq }}
                    </span>
                  </span>
                </div>
                <div class="batch-recommendation">
                  <div class="rca-label">建议措施</div>
                  <div class="recommendation-text">{{ diagnosisStore.diagnosisResult.batchRisk.recommendation }}</div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="处置建议" name="action">
              <div class="report-section">
                <div class="action-cards">
                  <div
                    v-for="action in diagnosisStore.diagnosisResult.recommendation.actions"
                    :key="action.id"
                    class="action-card"
                    :class="[`action-card--${action.type}`]"
                  >
                    <div class="action-header">
                      <span class="action-type-badge">{{ getActionTypeText(action.type) }}</span>
                      <span class="action-urgency">{{ action.urgency }}</span>
                    </div>
                    <div class="action-title">{{ action.title }}</div>
                    <div class="action-desc">{{ action.description }}</div>
                  </div>
                </div>

                <!-- FMEA信息 -->
                <div class="fmea-section">
                  <div class="rca-label">FMEA 分析</div>
                  <div class="fmea-grid">
                    <div class="fmea-item">
                      <span class="fmea-label">严重度(S)</span>
                      <span class="fmea-score" :class="getFmeaClass(diagnosisStore.diagnosisResult.fmea.severity)">{{ diagnosisStore.diagnosisResult.fmea.severity }}</span>
                    </div>
                    <div class="fmea-item">
                      <span class="fmea-label">频度(O)</span>
                      <span class="fmea-score" :class="getFmeaClass(diagnosisStore.diagnosisResult.fmea.occurrence)">{{ diagnosisStore.diagnosisResult.fmea.occurrence }}</span>
                    </div>
                    <div class="fmea-item">
                      <span class="fmea-label">探测度(D)</span>
                      <span class="fmea-score" :class="getFmeaClass(diagnosisStore.diagnosisResult.fmea.detection)">{{ diagnosisStore.diagnosisResult.fmea.detection }}</span>
                    </div>
                    <div class="fmea-item fmea-item--rpn">
                      <span class="fmea-label">RPN</span>
                      <span class="fmea-score fmea-score--rpn">{{ diagnosisStore.diagnosisResult.fmea.rpn }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 空状态 -->
          <div v-else class="report-empty">
            <el-icon :size="40" color="rgba(123,28,181,0.3)"><Document /></el-icon>
            <p>选择设备并启动诊断后，分析报告将在此展示</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h } from 'vue'
import { useEquipmentStore } from '@/stores/equipment'
import { useDiagnosisStore } from '@/stores/diagnosis'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { EvidenceNode } from '@/types'
import {
  VideoPlay, CircleCheckFilled, Loading, SuccessFilled, InfoFilled, Document
} from '@element-plus/icons-vue'

const equipmentStore = useEquipmentStore()
const diagnosisStore = useDiagnosisStore()

const selectedEquipmentId = ref('EQ001')
const activeReportTab = ref('basic')

const progressColor = [
  { color: '#E53935', percentage: 20 },
  { color: '#FF8C38', percentage: 40 },
  { color: '#FFB300', percentage: 60 },
  { color: '#26C6DA', percentage: 80 },
  { color: '#791CB5', percentage: 100 }
]

// EvidenceTree 递归组件
const EvidenceTree = defineComponent({
  name: 'EvidenceTree',
  props: {
    nodes: { type: Array as () => EvidenceNode[], required: true },
    depth: { type: Number, default: 0 }
  },
  setup(props) {
    return () => h('div', { class: 'evidence-tree', style: { paddingLeft: props.depth > 0 ? '20px' : '0' } },
      props.nodes.map(node =>
        h('div', { class: 'evidence-node-wrapper', key: node.id }, [
          h('div', { class: ['evidence-node', `evidence-node--${node.type}`] }, [
            h('span', { class: 'evidence-type-icon' },
              node.type === 'observation' ? '\u25CF' :
              node.type === 'test' ? '\u25B2' :
              node.type === 'analysis' ? '\u25A0' : '\u2605'
            ),
            h('span', { class: 'evidence-label' }, node.label),
            node.confidence != null
              ? h('span', {
                  class: ['evidence-confidence', node.confidence >= 0.8 ? 'high' : node.confidence >= 0.6 ? 'medium' : 'low']
                }, `${Math.round(node.confidence * 100)}%`)
              : null
          ]),
          node.children && node.children.length > 0
            ? h(EvidenceTree, { nodes: node.children, depth: props.depth + 1 })
            : null
        ])
      )
    )
  }
})

function getEquipmentStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    online: 'success', warning: 'warning', error: 'danger', offline: 'info'
  }
  return map[status] || 'info'
}

function getAgentStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    pending: 'info', running: 'warning', completed: 'success', error: 'danger'
  }
  return map[status] || 'info'
}

function getAgentStatusText(status: string): string {
  const map: Record<string, string> = {
    pending: '等待', running: '运行中', completed: '完成', error: '异常'
  }
  return map[status] || status
}

function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return 'confidence--high'
  if (confidence >= 0.6) return 'confidence--medium'
  return 'confidence--low'
}

function getPriorityText(priority: string): string {
  const map: Record<string, string> = { low: '低', medium: '中', high: '高', urgent: '紧急' }
  return map[priority] || priority
}

function getRiskText(level: string): string {
  const map: Record<string, string> = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[level] || level
}

function getActionTypeText(type: string): string {
  const map: Record<string, string> = {
    inspection: '检测', repair: '维修', replacement: '更换', monitoring: '监测'
  }
  return map[type] || type
}

function getFmeaClass(score: number): string {
  if (score <= 3) return 'fmea--low'
  if (score <= 6) return 'fmea--medium'
  return 'fmea--high'
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('zh-CN')
}

function handleStartDiagnosis() {
  if (selectedEquipmentId.value) {
    diagnosisStore.startDiagnosis(selectedEquipmentId.value)
  }
}
</script>

<style lang="scss" scoped>
.diagnosis-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  animation: fadeIn 0.4s ease;
}

// 工具栏
.diagnosis-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid $border-color;
  border-radius: $border-radius;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.equipment-select {
  width: 280px;

  :deep(.el-input__wrapper) {
    background: rgba(123, 28, 181, 0.1) !important;
    border: 1px solid $border-color !important;
    box-shadow: none !important;
    border-radius: $border-radius-sm !important;
  }

  :deep(.el-input__inner) {
    color: $text-primary !important;
  }
}

.eq-option {
  display: flex;
  align-items: center;
  gap: 8px;

  .eq-location {
    font-size: 12px;
    color: $text-muted;
    margin-left: auto;
  }
}

.start-btn {
  background: linear-gradient(135deg, $primary-color, $primary-light) !important;
  border: none !important;
  font-weight: 600;
  letter-spacing: 1px;
}

.toolbar-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;

  .progress-label {
    font-size: 13px;
    color: $text-secondary;
    white-space: nowrap;
  }

  .diagnosis-progress-bar {
    flex: 1;
  }
}

// 主体三栏
.diagnosis-body {
  display: grid;
  grid-template-columns: 280px 1fr 1fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.panel {
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid $border-color;
  border-radius: $border-radius;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 3px solid $primary-color;
  flex-shrink: 0;
}

// 传感器面板
.sensor-panel {
  overflow-y: auto;
}

.sensor-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sensor-card {
  padding: 12px;
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  position: relative;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
  }

  &--normal { .sensor-status-dot { background: $success-color; box-shadow: 0 0 8px rgba(38, 198, 218, 0.5); } }
  &--warning { .sensor-status-dot { background: $warning-color; box-shadow: 0 0 8px rgba(255, 179, 0, 0.5); } border-color: rgba(255, 179, 0, 0.2); }
  &--danger { .sensor-status-dot { background: $danger-color; box-shadow: 0 0 8px rgba(229, 57, 53, 0.5); animation: pulse 2s infinite; } border-color: rgba(229, 57, 53, 0.3); }
}

.sensor-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  top: 14px;
  right: 12px;
}

.sensor-name {
  font-size: 12px;
  color: $text-secondary;
}

.sensor-value {
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  margin: 4px 0;

  .sensor-unit {
    font-size: 12px;
    font-weight: 400;
    color: $text-muted;
  }
}

.sensor-threshold {
  font-size: 11px;
  color: $text-muted;
}

// Agent面板
.agent-panel {
  overflow-y: auto;
}

.agent-flow {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.agent-node-wrapper {
  position: relative;
}

.agent-connector {
  display: flex;
  justify-content: center;
  height: 24px;

  .connector-line {
    width: 2px;
    height: 100%;
    background: rgba(123, 28, 181, 0.2);
    transition: background 0.3s ease;
  }

  &.active .connector-line {
    background: $primary-color;
  }
}

.agent-node {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;

  &--running {
    background: rgba(255, 140, 56, 0.1);
    border-color: rgba(255, 140, 56, 0.3);
    box-shadow: 0 0 20px rgba(255, 140, 56, 0.1);
  }

  &--completed {
    background: rgba(38, 198, 218, 0.08);
    border-color: rgba(38, 198, 218, 0.2);
  }
}

.agent-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 700;

  .agent-node--pending & {
    background: rgba(123, 28, 181, 0.15);
    color: $text-muted;
  }

  .agent-node--running & {
    background: rgba(255, 140, 56, 0.2);
    color: $accent-color;
  }

  .agent-node--completed & {
    background: rgba(38, 198, 218, 0.2);
    color: $success-color;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.agent-name-en {
  font-size: 11px;
  color: $text-muted;
}

.agent-desc {
  font-size: 11px;
  color: $text-secondary;
  margin-top: 2px;
}

.agent-status-indicator {
  flex-shrink: 0;
}

.agent-number {
  font-size: 14px;
  font-weight: 700;
}

.diagnosis-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  margin-top: 16px;
  border-radius: $border-radius-sm;
  background: linear-gradient(135deg, rgba(38, 198, 218, 0.15), rgba(38, 198, 218, 0.05));
  border: 1px solid rgba(38, 198, 218, 0.3);
  color: $success-color;
  font-size: 14px;
  font-weight: 500;
}

// 报告面板
.report-panel {
  overflow-y: auto;
}

.report-tabs {
  flex: 1;

  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }

  :deep(.el-tabs__item) {
    color: $text-secondary;
    font-size: 13px;

    &.is-active {
      color: $primary-light;
    }
  }

  :deep(.el-tabs__active-bar) {
    background: $primary-color;
  }

  :deep(.el-tabs__nav-wrap::after) {
    background: rgba(123, 28, 181, 0.2);
  }
}

.report-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(123, 28, 181, 0.1);
}

.info-label {
  font-size: 13px;
  color: $text-secondary;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: $text-primary;
  font-weight: 500;
  text-align: right;
}

.confidence-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;

  &.confidence--high {
    background: rgba(38, 198, 218, 0.15);
    color: $success-color;
  }

  &.confidence--medium {
    background: rgba(255, 179, 0, 0.15);
    color: $warning-color;
  }

  &.confidence--low {
    background: rgba(229, 57, 53, 0.15);
    color: $danger-color;
  }
}

.priority-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;

  &.priority--high {
    background: rgba(255, 140, 56, 0.15);
    color: $accent-color;
  }

  &.priority--urgent {
    background: rgba(229, 57, 53, 0.15);
    color: $danger-color;
  }

  &.priority--medium {
    background: rgba(255, 179, 0, 0.15);
    color: $warning-color;
  }

  &.priority--low {
    background: rgba(38, 198, 218, 0.15);
    color: $success-color;
  }
}

// 根因分析
.rca-cause {
  padding: 14px;
  border-radius: $border-radius-sm;
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid rgba(123, 28, 181, 0.15);
}

.rca-label {
  font-size: 12px;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.rca-value {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 8px;
}

.evidence-chain {
  margin-top: 4px;
}

.evidence-tree {
  border-left: 2px solid rgba(123, 28, 181, 0.2);
  padding-left: 0;
}

:deep(.evidence-node-wrapper) {
  padding: 4px 0;
}

:deep(.evidence-node) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

:deep(.evidence-node--observation) { background: rgba(123, 28, 181, 0.08); }
:deep(.evidence-node--test) { background: rgba(38, 198, 218, 0.08); }
:deep(.evidence-node--analysis) { background: rgba(255, 140, 56, 0.08); }
:deep(.evidence-node--conclusion) { background: rgba(229, 57, 53, 0.1); border: 1px solid rgba(229, 57, 53, 0.2); }

:deep(.evidence-type-icon) {
  font-size: 10px;
  color: $primary-light;
}

:deep(.evidence-label) {
  flex: 1;
  color: $text-primary;
}

:deep(.evidence-confidence) {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 8px;
}

:deep(.evidence-confidence.high) { background: rgba(38, 198, 218, 0.15); color: $success-color; }
:deep(.evidence-confidence.medium) { background: rgba(255, 179, 0, 0.15); color: $warning-color; }
:deep(.evidence-confidence.low) { background: rgba(229, 57, 53, 0.15); color: $danger-color; }

.factor-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  color: $text-secondary;
}

// 批次风险
.risk-badge {
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;

  &.risk--high { background: rgba(229, 57, 53, 0.15); color: $danger-color; }
  &.risk--medium { background: rgba(255, 179, 0, 0.15); color: $warning-color; }
  &.risk--low { background: rgba(38, 198, 218, 0.15); color: $success-color; }
}

.affected-tag {
  display: inline-block;
  padding: 2px 8px;
  margin: 2px;
  border-radius: 4px;
  background: rgba(123, 28, 181, 0.12);
  color: $primary-light;
  font-size: 12px;
}

.recommendation-text {
  padding: 10px 14px;
  border-radius: $border-radius-sm;
  background: rgba(255, 140, 56, 0.08);
  border: 1px solid rgba(255, 140, 56, 0.15);
  font-size: 13px;
  color: $text-secondary;
  line-height: 1.6;
}

// 处置建议卡片
.action-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-card {
  padding: 14px;
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    transform: translateX(4px);
  }

  &--monitoring { border-left: 3px solid $success-color; }
  &--inspection { border-left: 3px solid $primary-color; }
  &--repair { border-left: 3px solid $warning-color; }
  &--replacement { border-left: 3px solid $danger-color; }
}

.action-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.action-type-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(123, 28, 181, 0.15);
  color: $primary-light;
}

.action-urgency {
  font-size: 11px;
  color: $accent-color;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.action-desc {
  font-size: 12px;
  color: $text-secondary;
  margin-top: 4px;
}

// FMEA
.fmea-section {
  margin-top: 8px;
}

.fmea-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.fmea-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px;
  border-radius: $border-radius-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.fmea-label {
  font-size: 11px;
  color: $text-muted;
}

.fmea-score {
  font-size: 22px;
  font-weight: 700;

  &.fmea--low { color: $success-color; }
  &.fmea--medium { color: $warning-color; }
  &.fmea--high { color: $danger-color; }
  &--rpn { color: $accent-color !important; }
}

.fmea-item--rpn {
  background: rgba(255, 140, 56, 0.08);
  border-color: rgba(255, 140, 56, 0.2);
}

// 空状态
.report-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $text-muted;

  p {
    margin-top: 12px;
    font-size: 13px;
  }
}

// Element Plus 下拉菜单暗色
:deep(.el-select-dropdown) {
  background: #2d1054 !important;
  border-color: $border-color !important;
}

:deep(.el-select-dropdown__item) {
  color: $text-primary !important;

  &:hover, &.hover {
    background: rgba(123, 28, 181, 0.2) !important;
  }
}
</style>
