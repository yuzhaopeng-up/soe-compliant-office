---
title: 114个开源AI Agent Skills：从金融到集群通信的企业级全链路实践
author: 于兆鹏
date: 2026-06-30
topic: Agent Skills生态
word_count: 4200
target_audience: AI Agent开发者、企业技术架构师
---

# 114个开源AI Agent Skills：从金融到集群通信的企业级全链路实践

你有没有遇到过这种情况：想给AI Agent加一个发票查验能力，却发现要从头写规则引擎？想让多个Agent之间加密通信，却没有现成的协议层？想做一个NL2SQL的查询网关，却不知道怎么编排权限校验、意图识别、执行、聚合这几个组件？

这些问题，现在有了一个统一的答案——**Agent Skills开源生态**。

## 三仓库生态：金融×业务×通信的三层架构

Agent Skills生态由三个GitHub仓库组成，覆盖企业级Agent开发的全链路：

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

三层架构的设计逻辑是：**行业层解决"做什么"，业务层解决"怎么算"，通信层解决"怎么协作"**。

## 金融行业层：104个Skills的实战检验

[financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) 是生态中最大的仓库，包含7个Skill包、104个场景引擎，覆盖财务、财富、风控三大金融赛道。

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

### 纯Python实现，零依赖

一个关键设计决策：**全部使用Python标准库，不依赖任何第三方包**。这意味着：

- 安装成本为零，clone即用
- 企业内网环境无需配置pip镜像
- 无供应链安全风险
- 平均响应时间 < 100ms

### 技术架构：规则引擎 + Mock数据

```python
from engines import InvoiceEngine
from formatters import FinancialFormatter

engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))
```

引擎层（Engine）负责业务逻辑，格式化层（Formatter）负责输出适配。这种分离让你可以：

- 在CLI中用Markdown格式输出
- 在企业微信/飞书中直接推送卡片
- 在API中返回JSON给前端

### 覆盖的7大Skill包

| Skill | 场景数 | 典型用途 |
|-------|--------|---------|
| financial-intelligence | 6 | 发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测 |
| wealth-management | 8 | 资产配置、财务健康、退休规划、保险规划、税务优化等 |
| risk-compliance | 9 | 企业风险评估、信用评级、反欺诈、合规检查、贷后监控等 |
| wecom-template-card | 5 | 企微消息卡片模板 |
| customer-marketing | 18 | 营销话术生成、异议处理、方言适配 |
| product-manual-rag | 3+ | 产品手册智能问答（BM25+TF-IDF双路RAG） |
| application-material-checker | 3 | 进件材料自动核对 |

## 通用业务层：5个可组合的组件化Skill

[teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) 提供5个通用业务组件，每个都可以独立使用，也可以通过Phase-Orchestrator编排成流水线：

### NL2Query：自然语言到SQL的完整网关

```python
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
# 输出：SQL语句 + 置信度 + 权限校验结果
```

完整的4-Phase编排：意图识别 → 权限校验 → SQL生成 → 结果格式化

### 评分引擎：YAML驱动的规则引擎

```python
from skills.scoring_engine.engine import ScoringEngine

engine = ScoringEngine(rules_path="scoring-rules.yaml")
result = engine.score(customer_data)
# 输出：总分 + 各维度得分 + 命中规则列表
```

业务规则存在YAML配置中，业务变了改配置不用改代码。

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

### 数据聚合器 + 可视化渲染

数据聚合器支持校验清洗、聚合计算、同比环比；可视化渲染输出ECharts配置和HTML Dashboard。

四者组合就是一条完整的**"问数据→算结果→出图表"**链路。

## 集群通信层：5层通信架构

[agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) 是三个仓库中架构设计最精巧的，它定义了Agent集群的5层通信模型：

### L1-L5分层设计

| 层级 | Skill | 通信模式 | 延迟 | 最佳场景 |
|------|-------|---------|------|---------|
| L1 | encrypted-p2p-messaging | 点对点加密 | <50ms | 敏感数据传输、金融交易 |
| L2 | redis-message-bus | 发布/订阅 | <10ms | 高频状态同步、实时告警 |
| L3 | group-chat-bot | 群聊协作 | ~500ms | 人机混合决策、专家会诊 |
| L4 | github-async-handoff | 异步交接 | 分钟级 | 跨班次任务、长期项目 |
| L5 | cluster-health-monitor | 健康监控 | 周期性 | 全局状态感知、故障自愈 |

### 4种组合模式

5个Skill不是孤立的，它们有4种经过验证的组合模式：

**模式1：高速通道（L1+L2）**
两个Agent之间需要高频交换敏感数据——L1加密通道保安全，L2 Redis总线保速度。

**模式2：人机协同（L1+L3）**
Agent处理敏感操作时，通过L1加密通道向L3群聊机器人推送确认消息，人工在群聊中审批后结果回传。

**模式3：异步接力（L2+L4）**
白班Agent通过L2 Redis总线实时处理，下班时通过L4 GitHub交接Issue给夜班Agent，实现7×24不间断服务。

**模式4：全局监控（L2+L5）**
L5健康监控器周期性采集Agent状态，通过L2 Redis总线广播健康报告，任一Agent故障时自动触发告警。

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

Demo将按L1→L2→L3→L4→L5顺序演示每层通信能力。

## 三个仓库的技术共性

尽管定位不同，三个仓库共享同一套工程规范：

### 目录结构统一

```
skills/{skill-name}/
├── SKILL.md          # Skill定义（触发词、参数、规则）
├── engine.py         # 核心引擎
├── demo.py           # 可运行演示
├── __init__.py       # 包入口
└── references/       # 知识库（可选）
```

### 引擎-格式化分离

所有Skill都遵循"Engine负责逻辑，Formatter负责输出"的分层设计。这意味着同一个发票查验引擎，可以输出Markdown（CLI）、JSON（API）或企微卡片（IM）三种格式。

### 脱敏与安全

所有Skill已通过10项脱敏检查：
- 无公司名称、无地区编码、无员工姓名
- 无合同编号、无真实金额、无设备ID
- 无电话邮箱、无AIGC水印、无教学专属内容

### 可编排性

teleagent-skills中的5个Skill通过Phase-Orchestrator强制编排为链式流水线：

```
NL2Query → Data Executor → Data Aggregator → Visualization Renderer
```

每个Phase由独立Agent执行，Phase间通过结构化JSON传递数据。

## 快速开始

```bash
# 金融Skills（零依赖）
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

## 为什么开源

三个仓库的核心价值不在于某个具体的发票查验引擎或加密通道，而在于**架构模式**：

1. **Engine-Formatter分离**——通用到任何Agent框架
2. **5层通信模型**——为Agent集群协作提供参考架构
3. **YAML驱动的规则引擎**——业务变化时改配置不改代码
4. **Phase-Orchestrator编排**——组件化Skill的可组合范式

如果你在构建企业级Agent系统，这三个仓库能省掉大量重复造轮子的时间。如果某个Skill正好满足你的需求，直接拿来用；如果架构模式对你有启发，Star一下是对我们最大的鼓励。

---

**相关链接：**

- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104个金融Agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5个通用业务Skill
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5个集群通信Skill

有问题欢迎提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)，也可以在评论区交流。
