---
title: "114 Open-Source AI Agent Skills: From Finance to Cluster Communication"
published: true
description: "How I built a three-repo ecosystem of 114 Agent Skills covering finance, composable business logic, and multi-agent cluster communication — all open source."
tags: [ai, python, opensource, agents]
author: Zhaopeng Yu
date: 2026-06-30
platform: devcommunity
---

# 114 Open-Source AI Agent Skills: From Finance to Cluster Communication

Ever run into this? You want your AI agent to verify invoices — but you have to build a rule engine from scratch. You need encrypted communication between agents — but there's no ready-made protocol layer. You're building an NL2SQL query gateway — but you're not sure how to chain permission checks, intent recognition, query execution, and data aggregation together.

I hit all three of these walls, and that's exactly why I built the **Agent Skills open-source ecosystem** — three repos, 114 Skills, one consistent architecture.

## A Three-Repo Ecosystem: Finance × Business × Communication

The ecosystem is organized in three layers, covering the full stack of enterprise agent development:

| Repo | Layer | Skills | Core Capabilities |
|------|-------|--------|-------------------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | Finance industry | 104 | Invoice verification, budget control, risk/compliance, wealth management |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | General business | 5 | Scoring engine, evidence chain, data aggregation, NL2Query, visualization |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | Cluster communication | 5 | Encrypted P2P, Redis message bus, group chat bot, GitHub async handoff, health monitor |

```
┌─────────────────────────────────────────────────────┐
│               Agent Skills Ecosystem                 │
├──────────────┬────────────────┬─────────────────────┤
│ Finance       │  Business      │  Communication      │
│ 104 Skills   │  5 Skills      │  5 Skills           │
│              │                │                     │
│ · Invoice    │ · Scoring      │ · L1 Encrypted P2P  │
│ · Budget     │ · Evidence     │ · L2 Redis Bus      │
│ · Risk       │ · Aggregator   │ · L3 Group Chat     │
│ · Wealth     │ · NL2Query     │ · L4 GitHub Handoff │
│ · Marketing  │ · Visualizer   │ · L5 Health Monitor │
└──────────────┴────────────────┴─────────────────────┘
```

The design logic is straightforward: **the industry layer answers "what to do," the business layer answers "how to compute," and the communication layer answers "how to collaborate."**

## The Finance Layer: 104 Skills Battle-Tested

[financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) is the largest repo — 7 Skill packs, 104 scenario engines, covering three major finance tracks: financial intelligence, wealth management, and risk compliance.

### Verify an Invoice in 30 Seconds

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678
```

Output:

```
## Invoice Verification Result

✅ Verification: Authentic

| Field        | Value                          |
|-------------|-------------------------------|
| Invoice Code | 011001900111                  |
| Invoice No.  | 12345678                      |
| Issuer       | Beijing XX Technology Co., Ltd.|
| Total        | ¥13,335.66                    |

🟢 Compliance Status: Pass (Score: 100/100)
```

### Pure Python, Zero Dependencies

Here's a design decision I'm particularly proud of: **everything uses the Python standard library only — no third-party packages at all.** This means:

- Zero install cost — clone and run
- Works in air-gapped enterprise networks without pip mirrors
- No supply-chain security risks
- Average response time under 100ms

### Engine + Formatter Architecture

```python
from engines import InvoiceEngine
from formatters import FinancialFormatter

engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))
```

The Engine layer handles business logic; the Formatter layer handles output adaptation. This separation lets you:

- Output Markdown for CLI
- Push card messages in WeCom/Feishu
- Return JSON from an API endpoint

Same engine, three surfaces. That's the kind of composability I wanted from day one.

### The 7 Skill Packs at a Glance

| Skill Pack | Scenarios | Typical Use |
|-----------|-----------|-------------|
| financial-intelligence | 6 | Invoice verification, budget control, financial report reader, tax planning, expense reimbursement, fund forecasting |
| wealth-management | 8 | Asset allocation, financial health check, retirement planning, insurance planning, tax optimization, and more |
| risk-compliance | 9 | Enterprise risk assessment, credit rating, anti-fraud, compliance check, post-loan monitoring, and more |
| wecom-template-card | 5 | WeCom message card templates |
| customer-marketing | 18 | Marketing script generation, objection handling, dialect adaptation |
| product-manual-rag | 3+ | Product manual Q&A (dual-route BM25 + TF-IDF RAG) |
| application-material-checker | 3 | Auto-verification of loan application materials |

## The Business Layer: 5 Composable Skill Components

[teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) provides 5 general-purpose components — each works standalone, or you can chain them into a pipeline via Phase-Orchestrator.

### NL2Query: A Complete Natural-Language-to-SQL Gateway

```python
from skills.nl2_query.engine import NL2QueryEngine

engine = NL2QueryEngine()
result = engine.process("查询上月投诉量排前5的区县")
# Output: SQL statement + confidence score + permission check result
```

It's a full 4-phase pipeline: intent recognition → permission check → SQL generation → result formatting.

### Scoring Engine: YAML-Driven Rule Engine

```python
from skills.scoring_engine.engine import ScoringEngine

engine = ScoringEngine(rules_path="scoring-rules.yaml")
result = engine.score(customer_data)
# Output: total score + per-dimension scores + matched rules list
```

Business rules live in YAML. When the business logic changes, you update the config — not the code.

### Evidence Chain: Multi-Source Cross-Validation

```python
from skills.evidence_chain.engine import EvidenceChainEngine

engine = EvidenceChainEngine()
result = engine.analyze(
    sources=[complaint_data, system_logs, sla_records],
    conflict_rules_path="conflict-rules.yaml"
)
# Output: conflict detection results + confidence scores + root cause inference
```

### Data Aggregator + Visualization Renderer

The aggregator handles validation, cleaning, aggregation, and year-over-year comparisons. The renderer outputs ECharts configs and HTML dashboards.

Chain all four together and you get a complete **"ask data → compute results → render charts"** pipeline.

## The Communication Layer: A 5-Layer Architecture for Agent Clusters

[agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) is the most architecturally intricate of the three repos. It defines a 5-layer communication model for agent clusters.

### L1–L5 Layered Design

| Layer | Skill | Communication Mode | Latency | Best For |
|-------|-------|-------------------|---------|----------|
| L1 | encrypted-p2p-messaging | Point-to-point encrypted | <50ms | Sensitive data transfer, financial transactions |
| L2 | redis-message-bus | Pub/Sub | <10ms | High-frequency state sync, real-time alerts |
| L3 | group-chat-bot | Group collaboration | ~500ms | Human-in-the-loop decisions, expert consultation |
| L4 | github-async-handoff | Async handoff | Minutes | Cross-shift tasks, long-running projects |
| L5 | cluster-health-monitor | Health monitoring | Periodic | Global awareness, self-healing |

### 4 Proven Composition Patterns

These 5 Skills aren't isolated — I've validated 4 composition patterns in real scenarios:

**Pattern 1: High-Speed Channel (L1 + L2)**

Two agents need to exchange sensitive data at high frequency: L1 encrypted channel for security, L2 Redis bus for speed.

**Pattern 2: Human-in-the-Loop (L1 + L3)**

When an agent handles a sensitive operation, it pushes a confirmation message through the L1 encrypted channel to the L3 group chat bot. A human approves in the chat, and the result flows back.

**Pattern 3: Async Relay (L2 + L4)**

The day-shift agent processes tasks in real time via L2 Redis. At shift change, it creates a handoff Issue via L4 GitHub for the night-shift agent — enabling 24/7 uninterrupted service.

**Pattern 4: Global Monitoring (L2 + L5)**

L5 health monitor periodically collects agent status and broadcasts health reports via L2 Redis. If any agent goes down, an alert fires automatically.

### Failover Decision Flow

```
               Agent Failure Detected
                      │
             ┌────────┴────────┐
             ↓                 ↓
      Backup available?    No backup?
             │                 │
        ┌────┴────┐       ┌────┴────┐
        ↓         ↓       ↓         ↓
     L1 switch  L2 notify  L4 create  L5 mark
     encrypted  broadcast  handoff    degraded
     channel               Issue      operation
```

### Experience the Full 5-Layer Stack in 30 Seconds

```bash
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt  # cryptography, pyyaml
python demo.py
```

The demo walks you through each communication layer in L1→L2→L3→L4→L5 order.

## What Ties the Three Repos Together

Despite their different domains, all three repos share the same engineering conventions.

### Unified Directory Structure

```
skills/{skill-name}/
├── SKILL.md          # Skill definition (trigger words, params, rules)
├── engine.py         # Core engine
├── demo.py           # Runnable demo
├── __init__.py       # Package entry
└── references/       # Knowledge base (optional)
```

### Engine-Formatter Separation

Every Skill follows the "Engine handles logic, Formatter handles output" pattern. That same invoice verification engine? It can output Markdown (CLI), JSON (API), or a WeCom card (IM) — no code changes needed.

### Desensitization & Security

All Skills passed a 10-point data scrub checklist:
- No company names, no region codes, no employee names
- No contract numbers, no real amounts, no device IDs
- No phone numbers or emails, no AIGC watermarks, no training-specific content

### Composability via Phase-Orchestrator

The 5 Skills in teleagent-skills chain into a pipeline through Phase-Orchestrator:

```
NL2Query → Data Executor → Data Aggregator → Visualization Renderer
```

Each phase runs as an independent agent, and phases pass data via structured JSON.

## Quick Start

```bash
# Finance Skills (zero dependencies)
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills/skills/financial-intelligence/scripts
python financial_cli.py invoice 011001900111 12345678

# General Business Skills
git clone https://github.com/yuzhaopeng-up/teleagent-skills.git
cd teleagent-skills
python demo.py

# Cluster Communication Skills
git clone https://github.com/yuzhaopeng-up/agent-cluster-comm.git
cd agent-cluster-comm
pip install -r requirements.txt
python demo.py
```

## Why I Open-Sourced This

The core value of these three repos isn't any single invoice engine or encrypted channel — it's the **architectural patterns**:

1. **Engine-Formatter separation** — portable to any agent framework
2. **5-layer communication model** — a reference architecture for agent cluster collaboration
3. **YAML-driven rule engine** — change the config, not the code, when business rules shift
4. **Phase-Orchestrator chaining** — a composable paradigm for modular Skills

If you're building enterprise-grade agent systems, these repos can save you a lot of reinventing-the-wheel time. If a Skill fits your need, use it directly. If the architecture patterns inspire you, a Star on any of the repos means a lot.

---

**Links:**

- [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) — 104 finance agent Skills
- [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) — 5 general business Skills
- [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) — 5 cluster communication Skills

Got questions? Open an [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues) — or let me know in the comments. What do you think?
