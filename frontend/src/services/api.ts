import axios from 'axios'
import type {
  AgentTrace,
  ApiResponse,
  BatchRiskItem,
  DiagnosisInput,
  DiagnosisTask,
  Equipment,
  EvidenceItem,
  MockEvent
} from '@/types'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 12000
})

async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await promise
  return response.data.data
}

export const api = {
  overview: () => unwrap<any>(client.get('/overview')),
  equipment: () => unwrap<Equipment[]>(client.get('/equipment')),
  equipmentDetail: (id: string) => unwrap<Equipment>(client.get(`/equipment/${id}`)),
  mockEvents: () => unwrap<MockEvent[]>(client.get('/events/mock')),
  triggerDiagnosis: (payload: DiagnosisInput) =>
    unwrap<{ diagnosis_id: string; orchestrator_id: string; agent_trace_id: string; status: string }>(
      client.post('/diagnosis/trigger', payload)
    ),
  diagnosis: (id: string) => unwrap<DiagnosisTask>(client.get(`/diagnosis/${id}`)),
  trace: (traceId: string) => unwrap<AgentTrace>(client.get(`/agents/traces/${traceId}`)),
  evidence: (q = '') => unwrap<{ items: EvidenceItem[]; graph: { nodes: string[]; edges: string[][] } }>(
    client.get('/knowledge/evidence', { params: q ? { q } : {} })
  ),
  assessBatch: (equipment_id: string) =>
    unwrap<{ equipment_id: string; items: BatchRiskItem[]; summary: string }>(
      client.post('/batch/assess', { equipment_id, batch_criteria: {} })
    ),
  reports: () => unwrap<any[]>(client.get('/reports')),
  report: (id: string) => unwrap<any>(client.get(`/reports/${id}`))
}

export function diagnosisWsUrl(diagnosisId: string): string {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.hostname
  const port = window.location.port === '3000' || window.location.port === '3001'
    ? '8000'
    : window.location.port
  return `${protocol}://${host}:${port}/ws/diagnosis/${diagnosisId}`
}
