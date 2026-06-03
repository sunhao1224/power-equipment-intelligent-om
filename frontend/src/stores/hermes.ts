import { defineStore } from 'pinia'
import { api, diagnosisWsUrl } from '@/services/api'
import type { AgentNode, AgentTrace, BatchRiskItem, DiagnosisReport, DiagnosisTask, Equipment, EvidenceItem, MockEvent, WsEvent } from '@/types'

interface HermesState {
  overview: any
  equipment: Equipment[]
  events: MockEvent[]
  evidence: EvidenceItem[]
  graph: { nodes: string[]; edges: string[][] }
  batch: BatchRiskItem[]
  reports: DiagnosisReport[]
  currentDiagnosis?: DiagnosisTask
  currentTrace?: AgentTrace
  agents: AgentNode[]
  wsEvents: WsEvent[]
  loading: boolean
  running: boolean
}

export const useHermesStore = defineStore('hermes', {
  state: (): HermesState => ({
    overview: null,
    equipment: [],
    events: [],
    evidence: [],
    graph: { nodes: [], edges: [] },
    batch: [],
    reports: [],
    agents: [],
    wsEvents: [],
    loading: false,
    running: false
  }),

  getters: {
    selectedReport: (state) => state.currentDiagnosis?.report,
    completedAgents: (state) => state.agents.filter((agent) => agent.status === 'completed').length
  },

  actions: {
    async bootstrap() {
      this.loading = true
      try {
        const [overview, equipment, events, knowledge, reports] = await Promise.all([
          api.overview(),
          api.equipment(),
          api.mockEvents(),
          api.evidence(),
          api.reports()
        ])
        this.overview = overview
        this.equipment = equipment
        this.events = events
        this.evidence = knowledge.items
        this.graph = knowledge.graph
        this.reports = reports
      } finally {
        this.loading = false
      }
    },

    async loadEvidence(query = '') {
      const result = await api.evidence(query)
      this.evidence = result.items
      this.graph = result.graph
    },

    async loadBatch(equipmentId = 'EQ-TR-001') {
      const result = await api.assessBatch(equipmentId)
      this.batch = result.items
      return result
    },

    async loadReports() {
      this.reports = await api.reports()
    },

    async triggerDiagnosis(eventId?: string) {
      const event = this.events.find((item) => item.event_id === eventId) ?? this.events[0]
      this.running = true
      this.wsEvents = []
      this.agents = []
      const created = await api.triggerDiagnosis({
        equipment_id: event?.equipment_id ?? 'EQ-TR-001',
        event_type: 'mock_event',
        event_id: event?.event_id,
        sensor_data: event?.sensor_data ?? {},
        time_window: event?.time_window ?? '24h',
        priority: event?.priority ?? 'important'
      })
      this.currentDiagnosis = {
        diagnosis_id: created.diagnosis_id,
        orchestrator_id: created.orchestrator_id,
        agent_trace_id: created.agent_trace_id,
        status: created.status,
        input: {
          equipment_id: event?.equipment_id ?? 'EQ-TR-001',
          event_type: 'mock_event',
          event_id: event?.event_id
        },
        agents_output: [],
        review_findings: []
      }
      await this.openDiagnosisStream(created.diagnosis_id)
    },

    openDiagnosisStream(diagnosisId: string) {
      return new Promise<void>((resolve) => {
        const socket = new WebSocket(diagnosisWsUrl(diagnosisId))
        socket.onmessage = async (message) => {
          const event = JSON.parse(message.data) as WsEvent
          this.wsEvents.unshift(event)
          if (event.event_type === 'agent_spawned') {
            this.upsertAgent(event.payload.agent)
          }
          if (event.event_type === 'agent_progress') {
            this.patchAgent(event.payload.agent_id, { status: 'running', progress: event.payload.progress })
          }
          if (event.event_type === 'agent_result') {
            this.upsertAgent(event.payload.agent)
          }
          if (event.event_type === 'diagnosis_done') {
            this.currentDiagnosis = await api.diagnosis(diagnosisId)
            this.currentTrace = await api.trace(this.currentDiagnosis.agent_trace_id)
            this.agents = this.currentDiagnosis.agents_output
            await this.loadReports()
            this.running = false
          }
        }
        socket.onerror = () => {
          this.running = false
          resolve()
        }
        socket.onclose = () => resolve()
      })
    },

    upsertAgent(agent: AgentNode) {
      const index = this.agents.findIndex((item) => item.agent_id === agent.agent_id)
      if (index >= 0) this.agents[index] = agent
      else this.agents.push(agent)
    },

    patchAgent(agentId: string, patch: Partial<AgentNode>) {
      const agent = this.agents.find((item) => item.agent_id === agentId)
      if (agent) Object.assign(agent, patch)
    }
  }
})
