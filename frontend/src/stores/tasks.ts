import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'

export interface Task {
  id: number
  email_id: number | null
  task_name: string
  deadline: string
  priority: 'high' | 'medium' | 'low'
  status: 'pending' | 'processing' | 'done'
  category: string
  confidence: number
  confidence_source: string
  created_at: string
  email_subject?: string | null
  email_sender?: string | null
}

export interface Stats {
  total: number
  high_priority: number
  active: number
  done: number
}

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const stats = ref<Stats>({ total: 0, high_priority: 0, active: 0, done: 0 })
  const loading = ref(false)
  const search = ref('')
  const priorityFilter = ref('')

  const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending'))
  const processingTasks = computed(() => tasks.value.filter(t => t.status === 'processing'))
  const doneTasks = computed(() => tasks.value.filter(t => t.status === 'done'))

  async function fetchTasks() {
    loading.value = true
    try {
      const params: Record<string, string> = {}
      if (search.value) params.search = search.value
      if (priorityFilter.value) params.priority = priorityFilter.value
      const res = await api.get('/tasks', { params })
      tasks.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    const res = await api.get('/tasks/stats')
    stats.value = res.data
  }

  async function createTask(data: {
    task_name: string
    deadline: string
    priority: string
    category: string
    status: string
  }) {
    const res = await api.post('/tasks', data)
    tasks.value.unshift(res.data)
    await fetchStats()
    return res.data
  }

  async function updateTask(id: number, data: Record<string, unknown>) {
    const res = await api.put(`/tasks/${id}`, data)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx >= 0) tasks.value[idx] = res.data
    return res.data
  }

  async function updateStatus(id: number, status: string) {
    // 乐观更新
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx >= 0) tasks.value[idx].status = status as Task['status']

    try {
      const res = await api.patch(`/tasks/${id}/status`, { status })
      if (idx >= 0) tasks.value[idx] = res.data
      await fetchStats()
    } catch {
      // 回滚
      await fetchTasks()
      await fetchStats()
    }
  }

  async function deleteTask(id: number) {
    await api.delete(`/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
    await fetchStats()
  }

  return {
    tasks, stats, loading, search, priorityFilter,
    pendingTasks, processingTasks, doneTasks,
    fetchTasks, fetchStats, createTask, updateTask, updateStatus, deleteTask,
  }
})
