# Compliance & Security Domain (Phase 2)

> **合规安全域** — 6个Skill构建央国企合规闭环：前置审查 → 静态审计 → 动态验证 → 运行守门 → 事后追溯

## Skills Overview

| Skill | 核心能力 | SOE SOE Relevance | Type |
|-------|---------|-------------------|------|
| [six-dimension-compliance-check](./six-dimension-compliance-check/) | 6维合规审查，A-D级评级 | 5 | Prompt |
| [human-in-loop](./human-in-loop/) | L1-L5风险分级审批，三重一大守门 | 5 | Prompt |
| [security-guard](./security-guard/) | 最小权限检查，敏感字段检测 | 5 | Prompt |
| [security-auditor](./security-auditor/) | 4-Phase自动化审计，D-A安全评级 | 5 | Prompt |
| [evidence-chain](./evidence-chain/) | 多源交叉验证，置信度评估 | 5 | Prompt |
| [red-team-tester](./red-team-tester/) | 6轮递进式对抗测试 | 5 | Prompt |

## Compliance Pipeline

```
前置审查 ──→ 静态审计 ──→ 动态验证 ──→ 运行守门 ──→ 事后追溯
6-dim       security     red-team     human-in     evidence
check       auditor      tester       loop         chain
```

## SOE Features Covered

- 三重一大集体决策
- 党委前置审议
- 穿透式监管
- 首席合规官审核
- 两人会签制度
- 13710督办制度
- GB/T 35273 数据分级分类
- DA/T 电子归档标准
- 等保合规验证

## Cross-Domain Dependencies

- All compliance skills use `shared/audit_trail.py` for operation logging
- All compliance skills use `shared/desensitize.py` for data classification
- `human-in-loop` depends on `security-guard` for risk assessment
- `security-auditor` depends on `security-guard` for permission evaluation
- `red-team-tester` pairs with `security-auditor` (static + dynamic verification)
