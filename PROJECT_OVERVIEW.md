# IMTS 项目概览

## 项目简介

IMTS（Intelligent Mail Task Synergy System / 智能邮件任务协同系统）是一个面向小团队的邮件任务管理工具。它自动从 QQ 邮箱抓取近期邮件，通过规则引擎或大模型（DeepSeek）识别其中包含的任务，汇总到本地看板中统一管理。

**核心价值：** 邮件里散落的任务请求、客户跟进、会议安排，不用手动整理，自动汇入看板。

## 核心功能

1. **邮件同步** — 通过 QQ IMAP 抓取近期邮件，支持去重、MIME 解析
2. **智能任务提取** — 三种模式可选：纯规则 / 大模型优先+规则兜底 / 纯大模型
3. **看板管理** — 待办 → 进行中 → 已完成 三栏管理，支持搜索、筛选
4. **任务编辑** — 支持修改任务名称、截止日期、优先级、分类，支持删除
5. **置信度标注** — 大模型任务显示置信度，低于 0.70 标红预警
6. **邮件溯源** — 每个任务可回溯到原始邮件正文

## 技术架构

```
┌─────────────────────────────────────────────┐
│                  UI 层                       │
│          frontend/ (Vue 3 + Ant Design)      │
├─────────────────────────────────────────────┤
│               API 层 (FastAPI)               │
│     tasks / emails / config / sync          │
├─────────────────────────────────────────────┤
│               服务层                         │
│  mail_sync_service  │  task_service         │
├─────────────────────────────────────────────┤
│               AI 引擎                        │
│  task_extractor → llm_client (DeepSeek)     │
│                 → rules engine (内置)        │
│  prompt_engine  │  task_schema              │
├─────────────────────────────────────────────┤
│              数据层                          │
│    SQLAlchemy ORM → SQLite                  │
└─────────────────────────────────────────────┘
```

**技术栈：**

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy |
| 前端 | Vue 3 / TypeScript / Ant Design Vue 4 / Pinia |
| 数据库 | SQLite（本地文件 `imts_demo.db`） |
| LLM 接口 | DeepSeek API（OpenAI 兼容 `/chat/completions`） |
| 邮件协议 | QQ Mail IMAP（SSL，imap.qq.com:993） |
| 部署 | Linux 服务器 + uvicorn / 本地 Windows BAT |

## 目录结构

```
IMTS-v1.0/
├── start-imts.bat              # Windows 一键启动
├── start-server.sh             # Linux 服务器启动
├── README.md                   # 用户使用教程
├── PROJECT_OVERVIEW.md         # 本文件：项目概览（面向开发者）
├── CLAUDE.md                   # AI 助手指引
├── FUTURE_OPTIMIZATION.md      # 后续优化备忘
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── imts_demo.db                # SQLite 数据库（运行时生成）
├── backend/                    # FastAPI 后端
│   └── app/
│       ├── main.py             # 应用入口 + 静态文件服务
│       ├── database.py         # SQLAlchemy 连接与会话
│       ├── config.py           # .env 配置读写
│       ├── api/                # REST API 路由
│       │   ├── tasks.py        # 任务 CRUD + 统计
│       │   ├── emails.py       # 邮件列表 + 同步 + 提取
│       │   └── config.py       # 配置读写
│       ├── models/             # SQLAlchemy ORM
│       │   ├── task.py
│       │   └── email.py
│       ├── schemas/            # Pydantic 校验
│       │   ├── task.py
│       │   ├── email.py
│       │   └── enums.py
│       ├── ai/                 # AI 引擎
│       │   ├── llm_client.py   # DeepSeek API 调用
│       │   ├── prompt_engine.py# Prompt 构造
│       │   ├── task_extractor.py# 任务提取入口 + 规则引擎
│       │   └── task_schema.py  # LLM 输出校验与规范化
│       ├── services/           # 业务服务
│       │   ├── mail_sync_service.py # 邮件同步（IMAP + MIME）
│       │   └── task_service.py      # 任务业务逻辑
│       └── data/               # 数据层
│           ├── database.py     # SQLite 初始化与连接
│           └── sample_emails.py# 34 封测试邮件
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── App.vue             # 全局 Layout + 导航
│       ├── views/
│       │   ├── Board.vue       # 三栏任务看板
│       │   └── Settings.vue    # 邮箱 + LLM 配置
│       ├── components/
│       │   ├── TaskCard.vue    # 任务卡片
│       │   └── TaskForm.vue    # 创建/编辑弹窗
│       ├── stores/tasks.ts     # Pinia 任务状态
│       ├── router/index.ts     # Vue Router 路由
│       └── api/index.ts        # Axios 请求封装
├── docs/                       # 项目文档
│   ├── requirements.md
│   ├── architecture.md
│   ├── design-spec.md
│   ├── development-plan.md
│   └── deployment.md
├── devlog/                     # 开发日志
└── scripts/                    # 工具脚本
    └── devlog.py
```

## 数据流

```
QQ 邮箱 ──IMAP──→ mail_sync_service ──→ emails 表
                       │
                       ▼
              task_extractor (规则/LLM)
                       │
                       ▼
                  tasks 表 ←── 手动创建
                       │
                       ▼
              Vue 3 看板 (三栏展示)
```

## AI 提取效果

在 100 封真实办公/科研邮件上的基准测试：

| 指标 | 纯规则 | LLM（DeepSeek V4 Flash） | 混合模式 |
|------|--------|--------------------------|---------|
| 准确率 | 79.0% | 96.0% | **96.0%** |
| 漏报 | 2 封 | **0 封** | **0 封** |
| 陷阱识别 | 56% | 87.5% | **87.5%** |
| 单封成本 | 0 | ~0.003 元 | ~0.003 元 |

> 行业参考：Travelers Insurance 用 Claude 做邮件分类，91% 即视为生产可用。IMTS 达 96%。

## 关键数据

- API 端点：20 个 | 前端组件：6 个
- 测试邮件：100 封（办公/科研真实场景）+ 15 封演示邮件
- 开发周期：2 天（Streamlit 单体 → FastAPI + Vue 3 重构 + 云部署）

## 快速开始

### 用户：一键运行

装 Python 3.10+ 和 Node.js 18+，双击 `start-imts.bat`

### 开发者：本地开发

```bash
# 1. 后端
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
cp .env.example .env   # 填写 API Key

# 2. 前端
cd frontend && npm install

# 3. 启动（两个终端）
.venv\Scripts\python -m uvicorn backend.app.main:app --port 8501 --reload
cd frontend && npm run dev
```

浏览器访问 `http://localhost:5173`，后端 Swagger `http://localhost:8501/docs`。

开发前先读 [CLAUDE.md](CLAUDE.md) 了解项目规范，然后看 [docs/development-plan.md](docs/development-plan.md) 了解当前进度。

### 云部署

见 [docs/deployment.md](docs/deployment.md)
