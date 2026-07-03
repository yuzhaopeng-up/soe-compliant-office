---
title: "Agent Skills开源生态：114个Skills的企业级Agent全链路实践"
author: 于兆鹏
date: 2026-06-30
topic: Agent Skills生态
word_count: 4500
target_audience: AI Agent开发者、企业技术架构师、开源社区
platform: oschina
adapted_from: AgentSkills生态_通用版.md
---

# Agent Skills开源生态：114个Skills的企业级Agent全链路实践

2026年，AI Agent从"单兵作战"进入"集群协作"阶段。LangChain、CrewAI、AutoGen等框架解决了Agent的调度问题，但一个关键缺口始终存在——**Agent的能力从哪来？** 每个企业都在重复造轮子：发票查验写一遍、NL2SQL写一遍、Agent间通信又写一遍。

本文的核心观点：**Agent Skills应该是可复用的开源组件，而非每次从零开始的私有工程。** 我们开源了114个Skills，覆盖金融行业、通用业务、集群通信三层，并提供了一套从目录结构到编排模式的工程规范，希望为Agent生态补上"能力层"这一块拼图。

## 三仓库生态：金融×业务×通信的三层架构

三个GitHub仓库，各自独立可用，又可组合编排：

| 仓库 | 定位 | Skills数 | 核心能力 | Star |
|------|------|---------|---------|------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 金融行业层 | 104 | 发票查验、预算管控、风控合规、财富管理 | 开源 |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | 通用业务层 | 5 | 评分引擎、证据链、数据聚合、NL2Query、可视化 | 开源 |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | 集群通信层 | 5 | 加密P2P、Redis消息总线、群聊机器人、GitHub异步交接、健康监控 | 开源 |

```
┌─────────────────────────────────────────────────────┐
│                  Agent Skills 生态                    │
├──────────────┬────────────────┬─────────────────────┤
│ 金融行业层    │  通用业务层     │  集群通信层          │
│ 104 Skills   │  5 Skills      │  5 Skills           │
│              │                │                     │
│ · 发票查验    │ · 评分引擎     │ · L1 加密P2P        │
│ · 预算管控    │ · 证据链分析   │ · L2 Redis消息总线  │
│ · 风控合规    │ · 数据聚合器   │ · L3 群聊机器人     │
│ · 财富管理    │ · NL2Query    │ · L4 GitHub异步交接 │
│ · 营销话术    │ · 可视化渲染   │ · L5 健康监控       │
└──────────────┴────────────────┴─────────────────────┘
```

设计逻辑很清晰：**行业层解决"做什么"，业务层解决"怎么算"，通信层解决"怎么协作"**。这三层基本覆盖了企业级Agent系统从业务执行到集群编排的全链路。

## 金融行业层：104个Skills，纯Python零依赖

[financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) 是生态中体量最大的仓库——7个Skill包、104个场景引擎，覆盖财务、财富、风控三大金融赛道。

### 30秒上手发票查验

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678
```

输出：

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

### 关键设计：纯标准库，零第三方依赖

这是个经过深思熟虑的工程决策。金融企业内网环境普遍存在pip镜像配置、供应链审计等限制，**全部使用Python标准库意味着**：

| 收益 | 说明 |
|------|------|
| 安装成本为零 | clone即用，无需pip install |
| 内网友好 | 无需配置私有pip镜像 |
| 无供应链风险 | 不依赖任何第三方包，规避typo squatting等攻击面 |
| 响应快 | 平均响应时间 < 100ms |

在LLVM Supply Chain Attack频发的当下，零依赖对金融场景不是"nice to have"，而是刚需。

### Engine-Formatter分离架构

```python
from engines import InvoiceEngine
from formatters import FinancialFormatter

engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))
```

引擎层（Engine）负责业务逻辑，格式化层（Formatter）负责输出适配。这种分离让你可以：

- CLI中输出Markdown
- 企业微信/飞书直接推送卡片
- API中返回JSON给前端

**这套Engine-Formatter模式是三个仓库的共享规范**，后面会专门讲。

### 7大Skill包一览

| Skill | 场景数 | 典型用途 |
|-------|--------|---------|
| financial-intelligence | 6 | 发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测 |
| wealth-management | 8 | 资产配置、财务健康、退休规划、保险规划、税务优化等 |
| risk-compliance | 9 | 企业风险评估、信用评级、反欺诈、合规检查、贷后监控等 |
| wecom-template-card | 5 | 企微消息卡片模板 |
| customer-marketing | 18 | 营销话术生成、异议处理、方言适配 |
| product-manual-rag | 3+ | 产品手册智能问答（BM25+TF-IDF双路RAG） |
| application-material-checker | 3 | 进件材料自动核对 |

其中 `customer-marketing` 的18个场景比较有意思——覆盖了从话术生成到方言适配的全链路，在电信、银行等电销场景中直接可用。

## 通用业务层：5个可组合的组件化Skill

[teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) 的5个Skill每个都能独立运行，但真正的价值在于组合——通过Phase-Orchestrator编排成流水线。

### NL2Query：自然语言到SQL的完整网关

```python
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
# 输出：SQL语句 + 置信度 + 权限校验结果
```

4-Phase编排：意图识别 → 权限校验 → SQL生成 → 结果格式化。每个Phase由独立Agent执行，Phase间通过结构化JSON传递数据。**这不是简单的prompt拼接，而是带有权限校验和审计日志的企业级网关。**

### 评分引擎：YAML驱动的规则引擎

```python
from skills.scoring_engine.engine import ScoringEngine

engine = ScoringEngine(rules_path="scoring-rules.yaml")
result = engine.score(customer_data)
# 输出：总分 + 各维度得分 + 命中规则列表
```

业务规则存在YAML配置中，**业务变了改配置不用改代码**。这对企业场景很重要——评分规则变更走配置审批流程即可，不需要发版。

### 证据链：多源交叉验证

```python
from skills.evidence_chain.engine import EvidenceChainEngine

engine = EvidenceChainEngine()
result = engine.analyze(
    sources=[complaint_data, system_logs, sla_records],
    conflict_rules_path="conflict-rules.yaml"
)
# 输出：冲突检测结果 + 置信度评分 + 根因推断
```

投诉处理、故障诊断等场景中，单一数据源往往不够。证据链引擎从多个独立源提取证据、交叉验证、检测冲突，最终输出置信度评分和根因推断。

### 数据聚合器 + 可视化渲染

数据聚合器支持校验清洗、聚合计算、同比环比；可视化渲染输出ECharts配置和HTML Dashboard。

四者组合就是一条完整的**"问数据→算结果→出图表"**链路：

```
NL2Query(意图识别) → Data Executor(安全查询) → Data Aggregator(聚合计算) → Visualization(ECharts图表)
```

## 集群通信层：Agent间协作的5层模型

[agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) 是三个仓库中架构设计最精巧的。当Agent从单机走向集群，通信协议就是基础设施。

### L1-L5分层设计

| 层级 | Skill | 通信模式 | 延迟 | 最佳场景 |
|------|-------|---------|------|---------|
| L1 | encrypted-p2p-messaging | 点对点加密 | <50ms | 敏感数据传输、金融交易 |
| L2 | redis-message-bus | 发布/订阅 | <10ms | 高频状态同步、实时告警 |
| L3 | group-chat-bot | 群聊协作 | ~500ms | 人机混合决策、专家会诊 |
| L4 | github-async-handoff | 异步交接 | 分钟级 | 跨班次任务、长期项目 |
| L5 | cluster-health-monitor | 健康监控 | 周期性 | 全局状态感知、故障自愈 |

这5层的设计参考了OSI模型的思想，但针对Agent集群的特点做了裁剪——比如L4的GitHub异步交接，就是利用Issue作为Agent间的任务队列，天然具备审计日志和版本追踪。

### 4种经过验证的组合模式

5个Skill不是孤立的，以下4种组合模式已在实际项目中验证：

**模式1：高速通道（L1+L2）**
两个Agent高频交换敏感数据——L1加密通道保安全，L2 Redis总线保速度。金融交易场景的标准配置。

**模式2：人机协同（L1+L3）**
Agent处理敏感操作时，通过L1加密通道推送确认消息到L3群聊机器人，人工审批后结果回传。满足金融行业的"双人复核"要求。

**模式3：异步接力（L2+L4）**
白班Agent实时处理，下班时通过L4 GitHub交接Issue给夜班Agent，实现7×24不间断服务。

**模式4：全局监控（L2+L5）**
L5健康监控器周期性采集Agent状态，通过L2 Redis总线广播健康报告，故障时自动触发告警和故障转移。

### 故障转移决策流

```
                Agent故障检测
                     │
            ┌────────┴────────┐
            ↓                 ↓
      有备援Agent?         无备援Agent?
            │                 │
       ┌────┴────┐       ┌────┴────┐
       ↓         ↓       ↓         ↓
    L1切换    L2通知   L4创建    L5标记
    加密通道  全局广播  交接Issue  降级运行
```

### 30秒体验完整5层

```bash
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt  # cryptography, pyyaml
python demo.py
```

## 三个仓库的技术共性

不同定位，同一套工程规范，这是设计上的刻意为之——降低组合使用时的心智负担。

### 目录结构统一

```
skills/{skill-name}/
├── SKILL.md          # Skill定义（触发词、参数、规则）
├── engine.py         # 核心引擎
├── demo.py           # 可运行演示
├── __init__.py       # 包入口
└── references/       # 知识库（可选）
```

`SKILL.md` 类似前端生态的 `package.json`，是Skill的元数据入口——触发词、参数定义、编排规则、防御规则都在这里声明。任何兼容此目录结构的Skill都可以被Phase-Orchestrator自动编排。

### 引擎-格式化分离

所有Skill遵循"Engine负责逻辑，Formatter负责输出"的分层。同一个发票查验引擎，可以输出Markdown（CLI）、JSON（API）或企微卡片（IM）。这和MVC中Model与View的分离是同一个思路。

### 脱敏与安全

所有Skill已通过10项脱敏检查：

| 检查项 | 状态 |
|--------|------|
| 无公司名称 | ✅ |
| 无地区编码 | ✅ |
| 无员工姓名 | ✅ |
| 无合同编号 | ✅ |
| 无真实金额 | ✅ |
| 无设备ID | ✅ |
| 无电话邮箱 | ✅ |
| 无AIGC水印 | ✅ |
| 无教学专属内容 | ✅ |
| 无内部术语 | ✅ |

开源项目的脱敏合规是很多团队容易忽视的，尤其金融场景中数据泄露风险极高。10项检查是底线，不是上限。

### 可编排性

teleagent-skills中的5个Skill通过Phase-Orchestrator强制编排为链式流水线，每个Phase由独立Agent执行，Phase间通过结构化JSON传递数据。这种设计参考了Unix Pipeline的理念——每个组件做好一件事，组合起来就是强大的流水线。

## 开源的意义

三个仓库的核心价值不在于某个具体的发票查验引擎或加密通道，而在于**架构模式**：

1. **Engine-Formatter分离**——通用到任何Agent框架，不绑定特定runtime
2. **5层通信模型**——为Agent集群协作提供参考架构，类比对OSI模型对网络协议的意义
3. **YAML驱动的规则引擎**——业务变化时改配置不改代码，降低Agent系统的维护成本
4. **Phase-Orchestrator编排**——组件化Skill的可组合范式，Unix Pipeline思想在Agent时代的延续

2026年Agent生态的竞争焦点正在从"框架"转向"能力"，LangChain/CrewAI解决了调度问题，但能力的复用仍然是空白。**我们希望这114个Skills和背后的架构模式，能为Agent开源生态的"能力层"提供一个起点。**

## 快速开始

```bash
# 金融Skills（零依赖，clone即用）
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills/skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678

# 通用业务Skills
git clone https://github.com/yuzhaopeng-up/teleagent-skills.git
cd teleagent-skills
python demo.py

# 集群通信Skills
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt
python demo.py
```

## 总结与思考

| 维度 | 要点 |
|------|------|
| 生态规模 | 3仓库114个Skills，覆盖金融×业务×通信三层 |
| 工程规范 | 统一目录结构、Engine-Formatter分离、10项脱敏检查 |
| 架构创新 | 5层通信模型、Phase-Orchestrator编排、YAML驱动规则引擎 |
| 开源价值 | 不是代码本身，而是可复用的架构模式 |

一个思考：当前Agent生态重框架轻能力的格局，和早期前端生态重jQuery/CSS框架、轻组件库的阶段很像。React/Vue之后，组件生态（Ant Design、Element UI）才真正爆发。**Agent Skills能否成为Agent生态的"组件库"？** 这需要更多的社区参与——如果你正在构建Agent系统，欢迎Fork、PR、提Issue，一起把这个能力层做厚。

### 延伸阅读

- [LangChain Skills设计模式](https://docs.langchain.com/) — Agent能力扩展的标准接口设计
- [CrewAI Agent协作框架](https://docs.crewai.com/) — 多Agent编排与角色分配
- [AutoGen多Agent对话](https://microsoft.github.io/autogen/) — 微软的多Agent对话框架
- [OSI七层模型](https://en.wikipedia.org/wiki/OSI_model) — 集群通信5层模型的设计参照
- [Unix Pipeline哲学](https://en.wikipedia.org/wiki/Pipeline_(Unix)) — Phase-Orchestrator的思想源头

---

**相关链接：**

- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104个金融Agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5个通用业务Skill
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5个集群通信Skill

有问题欢迎提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)，也可以在评论区交流。
