export type RiskLevel = 'normal' | 'important' | 'urgent' | 'low' | 'medium' | 'high' | 'critical'
export type AgentStatus = 'pending' | 'spawned' | 'running' | 'tool_calling' | 'completed' | 'failed' | 'need_human_review'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface Equipment {
  equipment_id: string
  name: string
  type: string
  manufacturer: string
  model: string
  batch_no: string
  location: string
  voltage_level: string
  commissioned_at: string
  health_score: number
  risk_level: RiskLevel
}

export interface MockEvent {
  event_id: string
  equipment_id: string
  title: string
  event_type: 'mock_event'
  priority: 'normal' | 'important' | 'urgent'
  time_window: string
  sensor_data: Record<string, number>
  summary: string
}

export interface DiagnosisInput {
  equipment_id: string
  event_type: 'mock_event' | 'historical_replay' | 'manual_upload'
  event_id?: string
  sensor_data?: Record<string, unknown>
  time_window?: string
  priority?: 'normal' | 'important' | 'urgent'
  edge_context?: Record<string, unknown>
}

export interface AgentNode {
  agent_id: string
  name: string
  role: string
  status: AgentStatus
  progress: number
  confidence: number
  evidence_count: number
  duration_ms: number
  summary: string
}

export interface EvidenceItem {
  evidence_id: string
  title: string
  source_type: 'regulation' | 'case' | 'graph' | 'timeseries' | 'standard'
  source_id: string
  content: string
  confidence: number
  linked_nodes: string[]
  tags: string[]
}

export interface ToolCall {
  call_id: string
  agent_id: string
  tool_name: string
  request_summary: string
  response_summary: string
  latency_ms: number
  status: string
}

export interface SkillCall {
  call_id: string
  agent_id: string
  skill_name: string
  skill_version: string
  status: string
}

export interface AgentTrace {
  trace_id: string
  diagnosis_id: string
  orchestrator_id: string
  status: string
  started_at: string
  completed_at?: string
  agent_steps: AgentNode[]
  tool_calls: ToolCall[]
  skill_calls: SkillCall[]
  evidence_links: EvidenceItem[]
}

export interface BatchRiskItem {
  equipment_id: string
  equipment_name: string
  manufacturer: string
  model: string
  batch_no: string
  location: string
  risk_level: RiskLevel
  probability_6m: number
  probability_12m: number
  probability_24m: number
  reason: string
}

export interface FmeaItem {
  failure_mode: string
  component: string
  severity: number
  occurrence: number
  detection: number
  rpn: number
  recommendation: string
}

export interface WorkOrderDraft {
  title: string
  priority: 'normal' | 'important' | 'urgent'
  actions: string[]
  required_roles: string[]
  spare_parts: string[]
  safety_notes: string[]
  estimated_hours: number
}

export interface DiagnosisReport {
  report_id: string
  diagnosis_id: string
  equipment_id: string
  title: string
  risk_level: 'normal' | 'important' | 'urgent'
  root_causes: Array<{ name: string; confidence: number; evidence_ids: string[] }>
  component_path: string[]
  batch_risks: BatchRiskItem[]
  fmea: FmeaItem[]
  work_order: WorkOrderDraft
  review_findings: Array<{ level: string; title: string; detail: string }>
  evidence_ids: string[]
  created_at: string
}

export interface DiagnosisTask {
  diagnosis_id: string
  orchestrator_id: string
  agent_trace_id: string
  status: string
  input: DiagnosisInput
  agents_output: AgentNode[]
  report?: DiagnosisReport
  review_findings: Array<Record<string, unknown>>
}

export interface WsEvent {
  event_type: string
  diagnosis_id: string
  timestamp: string
  payload: Record<string, any>
}
