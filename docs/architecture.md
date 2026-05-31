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
| 异步 | asyncio + aiosqlite | 邮件同步和 LLM 调用适合异步处理 |
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

当前使用 SQLite + SQLAlchemy ORM，远期可迁移 PostgreSQL：

- `emails` 表：原始邮件
- `tasks` 表：提取的任务

## 目录结构

```
IMTS-v1.0/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口 + 静态文件服务
│   │   ├── database.py    # SQLAlchemy 连接
│   │   ├── config.py      # 配置管理
│   │   ├── api/           # API 路由
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── ai/            # AI 引擎
│   │   ├── services/      # 业务逻辑
│   │   └── data/          # 数据层
│   └── requirements.txt
├── frontend/              # Vue 3 前端
│   └── src/
│       ├── components/    # 公共组件
│       ├── views/         # 页面
│       ├── api/           # API 请求封装
│       ├── stores/        # Pinia 状态
│       ├── router/        # 路由配置
│       ├── App.vue
│       └── main.ts
├── docs/                  # 项目文档
├── start-imts.bat         # Windows 一键启动
├── start-server.sh        # Linux 服务器启动
└── .env.example
```

## 开发原则

1. **增量迁移**：已从 Streamlit 完成迁移，当前为 FastAPI + Vue 3 架构
2. **API 先行**：每个功能先确定 API 契约，再实现前后端
3. **每次只改一个层次**：避免同时改前端和后端，降低风险
