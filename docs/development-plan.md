# IMTS 开发计划

## 原则

1. **增量、稳定**：每步只改一个模块，确保已有功能始终可用
2. **后端先行**：先出 API，再写前端；API 可用 curl/Swagger 验证
3. **每步提交**：一步一测，不攒代码

---

## 第零步：基础设施 ⏱ 预计 1-2 小时

### 0.1 初始化后端项目

- [x] 创建 `backend/` 目录
- [x] 编写 `backend/requirements.txt`（FastAPI、uvicorn、sqlalchemy、aiosqlite）
- [x] 搭建 FastAPI 最小骨架：`backend/app/main.py`（/health 端点）
- [x] 配置 CORS 中间件（允许前端开发服务器 localhost:5173）
- [x] 用 uvicorn 启动验证：`curl http://localhost:8501/health` 返回 200

**验证**：`curl localhost:8501/health` → `{"status": "ok"}`

### 0.2 初始化前端项目

- [x] 创建 Vite + Vue 3 + TypeScript 项目：`frontend/`
- [x] 安装 Ant Design Vue、Vue Router、Pinia、Axios
- [x] 配置 API 代理（/api → localhost:8501）
- [x] 搭建最小页面骨架：路由 + Layout 布局 + 空白首页
- [x] 启动验证：`npm run dev` → 浏览器看到 "IMTS" 标题

**验证**：浏览器访问 localhost:5173 看到 "IMTS" 标题和导航栏

### 0.3 验证环境

- [x] 确认后端 `backend/app/main.py` 可正常启动
- [x] 前后端并行开发：FastAPI（8501）+ Vue 3（5173）

**验证**：`curl localhost:8501/health` 返回 `{"status": "ok"}`

---

## 第一步：数据层迁移 ⏱ 预计 2-3 小时

### 1.1 SQLAlchemy 模型

- [x] 创建 `backend/app/models/`：Email、Task 两个模型
- [x] 映射现有 SQLite 表结构
- [x] 编写数据库连接和会话管理

**验证**：`python -c "from app.models import *; ..."` 无报错，能查询现有数据

### 1.2 Pydantic Schema

- [x] 创建 `backend/app/schemas/`：EmailOut、TaskOut、TaskCreate、TaskUpdate
- [x] 定义请求/响应数据格式
- [x] 定义枚举：Priority(high/medium/low)、Status(pending/processing/done)、Category

**验证**：OpenAPI 文档（/docs）自动生成正确的 schema

---

## 第二步：API 端点（按功能块拆分）⏱ 预计 3-4 小时

### 2.1 任务 API（核心）

- [x] `GET /api/tasks` — 列表（支持 ?search=&priority=&sort=）
- [x] `GET /api/tasks/{id}` — 详情
- [x] `POST /api/tasks` — 手动创建
- [x] `PUT /api/tasks/{id}` — 编辑
- [x] `DELETE /api/tasks/{id}` — 删除
- [x] `PATCH /api/tasks/{id}/status` — 状态流转
- [x] `GET /api/stats` — 统计数据（总数/高优先/活跃/完成）

**验证**：用 Swagger UI (/docs) 逐个测试每个端点

### 2.2 邮件 API

- [x] `GET /api/emails` — 邮件列表
- [x] `GET /api/emails/{id}` — 邮件详情（含正文）
- [x] `POST /api/sync/qq` — 同步 QQ 邮件
- [x] `POST /api/sync/demo` — 加载演示邮件
- [x] `POST /api/emails/{id}/extract` — 从单封邮件提取任务

**验证**：同步演示邮件 → 任务列表更新

### 2.3 配置 API

- [x] `GET /api/config` — 获取当前配置（脱敏）
- [x] `PUT /api/config/mail` — 更新邮箱配置
- [x] `PUT /api/config/llm` — 更新 LLM 配置

**验证**：修改配置 → 重启后配置保持

---

## 第三步：前端页面（按页面拆分）⏱ 预计 4-6 小时

### 3.1 全局布局与导航

- [x] 顶部导航栏：Logo + 设置图标 + 同步状态指示
- [x] 页面路由：/（看板）、/settings（设置）
- [x] 全局样式（Ant Design 主题：颜色、字体、间距）

**验证**：导航切换正常，页面布局符合设计规范

### 3.2 任务看板页面（核心）

- [x] 三栏布局：待办 | 进行中 | 已完成
- [x] 任务卡片组件（优先级色条、名称、日期、分类、操作按钮）
- [x] 搜索框 + 优先级筛选 + 排序下拉
- [x] 统计数据栏
- [x] 状态流转按钮（乐观更新）
- [x] 空状态展示
- [x] 低置信度预警样式

**验证**：同步演示邮件 → 看板正确显示 3 栏任务

### 3.3 任务详情

- [x] 编辑弹窗：修改名称、截止日、优先级、分类、状态
- [x] 删除确认对话框（Popconfirm）
- [x] 邮件溯源（卡片内显示来源邮件主题）

**验证**：编辑任务 → 保存 → 看板刷新正确

### 3.4 设置页面

- [x] 邮箱配置表单（Tabs 分组）
- [x] LLM 配置表单
- [x] 同步按钮（QQ / Demo）+ 结果提示
- [x] 配置脱敏展示

**验证**：修改配置 → 同步邮件 → 看板出现新任务

### 3.5 手动创建任务

- [x] 顶部工具栏 "+" 按钮 → 弹窗
- [x] 创建任务表单（名称、截止日、优先级、分类）
- [x] 不关联邮件，confidence=1.0，source=manual

**验证**：创建任务 → 看板出现 → 后续可编辑/删除

---

## 第四步：联调与清理 ⏱ 预计 1-2 小时

- [x] 全流程测试：配置 → 同步 → 看板 → 状态流转 → 编辑 → 删除
- [x] 错误处理：网络断开、API 超时、空数据
- [x] 更新启动脚本（同时启动前后端）
- [x] 更新 README
- [x] 更新 devlog

---

## 当前状态

| 步骤 | 状态 | 完成时间 |
|------|------|---------|
| 0.1 初始化后端 | ✅ 完成 | 2026-05-30 |
| 0.2 初始化前端 | ✅ 完成 | 2026-05-30 |
| 0.3 验证环境 | ✅ 完成 | 2026-05-30 |
| 1.1 SQLAlchemy 模型 | ✅ 完成 | 2026-05-30 |
| 1.2 Pydantic Schema | ✅ 完成 | 2026-05-30 |
| 2.1 任务 API | ✅ 完成 | 2026-05-30 |
| 2.2 邮件 API | ✅ 完成 | 2026-05-30 |
| 2.3 配置 API | ✅ 完成 | 2026-05-30 |
| 3.1 全局布局 | ✅ 完成 | 2026-05-30 |
| 3.2 任务看板 | ✅ 完成 | 2026-05-30 |
| 3.3 任务详情 | ✅ 完成 | 2026-05-30 |
| 3.4 设置页面 | ✅ 完成 | 2026-05-30 |
| 3.5 手动创建任务 | ✅ 完成 | 2026-05-30 |
| 4 联调清理 | ✅ 完成 | 2026-05-30 |
| 5.1-5.6 功能优化 | ✅ 完成 | 2026-05-31 |
| 6 AI 引擎优化 | 🔲 计划中 | — |

---

## 第五步：功能优化 ⏱ 预计 4-6 小时

（全部完成于 2026-05-31）

---

## 当前状态

| 步骤 | 状态 | 完成时间 |
|------|------|---------|
| 0-4 基础设施→联调 | ✅ 完成 | 2026-05-30 |
| 5.1-5.6 功能优化 | ✅ 完成 | 2026-05-31 |

---

## 第六步：AI 引擎优化（计划中）

详见 [docs/ai-optimization-requirements.md](ai-optimization-requirements.md)

### 6.1 规则先行调度

- [ ] `classify_email()`：三分法替换 `should_create_task()`（明确任务/明确非任务/不确定）
- [ ] `extract_task()`：规则先行 → LLM 监督者润色 / LLM 指挥官判断
- [ ] 弱非任务词删除，仅强非任务词触发跳过
- [ ] 监督者失败回退规则结果，不抛异常
- [ ] 同步循环错误记录（替换 `except: pass`）

### 6.2 LLM 双角色

- [ ] 指挥官 prompt：约束放宽，置信度 < 0.5 仍创建任务
- [ ] 监督者 prompt：只润色 task_name/deadline，2-3 字段
- [ ] `polish_with_llm_supervisor()`：合并规则结果与 LLM 润色

### 6.3 校验放宽

- [ ] 过期截止日期不拒绝，调整为今天 +3 天
- [ ] 低置信度不拒绝，改为标记 `low_confidence: True`

### 6.4 数据字段

- [ ] emails 表加 `skip_reason`
- [ ] tasks 表加 `decision_reason`
- [ ] `init_db()` 启动时自动迁移

### 6.5 前端改动

- [ ] TaskCard：置信度标签加 `confidence_source !== 'rules'` 条件
- [ ] TaskCard：低置信度展示 LLM 判断理由
- [ ] TaskCard：新增发件人显示
- [ ] EmailDrawer：展示具体 skip_reason
- [ ] 类型定义更新
