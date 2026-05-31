<template>
  <div class="settings">
    <a-card title="设置" :bordered="false" style="max-width: 640px; margin: 0 auto;">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 邮箱配置 -->
        <a-tab-pane key="mail" tab="邮箱配置">
          <a-form :model="mail" layout="vertical" @finish="saveMail">
            <a-form-item label="QQ 邮箱地址" required>
              <a-input v-model:value="mail.email" placeholder="example@qq.com" />
            </a-form-item>
            <a-form-item label="授权码">
              <a-input-password v-model:value="mail.auth_code" placeholder="QQ 邮箱 IMAP 授权码" />
            </a-form-item>
            <a-form-item label="同步天数">
              <a-input-number v-model:value="mail.lookback_days" :min="1" :max="90" style="width: 100%" />
            </a-form-item>
            <a-form-item label="每次最大获取">
              <a-input-number v-model:value="mail.max_fetch" :min="1" :max="50" style="width: 100%" />
            </a-form-item>
            <a-form-item>
              <a-space>
                <a-button type="primary" html-type="submit" :loading="mailSaving">保存</a-button>
                <a-button @click="syncQQ" :loading="syncing === 'qq'">同步 QQ 邮件</a-button>
              </a-space>
            </a-form-item>
          </a-form>
          <a-divider />
          <div class="sync-result" v-if="syncResult">
            <a-alert
              :type="syncResult.includes('失败') ? 'error' : 'success'"
              :message="syncResult"
              closable
              @close="syncResult = ''"
            />
          </div>
        </a-tab-pane>

        <!-- LLM 配置 -->
        <a-tab-pane key="llm" tab="LLM 配置">
          <a-alert
            message="接口兼容 OpenAI 格式，支持 DeepSeek / Qwen / GLM 等"
            type="info"
            show-icon
            style="margin-bottom: 16px;"
          />
          <a-form :model="llm" layout="vertical" @finish="saveLLM">
            <a-form-item label="API 地址" required>
              <a-input v-model:value="llm.api_base" placeholder="https://api.deepseek.com" />
            </a-form-item>
            <a-form-item label="API Key" required>
              <a-input-password v-model:value="llm.api_key" placeholder="sk-..." />
            </a-form-item>
            <a-form-item label="模型名称" required>
              <a-input v-model:value="llm.model" placeholder="deepseek-v4-flash" />
            </a-form-item>
            <a-form-item label="超时（秒）">
              <a-input-number v-model:value="llm.timeout" :min="5" :max="120" style="width: 160px" />
            </a-form-item>
            <a-form-item label="提取模式">
              <a-radio-group v-model:value="llm.mode">
                <a-radio-button value="hybrid">混合（推荐）</a-radio-button>
                <a-radio-button value="llm">纯 LLM</a-radio-button>
                <a-radio-button value="rules">纯规则</a-radio-button>
              </a-radio-group>
            </a-form-item>
            <a-form-item label="允许发送邮件内容给 LLM">
              <a-switch v-model:checked="llm.allow_email_content" />
              <span style="margin-left: 8px; color: #999; font-size: 12px;">
                关闭后仅用规则提取，不调用外部模型
              </span>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="llmSaving">保存</a-button>
            </a-form-item>
          </a-form>
        </a-tab-pane>

        <!-- 数据管理 -->
        <a-tab-pane key="data" tab="数据管理">
          <a-popconfirm
            title="确定清空所有邮件和任务？此操作不可恢复。"
            ok-text="确定清空"
            cancel-text="取消"
            ok-type="danger"
            @confirm="clearAll"
          >
            <a-button danger :loading="clearing">清空所有数据</a-button>
          </a-popconfirm>
          <p style="margin-top: 12px; color: #999; font-size: 13px;">
            清空后可通过"加载演示邮件"重新导入测试数据，或通过"同步 QQ 邮件"导入真实邮件。
          </p>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import api from '../api'
import { message } from 'ant-design-vue'

const activeTab = ref('mail')
const mailSaving = ref(false)
const llmSaving = ref(false)
const syncing = ref('')
const syncResult = ref('')
const clearing = ref(false)

const mail = reactive({
  email: '',
  auth_code: '',
  lookback_days: 7,
  max_fetch: 10,
  initial_sync: 'demo',
})

const llm = reactive({
  mode: 'hybrid',
  api_base: '',
  api_key: '',
  model: '',
  timeout: 10,
  allow_email_content: true,
})

onMounted(async () => {
  try {
    const res = await api.get('/config')
    const data = res.data
    mail.email = data.mail.email
    mail.lookback_days = data.mail.lookback_days
    mail.max_fetch = data.mail.max_fetch
    mail.initial_sync = data.mail.initial_sync

    llm.mode = data.llm.mode || 'hybrid'
    llm.api_base = data.llm.api_base || ''
    llm.model = data.llm.model || ''
    llm.timeout = data.llm.timeout || 10
    llm.allow_email_content = data.llm.allow_email_content ?? true
  } catch {
    message.error('加载配置失败')
  }
})

async function saveMail() {
  mailSaving.value = true
  try {
    await api.put('/config/mail', {
      email: mail.email,
      auth_code: mail.auth_code,
      lookback_days: mail.lookback_days,
      max_fetch: mail.max_fetch,
      initial_sync: mail.initial_sync,
    })
    message.success('邮箱配置已保存')
  } catch {
    message.error('保存失败')
  } finally {
    mailSaving.value = false
  }
}

async function saveLLM() {
  llmSaving.value = true
  try {
    await api.put('/config/llm', {
      mode: llm.mode,
      api_base: llm.api_base,
      api_key: llm.api_key,
      model: llm.model,
      timeout: llm.timeout,
      allow_email_content: llm.allow_email_content,
    })
    message.success('配置已保存，正在测试连接...')

    // 测试连接
    try {
      const testRes = await api.post('/config/llm/test')
      if (testRes.data.ok) {
        message.success(`${testRes.data.model} 接入成功`)
      }
    } catch (e: any) {
      message.warning(`配置已保存，但连接测试失败：${e.response?.data?.detail || e.message}`)
    }
  } catch {
    message.error('保存失败')
  } finally {
    llmSaving.value = false
  }
}

async function syncQQ() {
  syncing.value = 'qq'
  syncResult.value = ''
  try {
    const res = await api.post('/sync/qq')
    syncResult.value = `同步完成：${res.data.synced_emails} 封邮件，提取 ${res.data.extracted_tasks} 个任务`
    message.success(syncResult.value)
  } catch (e: any) {
    syncResult.value = `同步失败：${e.response?.data?.detail || e.message}`
    message.error(syncResult.value)
  } finally {
    syncing.value = ''
  }
}

async function clearAll() {
  clearing.value = true
  try {
    await api.delete('/data')
    message.success('所有数据已清空')
    syncResult.value = ''
  } catch (e: any) {
    message.error(e.response?.data?.detail || '清空失败')
  } finally {
    clearing.value = false
  }
}
</script>

<style scoped>
.settings {
  padding-top: 8px;
}
</style>
