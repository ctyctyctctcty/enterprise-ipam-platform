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

## 当前仓库已经准备了什么

脚本：

- [scripts/windows-hyperv-init.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-hyperv-init.ps1)
- [scripts/windows-hyperv-run.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-hyperv-run.ps1)
- [scripts/windows-hyperv-restore-demo-db.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-hyperv-restore-demo-db.ps1)
- [scripts/windows-scheduled-task-install.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-scheduled-task-install.ps1)
- [scripts/windows-scheduled-task-remove.ps1](C:\codex-workspace\enterprise-ipam\scripts\windows-scheduled-task-remove.ps1)

环境模板：

- [`.env.hyperv.example`](C:\codex-workspace\enterprise-ipam\.env.hyperv.example)

可直接恢复的 demo 假数据数据库：

- [demo/enterprise_ipam_demo_seed.db](C:\codex-workspace\enterprise-ipam\demo\enterprise_ipam_demo_seed.db)

## 基础部署步骤

### 1. 安装 Python

建议 Python 3.12 或 3.13。

安装时勾选：

- `Add Python to PATH`

验证：

```powershell
python --version
py --version
```

### 2. 拉代码

```powershell
git clone <你的仓库地址>
cd enterprise-ipam-platform
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
- 如果仓库里带了 demo seed 数据库，就直接恢复这份假数据
- 如果没有 demo seed 数据库，才走 migration 和 seed 初始化

### 4. 手工启动方式

```powershell
.\scripts\windows-hyperv-run.ps1 -Port 18000
```

这是最简单的启动方式，但有一个明显问题：

- 你一 logout，它就停

因为它仍然是前台 PowerShell 进程。

## 为什么 logout 以后服务会停

因为你现在跑的是：

- 你登录 Windows
- 打开 PowerShell
- 手工运行 `uvicorn`
- 这个进程属于你的登录会话

所以：

- 关 PowerShell 窗口会停
- logout 会停
- 重启 VM 会停

## 推荐的 Windows 原生解决办法

如果你不想引入第三方服务包装器，推荐方式是：

- **Windows 任务计划程序**

优点：

- Windows 原生
- 不需要额外安装 NSSM 之类工具
- logout 不会停
- VM 重启后可以自动拉起
- 对公司环境更容易解释

## 方案 A：用仓库自带脚本安装计划任务

推荐先用这个。

### 安装计划任务

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-scheduled-task-install.ps1 -Port 18000 -StartNow
```

这个脚本会：

- 创建一个名为 `EnterpriseIPAM` 的计划任务
- 在 Windows 启动时自动运行
- 默认使用 `SYSTEM` 账户运行
- 把日志写到：
  - `logs\scheduled-task-stdout.log`
  - `logs\scheduled-task-stderr.log`

### 检查计划任务

```powershell
Get-ScheduledTask -TaskName EnterpriseIPAM
```

### 立即启动计划任务

```powershell
Start-ScheduledTask -TaskName EnterpriseIPAM
```

### 删除计划任务

```powershell
.\scripts\windows-scheduled-task-remove.ps1
```

## 方案 B：GUI 点点点方式创建计划任务

如果你不想跑脚本，也可以用 Windows 自带界面手动建。

### 第 1 步：打开任务计划程序

在开始菜单搜索：

- `任务计划程序`
- 或 `Task Scheduler`

### 第 2 步：创建任务

不要用“创建基本任务”，直接用：

- `创建任务`

### 第 3 步：常规页签

建议这样填：

- 名称：`EnterpriseIPAM`
- 描述：`Enterprise IPAM internal platform startup task`
- 勾选：`使用最高权限运行`
- 选择：`无论用户是否登录都要运行`

### 第 4 步：触发器页签

新增触发器：

- `启动时`

这样每次 VM 开机都会自动启动。

### 第 5 步：操作页签

新增操作：

- 程序或脚本：
  `powershell.exe`

- 添加参数：

```powershell
-NoProfile -WindowStyle Hidden -Command "C:\你的项目路径\enterprise-ipam-platform\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 18000 >> C:\你的项目路径\enterprise-ipam-platform\logs\scheduled-task-stdout.log 2>> C:\你的项目路径\enterprise-ipam-platform\logs\scheduled-task-stderr.log"
```

注意：

- 路径要换成你 VM 里的真实路径
- `logs\` 目录最好先存在

### 第 6 步：条件页签

建议把会阻碍启动的选项关掉，尤其是：

- 仅在使用交流电源时启动

### 第 7 步：设置页签

建议打开：

- 允许按需运行任务
- 如果任务失败，按以下频率重新启动
- 如果任务已在运行，则不要启动新实例

## 安装完后怎么检查

### 1. 看计划任务状态

```powershell
Get-ScheduledTask -TaskName EnterpriseIPAM
```

### 2. 看端口监听

```powershell
netstat -ano | findstr :18000
```

### 3. 本机浏览器验证

- `http://127.0.0.1:18000/admin/`
- `http://127.0.0.1:18000/dashboard`

### 4. 同事访问

如果 VM 固定 IP 是 `10.10.10.25`，那同事访问：

- `http://10.10.10.25:18000/admin/`
- `http://10.10.10.25:18000/dashboard`

## 防火墙还要不要配

要。

如果你想让同事访问，仍然需要放行端口，比如 18000：

```powershell
New-NetFirewallRule -DisplayName "Enterprise IPAM 18000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 18000
```

## Hyper-V 网络必须确认的事

你必须确认：

- 这台 VM 不是只走 NAT
- VM 有固定内网 IP
- 同事所在网段能访问这台 VM
- 宿主机和 VM 的防火墙没有拦截

推荐：

- Hyper-V 使用 `External Virtual Switch`
- 给 VM 分配公司内网可达地址

## 当前这种形态的限制

现在这套“直接拉下来就能跑”的形态，默认仍然更偏 PoC：

- 默认数据库仍是 SQLite
- 还没有 HTTPS
- 还没有 Entra / AD 登录
- 还没有正式反向代理

但如果你只是想让同事先稳定访问，计划任务方案已经比手工打开 PowerShell 强很多。

## 之后建议升级的方向

如果这台 Hyper-V 机器要继续承担更稳定的内部服务，下一步建议至少做：

1. SQLite 切 PostgreSQL
2. 加 IIS / Nginx / Caddy 反向代理
3. 改成 HTTPS
4. 接公司认证体系

## 一句话建议

如果你当前目标是：

- logout 不停
- 重启后自动起来
- 又不想上第三方服务包装器

那就用 Windows 任务计划程序。这个仓库现在已经给你准备好了脚本和操作说明。 
