# 异常处理详细说明

## 目录

- [输入层异常](#输入层异常)
- [分析层异常](#分析层异常)
- [输出层异常](#输出层异常)
- [异常分级](#异常分级)

## 输入层异常

### E001: dataset 为空

- **触发条件**：dataset 为 null / undefined / [] / 非数组
- **处理方式**：status = "error"，不执行任何分析
- **输出示例**：

```json
{
  "status": "error",
  "summary": {"total": 0, "key_metrics": {}},
  "trends": [],
  "anomalies": [],
  "insights": [],
  "recommendations": [],
  "missing_fields": ["dataset"],
  "confidence": 0.0,
  "source": "dataset",
  "next_actions": ["请提供有效的结构化数据（JSON数组或表格）"]
}
```

### E002: metrics 字段不存在

- **触发条件**：metrics 中的字段名在 dataset 首元素中不存在
- **处理方式**：status = "error"，列出缺失字段
- **输出示例**：

```json
{
  "status": "error",
  "summary": {"total": 0, "key_metrics": {}},
  "trends": [],
  "anomalies": [],
  "insights": [],
  "recommendations": [],
  "missing_fields": ["处理时长", "转化率"],
  "confidence": 0.0,
  "source": "dataset",
  "next_actions": ["字段'处理时长'在数据中不存在，请确认字段名", "字段'转化率'在数据中不存在，请确认字段名"]
}
```

## 分析层异常

### E003: time_field 格式混乱

- **触发条件**：time_field 列中存在无法解析的日期格式，或混用多种格式
- **处理方式**：跳过趋势分析（Step 3），status = "partial"，记入 missing_fields
- **检测方法**：尝试解析 80% 以上数据点的日期，失败则判定为格式混乱
- **降级输出**：trends 为空数组，insights 中不含趋势相关内容

### E004: 数据量太小

- **触发条件**：dataset 行数 < 10
- **处理方式**：执行分析但标注风险，confidence 上限 0.3
- **输出标注**：insights 首条注明"⚠ 数据量仅N条，结论仅供参考"
- **特殊规则**：
  - 行数 < 5：不执行异常检测
  - 行数 < 3：不执行趋势判断

### E005: threshold_config 不合理

- **触发条件**：
  - upper < lower
  - upper 或 lower 为非数值
  - upper = lower = 0（对所有值都异常）
- **处理方式**：忽略该 metric 的自定义阈值，回退到 2σ 规则
- **输出标注**：anomalies 中对应项的 reason 标注"自定义阈值不合理，已回退2σ规则"

### E006: 数值字段混入文本

- **触发条件**：metrics 指定的字段中存在非数值内容
- **处理方式**：
  1. 尝试将文本转为数值（如 "3.5" → 3.5）
  2. 转换失败的行跳过，统计跳过数量
  3. 跳过数 > 50% → 该 metric 标记为不可用
- **输出标注**：missing_fields 中记录 "字段X存在N条非数值数据（已跳过）"

## 输出层异常

### E007: 所有分析步骤被跳过

- **触发条件**：因各种异常导致所有 Step 均未执行
- **处理方式**：status = "error"，列出所有跳过原因
- **与 E001 的区别**：E001 是输入完全无效，E007 是输入存在但因异常无法分析

### E008: 部分分析降级

- **触发条件**：至少 1 个 Step 被跳过，但仍有 Step 执行成功
- **处理方式**：status = "partial"，正常输出已执行部分的结果

## 异常分级

| 级别 | 影响 | 示例 |
|------|------|------|
| 致命 | 无法输出任何结果 | E001, E002, E007 |
| 严重 | 核心分析降级 | E003（趋势不可用） |
| 一般 | 部分数据跳过 | E006（非数值行跳过） |
| 轻微 | 建议调整但不影响分析 | E005（阈值回退）, E004（样本小） |

致命级别 → status = "error"
严重/一般级别 → status = "partial"
轻微级别 → status = "success"（但 confidence 可能降低）
