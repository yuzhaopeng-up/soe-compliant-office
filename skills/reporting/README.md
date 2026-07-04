# Reporting & Analysis Domain (Phase 3)

> **报告分析域** — 6个Skill构建央国企经营分析闭环：数据采集 → 分析洞察 → 报告生成 → 政策解读 → 社保精算

## Skills Overview

| Skill | 核心能力 | SOE Relevance | Type |
|-------|---------|---------------|------|
| [report-generator](./report-generator/) | 6类报告模板（日报/周报/会议纪要/复盘/简报/客户汇报），4-Phase自动生成 | 5 | Prompt |
| [data-analyst](./data-analyst/) | 5维度分析（汇总/趋势/异常/对比/洞察），7大央国企场景 | 5 | Prompt |
| [finance-expert](./finance-expert/) | 财务分析+税务计算+预算管控，EVA/国资委考核指标 | 5 | Prompt |
| [business-analysis](./business-analysis/) | 五层级经营分析框架，"一利五率"KPI体系 | 5 | Prompt |
| [gov-report-analyzer](./gov-report-analyzer/) | 政府经济报告6维解读，政策力度指数+A股板块影响 | 5 | Prompt |
| [social-security-advisor](./social-security-advisor/) | 五险一金精算+退休金测算+断缴分析，含Python计算引擎 | 4 | Prompt+Python |

## Reporting Pipeline

```
数据采集 ──→ 分析洞察 ──→ 报告生成 ──→ 政策解读 ──→ 专项精算
data        finance/     report       gov-report   social-
analyst     business     generator    analyzer     security
```

## SOE Features Covered

- 国资委月报/快报双头报送
- "一利五率"央国企KPI考核体系
- EVA经济增加值计算
- 穿透式监管数据呈现
- 政府工作报告6维解读+板块影响分析
- GB/T 9704报告格式合规
- DA/T电子归档标准
- 中央企业合规管理办法

## Skill Dependencies

- `data-analyst` feeds structured insights to `report-generator` and `business-analysis`
- `finance-expert` uses `data-analyst` for financial metric computation
- `gov-report-analyzer` feeds policy signals to `business-analysis` for strategic alignment
- `social-security-advisor` provides Python calculation engine (`scripts/`)

> Note: Each skill is self-contained. Audit trail, data desensitization, and SOE standards are integration points to implement per your infrastructure.
