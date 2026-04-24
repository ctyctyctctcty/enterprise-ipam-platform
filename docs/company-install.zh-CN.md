# 公司电脑从零安装指南

这份文档假设目标机器是一台新的公司电脑，之前没有安装 Python、PostgreSQL、Docker，也没有现成的开发环境。

目标不是“最佳开发机配置”，而是让系统可以在公司电脑上先跑起来，用于内部 demo、验证和初期部署准备。

## 先判断你要走哪种安装方式

推荐先做这个判断。

### 方式 A：本地 Python + SQLite

适合场景：

- 快速 demo
- 单机验证
- 先给领导或同事看
- 没有 Docker 权限
- 没有数据库服务器

优点：

- 最简单
- 不依赖 PostgreSQL
- 机器要求最低

缺点：

- 不适合多人共用
- 不适合正式环境

### 方式 B：Docker Compose + PostgreSQL

适合场景：

- 想更接近正式部署
- 公司电脑允许安装 Docker Desktop
- 希望环境更一致

优点：

- 更接近正式运行方式
- PostgreSQL 更贴近目标架构
- 部署清晰

缺点：

- 对电脑权限要求更高
- 需要 Docker Desktop

如果只是先在公司电脑上 demo，建议先用方式 A。

## 安装前准备

至少需要准备这些内容：

- 项目代码目录
- Windows 11 或 Windows 10
- 能打开 PowerShell
- 本地管理员权限或 IT 协助

## 方式 A：本地 Python + SQLite 安装步骤

### 第 1 步：安装 Python

建议安装 Python 3.12 或 3.13。

安装时请注意：

- 勾选 `Add Python to PATH`

安装后在 PowerShell 验证：

```powershell
python --version
```

### 第 2 步：打开项目目录

```powershell
Set-Location C:\codex-workspace\enterprise-ipam
```

如果项目不在这个路径，请切换到实际路径。

### 第 3 步：创建虚拟环境

```powershell
python -m venv .venv
```

### 第 4 步：激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止执行脚本，可以先在当前会话临时放开：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### 第 5 步：安装依赖

```powershell
pip install -r requirements.txt
```

### 第 6 步：复制环境文件

```powershell
Copy-Item .env.example .env
```

如果只是 demo，`.env` 可以先保持 SQLite 模式。

当前默认关键配置大致如下：

- `APP_ENV=local`
- `DEBUG=true`
- `DATABASE_URL=sqlite:///./enterprise_ipam.db`

注意：
如果项目现在本地已经在用另一个数据库文件，例如 `enterprise_ipam_demo.db`，请以你实际 `.env` 内容为准。

### 第 7 步：初始化数据库

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts\init_db.py
```

这一步会：

- 创建数据库表
- 写入 seed 数据
- 生成 demo Excel 文件

### 第 8 步：启动服务

建议避开常见端口冲突，使用高位端口，例如 `18000`。

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 18000
```

### 第 9 步：打开页面验证

- [http://127.0.0.1:18000/dashboard](http://127.0.0.1:18000/dashboard)
- [http://127.0.0.1:18000/admin](http://127.0.0.1:18000/admin)
- [http://127.0.0.1:18000/docs](http://127.0.0.1:18000/docs)

### 第 10 步：登录后台

默认 demo 账号：

- `admin@example.com`
- `admin123`

## 方式 B：Docker Compose + PostgreSQL 安装步骤

### 第 1 步：安装 Docker Desktop

需要 IT 或管理员权限。

安装后确认：

```powershell
docker --version
docker compose version
```

### 第 2 步：准备 `.env`

仍然建议先复制：

```powershell
Copy-Item .env.example .env
```

但要注意：
当前 [docker-compose.yml](C:\codex-workspace\enterprise-ipam\docker-compose.yml) 里引用的是 `.env.example`，不是 `.env`。

这意味着如果要拿去公司电脑长期使用，建议后续改成引用 `.env`，不要继续直接依赖 `.env.example`。

### 第 3 步：启动容器

```powershell
docker compose up --build
```

### 第 4 步：初始化数据库

如果容器中没有自动执行迁移和 seed，需要在 app 容器里手动执行。

实际操作方式取决于你后续是否把这些命令写进容器启动流程。

目前推荐的思路是：

1. 先让容器启动
2. 进入 app 容器
3. 执行

```bash
alembic upgrade head
python scripts/init_db.py
```

### 第 5 步：打开页面

默认 compose 暴露的是：

- [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)

如果公司电脑上 `8000` 被占用，需要修改 compose 端口映射。

## 给公司电脑安装时最容易遇到的问题

### 1. Python 没加 PATH

现象：

```powershell
python --version
```

找不到命令。

解决：

- 重新安装 Python，并勾选加入 PATH
- 或使用 Python 安装路径的绝对路径

### 2. PowerShell 不让激活虚拟环境

解决：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

### 3. 端口冲突

现象：

- 打开页面进入了别的系统
- Uvicorn 报 `address already in use`

解决：

- 改端口，例如 `18000`
- 并优先访问 `127.0.0.1`，不要混用 `localhost`

### 4. Docker Desktop 安装受限

如果公司电脑装不了 Docker，就先用本地 Python + SQLite 跑 demo。

### 5. 杀毒或代理导致依赖安装失败

解决：

- 需要公司网络代理配置
- 或让 IT 提供允许的 Python 包镜像

## 建议的公司内部分阶段落地方式

### 第 1 阶段：单机 demo

- 公司电脑
- Python 本地安装
- SQLite
- 只做业务演示

### 第 2 阶段：小范围验证

- Docker Compose
- PostgreSQL
- 受控网络环境
- 导入一部分真实数据样本

### 第 3 阶段：正式化部署

- 公司正式数据库
- 正式认证方式
- 受控导入任务
- 审计要求确认
- 备份和恢复流程

## 安装完成后的最小验证清单

安装后，至少验证这些：

1. `/dashboard` 能打开
2. `/admin` 能登录
3. `/docs` 能看到 OpenAPI
4. `scripts/init_db.py` 已生成 demo 数据
5. `Import Jobs` 页面有种子数据
6. `Request List` 页面有 demo request
7. `IP List` 页面能看到多种 IP 状态

如果这几项都正常，说明这台公司电脑已经具备基本演示能力。
