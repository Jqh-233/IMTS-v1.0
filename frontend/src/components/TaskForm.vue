<template>
  <a-modal
    :open="visible"
    :title="isEdit ? '编辑任务' : '创建任务'"
    :confirm-loading="props.loading"
    @ok="handleOk"
    @cancel="$emit('close')"
  >
    <a-form :model="form" layout="vertical">
      <a-form-item label="任务名称" required>
        <a-input v-model:value="form.task_name" placeholder="输入任务名称" :maxlength="200" />
      </a-form-item>

      <a-form-item label="截止日期" required>
        <a-date-picker
          v-model:value="form._deadline"
          style="width: 100%"
          placeholder="选择截止日期"
          :disabled-date="disabledDate"
        />
      </a-form-item>

      <a-form-item label="优先级">
        <a-radio-group v-model:value="form.priority">
          <a-radio-button value="high">高优先</a-radio-button>
          <a-radio-button value="medium">中优先</a-radio-button>
          <a-radio-button value="low">低优先</a-radio-button>
        </a-radio-group>
      </a-form-item>

      <a-form-item label="分类">
        <a-select v-model:value="form.category" style="width: 100%">
          <a-select-option value="会议通知">会议通知</a-select-option>
          <a-select-option value="客户跟进">客户跟进</a-select-option>
          <a-select-option value="科研协作">科研协作</a-select-option>
          <a-select-option value="报告提交">报告提交</a-select-option>
          <a-select-option value="通用任务">通用任务</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item v-if="isEdit" label="状态">
        <a-select v-model:value="form.status" style="width: 100%">
          <a-select-option value="pending">待办</a-select-option>
          <a-select-option value="processing">进行中</a-select-option>
          <a-select-option value="done">已完成</a-select-option>
        </a-select>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import dayjs from 'dayjs'
import type { Task, CreateTaskPayload } from '../stores/tasks'

const props = defineProps<{
  visible: boolean
  task: Task | null
  loading?: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [data: CreateTaskPayload]
}>()

const isEdit = !!props.task

const form = reactive({
  task_name: '',
  _deadline: undefined as dayjs.Dayjs | undefined,
  priority: 'medium' as CreateTaskPayload['priority'],
  category: '通用任务' as CreateTaskPayload['category'],
  status: 'pending' as CreateTaskPayload['status'],
})

watch(() => props.visible, (v) => {
  if (v && props.task) {
    form.task_name = props.task.task_name
    form._deadline = dayjs(props.task.deadline)
    form.priority = props.task.priority
    form.category = props.task.category
    form.status = props.task.status
  } else if (v) {
    form.task_name = ''
    form._deadline = undefined
    form.priority = 'medium'
    form.category = '通用任务'
    form.status = 'pending'
  }
})

function disabledDate(current: dayjs.Dayjs) {
  return current && current < dayjs().startOf('day')
}

function handleOk() {
  if (!form.task_name.trim() || !form._deadline) {
    return
  }
  emit('submit', {
    task_name: form.task_name.trim(),
    deadline: form._deadline.format('YYYY-MM-DD'),
    priority: form.priority,
    category: form.category,
    status: form.status,
  })
}
</script>
