# Demo 演示指南

这份文档是给内部演示人用的，不是给开发者看的技术说明。

目标只有一个：
在 5 到 10 分钟内，让听众理解这个平台的核心价值不是“数据库管理页”，而是“固定 IP 申请与 IP 证据整合的运营中台”。

## 一句话讲清楚这个系统

这个系统把固定 IP 管理涉及的几类信息放到同一个后端里：

- 申请数据
- IP 地址库存
- 子网和 VLAN
- 信息插座和交换机端口映射
- 导入证据来源
- 审计日志

然后它能做一个最关键的动作：
收到固定 IP 申请后，基于已有证据做确定性判断，告诉运营人员这个申请是：

- 可以推荐候选 IP
- 必须人工复核
- 当前应该阻止

## Demo 前准备

建议在演示前先确认以下几件事都已经完成：

1. 数据库已经初始化

```powershell
Set-Location C:\codex-workspace\enterprise-ipam
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts\init_db.py
```

2. 服务已经启动

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 18000
```

3. 浏览器页面可以正常打开

- [http://127.0.0.1:18000/dashboard](http://127.0.0.1:18000/dashboard)
- [http://127.0.0.1:18000/admin](http://127.0.0.1:18000/admin)
- [http://127.0.0.1:18000/docs](http://127.0.0.1:18000/docs)
- [http://127.0.0.1:18000/topology](http://127.0.0.1:18000/topology)

4. 默认管理员账号可登录

- `admin@example.com`
- `admin123`

## Demo 时重点看什么

不要一上来讲模型、模块、数据库。
先讲“运营价值”，再用页面证明。

建议顺序如下。

### 第一段：先看 Dashboard

打开：
- [http://127.0.0.1:18000/dashboard](http://127.0.0.1:18000/dashboard)

要讲的重点：

- 这是运营首页，不是技术后台首页
- 第一眼就能看到 IP 资源总体情况
- 能直接看到冲突、人工复核、导入失败、可疑追溯不足
- 对内部运维或网络团队来说，这比单纯的 CRUD 列表更有意义

建议指给观众看的位置：

- KPI 卡片
  - total IPs
  - allocated fixed IPs
  - available candidate IPs
  - conflict suspected
  - review needed requests
  - failed import jobs
- Fixed IP capacity alerts
- DHCP scope alerts
- Operational alerts
- Recent activity
- Site summary

你可以这样讲：

“这个首页的作用不是替代 CMDB，也不是替代 Power Apps，而是给内部运营人员一个固定 IP 资源和异常情况的统一观察面。”

### 第二段：看 Topology

打开：
- [http://127.0.0.1:18000/topology](http://127.0.0.1:18000/topology)

要讲的重点：

- 这是只读拓扑视图，不是编辑器
- 它把站点、楼层、房间、信息插座、交换机、端口、子网和 IP overlay 联系起来
- 未来可以接 LLDP / CDP / MAC 观测来增强自动发现

重点不是画图多漂亮，而是让人看到：

- 物理位置
- 交换机端口映射
- 信息插座
- 子网/IP 逻辑关系

### 第三段：看导入证据

先说明 demo 里已经准备了几份文件：

- [demo/demo_ips.xlsx](C:\codex-workspace\enterprise-ipam\demo\demo_ips.xlsx)
- [demo/capacity_alert_ips.xlsx](C:\codex-workspace\enterprise-ipam\demo\capacity_alert_ips.xlsx)
- [demo/branch_demo_ips.xlsx](C:\codex-workspace\enterprise-ipam\demo\branch_demo_ips.xlsx)

建议展示：

- 这些文件代表外部来源证据，不是最终真相
- 真正的系统记录在后端数据库
- 导入后会形成 `ImportJob`、`SourceRecord`、`IPAddressSourceObservation`

然后在 Admin 打开：

- `Operations > Import Jobs`
- `Operations > Source Records`
- `Operations > IP Source Observations`

要讲的重点：

- 这个平台不是把 Excel 直接当主数据
- 它保留“来源”和“观测”
- 所以未来可以做多源比对和冲突识别

### 第四段：看申请流程

打开 Swagger：
- [http://127.0.0.1:18000/docs](http://127.0.0.1:18000/docs)

建议演示：

- `POST /api/v1/requests/submit`
- `POST /api/v1/requests/{request_id}/transition`
- `GET /api/v1/requests/status/{request_number}`

重点要讲：

- 前端未来可以是 Power Apps
- 审批编排未来可以是 Power Automate
- 但申请记录和状态判断必须留在后端

### 第五段：讲确定性规则，不要讲 AI

当前 demo 中最重要的规则是确定性的，不是 AI 决定：

- `dhcp_pool` -> 不推荐 / 阻止
- `allocated_confirmed` -> 阻止
- `conflict_suspected` -> 人工复核
- 无明显阻断证据 -> 候选 IP

你可以直接强调：

“AI 可以以后用来解释风险、辅助查询，但不能替代硬规则和审计责任。”

### 第六段：看 Admin 里的结果和审计

打开：

- `IPAM > IP List`
- `IPAM > Conflict Review`
- `Requests > Request List`
- `Operations > Audit Logs`
- `Operations > Allocation History`

要讲的重点：

- 申请、导入、分配、状态变化都留下记录
- 后台是 source of truth
- Power Apps 和 Power Automate 只是外部壳层

## 最推荐的现场演示顺序

### 方案 A：5 分钟版本

1. 打开 Dashboard
2. 打开 Topology
3. 打开 Swagger，提交一个请求
4. 展示返回结果里的 `eligibility_outcome`
5. 在 Admin 里打开 Request List 和 Audit Logs

适合领导和非技术听众。

### 方案 B：10 分钟版本

1. 打开 Dashboard，说明系统目标
2. 打开 demo Excel 文件，说明这是外部证据
3. 在 Admin 里展示 Import Jobs、Source Records、IP Source Observations
4. 在 Swagger 提交请求
5. 展示 candidate / review_needed / blocked 的区别
6. 调用 transition 接口
7. 在 Admin 中展示 Request、IP 状态、Allocation History、Audit Logs
8. 打开 Topology 补充物理映射价值

适合 IT 部门、基础设施团队、网络团队。

## Demo 时不要陷进去的细节

下面这些点不要在 demo 现场讲太久：

- SQLAlchemy 模型层级
- Alembic 细节
- Dockerfile 细节
- AI skill 占位结构
- 为什么有些 importer 还是 stub

这些内容可以回答，但不是演示主线。

## Demo 里最容易被问到的问题

### 问：为什么不用 Excel 继续管？

建议回答：

Excel 能当来源，但不能当系统记录。它没有统一审计、状态机、审批衔接、多源冲突处理和 API 集成能力。

### 问：为什么不直接在 Power Apps 里做逻辑？

建议回答：

Power Apps 更适合做输入界面，不适合承载企业级的规则、审计和多源数据整合。真正稳定的逻辑应当在后端。

### 问：现在是不是已经能接公司真实数据？

建议回答：

架构和扩展点已经准备好，但正式接公司数据前还必须补公司内部环境参数、认证方式、DHCP/DNS/ARP 访问方式、字段映射和审计要求。

## 演示结束时的收尾话术

建议一句话总结：

“这个平台已经证明，固定 IP 管理可以从分散 Excel 和邮件流转，收敛成一个可审计、可集成、可逐步扩展的后端核心系统。”
