import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'

export interface EmailItem {
  id: number
  message_id: string | null
  subject: string
  sender: string
  received_at: string
  is_processed: boolean
  task_id: number | null
  task_name: string | null
  task_status: string | null
}

export const useEmailStore = defineStore('emails', () => {
  const emails = ref<EmailItem[]>([])
  const loading = ref(false)

  async function fetchEmails() {
    loading.value = true
    try {
      const res = await api.get('/emails')
      emails.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function extractTask(emailId: number) {
    const res = await api.post(`/emails/${emailId}/extract`)
    const idx = emails.value.findIndex(e => e.id === emailId)
    if (idx >= 0) {
      const data = res.data
      emails.value[idx] = { ...emails.value[idx], is_processed: true }
      if (data.extracted) {
        emails.value[idx] = {
          ...emails.value[idx],
          task_id: data.task.id,
          task_name: data.task.task_name,
          task_status: 'pending',
        }
      }
    }
    return res.data
  }

  async function forceTask(emailId: number) {
    const res = await api.post(`/emails/${emailId}/force-task`)
    if (res.data.created) {
      emails.value = emails.value.map(e =>
        e.id === emailId
          ? { ...e, is_processed: true, task_id: res.data.task.id, task_name: res.data.task.task_name }
          : e
      )
    }
    return res.data
  }

  function getEmailById(id: number) {
    return emails.value.find(e => e.id === id) || null
  }

  return { emails, loading, fetchEmails, extractTask, forceTask, getEmailById }
})
