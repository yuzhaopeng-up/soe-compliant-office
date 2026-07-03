---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '3127dc8b-4d66-4a54-813f-3fc379f10393'
  PropagateID: '3127dc8b-4d66-4a54-813f-3fc379f10393'
  ReservedCode1: 'd9ed7be9-03cc-4e43-8095-f305f611a922'
  ReservedCode2: 'd9ed7be9-03cc-4e43-8095-f305f611a922'
---

# AI Agent Skill工程化：GitHub开源项目与资料调研报告

> 调研时间：2026-07-01 | 覆盖范围：2025.10 - 2026.07 | 来源：GitHub + 技术社区

---

## 一、agent-skills 项目 — 核心架构与SKILL.md规范

### 1.1 Anthropic 官方：anthropics/skills
| 字段 | 内容 |
|------|------|
| **项目名** | anthropics/skills |
| **URL** | https://github.com/anthropics/skills |
| **Stars** | 约20K+（2026年5月数据） |
| **核心贡献** | Agent Skills开放标准的官方实现，16个生产级技能库 |
| **关键架构** | 见下文 |

**SKILL.md规范核心要素：**
```
skill-name/
├── SKILL.md          # 必需：YAML前置元数据 + Markdown指令文档
├── scripts/          # 可选：Python/Bash可执行脚本
├── references/       # 可选：按需加载的参考文档
└── assets/           # 可选：模板、字体、图标等输出资源
```

**SKILL.md元数据格式：**
```yaml
---
name: skill-name
version: 1.0.0
description: 一句话描述
triggers:            # 触发关键词
  - 关键词1
  - 关键词2
dependencies:        # 依赖的其他Skill或MCP Server
  - another-skill
---
# 正文：分步指令、工作流、约束规则
```

**6大设计原则（Anthropic官方）：**
1. 渐进式披露（Progressive Disclosure）— 分层加载，按需注入上下文
2. 单一职责 — 每个Skill专注一个领域
3. 幂等性 — 重复执行不产生副作用
4. 可组合性 — Skill之间可串联编排
5. 可测试性 — 输出可验证
6. 安全边界 — 明确权限和访问范围

**16个官方Skill分类：**
- 文档处理类：docx、pdf、pptx、xlsx
- 创意设计类：算法艺术、前端设计
- 开发技术类：Web测试、MCP构建
- 元技能：skill-creator（创建新Skill的Skill）

### 1.2 Agent Skills 开放标准
| 字段 | 内容 |
|------|------|
| **项目名** | agentskills（GitHub Organization） |
| **URL** | https://github.com/agentskills |
| **官网** | https://agentskills.io |
| **核心贡献** | 将Agent Skills从Claude专属升级为跨平台开放标准 |
| **关键架构** | 定义了兼容Claude Code/Codex/Cursor/Gemini的统一格式 |

**时间线：**
- 2025-10-16：Anthropic发布Claude Skills（Pro用户限定）
- 2025-12-18：Agent Skills开放标准发布，agentskills.io上线
- 2026-01：GitHub Copilot、OpenAI Codex、Cursor全部跟进支持
- 2026-05：社区Skill数量突破70万，占GitHub全站4%的提交

---

## 二、Claude Skills 生态 — 分类体系与最佳实践

### 2.1 生态规模
- **社区Skill总量**：70万+（2026年5月）
- **ClawHub**：16,000+ Skills（OpenClaw官方市场）
- **GitHub Trending**：2026年2月，前5名中4个是Agent/Skills项目

### 2.2 主要Skill合集仓库

| 项目名 | URL | Stars | 核心贡献 |
|--------|-----|-------|----------|
| **mattpocock/skills** | https://github.com/mattpocock/skills | ~58K | "Skills for Real Engineers"，21个工程化Skill，引发Agent工作流工程化讨论 |
| **badhope/AI-SKILL** | https://github.com/badhope/AI-SKILL | 高 | 2677+ Skills，14大类，支持13个平台（Claude/Cursor/Gemini/豆包/通义等） |
| **JackyST0/awesome-agent-skills** | https://github.com/JackyST0/awesome-agent-skills | 高 | 精选列表，适配Cursor/Claude Code/GitHub Copilot |
| **LuckyOneTwoThree/All-Skill** | https://github.com/LuckyOneTwoThree/All-Skill | 中 | 179个产品全生命周期Skills（PM×UI×Backend） |
| **K-Dense-AI/scientific-agent-skills** | https://github.com/K-Dense-AI/claude-scientific-skills | 高 | 140+科研Skills，16万科学家使用，覆盖生/化/医/药 |
| **psenger/ai-agent-skills** | https://github.com/psenger/ai-agent-skills | 中 | 生产级Skills，支持Claude Code/Codex/Cursor |
| **ZhanlinCui/Agent-Skills-Hunter** | https://github.com/ZhanlinCui/Agent-Skills-Hunter | 中 | 400+高质量Skills终极集合 |
| **NVIDIA/skills** | https://github.com/nvidia/skills | 高 | NVIDIA官方发布的Skills（Omniverse/USD等） |
| **microsoft/agent-skills** | https://github.com/microsoft/agent-skills | 高 | 微软官方Skills+MCP Servers+Custom Agents，622+commits |

### 2.3 Skill分类体系（行业共识）
| 类别 | 占比 | 代表Skill |
|------|------|-----------|
| 开发辅助类 | 最高（最早爆发） | 代码审查、测试生成、CI/CD |
| 文档处理类 | 高 | docx/pdf/pptx/xlsx生成 |
| 数据分析类 | 中 | 报表生成、趋势分析 |
| 创意设计类 | 增长快 | 前端设计、算法艺术 |
| 安全审计类 | 新兴 | 渗透测试、代码审计 |
| 运维自动化类 | 稳定 | SRE工具集、监控 |

### 2.4 最佳实践来源
| 项目名 | URL | 核心贡献 |
|--------|-----|----------|
| **lovstudio/agent-skill-design-guide** | https://github.com/lovstudio/agent-skill-design-guide | 系统化Skill设计方法论，从架构到发布的完整指南 |
| **GitHub官方文档** | https://docs.github.com/copilot/concepts/agents/about-agent-skills | Copilot Skill创建规范 |
| **Anthropic官方博客** | https://claude.com/blog/building-agents-with-skills | Skills完整思考与设计哲学 |

---

## 三、MCP协议与Skill的关系 — 工具调用标准化

### 3.1 四层技术栈架构（行业共识）

```
┌────────────────────────────────────────┐
│  Layer 4: SubAgent/Workflow            │  ← 多Agent编排层
├────────────────────────────────────────┤
│  Layer 3: Skills（业务流程/SOP）        │  ← 知识+流程+编排层
├────────────────────────────────────────┤
│  Layer 2: Tools（功能封装）             │  ← 单一功能调用层
├────────────────────────────────────────┤
│  Layer 1: MCP（通信协议/接口标准）      │  ← 底层互操作层
└────────────────────────────────────────┘
```

**核心关系总结：**
| 概念 | 定位 | 类比 | 解决的问题 |
|------|------|------|-----------|
| **MCP** | USB协议（通信标准） | 电源插座 | AI"能"调用什么工具 |
| **Tool** | 功能按钮（执行单元） | 电器 | 单一功能调用 |
| **Skill** | 应用程序（业务流程） | 厨师菜谱 | AI"应该"怎么做一件事 |
| **SubAgent** | 多工种协作 | 厨房团队 | 多步骤复杂任务编排 |

### 3.2 关键项目

| 项目名 | URL | 核心贡献 |
|--------|-----|----------|
| **Ghostricke9/StudyAgent** | https://github.com/ghostricke9/studyagent | Function Call + Skills + MCP 三层能力体完整实现 |
| **MMA-JAY/super-agent** | https://github.com/MMA-JAY/super-agent | 企业级Agent平台，覆盖MCP+Skills+RAG全链路 |
| **universal-tool-calling-protocol** | https://github.com/universal-tool-calling-protocol | UTCP协议，跨通道统一工具调用 |
| **microsoft/agent-skills** | https://github.com/microsoft/agent-skills | Skills + MCP Servers + Custom Agents集成方案 |

### 3.3 Skill对MCP的Token优化机制
- MCP每次加载全部工具描述→Token膨胀严重
- Skill通过**渐进式披露**解决：先注入摘要，按需加载详细指令
- 两者是互补而非对立：MCP提供工具接入能力，Skill提供业务流程编排

---

## 四、Skill注册中心/市场 — 分发和发现机制

### 4.1 主要注册中心

| 项目名 | URL | 核心贡献 |
|--------|-----|----------|
| **openclaw/clawhub** | https://github.com/openclaw/clawhub | OpenClaw官方Skill+Plugin注册中心，16K+ Skills，类npm包管理器 |
| **iflytek/skillhub** | https://github.com/iflytek/skillhub | 科大讯飞出品，企业级自托管Skill注册中心，RBAC+审计日志，Docker/K8s部署 |
| **A-Duang/skill-manager** | https://github.com/A-Duang/skill-manager | Skill跨平台管理器，一键复制到多平台（Tauri桌面应用） |
| **miracletiger/skills_agent** | https://github.com/miracletiger/skills_agent | Skills Foundry：智能体自动将需求转为Skill包，Generate→Validate→Test→Publish |
| **kriptoburak/skills-registry** | https://github.com/kriptoburak/skills-registry | 浏览/标签/安装一体化，支持Claude Code/OpenClaw/Codex |

### 4.2 分发机制对比

| 机制 | 代表 | 特点 |
|------|------|------|
| **CLI包管理** | `npx skills add` / `openclaw skills install` | 一条命令安装，类似npm |
| **Marketplace** | Claude Marketplace / ClawHub | 可视化浏览、版本追踪 |
| **Git仓库** | GitHub直接clone到`.claude/skills/` | 最原始但最灵活 |
| **企业私有** | SkillHub | 自托管、RBAC、审计合规 |

### 4.3 Skill发现路径
```
存储库级: .github/skills/           → 项目专用
用户级:   ~/.claude/skills/          → 个人通用
平台级:   ClawHub / Claude Marketplace → 社区共享
企业级:   SkillHub                   → 组织治理
```

---

## 五、Skill版本管理和依赖解析

### 5.1 现状
- **当前主流**：SKILL.md中通过YAML前置元数据的`version`和`dependencies`字段声明
- **ClawHub**：提供版本追踪，了解安装来源和版本号
- **SkillHub（科大讯飞）**：企业级版本管理，支持发布和版本化Skill包

### 5.2 关键设计模式
```yaml
# SKILL.md中的依赖声明
---
name: data-analyst
version: 2.1.0
dependencies:
  - name: security-guard
    version: ">=1.0.0"
  - name: info-extractor
    version: "^1.2.0"
  - mcp_server: mysql
---
```

### 5.3 待解决问题
- 缺乏统一的语义化版本规范（SemVer未成标准）
- 依赖冲突解决机制不成熟
- 跨平台版本兼容性验证缺失
- 锁文件（lockfile）机制尚未出现

---

## 六、Skill安全扫描和审计工具

### 6.1 重大安全事件
| 事件 | 时间 | 影响 |
|------|------|------|
| **ClawHavoc供应链攻击** | 2026年初 | 1184个恶意Skill，24.7万次安装 |
| **ClawHub恶意渗透** | 2026年2月 | 472+恶意Skills，窃取SSH密钥和API Token |
| **Koi Security审计** | 2026年3月 | 至少341个恶意Skill存在 |
| **Snyk ToxicSkills报告** | 2026年 | 36.82%的Skill存在安全风险 |

### 6.2 安全扫描工具

| 项目名 | URL | Stars | 核心贡献 |
|--------|-----|-------|----------|
| **NVIDIA/SkillSpector** | https://github.com/nvidia/skillspector | ~11K | 16类64条规则，静态分析+LLM语义评估，AST+污点流分析，CI/SARIF输出 |
| **smartchainark/skill-security-audit** | https://github.com/smartchainark/skill-security-audit | 中 | ClawHavoc事件后首发，`npx skills add`安装即扫 |
| **RuoJi6/audit-skills** | https://github.com/RuoJi6/audit-skills | 927 | 专注代码审计，最小化轻量，只负责安全边界 |
| **bruc3van/agent-skills-guard** | GitHub话题：skill-scanner | - | 桌面应用，安全扫描+可视化管理 |

### 6.3 SkillSpector架构详解（NVIDIA）
```
扫描流水线：
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Phase 1      │     │ Phase 2      │     │ Phase 3      │
│ 静态分析     │ ──→ │ AST+污点流   │ ──→ │ LLM语义评估  │
│ (64条规则)   │     │ (代码注入检测)│     │ (可选增强)   │
└──────────────┘     └──────────────┘     └──────────────┘
       ↓                    ↓                     ↓
   正则匹配            Python AST解析        LLM二次审查
   密码窃取检测        污点传播追踪          Prompt注入检测
   供应链扫描          权限提升分析          MCP安全检查
```

**16类安全风险：** 代码注入、数据泄露、权限提升、环境变量访问、网络请求、文件系统操作、命令执行、API密钥暴露、Prompt注入、依赖投毒、沙箱逃逸、信息收集、后门植入、资源耗尽、隐蔽通道、MCP工具滥用

### 6.4 评测基准

| 项目名 | 核心贡献 |
|--------|----------|
| **SkillTrustBench**（腾讯朱雀+港中深） | 首个Agent Skill安全评测基准，从62,652个Skill提炼5,520评测用例，覆盖九大威胁类型 |

---

## 七、Multi-Agent中Skill编排模式

### 7.1 编排项目

| 项目名 | URL | Stars | 核心贡献 |
|--------|-----|-------|----------|
| **KimYx0207/agent-teams-playbook** | https://github.com/KimYx0207/agent-teams-playbook | 高 | Claude Code多智能体编排Skill，自适应决策+6阶段工作流+5大场景，兼容4平台 |
| **jessepwj/CCteam-creator** | https://github.com/jessepwj/CCteam-creator | 中 | Multi-agent team编排，2-6 Agent并行，内置CI工程实践 |
| **davidtoby/edict** | https://github.com/davidtoby/edict | 高 | "三省六部制"多Agent编排，12个Agent角色，实时看板，审计追踪 |
| **architect-4-citadell/elektra-skills** | https://github.com/architect-4-citadell/elektra-skills | 中 | 治理型Skills，RAI gates结构化执行，66+生产会话验证 |
| **CaSkade-Automation/BPMN-SkillExecutor** | GitHub话题：skill-orchestration | - | BPMN流程引擎中嵌入Skill编排 |

### 7.2 编排模式总结

| 模式 | 描述 | 代表实现 |
|------|------|----------|
| **Phase链式编排** | Phase1→Phase2→...→PhaseN串行，Phase间JSON传递 | agent-teams-playbook |
| **蜂群并行编排** | 多Agent并行执行，汇总压缩结果 | CCteam-creator |
| **分层审核编排** | 规划→审核→执行三级分权制衡 | edict（三省六部） |
| **治理门控编排** | 每步执行前过RAI gate和安全检查 | elektra-skills |
| **文件驱动编排** | 通过持久化Markdown文件协调多Agent | planning-with-files |
| **事件驱动编排** | Skill作为事件处理器，按事件触发 | BPMN-SkillExecutor |

### 7.3 Skill编排的架构设计模式
```
┌─────────────────────────────────────────────┐
│           Orchestrator（编排器）              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Skill A │  │ Skill B │  │ Skill C │     │
│  │ (提取)  │  │ (分析)  │  │ (报告)  │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │           │
│  ┌────▼────────────▼────────────▼────┐      │
│  │   Structured JSON Data Bus       │      │
│  └──────────────────────────────────┘      │
│  ┌──────────────────────────────────┐      │
│  │   Security Guard / RAI Gate      │      │
│  └──────────────────────────────────┘      │
│  ┌──────────────────────────────────┐      │
│  │   Human-in-loop Approval         │      │
│  └──────────────────────────────────┘      │
└─────────────────────────────────────────────┘
```

---

## 八、综合发现与趋势判断

### 8.1 关键趋势
1. **范式转移**：从"Prompt Engineering"到"Skill Engineering"，AI从对话助手进化为数字员工
2. **标准化加速**：Agent Skills开放标准已获全行业采纳，SKILL.md成为事实标准
3. **安全成为刚需**：ClawHavoc事件后，Skill安全扫描从可选项变为必选项
4. **编排成熟化**：从简单串联到分层审核+治理门控的企业级编排
5. **供应链治理**：Skill被视为软件供应链发布物，需要完整的安全审计流程

### 8.2 与我们TeleAgent生态的对应
| 行业概念 | TeleAgent对应 | 状态 |
|----------|--------------|------|
| SKILL.md规范 | 已采用 | 完全兼容 |
| Skill注册中心 | ClawHub集成 | 需加强自托管 |
| 安全扫描 | teleai_claw_scan | 已实现，需对标SkillSpector |
| 编排模式 | phase-orchestrator | 链式+并行已实现 |
| 版本管理 | YAML元数据声明 | 基础实现，缺锁文件 |
| 依赖解析 | SKILL.md dependencies | 待工程化 |

---

*报告完成于 2026-07-01 | 基于GitHub公开项目和社区资料*

> AI生成