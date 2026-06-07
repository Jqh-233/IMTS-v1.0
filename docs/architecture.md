# IMTS 技术架构

## 架构概述

FastAPI + Vue 3 前后端分离架构：

```
┌──────────────────┐     HTTP/REST     ┌──────────────────┐
│  前端 (Vue 3)     │ ◄──────────────► │  后端 (FastAPI)   │
│  localhost:5173   │                  │  localhost:8501   │
└──────────────────┘                  └──────┬───────────┘
                                             │
                                    ┌────────▼───────────┐
                                    │   数据库 (SQLite)    │
                                    └────────────────────┘
```

生产模式（服务器部署）下，前端构建为静态文件由 FastAPI 直接托管，统一在 8501 端口。

## 技术选型

### 后端

| 项目 | 选择 | 原因 |
|------|------|------|
| 语言 | Python 3.10+ | 复用现有 AI 引擎和邮件服务代码 |
| 框架 | FastAPI | 高性能、自动 OpenAPI 文档、类型安全 |
| ORM | SQLAlchemy 2.0 | 成熟、支持 SQLite 和 PostgreSQL 切换 |
| 异步 | asyncio | 邮件同步和 LLM 调用适合异步处理（当前 SQLite 同步模式已满足需求） |
| 任务队列 | BackgroundTasks（内置） | 简单够用，远期可换 Celery |

### 前端

| 项目 | 选择 | 原因 |
|------|------|------|
| 框架 | **Vue 3** + Composition API | 中文文档一流、模板语法直观、学习曲线平缓 |
| 构建 | Vite | 快速开发服务器、Vue 官方推荐 |
| UI 库 | **Ant Design Vue 4** | 中文文档完善、组件开箱即用、国内最主流 |
| 状态管理 | Pinia | Vue 官方推荐，比 Vuex 更简洁 |
| 路由 | Vue Router 4 | 标准方案 |
| HTTP | Axios | 中文资料多、拦截器方便 |

### 为什么选 Vue 而不是 React

团队是大三学生，选型优先级：**能学会 > 能做出来 > 技术先进性**。

| 考量 | Vue 3 | React 18 |
|------|-------|----------|
| 中文文档 | 官方中文，尤雨溪是中国人 | 中文翻译，有时滞后 |
| 模板语法 | HTML 模板，和学网页一样 | JSX，需要理解 JavaScript 表达式 |
| 双向绑定 | `v-model` 一行搞定 | 需要手动写 onChange |
| 单文件组件 | `.vue` 文件 HTML/CSS/JS 在一起 | CSS-in-JS 或分离文件 |
| 入门时间 | 1-2 周能写页面 | 2-3 周 |

## API 设计

- RESTful 风格
- JSON 请求/响应
- 统一错误格式：`{ "detail": "错误描述" }`
- 自动生成 OpenAPI 文档（FastAPI 内置，访问 `/docs`）

## 核心 API 端点

```
POST   /api/sync/qq           # 同步 QQ 邮件
POST   /api/sync/demo         # 加载演示邮件
GET    /api/emails            # 获取邮件列表
GET    /api/emails/{id}       # 获取邮件详情
GET    /api/tasks             # 获取任务列表（支持筛选/排序）
POST   /api/tasks             # 手动创建任务
PUT    /api/tasks/{id}        # 更新任务
DELETE /api/tasks/{id}        # 删除任务
PATCH  /api/tasks/{id}/status # 更新任务状态
POST   /api/tasks/{id}/extract # 从邮件提取任务
GET    /api/config            # 获取配置
PUT    /api/config            # 更新配置
GET    /api/stats             # 获取统计数据
```

## 数据库

统一使用 SQLite + SQLAlchemy ORM（已消除早期的 raw sqlite3 双轨制），远期可迁移 PostgreSQL：

- `emails` 表：原始邮件
- `tasks` 表：提取的任务（外键关联 emails）
- 建表：`Base.metadata.create_all()` 在 lifespan 启动事件中自动执行

## 目录结构

```
IMTS-v1.0/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口 + lifespan 建表 + SPA 托管
│   │   ├── database.py    # SQLAlchemy 引擎与会话（DB 统一入口）
│   │   ├── config.py      # 配置管理（.env 读写）
│   │   ├── logging_config.py # 日志系统
│   │   ├── api/           # API 路由（tasks / emails / config）
│   │   ├── models/        # SQLAlchemy 模型（Email, Task）
│   │   ├── schemas/       # Pydantic 校验（枚举、请求/响应体）
│   │   ├── ai/            # AI 引擎（提取入口、LLM 客户端、Prompt、校验）
│   │   ├── services/      # 邮件同步服务（IMAP + MIME + 演示邮件）
│   │   ├── data/          # 测试邮件数据集
│   │   └── tests/         # pytest 自动化测试
│   └── requirements.txt
├── frontend/              # Vue 3 前端
│   └── src/
│       ├── components/    # TaskCard / TaskForm / EmailDrawer
│       ├── views/         # Board / Settings
│       ├── api/           # Axios 请求封装
│       ├── stores/        # Pinia 状态（tasks / emails）
│       ├── router/        # 路由配置
│       ├── App.vue
│       └── main.ts
├── docs/                  # 项目文档
├── start-imts.bat         # Windows 一键启动
├── start-server.sh        # Linux 服务器启动
└── .env.example
```

## AI 引擎架构

提取模式由 `LLM_MODE` 配置控制：`rules`（纯规则）、`llm`（纯 LLM）、`hybrid`（混合）。

### 计划架构（规则先行分层调度）

```
邮件 → classify_email() 三分法
         │
         ├─ 明确是任务（行动词+时间词+请求词全中）
         │    → 规则提取基础字段 → LLM"监督者"润色 task_name/deadline
         │
         ├─ 明确不是任务（强非任务词命中）
         │    → 直接跳过，不调 LLM
         │
         └─ 拿不准（其余所有情况）
              → LLM"指挥官"全权判断 → 规则兜底（宁可误报）
```

### 当前架构（LLM 优先）

```
邮件 → LLM 提取（含判断+6字段）→ 失败 → 规则兜底
```

## 开发原则

1. **增量迁移**：已从 Streamlit 完成迁移，当前为 FastAPI + Vue 3 架构
2. **API 先行**：每个功能先确定 API 契约，再实现前后端
3. **每次只改一个层次**：避免同时改前端和后端，降低风险
4. **每步验证**：改完一个模块立即验证，不积压到最后
