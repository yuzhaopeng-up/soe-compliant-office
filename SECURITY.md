# Security Policy

## Data Security Principles

This repository follows SOE (State-Owned Enterprise) data security principles:

1. **Local-first**: All skill execution happens locally, no data upload required
2. **Auto-desensitization**: Skills must call `shared/desensitize.py` before outputting sensitive data
3. **Classification labels**: Data must be classified as PUBLIC/INTERNAL/CONFIDENTIAL/SECRET
4. **Audit trail**: Every operation is logged with who/when/what

## Reporting a Vulnerability

If you discover a security vulnerability in this repository:

1. **Do NOT** open a public issue
2. Email the maintainer with details of the vulnerability
3. Include: affected skill, attack vector, potential impact
4. We will acknowledge within 48 hours and provide a fix timeline

## Sensitive Data Handling

### What Must NEVER Be Committed
- Real company names or employee information
- Actual financial figures or business data
- API keys, tokens, or credentials
- Personal identification numbers (身份证号, 手机号)
- Internal network addresses or server configurations

### What Is Acceptable
- Obviously fictional examples ("XX集团", "张三", "138****1234")
- Generic template structures without real data
- Code logic and algorithms without business-specific values

## Compliance Standards Referenced

| Standard | Scope | Usage |
|----------|-------|-------|
| GB/T 9704-2012 | Official document format | Document generation skills |
| DA/T 103-104 | Electronic archive standards | Archive management skills |
| SASAC monthly report | Business reporting format | Reporting skills |
| ISO-IEC29500-4 | OOXML schema validation | Office document skills |
| MLPS 2.0 (等保2.0) | Information security | All skills |

## Skill Security Scanning

All skills are scanned before publication using:
- `skillscan` — Security gate for skill content
- PII pattern matching — Automated sensitive data detection
- Compliance checklist — 6-dimension compliance verification
