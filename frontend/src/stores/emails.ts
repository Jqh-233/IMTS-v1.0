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
      emails.value[idx].is_processed = true
      if (data.extracted) {
        emails.value[idx].task_id = data.task.id
        emails.value[idx].task_name = data.task.task_name
        emails.value[idx].task_status = 'pending'
      }
    }
    return res.data
  }

  function getEmailById(id: number) {
    return emails.value.find(e => e.id === id) || null
  }

  return { emails, loading, fetchEmails, extractTask, getEmailById }
})
