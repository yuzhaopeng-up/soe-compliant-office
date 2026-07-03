---
title: "我用114个开源Skill搭了套AI Agent全链路生态，效率直接拉满"
author: 于兆鹏
date: 2026-06-30
topic: Agent Skills生态
word_count: 3800
platform: juejin
adapted_from: AgentSkills生态_通用版.md
---

# 我用114个开源Skill搭了套AI Agent全链路生态，效率直接拉满

给大家分享一个我最近在搞的事情——给AI Agent搭一套从金融业务到集群通信的全链路Skill生态，总共114个开源Skill，三个仓库，直接把企业级Agent开发的重复造轮子问题给终结了。

之前我遇到过一个很头疼的场景：想给Agent加个发票查验，得从头写规则引擎；想让多个Agent之间加密通信，没有现成协议层；想搞个NL2SQL查询网关，权限校验、意图识别、执行、聚合这些组件怎么编排完全没谱。

现在这些问题，一套生态全解决了。

---

## 三仓库架构：金融 × 业务 × 通信

三个GitHub仓库，各管一层：

| 仓库 | 定位 | Skills数 | 干啥的 |
|------|------|---------|--------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 金融行业层 | 104 | 发票查验、预算管控、风控合规、财富管理 |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | 通用业务层 | 5 | 评分引擎、证据链、数据聚合、NL2Query、可视化 |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | 集群通信层 | 5 | 加密P2P、Redis消息总线、群聊机器人、GitHub异步交接、健康监控 |

一句话总结设计逻辑：**行业层解决"做什么"，业务层解决"怎么算"，通信层解决"怎么协作"**。

---

## 金融层：104个Skills，clone即用

[financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) 是最大的仓库，7个Skill包、104个场景引擎，覆盖财务、财富、风控三大赛道。

先看最常用的发票查验，30秒上手：

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678
```

跑完直接出结果：

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

这里有个关键设计决策：**全部Python标准库，零第三方依赖**。好处很明显——企业内网不用配pip镜像，无供应链风险，响应时间<100ms。

引擎和输出是分离的：

```python
from engines import InvoiceEngine
from formatters import FinancialFormatter

engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))
```

同一套引擎，CLI出Markdown、企微推卡片、API返JSON，全靠Formatter切换。

7个Skill包一览：

| Skill | 场景数 | 典型用途 |
|-------|--------|---------|
| financial-intelligence | 6 | 发票查验、预算管控、财报速读、税务筹划 |
| wealth-management | 8 | 资产配置、财务健康、退休规划、保险规划 |
| risk-compliance | 9 | 企业风险评估、信用评级、反欺诈、合规检查 |
| wecom-template-card | 5 | 企微消息卡片模板 |
| customer-marketing | 18 | 营销话术生成、异议处理、方言适配 |
| product-manual-rag | 3+ | 产品手册智能问答（BM25+TF-IDF双路RAG） |
| application-material-checker | 3 | 进件材料自动核对 |

---

## 业务层：5个组件，随意组合

[teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) 的5个Skill，单拎出来能独立用，串起来就是一条流水线。

**NL2Query**：自然语言到SQL的完整网关，4-Phase编排——意图识别→权限校验→SQL生成→结果格式化：

```python
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
# 输出：SQL语句 + 置信度 + 权限校验结果
```

**评分引擎**：YAML驱动，业务变了改配置不用改代码：

```python
from skills.scoring_engine.engine import ScoringEngine

engine = ScoringEngine(rules_path="scoring-rules.yaml")
result = engine.score(customer_data)
# 输出：总分 + 各维度得分 + 命中规则列表
```

**证据链**：多源交叉验证，出冲突检测+置信度+根因推断：

```python
from skills.evidence_chain.engine import EvidenceChainEngine

engine = EvidenceChainEngine()
result = engine.analyze(
    sources=[complaint_data, system_logs, sla_records],
    conflict_rules_path="conflict-rules.yaml"
)
```

加上**数据聚合器**（校验清洗、同比环比）和**可视化渲染**（ECharts+HTML Dashboard），四者组合就是一条完整的 **"问数据→算结果→出图表"** 链路。

---

## 通信层：5层架构，4种组合模式

[agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) 是三个仓库里架构最精巧的，5层通信模型：

| 层级 | Skill | 通信模式 | 延迟 | 场景 |
|------|-------|---------|------|------|
| L1 | encrypted-p2p-messaging | 点对点加密 | <50ms | 金融交易、敏感数据 |
| L2 | redis-message-bus | 发布/订阅 | <10ms | 实时告警、高频同步 |
| L3 | group-chat-bot | 群聊协作 | ~500ms | 人机混合决策 |
| L4 | github-async-handoff | 异步交接 | 分钟级 | 跨班次任务接力 |
| L5 | cluster-health-monitor | 健康监控 | 周期性 | 全局状态、故障自愈 |

这5个Skill不是孤立的，有4种验证过的组合模式：

- **高速通道（L1+L2）**：加密保安全，Redis保速度，适合高频敏感数据交换
- **人机协同（L1+L3）**：Agent处理敏感操作→群聊推确认→人工审批→结果回传
- **异步接力（L2+L4）**：白班Redis实时处理→下班GitHub Issue交接给夜班→7×24不停
- **全局监控（L2+L5）**：健康监控周期采集→Redis广播→故障自动告警

30秒跑完5层Demo：

```bash
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt  # cryptography, pyyaml
python demo.py
```

---

## 三个仓库的工程共性

虽然定位不同，但共享一套规范：

**目录结构统一**——所有Skill都是`SKILL.md`定义+`engine.py`引擎+`demo.py`演示的三件套，开箱即跑。

**引擎-格式化分离**——同一套逻辑，CLI出Markdown、API返JSON、IM推卡片，全靠Formatter切换。

**脱敏安全**——10项检查全覆盖：无公司名、无地区码、无员工名、无合同号、无真实金额、无设备ID、无电话邮箱、无AIGC水印、无教学内容。

**可编排性**——Phase-Orchestrator强制链式调用：

```
NL2Query → Data Executor → Data Aggregator → Visualization Renderer
```

每个Phase独立Agent执行，Phase间结构化JSON传递。

---

## 快速开始

```bash
# 金融Skills（零依赖，clone即用）
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills/skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678

# 通用业务Skills
git clone https://github.com/yuzhaopeng-up/teleagent-skills.git
cd teleagent-skills && python demo.py

# 集群通信Skills
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm && pip install -r requirements.txt && python demo.py
```

---

## 写在最后

这套生态的核心价值不在于某个具体的发票引擎或加密通道，而在于**架构模式**：

1. **Engine-Formatter分离**——通用到任何Agent框架
2. **5层通信模型**——Agent集群协作的参考架构
3. **YAML驱动规则引擎**——业务变化改配置不改代码
4. **Phase-Orchestrator编排**——组件化Skill的可组合范式

如果你在搞企业级Agent系统，这套东西能省掉大量重复造轮子的时间。直接拿来用也行，架构有启发Star一下也行。

相关仓库：
- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104个金融Agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5个通用业务Skill
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5个集群通信Skill

有问题提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)，也欢迎在评论区聊聊你们团队是怎么给Agent做Skill拆分的，互相交流下经验。
