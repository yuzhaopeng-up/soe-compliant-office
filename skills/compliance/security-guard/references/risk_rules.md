# Security-Guard 风险规则参考

## 目录

1. [规则总表](#规则总表)
2. [规则详细定义](#规则详细定义)
3. [风险等级计算](#风险等级计算)
4. [央国企业务场景规则映射](#央国企业务场景规则映射)

---

## 规则总表

| 编号 | 规则 | 默认等级 | 触发条件 |
|------|------|---------|---------|
| R01 | 只读报表类不应申请写入或删除权限 | 高 | Skill 类型为报表/查询，但含 write/delete 权限 |
| R02 | 内部问答类不应读取全量业务明细 | 高 | Skill 类型为问答/客服，含 read:business_full |
| R03 | 自动外发消息必须人工确认 | 高 | 含 send:external_* 且无人工确认环节 |
| R04 | 删除/批量更新/敏感字段导出为高风险 | 高 | 含 delete:* 或 batch_write:* 或 export:sensitive |
| R05 | 知识库问答不得跨知识库越权检索 | 高 | 含 read:kb_cross 或 data_scope 跨知识库 |
| R06 | 无审计日志的写入类至少中风险 | 中 | 含 write/* 但无 audit_log 配置 |
| R07 | 明文输出手机号/证件号/办公地址为高风险 | 高 | 输出结构含敏感字段且无脱敏规则 |
| R08 | 权限编码不规范 | 中 | 权限项不符合 `操作:资源` 格式 |
| R09 | 数据范围未声明 | 中 | data_scope 为空或"未声明" |
| R10 | 敏感字段未声明 | 低 | sensitive_fields 为空 |

---

## 规则详细定义

### R01：只读报表类权限越界

**触发条件**：
- `skill_config.type` 为 `report` / `query` / `statistics` / `dashboard`
- `permission_list` 中包含 `write:*` 或 `delete:*`

**判定逻辑**：
```
IF skill_type IN ["report","query","statistics","dashboard"]
  AND permission_list CONTAINS "write:*" OR "delete:*"
THEN risk_level = "high"
```

**整改建议模板**：
- 移除 `write:XXX` 权限，仅保留 `read:XXX`
- 移除 `delete:XXX` 权限，如需清理历史数据应走独立运维流程

---

### R02：内部问答类全量读取

**触发条件**：
- `skill_config.type` 为 `qa` / `customer_service` / `chatbot`
- `permission_list` 中包含 `read:business_full` 或 `read:business_all`
- 或 `data_scope` 为 `全量业务数据`

**判定逻辑**：
```
IF skill_type IN ["qa","customer_service","chatbot"]
  AND (permission_list CONTAINS "read:business_full" 
       OR data_scope == "全量业务数据")
THEN risk_level = "high"
```

**整改建议模板**：
- 将 `read:business_full` 收敛为 `read:business_by_ticket`（按工单关联查询）
- 将 `data_scope` 从"全量业务数据"收窄为"按工单关联"或"按服务对象"

---

### R03：自动外发无人工确认

**触发条件**：
- `permission_list` 中包含 `send:external_message` 或 `send:external_*`
- `skill_config` 中无 `human_confirm: true` 或等效配置

**判定逻辑**：
```
IF permission_list CONTAINS "send:external_*"
  AND NOT skill_config.human_confirm == true
THEN risk_level = "high"
```

**整改建议模板**：
- 添加 `human_confirm: true` 配置，外发前弹出人工确认
- 或将 `send:external_message` 降级为 `send:internal_notification`

---

### R04：删除/批量更新/敏感导出

**触发条件**：
- `permission_list` 中包含 `delete:*`
- 或包含 `batch_write:*`（单次影响 > 100 条）
- 或包含 `export:business_detail`且 `sensitive_fields` 非空

**判定逻辑**：
```
IF permission_list CONTAINS "delete:*" → high
IF permission_list CONTAINS "batch_write:*" → high
IF permission_list CONTAINS "export:business_detail" 
  AND sensitive_fields NOT EMPTY → high
```

**整改建议模板**：
- 删除权限：改为软删除（标记状态）或走审批流程
- 批量写入：限制单次操作条数 ≤ 100，或添加批量操作审批
- 敏感导出：添加脱敏规则，禁止导出明文敏感字段

---

### R05：跨知识库越权检索

**触发条件**：
- `skill_config.type` 为 `knowledge_qa` / `kb_search`
- `permission_list` 中包含 `read:kb_cross` 或含多个知识库的读权限
- 或 `data_scope` 跨知识库

**判定逻辑**：
```
IF skill_type IN ["knowledge_qa","kb_search"]
  AND (permission_list CONTAINS "read:kb_cross"
       OR count(read:kb_*) > 1)
THEN risk_level = "high"
```

**整改建议模板**：
- 限定仅访问业务所需的知识库：`read:kb_core`（核心知识库）
- 移除 `read:kb_cross`，改为按业务域授权

---

### R06：写入类无审计日志

**触发条件**：
- `permission_list` 中包含 `write:*`
- `skill_config` 中无 `audit_log` 或 `audit_log.enabled != true`

**判定逻辑**：
```
IF permission_list CONTAINS "write:*"
  AND (NOT skill_config.audit_log 
       OR skill_config.audit_log.enabled != true)
THEN risk_level = "medium"
```

**整改建议模板**：
- 启用审计日志，至少记录：操作人、操作时间、输入摘要、输出摘要
- 添加 `audit_log: { enabled: true, fields: ["operator","timestamp","input_summary","output_summary"] }`

---

### R07：明文输出敏感字段

**触发条件**：
- `sensitive_fields` 中包含高敏字段（手机号/证件号/办公地址/银行账号）
- `skill_config` 中无对应脱敏规则

**敏感字段与脱敏规则映射**：

| 敏感字段 | 脱敏规则 | 示例 |
|---------|---------|------|
| 手机号 | 中间4位掩码 | `138****5678` |
| 证件号 | 保留前3后4 | `110***********1234` |
| 办公地址/项目地址 | 仅保留到区级 | `XX省XX市XX区***` |
| 银行账号 | 仅保留后4位 | `****5678` |
| 合同金额 | 视业务决定 | `***万` 或保留原值 |

**判定逻辑**：
```
FOR EACH field IN sensitive_fields:
  IF field IN ["手机号","证件号","办公地址/项目地址","银行账号"]
    AND NOT skill_config.mask_rules[field] EXISTS
  THEN risk_level = "high"
```

**整改建议模板**：
- 为 `{字段名}` 添加脱敏规则：`mask_rules: { "手机号": "middle_4_mask" }`

---

### R08：权限编码不规范

**触发条件**：
- `permission_list` 中的项不符合 `操作:资源` 格式
- 操作类型不在 `[read, write, delete, send, call]` 中

**判定逻辑**：
```
FOR EACH perm IN permission_list:
  IF NOT match(perm, "^(read|write|delete|send|call):[a-z_]+$")
  THEN risk_level = "medium"
```

**整改建议模板**：
- 将 `{原始编码}` 规范为 `{标准编码}`，格式为 `操作:资源`

---

### R09：数据范围未声明

**触发条件**：
- `data_scope` 为空或值为"未声明"

**整改建议模板**：
- 声明 `data_scope`，推荐值：`本人` / `班组` / `部门/单位` / `全量业务数据`
- 遵循最小范围原则

---

### R10：敏感字段未声明

**触发条件**：
- `sensitive_fields` 为空数组或未提供

**整改建议模板**：
- 梳理 Skill 涉及的敏感字段并声明
- 常见敏感字段：`手机号`、`证件号`、`办公地址/项目地址`、`合同金额`、`银行账号`

---

## 风险等级计算

### 整体风险等级

```
high_risk_count = COUNT(risk_items WHERE risk_level == "high")
medium_risk_count = COUNT(risk_items WHERE risk_level == "medium")

IF high_risk_count >= 3 → risk_level = "high"
IF high_risk_count >= 1 → risk_level = "medium"  (除非已因单项被评为high)
IF high_risk_count == 0 AND medium_risk_count >= 3 → risk_level = "medium"
IF high_risk_count == 0 AND medium_risk_count < 3 → risk_level = "low"
```

### 置信度计算

```
base_confidence = 1.0
IF "skill_config" MISSING → base_confidence -= 0.3
IF "permission_list" MISSING → base_confidence -= 0.3
IF "data_scope" MISSING → base_confidence -= 0.1
IF "sensitive_fields" MISSING → base_confidence -= 0.1
IF "action_list" MISSING → base_confidence -= 0.05
confidence = MAX(0.0, base_confidence)
```

---

## 央国企业务场景规则映射

| 场景 | 常见越权模式 | 适用规则 |
|------|-------------|---------|
| 运维工单查询 | 工单查询申请了全量业务数据读取 | R02 |
| 企业专线管理 | 专线配置 Skill 含删除权限 | R04 |
| 客户投诉处理 | 投诉回复自动外发无确认 | R03 |
| 业务记录流转 | 记录处理含批量关闭权限 | R04 |
| 营销活动推送 | 活动消息自动外发敏感内容 | R03, R07 |
| 知识库问答 | 问答 Skill 跨核心/合规知识库 | R05 |
| 经营分析报表 | 报表 Skill 含写入权限 | R01 |
| 资料归档 | 归档 Skill 无审计日志 | R06 |
| 客户信息展示 | 明文显示手机号 | R07 |
| 多 Agent 协作 | 协作流程无审计链路 | R06 |
