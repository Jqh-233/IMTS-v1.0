<template>
  <a-drawer
    :open="visible"
    title="邮件列表"
    placement="right"
    :width="480"
    @close="$emit('close')"
  >
    <a-spin :spinning="store.loading">
      <div v-if="store.emails.length === 0" style="text-align: center; padding: 40px 0;">
        <a-empty description="暂无邮件，请先同步" />
      </div>

      <div
        v-for="email in store.emails"
        :key="email.id"
        :class="['email-item', { active: highlightId === email.id }]"
        :ref="(el) => { if (highlightId === email.id && el) scrollToEmail(el as HTMLElement) }"
      >
        <!-- 摘要行（始终可见） -->
        <div class="email-summary" @click="toggleExpand(email.id)">
          <div class="email-header">
            <span class="email-sender">{{ email.sender }}</span>
            <span class="email-time">{{ formatTime(email.received_at) }}</span>
          </div>
          <div class="email-subject">{{ email.subject }}</div>
          <div class="email-status">
            <a-tag v-if="email.task_id" color="success">已提取：{{ email.task_name }}</a-tag>
            <a-tag v-else-if="email.is_processed" color="default">已跳过</a-tag>
            <a-tag v-else color="processing">待处理</a-tag>
            <span class="expand-hint">{{ expandedId === email.id ? '收起' : '展开详情' }}</span>
          </div>
        </div>

        <!-- 展开详情 -->
        <div v-if="expandedId === email.id" class="email-detail">
          <a-spin :spinning="loadingDetailId === email.id" v-if="!emailBody">
            <div style="height: 60px;" />
          </a-spin>

          <template v-else>
            <a-descriptions :column="1" size="small" style="margin-bottom: 12px;">
              <a-descriptions-item label="发件人">{{ email.sender }}</a-descriptions-item>
              <a-descriptions-item label="主题">{{ email.subject }}</a-descriptions-item>
              <a-descriptions-item label="时间">{{ email.received_at }}</a-descriptions-item>
            </a-descriptions>
            <div class="email-body">{{ emailBody || '(空)' }}</div>

            <!-- 操作 -->
            <div class="detail-actions">
              <template v-if="!email.is_processed">
                <a-button size="small" type="primary" :loading="extractingId === email.id" @click="handleExtract(email.id)">
                  提取任务
                </a-button>
              </template>
              <template v-else-if="!email.task_id">
                <a-button size="small" type="primary" :loading="forcingId === email.id" @click="handleForceTask(email.id)">
                  手动加入任务
                </a-button>
              </template>
              <template v-else>
                <a-button size="small" @click="$emit('close')">
                  查看关联任务（ID: {{ email.task_id }}）
                </a-button>
              </template>
            </div>
          </template>
        </div>
      </div>
    </a-spin>
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useEmailStore } from '../stores/emails'
import { useTaskStore } from '../stores/tasks'
import { message } from 'ant-design-vue'
import api from '../api'

const props = defineProps<{
  visible: boolean
  highlightId?: number | null
}>()

defineEmits<{
  close: []
}>()

const store = useEmailStore()
const taskStore = useTaskStore()
const extractingId = ref<number | null>(null)
const forcingId = ref<number | null>(null)
const expandedId = ref<number | null>(null)
const loadingDetailId = ref<number | null>(null)
const emailBody = ref('')

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function toggleExpand(emailId: number) {
  if (expandedId.value === emailId) {
    expandedId.value = null
    emailBody.value = ''
    return
  }
  expandedId.value = emailId
  loadingDetailId.value = emailId
  emailBody.value = ''
  try {
    const res = await api.get(`/emails/${emailId}`)
    emailBody.value = res.data.body || ''
  } catch {
    emailBody.value = '(加载失败)'
  } finally {
    loadingDetailId.value = null
  }
}

async function handleExtract(emailId: number) {
  extractingId.value = emailId
  try {
    const result = await store.extractTask(emailId)
    if (result.extracted) {
      message.success('任务已提取')
      await taskStore.fetchTasks()
      await taskStore.fetchStats()
    } else {
      message.info(result.skip_reason || '不包含任务')
    }
  } catch (e: any) {
    message.error(e.response?.data?.detail || '提取失败')
  } finally {
    extractingId.value = null
  }
}

async function handleForceTask(emailId: number) {
  forcingId.value = emailId
  try {
    const result = await store.forceTask(emailId)
    if (result.created) {
      message.success('任务已手动加入看板')
      await taskStore.fetchTasks()
      await taskStore.fetchStats()
    } else {
      message.info(result.message || '该邮件已有任务')
    }
  } catch (e: any) {
    message.error(e.response?.data?.detail || '操作失败')
  } finally {
    forcingId.value = null
  }
}

function scrollToEmail(el: HTMLElement) {
  nextTick(() => el.scrollIntoView({ behavior: 'smooth', block: 'center' }))
}
</script>

<style scoped>
.email-item {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.email-item.active .email-summary {
  background: #e6f4ff;
}
.email-summary {
  padding: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}
.email-summary:hover {
  background: #fafafa;
}
.email-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.email-sender {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}
.email-time {
  font-size: 12px;
  color: #999;
}
.email-subject {
  font-size: 13px;
  color: #555;
  margin-bottom: 6px;
}
.email-status {
  display: flex;
  align-items: center;
  gap: 8px;
}
.expand-hint {
  font-size: 12px;
  color: #1677ff;
}
.email-detail {
  padding: 0 12px 16px;
}
.email-body {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.7;
  color: #333;
  background: #fafafa;
  padding: 12px;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 12px;
}
.detail-actions {
  display: flex;
  gap: 8px;
}
</style>
