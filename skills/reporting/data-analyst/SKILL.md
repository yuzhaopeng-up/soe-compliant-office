---
name: data-analyst
name_cn: 数据分析组件
version: 1.0.0
domain: reporting
soe_relevance: 4
description: >
  Structured business data analysis with 5-Agent collaborative pipeline. Supports summary, trend,
  anomaly, comparison, and insight analysis modes. Auto-desensitization, confidence scoring,
  and SASAC report format compatibility. Transforms data into actionable SOE business insights.
description_cn: >
  数据分析基础组件，5-Agent团队协作分析，支持趋势判断、异常检测、同比环比、TOP问题识别。
  内置脱敏和置信度评估，适配央国企国资委报告格式。
---

# Data-Analyst 数据分析基础组件

> 核心理念：从数据到洞察，不只是求和平均，而是异常检测、趋势判断。
> 多Agent升级：5个专项角色协作完成分析，每个角色独立sub-Agent执行，Phase间结构化JSON传递。

## 适用人群

经营分析人员、数据支撑人员、部门业务骨干、管理支撑人员

## 典型业务场景

1. 业务异常日报分析
2. 重大项目进度分析
3. 营销活动转化效果分析
4. 客户投诉量趋势分析
5. 运维超时异常检测
6. 培训学员完成率和通过率分析
7. 下属单位经营指标波动分析

## 输入参数

| 字段 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|------|------|------|--------|------|------|
| dataset | JSON数组或表格摘要 | 必填 | - | 结构化业务数据 | `[{"部门":"XX部门","业务量":120,"处理时长":4.5}]` |
| metrics | 字符串数组 | 必填 | - | 需分析的指标字段名 | `["业务量","处理时长"]` |
| dimensions | 字符串数组 | 可选 | `[]` | 分析维度 | `["部门","下属单位","业务类型"]` |
| time_field | 字符串 | 可选 | `null` | 时间维度字段名 | `"日期"` |
| analysis_mode | 字符串 | 可选 | `"insight"` | 分析模式：summary / trend / anomaly / comparison / insight | `"anomaly"` |
| threshold_config | JSON对象 | 可选 | `{}` | 异常阈值配置 | `{"业务量":{"upper":200,"lower":10}}` |
| output_format | 字符串 | 可选 | `"markdown"` | 输出格式：json / markdown / table | `"json"` |

## 依赖组件

| 类型 | Skill | 用途 |
|------|-------|------|
| 调度器 | phase-orchestrator | 多Agent编排调度，逐Phase启动sub-Agent |
| 辅助 | info-extractor | Phase 1 数据字段提取与结构化 |
| 辅助 | security-guard | 脱敏检查与权限校验 |

## 多Agent团队——数据分析特工队

本Skill不是单Agent从头跑到尾，而是由5个专项角色组成"数据分析特工队"，通过phase-orchestrator调度，每个角色独立sub-Agent执行：

```
┌───────────────────────────────────────────────────────────────┐
│  Data-Analyst 技能（外层编排）                                  │
│  职责：解析输入 → 构造pipeline_config → 调用phase-orchestrator  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─ phase-orchestrator 调度 ─────────────────────────────┐    │
│  │                                                       │    │
│  │  [P1] Data-QA 数据质检员 → 质量报告 + 校验后数据       │    │
│  │         ↓ JSON                                        │    │
│  │  [P2] Stat-Analyst 统计分析师 → 基础统计 + 占比       │    │
│  │         ↓ JSON                                        │    │
│  │  [P3] Trend-Scout 趋势侦察兵 → 趋势方向 + 变化率     │    │
│  │         ↓ JSON                                        │    │
│  │  [P4] Anomaly-Hunter 异常猎手 → 异常项 + 维度拆解     │    │
│  │         ↓ JSON                                        │    │
│  │  [P5] Insight-Architect 洞察架构师 → 洞察 + 建议      │    │
│  │                                                       │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                               │
│  外层组装最终输出 → 脱敏检查 → 返回用户                        │
└───────────────────────────────────────────────────────────────┘
```

### 团队角色一览

| 代号 | 角色名 | 职责 | 对应Step | 依赖工具 |
|------|--------|------|----------|----------|
| data-qa | 数据质检员 | 数据完整性检查、字段校验、空值率统计 | Step 1 | info-extractor |
| stat-analyst | 统计分析师 | 基础统计（总量/均值/极值/中位数/标准差/占比） | Step 2 | - |
| trend-scout | 趋势侦察兵 | 趋势方向判定、变化率计算、波动识别 | Step 3 | - |
| anomaly-hunter | 异常猎手 | 异常检测（阈值/2σ）、维度拆解、TOP/BOTTOM识别 | Step 4-5 | - |
| insight-architect | 洞察架构师 | 三段式洞察生成、风险提示、建议输出 | Step 6-7 | security-guard |

## 5-Phase强制编排协议

通过 phase-orchestrator 执行5个Phase。详细prompt模板和数据传递契约见 [references/pipeline-phases.md](references/pipeline-phases.md)。

```
P1 → task(sub-Agent: data-qa)           → quality_report + validated_dataset
P2 → task(sub-Agent: stat-analyst)      → statistics + proportions
P3 → task(sub-Agent: trend-scout)       → trends + change_rates        [条件执行]
P4 → task(sub-Agent: anomaly-hunter)    → anomalies + dimension_decomp [条件执行]
P5 → task(sub-Agent: insight-architect) → insights + recommendations + risk_alerts
```

### Phase 1: 数据质检（强制执行）

代号 `data-qa`，数据质检员。校验输入完整性，输出质量报告和校验后数据。

- 校验 dataset 非空且为有效数组
- 校验 metrics 中每个字段在 dataset 中存在
- 检查空值比例，空值率 > 30% 的字段记入 `missing_fields`
- 若 time_field 格式混乱，记入 `missing_fields` 并降级
- 数值字段混入文本时统计跳过数量

### Phase 2: 基础统计（强制执行）

代号 `stat-analyst`，统计分析师。对每个 metric 计算基础统计量和维度占比。

- 计算 total / mean / max / min / median / std
- 按 dimensions 计算各组占比（若指定 dimensions）

### Phase 3: 趋势侦察（条件执行）

代号 `trend-scout`，趋势侦察兵。仅在 time_field 存在且 analysis_mode 为 trend/insight/comparison 时执行。

- 按时间排序后计算相邻周期变化率
- 判定方向：持续上升 / 持续下降 / 剧烈波动 / 基本持平 / 小幅波动
- 输出趋势方向、变化率、起止值、周期

### Phase 4: 异常猎杀（条件执行）

代号 `anomaly-hunter`，异常猎手。仅在 analysis_mode 为 anomaly/insight/comparison 时执行。

- 优先使用 threshold_config，未配置则用 2σ 规则
- 标注异常项、偏离程度、判断依据
- 按 dimensions 分组进行维度拆解
- 识别 TOP3 贡献者和 BOTTOM1 拖累项

### Phase 5: 洞察架构（强制执行）

代号 `insight-architect`，洞察架构师。汇总所有前序Phase产出，生成三段式洞察、风险提示和行动建议。

- 每条洞察必须满足"发生了什么/为什么值得关注/建议怎么做"
- 汇总风险提示（样本过小、字段缺失、格式混乱等）
- 生成 next_actions（推荐后续操作）
- 计算综合 confidence

## Phase调度矩阵

不同 analysis_mode 触发不同Phase组合：

| analysis_mode | P1(质检) | P2(统计) | P3(趋势) | P4(异常) | P5(洞察) |
|---------------|----------|----------|----------|----------|----------|
| summary       | 执行     | 执行     | 跳过     | 跳过     | 轻量(仅风险提示) |
| trend         | 执行     | 执行     | 执行     | 跳过     | 执行     |
| anomaly       | 执行     | 执行     | 跳过     | 执行     | 执行     |
| comparison    | 执行     | 执行     | 执行     | 执行     | 执行     |
| insight       | 执行     | 执行     | 执行     | 执行     | 执行     |

> P3跳过条件：time_field 不存在时，即使 mode 为 trend/insight 也跳过，P5 中标注"趋势分析因缺时间字段而跳过"。

## 标准输出结构

```json
{
  "status": "success | partial | error",
  "pipeline_trace": {
    "phases_completed": 5,
    "phases_skipped": [],
    "fallback_used": [],
    "execution_mode": "multi_agent | degraded_single"
  },
  "summary": {
    "total": 0,
    "key_metrics": {}
  },
  "statistics": {
    "per_metric": {}
  },
  "trends": [
    {"field": "", "direction": "", "change_rate": 0, "from": 0, "to": 0, "period": ""}
  ],
  "anomalies": [
    {"item": "", "field": "", "value": 0, "expected": 0, "deviation": "", "reason": ""}
  ],
  "dimension_decomposition": {
    "top3": [{"dimension_value": "", "metric": "", "value": 0, "percentage": 0}],
    "bottom1": {"dimension_value": "", "metric": "", "value": 0, "note": ""}
  },
  "insights": [
    {"what": "", "why_matters": "", "suggestion": ""}
  ],
  "recommendations": [""],
  "missing_fields": [""],
  "confidence": 0.0,
  "source": "dataset",
  "next_actions": [""]
}
```

**字段说明**：
- `pipeline_trace`：多Agent执行追踪，记录完成/跳过/降级的Phase
- `statistics`：P2输出的完整基础统计（原版合并在summary中，现在独立输出）
- `dimension_decomposition`：P4输出的维度拆解结果

## 分析质量要求

见 [references/analysis_rules.md](references/analysis_rules.md) 中"洞察质量红线"章节。核心原则：
- 每条洞察必须对应具体数据
- 每条异常必须说明判断依据（阈值/统计偏离）
- 每条建议必须可被业务人员执行
- 数据不足时禁止编造结论，必须明确标注

## 异常处理

见 [references/exception_handling.md](references/exception_handling.md)。多Agent新增场景：

| 异常场景 | 处理方式 |
|----------|----------|
| P1返回status=error | 终止流水线，直接返回error结果 |
| P3因缺time_field跳过 | P5洞察中不含趋势相关内容，status=partial |
| 任一sub-Agent返回非JSON | 重试1次，再失败→当前Agent执行该Phase，记入fallback_used |
| sub-Agent启动失败 | 当前Agent直接执行该Phase prompt，标注[降级] |
| 连续2个Phase降级 | 全部后续Phase由当前Agent执行，标注[全降级] |

## 安全与脱敏

见 [references/security.md](references/security.md)。核心规则：
- P5(洞察架构师)输出前执行脱敏检查：手机号/姓名/证件号/地址
- 分析结果默认聚合到部门/单位/业务类型层面
- 审计日志记录：输入字段摘要、Phase执行链、输出摘要

## 央国企特色

### SOE Data Analysis Requirements

| SOE分析需求 | 本Skill对应能力 | 对应Phase |
|------------|---------------|----------|
| 国资委月报/快报数据 | P2统计+P3趋势 | 同比环比+预算完成率 |
| 下属单位指标波动 | P4异常检测+维度拆解 | 2σ检测+TOP/BOTTOM识别 |
| 穿透式监管数据准备 | P5洞察+风险提示 | 三段式洞察+可执行建议 |
| 经营分析会材料 | insight模式全链路 | 从质检到洞察的完整分析链 |
| 预算差异分析 | comparison模式 | P3趋势+P4异常+P5洞察 |
| 审计数据支撑 | 统计+异常自动标注 | 异常项自动标注偏离程度 |

### SOE Dimension Standards

央国企分析维度标准（替代部门/下属单位/业务类型）：

| 维度层级 | 示例 | 分析用途 |
|---------|------|---------|
| 集团级 | XX集团整体 | 宏观趋势判断 |
| 板块/业务单元 | XX板块/XX事业部 | 中观对标分析 |
| 下属单位 | XX公司/XX工厂 | 微观异常定位 |
| 业务类型 | 主营业务/投资/其他 | 结构变化分析 |
| 产品线 | 产品A/产品B | 贡献度拆解 |

### SOE Report Format Compatibility

本组件输出可直接对接国资委报告格式：
- 月报：P2统计+P3趋势 → 经营数据概览
- 快报：P4异常+P5洞察 → 重点关注事项
- 专题分析：全链路5-Phase → 深度分析报告

## 演示数据

见 [references/demo_data.md](references/demo_data.md)。覆盖全部 7 个典型场景，均为脱敏数据。

## 上线前自查清单

见 [references/checklist.md](references/checklist.md)。

## 课堂演示话术

> "现在数据分析师不是一个Agent从头干到尾了——它组建了一支5人特工队：质检员先过滤脏数据，统计师算基础指标，侦察兵盯趋势，猎手抓异常，架构师把发现串成洞察。每个角色都是独立的sub-Agent，上下文完全隔离，不会互相干扰。Phase间用结构化JSON传数据，和现实中的专业分工一模一样——质检和数据建模是两拨人，异常检测和洞察生成也是两拨人。"
