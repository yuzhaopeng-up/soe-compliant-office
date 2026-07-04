---
name: meeting-minutes
description: >
  Organize and structure meeting minutes from raw transcripts, notes, or documents.
  Extract key information including time, location, participants, decisions, and action items.
  Use when the user asks to: (1) organize meeting notes, (2) extract meeting details,
  (3) create meeting minutes, (4) summarize a meeting, (5) generate meeting summaries,
  (6) parse meeting transcripts, or provides meeting-related content and wants structured output.
  Supports input from plain text, DOCX, PDF, chat records, or voice-to-text transcriptions.
name_cn: 会议纪要整理
description_cn: 整理会议纪要，自动提取时间、地点、参会人、决议事项和待办任务，生成结构化文档
create_source: super-agent-skill-creator
version: 1.0.0
domain: document
soe_relevance: 4
---

# 会议纪要整理

从会议录音转写文本、粗略笔记、聊天记录或文档中，提取关键结构化信息并生成规范的会议纪要文档。

## 工作流程

1. 读取用户提供的会议内容（文本输入或文档文件）
2. 按提取字段解析内容（详见 [references/output_format.md](references/output_format.md)）
3. 构建结构化 JSON 数据
4. 运行 `scripts/generate_minutes.py` 生成 DOCX 文档
5. 向用户交付文档

## 第一步：读取会议内容

支持以下输入方式：

- **直接输入文本**：用户粘贴会议记录、聊天记录、转写文本
- **文档文件**：读取 DOCX/PDF/TXT 等文件内容
- **网页内容**：从在线会议记录中提取

若输入为文档，先提取全部文本内容再进行分析。

## 第二步：提取结构化信息

按以下结构提取，详细提取规则见 [references/output_format.md](references/output_format.md)：

```
{
    "title": "会议名称",
    "time": "YYYY-MM-DD HH:MM-HH:MM",
    "location": "会议地点或线上链接",
    "participants": [{"name": "姓名", "role": "角色"}],
    "absent": ["缺席者"],
    "decisions": [{"id": 1, "content": "决议内容", "notes": "补充"}],
    "action_items": [{"id": 1, "task": "任务", "assignee": "负责人", "deadline": "截止日期", "status": "待启动"}],
    "notes": "其他备注"
}
```

提取要点：

- **会议时间**：标准化为 `YYYY-MM-DD HH:MM-HH:MM` 格式；相对时间转绝对时间
- **参会人员**：区分主持人/记录人/参会人角色；无角色信息则默认为"参会人"
- **决议事项**：仅提取"决定/通过/确认/同意/批准"等确定性表述，排除讨论中未确认内容
- **待办任务**：每条需含任务描述和负责人；无负责人标注"待分配"；无截止日期标注"待定"

## 第三步：生成 DOCX 文档

1. 将提取的结构化 JSON 保存为 `.temp/minutes_data.json`
2. 运行脚本生成文档：

```bash
python scripts/generate_minutes.py --input .temp/minutes_data.json --output <输出路径>
```

输出路径默认为用户工作目录下的 `会议纪要_<会议名称>.docx`。

## 输出格式概览

生成文档包含：居中加粗标题 → 基本信息表格（蓝色标签列） → 决议事项（编号列表） → 待办任务（深蓝表头表格） → 其他备注。

完整格式规范和示例见 [references/output_format.md](references/output_format.md)。
