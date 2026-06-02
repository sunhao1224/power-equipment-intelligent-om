import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Equipment, EquipmentStats, Alarm, WorkOrder, HealthDistribution } from '@/types'

export const useEquipmentStore = defineStore('equipment', () => {
  const equipmentList = ref<Equipment[]>([])
  const stats = ref<EquipmentStats>({ total: 0, online: 0, warning: 0, offline: 0 })
  const alarms = ref<Alarm[]>([])
  const workOrders = ref<WorkOrder[]>([])
  const healthDistribution = ref<HealthDistribution>({ healthy: 0, attention: 0, abnormal: 0, critical: 0 })
  const isLoading = ref(false)

  const healthyEquipment = computed(() =>
    equipmentList.value.filter(e => e.healthLevel === 'healthy')
  )

  const attentionEquipment = computed(() =>
    equipmentList.value.filter(e => e.healthLevel === 'attention')
  )

  const abnormalEquipment = computed(() =>
    equipmentList.value.filter(e => e.healthLevel === 'abnormal')
  )

  const criticalEquipment = computed(() =>
    equipmentList.value.filter(e => e.healthLevel === 'critical')
  )

  function initMockData() {
    // 模拟设备列表
    equipmentList.value = [
      { id: 'EQ001', name: '#1主变压器', type: 'transformer', model: 'SFZ11-120000/220', location: 'A变电站', status: 'warning', healthScore: 62, healthLevel: 'attention', lastMaintenance: '2024-08-15', installDate: '2012-03-20', ratedVoltage: '220kV', ratedCapacity: '120MVA' },
      { id: 'EQ002', name: '#2主变压器', type: 'transformer', model: 'SFZ11-120000/220', location: 'A变电站', status: 'online', healthScore: 88, healthLevel: 'healthy', lastMaintenance: '2024-10-01', installDate: '2012-03-20', ratedVoltage: '220kV', ratedCapacity: '120MVA' },
      { id: 'EQ003', name: '#1断路器', type: 'breaker', model: 'LW36-252/T4000-50', location: 'A变电站', status: 'online', healthScore: 92, healthLevel: 'healthy', lastMaintenance: '2024-11-10', installDate: '2015-06-01', ratedVoltage: '220kV', ratedCapacity: '4000A' },
      { id: 'EQ004', name: '#2断路器', type: 'breaker', model: 'LW36-252/T4000-50', location: 'A变电站', status: 'online', healthScore: 85, healthLevel: 'healthy', lastMaintenance: '2024-09-20', installDate: '2015-06-01', ratedVoltage: '220kV', ratedCapacity: '4000A' },
      { id: 'EQ005', name: 'GIS-220kV', type: 'gis', model: 'ZF-252/T3150-40', location: 'B变电站', status: 'online', healthScore: 95, healthLevel: 'healthy', lastMaintenance: '2024-12-01', installDate: '2018-09-15', ratedVoltage: '220kV', ratedCapacity: '3150A' },
      { id: 'EQ006', name: '#3主变压器', type: 'transformer', model: 'SFZ10-90000/110', location: 'C变电站', status: 'warning', healthScore: 55, healthLevel: 'attention', lastMaintenance: '2024-06-15', installDate: '2010-11-10', ratedVoltage: '110kV', ratedCapacity: '90MVA' },
      { id: 'EQ007', name: '#1配变', type: 'transformer', model: 'S13-800/10', location: 'D配电站', status: 'online', healthScore: 78, healthLevel: 'attention', lastMaintenance: '2024-07-20', installDate: '2016-04-05', ratedVoltage: '10kV', ratedCapacity: '800kVA' },
      { id: 'EQ008', name: '#3断路器', type: 'breaker', model: 'ZW32-12/T630-20', location: 'D配电站', status: 'offline', healthScore: 35, healthLevel: 'critical', lastMaintenance: '2023-12-10', installDate: '2014-08-20', ratedVoltage: '10kV', ratedCapacity: '630A' },
      { id: 'EQ009', name: 'GIS-110kV', type: 'gis', model: 'ZF-126/T2000-40', location: 'C变电站', status: 'online', healthScore: 90, healthLevel: 'healthy', lastMaintenance: '2024-11-25', installDate: '2019-03-10', ratedVoltage: '110kV', ratedCapacity: '2000A' },
      { id: 'EQ010', name: '#4主变压器', type: 'transformer', model: 'SFZ11-150000/220', location: 'E变电站', status: 'online', healthScore: 91, healthLevel: 'healthy', lastMaintenance: '2024-10-30', installDate: '2020-01-15', ratedVoltage: '220kV', ratedCapacity: '150MVA' }
    ]

    // 统计数据
    stats.value = {
      total: equipmentList.value.length,
      online: equipmentList.value.filter(e => e.status === 'online' || e.status === 'warning').length,
      warning: equipmentList.value.filter(e => e.status === 'warning').length,
      offline: equipmentList.value.filter(e => e.status === 'offline').length
    }

    // 健康分布
    healthDistribution.value = {
      healthy: equipmentList.value.filter(e => e.healthLevel === 'healthy').length,
      attention: equipmentList.value.filter(e => e.healthLevel === 'attention').length,
      abnormal: equipmentList.value.filter(e => e.healthLevel === 'abnormal').length,
      critical: equipmentList.value.filter(e => e.healthLevel === 'critical').length
    }

    // 告警数据
    alarms.value = [
      { id: 'AL001', equipmentId: 'EQ001', equipmentName: '#1主变压器', level: 'danger', message: '油中C2H2含量超标 (8.7μL/L > 5μL/L)', timestamp: '2025-01-15 14:32:00', status: 'active' },
      { id: 'AL002', equipmentId: 'EQ001', equipmentName: '#1主变压器', level: 'warning', message: '顶层油温偏高 (72.5℃)', timestamp: '2025-01-15 14:28:00', status: 'active' },
      { id: 'AL003', equipmentId: 'EQ006', equipmentName: '#3主变压器', level: 'warning', message: '局部放电量增大趋势', timestamp: '2025-01-15 13:15:00', status: 'active' },
      { id: 'AL004', equipmentId: 'EQ008', equipmentName: '#3断路器', level: 'critical', message: 'SF6气体压力低告警', timestamp: '2025-01-15 11:45:00', status: 'active' },
      { id: 'AL005', equipmentId: 'EQ003', equipmentName: '#1断路器', level: 'info', message: '操作次数接近检修周期', timestamp: '2025-01-15 10:20:00', status: 'acknowledged' },
      { id: 'AL006', equipmentId: 'EQ007', equipmentName: '#1配变', level: 'warning', message: '负荷率超过80%', timestamp: '2025-01-15 09:30:00', status: 'active' },
      { id: 'AL007', equipmentId: 'EQ002', equipmentName: '#2主变压器', level: 'info', message: '定期DGA检测提醒', timestamp: '2025-01-14 16:00:00', status: 'resolved' }
    ]

    // 工单数据
    workOrders.value = [
      { id: 'WO001', title: '#1主变停电检修', equipmentId: 'EQ001', equipmentName: '#1主变压器', status: 'pending_review', priority: 'high', createdAt: '2025-01-15', scheduledDate: '2025-01-20', description: '根据DGA分析结果，需进行绕组直流电阻和绝缘电阻测试', actions: ['绕组直流电阻测试', '绝缘电阻测试', '油样化验'], estimatedCost: '5万元', assignedTo: '张工' },
      { id: 'WO002', title: '#3断路器SF6补气', equipmentId: 'EQ008', equipmentName: '#3断路器', status: 'approved', priority: 'urgent', createdAt: '2025-01-15', scheduledDate: '2025-01-16', description: 'SF6气体压力低，需补气并检漏', actions: ['SF6气体补充', '气密性检测', '微水含量测试'], estimatedCost: '2万元', assignedTo: '李工' },
      { id: 'WO003', title: '#3主变加强监测', equipmentId: 'EQ006', equipmentName: '#3主变压器', status: 'in_progress', priority: 'medium', createdAt: '2025-01-14', scheduledDate: '2025-01-15', description: '局放量呈增大趋势，需加强在线监测', actions: ['增加局放监测频率', 'DGA取样分析'], estimatedCost: '1万元', assignedTo: '王工' },
      { id: 'WO004', title: 'GIS年度预防性试验', equipmentId: 'EQ005', equipmentName: 'GIS-220kV', status: 'completed', priority: 'low', createdAt: '2025-01-10', scheduledDate: '2025-01-12', description: '年度预防性试验已完成，各项指标合格', actions: ['主回路电阻测试', 'SF6气体检测', '机构特性测试'], estimatedCost: '3万元', assignedTo: '赵工' }
    ]
  }

  return {
    equipmentList,
    stats,
    alarms,
    workOrders,
    healthDistribution,
    isLoading,
    healthyEquipment,
    attentionEquipment,
    abnormalEquipment,
    criticalEquipment,
    initMockData
  }
})
