# SOE Compliant Office Skills

<p align="center">
  <img src="https://img.shields.io/badge/Skills-17_(Phase1+2_done)-blue" alt="17 Skills" />
  <img src="https://img.shields.io/badge/Python-3.8+-green" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-Apache--2.0-yellow" alt="License" />
  <img src="https://img.shields.io/badge/SOE-Compliant-orange" alt="SOE Compliant" />
  <img src="https://img.shields.io/badge/GB/T_9704-Supported-red" alt="GB/T 9704" />
</p>

**AI Agent Skills for Chinese State-Owned Enterprise (SOE) — Built-in Compliance, Audit Trail, National Standards.**

This is NOT another generic office automation toolkit. Every skill is designed around **three principles that SOEs require but private-sector tools ignore**:

| Principle | What It Means | Why SOEs Need It |
|-----------|--------------|-----------------|
| **Compliance Built-in** | Compliance logic runs DURING execution, not after | 三重一大, 穿透式监管, 首席合规官 — compliance is a survival line, not a feature |
| **Audit Trail by Default** | Every operation logs who/when/what, automatically | 表决记录10年+保存, 全级次全要素追溯, 巡视整改可查 |
| **National Standards Ready** | GB/T 9704, DA/T archive, SASAC report formats built-in | 红头文件格式, 国资委月报模板, 电子归档规范 |

## Three Domains

```
┌──────────────────────────────────────────────────────────┐
│           SOE Compliant Office Skills                     │
├──────────────┬──────────────────┬────────────────────────┤
│  Document    │   Compliance     │   Reporting            │
│  文档作业     │   合规安全        │   报告分析              │
│  (Phase 1)   │   (Phase 2)      │   (Phase 3)            │
│              │                  │                        │
│  pptx        │  six-dim-check   │  report-generator      │
│  docx        │  human-in-loop   │  data-analyst          │
│  xlsx        │  security-guard  │  finance-expert        │
│  pdf         │  security-audit  │  business-analysis     │
│  contract    │  evidence-chain  │  gov-report-analyzer   │
│  diagram     │  red-team-test   │  social-security       │
│  meeting     │                  │                        │
│  print       │                  │                        │
└──────────────┴──────────────────┴────────────────────────┘
         ↕              ↕                   ↕
    ┌──────────────────────────────────────────────┐
    │       Shared Infrastructure (shared/)         │
    │  ooxml/ · audit_trail · soe_standards         │
    │  desensitize · soe_classification              │
    └──────────────────────────────────────────────┘
```

## Phase 1: Document Operations (8 Skills — Available Now)

### L1: Core Infrastructure

| Skill | LOC | Key Capability | SOE Feature |
|-------|-----|---------------|-------------|
| **pptx** | 16K | Full OOXML PPTX generation, SVG-to-PPTX conversion (20+ modules) | SOE reporting template compliance, structured slide hierarchy |
| **docx** | 3.7K | OOXML document creation, redlining/track-changes workflow | GB/T 9704 official document format, revision audit trail |
| **xlsx** | 442 | Formula recalculation engine, financial modeling | SOE financial color standards (blue=input, black=calc, green=link, red=error) |
| **pdf** | 5K | End-to-end PDF: create/read/manipulate/fill/OCR | Official cover page design system, watermark/encryption for classified docs |

### L2: Scenario Tools

| Skill | LOC | Key Capability | SOE Feature |
|-------|-----|---------------|-------------|
| **contract-review** | 2.9K | 3-layer review (basic/business/legal), comment-based annotations | Multi-stage serial approval flow (business→legal→compliance→audit→leadership) |
| **diagram-drawing** | 634 | 23 diagram types, dual-engine (Draw.io + Excalidraw) | Compliance flowcharts, governance architecture diagrams |
| **meeting-minutes** | 215 | Structured field extraction, DOCX generation | Three meeting templates (Party Committee / Board / GM Office) |
| **print** | 986 | Cross-platform printing, preview-first strategy | Secure print with dry-run, prevent accidental disclosure |

### Shared Infrastructure

The 4 core office skills (pptx/docx/xlsx/pdf) share an **OOXML infrastructure layer**:

```
shared/ooxml/
├── schemas/          # 39 XSD validation schemas (ISO-IEC29500-4)
├── scripts/
│   ├── pack.py       # ZIP-based OOXML package builder
│   ├── unpack.py     # OOXML package extractor
│   └── validate.py   # Schema + relationship validation
```

## Phase 2: Compliance & Security (6 Skills — Available Now)

### L3: Compliance Framework

| Skill | Type | Key Capability | SOE Feature |
|-------|------|---------------|-------------|
| **six-dimension-compliance-check** | Prompt | 6-dimension systematic compliance review (scenario/parameter/logic/output/security/archival) | 三重一大集体决策检查, 党委前置审议, 穿透式监管, DA/T归档标准, A-D级合规评级 |
| **human-in-loop** | Prompt | L1-L5 risk-graded approval, 4-Phase pipeline (Info-Extractor→Security-Guard→Report→Archive) | 三重一大强制人工确认, 两人会签制度, 13710督办, 党委审议前置流程 |
| **security-guard** | Prompt | Permission check, data scope validation, sensitive field detection, audit trail verification | 最小权限原则, 数据分级分类(GB/T 35273), 高危动作双人确认, 首席合规官审核 |

### L4: Security Audit & Testing

| Skill | Type | Key Capability | SOE Feature |
|-------|------|---------------|-------------|
| **security-auditor** | Prompt | 4-Phase automated audit (Info-Extract→Security-Guard→Data-Analyst→Report), D-A security rating | Skill上线门禁, 权限收敛闭环, soe_basic/soe_enhanced双合规标准, F/D级自动告警 |
| **evidence-chain** | Prompt | Multi-source cross-validation, conflict detection, confidence scoring, root cause inference | 巡视整改证据链, 投诉核查多源对证, 合规审查冲突检测, 故障定责三维推断 |
| **red-team-tester** | Prompt | 6-round progressive adversarial testing, defense maturity grading (脆弱→坚固) | 等保合规验证, 首席合规官签审, 信创环境安全测试, 与Security-Auditor形成静态+动态闭环 |

### Cross-Domain Compliance Flow

```
                    ┌─────────────────────────────┐
                    │   Skill Deployment Pipeline  │
                    └─────────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │  six-dimension-compliance   │  ← 6维合规前置检查
                    │  -check (前置审查)           │
                    └─────────────┬──────────────┘
                                  │ A/B级通过
                    ┌─────────────▼──────────────┐
                    │  security-auditor           │  ← 静态安全审计
                    │  (静态审计, D-A评级)         │
                    └─────────────┬──────────────┘
                                  │ B级以上通过
                    ┌─────────────▼──────────────┐
                    │  red-team-tester            │  ← 动态红队验证
                    │  (动态对抗测试)              │
                    └─────────────┬──────────────┘
                                  │ 🟢良好以上
                    ┌─────────────▼──────────────┐
                    │  human-in-loop              │  ← 上线运行时守门
                    │  (运行时审批守门)            │
                    └─────────────┬──────────────┘
                                  │ L4+需人工确认
                    ┌─────────────▼──────────────┐
                    │  evidence-chain             │  ← 事后审计追溯
                    │  (事后证据链审计)            │
                    └────────────────────────────┘
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yuzhaopeng-up/soe-compliant-office.git

# Any skill can be used independently — copy to your TeleAgent skills directory
cp -r skills/document/pptx ~/.config/TeleAgent/skills/pptx

# Or use the Python engines directly
cd skills/document/contract-review
pip install -r requirements.txt
python demo.py
```

### Generate a GB/T 9704 Compliant Document

```python
from docx.engine import SkillEngine

engine = SkillEngine()
result = engine.run({
    "action": "create_official_document",
    "doc_type": "请示",           # One of 15 statutory types
    "issuer": "XX集团",
    "recipient": "国务院国资委",
    "classification": "秘密",      # 秘密/机密/绝密
    "urgency": "加急",            # 特急/加急
    "body": "关于XXX的请示..."
})
```

### Review a Contract with 3-Layer Compliance

```python
from contract_review.engine import SkillEngine

engine = SkillEngine()
result = engine.run({
    "action": "review",
    "contract_path": "procurement_contract.docx",
    "review_layers": ["basic", "business", "legal"],
    "risk_threshold": "MEDIUM"    # LOW/MEDIUM/HIGH/CRITICAL
})
# Returns: structured issues, risk levels, Mermaid business flowchart
```

## SOE vs Private-Sector: Why This Repo Exists

| Capability | Generic AI Office Tools | SOE Compliant Office |
|-----------|----------------------|---------------------|
| Document format | Free-form | GB/T 9704 15 statutory types |
| Contract review | Grammar check only | 3-layer compliance review + risk grading |
| Approval flow | Single-step | Multi-stage serial (business→legal→compliance→audit) |
| Data security | Cloud-first | Local-first, auto-desensitization, classification labels |
| Audit trail | None | Every operation logged with who/when/what |
| Meeting minutes | Generic template | Party Committee / Board / GM Office specific templates |
| Printing | Direct print | Preview-first dry-run, secure print strategies |
| National standards | None | GB/T 9704, DA/T archive, SASAC report formats |

## Roadmap

| Phase | Domain | Skills | Status |
|-------|--------|--------|--------|
| Phase 1 | Document Operations | 8 skills (pptx, docx, xlsx, pdf, contract-review, diagram-drawing, meeting-minutes, print) | **Done** |
| Phase 2 | Compliance & Security | 6 skills (6-dim compliance check, human-in-loop, security-guard, security-auditor, evidence-chain, red-team-tester) | **Done** |
| Phase 3 | Reporting & Analysis | 6 skills (report-generator, data-analyst, finance-expert, business-analysis, gov-report-analyzer, social-security) | Planned |

## Ecosystem

| Repo | Description |
|------|------------|
| [financial-ai-skills](https://github.com/yuzhaopeng-up/financial-ai-skills) | 104 financial AI skills |
| [skill-framework](https://github.com/yuzhaopeng-up/skill-framework) | L0-L4 skill governance framework + templates |
| [fintech-h5-demos](https://github.com/yuzhaopeng-up/fintech-h5-demos) | 12 zero-dependency financial H5 demos |
| [teleagent-skills](https://github.com/yuzhaopeng-up/teleagent-skills) | 5 general business skills |
| [agent-cluster-comm](https://github.com/yuzhaopeng-up/agent-cluster-comm) | 5 agent cluster communication skills |
| **soe-compliant-office** (this repo) | 17 SOE-compliant office skills |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines. Key rules:
- All skills must declare `soe_relevance` (1-5) in SKILL.md frontmatter
- Skills with soe_relevance >= 4 must include a "央国企特色" section
- Python engine classes must call audit trail at entry/exit
- Desensitization is mandatory for any output containing personal or business data

## License

Apache-2.0 — See [LICENSE](./LICENSE)
