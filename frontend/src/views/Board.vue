<template>
  <div class="board">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <a-input-search
          v-model:value="store.search"
          placeholder="搜索任务名称..."
          style="width: 260px"
          @search="store.fetchTasks()"
          allow-clear
        />
        <a-select
          v-model:value="store.priorityFilter"
          placeholder="优先级筛选"
          style="width: 130px"
          allow-clear
          @change="store.fetchTasks()"
        >
          <a-select-option value="high">高优先</a-select-option>
          <a-select-option value="medium">中优先</a-select-option>
          <a-select-option value="low">低优先</a-select-option>
        </a-select>
      </div>
      <div class="toolbar-right">
        <a-space>
          <a-tag color="error">高优先 {{ stats.high_priority }}</a-tag>
          <a-tag color="processing">活跃 {{ stats.active }}</a-tag>
          <a-tag color="success">已完成 {{ stats.done }}</a-tag>
        </a-space>
        <a-button @click="openDrawer">邮件列表</a-button>
        <a-button type="primary" @click="showCreate = true">+ 新建任务</a-button>
      </div>
    </div>

    <!-- 三栏看板 -->
    <a-spin :spinning="store.loading" tip="加载中...">
      <div class="columns">
        <!-- 待办 -->
        <div class="column">
          <div class="column-header pending">
            <span>📋 待办</span>
            <a-badge :count="store.pendingTasks.length" :number-style="{ backgroundColor: '#1677ff' }" />
          </div>
          <div class="column-body">
            <TaskCard
              v-for="task in store.pendingTasks" :key="task.id"
              :task="task"
              @move="(s) => store.updateStatus(task.id, s)"
              @edit="openEdit(task)"
              @delete="store.deleteTask(task.id)"
              @view-email="(eid) => { highlightEmailId = eid; openDrawer() }"
            />
            <a-empty v-if="store.pendingTasks.length === 0 && !store.loading" description="暂无待办任务" />
          </div>
        </div>

        <!-- 进行中 -->
        <div class="column">
          <div class="column-header processing">
            <span>🔄 进行中</span>
            <a-badge :count="store.processingTasks.length" :number-style="{ backgroundColor: '#faad14' }" />
          </div>
          <div class="column-body">
            <TaskCard
              v-for="task in store.processingTasks" :key="task.id"
              :task="task"
              @move="(s) => store.updateStatus(task.id, s)"
              @edit="openEdit(task)"
              @delete="store.deleteTask(task.id)"
              @view-email="(eid) => { highlightEmailId = eid; openDrawer() }"
            />
            <a-empty v-if="store.processingTasks.length === 0 && !store.loading" description="暂无进行中任务" />
          </div>
        </div>

        <!-- 已完成 -->
        <div class="column">
          <div class="column-header done">
            <span>✅ 已完成</span>
            <a-badge :count="store.doneTasks.length" :number-style="{ backgroundColor: '#52c41a' }" />
          </div>
          <div class="column-body">
            <TaskCard
              v-for="task in store.doneTasks" :key="task.id"
              :task="task"
              @move="(s) => store.updateStatus(task.id, s)"
              @edit="openEdit(task)"
              @delete="store.deleteTask(task.id)"
              @view-email="(eid) => { highlightEmailId = eid; openDrawer() }"
            />
            <a-empty v-if="store.doneTasks.length === 0 && !store.loading" description="暂无已完成任务" />
          </div>
        </div>
      </div>
    </a-spin>

    <!-- 邮件抽屉 -->
    <EmailDrawer
      :visible="drawerVisible"
      :highlight-id="highlightEmailId"
      @close="drawerVisible = false; highlightEmailId = null"
    />

    <!-- 创建/编辑弹窗 -->
    <TaskForm
      :visible="showCreate || !!editingTask"
      :task="editingTask"
      @close="showCreate = false; editingTask = null"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTaskStore } from '../stores/tasks'
import type { Task } from '../stores/tasks'
import { useEmailStore } from '../stores/emails'
import TaskCard from '../components/TaskCard.vue'
import TaskForm from '../components/TaskForm.vue'
import EmailDrawer from '../components/EmailDrawer.vue'

const store = useTaskStore()
const emailStore = useEmailStore()
const showCreate = ref(false)
const editingTask = ref<Task | null>(null)
const drawerVisible = ref(false)
const highlightEmailId = ref<number | null>(null)

const stats = store.stats

function openEdit(task: Task) {
  editingTask.value = task
}

async function handleSubmit(data: Record<string, unknown>) {
  if (editingTask.value) {
    await store.updateTask(editingTask.value.id, data)
    editingTask.value = null
  } else {
    await store.createTask(data as any)
    showCreate.value = false
  }
}

function openDrawer() {
  drawerVisible.value = true
  emailStore.fetchEmails()
}

onMounted(() => {
  store.fetchTasks()
  store.fetchStats()
})
</script>

<style scoped>
.board {
  max-width: 1400px;
  margin: 0 auto;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
}
.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}
.columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.column {
  background: #fafafa;
  border-radius: 8px;
  min-height: 300px;
}
.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
  border-radius: 8px 8px 0 0;
}
.column-header.pending { background: #e6f4ff; }
.column-header.processing { background: #fffbe6; }
.column-header.done { background: #f6ffed; }
.column-body {
  padding: 12px;
}
</style>
