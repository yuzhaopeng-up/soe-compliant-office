---
name: evidence-chain
name_cn: 多源证据链分析
version: 1.0.0
domain: compliance
soe_relevance: 5
description: >
  Multi-source evidence chain analysis with cross-validation, conflict detection, confidence scoring,
  and root cause inference. 4-Phase pipeline (Info-Extractor → Data-Analyst → Report-Generator →
  Archive-Manager). Essential for SOE complaint investigation, regulatory inspection response,
  and compliance evidence gathering.
description_cn: >
  多源证据链分析组件，交叉验证、冲突检测、置信度评估与根因推断。4-Phase流水线自动化分析，
  央国企投诉核查、巡视整改、合规证据链等场景的核心能力。
---

# Evidence-Chain 多源证据链分析组件

核心理念：**不是单RAG从知识库回答，而是多源证据链——普通RAG从知识库回答，高级Skill从多个来源交叉验证，识别冲突，评估置信度。**

## 组件编排

本 Skill 由4个组件串联执行，**必须严格按序调用**，前一阶段的输出是下一阶段的输入：

```
Info-Extractor ──→ Data-Analyst ──→ Report-Generator ──→ Archive-Manager
   Phase 1            Phase 2            Phase 3              Phase 4
  证据提取         交叉验证+推断        生成报告             归档留痕
```

**执行规则**：
- 每个组件必须通过 `skill` 工具加载对应技能后执行，禁止跳过或合并
- 组件间通过结构化 JSON 对象传递中间结果（见下方各 Phase 的输出契约）
- 任意组件加载失败时，执行降级策略（见"异常处理"）

详细编排协议见 [references/orchestration.md](references/orchestration.md)。

## 输入参数

### 必须

| 参数 | 类型 | 说明 |
|------|------|------|
| `evidence_sources` | JSON数组 | 每个元素含 `source_name`、`source_type`、`content` |
| `analysis_question` | 字符串 | 核心问题，如"核心业务系统是否存在服务质量问题" |

`source_type` 枚举：`投诉记录` / `告警日志` / `合同条款` / `运维记录` / `其他`

### 可选

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `conflict_sensitivity` | 枚举 | `medium` | `high`/`medium`/`low` |
| `confidence_threshold` | 0-1 | `0.7` | 低于此值的根因标注"⚠️ 待进一步验证" |
| `output_format` | 枚举 | `markdown` | `markdown` / `json` / `table` |

## Phase 1 — Info-Extractor 证据提取

**调用方式**：通过 `skill` 工具加载 `info-extractor` 技能，对每个来源执行提取

**输入**：`evidence_sources` 中的每个元素

**处理**：
1. 遍历 `evidence_sources`，对每个来源调用 Info-Extractor
2. 提取结构化字段：时间、事件、数值、对象、地点等
3. 对每条证据标注来源类型和初始置信度

| 来源类型 | 初始置信度 | 属性 |
|----------|-----------|------|
| 投诉记录 | ⭐⭐ (0.4) | 主观陈述 |
| 告警日志 | ⭐⭐⭐⭐ (0.8) | 客观数据 |
| 合同条款 | ⭐⭐⭐ (0.6) | 权威参照 |
| 运维记录 | ⭐⭐⭐⭐ (0.8) | 客观数据 |
| 其他 | ⭐⭐⭐ (0.6) | 待评估 |

**Phase 1 输出契约**（传递给 Phase 2）：

```json
{
  "extracted_evidences": [
    {
      "evidence_id": "E-01",
      "source_name": "来源名称",
      "source_type": "投诉记录",
      "extracted_fields": { "time": "...", "event": "...", "value": "..." },
      "initial_confidence": 0.4,
      "raw_summary": "一句话摘要"
    }
  ]
}
```

## Phase 2 — Data-Analyst 交叉验证与推断

**调用方式**：通过 `skill` 工具加载 `data-analyst` 技能，将 Phase 1 输出作为分析输入，按以下子步骤执行交叉验证与推断

**输入**：Phase 1 的 `output_phase1` 对象

**子步骤**：

### 2a - 时间线对齐
- 将 `extracted_evidences` 按时间排序
- 识别同一事件的多个来源记录，标注时间差
- 输出：`timeline_events` 数组

### 2b - 冲突检测
- 比对同一事件不同来源的描述
- 按 `conflict_sensitivity` 调整检测粒度
- 每条冲突标注：冲突ID、类型、描述、涉及来源、差异分析
- 冲突检测规则详见 [references/conflict-rules.md](references/conflict-rules.md)

### 2c - 置信度评估
- 公式：`综合置信度 = 来源置信度 × 跨源验证度 × 时效性衰减`
  - 跨源验证度：独立来源验证同一事实的比例（0-1）
  - 时效性衰减：超过30天按 0.95^月数 衰减

### 2d - 根因推断
- 三个维度：**时间最早** / **下游依赖** / **高频出现**
- 输出：疑似根因 + 置信度（高/中/低）+ 数值 + 判断依据
- 低于 `confidence_threshold` 标注 "⚠️ 待进一步验证"

**Phase 2 输出契约**（传递给 Phase 3）：

```json
{
  "timeline_events": [...],
  "conflicts": [
    {
      "conflict_id": "C-01",
      "type": "数值冲突",
      "description": "...",
      "sources_involved": ["E-01", "E-03"],
      "difference": "差值=1次",
      "possible_reason": "..."
    }
  ],
  "confidence_scores": [
    { "evidence_id": "E-01", "source_confidence": 0.4, "cross_validation": 0.7, "time_decay": 1.0, "final_confidence": 0.28 }
  ],
  "root_cause": {
    "suspected": "...",
    "confidence_level": "高",
    "confidence_value": 0.85,
    "basis": ["时间最早", "下游依赖", "高频出现"],
    "needs_further_verification": false
  },
  "recommended_actions": [
    { "priority": "🔴优先", "action": "...", "linked_evidence": ["E-04"] },
    { "priority": "🟡同时", "action": "...", "linked_evidence": ["E-01","E-05"] }
  ]
}
```

## Phase 3 — Report-Generator 生成报告

**调用方式**：通过 `skill` 工具加载 `report-generator` 技能，将 Phase 2 分析结果按模板生成报告

**输入**：Phase 2 的 `output_phase2` 对象 + Phase 1 的 `output_phase1` 对象

**输出格式**：按 `output_format` 参数选择

### 模块1：证据清单表格
| # | 来源 | 来源类型 | 时间 | 关键内容 | 置信度 |
|---|------|---------|------|---------|--------|

### 模块2：冲突检测区
每条冲突：冲突ID + 类型 + 描述 + 涉及来源 + 差异分析

### 模块3：根因判断
疑似根因 + 置信度（高/中/低）+ 数值 + 判断依据 + ⚠️标记（如适用）

### 模块4：建议动作
| 优先级 | 建议动作 | 关联证据 |
|--------|---------|---------|
| 🔴 优先 | ... | 证据#n |
| 🟡 同时 | ... | 证据#n |
| 🟢 暂缓 | ... | 证据#n |

### 模块5：元数据
分析时间 / 证据数量 / 冲突数量 / 最高置信度

**Phase 3 输出契约**（传递给 Phase 4）：

```json
{
  "report_content": "完整报告文本（markdown/json/table）",
  "report_metadata": {
    "analysis_time": "2026-06-20T...",
    "evidence_count": 7,
    "conflict_count": 2,
    "max_confidence": 0.85
  }
}
```

## Phase 4 — Archive-Manager 归档

**调用方式**：通过 `skill` 工具加载 `archive-manager` 技能执行归档

**输入**：Phase 3 的 `output_phase3` 对象

**归档内容**：
- 分析过程：Phase 1 提取结果 + Phase 2 分析结果
- 分析结论：Phase 3 完整报告
- 归档元数据：分析人、分析时间、证据来源清单

**归档前必须脱敏**：
- 相关方名称 → "Client-A"
- 合同编号保留、具体金额 → 保留编号但隐藏金额细节

## 组件加载失败降级策略

| 组件 | 加载失败时降级方案 |
|------|------------------|
| Info-Extractor | 手动按来源类型提取结构化字段，标注初始置信度 |
| Data-Analyst | 按 SKILL.md 中 Phase 2 的子步骤手动执行分析（时间线对齐/冲突检测/置信度评估/根因推断） |
| Report-Generator | 按 SKILL.md 中 Phase 3 的5模块模板手动生成报告 |
| Archive-Manager | 将归档内容保存为本地 `.md` 文件，文件名含时间戳和分析问题 |

**降级时必须在报告元数据中标注**：`"degraded": true, "degraded_components": ["info-extractor"]`

## 异常处理

| 条件 | 行为 |
|------|------|
| 来源数 = 0 | 报错："至少需要2个证据来源才能进行交叉验证" |
| 来源数 = 1 | 降级为单源分析 + 警告："仅1个来源，无法交叉验证，结论置信度受限" |
| 所有证据无时间信息 | 跳过Phase 2a + 报告标注"缺少时间维度，无法进行时序分析" |
| sensitivity=high 但无冲突 | 输出"未检测到冲突，各来源描述一致" |
| 根因置信度 < threshold | 标注 "⚠️ 待进一步验证" + 列出需补充的证据 |

## 安全要求

- 相关方投诉内容**不得脱敏处理前**归档到公开知识库
- 合同条款属商业机密，归档时**必须脱敏**
- 根因判断**必须标注置信度**，禁止以低置信度结论作为操作依据
- 所有归档记录**必须包含**：分析人、分析时间、证据来源清单

## 央国企特色

### SOE-Unique Evidence Chain Requirements

本Skill直接解决央国企证据链分析中的独有需求：

| SOE证据链需求 | 本Skill对应能力 | 实现方式 |
|-------------|---------------|---------|
| 巡视整改证据链 | 多源交叉验证 | 投诉/告警/合同/运维四源交叉，还原事件全貌 |
| 穿透式监管响应 | 全链路可追溯 | Phase 1-4端到端记录，支持从结论回溯至原始证据 |
| 合规审查证据链 | 冲突检测+置信度 | 自动识别不同来源间的矛盾，标注数据可信度 |
| 投诉核查 | 多源对证 | 客诉陈述 vs 系统记录 vs 合同条款三方对证 |
| 故障定责 | 根因推断 | 时间线+下游依赖+高频出现三维推断 |
| 归档留痕 | 4-Phase归档 | 分析过程+结论+原始证据清单全量归档 |

### SOE Evidence Source Weighting

央国企场景下的证据来源权重调整：

| 来源类型 | 标准权重 | SOE调整后权重 | 调整原因 |
|---------|---------|-------------|---------|
| 投诉/信访记录 | 0.4 | 0.5 | SOE重视信访，需适当提升权重 |
| 告警/监控日志 | 0.8 | 0.9 | 客观数据在SOE审计中权重更高 |
| 合同/制度条款 | 0.6 | 0.8 | 制度文件在SOE合规判定中为权威依据 |
| 运维/操作记录 | 0.8 | 0.85 | 操作留痕在SOE审计中为核心证据 |
| 会议纪要 | 0.5 | 0.7 | SOE决策记录（含三重一大）具有法律效力 |

### SOE Conflict Sensitivity Levels

| 敏感度 | 适用场景 | 检测粒度 |
|-------|---------|---------|
| high | 巡视整改、合规审查 | 数值偏差>5%即标记冲突 |
| medium | 日常投诉核查 | 数值偏差>10%标记冲突 |
| low | 常规业务分析 | 仅标记方向性矛盾 |

## 演示数据

完整的3源证据链示例见 [references/demo-data.md](references/demo-data.md)。

## 学员指南

- 修改 `evidence_sources` 中的内容，尝试制造不同冲突
- 调整 `conflict_sensitivity`，观察对冲突检测结果的影响
- 尝试2源 vs 3源，观察交叉验证能力差异
- 尝试把证据时间改掉，观察时序分析效果

## 自查清单

- [ ] 能否正确从3个不同类型来源提取结构化字段
- [ ] 能否检测到相关方陈述与系统记录的冲突
- [ ] 能否给出带置信度的根因判断
- [ ] 能否区分🔴优先/🟡同时/🟢暂缓的建议动作
- [ ] 脱敏数据是否正确隐藏了相关方名称
- [ ] 归档记录是否包含完整的证据来源清单
