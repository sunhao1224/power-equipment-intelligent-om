import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '可视化大屏', icon: 'DataAnalysis' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/chat/ChatView.vue'),
        meta: { title: '运维问答', icon: 'ChatDotRound' }
      },
      {
        path: 'diagnosis',
        name: 'Diagnosis',
        component: () => import('@/views/diagnosis/DiagnosisView.vue'),
        meta: { title: '故障诊断', icon: 'FirstAidKit' }
      },
      {
        path: 'maintenance',
        name: 'Maintenance',
        component: () => import('@/views/maintenance/MaintenanceView.vue'),
        meta: { title: '维护决策', icon: 'SetUp' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
