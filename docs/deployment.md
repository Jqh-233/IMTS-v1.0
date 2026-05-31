# IMTS 云服务器部署指南

部署后团队成员只需浏览器访问，无需安装任何东西。

## 第一步：买服务器

推荐 **腾讯云轻量应用服务器**，学生价 60-100 元/年。

配置：1 核 / 1 GB 内存 / 系统选 **Ubuntu 24.04**（22.04 也可以）。

买完记下 **公网 IP**。如果不知道 root 密码，去控制台"重置密码"。

## 第二步：安装 Python

```bash
ssh ubuntu@你的IP   # 用户名是 ubuntu，不是 root
sudo apt update && sudo apt install python3 python3-venv python3-pip -y
```

## 第三步：上传项目

在你**本地电脑**的 cmd 中（不是在服务器上）：

```bash
scp IMTS-distribution.zip ubuntu@你的IP:/home/ubuntu/
```

## 第四步：启动服务

回到服务器 SSH 窗口：

```bash
unzip IMTS-distribution.zip
cd IMTS-v1.0
bash start-server.sh
```

## 第五步：放行端口

去云服务器控制台 → **防火墙**（腾讯云轻量）/ **安全组**（阿里云 ECS）→ 添加规则：

| 来源 | 协议 | 端口 | 策略 |
|------|------|------|------|
| 0.0.0.0/0 | TCP | 8501 | 允许 |

## 第六步：访问

```
http://你的公网IP:8501
```

## 后台运行（持久化）

关掉 SSH 窗口后服务会停。用 screen 让它在后台持续运行：

```bash
# 先 Ctrl+C 停掉当前服务
sudo apt install screen -y
screen -S imts
.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8501
# 看到 Uvicorn running 后，按 Ctrl+A 然后 D 分离
```

服务继续在后台跑，关 SSH 不影响。重新连接管理：

```bash
screen -r imts   # 回到服务界面
```

## 绑定域名（可选）

1. 腾讯云/阿里云搜"域名注册"，买个便宜域名（5-10 元/年）
2. 域名控制台 → DNS 解析 → 添加 A 记录，记录值填服务器 IP
3. 几分钟后即可用 `http://你的域名:8501` 访问

## 后续更新

```bash
# 本地：重新打包
# 服务器：覆盖并重启
screen -r imts   # 进入 screen
Ctrl+C            # 停服务
unzip -o IMTS-distribution.zip  # 覆盖文件
.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8501
Ctrl+A D          # 分离
```

## 常见问题

**Q: 访问不了？**
A: 三重检查：1) `curl localhost:8501/health` 返回 OK；2) 防火墙放行 8501；3) 浏览器用 `http://` 不是 `https://`。

**Q: Permission denied (publickey,password)？**
A: 用户名换成 `ubuntu`，不是 `root`。Ubuntu 云镜像默认禁用 root SSH 登录。
