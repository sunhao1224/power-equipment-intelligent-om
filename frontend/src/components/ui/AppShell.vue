<template>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand-mark">H</div>
      <nav class="nav-stack">
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path" class="nav-dot" :title="item.label">
          <component :is="item.icon" />
        </RouterLink>
      </nav>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <div class="eyebrow">Hermes Agent Cloud Console</div>
          <h1>{{ route.meta.title }}</h1>
        </div>
        <div class="topbar-meta">
          <span class="status-pill"></span>
          <span>featrue/hermes</span>
          <span>Mock Runtime</span>
        </div>
      </header>
      <RouterView />
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { DataLine, Cpu, Share, Tickets, DocumentChecked } from '@element-plus/icons-vue'

const route = useRoute()
const navItems = [
  { path: '/overview', label: '总览工作台', icon: DataLine },
  { path: '/diagnosis', label: 'Hermes 诊断中心', icon: Cpu },
  { path: '/knowledge', label: '知识与证据图谱', icon: Share },
  { path: '/batch', label: '批次风险评估', icon: Tickets },
  { path: '/reports', label: '决策报告中心', icon: DocumentChecked }
]
</script>
