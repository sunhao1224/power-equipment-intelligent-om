import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type {
  ApiResponse,
  Equipment,
  EquipmentStats,
  EquipmentTypeDistribution,
  Alarm,
  AlarmTrend,
  HealthDistribution,
  ChatSession,
  ChatMessage,
  DiagnosisResult,
  SensorData,
  AgentNode,
  MaintenancePlan,
  WorkOrder
} from '@/types'

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可在此添加 token 等认证信息
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    if (data.code !== 0 && data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请稍后重试')
    } else {
      ElMessage.error('网络异常，请检查连接')
    }
    return Promise.reject(error)
  }
)

// ===== Dashboard API =====
export const dashboardApi = {
  getEquipmentStats: (): Promise<ApiResponse<EquipmentStats>> =>
    apiClient.get('/dashboard/equipment-stats').then(r => r.data),

  getTypeDistribution: (): Promise<ApiResponse<EquipmentTypeDistribution[]>> =>
    apiClient.get('/dashboard/type-distribution').then(r => r.data),

  getAlarmTrend: (days: number = 7): Promise<ApiResponse<AlarmTrend[]>> =>
    apiClient.get('/dashboard/alarm-trend', { params: { days } }).then(r => r.data),

  getHealthDistribution: (): Promise<ApiResponse<HealthDistribution>> =>
    apiClient.get('/dashboard/health-distribution').then(r => r.data),

  getLatestAlarms: (limit: number = 10): Promise<ApiResponse<Alarm[]>> =>
    apiClient.get('/dashboard/latest-alarms', { params: { limit } }).then(r => r.data)
}

// ===== 设备 API =====
export const equipmentApi = {
  getList: (params?: { type?: string; status?: string; page?: number; pageSize?: number }): Promise<ApiResponse<Equipment[]>> =>
    apiClient.get('/equipment', { params }).then(r => r.data),

  getById: (id: string): Promise<ApiResponse<Equipment>> =>
    apiClient.get(`/equipment/${id}`).then(r => r.data),

  getSensorData: (id: string): Promise<ApiResponse<SensorData[]>> =>
    apiClient.get(`/equipment/${id}/sensor-data`).then(r => r.data),

  getHealthScore: (id: string): Promise<ApiResponse<{ score: number; level: string }>> =>
    apiClient.get(`/equipment/${id}/health-score`).then(r => r.data)
}

// ===== 聊天 API =====
export const chatApi = {
  getSessions: (): Promise<ApiResponse<ChatSession[]>> =>
    apiClient.get('/chat/sessions').then(r => r.data),

  getSession: (id: string): Promise<ApiResponse<ChatSession>> =>
    apiClient.get(`/chat/sessions/${id}`).then(r => r.data),

  createSession: (title?: string): Promise<ApiResponse<ChatSession>> =>
    apiClient.post('/chat/sessions', { title }).then(r => r.data),

  deleteSession: (id: string): Promise<ApiResponse<void>> =>
    apiClient.delete(`/chat/sessions/${id}`).then(r => r.data),

  sendMessage: (sessionId: string, content: string): Promise<ApiResponse<ChatMessage>> =>
    apiClient.post(`/chat/sessions/${sessionId}/messages`, { content }).then(r => r.data),

  searchKnowledge: (query: string): Promise<ApiResponse<any[]>> =>
    apiClient.post('/chat/knowledge/search', { query }).then(r => r.data)
}

// ===== 诊断 API =====
export const diagnosisApi = {
  startDiagnosis: (equipmentId: string): Promise<ApiResponse<{ taskId: string }>> =>
    apiClient.post('/diagnosis/start', { equipmentId }).then(r => r.data),

  getDiagnosisStatus: (taskId: string): Promise<ApiResponse<{ agents: AgentNode[]; progress: number }>> =>
    apiClient.get(`/diagnosis/${taskId}/status`).then(r => r.data),

  getDiagnosisResult: (taskId: string): Promise<ApiResponse<DiagnosisResult>> =>
    apiClient.get(`/diagnosis/${taskId}/result`).then(r => r.data),

  getDiagnosisHistory: (equipmentId?: string): Promise<ApiResponse<DiagnosisResult[]>> =>
    apiClient.get('/diagnosis/history', { params: { equipmentId } }).then(r => r.data)
}

// ===== 维护决策 API =====
export const maintenanceApi = {
  getPlans: (params?: { equipmentId?: string; status?: string }): Promise<ApiResponse<MaintenancePlan[]>> =>
    apiClient.get('/maintenance/plans', { params }).then(r => r.data),

  generatePlan: (equipmentId: string): Promise<ApiResponse<MaintenancePlan>> =>
    apiClient.post('/maintenance/plans/generate', { equipmentId }).then(r => r.data),

  getWorkOrders: (params?: { status?: string }): Promise<ApiResponse<WorkOrder[]>> =>
    apiClient.get('/maintenance/work-orders', { params }).then(r => r.data),

  updateWorkOrderStatus: (id: string, status: string): Promise<ApiResponse<WorkOrder>> =>
    apiClient.patch(`/maintenance/work-orders/${id}/status`, { status }).then(r => r.data)
}

export default apiClient
