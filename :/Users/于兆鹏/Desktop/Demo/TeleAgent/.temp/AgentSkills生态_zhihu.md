---
title: 114个开源AI Agent Skills，凭什么覆盖企业全场景？
author: 于兆鹏
date: 2026-06-30
topic: Agent Skills生态
word_count: 5200
target_audience: AI Agent开发者、企业技术架构师
platform: zhihu
adapted_from: AgentSkills生态_通用版.md
---

# 114个开源AI Agent Skills，凭什么覆盖企业全场景？

你的AI Agent能查发票吗？

大概率不能。不是Agent不够聪明，而是没有"查发票"这个能力单元。同理，想让多个Agent安全地交换敏感数据？想让自然语言直接变成可执行的SQL？想让Agent集群7×24不掉线？每一个需求背后，都需要一个专门的Skill来承载。

但问题是——这些Skill从哪来？自己写？一个发票查验引擎，从规则定义到格式化输出，至少一周。5个Agent之间的加密通信层？一个月起步。

如果有人已经把114个这样的Skill开源了呢？

## 三仓库，三层架构：金融×业务×通信

Agent Skills生态由三个GitHub仓库组成，乍一看是三个独立项目，实际上遵循一套严格的分层逻辑：

| 仓库 | 定位 | Skills数 | 核心能力 |
|------|------|---------|---------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 金融行业层 | 104 | 发票查验、预算管控、风控合规、财富管理 |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | 通用业务层 | 5 | 评分引擎、证据链、数据聚合、NL2Query、可视化 |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | 集群通信层 | 5 | 加密P2P、Redis消息总线、群聊机器人、GitHub异步交接、健康监控 |

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

> **行业层解决"做什么"，业务层解决"怎么算"，通信层解决"怎么协作"。**

这三句话听起来像口号，但当你深入到仓库代码里，会发现每个Skill的设计确实遵循这套逻辑——行业层只关心业务语义，业务层只关心计算范式，通信层只关心消息传递。没有越界，没有耦合。

## 104个金融Skills：做行业层，必须做到"开箱即验证"

[financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) 是三个仓库中规模最大的，7个Skill包、104个场景引擎，覆盖财务、财富、风控三大赛道。

行业层的Skill有什么特殊？四个字：**开箱即验证**。金融行业的AI应用，最怕的不是功能缺失，而是"看起来能用，实际上不敢用"。所以这个仓库做了一个关键决策——

### 纯Python，零依赖

全部使用Python标准库，不依赖任何第三方包。这不是偷懒，而是刻意的设计约束：

- 企业内网环境无需配置pip镜像，clone即用
- 零供应链安全风险——你不用审计requests或numpy的版本漏洞
- 安装成本严格为零
- 平均响应时间 < 100ms

> **金融场景的安全合规，不是靠审计报告，而是靠架构约束。零依赖就是最强的约束。**

30秒跑通发票查验：

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

### 引擎与格式化分离：一个核心，三种输出

```python
# 这段代码解决了"同一个引擎适配多种输出渠道"的问题
# Engine只管业务逻辑，Formatter只管输出格式
from engines import InvoiceEngine
from formatters import FinancialFormatter

engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))
```

为什么要分离？因为在企业级场景中，同一个发票查验结果，可能需要三种输出：

- CLI里输出Markdown——给开发者调试
- 企微/飞书里推卡片——给业务人员查看
- API里返回JSON——给前端消费

> **Engine-Formatter分离不是过度设计，而是企业级Agent Skill能否被复用的前提条件。**

### 7个Skill包的覆盖范围

| Skill | 场景数 | 典型用途 |
|-------|--------|---------|
| financial-intelligence | 6 | 发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测 |
| wealth-management | 8 | 资产配置、财务健康、退休规划、保险规划、税务优化等 |
| risk-compliance | 9 | 企业风险评估、信用评级、反欺诈、合规检查、贷后监控等 |
| wecom-template-card | 5 | 企微消息卡片模板 |
| customer-marketing | 18 | 营销话术生成、异议处理、方言适配 |
| product-manual-rag | 3+ | 产品手册智能问答（BM25+TF-IDF双路RAG） |
| application-material-checker | 3 | 进件材料自动核对 |

104个场景，覆盖了金融行业从"看到发票"到"做出决策"的全链路。但值得注意的是，这些Skill不是"能用"就算——每个都带合规评分、脱敏输出、格式化适配，达到的是"敢用"的标准。

## 5个业务组件：可独立，可编排

[teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) 只有5个Skill，但它们的设计思路和金融层完全不同——这里追求的不是场景覆盖，而是**可组合性**。

### NL2Query：从一句话到一条SQL，中间需要几步？

用户说"查询上月投诉量排前5的区县"，Agent拿到这句话后要做什么？直接让LLM生成SQL？那权限校验谁做？SQL注入谁防？结果格式谁管？

```python
# 这段代码解决了"自然语言查询的安全性问题"
# 不是直接让LLM生成SQL，而是经过4个Phase的强制编排
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
# 输出：SQL语句 + 置信度 + 权限校验结果
```

4-Phase编排：**意图识别 → 权限校验 → SQL生成 → 结果格式化**。每个Phase由独立Agent执行，Phase间通过结构化JSON传递数据。任何一环失败，整条链路中止。

> **自然语言转SQL不难，难的是转出来的SQL安全、可审计、可回溯。**

### 评分引擎：业务规则参数化，改配置不改代码

```python
# 这段代码解决了"业务规则频繁变化时重复改代码"的问题
# 所有规则参数化存在YAML中，业务变了改配置文件即可
from skills.scoring_engine.engine import ScoringEngine

engine = ScoringEngine(rules_path="scoring-rules.yaml")
result = engine.score(customer_data)
# 输出：总分 + 各维度得分 + 命中规则列表
```

这是我在企业级场景中见过最常见的需求变化——评分规则三个月一调。如果每次调规则都要改代码、走发布流程，效率低到不可接受。YAML驱动的规则引擎，让业务人员自己就能调整权重和阈值。

### 证据链：多源数据，谁在说谎？

```python
# 这段代码解决了"多个数据源之间信息冲突时的根因推断"问题
# 客户说A、系统日志说B、SLA记录说C——到底谁是对的？
from skills.evidence_chain.engine import EvidenceChainEngine

engine = EvidenceChainEngine()
result = engine.analyze(
    sources=[complaint_data, system_logs, sla_records],
    conflict_rules_path="conflict-rules.yaml"
)
# 输出：冲突检测结果 + 置信度评分 + 根因推断
```

### 数据聚合 + 可视化：从数字到图表的最后一公里

数据聚合器支持校验清洗、聚合计算、同比环比；可视化渲染输出ECharts配置和HTML Dashboard。二者与前三个Skill组合，就是一条完整的**"问数据→算结果→出图表"**链路：

```
NL2Query → Data Executor → Data Aggregator → Visualization Renderer
```

> **5个组件不是5个工具，而是排列组合后可以生成数十条业务流水线的基础设施。**

## 集群通信层：5层模型，Agent集群的"操作系统"

[agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) 是三个仓库中架构设计最精巧的。它回答了一个很少被讨论但极其重要的问题——**Agent之间怎么通信？**

单个Agent很聪明，但多个Agent组成集群后，通信就成了瓶颈。点对点直连？安全隐患。广播？信息过载。异步传递？延迟不可控。这个仓库定义了5层通信模型，从延迟最低到最安全，逐层递进：

| 层级 | Skill | 通信模式 | 延迟 | 最佳场景 |
|------|-------|---------|------|---------|
| L1 | encrypted-p2p-messaging | 点对点加密 | <50ms | 敏感数据传输、金融交易 |
| L2 | redis-message-bus | 发布/订阅 | <10ms | 高频状态同步、实时告警 |
| L3 | group-chat-bot | 群聊协作 | ~500ms | 人机混合决策、专家会诊 |
| L4 | github-async-handoff | 异步交接 | 分钟级 | 跨班次任务、长期项目 |
| L5 | cluster-health-monitor | 健康监控 | 周期性 | 全局状态感知、故障自愈 |

5层不是5种选择，而是5种互补。在实际场景中，几乎不会只单用一层，而是组合使用。

### 4种经过验证的组合模式

**模式1：高速通道（L1+L2）**——两个Agent需要高频交换敏感数据。L1加密通道保安全，L2 Redis总线保速度。缺一不可。

**模式2：人机协同（L1+L3）**——Agent处理敏感操作时，通过L1加密通道向L3群聊推送确认消息，人工在群聊中审批后回传。解决了"AI不敢替人做主"的问题。

**模式3：异步接力（L2+L4）**——白班Agent通过L2实时处理，下班时通过L4创建GitHub Issue交接给夜班Agent。这就是7×24不间断服务的底层支撑。

**模式4：全局监控（L2+L5）**——L5采集Agent状态，通过L2广播健康报告。任一Agent故障，立即告警。

> **5层通信模型的价值不在于单层有多强，而在于层与层之间的组合能覆盖从"两个Agent聊天的安全"到"整个集群的自愈"的全频谱需求。**

### 故障转移决策流

当Agent集群中某个节点故障，集群如何自愈？这不是理论问题，而是运维实践中每天都在发生的场景：

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

有备援？L1切换加密通道到备援节点，L2通知所有成员。无备援？L4创建交接Issue等人工介入，L5标记降级运行。这不是"要么成功要么失败"的二选一，而是**在有限条件下始终找到可接受的最优解**。

30秒体验完整5层：

```bash
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt  # 仅需要 cryptography, pyyaml
python demo.py
```

## 三个仓库的技术共性

114个Skill分散在三个仓库，但它们共享同一套工程规范——这绝不是巧合，而是刻意的设计。

### 目录结构统一

```
skills/{skill-name}/
├── SKILL.md          # Skill定义（触发词、参数、规则）
├── engine.py         # 核心引擎
├── demo.py           # 可运行演示
├── __init__.py       # 包入口
└── references/       # 知识库（可选）
```

这种统一意味着什么？意味着当你学会了一个Skill的目录结构，你就学会了所有114个的结构。学习成本从N降到了1。

### 脱敏与安全

所有Skill已通过10项脱敏检查：无公司名称、无地区编码、无员工姓名、无合同编号、无真实金额、无设备ID、无电话邮箱、无AIGC水印、无教学专属内容。

> **开源不等于裸奔。脱敏是开源的前提，安全是企业级的底线。**

## 为什么开源

三个仓库的核心价值不在于某个具体的发票查验引擎或加密通道，而在于**架构模式**：

1. **Engine-Formatter分离**——通用到任何Agent框架，不是绑定某个平台的"插件"
2. **5层通信模型**——为Agent集群协作提供参考架构，补上了当前行业空白
3. **YAML驱动的规则引擎**——业务变化时改配置不改代码，把"改需求"的成本从"改代码"降到了"改配置"
4. **Phase-Orchestrator编排**——组件化Skill的可组合范式，5个组件排列组合出数十条流水线

如果你在构建企业级Agent系统，这三个仓库能省掉大量重复造轮子的时间。如果某个Skill正好满足你的需求，直接拿来用；如果架构模式对你有启发，Star一下是对我们最大的鼓励。

---

**相关链接：**

- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104个金融Agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5个通用业务Skill
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5个集群通信Skill

有问题欢迎提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)。

> 114个Skill覆盖了企业级Agent的"做什么""怎么算""怎么协作"——但它们真的能覆盖全场景吗？还是只是从"每个场景都要自己写"变成了"大部分场景有参考架构"？你的企业场景中，最缺的Agent Skill是什么？欢迎在评论区讨论。
