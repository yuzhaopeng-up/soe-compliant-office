# 组件编排协议

本文件定义 Human-In-Loop 组件的4 Phase强制链式编排协议，确保每次执行都严格通过 `skill` 工具加载基础组件，而非由 LLM 自行模拟。

## 编排总览

```
[Phase 1] ──→ [Phase 2] ──→ [中断点: 人工确认] ──→ [Phase 3] ──→ [Phase 4]
Info-Extractor  Security-Guard                         Report-Generator  Archive-Manager
```

**强制规则**：
1. 每个 Phase 必须通过 `skill(name="<组件名>")` 加载对应组件
2. 上一个 Phase 的输出是下一个 Phase 的输入，不可跳过
3. 任何 Phase 组件加载失败时执行降级策略，但流程不中断
4. 降级执行标记 `phaseN_method: "manual_fallback"` 写入归档记录

---

## Phase 1: 操作解析

### 加载组件

```
skill(name="info-extractor")
```

### 输入构造

将用户输入的3个必须参数转为 Info-Extractor 的标准输入：

```json
{
  "input_content": "操作类型：{operation_type}\n操作目标：{operation_target}\n操作内容：{operation_content}",
  "extract_schema": [
    {"name": "op_category", "label": "操作类别", "required": true},
    {"name": "scope", "label": "影响范围", "required": true},
    {"name": "keywords", "label": "内容关键词", "required": false},
    {"name": "has_sensitive", "label": "是否含敏感信息", "required": true}
  ],
  "output_format": "json"
}
```

### 输出规范

从 Info-Extractor 返回的 `data` 中提取：

| 字段 | 来源路径 | 说明 |
|------|----------|------|
| `op_category` | `data.op_category.value` | 操作类别 |
| `scope` | `data.scope.value` | 影响范围（需解析为 {type, count, detail}） |
| `keywords` | `data.keywords.value` | 内容关键词列表 |
| `has_sensitive` | `data.has_sensitive.value` | 布尔值 |
| `sensitive_types` | 推断 | 从 keywords 和 content 推断敏感类型 |

### 降级策略

Info-Extractor 加载失败时：
1. 从 `operation_type` 直接取 `op_category`
2. 从 `operation_target` 解析 `scope`（正则匹配数字计数）
3. 从 `operation_content` 提取前5个实词作为 `keywords`
4. 根据关键词特征判断 `has_sensitive`
5. 标记 `"phase1_method": "manual_fallback"`

### 传递给 Phase 2 的数据

```json
{
  "phase1_output": {
    "op_category": "发送群消息",
    "scope": {"type": "群组", "count": 12, "detail": "管理层通知群(12人)"},
    "keywords": ["业务风险预警", "年度经营数据", "回访"],
    "has_sensitive": true,
    "sensitive_types": ["客户经营数据", "交易金额"],
    "phase1_method": "skill" 
  }
}
```

---

## Phase 2: 风险评估与敏感内容识别

### 加载组件

```
skill(name="security-guard")
```

### 输入构造

将 Phase 1 输出转为 Security-Guard 的标准输入：

```json
{
  "skill_config": {
    "name": "{operation_type}",
    "type": "{infer_category(operation_type)}",
    "business_purpose": "{operation_target} - {operation_content}"
  },
  "permission_list": ["{map_permission(operation_type)}"],
  "data_scope": "{infer_scope(phase1_output.scope)}",
  "sensitive_fields": ["{map_sensitive(phase1_output.sensitive_types)}"],
  "action_list": ["{infer_actions(operation_type)}"]
}
```

**映射函数**：

`infer_category(operation_type)`:
| operation_type | → type |
|----------------|--------|
| 发送群消息 | communication |
| 修改客户数据 | dataModification |
| 删除业务记录 | dataDeletion |
| 导出业务数据 | dataExport |
| 发送外部邮件 | externalCommunication |
| 执行系统命令 | systemOperation |

`map_permission(operation_type)`:
| operation_type | → permission |
|----------------|-------------|
| 发送群消息 | msg:send |
| 修改客户数据 | customer:edit |
| 删除业务记录 | ticket:delete |
| 导出业务数据 | customer:export |
| 发送外部邮件 | mail:external |
| 执行系统命令 | system:exec |

`infer_scope(scope)`: count≤5 → "班组", count≤50 → "地市", count>50 → "全量客户"

`infer_actions(operation_type)`:
| operation_type | → actions |
|----------------|----------|
| 发送群消息 | ["外发"] |
| 修改客户数据 | ["写入"] |
| 删除业务记录 | ["删除"] |
| 导出业务数据 | ["读取","外发"] |
| 发送外部邮件 | ["外发"] |
| 执行系统命令 | ["写入","删除"] |

### 输出规范

从 Security-Guard 返回结果中提取：

| 字段 | 来源路径 | 说明 |
|------|----------|------|
| `risk_level` | 根据 `risk_items` 数量和类型映射 | L1-L5 |
| `risk_evidence` | `risk_items[].description` | 风险证据列表 |
| `permission_passed` | 无 `PERMISSION_OVERSCOPE` 类型 | 权限是否通过 |
| `permission_missing` | `risk_items` 中 `PERMISSION_OVERSCOPE` | 缺失权限 |

**风险等级映射**（Security-Guard risk_level → L等级）：

| Security-Guard risk_level | 条件 | → L等级 |
|---------------------------|------|---------|
| low | 只读/查询操作 | L1 🟢 |
| low | 内部消息通知 | L2 🔵 |
| medium | 无删除/系统命令 | L3 🟡 |
| high | 无删除/系统命令 | L4 🟠 |
| high | 含删除/系统命令 | L5 🔴 |
| — | operation_type=执行系统命令 | L5 🔴 (强制) |
| — | operation_type=删除业务记录 | L5 🔴 (强制) |

### 权限不足处理

`permission_passed=false` → **直接终止流程**，不进入 Phase 3：
输出：`"当前用户无执行此操作的权限：缺少{permission_missing}权限"`

### 敏感内容标注

同步扫描 `operation_content`，按以下规则标注 ⚠️：

| 模式 | 识别规则 | 标注 |
|------|----------|------|
| 客户经营信息 | "流失"/"预警"/"月均"/"营收"/"合同金额" | ⚠️ 客户经营信息 |
| 合同条款 | "合同编号"/"HT-"/"有效期"/"保密" | ⚠️ 合同条款 |
| 系统配置 | IP格式/端口号/"API"/"Token"/"密钥" | ⚠️ 系统配置参数 |
| 个人隐私 | 手机号/身份证号/银行卡号/邮箱 | ⚠️ 个人隐私数据 |

### 降级策略

Security-Guard 加载失败时：
1. 根据 `references/risk-rules.md` 中的规则表手动评估
2. 按操作类型确定基础等级
3. 按敏感内容和范围做升级判断
4. 标记 `"phase2_method": "manual_fallback"`

### 传递给 Phase 3 的数据

```json
{
  "phase2_output": {
    "risk_level": "L4",
    "risk_emoji": "🟠",
    "risk_label": "中高风险",
    "risk_evidence": ["内容包含客户经营风险信息", "群发目标12人(>5人)", "含客户月度交易金额"],
    "permission_check": {"passed": true, "missing": []},
    "sensitive_marks": [
      {"type": "客户经营信息", "content": "业务风险预警", "mark": "⚠️"},
      {"type": "交易金额", "content": "年度经营数据", "mark": "⚠️"}
    ],
    "requires_confirm": true,
    "requires_2fa": false,
    "phase2_method": "skill"
  }
}
```

---

## 中断点: 等待人工确认

**此步骤不加载组件，为交互中断点。**

### 确认规则

| 风险等级 | 行为 |
|----------|------|
| L1 🟢 | 直接执行，跳过确认 |
| L2 🔵 | 直接执行，跳过确认 |
| L3 🟡 | 输出审批单建议确认，非强制（可直接执行） |
| L4 🟠 | 输出审批单，**强制**确认；选择[1]时需输入 `CONFIRM` |
| L5 🔴 | 输出审批单，**强制**确认 + 输入 `CONFIRM`；执行系统命令需 `requires_2fa=true` |

### 用户选择项

1. **确认执行** — 按原操作执行
2. **修改内容后执行** — 用户提供修改后的 `operation_content`，回到 Phase 1 重新评估
3. **降级执行** — 按降级策略执行（见 references/risk-rules.md 降级执行策略）
4. **取消操作** — 终止流程，进入 Phase 4 归档"用户主动取消"

### 超时处理

用户在 `timeout_minutes` 内未响应 → 自动选择[4]取消操作

---

## Phase 3: 生成审批单

### 加载组件

```
skill(name="report-generator")
```

### 输入构造

将 Phase 1 + Phase 2 输出转为 Report-Generator 的标准输入：

```json
{
  "report_type": "customer_brief",
  "input_data": "{JSON.stringify(phase1_output + phase2_output + user_choice)}",
  "audience": "操作审批人",
  "tone": "简洁",
  "template_style": "one_page",
  "max_length": 500,
  "include_next_actions": false
}
```

### 输出规范（覆盖 Report-Generator 默认格式）

无论 Report-Generator 原始输出格式如何，**必须按审批单4区域格式输出**：

**区域1 - 操作信息**：
```
【操作信息】
 类型：{op_category}
 目标：{scope.detail}
 风险：{risk_emoji} {risk_level} {risk_label}
```

**区域2 - 内容预览**：
```
【内容预览】
 {operation_content，敏感位置插入⚠️标注}
```

**区域3 - 风险提示**：
```
【风险提示】
 ⚠️ {risk_evidence[0]}
 ⚠️ {risk_evidence[1]}
 ...
```

**区域4 - 确认选项**：
```
【确认选项】
 [1] 确认执行
 [2] 修改内容后执行
 [3] 降级执行（如群发改为私发）
 [4] 取消操作

 ⚠️ L4+中高风险操作，选择[1]确认执行需额外输入 CONFIRM
```

### 降级策略

Report-Generator 加载失败时：
1. 直接按4区域模板格式输出
2. 用 Phase 1 和 Phase 2 的输出数据填充模板
3. 标记 `"phase3_method": "manual_fallback"`

### 传递给 Phase 4 的数据

```json
{
  "phase3_output": {
    "approval_form": "完整审批单文本",
    "user_choice": {
      "option": 1,
      "confirmed": true,
      "confirm_text": "CONFIRM",
      "modified_content": null
    },
    "execution_result": "成功",
    "phase3_method": "skill"
  }
}
```

---

## Phase 4: 执行与归档

### 加载组件

```
skill(name="archive-manager")
```

### 输入构造

将 Phase 1-3 全部输出转为 Archive-Manager 的标准输入：

```json
{
  "archive_content": "{JSON.stringify(完整审批链)}",
  "archive_type": "ticket",
  "write_target": "审批记录库",
  "metadata": {
    "operation": "{operation_type}",
    "risk_level": "{risk_level}",
    "operator": "{用户身份}",
    "log_id": "APR-{YYYYMMDD}-{NNN}",
    "source": "Human-In-Loop"
  },
  "tags": ["{operation_type}", "{risk_level}标签", "人在回路"],
  "privacy_level": "{L4+ ? 'restricted' : 'department_only'}",
  "require_confirm": false,
  "retention_policy": "1y"
}
```

### 审批链内容（归档原文）

归档的 `archive_content` 必须包含完整审批链：

```json
{
  "operation": {
    "type": "发送群消息",
    "target": "管理层通知群(12人)",
    "content_original": "⚠️ 已脱敏，原文含客户经营信息"
  },
  "risk_assessment": {
    "level": "L4",
    "evidence": ["..."]
  },
  "approval": {
    "operator": "Contributor",
    "time": "2026-07-10T14:32:15Z",
    "choice": 1,
    "confirm_text": "CONFIRM"
  },
  "execution": {
    "result": "成功",
    "log_id": "APR-20260710-001"
  },
  "pipeline": {
    "phase1_method": "skill",
    "phase2_method": "skill",
    "phase3_method": "skill",
    "phase4_method": "skill"
  }
}
```

**归档脱敏规则**：

| 数据类型 | 脱敏方式 |
|----------|----------|
| 手机号 | 保留前3后4：138\*\*\*\*1234 |
| 身份证号 | 保留前3后4：360\*\*\*\*\*\*\*\*\*\*\*\*1234 |
| 合同金额 | 保留量级：XX万 → \*\*万 |
| 客户名称 | 保留行业：某制造企业 → 某制造企业 |
| 银行卡号 | 保留后4：\*\*\*\*1234 |

### 日志编号规则

格式：`APR-YYYYMMDD-NNN`
- APR：Approval Record（审批记录）
- YYYYMMDD：操作日期
- NNN：当日序号（从001递增）

### 降级策略

Archive-Manager 加载失败时：
1. 将归档记录以 JSON 格式直接输出给用户
2. 提示"归档组件不可用，请手动保存以下记录"
3. 标记 `"phase4_method": "manual_fallback"`

---

## 编排执行检查点

每个 Phase 执行后，检查以下条件决定是否继续：

| 检查点 | 条件 | 动作 |
|--------|------|------|
| Phase 1 完成 | `phase1_output.has_sensitive` 有值 | 继续 Phase 2 |
| Phase 2 权限 | `permission_check.passed = false` | **终止**，输出权限不足提示 |
| Phase 2 风险 | `risk_level = L5` 且 `operation_type = 执行系统命令` 且 `requires_2fa = false` | **终止**，提示需启用2FA |
| Phase 2 完成 | `risk_level` 和 `sensitive_marks` 有值 | 输出审批单，进入中断点 |
| 中断点 | 用户选择[4]取消 | 进入 Phase 4 归档"用户主动取消" |
| 中断点 | 用户选择[2]修改 | 回到 Phase 1 重新执行 |
| Phase 3 完成 | 审批单已输出 | 等待人工确认后再进入 Phase 4 |
| Phase 4 完成 | 归档记录已生成 | 流程结束 |
| 任何Phase加载失败 | `skill()` 调用异常 | 执行降级策略，标记 method |

## 全流程示例

见 [references/demo-and-classroom.md](references/demo-and-classroom.md) 中的完整审批流程示例。
