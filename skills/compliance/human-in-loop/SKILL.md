---
name: human-in-loop
name_cn: 人在回路审批
version: 1.0.0
domain: compliance
soe_relevance: 5
description: >
  Human-in-the-loop approval component with L1-L5 risk grading. Automatically evaluates risk level,
  generates approval forms with risk alerts and content preview, requires human confirmation before
  executing high-risk operations. Full audit trail for compliance. Essential for SOE "三重一大"
  collective decision-making and approval workflows.
description_cn: >
  人在回路审批组件，L1-L5五级风险评估，高风险操作强制人工确认，执行全过程留痕归档。
  满足央国企三重一大集体决策、两人会签、审批留痕等刚性要求。
---

# Human-In-Loop 人在回路审批组件

核心理念：不是AI自由执行，而是人在回路——普通Skill直接操作，高级Skill先预览、再确认、后执行、全留痕。

## 编排架构

本组件**强制执行4 Phase组件编排**，每个Phase必须通过 `skill` 工具加载对应基础组件，按序执行，不可跳过、不可合并。

```
用户输入 → [Phase 1: Info-Extractor] → [Phase 2: Security-Guard] → 等待人工确认 → [Phase 3: Report-Generator] → [Phase 4: Archive-Manager] → 完成
```

详细编排协议见 [references/orchestration.md](references/orchestration.md)。

## 输入参数

### 必须参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `operation_type` | 枚举 | 操作类型：发送群消息/修改客户数据/删除业务记录/导出业务数据/发送外部邮件/执行系统命令 |
| `operation_target` | 字符串 | 操作目标，如"管理层通知群(12人)"、"Client-A的所有工单" |
| `operation_content` | 字符串 | 操作具体内容，如要发送的消息文本、要修改的数据内容 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `auto_risk_level` | 枚举 | auto | 风险等级：auto/L1/L2/L3/L4/L5，auto表示自动评估 |
| `requires_2fa` | 布尔 | false | 是否需要二次验证，L4+风险自动启用 |
| `timeout_minutes` | 数字 | 30 | 审批超时时间（分钟），超时自动取消 |

## Phase 1 - 操作解析

**强制加载组件**：`info-extractor`

**执行方式**：
1. 调用 `skill(name="info-extractor")` 加载信息提取组件
2. 构造 Info-Extractor 输入：
   - `input_content` = `operation_type` + `operation_target` + `operation_content` 拼接
   - `extract_schema` = `[{"name":"op_category","label":"操作类别","required":true},{"name":"scope","label":"影响范围","required":true},{"name":"keywords","label":"内容关键词","required":false},{"name":"has_sensitive","label":"是否含敏感信息","required":true}]`
   - `output_format` = `"json"`
3. 从 Info-Extractor 输出中提取4个字段值

**输出契约（Phase 1 → Phase 2）**：
```json
{
  "op_category": "发送群消息",
  "scope": {"type": "群组", "count": 12, "detail": "管理层通知群(12人)"},
  "keywords": ["业务风险预警", "年度经营数据", "回访"],
  "has_sensitive": true,
  "sensitive_types": ["客户经营数据", "交易金额"]
}
```

**降级策略**：Info-Extractor 加载失败 → 手动从输入参数提取上述5个字段，标记 `phase1_method: "manual_fallback"`

## Phase 2 - 风险评估与敏感内容识别

**强制加载组件**：`security-guard`

**执行方式**：
1. 调用 `skill(name="security-guard")` 加载安全权限组件
2. 构造 Security-Guard 输入：
   - `skill_config` = `{"name": operation_type, "type": infer_category(operation_type), "business_purpose": operation_target + operation_content}`
   - `permission_list` = 根据 `operation_type` 映射：发送群消息→`["msg:send"]`，修改客户数据→`["customer:edit"]`，删除业务记录→`["ticket:delete"]`，导出业务数据→`["customer:export"]`，发送外部邮件→`["mail:external"]`，执行系统命令→`["system:exec"]`
   - `data_scope` = 从 Phase 1 的 `scope.detail` 推断
   - `sensitive_fields` = 从 Phase 1 的 `sensitive_types` 映射
   - `action_list` = 根据 `operation_type` 推断
3. 根据 Security-Guard 输出确定风险等级（L1-L5映射规则见 [references/risk-rules.md](references/risk-rules.md)）
4. 同步扫描 `operation_content`，标注敏感内容 ⚠️

**输出契约（Phase 2 → Phase 3）**：
```json
{
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
  "requires_2fa": false
}
```

**风险等级映射**（Security-Guard 的 risk_level → L等级）：
- `low` + 只读 → L1 🟢
- `low` + 内部消息 → L2 🔵
- `medium` → L3 🟡
- `high` + 无删除/系统命令 → L4 🟠
- `high` + 删除/系统命令 → L5 🔴

**权限不足处理**：`permission_check.passed=false` → 直接拒绝，不进入 Phase 3，输出"当前用户无执行此操作的权限：缺少{missing}权限"

**降级策略**：Security-Guard 加载失败 → 根据 [references/risk-rules.md](references/risk-rules.md) 中的规则表手动评估，标记 `phase2_method: "manual_fallback"`

## 等待人工确认

**此步骤不加载组件，为交互中断点。**

输出审批单后暂停执行，等待用户选择确认选项：

| 风险等级 | 确认要求 |
|----------|----------|
| L1 🟢 | 直接执行，无需确认 |
| L2 🔵 | 直接执行，无需确认 |
| L3 🟡 | 建议确认，非强制 |
| L4 🟠 | **强制**人工确认；选择[1]时需额外输入 `CONFIRM` |
| L5 🔴 | **强制**人工确认 + `CONFIRM`；执行系统命令必须 `requires_2fa=true` |

4个确认选项：
1. 确认执行
2. 修改内容后执行
3. 降级执行（如群发改为私发）
4. 取消操作

**L4+ 禁止自动跳过确认步骤。**

## Phase 3 - 生成审批单

**强制加载组件**：`report-generator`

**执行方式**：
1. 调用 `skill(name="report-generator")` 加载报告生成组件
2. 构造 Report-Generator 输入：
   - `report_type` = `"customer_brief"`
   - `input_data` = Phase 1 输出 + Phase 2 输出的拼接 JSON
   - `audience` = `"操作审批人"`
   - `tone` = `"简洁"`
   - `template_style` = `"one_page"`
   - `max_length` = 500
   - `include_next_actions` = false
3. 在 Report-Generator 输出基础上，**覆盖格式**为标准审批单4区域

**审批单必须包含4个区域**：

```
╔══════════════════════════════════════════╗
║          操作审批单                       ║
╠══════════════════════════════════════════╣
║ 【操作信息】                              ║
║  类型：发送群消息                          ║
║  目标：管理层通知群(12人)                  ║
║  风险：🟠 L4 中高风险                      ║
╠══════════════════════════════════════════╣
║ 【内容预览】                              ║
║  ⚠️业务风险预警信息...                     ║
╠══════════════════════════════════════════╣
║ 【风险提示】                              ║
║  ⚠️ 该内容包含客户经营风险信息              ║
║  ⚠️ 发送范围：管理层通知群（12人）          ║
║  ⚠️ 请确认发送范围是否合规                  ║
╠══════════════════════════════════════════╣
║ 【确认选项】                              ║
║  [1] 确认执行                             ║
║  [2] 修改内容后执行                        ║
║  [3] 降级执行（如群发改为私发）             ║
║  [4] 取消操作                             ║
╚══════════════════════════════════════════╝
```

**降级策略**：Report-Generator 加载失败 → 直接按上方模板格式输出审批单，标记 `phase3_method: "manual_fallback"`

## Phase 4 - 执行与归档

**强制加载组件**：`archive-manager`

**执行方式**：
1. 调用 `skill(name="archive-manager")` 加载归档组件
2. 构造 Archive-Manager 输入：
   - `archive_content` = 完整审批链 JSON（包含 Phase 1-3 全部输出 + 用户选择项 + 执行结果）
   - `archive_type` = `"ticket"`
   - `write_target` = `"审批记录库"`
   - `metadata` = `{"operation": operation_type, "risk_level": risk_level, "operator": 用户身份, "log_id": "APR-YYYYMMDD-NNN"}`
   - `tags` = [operation_type, risk_level标签, "人在回路"]
   - `privacy_level` = L4+ → `"restricted"`，其他 → `"department_only"`
   - `require_confirm` = false（审批已是确认后的操作）
3. 从 Archive-Manager 输出获取归档编号

**归档记录必须包含**：
- 操作人（从用户信息获取）
- 审批时间
- 选择项（1/2/3/4）
- 执行结果（成功/已取消/已降级）
- 日志编号：格式 `APR-YYYYMMDD-NNN`

**归档时必须对敏感信息脱敏**（脱敏规则见 [references/risk-rules.md](references/risk-rules.md) 脱敏规则章节）。

**降级策略**：Archive-Manager 加载失败 → 将归档记录以 JSON 格式直接输出给用户，提示"归档组件不可用，请手动保存以下记录"，标记 `phase4_method: "manual_fallback"`

## 异常处理

| 异常场景 | 处理方式 |
|----------|----------|
| L5 + 执行系统命令 + requires_2fa=false | 拒绝执行："极高风险操作需启用二次验证" |
| 审批超时 | 自动取消，归档标注"超时自动取消" |
| 用户选择[4]取消 | 正常归档，标注"用户主动取消" |
| 用户选择[2]修改但未提供内容 | 提示"请提供修改后的内容，或选择其他选项" |
| 权限不足（Phase 2检测） | 直接拒绝，不进入后续Phase，输出"当前用户无执行此操作的权限：缺少XXX权限" |
| 模拟执行失败 | 归档标注"执行失败：原因"，不重试 |
| 24h内重复L4+操作 | 提示"24小时内已有相似操作审批记录" |
| 任何Phase组件加载失败 | 执行该Phase的降级策略，标记 `phaseN_method: "manual_fallback"` |

## 安全要求

- L4+ 操作必须经人工确认，禁止自动执行
- 审批单中敏感信息不脱敏（审批者需看完整内容），归档时必须脱敏
- 归档记录不可删除，仅可追加（append-only）
- 每条执行记录必须含日志编号，可追溯
- 审批超时取消也必须归档
- 组件编排为强制链式调用，不可跳过任何Phase

## 央国企特色

### SOE-Unique Approval Requirements

本Skill直接解决央国企审批流程中的独有需求：

| SOE审批需求 | 本Skill对应能力 | 实现方式 |
|------------|---------------|---------|
| 三重一大集体决策 | L4+强制人工确认 | 重大决策操作自动升级为L4+，需多人确认 |
| 两人会签制度 | `requires_dual_sign=True` | Phase 1-2自动识别会签场景，Phase 3审批单包含双签区域 |
| 党委前置审议 | 操作类型扩展 | 新增"党委审议"操作类型，自动触发前置流程 |
| 13710督办制度 | 审批超时处理 | 超时自动取消+归档+催办提醒，支持督办编号 |
| 穿透式监管 | 全链路归档 | Phase 4记录完整审批链，支持从结果穿透至发起人 |
| 首席合规官审核 | L5级二次验证 | 极高风险操作自动要求合规官签审 |

### 风险等级与央国企管控对应

| 本Skill等级 | 央国企管控对应 | 典型场景 |
|------------|-------------|---------|
| L1 🟢 询问级 | 日常查询，无需审批 | 查询公开制度、查询内部通讯录 |
| L2 🔵 通知级 | 一般通知，事后备案 | 部门工作群消息、例会通知 |
| L3 🟡 操作级 | 部门负责人审批 | 修改客户信息、导出业务数据 |
| L4 🟠 执行级 | 分管领导审批+两人会签 | 批量数据操作、跨部门信息共享 |
| L5 🔴 高危级 | 主要领导审批+合规官会签 | 系统命令执行、全量数据导出、删除归档记录 |

### SOE操作类型扩展

在标准6种操作类型基础上，央国企场景新增：
- **党委审议**：触发党委前置流程，自动升级为L4+
- **督办事项**：13710制度下的限时督办，超时自动升级
- **巡视整改**：巡视发现问题整改操作，自动归档至专项记录
- **三重一大**：重大决策/重要人事/重大项目/大额资金，强制集体决策+多人会签

## 演示与教学

详见 [references/demo-and-classroom.md](references/demo-and-classroom.md)，包含：
- 完整审批流程示例（脱敏数据）
- 课堂脚本（4步演示）
- 学员指南（5个实验）
- 自查清单（8项）
