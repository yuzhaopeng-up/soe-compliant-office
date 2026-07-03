# 编排协议：4组件链式调用

## 目录

1. [总览](#总览)
2. [Phase 1 — Info-Extractor](#phase-1)
3. [Phase 2 — Data-Analyst](#phase-2)
4. [Phase 3 — Report-Generator](#phase-3)
5. [Phase 4 — Archive-Manager](#phase-4)
6. [端到端调用示例](#端到端调用示例)
7. [降级策略细节](#降级策略细节)

---

## 总览

```
用户输入 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → 用户输出
            │          │          │          │
            ↓          ↓          ↓          ↓
        output_1    output_2    output_3    archive_record
```

### 数据流契约

每个 Phase 的输出必须是合法 JSON 对象，传递给下一 Phase 作为输入。不可跳过任何 Phase。

### 组件类型说明

| 组件 | 类型 | 加载方式 |
|------|------|---------|
| Info-Extractor | 外部技能 | `skill` 工具加载 `info-extractor` |
| Data-Analyst | 外部技能 | `skill` 工具加载 `data-analyst` |
| Report-Generator | 外部技能 | `skill` 工具加载 `report-generator` |
| Archive-Manager | 外部技能 | `skill` 工具加载 `archive-manager` |

---

## Phase 1

### 调用指令

```
1. 执行 skill 工具，参数 name="info-extractor"
2. 加载成功后，对 evidence_sources 中的每个来源：
   a. 构造提取请求：原始内容 = source.content，提取目标 = 时间、事件、数值、对象
   b. 按 Info-Extractor 的规范执行提取
   c. 将提取结果加上 source_name、source_type、initial_confidence，存入 extracted_evidences 数组
3. 未提取到时间字段的证据，将 extracted_fields.time 设为 null
```

### 输出 JSON Schema

```json
{
  "phase": 1,
  "status": "success|degraded|failed",
  "extracted_evidences": [
    {
      "evidence_id": "E-01",
      "source_name": "相关方投诉记录",
      "source_type": "投诉记录",
      "extracted_fields": {
        "time": "2026-06-12T09:00:00",
        "event": "核心业务系统中断投诉",
        "value": "中断3次",
        "object": "核心业务系统",
        "location": null
      },
      "initial_confidence": 0.4,
      "raw_summary": "某制造企业投诉核心业务系统一周内中断3次，影响生产"
    }
  ],
  "degraded_components": []
}
```

### 降级

若 `info-extractor` 加载失败：
- `status` 设为 `"degraded"`
- `degraded_components` 添加 `"info-extractor"`
- 手动按来源类型提取：识别文本中的时间、数值、关键动作，填入 extracted_fields
- 报告中标注"证据提取采用降级模式"

---

## Phase 2

### 调用指令

```
1. 执行 skill 工具，参数 name="data-analyst"
2. 加载成功后，将 output_phase1 作为分析输入
3. 按以下4个子步骤顺序执行交叉验证与推断
```

若 `data-analyst` 加载失败，按 SKILL.md 中 Phase 2 子步骤手动执行分析。

### 2a - 时间线对齐

```
1. 从 output_phase1.extracted_evidences 中筛选 extracted_fields.time 非 null 的证据
2. 按时间升序排列
3. 对时间差 ≤ 15分钟（conflict_sensitivity=medium）或 ≤ 1分钟（high）的证据对，
   标记为"可能描述同一事件"，存入 timeline_events
4. 全部无时间的证据，存入 timeline_events 的 untimed 子数组
```

**输出字段**：
```json
{
  "timeline_events": {
    "timed": [
      {
        "time": "2026-06-05T10:22:00",
        "evidence_ids": ["E-02"],
        "event_summary": "链路A丢包8.2%"
      }
    ],
    "untimed": [
      { "evidence_ids": ["E-05"], "event_summary": "合同承诺≥99.5%" }
    ]
  }
}
```

### 2b - 冲突检测

```
1. 遍历 timeline_events.timed 中同一事件的证据对
2. 按 conflict-rules.md 中的类型（数值/时间/状态/范围）和敏感度级别逐项比对
3. 构成冲突 → 生成冲突记录
4. 不构成冲突 → 标记为"相互验证"，提升跨源验证度
```

冲突检测规则详见 [conflict-rules.md](conflict-rules.md)。

### 2c - 置信度评估

```
对每条证据计算：
  final_confidence = initial_confidence × cross_validation × time_decay

其中：
  cross_validation:
    - 有≥2个独立来源验证同一事实: 0.8-1.0
    - 有1个独立来源部分验证: 0.5-0.7
    - 无其他来源验证: 0.3

  time_decay:
    - 30天内: 1.0
    - 超过30天: 0.95^(超过月数)
```

### 2d - 根因推断

```
1. 从冲突和非冲突证据中，按3个维度评分：
   - 时间最早：最早出现的异常事件 +1分
   - 下游依赖：被后续事件依赖最多的源事件 +1分/依赖
   - 高频出现：在≥2条证据中反复出现的模式 +1分
2. 综合评分最高的 = 疑似根因
3. 置信度映射：
   - 根因置信度 ≥ 0.8: 高
   - 0.5 ≤ 根因置信度 < 0.8: 中
   - 根因置信度 < 0.5: 低 + "⚠️ 待进一步验证"
4. 根因置信度 < confidence_threshold → 标注 "⚠️ 待进一步验证" + 列出需补充的证据
```

### Phase 2 完整输出

```json
{
  "phase": 2,
  "status": "success",
  "timeline_events": { "timed": [...], "untimed": [...] },
  "conflicts": [
    {
      "conflict_id": "C-01",
      "type": "数值冲突",
      "description": "相关方称中断3次，系统仅记录2次异常",
      "sources_involved": ["E-01", "E-02", "E-03"],
      "difference": "差值=1次",
      "possible_reason": "第3次可能是相关方侧设备问题"
    }
  ],
  "confidence_scores": [
    {
      "evidence_id": "E-01",
      "source_confidence": 0.4,
      "cross_validation": 0.7,
      "time_decay": 1.0,
      "final_confidence": 0.28
    }
  ],
  "root_cause": {
    "suspected": "链路A光模块劣化",
    "confidence_level": "高",
    "confidence_value": 0.85,
    "basis": ["时间最早", "下游依赖", "高频出现"],
    "needs_further_verification": false
  },
  "recommended_actions": [
    {
      "priority": "🔴优先",
      "action": "更换光模块",
      "linked_evidence": ["E-04"]
    },
    {
      "priority": "🟡同时",
      "action": "提供书面故障分析",
      "linked_evidence": ["E-01", "E-05"]
    }
  ]
}
```

---

## Phase 3

### 调用指令

```
1. 执行 skill 工具，参数 name="report-generator"
2. 加载成功后，将 output_phase2 分析结果和 output_phase1 证据清单作为报告输入
3. 按以下模板生成报告
```

若 `report-generator` 加载失败，按 SKILL.md 中 Phase 3 的5模块模板手动生成报告。

### 生成规则

1. 取 `output_phase2` 的 conflicts、confidence_scores、root_cause、recommended_actions
2. 取 `output_phase1` 的 extracted_evidences 构建证据清单
3. 严格按 SKILL.md 中"标准输出结构"的5个模块排版
4. 按 `output_format` 参数选择格式：
   - `markdown`：标准 Markdown 表格和列表
   - `json`：完整 JSON 对象
   - `table`：纯表格模式（适合粘贴到 Excel）

### Phase 3 输出

```json
{
  "phase": 3,
  "status": "success",
  "output_format": "markdown",
  "report_content": "（完整报告文本）",
  "report_metadata": {
    "analysis_time": "2026-06-20T14:30:00+08:00",
    "evidence_count": 7,
    "conflict_count": 2,
    "max_confidence": 0.85
  }
}
```

---

## Phase 4

### 调用指令

```
1. 执行 skill 工具，参数 name="archive-manager"
2. 加载成功后，构造归档请求：
   - 归档类型：evidence-chain-analysis
   - 归档内容：
     a. 分析过程：output_phase1 + output_phase2 摘要
     b. 分析结论：output_phase3.report_content
     c. 归档元数据：分析人、分析时间、证据来源清单
3. 归档前执行脱敏：
   - 相关方名称 → "Client-A"
   - 合同编号保留，金额细节隐藏
   - 个人电话号码 → 139****5678
4. 按 Archive-Manager 的规范执行归档
```

### 归档元数据必须包含

```json
{
  "archive_type": "evidence-chain-analysis",
  "analysis_question": "（原始问题）",
  "analyst": "（分析人）",
  "analysis_time": "（ISO时间）",
  "evidence_sources": [
    { "source_name": "...", "source_type": "...", "sanitized": true/false }
  ],
  "degraded_components": [],
  "related_conflicts": ["C-01", "C-02"]
}
```

### 降级

若 `archive-manager` 加载失败：
- 将归档内容保存为本地 Markdown 文件
- 文件名：`evidence-chain-archive-{YYYYMMDD-HHmmss}.md`
- 保存路径：当前工作目录
- 报告中标注"归档采用降级模式，保存为本地文件"

---

## 端到端调用示例

以演示数据为例的完整调用链：

### Step 1: 加载 Info-Extractor

```
skill(name="info-extractor")  →  加载成功
对3个来源分别提取 → 得到7条结构化证据 → output_phase1
```

### Step 2: 加载 Data-Analyst

```
skill(name="data-analyst")  →  加载成功
将 output_phase1 传入 Data-Analyst 执行分析：
2a: 时间线对齐 → 5条有时间的证据排序 + 2条无时间
2b: 冲突检测 → C-01(数值冲突), C-02(状态冲突)
2c: 置信度评估 → E-03最高0.72, E-04次之0.68
2d: 根因推断 → 链路A光模块劣化, 0.85(高)
→ output_phase2
```

### Step 3: 加载 Report-Generator

```
skill(name="report-generator")  →  加载成功
将 output_phase1 + output_phase2 传入 → 按5模块模板生成 → output_phase3
```

### Step 4: 加载 Archive-Manager

```
skill(name="archive-manager")  →  加载成功
脱敏 → 归档 → 完成
```

---

## 降级策略细节

### 降级触发条件

| 条件 | 触发降级的组件 |
|------|--------------|
| `skill` 工具加载 `info-extractor` 失败 | Info-Extractor |
| `skill` 工具加载 `data-analyst` 失败 | Data-Analyst |
| `skill` 工具加载 `report-generator` 失败 | Report-Generator |
| `skill` 工具加载 `archive-manager` 失败 | Archive-Manager |

### 降级时报告标注

在报告元数据中添加：

```json
{
  "degraded": true,
  "degraded_components": ["info-extractor"],
  "degradation_notes": "证据提取采用手动模式，置信度评估可能偏低"
}
```

### 全降级场景

若所有外部组件均加载失败：
- Phase 1 手动提取 + Phase 2 按 SKILL.md 子步骤手动分析 + Phase 3 按5模块模板手动生成 + Phase 4 保存本地文件
- 报告标注"完全降级模式"
- 分析逻辑不受影响（手动执行等价于技能加载），但归档方式变化
