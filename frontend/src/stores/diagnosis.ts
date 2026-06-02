import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AgentNode, DiagnosisResult, SensorData, EvidenceNode } from '@/types'

export const useDiagnosisStore = defineStore('diagnosis', () => {
  const selectedEquipmentId = ref<string | null>(null)
  const isDiagnosing = ref(false)
  const diagnosisProgress = ref(0)
  const currentTaskId = ref<string | null>(null)
  const agents = ref<AgentNode[]>([])
  const diagnosisResult = ref<DiagnosisResult | null>(null)
  const sensorData = ref<SensorData[]>([])

  const isComplete = computed(() => {
    return agents.value.length > 0 && agents.value.every(a => a.status === 'completed')
  })

  function initAgents() {
    agents.value = [
      {
        id: 'rca',
        name: '根因分析',
        nameEn: 'RCA Agent',
        status: 'pending',
        progress: 0,
        description: '分析设备故障的根本原因，构建证据链'
      },
      {
        id: 'batch',
        name: '批次风险',
        nameEn: 'Batch Risk Agent',
        status: 'pending',
        progress: 0,
        description: '评估同批次设备的潜在风险'
      },
      {
        id: 'fmea',
        name: '失效模式',
        nameEn: 'FMEA Agent',
        status: 'pending',
        progress: 0,
        description: '进行失效模式与影响分析'
      },
      {
        id: 'decision',
        name: '处置决策',
        nameEn: 'Decision Agent',
        status: 'pending',
        progress: 0,
        description: '生成维护处置建议方案'
      },
      {
        id: 'review',
        name: '综合评审',
        nameEn: 'Review Agent',
        status: 'pending',
        progress: 0,
        description: '综合各Agent结果进行最终评审'
      }
    ]
  }

  function loadMockSensorData(equipmentId: string) {
    sensorData.value = [
      { name: '油温', value: 72.5, unit: '℃', status: 'warning', threshold: { min: 0, max: 85 } },
      { name: '绕组温度', value: 88.3, unit: '℃', status: 'danger', threshold: { min: 0, max: 95 } },
      { name: '油中H2', value: 45.2, unit: 'μL/L', status: 'warning', threshold: { min: 0, max: 150 } },
      { name: '油中C2H2', value: 8.7, unit: 'μL/L', status: 'danger', threshold: { min: 0, max: 5 } },
      { name: '油中CH4', value: 125.6, unit: 'μL/L', status: 'normal', threshold: { min: 0, max: 200 } },
      { name: '局部放电', value: 350, unit: 'pC', status: 'warning', threshold: { min: 0, max: 500 } },
      { name: '铁芯接地电流', value: 0.8, unit: 'A', status: 'normal', threshold: { min: 0, max: 1.0 } },
      { name: '油中微水', value: 18.5, unit: 'mg/L', status: 'normal', threshold: { min: 0, max: 35 } }
    ]
  }

  async function startDiagnosis(equipmentId: string) {
    selectedEquipmentId.value = equipmentId
    isDiagnosing.value = true
    diagnosisProgress.value = 0
    diagnosisResult.value = null
    currentTaskId.value = `task_${Date.now()}`

    initAgents()
    loadMockSensorData(equipmentId)

    // 模拟逐步完成各Agent
    for (let i = 0; i < agents.value.length; i++) {
      agents.value[i].status = 'running'

      // 模拟进度
      for (let p = 0; p <= 100; p += 10) {
        await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 200))
        agents.value[i].progress = p
        diagnosisProgress.value = Math.round(((i * 100 + p) / (agents.value.length * 100)) * 100)
      }

      agents.value[i].status = 'completed'
      agents.value[i].progress = 100
    }

    // 设置模拟诊断结果
    diagnosisResult.value = {
      equipmentId,
      equipmentName: '#1主变压器',
      timestamp: new Date().toISOString(),
      overallConfidence: 0.87,
      rootCause: {
        primaryCause: '绕组匝间绝缘劣化导致局部过热',
        confidence: 0.87,
        evidenceChain: [
          {
            id: 'e1',
            label: '油温异常升高 (72.5℃)',
            type: 'observation',
            confidence: 0.95,
            children: [
              {
                id: 'e2',
                label: 'DGA分析: C2H2超标 (8.7μL/L)',
                type: 'test',
                confidence: 0.92,
                children: [
                  {
                    id: 'e3',
                    label: '三比值法判断: 高温过热故障',
                    type: 'analysis',
                    confidence: 0.88,
                    children: [
                      {
                        id: 'e4',
                        label: '结论: 绕组匝间绝缘劣化',
                        type: 'conclusion',
                        confidence: 0.87
                      }
                    ]
                  }
                ]
              },
              {
                id: 'e5',
                label: '局放量增大 (350pC)',
                type: 'test',
                confidence: 0.85,
                children: [
                  {
                    id: 'e6',
                    label: '佐证: 绝缘劣化程度加剧',
                    type: 'analysis',
                    confidence: 0.82
                  }
                ]
              }
            ]
          }
        ],
        contributingFactors: [
          '设备运行年限较长（已投运12年）',
          '近两年负荷率持续偏高（平均85%以上）',
          '上次大修距今已超过6年'
        ]
      },
      batchRisk: {
        affectedEquipment: ['#2主变压器', '#3主变压器'],
        riskLevel: 'medium',
        commonDefect: '同批次绕组绝缘材料可能存在批次性质量缺陷',
        recommendation: '建议对同批次设备进行DGA普查和频响法绕组变形测试'
      },
      fmea: {
        failureMode: '绕组匝间短路',
        effect: '局部过热、油中特征气体超标、严重时可能导致设备跳闸',
        severity: 8,
        occurrence: 5,
        detection: 3,
        rpn: 120
      },
      recommendation: {
        actions: [
          { id: 'a1', title: '立即降低负荷至70%以下', description: '减缓绝缘劣化速度，降低故障风险', type: 'monitoring', urgency: '立即执行' },
          { id: 'a2', title: '安排停电试验', description: '进行绕组直流电阻、绝缘电阻和频响法测试', type: 'inspection', urgency: '一周内' },
          { id: 'a3', title: '加强DGA监测频率', description: '由每月一次改为每周一次在线监测', type: 'monitoring', urgency: '立即执行' },
          { id: 'a4', title: '准备备用变压器', description: '如试验结果确认绕组故障，需安排更换', type: 'replacement', urgency: '两周内' }
        ],
        priority: 'high',
        estimatedCost: '15-25万元',
        estimatedDuration: '7-14天（含试验和决策）'
      }
    }

    isDiagnosing.value = false
    diagnosisProgress.value = 100
  }

  return {
    selectedEquipmentId,
    isDiagnosing,
    diagnosisProgress,
    currentTaskId,
    agents,
    diagnosisResult,
    sensorData,
    isComplete,
    initAgents,
    loadMockSensorData,
    startDiagnosis
  }
})
