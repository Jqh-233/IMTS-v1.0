# IMTS — 智能邮件任务协同系统

IMTS 是一个小团队邮件任务管理工具。同步 QQ 邮箱，通过 AI 自动提取任务，在看板中管理进度。

## 技术架构

```
浏览器 → Vue 3 前端 → FastAPI 后端 → SQLite
```

- **前端**：Vue 3 + Ant Design Vue 4 + Pinia + TypeScript + Vite
- **后端**：FastAPI + SQLAlchemy + Pydantic
- **AI**：DeepSeek API（OpenAI 兼容），支持 rules / llm / hybrid 三种模式
- **数据库**：SQLite（imts_demo.db）

## 快速启动

### 前提

- 安装 [Python 3.10+](https://www.python.org/downloads/)（勾选 "Add Python to PATH"）
- 安装 [Node.js 18+](https://nodejs.org/)（LTS 版本）

### 本地使用

```
双击 → start-imts.bat
```

脚本自动完成：检测环境 → 创建虚拟环境 → 安装依赖 → 启动后端:8501 + 前端:5173 → 打开浏览器。

首次需等待 2-3 分钟下载依赖，之后秒开。

### 环境配置

复制 `.env.example` 为 `.env`，按需填写：

```text
QQ_EMAIL=your@qq.com          # 可选，同步 QQ 邮箱才需要
QQ_AUTH_CODE=your_auth_code   # 可选
LLM_API_KEY=sk-your-key       # 可选，使用 AI 提取才需要
LLM_MODEL=deepseek-chat       # 可选
```

不填也能用——系统内置 34 封演示邮件。

### 云部署（团队共享）

将 IMTS 部署到云服务器，全队浏览器访问，无需各自安装环境。

详见 **[docs/deployment.md](docs/deployment.md)**

## 功能概览

| 功能 | 描述 |
|------|------|
| 📧 邮件同步 | QQ 邮箱 IMAP 同步，演示邮件直接体验 |
| 🤖 AI 提取 | 规则 / LLM / 混合三种模式，智能判断是否包含任务 |
| 📊 三栏看板 | 待办 → 进行中 → 已完成，一键流转 |
| ⚠️ 置信度 | LLM 置信度 <70% 红色标记，用户二次确认 |
| 🔍 搜索筛选 | 任务名称搜索 + 优先级过滤 |
| ⚙️ 配置管理 | 邮箱 / LLM 配置页面，密钥脱敏 |
| 📝 手动任务 | 不依赖邮件，直接创建任务 |

## API 文档

后端启动后访问：**http://localhost:8501/docs**

## 项目结构

```
IMTS-v1.0/
├── backend/               # FastAPI 后端
│   └── app/
│       ├── main.py        # 应用入口 + 静态文件服务
│       ├── api/           # 路由：tasks / emails / config
│       ├── models/        # ORM 模型
│       ├── schemas/       # Pydantic 校验
│       ├── ai/            # AI 引擎
│       ├── services/      # 业务服务
│       └── data/          # 数据层
├── frontend/              # Vue 3 前端
│   └── src/
│       ├── views/         # Board / Settings
│       ├── components/    # TaskCard / TaskForm
│       ├── stores/        # Pinia 状态
│       └── api/           # Axios 请求
├── docs/                  # 项目文档
├── start-imts.bat         # 一键启动
├── start-backend.bat      # 单独启动后端
├── start-frontend.bat     # 单独启动前端
└── start-server.sh        # Linux 服务器启动
```

## 常见问题

### QQ 邮箱同步失败

- 确保已开启 QQ 邮箱 IMAP 服务
- 使用授权码而不是 QQ 密码

### LLM 调用失败

- API Key 是否有效、模型名称是否正确
- 是否在设置中勾选"允许发送邮件内容给外部模型"

### 端口被占用

后端默认 8501，前端默认 5173。可修改 `vite.config.ts` 或 uvicorn `--port` 参数。
