# IMTS 后续优化备忘

本文档记录当前项目未来可以继续优化的方向，便于后续迭代。

## 1. 同步体验优化

当前同步邮件是页面内同步执行，用户点击按钮后需要等待 IMAP 抓取和任务提取完成。

可优化方向：

- 把"抓邮件"和"任务提取"拆开：先快速入库，再后台提取。
- 使用后台线程或任务队列，按钮点击后立即返回。
- 页面显示同步状态：等待中、同步中、已完成、失败。
- 支持分批处理，例如一次只处理 5 封未处理邮件。
- 支持"停止同步"或"稍后继续"。
- 对 LLM 调用增加失败统计和重试策略。

目标体验：

- 1-3 秒内给用户反馈。
- 3-8 秒内完成小批量同步。
- 超过 8 秒必须有明确进度提示。

## 2. 多用户化

当前是单用户模式。多人访问云服务器时看到同一套任务池。

多用户版本需要：

- 登录注册。
- `emails` 和 `tasks` 增加 `user_id`。
- 每个用户独立保存邮箱配置。
- 邮箱授权码加密存储。
- 后端接口鉴权。

## 3. 数据库升级

SQLite 适合本地演示和单用户使用。部署升级建议 PostgreSQL 或 MySQL，搭配 Alembic 迁移工具、定期备份。

## 4. 邮件同步能力

可继续增强：

- 支持多邮箱账号。
- 支持更多邮箱服务商（Gmail、163 等）。
- 支持按发件人、主题、文件夹过滤。
- 支持只同步未读邮件。
- 支持用户手动标记"永远忽略此类邮件"。

## 5. 大模型提取质量

可继续优化：

- 建立评测集，记录规则和 LLM 每次结果。
- 在页面提供"这个判断错了"反馈按钮。
- 把用户修正后的结果沉淀为规则或 few-shot 示例。
- 对低置信度任务进入人工确认区。
- 对营销、收据、系统通知继续扩展负样本。

## 6. 规则兜底

维护原则：

- 只补充高频、明确、低风险规则。
- 避免过宽关键词，例如单独用"交易""购买"排除。
- 新规则必须用样例邮件验证。
- 保留少量规则陷阱样例，用于展示 LLM 的语义优势。

## 7. 部署上线

已实现：FastAPI 后端云服务器部署，screen 后台守护，防火墙放行。详见 [docs/deployment.md](docs/deployment.md)。

后续可补：Nginx 反向代理、HTTPS 证书、systemd 守护进程。

## 8. 打包和分发

当前 `start-imts.bat` 支持 Windows 一键启动，仍需 Python + Node.js。云服务器部署方案（[docs/deployment.md](docs/deployment.md)）已实现免安装浏览器访问。

更进一步可以：

- 制作桌面快捷方式。
- 使用 VBS 隐藏命令行窗口。
- 使用 Electron / Tauri 做桌面壳。
（PyInstaller 已尝试，与项目架构不兼容，放弃。）

## 9. 测试覆盖扩展

已有基础：`pytest`（10 个任务 CRUD 用例），`vue-tsc` + `vite build`（前端类型检查）。

可扩展方向：

- AI 引擎测试：用 `test_emails_100.py` 的 100 封标注邮件验证规则引擎准确率
- 邮件同步测试：mock IMAP 连接，验证 MIME 解析和去重逻辑
- 前端组件测试：vitest + @vue/test-utils 覆盖 Pinia store
- 端到端测试：Playwright 覆盖核心用户流程（配置→同步→看板→状态流转）

## 10. 日志系统增强

已有基础：`logging_config.py`（模块级 logger，stdout 输出）。

可扩展方向：

- 日志级别按模块可配置（如 ai 模块 DEBUG，api 模块 INFO）
- 日志持久化到文件 + 按日期轮转
- 结构化 JSON 日志（便于 ELK/Loki 等日志平台接入）
- 请求级别 trace ID（便于追踪单次同步的完整调用链）

## 11. 2026-06-07 代码审计遗留问题

以下问题来自全面代码审计（9 角度查找），已确认但暂缓修复：

| # | 问题 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | 数据库索引缺失 | 中 | tasks 表缺少 deadline+status、priority+status 复合索引，大量任务时全表扫描 |
| 2 | N+1 查询 | 中 | list_emails 循环内逐行查 Task，应改用 joinedload |
| 3 | email_dict 重复 5 处 | 低 | 同一个 ORM→dict 转换在 emails.py 中重复定义，应提取为 Email.to_extraction_dict() |
| 4 | FK pragma 未启用 | 中 | SQLite 默认忽略外键，删邮件后 Task 变成孤儿行 |
| 5 | forceTask 缺 task_status | 低 | store 中 forceTask 未设置 task_status: 'pending'，与 extractTask 不一致 |
| 6 | 规则引擎置信度 0.0 | 低 | 规则提取的任务一律 confidence=0.0，触发低置信度黄色预警，实际应区分"不确定"和"确定" |
| 7 | 日志架构优化 | 低 | per-module handler 创建反模式，应改为根 logger 统一 handler + 传播 |
| 8 | emailBody 竞态条件 | 低 | EmailDrawer 中 emailBody 是单 ref，快速切换邮件时正文可能覆盖 |
| 9 | allow_email_content 默认值不一致 | 低 | config.py 默认 False，PUT API 的 Pydantic 模型默认 True |
| 10 | Dead sort 参数 | 低 | tasks API 接受 sort 参数但从未使用，查询始终按 deadline 排序 |
| 11 | 硬编码 "DeepSeek" 错误信息 | 低 | llm_client.py 错误消息写死 "DeepSeek"，用其他 API 时会误导用户 |
| 12 | 脆弱 provider 检测 | 低 | llm_client.py 用 URL 子串匹配判断是否 DeepSeek，代理场景误判 |
