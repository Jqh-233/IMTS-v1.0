<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header class="header">
      <div class="header-left">
        <span class="logo">IMTS</span>
        <span class="subtitle">智能邮件任务协同系统</span>
      </div>
      <div class="header-right">
        <a-menu
          v-model:selectedKeys="currentRoute"
          mode="horizontal"
          :style="{ border: 'none', background: 'transparent' }"
        >
          <a-menu-item key="/">
            <router-link to="/">任务看板</router-link>
          </a-menu-item>
          <a-menu-item key="/settings">
            <router-link to="/settings">设置</router-link>
          </a-menu-item>
        </a-menu>
      </div>
    </a-layout-header>
    <a-layout-content class="content">
      <router-view />
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => [route.path])
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
  height: 56px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-right {
  display: flex;
  align-items: center;
}
.logo {
  font-size: 18px;
  font-weight: 700;
  color: #1677ff;
}
.subtitle {
  font-size: 13px;
  color: #999;
}
.content {
  padding: 24px;
  background: #f5f5f5;
}
</style>
