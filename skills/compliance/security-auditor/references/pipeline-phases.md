# Security-Audit-Pipeline Phase Prompt Templates

> This file defines 4 Phase prompt templates for the Security-Audit-Pipeline.
> When executing, the Security-Auditor skill reads this file, replaces placeholders, and passes the complete prompt to phase-orchestrator.

## Placeholder Description

| Placeholder | Description | Example |
|---|---|---|
| `{{skill_config}}` | JSON configuration of the Skill to be audited | `{"name":"business_query_skill",...}` |
| `{{expected_usage}}` | Expected usage description | `"Query business records under own responsibility"` |
| `{{audit_mode}}` | Audit mode | `full_scan` / `permission_only` |
| `{{compliance_standard}}` | Compliance standard | `soe_basic` / `soe_enhanced` |
| `{{phase1_output}}` | JSON output from Phase 1 | Auto-injected by pipeline |
| `{{phase2_output}}` | JSON output from Phase 2 | Auto-injected by pipeline |
| `{{phase3_output}}` | JSON output from Phase 3 | Auto-injected by pipeline |

---

## Phase 1 — Info-Extractor Information Extraction

**Loaded Component**: `info-extractor`
**Input**: skill_config (the Skill configuration JSON to be audited)
**Output contract key**: `extraction_result`

```markdown
You are Phase 1 of the Security-Audit-Pipeline — Information Extraction Phase.

## Objective
Extract structured security-related feature information from the input Skill configuration.

## Loaded Component
Load via skill(name="info-extractor") to obtain professional information extraction capability.

## Input
The Skill configuration to be audited is as follows:
{{skill_config}}

Expected usage description (may be empty):
{{expected_usage}}

## Task
From the above configuration, extract the following fields:
1. **skill_name**: Skill name
2. **permissions**: List of all declared permissions
3. **data_scope**: Data access scope description
4. **operations**: List of supported operation types
5. **field_access**: List of accessed sensitive fields (if no explicit declaration, infer from permissions and data_scope)
6. **defense_rules**: Existing defense rules (such as field whitelisting, desensitization policies; mark as empty array if none)
7. **expected_usage**: Expected usage (from input, null if not provided)

## Output Contract
Strictly output according to the following JSON format, do not add any other content:
```json
{
  "status": "success|error",
  "skill_name": "string",
  "permissions": ["string"],
  "data_scope": "string",
  "operations": ["string"],
  "field_access": ["string"],
  "defense_rules": ["string"],
  "expected_usage": "string|null"
}
```

If the input lacks the permissions field, output:
```json
{"status": "error", "skill_name": "unknown", "permissions": [], "data_scope": "", "operations": [], "field_access": [], "defense_rules": [], "expected_usage": null}
```
```

---

## Phase 2 — Security-Guard Security Assessment

**Loaded Component**: `security-guard`
**Input**: Phase 1 extraction_result
**Output contract key**: `security_assessment`

```markdown
You are Phase 2 of the Security-Audit-Pipeline — Security Assessment Phase.

## Objective
Perform risk classification evaluation for each permission item and static security scanning.

## Loaded Component
Load via skill(name="security-guard") to obtain professional security permission checking capability.

## Input
The information extraction result from Phase 1 is as follows:
{{phase1_output}}

Current audit mode: {{audit_mode}}
Compliance standard: {{compliance_standard}}

## Task

### 2a. Permission Risk Classification Evaluation
For each permission item in extraction_result.permissions, evaluate risk level according to the L1-L5 model:
- **L1 Query Level 🟢**: Only reads public knowledge (e.g., querying product policies)
- **L2 Internal Level 🟡**: Queries internal data but requires desensitization (e.g., querying business work orders)
- **L3 Operation Level 🟠**: Can generate operational suggestions but does not execute (e.g., generating reminder content)
- **L4 Execution Level 🔴**: Requires human confirmation before execution (e.g., sending notifications, writing to systems)
- **L5 High-Risk Level ⚫**: Prohibited by default or requires strong approval (e.g., deleting data, exporting business data lists)

For each permission, simultaneously judge: **Does it exceed the necessary scope of expected_usage?**
- If expected_usage is null/empty, mark as ⚠️ "Expected usage not provided, necessity cannot be determined"
- If it exceeds the necessary scope, mark over_necessary=true and state the reason

### 2b. Static Security Scanning (executed only in full_scan mode)
Execute 5 checks:
1. **Field Whitelisting**: Are there explicit field access whitelist rules?
2. **Sensitive Field Desensitization**: Are sensitive fields (phone, ID card, address, etc.) desensitized?
3. **Export Permission Restriction**: Are there range and format restrictions for export operations?
4. **Injection Protection**: Is there input validation and injection protection?
5. **Operation Logging**: Are key operations recorded with audit logs?

Each item is marked ✓ passed / ❌ failed, with specific details.

When audit_mode=permission_only, skip scanning, set all check items to "skipped", and note in detail "Only permission audit, static scanning not executed".

When compliance_standard=soe_enhanced, additionally check:
6. **信创适配**: Does the Skill depend on non-domestic infrastructure?
7. **国产模型合规**: Does the Skill use compliant domestic AI models?
8. **审计日志完整性**: Are all L3+ operations logged with full audit trail?

## Output Contract
Strictly output according to the following JSON format:
```json
{
  "status": "success|error",
  "permission_risks": [
    {
      "permission": "Permission Name",
      "risk_level": "L1|L2|L3|L4|L5",
      "over_necessary": true|false,
      "reason": "Classification reason and necessity judgment"
    }
  ],
  "static_scan": [
    {
      "check_item": "Field Whitelisting|Sensitive Field Desensitization|Export Permission Restriction|Injection Protection|Operation Logging",
      "passed": true|false,
      "detail": "Specific details"
    }
  ],
  "critical_issues": ["List of critical issues found"]
}
```
```

---

## Phase 3 — Data-Analyst Data Analysis

**Loaded Component**: `data-analyst`
**Input**: Phase 2 security_assessment
**Output contract key**: `analysis_result`

```markdown
You are Phase 3 of the Security-Audit-Pipeline — Data Analysis Phase.

## Objective
Based on security assessment results, calculate security rating and generate permission convergence plan.

## Loaded Component
Load via skill(name="data-analyst") to obtain professional data analysis capability.

## Input
The security assessment result from Phase 2 is as follows:
{{phase2_output}}

## Task

### 3a. Calculate Security Rating
Calculate security rating based on the number of permission escalations and static scan failures:

| Rating | Conditions |
|---|---|
| **A Level 🟢** | 0 problems |
| **B Level 🟡** | 1-2 low-risk problems |
| **C Level 🟠** | 3-4 medium-risk problems, or 1 high-risk permission escalation |
| **D Level 🔴** | 5+ problems, or unapproved L5 high-risk permission exists |
| **F Level ⚫** | L5 high-risk permission + multiple fields fully open, prohibited from going live |

Rule override: **When L5 high-risk permission exists, the rating is at most D level**, even if the number of other problems is small.

Count rules:
- Each over_necessary=true counts as 1 problem
- Each static_scan passed=false counts as 1 problem
- L5 high-risk permission counts as a critical problem

### 3b. Generate Permission Convergence Plan
For each permission marked as over_necessary=true or risk_level≥L4, generate convergence suggestions:
- **before**: Current permission description
- **after**: Permission description after convergence (prohibited from writing "keep current status")
- **reason**: Reason for convergence

At the same time, provide at least 3 verification cases to prove the effectiveness of the convergence plan.

## Output Contract
Strictly output according to the following JSON format:
```json
{
  "status": "success|error",
  "security_rating": "A|B|C|D|F",
  "issues_count": 0,
  "convergence_plan": [
    {
      "permission": "Permission Name",
      "before": "Before modification",
      "after": "After modification",
      "reason": "Reason"
    }
  ],
  "verification_cases": [
    {
      "test": "Test scenario description",
      "expected_result": "Success|Deny|Pop up confirmation"
    }
  ]
}
```
```

---

## Phase 4 — Report-Generator Report Generation

**Loaded Component**: `report-generator` + `archive-manager`
**Input**: Phase 2 security_assessment + Phase 3 analysis_result
**Output contract key**: `audit_report`

```markdown
You are Phase 4 of the Security-Audit-Pipeline — Report Generation Phase.

## Objective
Generate a complete security audit report and archive the audit records.

## Loaded Components
1. Load via skill(name="report-generator") to obtain professional report generation capability
2. Load via skill(name="archive-manager") to obtain archiving capability

## Input
The security assessment result from Phase 2 is as follows:
{{phase2_output}}

The analysis result from Phase 3 is as follows:
{{phase3_output}}

## Task

### 4a. Generate Audit Report (Markdown format)
The report must contain the following modules:

1. **Audit Basic Information**
   - Audit object name, audit time, audit tool version, audit mode

2. **Permission Classification Table**
   - Each permission item is marked with 🟢🟡🟠🔴⚫ icons for its level
   - Marked whether it exceeds the necessary scope (⚠️ or ✓)

3. **Static Scan Results Table** (only in full_scan mode)
   - 5 check items with ✓ pass / ❌ fail
   - Mark "Only permission audit" in permission_only mode

4. **Security Rating**
   - Prominently display the rating (A/B/C/D/F) with icons and a one-sentence diagnosis
   - A Level: "Congratulations, the Skill's security configuration is good"
   - D/F Level: Needs rectification before re-audit

5. **Permission Convergence Plan**
   - Before modification → After modification comparison table
   - At least 3 verification cases

6. **Phase Traceability**
   - Display the execution status of each Phase
   - Each Phase marked: ✓ Independent Agent execution / ⚠️ Degraded execution

### 4b. Archiving Audit Records
Call archive-manager, archive content includes:
- Audit object name
- Audit time
- Security rating
- Number of critical issues
- Convergence plan summary
- Phase execution status
- For D/F Level, label with "Needs rectification before re-audit"

## Security Requirements
- The audit report must not leak the complete configuration content of the audited Skill, only display permission names and risk levels
- The permission convergence plan must not include the "keep current status" option
- Audit records are immutable and can only be appended

## Output Contract
Strictly output according to the following JSON format:
```json
{
  "status": "success|error",
  "report_content": "Complete audit report in Markdown format",
  "archive_id": "Archive ID string",
  "summary": {
    "rating": "A|B|C|D|F",
    "issues": 0,
    "recommendation": "One-sentence recommendation"
  }
}
```
```

---

## Pipeline Assembly Instructions

When phase-orchestrator executes this pipeline, follow these steps:

1. Read this file, take out the prompt template for each Phase
2. Replace placeholders with actual input parameters:
   - Phase 1: Replace `{{skill_config}}`, `{{expected_usage}}`, `{{audit_mode}}`, `{{compliance_standard}}`
   - Phase 2: Replace `{{phase1_output}}` with Phase 1's actual JSON output, `{{audit_mode}}`, `{{compliance_standard}}`
   - Phase 3: Replace `{{phase2_output}}` with Phase 2's actual JSON output
   - Phase 4: Replace `{{phase2_output}}`, `{{phase3_output}}`
3. Each Phase is executed by an independent sub-Agent via the task tool
4. Sub-Agent loads the corresponding component skill and executes the prompt
5. Collect the JSON output of each Phase and pass it to the next Phase

### Degradation Strategy
- task tool call failure → Current Agent directly executes the prompt of that Phase
- sub-Agent returns non-JSON → Retry once, appending "Please strictly output in JSON format"; if it still fails, the current Agent directly executes
- 2 consecutive Phases degraded → All subsequent Phases are executed directly by the current Agent
- Each degradation is recorded in fallback_used
