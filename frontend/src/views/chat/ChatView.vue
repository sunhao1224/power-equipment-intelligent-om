<template>
  <div class="chat-view">
    <!-- 左侧会话列表 -->
    <div class="session-sidebar">
      <div class="session-header">
        <h3>历史会话</h3>
        <el-button type="primary" size="small" round @click="handleNewSession">
          <el-icon><Plus /></el-icon> 新建
        </el-button>
      </div>

      <div class="session-list">
        <div
          v-for="session in chatStore.sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: session.id === chatStore.currentSessionId }"
          @click="chatStore.selectSession(session.id)"
        >
          <el-icon :size="16"><ChatDotRound /></el-icon>
          <div class="session-info">
            <div class="session-title">{{ session.title }}</div>
            <div class="session-time">{{ formatDate(session.updatedAt) }}</div>
          </div>
          <el-icon
            class="session-delete"
            :size="14"
            @click.stop="handleDeleteSession(session.id)"
          >
            <Delete />
          </el-icon>
        </div>
      </div>
    </div>

    <!-- 中间聊天区域 -->
    <div class="chat-main">
      <!-- 消息区域 -->
      <div class="message-area" ref="messageAreaRef">
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <el-icon :size="48" color="rgba(123,28,181,0.4)"><ChatDotRound /></el-icon>
          <h3>开始智能运维对话</h3>
          <p>您可以向我提问关于电力设备运维、故障分析、标准规范等方面的问题</p>

          <!-- 快捷问题 -->
          <div class="quick-questions">
            <div
              v-for="q in quickQuestions"
              :key="q"
              class="quick-question-btn"
              @click="handleQuickQuestion(q)"
            >
              <el-icon><Promotion /></el-icon>
              {{ q }}
            </div>
          </div>
        </div>

        <div v-else class="message-list">
          <div
            v-for="message in chatStore.messages"
            :key="message.id"
            class="message-wrapper"
            :class="[`message-wrapper--${message.role}`]"
          >
            <!-- 头像 -->
            <div class="message-avatar" :class="[`avatar--${message.role}`]">
              <el-icon v-if="message.role === 'user'" :size="18"><User /></el-icon>
              <el-icon v-else :size="18"><Monitor /></el-icon>
            </div>

            <!-- 消息内容 -->
            <div class="message-body">
              <div class="message-role">{{ message.role === 'user' ? '我' : 'AI 运维助手' }}</div>

              <div class="message-content" v-html="renderMarkdown(message.content)" />

              <!-- 置信度标签 -->
              <div v-if="message.confidence" class="confidence-tag">
                <span class="confidence-label">置信度：</span>
                <el-progress
                  :percentage="Math.round(message.confidence * 100)"
                  :stroke-width="6"
                  :width="80"
                  :color="getConfidenceColor(message.confidence)"
                  type="circle"
                  :show-text="true"
                  :format="() => `${Math.round(message.confidence! * 100)}%`"
                  class="confidence-progress"
                />
              </div>

              <!-- 知识来源 -->
              <div v-if="message.sources && message.sources.length > 0" class="sources-section">
                <div
                  class="sources-toggle"
                  @click="toggleSources(message.id)"
                >
                  <el-icon :size="14"><Document /></el-icon>
                  <span>引用来源 ({{ message.sources.length }})</span>
                  <el-icon :size="12" class="toggle-arrow" :class="{ expanded: expandedSources.includes(message.id) }">
                    <ArrowRight />
                  </el-icon>
                </div>

                <transition name="slide-down">
                  <div v-if="expandedSources.includes(message.id)" class="sources-list">
                    <div v-for="source in message.sources" :key="source.id" class="source-item">
                      <div class="source-header">
                        <span class="source-type" :class="[`source-type--${source.type}`]">
                          {{ getSourceTypeLabel(source.type) }}
                        </span>
                        <span class="source-relevance">
                          相关度 {{ Math.round(source.relevance * 100) }}%
                        </span>
                      </div>
                      <div class="source-title">{{ source.title }}</div>
                      <div class="source-excerpt">{{ source.excerpt }}</div>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>

          <!-- 加载指示器 -->
          <div v-if="chatStore.isLoading" class="message-wrapper message-wrapper--assistant">
            <div class="message-avatar avatar--assistant">
              <el-icon :size="18"><Monitor /></el-icon>
            </div>
            <div class="message-body">
              <div class="message-role">AI 运维助手</div>
              <div class="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区域 -->
      <div class="input-area">
        <!-- 快捷问题标签 -->
        <div class="input-quick-tags">
          <span
            v-for="q in quickQuestions"
            :key="q"
            class="input-quick-tag"
            @click="handleQuickQuestion(q)"
          >
            {{ q }}
          </span>
        </div>

        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的问题，如：变压器DGA分析结果如何解读？"
            @keydown.enter.exact.prevent="handleSend"
            class="chat-input"
          />
          <el-button
            type="primary"
            :disabled="!inputMessage.trim() || chatStore.isLoading"
            @click="handleSend"
            class="send-btn"
            circle
          >
            <el-icon><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import {
  Plus, Delete, ChatDotRound, Promotion, User, Monitor, Document, ArrowRight
} from '@element-plus/icons-vue'
import type { KnowledgeSource } from '@/types'

const chatStore = useChatStore()

const inputMessage = ref('')
const messageAreaRef = ref<HTMLElement>()
const expandedSources = ref<string[]>([])

const quickQuestions = [
  '变压器油温异常分析',
  'GIS气室压力标准',
  '断路器操作机构故障排查',
  'DGA三比值法解读'
]

function renderMarkdown(content: string): string {
  // 简单的 Markdown 渲染
  let html = content
  // Headers
  html = html.replace(/^### (.*$)/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.*$)/gm, '<h3>$1</h3>')
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  // Blockquote
  html = html.replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
  // Lists
  html = html.replace(/^- (.*$)/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  // Numbered lists
  html = html.replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
  // Line breaks
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br/>')
  html = `<p>${html}</p>`
  return html
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return '#26C6DA'
  if (confidence >= 0.6) return '#FFB300'
  return '#E53935'
}

function getSourceTypeLabel(type: string): string {
  const map: Record<string, string> = {
    standard: '标准规范',
    manual: '运维手册',
    history: '历史案例',
    expert: '专家经验'
  }
  return map[type] || type
}

function toggleSources(messageId: string) {
  const index = expandedSources.value.indexOf(messageId)
  if (index === -1) {
    expandedSources.value.push(messageId)
  } else {
    expandedSources.value.splice(index, 1)
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

function handleNewSession() {
  chatStore.createSession()
}

function handleDeleteSession(id: string) {
  chatStore.deleteSession(id)
}

function handleQuickQuestion(question: string) {
  inputMessage.value = question
  handleSend()
}

async function handleSend() {
  const content = inputMessage.value.trim()
  if (!content || chatStore.isLoading) return

  inputMessage.value = ''
  await chatStore.sendMessage(content)
}

function scrollToBottom() {
  nextTick(() => {
    if (messageAreaRef.value) {
      messageAreaRef.value.scrollTop = messageAreaRef.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, scrollToBottom)
watch(() => chatStore.isLoading, scrollToBottom)
</script>

<style lang="scss" scoped>
.chat-view {
  display: flex;
  height: 100%;
  gap: 16px;
  animation: fadeIn 0.4s ease;
}

// 左侧会话列表
.session-sidebar {
  width: 260px;
  flex-shrink: 0;
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid $border-color;
  border-radius: $border-radius;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid $border-color;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
  }
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: $border-radius-sm;
  cursor: pointer;
  transition: all 0.2s ease;
  color: $text-secondary;

  &:hover {
    background: rgba(123, 28, 181, 0.15);

    .session-delete {
      opacity: 1;
    }
  }

  &.active {
    background: rgba(123, 28, 181, 0.25);
    color: $text-primary;
    box-shadow: inset 0 0 0 1px rgba(123, 28, 181, 0.3);
  }
}

.session-info {
  flex: 1;
  min-width: 0;

  .session-title {
    font-size: 13px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .session-time {
    font-size: 11px;
    color: $text-muted;
    margin-top: 2px;
  }
}

.session-delete {
  opacity: 0;
  color: $text-muted;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    color: $danger-color;
  }
}

// 主聊天区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(123, 28, 181, 0.05);
  border: 1px solid $border-color;
  border-radius: $border-radius $border-radius 0 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;

  h3 {
    margin-top: 16px;
    font-size: 18px;
    color: $text-primary;
  }

  p {
    margin-top: 8px;
    font-size: 14px;
    color: $text-secondary;
    max-width: 400px;
  }
}

.quick-questions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 24px;
  max-width: 500px;
  width: 100%;
}

.quick-question-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: $border-radius-sm;
  background: rgba(123, 28, 181, 0.12);
  border: 1px solid rgba(123, 28, 181, 0.25);
  color: $text-secondary;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(123, 28, 181, 0.25);
    color: $text-primary;
    border-color: $primary-color;
    transform: translateY(-1px);
  }
}

// 消息样式
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  animation: slideInLeft 0.3s ease;

  &--user {
    flex-direction: row-reverse;

    .message-body {
      align-items: flex-end;
    }

    .message-content {
      background: linear-gradient(135deg, rgba(123,28,181,0.3), rgba(123,28,181,0.15));
      border: 1px solid rgba(123,28,181,0.3);
    }
  }

  &--assistant {
    .message-content {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
  }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.avatar--user {
    background: linear-gradient(135deg, $primary-color, $primary-light);
    color: white;
  }

  &.avatar--assistant {
    background: linear-gradient(135deg, $success-color, #1ba8b8);
    color: white;
  }
}

.message-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 70%;
}

.message-role {
  font-size: 12px;
  color: $text-muted;
  font-weight: 500;
}

.message-content {
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
  color: $text-primary;

  :deep(h3) {
    font-size: 16px;
    margin: 8px 0;
    color: $primary-light;
  }

  :deep(h4) {
    font-size: 14px;
    margin: 6px 0;
    color: $text-primary;
  }

  :deep(strong) {
    color: $accent-color;
  }

  :deep(blockquote) {
    border-left: 3px solid $primary-color;
    padding-left: 12px;
    margin: 8px 0;
    color: $text-secondary;
    font-style: italic;
  }

  :deep(ul) {
    padding-left: 20px;
    margin: 6px 0;
  }

  :deep(li) {
    margin: 4px 0;
  }
}

// 置信度标签
.confidence-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: $text-secondary;

  .confidence-progress {
    width: 28px !important;
    height: 28px !important;

    :deep(.el-progress__text) {
      font-size: 8px !important;
      color: $text-secondary;
    }
  }
}

// 知识来源
.sources-section {
  margin-top: 4px;
}

.sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  background: rgba(123, 28, 181, 0.1);
  border: 1px solid rgba(123, 28, 181, 0.2);
  font-size: 12px;
  color: $primary-light;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(123, 28, 181, 0.2);
  }
}

.toggle-arrow {
  transition: transform 0.2s ease;

  &.expanded {
    transform: rotate(90deg);
  }
}

.sources-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  padding: 10px 14px;
  border-radius: $border-radius-sm;
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid rgba(123, 28, 181, 0.15);
}

.source-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.source-type {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;

  &--standard {
    background: rgba(123, 28, 181, 0.2);
    color: $primary-light;
  }

  &--manual {
    background: rgba(38, 198, 218, 0.2);
    color: $success-color;
  }

  &--history {
    background: rgba(255, 140, 56, 0.2);
    color: $accent-color;
  }

  &--expert {
    background: rgba(255, 179, 0, 0.2);
    color: $warning-color;
  }
}

.source-relevance {
  font-size: 11px;
  color: $text-muted;
}

.source-title {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
}

.source-excerpt {
  font-size: 12px;
  color: $text-secondary;
  margin-top: 4px;
  line-height: 1.5;
}

// 加载动画
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  width: fit-content;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $primary-light;
    animation: typing 1.4s infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

// 输入区域
.input-area {
  background: rgba(26, 5, 51, 0.6);
  border: 1px solid $border-color;
  border-top: none;
  border-radius: 0 0 $border-radius $border-radius;
  padding: 12px 16px;
}

.input-quick-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  overflow-x: auto;
  padding-bottom: 4px;

  &::-webkit-scrollbar {
    height: 3px;
  }
}

.input-quick-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  color: $text-muted;
  background: rgba(123, 28, 181, 0.08);
  border: 1px solid rgba(123, 28, 181, 0.15);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: $primary-light;
    background: rgba(123, 28, 181, 0.15);
    border-color: $primary-color;
  }
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;

  .chat-input {
    flex: 1;

    :deep(.el-textarea__inner) {
      background: rgba(123, 28, 181, 0.08) !important;
      border: 1px solid $border-color !important;
      border-radius: $border-radius-sm !important;
      color: $text-primary !important;
      padding: 10px 14px;
      font-size: 14px;
      resize: none;
      box-shadow: none !important;

      &::placeholder {
        color: $text-muted;
      }
    }
  }

  .send-btn {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    background: $primary-color !important;
    border: none !important;

    &:hover {
      background: $primary-light !important;
    }

    &:disabled {
      opacity: 0.4;
    }
  }
}

// 过渡动画
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
