// ===== 设备相关 =====
export interface Equipment {
  id: string
  name: string
  type: 'transformer' | 'breaker' | 'gis'
  model: string
  location: string
  status: 'online' | 'offline' | 'warning' | 'error'
  healthScore: number
  healthLevel: 'healthy' | 'attention' | 'abnormal' | 'critical'
  lastMaintenance: string
  installDate: string
  ratedVoltage: string
  ratedCapacity: string
}

export interface EquipmentStats {
  total: number
  online: number
  warning: number
  offline: number
}

export interface EquipmentTypeDistribution {
  type: string
  count: number
  percentage: number
}

// ===== 告警相关 =====
export interface Alarm {
  id: string
  equipmentId: string
  equipmentName: string
  level: 'info' | 'warning' | 'danger' | 'critical'
  message: string
  timestamp: string
  status: 'active' | 'acknowledged' | 'resolved'
}

export interface AlarmTrend {
  date: string
  count: number
}

// ===== 健康相关 =====
export interface HealthDistribution {
  healthy: number
  attention: number
  abnormal: number
  critical: number
}

// ===== 聊天相关 =====
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  confidence?: number
  sources?: KnowledgeSource[]
}

export interface KnowledgeSource {
  id: string
  title: string
  type: 'standard' | 'manual' | 'history' | 'expert'
  relevance: number
  excerpt: string
}

export interface ChatSession {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: ChatMessage[]
}

// ===== 诊断相关 =====
export interface SensorData {
  name: string
  value: number
  unit: string
  status: 'normal' | 'warning' | 'danger'
  threshold?: { min: number; max: number }
}

export interface DGAData {
  h2: number
  ch4: number
  c2h2: number
  c2h4: number
  c2h6: number
  co: number
  co2: number
  totalHydrocarbon: number
}

export interface AgentNode {
  id: string
  name: string
  nameEn: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  description: string
  result?: any
}

export interface DiagnosisResult {
  equipmentId: string
  equipmentName: string
  timestamp: string
  overallConfidence: number
  rootCause: RootCauseAnalysis
  batchRisk: BatchRiskAnalysis
  fmea: FMEAAnalysis
  recommendation: MaintenanceRecommendation
}

export interface RootCauseAnalysis {
  primaryCause: string
  confidence: number
  evidenceChain: EvidenceNode[]
  contributingFactors: string[]
}

export interface EvidenceNode {
  id: string
  label: string
  type: 'observation' | 'test' | 'analysis' | 'conclusion'
  children?: EvidenceNode[]
  confidence?: number
}

export interface BatchRiskAnalysis {
  affectedEquipment: string[]
  riskLevel: 'low' | 'medium' | 'high'
  commonDefect: string
  recommendation: string
}

export interface FMEAAnalysis {
  failureMode: string
  effect: string
  severity: number
  occurrence: number
  detection: number
  rpn: number
}

export interface MaintenanceRecommendation {
  actions: MaintenanceAction[]
  priority: 'low' | 'medium' | 'high' | 'urgent'
  estimatedCost: string
  estimatedDuration: string
}

export interface MaintenanceAction {
  id: string
  title: string
  description: string
  type: 'inspection' | 'repair' | 'replacement' | 'monitoring'
  urgency: string
}

// ===== 维护决策相关 =====
export interface MaintenancePlan {
  id: string
  equipmentId: string
  equipmentName: string
  type: 'preventive' | 'corrective' | 'predictive'
  scheduledDate: string
  status: 'pending_review' | 'approved' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  description: string
  estimatedCost: string
  assignedTo: string
}

export interface WorkOrder {
  id: string
  title: string
  equipmentId: string
  equipmentName: string
  status: 'pending_review' | 'approved' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  createdAt: string
  scheduledDate: string
  description: string
  actions: string[]
  estimatedCost: string
  assignedTo: string
}

// ===== API 响应 =====
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
