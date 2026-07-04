# SOE Compliant Office — Architecture & Conventions

> This document defines the system architecture, naming conventions, and cross-domain interfaces
> that ALL skills in this repo must follow. Phase 2/3 skills MUST conform to these rules.

## Three-Domain Architecture

```
soe-compliant-office/
├── skills/
│   ├── document/       # Domain 1: Document Operations (Phase 1)
│   ├── compliance/     # Domain 2: Compliance & Security (Phase 2)
│   └── reporting/      # Domain 3: Reporting & Analysis (Phase 3)

├── docs/               # Architecture docs, integration guides
├── LICENSE             # Apache-2.0
├── CONTRIBUTING.md     # Contribution guide
├── SECURITY.md         # Security policy
└── README.md           # Main documentation
```

## Naming Conventions

### Skill Directory Naming
- Use kebab-case: `contract-review`, `meeting-minutes`, `six-dimension-compliance-check`
- Each skill directory contains:
  ```
  skill-name/
  ├── SKILL.md              # Skill definition (required)
  ├── engine.py             # Main execution logic (if has code)
  ├── demo.py               # Demo/quick-start script (if has code)
  ├── requirements.txt      # Python dependencies (if has code)
  └── references/           # Supplementary docs
      └── *.md
  ```

### Python Module Conventions
- All engine.py must expose `class SkillEngine` with `run(input_data: dict) -> dict`
- All engine.py must log operations at entry and exit (audit trail integration point - implement per your infrastructure)
- All engine.py must use a shared OOXML module for OOXML operations (no local reimplementations)

### SKILL.md Conventions
- Must include YAML frontmatter with: name, name_cn, version, domain, soe_relevance
- Must include section: "央国企特色" (SOE-specific features)
- Must reference audit trail and desensitization integration points when applicable
- Example domain values: `document`, `compliance`, `reporting`

## Cross-Domain Interfaces

### 1. Audit Trail (ALL skills MUST use)
```python
# Audit trail integration point - implement per your infrastructure
# Example: log skill entry/exit with name, action, summary, and level
```

### 2. SOE Standards Integration (Document domain MUST use)
```python
# SOE standards integration point - implement per your infrastructure
# Example: GB/T 9704, DA/T archive, SASAC report format support
```

### 3. Data Classification & Desensitization (Compliance domain MUST use)
```python
# Data classification & desensitization integration point - implement per your infrastructure
# Example: classify output data and auto-desensitize sensitive fields
```

### 4. Human-in-Loop Integration (High-risk operations MUST trigger)
```python
# Human-in-loop approval integration point - implement per your infrastructure
# Example: request approval for high-risk operations with risk level and dual sign
```

## SOE Relevance Scoring

Every skill must declare its SOE relevance (1-5) in SKILL.md frontmatter:

| Score | Meaning | Example |
|-------|---------|---------|
| 1 | General utility, no SOE-specific features | article-writer |
| 2 | Useful in SOE but not SOE-specific | diagram-drawing |
| 3 | Has SOE-relevant features | print (secure printing) |
| 4 | Addresses SOE-pain point | data-analyst (SASAC report formats) |
| 5 | Solves SOE-unique problem | contract-review (3-layer compliance audit) |

## Three Phase Roadmap

| Phase | Domain | Skills | Status |
|-------|--------|--------|--------|
| Phase 1 | Document Operations | pptx, docx, xlsx, pdf, contract-review, diagram-drawing, meeting-minutes, print | **DONE** |
| Phase 2 | Compliance & Security | six-dimension-compliance-check, human-in-loop, security-guard, security-auditor, evidence-chain, red-team-tester | **DONE** |
| Phase 3 | Reporting & Analysis | report-generator, data-analyst, finance-expert, business-analysis, gov-report-analyzer, social-security-advisor | **DONE** |

## Shared Infrastructure (Design Pattern)

The `shared/` directory is a **design pattern**, not existing code. Each domain implements these integration points independently:

| Integration Point | Description | Used By |
|-------------------|-------------|---------|
| OOXML operations | Shared OOXML packing/unpacking logic | All document skills |
| Audit trail | Operation logging (who/when/what) | ALL skills (recommended) |
| SOE standards | GB/T 9704, DA/T archive, SASAC formats | document + reporting |
| Data desensitization | Auto-classification and field-level masking | ALL skills (recommended) |
