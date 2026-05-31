# IMTS 设计规范

## 设计理念

**清新简洁，信息优先。** 基于 Ant Design 5，通过主题定制消除"企业风"，让界面清爽现代。

## 技术基础

基于 Ant Design Vue 4，用 `ConfigProvider` 全局定制主题：

```vue
<!-- App.vue -->
<template>
  <a-config-provider :theme="theme">
    <router-view />
  </a-config-provider>
</template>

<script setup>
const theme = {
  token: {
    colorPrimary: '#1677ff',
    borderRadius: 8,
  },
};
</script>
```

## 色彩系统（Ant Design Token 覆盖）

| Token | 值 | 用途 |
|-------|-----|------|
| `colorPrimary` | `#1677FF` | 品牌主色 |
| `colorSuccess` | `#52C41A` | 成功/已完成 |
| `colorWarning` | `#FAAD14` | 警告/低置信度 |
| `colorError` | `#FF4D4F` | 危险/逾期/高优 |
| `colorBgLayout` | `#F5F5F5` | 页面背景 |
| `colorBgContainer` | `#FFFFFF` | 卡片/容器背景 |

### 优先级标签配色（使用 Ant Design Tag 组件）

| 优先级 | Tag color | 效果 |
|--------|-----------|------|
| High | `error`（红色） | 红底白字标签 |
| Medium | `warning`（橙色） | 橙底白字标签 |
| Low | `processing`（蓝色） | 蓝底白字标签 |

## 字体

Ant Design 默认字体已包含中英文字体栈，无需额外配置。

## 布局

### 整体结构（使用 Ant Design Layout 组件）

```
┌──────────────────────────────────────────────────┐
│  Header：Logo + 同步状态 Badge + 设置齿轮图标       │
├────────┬─────────────────────────────────────────┤
│ Sider  │  Content：三栏看板                        │
│ 统计卡片 │  待办  │  进行中  │  已完成               │
│ 搜索框   │  卡片  │  卡片   │  卡片                 │
│ 筛选器   │  卡片  │         │                       │
│ 排序     │        │         │                       │
└────────┴─────────────────────────────────────────┘
```

- Sider 可收起（`collapsible`），默认展开
- 适合桌面端使用（≥1280px），暂不考虑移动端

## 组件选型（全部使用 Ant Design 内置）

| 功能 | Ant Design 组件 |
|------|----------------|
| 全局布局 | `Layout` + `Menu` |
| 任务卡片 | `Card`（带 `hoverable`） |
| 三栏看板 | `Row` + `Col`，每栏一个 `Card` 容器 |
| 搜索框 | `Input.Search` |
| 筛选下拉 | `Select` |
| 优先级标签 | `Tag` |
| 状态流转按钮 | `Button.Group` 或三个小 `Button` |
| 任务编辑弹窗 | `Modal` + `Form` |
| 配置表单 | `Form` + `Input` + `InputNumber` + `Switch` |
| 同步进度 | `Progress` 或 `Steps` |
| 空状态 | `Empty` |
| 确认删除 | `Popconfirm` |
| 消息提示 | `message.success()` / `message.error()` |
| 加载状态 | `Spin` 或 `Skeleton` |
| 日期选择 | `DatePicker` |
| 设置页 | `Tabs` 分组邮箱/LLM 配置 |

## 任务卡片样式

```
┌ Card ──────────────────────────┐
│ [Tag: High/Medium/Low]          │
│ 任务名称（Card title，16px 加粗） │
│ ─────────────────────────────── │
│ 截止：2026-06-05  📂 客户跟进     │
│ ─────────────────────────────── │
│ 来源：xxx 邮件主题（灰色 12px）    │
│ [待办] [进行中] [已完成]          │
│ [编辑] [删除]                    │
└────────────────────────────────┘
```

特殊状态：
- **低置信度**（LLM 任务置信度 <0.70）：Card 左侧红色边框 + 顶部 Warning Tag
- **逾期**：截止日期文字变红
- **今日截止**：截止日期文字变橙

## 交互规范

- **数据加载中**：使用 `Spin` 包裹内容区
- **操作处理中**：按钮 `loading` 属性
- **操作成功/失败**：`message.success()` / `message.error()`
- **空状态**：`Empty` 组件 + 引导文字
- **搜索防抖**：`Input.Search` 自带防抖
- **乐观更新**：状态流转时先更新 UI，再发请求，失败时回滚

## 推荐学习路径（大三团队）

1. **Vue 3 基础**：官方中文教程（cn.vuejs.org）- 1 周
   - 重点看：模板语法、响应式数据（`ref`/`reactive`）、`v-model`、`v-if`/`v-for`、组件通信
2. **TypeScript 基础**：TypeScript 中文手册 - 3 天
   - 够用就行：类型注解、interface、泛型基础
3. **Ant Design Vue 入门**：antdv.com 挨个看组件示例 - 1 周
   - 重点看：Card、Table、Form、Modal、Tag、Button、Layout
4. **实战**：照着本项目开发计划逐步实现

全部中文资料，全部免费。
