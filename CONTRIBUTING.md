# Contributing to SOE Compliant Office Skills

Thank you for your interest in contributing! This repo follows specific conventions to maintain consistency across all three domains.

## Skill Structure

Each skill must follow this directory structure:

```
skill-name/
├── SKILL.md              # Skill definition (required)
├── engine.py             # Main execution logic (if code-based)
├── demo.py               # Quick-start demo (if code-based)
├── requirements.txt      # Python dependencies (if code-based)
└── references/           # Supplementary documentation
    └── *.md
```

## SKILL.md Frontmatter (Required)

Every SKILL.md must include this YAML frontmatter:

```yaml
---
name: skill-name
name_cn: 技能中文名
version: "1.0.0"
domain: document|compliance|reporting
soe_relevance: 1-5
description: >
  One-line description of what this skill does.
---
```

### SOE Relevance Scoring

| Score | Meaning | Requirement |
|-------|---------|-------------|
| 1 | General utility, no SOE features | None |
| 2 | Useful in SOE but not SOE-specific | None |
| 3 | Has SOE-relevant features | Brief SOE note in description |
| 4 | Addresses SOE pain point | "央国企特色" section required |
| 5 | Solves SOE-unique problem | "央国企特色" section + compliance checklist |

## Python Engine Convention

If your skill includes a Python engine:

```python
from shared.audit_trail import log_operation, AuditLevel

class SkillEngine:
    def run(self, input_data: dict) -> dict:
        log_operation(
            skill_name="skill-name",
            action="start",
            input_summary=str(input_data)[:100],
            level=AuditLevel.INFO
        )
        
        # ... your logic here ...
        
        log_operation(
            skill_name="skill-name",
            action="complete",
            output_summary=str(result)[:100],
            level=AuditLevel.INFO
        )
        return result
```

## Domain-Specific Rules

### Document Domain (skills/document/)
- Must use shared/ooxml/ for OOXML operations when applicable
- Document generation must support GB/T 9704 format options
- Contract-related skills must implement multi-stage approval awareness

### Compliance Domain (skills/compliance/)
- Must call shared/desensitize.py before any output
- Risk assessments must use the L1-L5 scale
- Security ratings must use the D-A scale

### Reporting Domain (skills/reporting/)
- Financial reports must follow SOE color standards
- Report templates must support SASAC monthly report format
- Data analysis must include anomaly detection + trend judgment

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-skill-name`
3. Ensure your skill follows the structure and conventions above
4. Add your skill to the appropriate domain directory
5. Update the README.md skill table if adding a new skill
6. Submit a pull request with a clear description

## Code of Conduct

- Be respectful and constructive
- Focus on SOE compliance value
- No sensitive data (company names, employee info, real financial data) in code or documentation
- All examples must use obviously fictional data (e.g., "XX集团", "张三")
