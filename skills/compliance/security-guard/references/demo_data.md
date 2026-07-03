# Security-Guard 演示数据

## 场景：权限过大的信息查询助手

### 输入数据

```json
{
  "skill_config": {
    "name": "信息查询助手",
    "type": "query",
    "version": "1.0.2",
    "business_purpose": "内部人员根据工单号或客户姓名查询客户业务信息",
    "human_confirm": false,
    "audit_log": {
      "enabled": false
    }
  },
  "permission_list": [
    "read:business_full",
    "export:business_detail",
    "send:external_message",
    "write:business_remark"
  ],
  "data_scope": "全量业务数据",
  "sensitive_fields": ["手机号", "办公地址/项目地址", "证件号"],
  "action_list": ["读取", "导出", "外发", "写入"]
}
```

### 预期输出

```json
{
  "status": "partial",
  "risk_level": "high",
  "risk_items": [
    {
      "risk_type": "PERMISSION_OVERSCOPE",
      "description": "内部查询类 Skill 申请了业务备注写入权限(write:business_remark)，超出业务必要范围",
      "evidence": "skill_config.type=query, permission_list 含 write:business_remark",
      "recommendation": "移除 write:business_remark 权限，业务备注修改应走专门的数据维护 Skill"
    },
    {
      "risk_type": "DATA_SCOPE_OVERSCOPE",
      "description": "内部查询 Skill 数据范围为全量业务数据，超出按工单关联查询的业务需要",
      "evidence": "data_scope=全量业务数据, skill_config.type=query",
      "recommendation": "将 data_scope 从'全量业务数据'收窄为'按工单关联'或'按服务对象'，权限改为 read:business_by_ticket"
    },
    {
      "risk_type": "SENSITIVE_FIELD_EXPOSURE",
      "description": "Skill 涉及手机号、办公地址/项目地址、证件号三个高敏字段，但无脱敏规则配置",
      "evidence": "sensitive_fields=['手机号','办公地址/项目地址','证件号'], skill_config 无 mask_rules",
      "recommendation": "添加脱敏规则：手机号中间4位掩码(138****5678)、证件号保留前3后4(110***********1234)、办公地址/项目地址仅保留到区级(XX省XX市XX区***)"
    },
    {
      "risk_type": "HIGH_RISK_ACTION",
      "description": "Skill 可导出业务明细(export:business_detail)，且敏感字段无脱敏，存在批量泄露风险",
      "evidence": "permission_list 含 export:business_detail, sensitive_fields 含高敏字段",
      "recommendation": "移除 export:business_detail 权限，或添加导出脱敏规则并走人工审批流程"
    },
    {
      "risk_type": "HIGH_RISK_ACTION",
      "description": "Skill 可自动外发消息(send:external_message)，且无人工确认环节",
      "evidence": "permission_list 含 send:external_message, skill_config.human_confirm=false",
      "recommendation": "添加 human_confirm:true 配置，外发前必须人工确认；或将外发权限降级为内部通知 send:internal_notification"
    },
    {
      "risk_type": "AUDIT_MISSING",
      "description": "Skill 含写入权限但未启用审计日志",
      "evidence": "permission_list 含 write:business_remark, audit_log.enabled=false",
      "recommendation": "启用审计日志，至少记录：操作人、操作时间、输入摘要、输出摘要"
    }
  ],
  "permission_reduction_suggestions": [
    "read:business_full → read:business_by_ticket：从全量读取收窄为按工单关联查询",
    "移除 write:business_remark：内部查询不应修改业务备注",
    "移除 export:business_detail：如确需导出应添加脱敏+审批",
    "send:external_message → send:internal_notification：外发改为内部通知"
  ],
  "required_human_confirmations": [
    "外发消息(send:external_message)必须添加人工确认机制",
    "导出业务明细(export:business_detail)需人工审批后执行",
    "全量业务数据读取权限需业务负责人确认必要性"
  ],
  "audit_requirements": [
    "启用审计日志：audit_log.enabled = true",
    "记录操作人(operator)：必须",
    "记录操作时间(timestamp)：必须",
    "记录输入摘要(input_summary)：推荐",
    "记录输出摘要(output_summary)：推荐"
  ],
  "missing_fields": [],
  "confidence": 0.85,
  "source": "Security-Guard v1.0",
  "next_actions": [
    "1. 将 read:business_full 改为 read:business_by_ticket",
    "2. 移除 write:business_remark 权限",
    "3. 为敏感字段添加脱敏规则(mask_rules)",
    "4. 添加 human_confirm:true 或移除外发权限",
    "5. 启用 audit_log",
    "6. 修改完成后重新运行 Security-Guard 检查"
  ]
}
```

---

## 场景：合规的运维工单查询 Skill（对照示例）

### 输入数据

```json
{
  "skill_config": {
    "name": "运维工单查询",
    "type": "query",
    "version": "1.0.0",
    "business_purpose": "运维人员查询本人待处理工单",
    "human_confirm": false,
    "audit_log": {
      "enabled": true,
      "fields": ["operator", "timestamp", "input_summary"]
    },
    "mask_rules": {
      "手机号": "middle_4_mask",
      "办公地址/项目地址": "district_only"
    }
  },
  "permission_list": [
    "read:business_self"
  ],
  "data_scope": "本人",
  "sensitive_fields": ["手机号", "办公地址/项目地址"],
  "action_list": ["读取"]
}
```

### 预期输出

```json
{
  "status": "success",
  "risk_level": "low",
  "risk_items": [],
  "permission_reduction_suggestions": [],
  "required_human_confirmations": [],
  "audit_requirements": ["建议补充输出摘要(output_summary)到审计日志"],
  "missing_fields": [],
  "confidence": 1.0,
  "source": "Security-Guard v1.0",
  "next_actions": ["审计日志可考虑补充 output_summary 字段"]
}
```

---

## 场景：知识库跨库越权检索

### 输入数据

```json
{
  "skill_config": {
    "name": "业务问答助手",
    "type": "knowledge_qa",
    "version": "2.1.0",
    "business_purpose": "回答内部人员关于业务流程和运维规范的问题",
    "audit_log": {
      "enabled": true,
      "fields": ["operator", "timestamp"]
    }
  },
  "permission_list": [
    "read:kb_core",
    "read:kb_compliance",
    "read:kb_finance"
  ],
  "data_scope": "全量知识库",
  "sensitive_fields": [],
  "action_list": ["读取"]
}
```

### 预期输出（关键风险项）

```json
{
  "status": "success",
  "risk_level": "high",
  "risk_items": [
    {
      "risk_type": "DATA_SCOPE_OVERSCOPE",
      "description": "业务问答 Skill 可跨知识库检索（含合规知识库、财务知识库），超出核心业务范畴",
      "evidence": "permission_list 含 read:kb_compliance 和 read:kb_finance，data_scope=全量知识库",
      "recommendation": "移除 read:kb_compliance 和 read:kb_finance，仅保留 read:kb_core；data_scope 改为'核心知识库'"
    }
  ],
  "permission_reduction_suggestions": [
    "移除 read:kb_compliance：业务问答不应访问合规知识库",
    "移除 read:kb_finance：业务问答不应访问财务知识库",
    "data_scope 从'全量知识库'改为'核心知识库'"
  ],
  "required_human_confirmations": [],
  "audit_requirements": [],
  "missing_fields": [],
  "confidence": 1.0,
  "source": "Security-Guard v1.0",
  "next_actions": [
    "1. 移除 read:kb_compliance 和 read:kb_finance",
    "2. 将 data_scope 限制为'核心知识库'",
    "3. 重新运行 Security-Guard 检查"
  ]
}
```

---

## 脱敏演示数据说明

以上所有示例数据均为课程演示用途，不涉及任何真实业务信息：
- 名称：`张三`、`李四` 等化名
- 手机号：`138****5678` 均为脱敏格式
- 证件号：`110***********1234` 均为脱敏格式
- 地址：`XX省XX市XX区***` 仅保留到区级
- 工单号：`WO20260620XXXX` 为虚构编号
