# Security-Guard 学员操作指南

## 前置条件

- 已安装 TeleAgent 并启动
- 已安装 Security-Guard 安全权限基础组件
- 准备好待检查的 Skill 配置信息

---

## 7 步操作流程

### 第 1 步：粘贴 Skill 配置

将待检查 Skill 的配置信息以 JSON 格式粘贴。

**示例**：
```json
{
  "name": "信息查询助手",
  "type": "query",
  "version": "1.0.2",
  "business_purpose": "内部人员根据工单号查询客户业务信息",
  "human_confirm": false,
  "audit_log": {
    "enabled": false
  }
}
```

**要求**：至少包含 `name`、`type`、`business_purpose` 三个字段。

---

### 第 2 步：填写权限列表

列出该 Skill 申请的所有权限，使用 `操作:资源` 编码格式。

**权限编码规范**：

| 操作 | 编码前缀 | 示例 |
|------|---------|------|
| 读取 | read: | `read:business_full`、`read:business_self` |
| 写入 | write: | `write:business_remark`、`write:business_status` |
| 删除 | delete: | `delete:log`、`delete:business_record` |
| 外发 | send: | `send:external_message`、`send:internal_notification` |
| 接口调用 | call: | `call:api_internal`、`call:api_crm` |

**示例**：
```json
["read:business_full", "export:business_detail", "send:external_message", "write:business_remark"]
```

---

### 第 3 步：填写数据范围

选择该 Skill 实际需要的数据访问范围：

| 范围选项 | 说明 | 适用场景 |
|---------|------|---------|
| 本人 | 仅访问本人数据 | 个人工单查询 |
| 班组 | 访问班组内数据 | 班组长查看组内工单 |
| 部门/单位 | 跨班组但限制在部门/单位内 | 部门/单位管理员 |
| 全量业务数据 | 跨部门/单位或访问全量 | 集团报表（极少场景） |
| 未声明 | 不确定范围 | 新 Skill 尚未梳理 |

**示例**：`"全量业务数据"`

---

### 第 4 步：运行检查

将以上信息组合为完整输入，触发 Security-Guard 检查。

**完整输入示例**：
```json
{
  "skill_config": {
    "name": "信息查询助手",
    "type": "query",
    "version": "1.0.2",
    "business_purpose": "内部人员根据工单号查询客户业务信息",
    "human_confirm": false,
    "audit_log": {"enabled": false}
  },
  "permission_list": ["read:business_full", "export:business_detail", "send:external_message", "write:business_remark"],
  "data_scope": "全量业务数据",
  "sensitive_fields": ["手机号", "办公地址/项目地址", "证件号"],
  "action_list": ["读取", "导出", "外发", "写入"]
}
```

对 TeleAgent 说：
> "使用 Security-Guard 检查以下 Skill 的安全权限配置：[粘贴上述 JSON]"

---

### 第 5 步：查看 risk_items

检查结果中的 `risk_items` 是核心关注点。逐条阅读：

| 字段 | 含义 | 行动 |
|------|------|------|
| risk_type | 风险类别 | 了解是哪类问题 |
| description | 风险描述 | 理解具体问题 |
| evidence | 触发依据 | 定位输入中的问题点 |
| recommendation | 整改建议 | 按此修改配置 |

**常见风险类型速查**：

| risk_type | 含义 | 紧急度 |
|-----------|------|--------|
| PERMISSION_OVERSCOPE | 权限超出业务需要 | 高 |
| DATA_SCOPE_OVERSCOPE | 数据范围过大 | 高 |
| SENSITIVE_FIELD_EXPOSURE | 敏感字段未脱敏 | 高 |
| HIGH_RISK_ACTION | 高危动作（删除/外发/批量写入） | 高 |
| AUDIT_MISSING | 审计日志缺失 | 中 |
| ENCODING_NONSTANDARD | 权限编码不规范 | 低 |

---

### 第 6 步：根据建议收敛权限

按 `permission_reduction_suggestions` 和 `recommendation` 逐条修改 Skill 配置。

**常见收敛模式**：

| 原权限 | 收敛后 | 理由 |
|--------|-------|------|
| read:business_full | read:business_by_ticket | 按工单关联查询而非全量 |
| export:business_detail | 移除或加脱敏+审批 | 避免批量泄露 |
| send:external_message | send:internal_notification + 人工确认 | 外发必须可控 |
| write:business_remark | 移除 | 查询类不需要写入 |
| delete:* | 软删除或走审批流程 | 删除不可逆 |

**别忘了**：
- 添加敏感字段脱敏规则（mask_rules）
- 启用审计日志（audit_log）
- 外发/删除添加人工确认（human_confirm）

---

### 第 7 步：再次运行复查

修改完成后，用整改后的配置重新运行 Security-Guard 检查。

**预期**：
- `risk_level` 从 high → low
- `risk_items` 为空数组
- `confidence` 接近 1.0

如果仍有风险项，重复第 5-7 步直到全部通过。

---

## 常见问题

**Q：如果我不确定某个权限是否必要怎么办？**
A：`required_human_confirmations` 中会提示需要人工复核的权限项，请业务负责人判断。

**Q：敏感字段列表不确定怎么办？**
A：参考常见敏感字段：手机号、证件号、办公地址/项目地址、合同金额、银行账号。宁可多声明不要漏。

**Q：所有 Skill 都必须通过 Security-Guard 检查吗？**
A：建议所有上线 Skill 至少通过 low 等级检查。high 等级的 Skill 不应上线。

**Q：Security-Guard 会自动修改权限吗？**
A：不会。它只输出检查结果和建议，所有修改需人工执行。

**Q：检查结果置信度低于 0.7 怎么办？**
A：说明关键输入字段缺失，请补全 `skill_config` 和 `permission_list` 后重新检查。
