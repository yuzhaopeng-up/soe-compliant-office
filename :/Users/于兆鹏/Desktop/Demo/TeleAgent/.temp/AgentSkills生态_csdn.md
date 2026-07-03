---
title: 手把手体验114个开源AI Agent Skills：5分钟跑通金融+业务+通信全场景
author: 于兆鹏
date: 2026-06-30
topic: Agent Skills生态
word_count: 3800
target_audience: AI Agent开发者、企业技术架构师
platform: csdn
adapted_from: AgentSkills生态_通用版.md
---

# 手把手体验114个开源AI Agent Skills：5分钟跑通金融+业务+通信全场景

> 想给Agent加发票查验？想多Agent加密通信？想搭NL2SQL网关？114个开源Skill直接拿来用，5分钟跑通全链路。

---

## Step 1：整体认识——三层仓库架构

Agent Skills生态由3个GitHub仓库组成，一共114个Skill，按"金融×业务×通信"三层分工：

| 仓库 | 定位 | Skills数 | 核心能力 |
|------|------|---------|---------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 金融行业层 | 104 | 发票查验、预算管控、风控合规、财富管理 |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | 通用业务层 | 5 | 评分引擎、证据链、数据聚合、NL2Query、可视化 |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | 集群通信层 | 5 | 加密P2P、Redis消息总线、群聊机器人、GitHub异步交接、健康监控 |

**设计逻辑**：行业层解决"做什么"，业务层解决"怎么算"，通信层解决"怎么协作"。

---

## Step 2：Clone金融Skills——零依赖，clone即用

> **注意**：金融层全部使用Python标准库，不依赖任何第三方包，企业内网零配置直接跑。

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills/skills/financial-intelligence/scripts
```

金融层包含7个Skill包、104个场景引擎，覆盖财务、财富、风控三大赛道：

| Skill | 场景数 | 典型用途 |
|-------|--------|---------|
| financial-intelligence | 6 | 发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测 |
| wealth-management | 8 | 资产配置、财务健康、退休规划、保险规划、税务优化等 |
| risk-compliance | 9 | 企业风险评估、信用评级、反欺诈、合规检查、贷后监控等 |
| wecom-template-card | 5 | 企微消息卡片模板 |
| customer-marketing | 18 | 营销话术生成、异议处理、方言适配 |
| product-manual-rag | 3+ | 产品手册智能问答（BM25+TF-IDF双路RAG） |
| application-material-checker | 3 | 进件材料自动核对 |

---

## Step 3：跑通发票查验——30秒看到结果

```bash
python financial_cli.py invoice 011001900111 12345678
```

**运行结果：**

```
## 发票查验结果

✅ 查验结果: 真票

| 项目 | 内容 |
|------|------|
| 发票代码 | 011001900111 |
| 发票号码 | 12345678 |
| 开票单位 | 北京 XX 科技有限公司 |
| 价税合计 | ¥13,335.66 |

🟢 合规状态: 合规 (评分: 100/100)
```

> **踩坑提醒**：发票代码和号码必须是合法格式（12位代码+8位号码），否则会返回格式错误而非查无此票。

---

## Step 4：用Python调用引擎——Engine-Formatter分离架构

所有Skill遵循"Engine负责逻辑，Formatter负责输出"的分层设计，同一个引擎可输出三种格式：

```python
from engines import InvoiceEngine
from formatters import FinancialFormatter

# 创建引擎实例
engine = InvoiceEngine()

# 执行发票查验，返回结构化结果
result = engine.verify("011001900111", "12345678")

# 格式化输出——默认Markdown（适合CLI）
print(FinancialFormatter.format_invoice(result))

# 也可以输出JSON（适合API）
# print(FinancialFormatter.format_invoice(result, output="json"))

# 也可以输出企微卡片（适合IM推送）
# print(FinancialFormatter.format_invoice(result, output="wecom_card"))
```

**运行结果：**

```python
{
    "invoice_code": "011001900111",
    "invoice_number": "12345678",
    "issuer": "北京 XX 科技有限公司",
    "total_amount": 13335.66,
    "verify_status": "valid",
    "compliance_score": 100
}
```

> **重要**：`engine.verify()`返回的是纯数据dict，所有展示逻辑都在Formatter里。如果你要对接自己的前端，只需写一个新Formatter，不用动Engine。

---

## Step 5：Clone通用业务Skills——5个可组合组件

```bash
git clone https://github.com/yuzhaopeng-up/teleagent-skills.git
cd teleagent-skills
```

5个组件独立可用，也可通过Phase-Orchestrator编排成流水线。逐个体验：

### 5.1 NL2Query：自然语言→SQL完整网关

```python
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
```

**运行结果：**

```python
{
    "sql": "SELECT district, COUNT(*) AS cnt FROM complaints WHERE month='2026-05' GROUP BY district ORDER BY cnt DESC LIMIT 5",
    "confidence": 0.92,
    "permission_check": "passed",
    "phases": ["intent_recognition", "permission_check", "sql_generation", "result_format"]
}
```

> **注意**：4-Phase强制编排——意图识别→权限校验→SQL生成→结果格式化，任何一Phase失败都会中断，不会生成不安全SQL。

### 5.2 评分引擎：YAML驱动的规则引擎

```python
from skills.scoring_engine.engine import ScoringEngine

# 加载YAML规则配置
engine = ScoringEngine(rules_path="scoring-rules.yaml")

# 传入客户数据，自动匹配规则打分
customer_data = {
    "company_size": 500,
    "annual_revenue": 80000000,
    "industry": "制造业",
    "years_in_business": 12
}
result = engine.score(customer_data)
```

**运行结果：**

```python
{
    "total_score": 78,
    "dimensions": {
        "scale_score": 25,
        "revenue_score": 20,
        "industry_score": 18,
        "stability_score": 15
    },
    "matched_rules": ["R001", "R003", "R007", "R012"],
    "risk_level": "medium"
}
```

> **踩坑提醒**：YAML规则文件编码必须是UTF-8，中文规则词如果用GBK会匹配失败。

### 5.3 证据链：多源交叉验证

```python
from skills.evidence_chain.engine import EvidenceChainEngine

engine = EvidenceChainEngine()
result = engine.analyze(
    sources=[complaint_data, system_logs, sla_records],
    conflict_rules_path="conflict-rules.yaml"
)
```

**运行结果：**

```python
{
    "conflicts_detected": 1,
    "conflict_detail": "投诉称'2小时未响应'，系统日志显示'1.5小时已回复'",
    "confidence": 0.87,
    "root_cause": "投诉人可能混淆了首次响应与最终解决的时间"
}
```

### 5.4 数据聚合器 + 可视化渲染

聚合器支持校验清洗、聚合计算、同比环比；可视化渲染输出ECharts配置和HTML Dashboard。

**四者组合就是完整链路**：

```
NL2Query → Data Executor → Data Aggregator → Visualization Renderer
"问数据"  →  "查数据"   →  "算结果"    →  "出图表"
```

---

## Step 6：Clone集群通信Skills——5层Agent通信架构

> **注意**：通信层需要`cryptography`和`pyyaml`两个依赖，安装命令在下方。

```bash
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt   # cryptography, pyyaml
python demo.py
```

### 5层通信模型

| 层级 | Skill | 通信模式 | 延迟 | 最佳场景 |
|------|-------|---------|------|---------|
| L1 | encrypted-p2p-messaging | 点对点加密 | <50ms | 敏感数据传输、金融交易 |
| L2 | redis-message-bus | 发布/订阅 | <10ms | 高频状态同步、实时告警 |
| L3 | group-chat-bot | 群聊协作 | ~500ms | 人机混合决策、专家会诊 |
| L4 | github-async-handoff | 异步交接 | 分钟级 | 跨班次任务、长期项目 |
| L5 | cluster-health-monitor | 健康监控 | 周期性 | 全局状态感知、故障自愈 |

### 4种实战组合模式

**模式1：高速通道（L1+L2）**——L1加密保安全，L2 Redis保速度，适合Agent间高频敏感数据交换。

**模式2：人机协同（L1+L3）**——Agent通过L1加密通道推消息到L3群聊，人工审批后回传，适合敏感操作需人工确认。

**模式3：异步接力（L2+L4）**——白班Agent实时处理，下班时L4交接Issue给夜班Agent，实现7×24不间断。

**模式4：全局监控（L2+L5）**——L5周期采集Agent状态，L2广播健康报告，故障自动触发告警。

```python
# demo.py 运行后输出（节选）
# [L1] Encrypted P2P: message sent, latency=32ms
# [L2] Redis Bus: event published to channel 'agent_alerts', latency=8ms
# [L3] Group Chat: human approved action #42, roundtrip=487ms
# [L4] GitHub Handoff: Issue #127 created for night-shift agent
# [L5] Health Monitor: 5/5 agents healthy, next check in 60s
```

> **踩坑提醒**：L2 Redis消息总线需要本地或远程Redis服务，没装Redis的话L2会graceful降级，不影响L1/L3/L4/L5运行。

---

## Step 7：理解技术共性——三个仓库的统一规范

虽然定位不同，三个仓库共享同一套工程规范：

**目录结构统一**：

```
skills/{skill-name}/
├── SKILL.md          # Skill定义（触发词、参数、规则）
├── engine.py         # 核心引擎
├── demo.py           # 可运行演示
├── __init__.py       # 包入口
└── references/       # 知识库（可选）
```

**脱敏与安全**：所有Skill已通过10项脱敏检查——无公司名称、无地区编码、无员工姓名、无合同编号、无真实金额、无设备ID、无电话邮箱、无AIGC水印、无教学专属内容。

**可编排性**：5个业务Skill通过Phase-Orchestrator强制编排，每个Phase由独立Agent执行，Phase间通过结构化JSON传递数据。

---

## 总结

| 要点 | 说明 |
|------|------|
| 零依赖 | 金融层纯Python标准库，clone即用 |
| Engine-Formatter分离 | 同一引擎输出Markdown/JSON/企微卡片三种格式 |
| YAML驱动 | 评分规则改配置不改代码 |
| 5层通信模型 | L1-L5从加密P2P到健康监控，4种组合模式覆盖主流Agent协作场景 |
| Phase-Orchestrator | 业务Skill强制链式编排，"问→查→算→出"一条龙 |
| 10项脱敏 | 所有Skill数据零敏感，可安全开源 |

**三个仓库地址：**

- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104个金融Agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5个通用业务Skill
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5个集群通信Skill

---

## FAQ

**Q：需要什么Python版本？**
A：Python 3.8+，金融层零依赖，业务层和通信层只需`pyyaml`和`cryptography`。

**Q：能在企业内网使用吗？**
A：可以。金融层无任何外部依赖和网络请求，clone到内网直接跑。

**Q：怎么把Skill集成到自己的Agent框架？**
A：每个Skill的`engine.py`是纯逻辑入口，返回dict/JSON。你只需import engine，调用对应方法，把返回结果喂给你的Agent即可。

**Q：5层通信必须全部部署吗？**
A：不需要。5层独立运行，按需组合。只用L1加密通信也完全没问题。

**Q：YAML规则文件从哪来？**
A：仓库自带示例规则文件（`scoring-rules.yaml`、`conflict-rules.yaml`），可直接修改使用。

有问题欢迎提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)，也可以在评论区交流。
