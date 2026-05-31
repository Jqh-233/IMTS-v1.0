<template>
  <a-card
    :class="['task-card', { 'low-confidence': task.confidence < 0.7 }]"
    :hoverable="true"
    size="small"
  >
    <template #title>
      <div class="card-title">
        <span class="task-name">{{ task.task_name }}</span>
      </div>
    </template>

    <!-- 标签行 -->
    <div class="tags">
      <a-tag :color="priorityColor">{{ priorityLabel }}</a-tag>
      <a-tag v-if="task.confidence < 0.7" color="warning">低置信度 {{ (task.confidence * 100).toFixed(0) }}%</a-tag>
      <a-tag :color="isOverdue ? 'error' : ''">
        {{ task.deadline }}
      </a-tag>
    </div>

    <div class="meta">
      <span class="category">📂 {{ task.category }}</span>
    </div>

    <!-- 邮件溯源 -->
    <div v-if="task.email_id" class="email-source" @click="$emit('viewEmail', task.email_id)">
      查看原始邮件
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <template v-if="task.status === 'pending'">
        <a-button size="small" type="primary" @click="$emit('move', 'processing')">
          开始处理
        </a-button>
      </template>
      <template v-else-if="task.status === 'processing'">
        <a-button size="small" @click="$emit('move', 'pending')">退回待办</a-button>
        <a-button size="small" type="primary" @click="$emit('move', 'done')">
          标记完成
        </a-button>
      </template>
      <template v-else>
        <a-button size="small" @click="$emit('move', 'pending')">重新打开</a-button>
      </template>
      <a-button size="small" @click="$emit('edit')">编辑</a-button>
      <a-popconfirm
        title="确定删除此任务？"
        ok-text="删除"
        cancel-text="取消"
        @confirm="$emit('delete')"
      >
        <a-button size="small" danger>删除</a-button>
      </a-popconfirm>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../stores/tasks'

const props = defineProps<{ task: Task }>()
defineEmits<{
  move: [status: string]
  edit: []
  delete: []
  viewEmail: [emailId: number]
}>()

const priorityColor = computed(() =>
  props.task.priority === 'high' ? 'error' : props.task.priority === 'medium' ? 'warning' : 'processing'
)

const priorityLabel = computed(() =>
  props.task.priority === 'high' ? '高优先' : props.task.priority === 'medium' ? '中优先' : '低优先'
)

const isOverdue = computed(() => {
  const d = new Date(props.task.deadline)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return d < today
})
</script>

<style scoped>
.task-card {
  margin-bottom: 12px;
  border-radius: 8px;
}
.task-card.low-confidence {
  border-left: 3px solid #faad14;
}
.card-title {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.task-name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}
.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}
.email-source {
  font-size: 12px;
  color: #1677ff;
  margin-bottom: 8px;
  cursor: pointer;
}
.email-source:hover {
  text-decoration: underline;
}
.actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
</style>
