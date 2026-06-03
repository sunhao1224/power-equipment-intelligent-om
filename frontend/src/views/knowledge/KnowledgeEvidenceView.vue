<template>
  <main class="page-grid">
    <section class="panel span-2">
      <div class="section-head">
        <h3>Evidence Pack</h3>
        <input v-model="query" class="search-input" placeholder="搜索规程、案例、图谱节点" @keyup.enter="store.loadEvidence(query)" />
      </div>
      <div class="evidence-list">
        <article v-for="item in store.evidence" :key="item.evidence_id" class="evidence-card">
          <div>
            <span class="source-chip">{{ item.source_type }}</span>
            <strong>{{ item.title }}</strong>
          </div>
          <p>{{ item.content }}</p>
          <footer>
            <span>{{ item.source_id }}</span>
            <span>{{ Math.round(item.confidence * 100) }}%</span>
          </footer>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="section-head">
        <h3>知识子图</h3>
        <span>{{ store.graph.nodes.length }} nodes</span>
      </div>
      <div class="graph-cloud">
        <span v-for="node in store.graph.nodes" :key="node">{{ node }}</span>
      </div>
      <div class="edge-list">
        <div v-for="edge in store.graph.edges" :key="edge.join('-')">{{ edge[0] }} -> {{ edge[1] }}</div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useHermesStore } from '@/stores/hermes'

const store = useHermesStore()
const query = ref('')

onMounted(async () => {
  if (!store.evidence.length) await store.bootstrap()
})
</script>
