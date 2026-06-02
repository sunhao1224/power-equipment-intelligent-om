import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatSession, ChatMessage, KnowledgeSource } from '@/types'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string | null>(null)
  const isLoading = ref(false)

  const currentSession = computed(() => {
    return sessions.value.find(s => s.id === currentSessionId.value) || null
  })

  const messages = computed(() => {
    return currentSession.value?.messages || []
  })

  function createSession(title: string = '新对话') {
    const session: ChatSession = {
      id: `session_${Date.now()}`,
      title,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: []
    }
    sessions.value.unshift(session)
    currentSessionId.value = session.id
    return session
  }

  function deleteSession(id: string) {
    const index = sessions.value.findIndex(s => s.id === id)
    if (index !== -1) {
      sessions.value.splice(index, 1)
      if (currentSessionId.value === id) {
        currentSessionId.value = sessions.value.length > 0 ? sessions.value[0].id : null
      }
    }
  }

  function selectSession(id: string) {
    currentSessionId.value = id
  }

  function addUserMessage(content: string) {
    if (!currentSessionId.value) {
      createSession(content.slice(0, 20))
    }
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    if (session) {
      const message: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date().toISOString()
      }
      session.messages.push(message)
      session.updatedAt = new Date().toISOString()
      // Update title from first message
      if (session.messages.length === 1) {
        session.title = content.slice(0, 30) + (content.length > 30 ? '...' : '')
      }
    }
  }

  function addAssistantMessage(content: string, confidence?: number, sources?: KnowledgeSource[]) {
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    if (session) {
      const message: ChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content,
        timestamp: new Date().toISOString(),
        confidence,
        sources
      }
      session.messages.push(message)
      session.updatedAt = new Date().toISOString()
    }
  }

  // 模拟 AI 回复
  async function sendMessage(content: string) {
    addUserMessage(content)
    isLoading.value = true

    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1500))

    const mockResponses: Record<string, { content: string; confidence: number; sources: KnowledgeSource[] }> = {
      '变压器油温异常分析': {
        content: `## 变压器油温异常分析\n\n根据您提供的信息，我对变压器油温异常问题进行了综合分析：\n\n### 可能原因\n1. **冷却系统故障** - 风扇或油泵运行异常导致散热不足\n2. **过负荷运行** - 长期超过额定容量运行\n3. **内部故障** - 绕组匝间短路或铁芯多点接地\n4. **环境温度过高** - 夏季高温环境散热困难\n\n### 建议措施\n- 检查冷却系统各组件运行状态\n- 核实当前负荷是否在额定范围内\n- 进行油中溶解气体分析（DGA）\n- 检查温度传感器是否准确\n\n> 根据历史数据分析，85%的油温异常与冷却系统故障相关。`,
        confidence: 0.89,
        sources: [
          { id: 's1', title: 'DL/T 722-2014 变压器油中溶解气体分析和判断导则', type: 'standard', relevance: 0.95, excerpt: '油温升高伴随总烃含量增大时，应考虑存在过热性故障...' },
          { id: 's2', title: '变压器运行维护手册 第3章', type: 'manual', relevance: 0.88, excerpt: '顶层油温超过85℃时应立即检查冷却系统...' },
          { id: 's3', title: '2024年Q3变压器故障案例库', type: 'history', relevance: 0.82, excerpt: '某站#2主变油温异常升高至92℃，经检查为风扇电机烧毁...' }
        ]
      },
      'default': {
        content: `## 分析结果\n\n根据您的提问，我进行了知识库检索和分析：\n\n### 关键信息\n1. 已检索到相关标准文档 **3份**\n2. 匹配历史运维案例 **5个**\n3. 关联设备运行数据 **2组**\n\n### 初步判断\n基于现有数据分析，该问题可能与设备运行环境变化或组件老化有关。建议进一步进行现场检查和测试验证。\n\n### 建议操作\n- 安排专项巡检\n- 调取近期在线监测数据进行趋势分析\n- 必要时进行停电试验\n\n如需更详细的分析，请提供具体的设备编号和异常现象描述。`,
        confidence: 0.75,
        sources: [
          { id: 's1', title: '电力设备预防性试验规程 DL/T 596', type: 'standard', relevance: 0.85, excerpt: '设备运行中应定期进行绝缘电阻测量...' },
          { id: 's2', title: '变电站设备运维管理规范', type: 'manual', relevance: 0.78, excerpt: '对于运行超过15年的设备应缩短巡检周期...' }
        ]
      }
    }

    const key = Object.keys(mockResponses).find(k => content.includes(k)) || 'default'
    const response = mockResponses[key]

    addAssistantMessage(response.content, response.confidence, response.sources)
    isLoading.value = false
  }

  // 初始化模拟数据
  function initMockData() {
    if (sessions.value.length === 0) {
      createSession('变压器油温问题咨询')
      addUserMessage('变压器油温偏高怎么处理？')
      addAssistantMessage(
        '## 变压器油温偏高处理建议\n\n1. **立即检查**冷却系统运行状态\n2. 核实负荷电流是否超标\n3. 进行DGA分析判断内部状态\n4. 如油温持续升高，应考虑降负荷或停运',
        0.85,
        [
          { id: 's1', title: 'DL/T 572 变压器运行规程', type: 'standard', relevance: 0.92, excerpt: '油浸式变压器顶层油温一般不超过85℃...' }
        ]
      )
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession,
    messages,
    isLoading,
    createSession,
    deleteSession,
    selectSession,
    sendMessage,
    initMockData
  }
})
