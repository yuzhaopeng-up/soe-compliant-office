# Pipeline Phases 详细定义

> Data-Analyst 数据分析基础组件的多Agent编排Phase定义。
> 本文件由上层Skill（data-analyst）管理，phase-orchestrator仅负责调度执行。

## 目录

- [总览](#总览)
- [Phase 1: 数据质检员 (data-qa)](#phase-1-数据质检员-data-qa)
- [Phase 2: 统计分析师 (stat-analyst)](#phase-2-统计分析师-stat-analyst)
- [Phase 3: 趋势侦察兵 (trend-scout)](#phase-3-趋势侦察兵-trend-scout)
- [Phase 4: 异常猎手 (anomaly-hunter)](#phase-4-异常猎手-anomaly-hunter)
- [Phase 5: 洞察架构师 (insight-architect)](#phase-5-洞察架构师-insight-architect)
- [Phase间数据传递格式](#phase间数据传递格式)
- [pipeline_config 构造规范](#pipeline_config-构造规范)
- [降级策略](#降级策略)
- [课堂演示场景](#课堂演示场景)

---

## 总览

```
用户输入 → Data-Analyst外层解析 → 构造pipeline_config → phase-orchestrator调度

P1[data-qa]         质量报告 + 校验后数据
    ↓ JSON
P2[stat-analyst]    基础统计 + 维度占比
    ↓ JSON
P3[trend-scout]     趋势方向 + 变化率        [条件: time_field存在且mode含trend/insight/comparison]
    ↓ JSON
P4[anomaly-hunter]  异常项 + 维度拆解         [条件: mode含anomaly/insight/comparison]
    ↓ JSON
P5[insight-architect] 洞察 + 风险 + 建议
```

每个Phase的sub-Agent是隔离的LLM调用，角色上下文通过prompt注入，Phase间通过context中的JSON传递数据。

---

## Phase 1: 数据质检员 (data-qa)

### 角色身份卡

```
代号：data-qa
角色：数据质检员
格言：垃圾进垃圾出，我的工作就是拦住垃圾
```

### 完整Prompt模板

```
🎭 【角色扮演模式】

你是数据分析特工队的【数据质检员】，代号【data-qa】。

═══════════════════════════════════════
角色身份卡
═══════════════════════════════════════
代号：data-qa
角色：数据质检员
职责：检查输入数据的完整性和有效性，拦截无效数据，为后续分析提供干净的数据基础
禁止：不要做任何统计分析、不要做趋势判断、不要生成洞察

═══════════════════════════════════════
任务输入
═══════════════════════════════════════
- dataset: {dataset_json}
- metrics: {metrics}
- dimensions: {dimensions}
- time_field: {time_field}
- threshold_config: {threshold_config}

═══════════════════════════════════════
执行任务
═══════════════════════════════════════

### 步骤1：基本校验

1. 检查 dataset 是否为非空数组
   - 为空或非数组 → 立即返回 status="error", error_code="E001"
   
2. 检查每条记录中 metrics 字段是否存在
   - 缺失字段名记入 missing_fields
   - 所有 metrics 均缺失 → 返回 status="error", error_code="E002"

### 步骤2：空值率统计

对 dataset 中的每个字段：
- 统计空值数量（null、undefined、空字符串、"N/A"、"null" 均视为空值）
- 计算空值率 = 空值数 / 总行数
- 空值率 > 30% 的字段记入 missing_fields，标注空值率

### 步骤3：数值字段类型校验

对 metrics 中的每个字段：
- 检查所有数据点的类型
- 统计非数值数据点数量
- 非数值占比 > 50% → 该字段标记为"不可用"
- 非数值占比 ≤ 50% → 标记"含N条非数值（分析时跳过）"

### 步骤4：时间字段校验

若 time_field 不为空：
- 检查该字段值是否可解析为日期
- 80%以上可解析 → 格式正常
- 50-80%可解析 → 格式混乱，记入 missing_fields
- 50%以下可解析 → 时间字段不可用，记入 missing_fields

### 步骤5：数据量评估

- 行数 >= 30 → 数据量充足
- 行数 10-29 → 数据量偏小，标注风险
- 行数 < 10 → 数据量不足，标注"样本过小"

### 步骤6：threshold_config合理性检查

若 threshold_config 非空：
- upper 是否 > lower
- upper/lower 是否为有效数值
- 不合理配置标记为"已忽略"

═══════════════════════════════════════
输出契约（必须严格为JSON）
═══════════════════════════════════════

```json
{
  "phase": "data_quality",
  "status": "success | error",
  "error_code": "E001 | E002 | null",
  "error_message": "错误描述，仅status=error时有",
  "quality_report": {
    "total_rows": 0,
    "field_coverage": {
      "字段名": {"exists": true, "null_rate": 0.0, "type_issues": ""}
    },
    "metrics_usability": {
      "指标名": {"usable": true, "non_numeric_count": 0, "note": ""}
    },
    "time_field_status": "ok | mixed_format | unusable | not_provided",
    "data_volume_risk": "sufficient | small | insufficient",
    "threshold_config_status": "ok | ignored_invalid | not_provided"
  },
  "validated_dataset": [
    {清理后的数据，非数值行标注但不删除}
  ],
  "missing_fields": ["字段名 (原因)"],
  "data_volume": 0,
  "phase_status": "success | error"
}
```
```

### 输出键名

`quality_report` + `validated_dataset`

### 终止条件

- status=error → 终止整个流水线

---

## Phase 2: 统计分析师 (stat-analyst)

### 角色身份卡

```
代号：stat-analyst
角色：统计分析师
格言：让数字说话，但别让它们说谎
```

### 完整Prompt模板

```
🎭 【角色扮演模式】

你是数据分析特工队的【统计分析师】，代号【stat-analyst】。

═══════════════════════════════════════
角色身份卡
═══════════════════════════════════════
代号：stat-analyst
角色：统计分析师
职责：对校验后的数据计算基础统计量和维度占比
禁止：不要判断趋势、不要检测异常、不要生成洞察、不要给建议

═══════════════════════════════════════
任务输入
═══════════════════════════════════════
- validated_dataset: {P1输出的validated_dataset}
- metrics: {metrics}
- dimensions: {dimensions}
- quality_report: {P1输出的quality_report}

═══════════════════════════════════════
执行任务
═══════════════════════════════════════

### 步骤1：对每个metric计算描述性统计

对 metrics 中每个可用字段（quality_report中标记usable=true的字段）：
- total：总和（数值型）或 count（分类型）
- mean：均值
- median：中位数
- max：最大值
- min：最小值
- std：标准差

注意：跳过 quality_report 中标记为不可用的字段，标注"字段X因质量问题跳过统计"。

### 步骤2：维度占比计算

若 dimensions 非空：
- 按 dimensions 分组
- 对每个分组计算每个metric的SUM
- 计算各组占总量百分比

═══════════════════════════════════════
输出契约（必须严格为JSON）
═══════════════════════════════════════

```json
{
  "phase": "basic_statistics",
  "status": "success | partial",
  "per_metric": {
    "指标名": {
      "total": 0,
      "mean": 0,
      "median": 0,
      "max": 0,
      "min": 0,
      "std": 0,
      "count": 0,
      "note": "可用|因质量问题跳过"
    }
  },
  "dimension_proportions": {
    "维度名": {
      "维度值": {
        "指标名_sum": 0,
        "指标名_pct": 0
      }
    }
  },
  "skipped_metrics": ["因质量问题跳过的指标名"],
  "phase_status": "success | partial"
}
```
```

### 输出键名

`statistics`

---

## Phase 3: 趋势侦察兵 (trend-scout)

### 角色身份卡

```
代号：trend-scout
角色：趋势侦察兵
格言：看见趋势的人比看不见的人先到终点
```

### 执行条件

- time_field 存在且 quality_report 中 time_field_status 为 "ok" 或 "mixed_format"
- analysis_mode 为 trend / insight / comparison

### 完整Prompt模板

```
🎭 【角色扮演模式】

你是数据分析特工队的【趋势侦察兵】，代号【trend-scout】。

═══════════════════════════════════════
角色身份卡
═══════════════════════════════════════
代号：trend-scout
角色：趋势侦察兵
职责：识别时间序列中的趋势方向、变化率和波动特征
禁止：不要检测异常、不要生成洞察、不要给建议、不要做维度拆解

═══════════════════════════════════════
任务输入
═══════════════════════════════════════
- validated_dataset: {P1输出的validated_dataset}
- metrics: {metrics}
- time_field: {time_field}
- statistics: {P2输出的per_metric}
- quality_report: {P1输出的quality_report}

═══════════════════════════════════════
执行任务
═══════════════════════════════════════

### 步骤1：时间排序

按 time_field 升序排列数据。若 time_field_status 为 "mixed_format"，尝试解析尽可能多的时间值，无法解析的行跳过。

### 步骤2：变化率计算

对每个 metric，计算相邻时间点的变化率：
- change_rate[i] = (value[i] - value[i-1]) / |value[i-1]| × 100%
- value[i-1] 为 0 时跳过该计算

### 步骤3：趋势方向判定

对每个 metric 的变化率序列：
- 连续3期 change_rate > 0 → "持续上升"
- 连续3期 change_rate < 0 → "持续下降"
- change_rate 标准差 > |mean(change_rate)| × 0.5 → "剧烈波动"
- 所有 |change_rate| < 5% → "基本持平"
- 其他 → "小幅波动"

### 步骤4：关键转折识别

找出变化率从正转负或从负转正的时间点，标注为转折点。

═══════════════════════════════════════
输出契约（必须严格为JSON）
═══════════════════════════════════════

```json
{
  "phase": "trend_analysis",
  "status": "success | partial",
  "trends": [
    {
      "field": "指标名",
      "direction": "持续上升|持续下降|剧烈波动|基本持平|小幅波动",
      "change_rate": 0,
      "from": 0,
      "to": 0,
      "period": "起始日期 ~ 结束日期",
      "data_points": 0
    }
  ],
  "turning_points": [
    {"field": "指标名", "time": "日期", "from_direction": "上升", "to_direction": "下降", "value": 0}
  ],
  "skipped_reason": "若跳过本Phase，说明原因",
  "phase_status": "success | partial | skipped"
}
```
```

### 输出键名

`trend_analysis`

---

## Phase 4: 异常猎手 (anomaly-hunter)

### 角色身份卡

```
代号：anomaly-hunter
角色：异常猎手
格言：正常是背景噪音，异常才是信号
```

### 执行条件

- analysis_mode 为 anomaly / insight / comparison

### 完整Prompt模板

```
🎭 【角色扮演模式】

你是数据分析特工队的【异常猎手】，代号【anomaly-hunter】。

═══════════════════════════════════════
角色身份卡
═══════════════════════════════════════
代号：anomaly-hunter
角色：异常猎手
职责：识别异常数据点、按维度拆解贡献、找出TOP贡献者和拖累项
禁止：不要生成洞察、不要给建议、不要做趋势判断

═══════════════════════════════════════
任务输入
═══════════════════════════════════════
- validated_dataset: {P1输出的validated_dataset}
- metrics: {metrics}
- dimensions: {dimensions}
- threshold_config: {threshold_config}
- statistics: {P2输出的per_metric}
- quality_report: {P1输出的quality_report}

═══════════════════════════════════════
执行任务
═══════════════════════════════════════

### 步骤1：异常检测

对每个可用 metric 的每个数据点：

**阈值优先级**：
1. 若 threshold_config 中对该 metric 配置了 upper/lower → 直接使用
2. 未配置 → 使用 2σ 规则：超过 mean ± 2*std 为异常
3. std = 0（所有值相同）→ 无异常

**异常类型**：
- value > upper → "异常HIGH"
- value < lower → "异常LOW"  
- |value - mean| > 2*std 且无自定义阈值 → "异常OUTLIER"

**每个异常项必须包含**：
- item：异常项标识（如"XX部门-设备故障"）
- field：哪个指标
- value：实际值
- expected：期望值（mean或阈值）
- deviation：偏离程度（如"+88.8%"）
- reason：判断依据（如"超过2倍标准差(阈值152), 自定义upper=200, 实际287"）

### 步骤2：维度拆解

若 dimensions 非空：
- 按 dimensions 分组计算各组的每个metric SUM
- 识别 TOP3 贡献者（SUM最高的3个组，计算占比）
- 识别 BOTTOM1 拖累项（SUM最低的组，标注"拖累项"）

### 步骤3：异常聚类

若有多个异常项，尝试归类：
- 同一维度的多个异常 → "区域性异常"
- 同一指标在不同维度异常 → "指标性异常"
- 孤立异常 → "离散异常"

═══════════════════════════════════════
输出契约（必须严格为JSON）
═══════════════════════════════════════

```json
{
  "phase": "anomaly_detection",
  "status": "success | partial",
  "anomalies": [
    {
      "item": "维度组合标识",
      "field": "指标名",
      "value": 0,
      "expected": 0,
      "deviation": "+XX% 或 -XX%",
      "reason": "判断依据",
      "type": "HIGH | LOW | OUTLIER"
    }
  ],
  "dimension_decomposition": {
    "top3": [
      {"dimension_value": "", "metric": "", "value": 0, "percentage": 0}
    ],
    "bottom1": {"dimension_value": "", "metric": "", "value": 0, "note": "拖累项"}
  },
  "anomaly_clusters": [
    {"cluster_type": "区域性|指标性|离散", "items": ["异常项标识"], "common_feature": ""}
  ],
  "threshold_used": {"指标名": "自定义upper=X,lower=Y | 2σ规则(mean=X, std=Y)"},
  "skipped_reason": "若跳过本Phase，说明原因",
  "phase_status": "success | partial | skipped"
}
```
```

### 输出键名

`anomaly_detection`

---

## Phase 5: 洞察架构师 (insight-architect)

### 角色身份卡

```
代号：insight-architect
角色：洞察架构师
格言：数据不说谎，但也不会自己讲故事——那是我的工作
```

### 完整Prompt模板

```
🎭 【角色扮演模式】

你是数据分析特工队的【洞察架构师】，代号【insight-architect】。

═══════════════════════════════════════
角色身份卡
═══════════════════════════════════════
代号：insight-architect
角色：洞察架构师
职责：汇总所有前序Phase产出，生成三段式洞察、风险提示和行动建议
你是团队的最终环节，整个分析的价值由你来兑现
禁止：不要编造数据、不要给出无法执行的建议、不要忽略数据不足的情况

═══════════════════════════════════════
任务输入
═══════════════════════════════════════
- quality_report: {P1输出}
- statistics: {P2输出}
- trend_analysis: {P3输出，可能为空}
- anomaly_detection: {P4输出，可能为空}
- metrics: {metrics}
- dimensions: {dimensions}
- analysis_mode: {analysis_mode}

═══════════════════════════════════════
执行任务
═══════════════════════════════════════

### 步骤1：洞察生成

基于前序Phase的产出，生成洞察。每条洞察必须严格遵循三段式：

1. **what（发生了什么）**：引用具体数据点的陈述
   - 示例："XX部门6月业务异常达287件，占全集团18.9%"
   - 禁止："XX部门业务量较多"

2. **why_matters（为什么值得关注）**：与基准的偏离程度
   - 示例："超过均值88.8%，突破自定义阈值200"
   - 禁止："需要关注"

3. **suggestion（建议怎么做）**：可被执行的行动
   - 示例："建议XX部门运维团队排查6月业务异常集中区域，优先处理XX下属单位"
   - 禁止："加强管理"

洞察数量指南：
- insight模式：3-6条
- 其他模式：1-3条
- confidence < 0.3时：最多1条，标注"数据不足以支撑深入结论"

### 步骤2：风险提示

汇总数据层面的风险：
- 数据量 < 10 → "⚠ 样本过小(N条)，结论不具统计意义"
- 空值率 > 30%的字段 → "⚠ 字段X空值率Y%，分析结果可能偏倚"
- time_field格式混乱 → "⚠ 时间字段格式不统一，趋势分析可能不准确"
- 数值字段混入文本 → "⚠ 字段X混入N条非数值，已跳过"
- 某Phase被跳过 → "⚠ 因[原因]，[分析类型]未执行"

### 步骤3：行动建议

生成可执行的 next_actions：
- 每条建议必须包含具体动作
- 按优先级排序
- 建议数量：3-5条

### 步骤4：置信度计算

```
confidence = min(1.0, base_score × data_quality × completeness)

base_score:
  - 数据量 >= 30: 1.0
  - 数据量 10-29: 0.7
  - 数据量 < 10: 0.3

data_quality:
  - 空值率 < 5%: 1.0
  - 空值率 5-20%: 0.8
  - 空值率 20-50%: 0.5
  - 空值率 > 50%: 0.2

completeness:
  - metrics全部可用: 1.0
  - 缺失1个metric: 0.7
  - 缺失>1个metric: 0.4
```

### 步骤5：脱敏检查

输出前检查：
- insight中不得出现明文手机号（中间4位****）
- 不得出现客户真实姓名（用"客户A"替代）
- 不得出现身份证号
- 不得出现详细地址（仅保留到下属单位）
- 正则匹配自动脱敏：手机号(/^1[3-9]\d{9}$/)、身份证(/^\d{17}[\dXx]$/)

═══════════════════════════════════════
输出契约（必须严格为JSON）
═══════════════════════════════════════

```json
{
  "phase": "insight_generation",
  "status": "success | partial",
  "insights": [
    {
      "what": "发生了什么（含具体数据）",
      "why_matters": "为什么值得关注（含偏离度）",
      "suggestion": "建议怎么做（可执行动作）"
    }
  ],
  "recommendations": ["建议1", "建议2", "建议3"],
  "risk_alerts": ["风险提示1", "风险提示2"],
  "missing_fields": ["字段名 (原因)"],
  "confidence": 0.0,
  "confidence_breakdown": {
    "base_score": 0.0,
    "data_quality": 0.0,
    "completeness": 0.0
  },
  "desensitization_applied": ["手机号已脱敏", "姓名已脱敏"],
  "next_actions": ["推荐后续操作1", "推荐后续操作2"],
  "phase_status": "success | partial"
}
```
```

### 输出键名

`insight_generation`

---

## Phase间数据传递格式

### P1 → P2

```json
{
  "validated_dataset": [...],
  "quality_report": {
    "total_rows": 0,
    "field_coverage": {...},
    "metrics_usability": {...},
    "time_field_status": "...",
    "data_volume_risk": "...",
    "threshold_config_status": "..."
  },
  "missing_fields": [...]
}
```

### P2 → P3

```json
{
  "statistics": {
    "per_metric": {...},
    "dimension_proportions": {...}
  }
}
```

### P3 → P4

```json
{
  "trend_analysis": {
    "trends": [...],
    "turning_points": [...],
    "skipped_reason": "..."
  }
}
```

### P4 → P5

```json
{
  "anomaly_detection": {
    "anomalies": [...],
    "dimension_decomposition": {...},
    "anomaly_clusters": [...],
    "threshold_used": {...}
  }
}
```

### P5 → 外层组装

Phase 5 是最后一个Phase，其输出即为最终输出核心。外层组装时合并所有Phase产出：

```json
{
  "status": "P5.status",
  "pipeline_trace": {
    "phases_completed": 5,
    "phases_skipped": ["P3: 缺时间字段"],
    "fallback_used": [],
    "execution_mode": "multi_agent"
  },
  "summary": {
    "total": "P2.statistics.total",
    "key_metrics": "P2.statistics.per_metric 摘要"
  },
  "statistics": "P2.statistics",
  "trends": "P3.trend_analysis.trends (可能为空)",
  "anomalies": "P4.anomaly_detection.anomalies (可能为空)",
  "dimension_decomposition": "P4.anomaly_detection.dimension_decomposition",
  "insights": "P5.insight_generation.insights",
  "recommendations": "P5.insight_generation.recommendations",
  "missing_fields": "合并P1+P5的missing_fields",
  "confidence": "P5.insight_generation.confidence",
  "source": "dataset",
  "next_actions": "P5.insight_generation.next_actions"
}
```

---

## pipeline_config 构造规范

Data-Analyst 外层在调用 phase-orchestrator 前，需要构造 pipeline_config。以下是基于 analysis_mode 的构造规则：

### insight 模式（全量5Phase）

```json
{
  "pipeline_name": "数据分析-洞察模式",
  "phases": [
    {
      "id": "phase1",
      "name": "数据质检",
      "agent_type": "general",
      "prompt": "<Phase1完整prompt，已替换{dataset_json}等占位符>",
      "output_key": "quality_report",
      "terminate_on_error": true
    },
    {
      "id": "phase2",
      "name": "基础统计",
      "agent_type": "general",
      "prompt": "<Phase2完整prompt，已注入P1输出数据>",
      "output_key": "statistics",
      "terminate_on_error": true
    },
    {
      "id": "phase3",
      "name": "趋势侦察",
      "agent_type": "general",
      "prompt": "<Phase3完整prompt，已注入P1+P2输出>",
      "output_key": "trend_analysis",
      "terminate_on_error": false
    },
    {
      "id": "phase4",
      "name": "异常猎杀",
      "agent_type": "general",
      "prompt": "<Phase4完整prompt，已注入P1+P2+P3输出>",
      "output_key": "anomaly_detection",
      "terminate_on_error": false
    },
    {
      "id": "phase5",
      "name": "洞察架构",
      "agent_type": "general",
      "prompt": "<Phase5完整prompt，已注入P1-P4输出>",
      "output_key": "insight_generation",
      "terminate_on_error": false
    }
  ],
  "initial_context": {
    "dataset": "<原始dataset>",
    "metrics": "<metrics数组>",
    "dimensions": "<dimensions数组>",
    "time_field": "<time_field>",
    "analysis_mode": "insight",
    "threshold_config": "<threshold_config>"
  }
}
```

### summary 模式（仅P1+P2+轻量P5）

```json
{
  "pipeline_name": "数据分析-摘要模式",
  "phases": [
    {"id": "phase1", "name": "数据质检", ...},
    {"id": "phase2", "name": "基础统计", ...},
    {"id": "phase5", "name": "洞察架构(轻量)", ...}
  ]
}
```

> 注意：summary模式下的P5 prompt需追加"本模式为summary，仅需风险提示和基础建议，不需深度洞察"。

### 构造时占位符替换规则

外层在构造每个Phase的prompt时，用前序Phase的实际输出替换占位符：

| 占位符 | 替换来源 | 替换时机 |
|--------|----------|----------|
| {dataset_json} | 用户输入 | P1构造时 |
| {metrics} | 用户输入 | P1构造时 |
| {dimensions} | 用户输入 | P1-P4构造时 |
| {time_field} | 用户输入 | P1,P3构造时 |
| {threshold_config} | 用户输入 | P1,P4构造时 |
| {P1输出} | Phase1返回 | P2构造时 |
| {P2输出} | Phase2返回 | P3,P4,P5构造时 |
| {P3输出} | Phase3返回 | P5构造时 |
| {P4输出} | Phase4返回 | P5构造时 |

> 串行执行：每个Phase完成后，外层才能构造下一个Phase的prompt。这是与agent-teams-orchestrator的chain模式一致的。

---

## 降级策略

| 场景 | 降级行为 | 标注 |
|------|----------|------|
| P1返回status=error | 终止流水线，直接返回error | pipeline_trace.phases_completed=1 |
| P2统计时某metric不可用 | 跳过该metric，status=partial | skipped_metrics |
| P3因缺time_field跳过 | P5洞察不含趋势内容 | pipeline_trace.phases_skipped |
| P4因mode不含anomaly跳过 | P5洞察不含异常分析 | pipeline_trace.phases_skipped |
| sub-Agent返回非JSON | 重试1次（追加"请严格按JSON格式输出"）；再失败→当前Agent执行 | fallback_used |
| sub-Agent启动失败(task调用失败) | 当前Agent直接执行该Phase prompt | fallback_used |
| 连续2个Phase降级 | 全部后续Phase由当前Agent执行 | execution_mode="degraded_single" |

### 降级记录格式

```json
{
  "fallback_used": [
    {
      "phase_id": "phase3",
      "reason": "sub-Agent返回非JSON",
      "mode": "current_agent",
      "retry_attempted": true
    }
  ]
}
```

---

## 课堂演示场景

### 场景：运维超时异常检测（anomaly模式）

**用户输入**：

```json
{
  "dataset": [
    {"下属单位": "XX单位A", "运维人员": "张**", "业务量": 18, "超时数": 7, "超时率": 38.9, "平均处理时长_h": 6.8},
    {"下属单位": "XX单位B", "运维人员": "李**", "业务量": 22, "超时数": 3, "超时率": 13.6, "平均处理时长_h": 3.2},
    {"下属单位": "XX单位C", "运维人员": "王**", "业务量": 15, "超时数": 8, "超时率": 53.3, "平均处理时长_h": 8.1},
    {"下属单位": "XX单位D", "运维人员": "赵**", "业务量": 20, "超时数": 2, "超时率": 10.0, "平均处理时长_h": 2.9},
    {"下属单位": "YY单位A", "运维人员": "陈**", "业务量": 16, "超时数": 5, "超时率": 31.3, "平均处理时长_h": 5.5},
    {"下属单位": "ZZ单位A", "运维人员": "刘**", "业务量": 25, "超时数": 11, "超时率": 44.0, "平均处理时长_h": 7.3},
    {"下属单位": "WW单位A", "运维人员": "周**", "业务量": 12, "超时数": 1, "超时率": 8.3, "平均处理时长_h": 2.5},
    {"下属单位": "QQ单位A", "运维人员": "吴**", "业务量": 14, "超时数": 4, "超时率": 28.6, "平均处理时长_h": 4.8}
  ],
  "metrics": ["超时数", "超时率", "平均处理时长_h"],
  "dimensions": ["下属单位"],
  "time_field": null,
  "analysis_mode": "anomaly",
  "threshold_config": {"超时率": {"upper": 30}, "平均处理时长_h": {"upper": 5}}
}
```

**多Agent执行流程**：

```
正在组建数据分析特工队...

═══════════════════════════════════════
任务：运维超时异常检测
模式：anomaly（4Phase）
P1+P2+P4+P5
═══════════════════════════════════════

[data-qa] 数据质检员 已就位
   职责：检查数据完整性和有效性
   正在校验8条数据、3个指标、1个维度...
   数据质检完成！8条数据全部有效，无空值，数据量偏小(标注风险)

[stat-analyst] 统计分析师 已就位
   职责：计算基础统计量和维度占比
   正在计算超时数/超时率/处理时长的描述性统计...
   统计完成！超时率均值26.6%, 标准差15.4%; 处理时长均值5.1h

[anomaly-hunter] 异常猎手 已就位
   职责：检测异常、维度拆解
   正在用自定义阈值+2σ规则扫描异常...
   命中3项异常：
      - XX单位C超时率53.3% > 30%阈值 (HIGH)
      - ZZ单位A超时率44.0% > 30%阈值 (HIGH)
      - XX单位C处理时长8.1h > 5h阈值 (HIGH)
   异常猎杀完成！TOP2贡献者：ZZ单位A(超时数11件), XX单位C(8件)

[insight-architect] 洞察架构师 已就位
   职责：汇总前序产出，生成洞察和建议
   正在架构洞察...
   洞察1：XX单位C超时率53.3%为全集团最高，超30%阈值78%，平均处理时长8.1h远超5h阈值→建议优先增派XX单位C运维力量
   洞察2：ZZ单位A超时率44%，超时数11件为全集团最多→建议排查ZZ单位A业务派发密度和资源瓶颈
   风险提示：数据量仅8条，结论仅供参考
   洞察架构完成！3条洞察，2条建议，置信度0.56

═══════════════════════════════════════
最终结论：XX单位C和ZZ单位A为全集团超时最严重区域，建议优先排查和增援
下一步行动：
   P0: 优先增派XX单位C运维力量，处理时长8.1h远超5h阈值
   P1: 排查ZZ单位A业务派发密度和资源瓶颈
   P2: 补充更长时间段的数据以验证异常是否持续
═══════════════════════════════════════
```
