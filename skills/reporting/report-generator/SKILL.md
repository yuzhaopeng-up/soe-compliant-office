---
name: report-generator
name_cn: 报告生成组件
version: 1.0.0
domain: reporting
soe_relevance: 4
description: >
  Report generation component for structured data, business records, meeting notes, and KPI metrics.
  Supports 5 report types: daily/weekly/meeting minutes/issue review/customer briefing.
  Auto-desensitization, confidence scoring, and audit trail logging built-in.
description_cn: >
  报告生成基础组件，粘贴数据即可生成日报、周报、会议纪要、问题复盘、客户汇报等标准文本。
  内置脱敏、置信度评估和审计留痕，适配央国企报告规范。
---

# Report-Generator 报告生成基础组件

**核心理念**：一线学员最爱这个，因为拿来就能用。

**适用人群**：一线人员、班组长、客户经理、支撑人员、培训学员。

**组件定位**：把结构化数据、业务记录、会议要点、经营指标或分析结论快速生成标准文本。模板清晰，适合一线学员改字段、改标题、改口径后马上使用。

---

## 输入参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `report_type` | string | 是 | — | 报告类型：`daily` / `weekly` / `meeting_minutes` / `issue_review` / `customer_brief` |
| `input_data` | string | 是 | — | 结构化数据或文本摘要，可以是自然语言、JSON、关键数字列表 |
| `audience` | string | 否 | `"班组长"` | 报告对象：班组长 / 部门领导 / 客户经理 / 客户方 |
| `tone` | string | 否 | `"简洁"` | 语气风格：`正式` / `简洁` / `汇报型` / `客户友好型` |
| `template_style` | string | 否 | `"standard"` | 模板风格：`one_page`（一页纸简报）/ `standard`（标准模板）/ `brief`（简要版） |
| `max_length` | number | 否 | `1000` | 最大字数限制 |
| `include_next_actions` | boolean | 否 | `true` | 是否包含下一步计划 |

---

## 处理流程

### 步骤 1：报告类型识别

根据 `report_type` 选择对应模板。映射规则：

| report_type | 模板 |
|-------------|------|
| `daily` | 日报模板 |
| `weekly` | 周报模板 |
| `meeting_minutes` | 会议纪要模板 |
| `issue_review` | 问题复盘模板 |
| `customer_brief` | 客户汇报模板 |

若 `report_type` 不在上述范围，进入异常处理（见下方）。

模板详细结构见 [references/report-templates.md](references/report-templates.md)。

### 步骤 2：输入信息整理

从 `input_data` 中提取：
- **关键事实**：事件、动作、结果
- **关键数字**：业务量、完成率、达标率等，必须原样引用，不得编造
- **关键问题**：阻塞项、风险项、超时项
- **责任人**：负责人、参与人、对接人
- **时间节点**：截止日期、计划时间

提取规则：
1. 数字只能来自 `input_data`，缺失的数字不推测、不补零
2. 人名按脱敏规则处理（姓+\*+名最后一字）
3. 缺失的关键信息记入 `missing_fields`

### 步骤 3：结构生成

按所选模板的固定章节顺序生成报告正文。每个章节：
- 有数据则填入
- 无数据则标注 `[缺失：XX]`，同时记入 `missing_fields`
- 不跳过章节，不合并章节

### 步骤 4：风险与问题提炼

从 `input_data` 中识别需要领导/上级关注的事项：
- 超期/超时业务记录
- 未达标指标
- 客户投诉/升级风险
- 资源不足/人手紧张
- 供应商延迟/到货风险

每条风险写明：**风险描述 + 影响范围 + 当前措施（如有）**。

### 步骤 5：下一步计划生成

当 `include_next_actions` 为 `true` 时，从 `input_data` 中提取或推导下一步：
- 每条必须包含：`action`（动作）、`owner`（负责人）、`deadline`（截止时间）
- 负责人和截止时间缺失时标注 `[待确认]`
- 不得编造不存在的计划

### 步骤 6：语言润色

润色规则：
- 保持简洁，去掉冗余修饰
- 不使用"至关重要""深入探讨""织锦"等 AI 套话
- 把不确定事项写为"初步排查为 XX，待确认"，不写成确定结论
- 数字保留原始精度，不四舍五入美化
- `tone` 参数影响措辞风格，但不改变事实内容

### 步骤 7：格式化输出

- 默认输出 Markdown 格式
- 当 `max_length` 限制时，优先保留：关键数字 > 风险提示 > 下一步计划 > 润色修饰
- 超出 `max_length` 时截断正文并在末尾标注 `[已截断，完整内容见 report_body]`
- 外部可复制到飞书/企微/PPT备注/Word/邮件

---

## 标准输出结构

```json
{
  "status": "success | partial | error",
  "report_title": "报告标题，含日期和单位",
  "report_body": "完整报告正文（Markdown）",
  "key_points": ["关键要点1", "关键要点2"],
  "risks": ["风险1：描述+影响", "风险2：描述+影响"],
  "next_actions": [
    {"action": "动作", "owner": "负责人", "deadline": "截止时间"},
    {"action": "动作", "owner": "负责人", "deadline": "截止时间"}
  ],
  "missing_fields": ["缺失字段1", "缺失字段2"],
  "confidence": 0.0,
  "source": "input_data"
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `status` | `success`：数据齐全；`partial`：有缺失但仍可生成；`error`：无法生成 |
| `report_title` | 自动生成，含日期+单位+报告类型 |
| `report_body` | 按模板生成的完整正文 |
| `key_points` | 3~5 条核心要点 |
| `risks` | 需上级关注的风险项 |
| `next_actions` | 可执行动作，每条含 action/owner/deadline |
| `missing_fields` | 输入中缺失但模板要求的关键字段 |
| `confidence` | 0.0~1.0，数据完整度评估：≥0.8 可直接用，0.5~0.8 建议补充，<0.5 不建议直接用 |
| `source` | 固定为 `"input_data"`，声明数据来源 |

### confidence 计算规则

- 模板要求的关键字段全部有值：基础分 0.8
- 每缺失一个关键字段：-0.1
- 有冲突数据：-0.1
- 有风险但无当前措施：-0.05
- 下限 0.1

---

## 报告内容红线

1. **不允许编造不存在的数据** — 输入没写的数字、姓名、事件，不得出现
2. **数字必须来自 input_data** — 不得计算输入中未隐含的指标
3. **缺失信息必须标注** — 用 `[缺失：XX]` 标记，同时记入 `missing_fields`
4. **不确定事项不写成确定结论** — 使用"初步判断""待确认"等措辞
5. **输出适合直接复制** — 适配飞书、企微、PPT 备注、Word、邮件

---

## 异常处理

| 异常场景 | 处理方式 | status |
|---------|---------|--------|
| `input_data` 为空或仅空白 | 返回错误，提示"请提供报告所需的输入数据" | `error` |
| `report_type` 不支持 | 列出支持的 5 种类型，提示用户选择 | `error` |
| 关键数据缺失（如日报无业务量） | 生成报告但标注 `[缺失：XX]`，`missing_fields` 记录，`confidence` 降低 | `partial` |
| 输入中存在冲突数据（如完成数+未完成数≠总数） | 标注冲突，以 `input_data` 原文为准，`confidence` -0.1 | `partial` |
| 输出长度超过 `max_length` | 截断正文，优先保留数字和风险提示，末尾标注截断 | `success` |
| 用户要求夸大或编造不真实表述 | 拒绝编造，返回提示"报告需基于输入数据生成，不支持编造数据" | `error` |
| 人名/手机号未脱敏 | 自动按脱敏规则处理 | `success` |
| `input_data` 格式混乱 | 尽最大努力提取关键信息，降低 `confidence` | `partial` |

---

## 安全与权限要求

### 最小权限原则
- 本组件仅读取 `input_data`，不访问文件系统、数据库或外部 API
- 不主动获取用户身份信息，仅处理输入中提供的内容

### 脱敏规则（默认开启，不可关闭）

| 字段类型 | 脱敏方式 |
|---------|---------|
| 客户姓名 | 姓+\*+名最后一字（张\*明） |
| 手机号 | 前 3 后 4，中间 \*（139\*\*\*\*3681） |
| 证件号 | 前 3 后 1，中间 \*（360\*\*\*\*8） |
| 地址 | 仅保留到区/路（XX区\*\*\*小区） |

### 承诺性语言控制
- 不得生成"保证一定解决""承诺 XX 天完成"等对外承诺，除非 `input_data` 中明确包含该承诺并注明来源
- 对外报告（`audience` 为"客户方"）必须追加提示："本报告需经人工复核后方可对外发送。"

### 审计日志
每次生成记录以下信息：
- `report_type`：报告类型
- `input_summary`：输入数据摘要（前 100 字）
- `output_summary`：输出数据摘要（前 100 字）
- `timestamp`：生成时间
- `status`：生成状态

---

## 央国企特色

### SOE Report Requirements

| SOE报告需求 | 本Skill对应能力 | 实现方式 |
|------------|---------------|---------|
| 国资委月报/快报双头报送 | weekly模板+双audience | 一份数据生成对内/对外两种口径报告 |
| 三重一大决策纪要 | meeting_minutes模板 | 自动标注决策类别、参会人、表决结果 |
| 巡视整改报告 | issue_review模板 | 问题清单+整改措施+完成时限+责任人 |
| 客户汇报材料 | customer_brief模板 | 执行摘要+数据表格+行动建议三段式 |
| GB/T 9704格式适配 | 标题/编号/密级支持 | 模板支持文号、密级、紧急程度标注 |
| 对外报告人工复核 | audience="客户方"自动触发 | 追加"本报告需经人工复核后方可对外发送" |

### SOE Report Type Extension

央国企场景下的报告类型映射：

| report_type | SOE典型场景 | SOE特殊要求 |
|------------|-----------|-----------|
| daily | 日报/值班简报 | 含值班人员、突发事项、领导批示 |
| weekly | 周报/国资委快报 | 双口径（对内详/对外简） |
| meeting_minutes | 会议纪要（党委会/董事会/总经理办公会） | 三会模板+表决记录+出席情况 |
| issue_review | 问题复盘/巡视整改 | 问题清单+整改措施+时限+责任人 |
| customer_brief | 客户汇报/上级汇报 | 执行摘要+数据+建议，一页纸优先 |

---

## 上游组件接入

本组件可直接接收以下上游组件的输出作为 `input_data`：

| 上游组件 | 输出格式 | 接入方式 |
|---------|---------|---------|
| Info-Extractor | 结构化 JSON | 直接传入 `input_data` |
| Data-Analyst | 分析结论 JSON | 直接传入 `input_data` |

示例串联流程：
```
原始消息 → Info-Extractor（提取结构化字段）→ Data-Analyst（分析异常/趋势）→ Report-Generator（生成报告）
```

---

## 参考资源

- **报告模板库**：[references/report-templates.md](references/report-templates.md) — 5 类内置模板完整结构
- **演示数据**：[references/demo-data.md](references/demo-data.md) — 9 个央国企业务场景脱敏数据 + 生成示例
- **课堂指南**：[references/classroom-guide.md](references/classroom-guide.md) — 3 分钟演示脚本 + 学员操作指南

---

## 自查清单

> 判断此 Skill 是否可交付、可复用、可上线测试。

### 模板完整度

- [ ] 5 种报告类型均有对应模板
- [ ] 每种模板至少支持 1 种 `template_style`
- [ ] 模板章节齐全，无空章节
- [ ] 模板可在飞书/企微/Word 中正确显示

### 事实来源

- [ ] 报告中所有数字均来自 `input_data`
- [ ] 无编造数据的情况
- [ ] 缺失数字标注为 `[缺失：XX]`，未用 0 填充
- [ ] 不确定结论使用"待确认"表述

### 缺失标记

- [ ] `missing_fields` 正确记录所有缺失项
- [ ] `confidence` 分数与数据完整度匹配
- [ ] 报告正文中缺失位置有 `[缺失：XX]` 标记
- [ ] 生成 `partial` 状态时提示用户补充数据

### 脱敏

- [ ] 客户姓名已脱敏
- [ ] 手机号已脱敏
- [ ] 证件号已脱敏
- [ ] 地址仅保留到区/路级别
- [ ] 脱敏规则不依赖用户手动触发

### 可复制性

- [ ] 输出可直接复制到飞书/企微
- [ ] Markdown 格式在常见平台中正确渲染
- [ ] 另一学员仅改 `report_type` 和 `input_data` 即可生成不同报告
- [ ] 无硬编码的单位名/人名/指标名
- [ ] 模板中的占位符清晰可替换

### 安全合规

- [ ] 无对外承诺性语言（除非输入明确授权）
- [ ] 对外报告有人工复核提示
- [ ] 审计日志字段完整

### 课堂可用

- [ ] 演示数据为脱敏央国企业务数据
- [ ] 3 分钟演示脚本人人可执行
- [ ] 学员操作指南步骤清晰，无需技术背景
- [ ] 上游组件（Info-Extractor、Data-Analyst）接入方式已说明
