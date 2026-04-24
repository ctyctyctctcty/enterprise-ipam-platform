# 正式落地前必须补齐的信息和必须修改的内容

这份文档不是“以后有空再说”的清单，而是把系统从 demo 带到公司内部真实使用前，必须补齐的内容。

建议把下面内容分成三类理解：

- 现在为了 demo 先写死的内容
- 现在还是 placeholder 的内容
- 接公司真实环境前必须确认的内部信息

## 一、必须先改的内容

这些内容如果不改，系统只能算 demo。

### 1. `SECRET_KEY`

当前 [`.env.example`](C:\codex-workspace\enterprise-ipam\.env.example) 里：

```env
SECRET_KEY=change-me
```

这在正式环境绝对不能使用。

必须改成：

- 足够长
- 随机生成
- 由公司安全要求管理

### 2. 数据库连接

当前默认是：

```env
DATABASE_URL=sqlite:///./enterprise_ipam.db
```

或本地 demo SQLite 文件。

正式环境必须改成公司认可的数据库连接，例如：

- PostgreSQL
- 公司托管数据库

你必须拿到的信息：

- 数据库类型
- 主机名或地址
- 端口
- 数据库名
- 用户名
- 密码
- 是否要求 SSL/TLS
- 是否允许应用主机访问

### 3. 默认账号和默认密码

当前 demo 用户包括：

- `admin@example.com / admin123`
- 其他 demo 账号

这些在公司环境中必须移除或替换。

必须改成：

- 公司账号体系
- 或临时受控账号
- 并且强制重置默认密码

### 4. `DEBUG`

当前示例环境里：

```env
DEBUG=true
```

正式环境必须评估是否关闭。

### 5. `.env.example` 与 `.env` 的使用方式

当前 [docker-compose.yml](C:\codex-workspace\enterprise-ipam\docker-compose.yml) 直接引用 `.env.example`。

这对 demo 方便，但对公司部署不合适。

建议正式化前至少改成：

- `.env.example` 只做模板
- `.env` 才是真实运行配置
- 真正的机密不要提交到仓库

## 二、必须取得的公司内部信息

下面这些信息如果拿不到，平台就只能停留在 demo 或半手工阶段。

## 1. 组织与位置主数据

至少要确认：

- 站点清单
- 建筑清单
- 楼层清单
- 房间编码规则
- 信息插座编码规则

为什么重要：

- `Site / Building / Floor / Room / InformationOutlet` 是物理映射的基础
- 如果公司内部没有统一编码，需要先确定一个映射策略

## 2. 网络设备与端口信息

至少要确认：

- 交换机清单
- 设备命名规则
- 管理 IP
- 端口命名格式
- 信息插座与端口是否已有对应表

为什么重要：

- 没有这些，`SwitchPort Mapping` 和 `Topology` 只能做 demo

## 3. VLAN / Subnet / 固定 IP 管理规则

至少要确认：

- 固定 IP 使用哪些 VLAN
- 每个 VLAN 对应哪些 Subnet
- 哪些网段允许固定 IP
- 哪些网段是 DHCP pool
- 哪些网段禁止分配
- 是否有保留地址段

为什么重要：

- 当前规则引擎只能做基础判断
- 真正上线前必须知道公司自己的网络分配规则

## 4. 申请流程信息

至少要确认：

- 谁发起固定 IP 申请
- 审批节点有哪些
- 哪些角色能批准
- 是否分站点、部门、用途走不同审批路径
- Power Apps 和 Power Automate 未来分别负责什么

为什么重要：

- `IntakeRequest` 和 `ApprovalStep` 结构已经有了
- 但真实审批路线必须来自公司实际流程

## 5. 身份认证与权限信息

至少要确认：

- 是否接 Entra ID / Azure AD
- 是否允许本地账号
- 用户角色如何映射
- 是否要按部门、站点、角色做权限隔离

为什么重要：

- 当前 auth 是本地 scaffold
- 正式上线一般不应继续靠本地 demo 用户

## 6. 审计与合规要求

至少要确认：

- 审计日志保留多久
- 哪些字段属于敏感信息
- 是否允许存储 MAC 地址
- 是否要记录操作人真实身份
- 是否需要导出审计记录

为什么重要：

- 当前 `AuditLog` 已经有基础结构
- 但保留策略和敏感数据要求必须来自公司规范

## 三、必须补实现的 importer / integration

当前项目里这些 importer 和 integration 只是结构和占位，不是正式可接入版本。

### 当前 importer 状态

目录：
- [app/importers](C:\codex-workspace\enterprise-ipam\app\importers)

现状：

- `excel.py`：已有 demo 可用实现
- `dhcp.py`：仍需真实接入
- `dns.py`：仍需真实接入
- `arp.py`：仍需真实接入

### 当前 integration 状态

目录：
- [app/integrations](C:\codex-workspace\enterprise-ipam\app\integrations)

现状：

- `microsoft.py`：未来 Power Apps / Power Automate 集成边界
- `network.py`：未来网络侧接入边界
- `topology_discovery.py`：未来 LLDP / CDP / MAC 发现占位

## 正式环境前必须明确每个 importer 的真实来源

### 1. Excel importer

必须确认：

- 谁提供 Excel
- Excel 字段列名固定吗
- 一天导几次
- 是人工上传还是共享目录抓取
- 哪些列是必填

### 2. DHCP importer

必须确认：

- DHCP 服务器是什么
- 是否 AD-backed
- 是否能导出 CSV
- 是否有 API / PowerShell / WMI
- 应用如何认证
- 允许读取哪些 scope

### 3. DNS importer

必须确认：

- DNS 服务类型
- 是否允许导出记录
- 是否能拉取 A / PTR 记录
- 是否有权限限制

### 4. ARP importer

必须确认：

- ARP 数据从哪里来
- 是交换机采集、日志采集还是网管平台
- 采集频率
- 是否能关联端口和时间

### 5. Topology discovery

必须确认：

- 是否能获取 LLDP/CDP 邻接信息
- 是否有 MAC address table 访问方式
- 是否允许 SNMP / SSH / API
- 哪些设备品牌和命令集需要支持

## 四、必须确认的 `.env` 项目

除了已有 `.env.example` 字段，正式环境通常还需要继续补充。

当前至少要确认这些已有项：

- `APP_NAME`
- `APP_ENV`
- `DEBUG`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`
- `POSTGRES_SERVER`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `ADMIN_TITLE`

建议后续新增但现在还没完全落地的项：

- Entra / SSO 相关配置
- 公司代理配置
- SMTP 或通知渠道配置
- 导入任务共享目录路径
- 外部系统 API 地址
- 外部系统认证方式

## 五、必须确认的数据映射问题

真实落地前非常容易出问题的，不是代码本身，而是字段和主数据映射。

必须确认：

- 公司“信息插座编码”怎么映射到 `InformationOutlet.code`
- 设备型号怎么映射到 `DeviceModel`
- Power Apps 表单字段怎么映射到 `IntakeRequest`
- 审批流外部步骤怎么映射到 `ApprovalStep`
- DHCP/DNS/ARP 观测怎么映射到 `SourceRecord` 和 `IPAddressSourceObservation`

## 六、正式切换前建议做的最小改造

如果准备把这个 demo 带到公司内部试点，建议先做下面几件事：

1. 把 `.env.example` 和真实运行配置分离清楚
2. 把默认 demo 用户和密码移除
3. 把 Docker Compose 改成真正读取 `.env`
4. 先接一个真实但低风险的数据源
5. 先做一个真实 Power Apps 提交入口
6. 先确认一条真实审批路径
7. 先和网络团队确认一套真实 outlet / switch-port 映射样本

## 七、你现在可以把项目分成哪几种状态来理解

### 状态 A：纯 demo

特点：

- 本地电脑
- SQLite
- demo seed
- Excel demo 导入

### 状态 B：内部 PoC

特点：

- 公司电脑或测试服务器
- PostgreSQL
- 少量真实主数据
- 半手工 importer
- 部分真实流程

### 状态 C：正式试点

特点：

- 公司认证体系
- 真实 DHCP / DNS / ARP 接入
- 审计要求已确认
- 多角色权限明确
- 备份和恢复策略明确

## 最后一句话

这套系统现在已经具备“演示和架构验证”的条件，但要进入公司真实使用，关键不是继续多写几个页面，而是尽快拿到公司内部的真实主数据、认证方式、网络数据来源和审批规则。 
