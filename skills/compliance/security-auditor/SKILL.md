---
name: security-auditor
name_cn: 安全审计组件
version: 1.0.0
domain: compliance
soe_relevance: 5
description: >
  Automated security audit component for Skills. Performs permission grading, static security scanning,
  and outputs D-A security ratings with convergence plans. 4-Phase pipeline (Info-Extractor →
  Security-Guard → Data-Analyst → Report-Generator). Mandatory for SOE Skill pre-deployment audit.
description_cn: >
  Skill安全审计组件，权限分级评估+静态安全扫描，输出D-A级安全评级和权限收敛方案。
  4-Phase流水线自动化审计，央国企Skill上线前强制审计组件。
---

# Security-Auditor 安全审计组件

## 核心理念

不是手动检查，而是自动化安全审计——普通安全是"人眼找漏洞"，高级安全是"AI自动扫描、自动分级、自动出整改方案"。

## 输入参数

### 必须参数

1. **skill_config**（JSON对象）：待审计的Skill配置，必须包含 `name`、`permissions`、`data_scope`、`operations`
   ```json
   {"name":"business_query_skill","permissions":["read_input","write_result","delete_file","export_all","read_all_business_data"],"data_scope":"全量业务数据","operations":["查询","修改","删除","导出"]}
   ```
2. **audit_mode**（枚举）：`permission_only`（仅权限审计）/ `full_scan`（全量扫描含静态），默认 `full_scan`

### 可选参数

3. **expected_usage**（字符串）：该Skill的预期用途描述
4. **compliance_standard**（枚举）：`soe_basic` / `soe_enhanced`，默认 `soe_basic`
5. **output_format**（枚举）：`markdown` / `json` / `table`，默认 `markdown`

## 4-Phase强制编排协议

本Skill必须通过 `phase-orchestrator` 执行4-Phase流水线，每个Phase由独立sub-Agent执行，Phase间通过结构化JSON传递数据。**禁止LLM模拟各阶段任务，必须真正调用对应技能组件。**

### Phase编排

| Phase | 组件 | 加载方式 | 输入 | 输出key |
|---|---|---|---|---|
| 1 | Info-Extractor 信息提取 | `skill(name="info-extractor")` | skill_config | extraction_result |
| 2 | Security-Guard 安全评估 | `skill(name="security-guard")` | Phase 1输出 | security_assessment |
| 3 | Data-Analyst 数据分析 | `skill(name="data-analyst")` | Phase 2输出 | analysis_result |
| 4 | Report-Generator 报告生成 | `skill(name="report-generator")` + `skill(name="archive-manager")` | Phase 2+3输出 | audit_report |

### 执行流程

1. 读取 `references/pipeline-phases.md` 中各Phase的prompt模板
2. 替换占位符为实际输入参数
3. 调用 `skill(name="phase-orchestrator")` 启动流水线
4. 每个Phase通过 `task` 工具启动独立sub-Agent执行
5. sub-Agent内通过 `skill` 工具加载对应组件，执行prompt
6. 收集各Phase的JSON输出传递给下一Phase

### Phase输出契约

**Phase 1 extraction_result**：
```json
{"status":"success|error","skill_name":"string","permissions":["string"],"data_scope":"string","operations":["string"],"field_access":["string"],"defense_rules":["string"],"expected_usage":"string|null"}
```

**Phase 2 security_assessment**：
```json
{"status":"success|error","permission_risks":[{"permission":"string","risk_level":"L1|L2|L3|L4|L5","over_necessary":true|false,"reason":"string"}],"static_scan":[{"check_item":"string","passed":true|false,"detail":"string"}],"critical_issues":["string"]}
```

**Phase 3 analysis_result**：
```json
{"status":"success|error","security_rating":"A|B|C|D|F","issues_count":0,"convergence_plan":[{"permission":"string","before":"string","after":"string","reason":"string"}],"verification_cases":[{"test":"string","expected_result":"成功|拒绝|弹出确认"}]}
```

**Phase 4 audit_report**：
```json
{"status":"success|error","report_content":"markdown","archive_id":"string","summary":{"rating":"string","issues":0,"recommendation":"string"}}
```

## 权限分级模型

| 等级 | 名称 | 图标 | 定义 |
|---|---|---|---|
| L1 | 查询级 | 🟢 | 只读公开知识 |
| L2 | 内部级 | 🟡 | 查询内部资料但需脱敏 |
| L3 | 操作级 | 🟠 | 可生成操作建议但不执行 |
| L4 | 执行级 | 🔴 | 需人工确认后执行 |
| L5 | 高危级 | ⚫ | 默认禁止或强审批 |

## 安全评级规则

| 评级 | 图标 | 条件 |
|---|---|---|
| A级 | 🟢 | 0个问题 |
| B级 | 🟡 | 1-2个低风险问题 |
| C级 | 🟠 | 3-4个中风险问题，或1个高危权限越级 |
| D级 | 🔴 | 5+个问题，或存在L5高危权限未审批 |
| F级 | ⚫ | L5高危权限+多字段全开，禁止上线 |

**覆盖规则**：发现L5高危权限时，评级最高D级。

## 降级策略

遵循phase-orchestrator的统一降级规则：

- `task`工具调用失败 → 由当前Agent直接执行该Phase的prompt
- sub-Agent返回非JSON → 重试1次追加"请严格按JSON格式输出"
- 连续2个Phase降级 → 后续Phase全部由当前Agent执行
- 每次降级在 `fallback_used` 中记录

## 标准输出格式

审计报告必须包含以下6个模块：

1. **审计基本信息**：审计对象名称、审计时间、审计工具版本、审计模式
2. **权限分级表**：每个权限项用🟢🟡🟠🔴⚫图标标注等级，标注是否超出必要范围
3. **静态扫描结果表**（full_scan模式）：5项检查✓通过/❌失败
4. **安全评级**：大号显示评级配图标和一句话诊断
5. **权限收敛方案**：修改前→修改后对照表+3条验证用例
6. **阶段溯源**：展示4个Phase的执行状态（✓独立Agent执行 / ⚠️降级执行）

## 异常处理

| 场景 | 处理 |
|---|---|
| skill_config缺少permissions | 报错"无法审计：缺少permissions字段" |
| expected_usage为空 | 所有权限标注"⚠️ 未提供预期用途，无法判断必要性" |
| audit_mode=permission_only | Phase 2跳过静态扫描，报告中标注"仅权限审计" |
| 所有权限L1且全✓ | 评级A级，标注"恭喜，该Skill安全配置良好" |
| 发现L5高危权限 | 无论其他项如何，评级最高D级 |

## 安全要求

- 审计报告不得泄露被审计Skill的完整配置内容，仅展示权限名称和风险等级
- D级和F级自动触发告警，归档标注"需整改后重新审计"
- 权限收敛方案不得包含"保持现状"选项
- 审计记录不可篡改，仅可追加

## 央国企特色

### SOE-Unique Audit Requirements

本Skill直接解决央国企安全审计中的独有需求：

| SOE审计需求 | 本Skill对应能力 | 对应Phase |
|------------|---------------|----------|
| 最小权限原则审计 | 权限分级评估+越级检测 | Phase 2: Security-Guard |
| 数据分级分类合规 | `soe_basic`/`soe_enhanced` 合规标准 | Phase 2: compliance_standard |
| 穿透式监管要求 | 4-Phase全链路溯源 | Phase 1-4: 端到端审计链 |
| Skill上线审批 | D-A评级作为上线门禁 | Phase 3: 评级结果 |
| 权限收敛闭环 | 收敛方案+验证用例 | Phase 3: convergence_plan |
| 审计报告归档 | 自动归档至审计记录库 | Phase 4: Archive-Manager |
| 首席合规官审核 | F/D级自动告警 | Phase 4: 告警+标注 |

### SOE Compliance Standards

| 合规标准 | 对应参数值 | 检查范围 |
|---------|----------|---------|
| soe_basic | 默认 | 权限分级+数据范围+敏感字段 |
| soe_enhanced | 高安全等级 | +审计日志+外发检测+信创适配+国产模型合规 |

### SOE Security Rating Governance

| 评级 | 上线许可 | SOE处置要求 |
|-----|---------|-----------|
| A 🟢 | 可直接上线 | 季度复查 |
| B 🟡 | 可上线 | 补充轻微项，月度复查 |
| C 🟠 | 需整改 | 整改后重新审计，不可上线 |
| D 🔴 | 禁止上线 | 需权限收敛方案+安全评审会 |
| F ⚫ | 禁止上线 | 需全面重构+安全评审会+合规官签审 |

## 脱敏演示数据

"有毒Skill"完整审计示例：

```json
{
  "name": "business_query_skill",
  "permissions": ["read_input", "write_result", "delete_file", "export_all", "read_all_business_data"],
  "data_scope": "全量业务数据",
  "operations": ["查询", "修改", "删除", "导出"],
  "expected_usage": "查询本人负责的业务记录信息"
}
```

**预期审计结果**：F级⚫禁止上线

**权限收敛方案**：
- [全量业务数据] → [仅本人负责业务数据]
- [delete_file] → [移除]
- [export_all] → [需二次确认+范围限制]
- [write_result] → [仅备注字段]

**验证用例**：
1. 查询本人业务 → 成功
2. 查询非本人业务 → 拒绝
3. 导出 → 弹出确认

## 课堂脚本

1. **开场话术**："不是手动检查，而是自动化安全审计——普通安全是'人眼找漏洞'，高级安全是'AI自动扫描、自动分级、自动出整改方案'"
2. **演示步骤**：
   - 输入"有毒Skill"配置 → 启动4-Phase流水线
   - 观察Phase 1 Info-Extractor提取权限列表
   - Phase 2 Security-Guard评估5个权限的风险等级+5项静态扫描
   - Phase 3 Data-Analyst计算F级评级+生成收敛方案
   - Phase 4 Report-Generator输出完整报告+归档
3. **技术爆点**："4个Phase是4个独立Agent——提取、评估、分析、报告各司其职，不是一个人演4个角色，而是4个专家各干各的"
4. **互动提问**："如果我只删掉delete_file，其他不改，F级能升到几级？"

## Resources

### references/

- **pipeline-phases.md**：4-Phase流水线的prompt模板定义。执行时由本Skill读取模板→替换占位符→构造完整prompt→传给phase-orchestrator。每个Phase模板包含：Phase编号与目标、上游JSON输入、输出契约、加载的组件技能声明。
