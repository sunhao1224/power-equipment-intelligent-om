import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppShell from '@/components/ui/AppShell.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppShell,
    redirect: '/overview',
    children: [
      { path: 'overview', name: 'Overview', component: () => import('@/views/overview/OverviewView.vue'), meta: { title: '总览工作台' } },
      { path: 'diagnosis', name: 'Diagnosis', component: () => import('@/views/diagnosis/HermesDiagnosisView.vue'), meta: { title: 'Hermes 诊断中心' } },
      { path: 'knowledge', name: 'Knowledge', component: () => import('@/views/knowledge/KnowledgeEvidenceView.vue'), meta: { title: '知识与证据图谱' } },
      { path: 'batch', name: 'Batch', component: () => import('@/views/batch/BatchRiskView.vue'), meta: { title: '批次风险评估' } },
      { path: 'reports', name: 'Reports', component: () => import('@/views/reports/ReportsView.vue'), meta: { title: '决策报告中心' } }
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
