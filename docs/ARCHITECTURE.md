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
├── shared/             # Cross-domain shared infrastructure
│   ├── ooxml/          # OOXML base.py, pack.py, unpack.py (shared by pptx/docx/xlsx)
│   ├── audit_trail.py  # Audit trail logging (all skills call this)
│   ├── soe_standards/  # GB/T 9704 templates, DA/T archive specs, SASAC report formats
│   └── desensitize.py  # Data classification & auto-desensitization utilities
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
- All engine.py must call `shared.audit_trail.log_operation()` at entry and exit
- All engine.py must import from `shared.ooxml.*` for OOXML operations (no local reimplementations)

### SKILL.md Conventions
- Must include YAML frontmatter with: name, name_cn, version, domain, soe_relevance
- Must include section: "央国企特色" (SOE-specific features)
- Must reference shared infrastructure when applicable
- Example domain values: `document`, `compliance`, `reporting`

## Cross-Domain Interfaces

### 1. Audit Trail (ALL skills MUST use)
```python
from shared.audit_trail import log_operation, AuditLevel

# Called at skill entry
log_operation(
    skill_name="contract-review",
    action="start_review",
    input_summary="Contract #2026-001, type=procurement",
    level=AuditLevel.INFO
)

# Called at skill exit
log_operation(
    skill_name="contract-review",
    action="complete_review",
    output_summary="3 issues found, max risk=HIGH",
    level=AuditLevel.INFO
)
```

### 2. SOE Standards Integration (Document domain MUST use)
```python
from shared.soe_standards importGBT9704, DAT_ARCHIVE, SASAC_REPORT

# Document generation with GB/T 9704 compliance
doc = GBT9704.create_official_document(
    doc_type="请示",  # One of 15 statutory document types
    issuer="XX集团",
    recipient="国资委",
    classification="秘密",  # 秘密/机密/绝密
    urgency="加急",  # 特急/加急
)
```

### 3. Data Classification & Desensitization (Compliance domain MUST use)
```python
from shared.desensitize import classify_data, auto_desensitize

# Before any output
classified = classify_data(output_data)  # Returns: PUBLIC/INTERNAL/CONFIDENTIAL/SECRET
if classified.level >= DataLevel.INTERNAL:
    output_data = auto_desensitize(output_data, classified.fields)
```

### 4. Human-in-Loop Integration (High-risk operations MUST trigger)
```python
from shared.audit_trail import request_approval

# Before executing high-risk operations
approval = request_approval(
    operation="archive_delete",
    risk_level="L3",  # L1-L5 scale
    description="Delete archived records older than 10 years",
    requires_dual_sign=True  # 两人会签
)
if not approval.approved:
    raise OperationBlocked("Approval denied")
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
| Phase 3 | Reporting & Analysis | report-generator, data-analyst, finance-expert, business-analysis, gov-report-analyzer, social-security-advisor | PLANNED |

## Shared Infrastructure Ownership

| Component | Primary Owner | Used By |
|-----------|--------------|---------|
| shared/ooxml/ | pptx, docx, xlsx | All document skills |
| shared/audit_trail.py | compliance domain | ALL skills (mandatory) |
| shared/soe_standards/ | document domain | document + reporting |
| shared/desensitize.py | compliance domain | ALL skills (mandatory) |
