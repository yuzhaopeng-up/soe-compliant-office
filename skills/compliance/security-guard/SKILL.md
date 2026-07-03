---
name: security-guard
name_cn: 安全权限基础组件
version: 1.0.0
domain: compliance
soe_relevance: 5
description: >
  Security permission checking component for Skill/Agent configurations. Validates minimum privilege
  principle, data scope, sensitive field handling, high-risk action detection, and audit trail completeness.
  Outputs risk grading (low/medium/high) with remediation suggestions. Mandatory gate for all SOE
  Skill deployments.
description_cn: >
  安全权限基础组件，检查Skill/Agent权限配置、数据访问范围、敏感字段、高危动作与审计日志。
  输出低/中/高风险分级与整改建议，是央国企Skill上线前的强制守门组件。
---

# Security-Guard 安全权限基础组件

## 一、定位与适用人群

**核心理念**："客户明确关注安全权限，这个组件必须做。"

**组件定位**：检查其他 Skill 或 Agent 的权限配置、数据访问范围、敏感字段处理、外发动作、删除动作和审计日志，帮助理解权限最小化原则。既是安全教学组件，也是所有 Skill 上线前的守门组件。

**适用人群**：技术骨干、系统管理员、平台运营人员、项目负责人、合规人员。

**典型央国企业务场景**：
1. 检查客户信息查询 Skill 是否读取范围过大
2. 检查业务记录处理 Skill 是否具备不必要的删除权限
3. 检查报表生成 Skill 是否会输出明文敏感字段
4. 检查知识库问答 Skill 是否跨知识库越权检索
5. 检查消息推送 Skill 是否自动外发敏感内容
6. 检查多 Agent 流程是否保留审计链路

## 二、输入参数

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| skill_config | object | 必填 | 待检查 Skill 的配置内容 | `{"name":"信息查询助手","type":"query","business_purpose":"内部查询客户业务信息"}` |
| permission_list | array | 必填 | 该 Skill 申请的权限列表 | `["read:business_full","export:business_detail","send:external_message"]` |
| data_scope | string | 可选 | 数据访问范围 | `"全量业务数据"` / `"本人班组"` / `"部门/单位范围"` |
| sensitive_fields | array | 可选 | 敏感字段列表 | `["手机号","证件号","办公地址/项目地址","合同金额"]` |
| action_list | array | 可选 | 该 Skill 会执行的动作 | `["读取","写入","外发","删除","调用接口"]` |
| risk_level_policy | object | 可选 | 风险等级规则（覆盖默认规则） | `{"plaintext_sensitive":"high","cross_scope_access":"high"}` |

**权限编码规范**：权限列表项格式为 `操作:资源`，如 `read:business_full`、`write:business_record`、`delete:log`、`send:external_message`、`call:api_internal`。

## 三、处理流程

### 步骤 1：输入校验与补全

1. 检查 `skill_config` 是否为空 → 为空则立即返回 error
2. 检查 `permission_list` 是否为空 → 为空则标记 `missing_fields`
3. 补全可选字段默认值：
   - `data_scope` 未填 → 默认 `"未声明"`，标记为中风险
   - `sensitive_fields` 未填 → 默认 `[]`，标记提示"建议声明敏感字段"
   - `action_list` 未填 → 从 `permission_list` 推断
4. 校验权限编码格式，不规范的项记入 `risk_items`

### 步骤 2：权限解析

解析 `permission_list`，按操作类型分类：

| 操作类型 | 编码前缀 | 说明 |
|----------|----------|------|
| 读取 | read: | 数据查询/检索 |
| 写入 | write: | 新增/修改数据 |
| 删除 | delete: | 删除数据 |
| 外发 | send: | 向外部系统/人员发送消息 |
| 接口调用 | call: | 调用其他系统 API |

输出：`{read_permissions: [], write_permissions: [], delete_permissions: [], send_permissions: [], call_permissions: []}`

### 步骤 3：最小权限检查

对照 `skill_config.business_purpose` 评估每个权限的必要性：

- **只读报表类** Skill → 不应申请 write 或 delete 权限
- **内部问答类** Skill → 不应读取全量业务明细（read:business_full）
- **业务记录处理类** Skill → delete 权限需有业务必要性证明
- **知识库问答类** Skill → 不应跨知识库越权检索

权限越界项记入 `risk_items`，risk_type 为 `PERMISSION_OVERSCOPE`。

### 步骤 4：数据范围检查

根据 `data_scope` 判定风险：

| 数据范围 | 风险等级 | 条件 |
|----------|----------|------|
| 本人 | 低 | 仅访问本人数据 |
| 班组 | 低 | 访问班组内数据 |
| 部门/单位 | 中 | 跨班组但限制在部门/单位内 |
| 全量业务数据 | 高 | 跨部门/单位或访问全量 |
| 未声明 | 中 | 不确定范围 |

越权访问项记入 `risk_items`，risk_type 为 `DATA_SCOPE_OVERSCOPE`。

### 步骤 5：敏感字段检查

扫描 `sensitive_fields` 和 Skill 输出结构：

| 敏感字段类型 | 明文输出风险 | 脱敏要求 |
|-------------|-------------|----------|
| 手机号 | 高 | 中间4位掩码 `138****5678` |
| 证件号 | 高 | 保留前3后4 `110***********1234` |
| 办公地址/项目地址 | 高 | 仅保留到区级 `XX省XX市XX区***` |
| 合同金额 | 中 | 视业务需要决定是否掩码 |
| 银行账号 | 高 | 仅保留后4位 `****5678` |

明文输出敏感字段的项记入 `risk_items`，risk_type 为 `SENSITIVE_FIELD_EXPOSURE`。

### 步骤 6：高危动作检查

高危动作判定规则：

| 动作 | 风险等级 | 条件 |
|------|----------|------|
| 自动外发消息 | 高 | 无人工确认环节 |
| 删除数据 | 高 | 任何删除操作 |
| 批量写入 | 高 | 单次影响 > 100 条记录 |
| 跨系统调用 | 中 | 调用非本系统 API |
| 人工确认的外发 | 中 | 有确认环节但仍有泄露风险 |

高危动作项记入 `risk_items`，risk_type 为 `HIGH_RISK_ACTION`。

### 步骤 7：审计能力检查

检查 Skill 是否记录以下审计要素：

| 审计要素 | 必要性 | 缺失风险 |
|---------|--------|----------|
| 操作人 | 必要 | 高 |
| 操作时间 | 必要 | 高 |
| 输入摘要 | 推荐 | 中 |
| 输出摘要 | 推荐 | 中 |
| 权限变更记录 | 必要 | 高 |

无审计日志的写入类 Skill 至少中风险。缺失项记入 `risk_items`，risk_type 为 `AUDIT_MISSING`。

### 步骤 8：风险分级与整改建议

1. 汇总所有 `risk_items`，按高风险项数量确定整体 `risk_level`：
   - 0 个高风险 → low
   - 1-2 个高风险 → medium
   - 3+ 个高风险 → high
2. 生成 `permission_reduction_suggestions`：每个越权权限的收敛方案
3. 生成 `required_human_confirmations`：必须人工确认的动作
4. 生成 `audit_requirements`：审计补全建议
5. 生成 `next_actions`：可执行的下一步操作

## 四、标准输出结构

```json
{
  "status": "success | partial | error",
  "risk_level": "low | medium | high",
  "risk_items": [
    {
      "risk_type": "PERMISSION_OVERSCOPE | DATA_SCOPE_OVERSCOPE | SENSITIVE_FIELD_EXPOSURE | HIGH_RISK_ACTION | AUDIT_MISSING | ENCODING_NONSTANDARD",
      "description": "具体风险描述",
      "evidence": "触发该风险的输入依据",
      "recommendation": "可执行的整改建议"
    }
  ],
  "permission_reduction_suggestions": ["权限收敛方案1", "权限收敛方案2"],
  "required_human_confirmations": ["需人工确认项1", "需人工确认项2"],
  "audit_requirements": ["审计补全建议1", "审计补全建议2"],
  "missing_fields": ["缺失字段1", "缺失字段2"],
  "confidence": 0.0,
  "source": "Security-Guard v1.0",
  "next_actions": ["下一步操作1", "下一步操作2"]
}
```

**字段说明**：
- `status`：success=检查完成无缺失，partial=检查完成但有字段缺失，error=输入无法检查
- `risk_level`：整体风险等级
- `confidence`：检查结果置信度（0-1），受缺失字段影响
- `missing_fields`：未提供的输入字段
- `next_actions`：建议用户立即执行的整改操作

## 五、风险规则

详细规则与判断逻辑见 [references/risk_rules.md](references/risk_rules.md)。核心规则摘要：

| 规则编号 | 规则内容 | 默认风险等级 |
|---------|---------|-------------|
| R01 | 只读报表类 Skill 不应申请写入或删除权限 | 高 |
| R02 | 内部问答类 Skill 不应读取全量业务明细 | 高 |
| R03 | 自动外发消息必须人工确认 | 高 |
| R04 | 删除、批量更新、敏感字段导出 | 高 |
| R05 | 知识库问答不得跨知识库越权检索 | 高 |
| R06 | 没有审计日志的写入类 Skill | 中 |
| R07 | 明文输出手机号、证件号、办公地址/项目地址 | 高 |

## 六、异常处理

| 异常场景 | 处理方式 | 输出变更 |
|---------|---------|---------|
| skill_config 为空 | 立即终止，返回 error | status=error, missing_fields=["skill_config"] |
| permission_list 为空 | 继续检查但标记缺失 | status=partial, missing_fields=["permission_list"] |
| 权限编码不规范 | 记入 risk_items 并尝试推断 | risk_type=ENCODING_NONSTANDARD |
| data_scope 未说明 | 默认"未声明"，标记中风险 | risk_type=DATA_SCOPE_OVERSCOPE |
| sensitive_fields 未声明 | 提示建议声明，降低 confidence | confidence 扣 0.1 |
| 无法判断业务必要性 | 标记 required_human_confirmations | 新增"需人工复核XXX权限" |

## 七、安全要求

> **本 Skill 自身必须只读，不得修改被检查对象。**

1. 检查过程不写入任何外部系统
2. 只输出检查结果和整改建议，不自动变更权限
3. 所有检查过程必须记录审计摘要（操作人、时间、被检查 Skill 名称、检查结果摘要）
4. 演示数据必须脱敏，禁止使用真实业务信息
5. 遵循最小权限原则：本 Skill 自身仅需读取权限

## 八、央国企特色

### SOE-Unique Security Requirements

本Skill直接解决央国企安全管控中的独有需求：

| SOE安全需求 | 本Skill对应能力 | 检查维度 |
|------------|---------------|---------|
| 最小权限原则 | 权限解析+越界检测 | 步骤3：只读报表类不应有write/delete |
| 数据分级分类 | 敏感字段检查+脱敏要求 | 步骤5：手机号/证件号/金额分级管理 |
| 穿透式监管 | 审计能力检查 | 步骤7：无审计日志的写入类Skill不可上线 |
| 两人会签 | 高危动作检查 | 步骤6：删除/批量写入需双人确认 |
| 首席合规官审核 | 权限分级映射 | 高危权限自动触发合规官审批流程 |
| 信创适配 | 权限编码规范性 | 步骤1：权限编码需符合统一规范 |

### SOE Data Classification Enhancement

央国企数据分级分类标准（参考GB/T 35273）：

| 数据级别 | 示例 | 脱敏要求 | 访问控制 |
|---------|------|---------|---------|
| 公开 | 公司简介、公开制度 | 无需脱敏 | L1即可 |
| 内部 | 内部通知、部门数据 | 部分脱敏 | L2+ |
| 敏感 | 客户信息、经营数据 | 强制脱敏 | L3+ |
| 机密 | 战略规划、核心数据 | 禁止明文输出 | L4+双人 |
| 绝密 | 国家秘密相关 | 禁止AI处理 | L5禁止上线 |

### SOE Permission Coding Standard

央国企Skill权限编码规范（扩展版）：

| 操作类型 | 编码前缀 | 示例 | SOE管控要求 |
|---------|---------|------|-----------|
| read: | 数据查询 | read:business_full | 全量读取需L3+审批 |
| write: | 数据写入 | write:business_record | 写入需审计日志 |
| delete: | 数据删除 | delete:archive | 删除需双人确认+合规官审批 |
| send:  | 消息外发 | send:external_message | 外发需内容审查+人工确认 |
| call:  | 接口调用 | call:api_internal | 跨系统调用需网络安全审核 |
| export: | 数据导出 | export:sensitive_data | 导出需范围限制+脱敏处理 |
| admin: | 系统管理 | admin:config_modify | 系统配置修改需L4+审批 |

## 九、演示数据与课堂材料

- **演示数据**：见 [references/demo_data.md](references/demo_data.md) — 包含"权限过大"的 Skill 配置示例及检查结果
- **课堂演示脚本**：见 [references/demo_script.md](references/demo_script.md) — 3 分钟演示流程
- **学员操作指南**：见 [references/student_guide.md](references/student_guide.md) — 7 步实操指引
- **自查清单**：见 [references/checklist.md](references/checklist.md) — 交付/复用/上线测试检查项
