# Hyper-V Windows 服务器部署说明

这份文档针对的是最实际的场景：

- 你把仓库从 GitHub 拉到公司的一台 Hyper-V Windows 虚拟机
- 不安装 Docker
- 直接把这台机器当作内部试运行服务器
- 让同事通过内网 IP 访问这个系统

这是一种 PoC / 内部试运行部署方式，不是最终正式生产方案。

## 推荐用途

适合：

- 内部演示
- 小范围试用
- 先让几个同事连接验证
- 先跑 Power Apps / Power Automate 对接前的后端验证

不适合：

- 大规模并发
- 正式生产高可用
- 严格合规环境

## 当前仓库已经为这种方式准备了什么

新增了两个脚本：

- [scripts/windows-hyperv-init.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-hyperv-init.ps1)
- [scripts/windows-hyperv-run.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-hyperv-run.ps1)

以及一个专门给 Hyper-V Windows 用的环境模板：

- [`.env.hyperv.example`](C:\codex-workspace\enterprise-ipam\.env.hyperv.example)

默认思路：

- Windows VM
- Python 虚拟环境
- SQLite 单机数据库
- Uvicorn 直接对内网监听

这样做的优点是：

- 拉下来就能跑
- 依赖最少
- 不要求 Docker

## 在 Hyper-V 里的操作步骤

### 1. 在 VM 上安装 Python

建议 Python 3.12 或 3.13。

安装时勾选：

- `Add Python to PATH`

验证：

```powershell
python --version
py --version
```

### 2. 从 GitHub 拉代码

```powershell
git clone <你的仓库地址>
cd enterprise-ipam
```

### 3. 初始化

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-hyperv-init.ps1
```

这个脚本会自动做：

- 创建 `.venv`
- 安装依赖
- 从 `.env.hyperv.example` 复制出 `.env`
- 执行 Alembic migration
- 执行 seed 初始化

### 4. 修改 `.env`

最少要改：

- `SECRET_KEY`
- `DEBUG=false` 保持关闭

如果只是内部试运行，默认 SQLite 可以先保留：

```env
DATABASE_URL=sqlite:///./enterprise_ipam_server.db
```

### 5. 启动服务

```powershell
.\scripts\windows-hyperv-run.ps1 -Port 18000
```

这个脚本会以：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 18000
```

的方式启动，所以同一内网里的同事可以访问。

### 6. 开防火墙

如果 Windows 防火墙拦截，需要放行端口。

例如 18000：

```powershell
New-NetFirewallRule -DisplayName "Enterprise IPAM 18000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 18000
```

### 7. 给同事访问地址

例如这台 VM 的 IP 是 `10.10.10.25`，则同事访问：

- `http://10.10.10.25:18000/admin/`
- `http://10.10.10.25:18000/docs`
- `http://10.10.10.25:18000/topology`

## Hyper-V 网络必须确认的事

最容易出问题的不是应用，而是 Hyper-V 网络。

你必须确认：

- 这台 VM 不是只走 NAT
- VM 有固定内网 IP
- 同事所在网段能访问这台 VM
- 宿主机和 VM 的防火墙没有拦截

最推荐：

- Hyper-V 使用 `External Virtual Switch`
- 给 VM 分配公司内网可达地址

## 当前这种 Hyper-V 形态的限制

现在这套“直接拉下来就能跑”的形态，默认更偏 PoC：

- 默认数据库仍是 SQLite
- 没有 Windows Service 自动托管
- 没有 HTTPS
- 没有 Entra / AD 登录
- 没有正式反向代理

所以它适合先让同事看和试，不适合长期正式运行。

## 之后建议升级的方向

如果这台 Hyper-V 机器要继续承担更稳定的内部服务，下一步建议至少做：

1. SQLite 切 PostgreSQL
2. Uvicorn 进程改为 Windows Service 托管
3. 加 IIS / Nginx / Caddy 反向代理
4. 改成 HTTPS
5. 接公司认证体系

## 给同事的最小使用入口

你可以先只给他们这两个地址：

- `/admin/`
- `/dashboard`

如果是技术同事再给：

- `/docs`

## 一句话建议

如果你的目标是“公司同事先连上来看和用”，这个仓库现在已经被整理成可以直接在 Hyper-V Windows VM 上拉下来、初始化、启动并开放内网访问的形态了。 
