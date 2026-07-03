---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'f604dd3c-46c2-4b8a-b256-6f4f589aa009'
  PropagateID: 'f604dd3c-46c2-4b8a-b256-6f4f589aa009'
  ReservedCode1: 'ccd39473-9721-4317-a195-eed56f585b44'
  ReservedCode2: 'ccd39473-9721-4317-a195-eed56f585b44'
---

# 党建AI助手（Party-Building AI Assistant）

> **版本**: 1.0.0  
> **编排模式**: Phase-Orchestrator 6-Phase 强制链式调用  
> **上级编排**: 可独立触发，也可被 l7-arkclaw-01 等编排调用  
> **触发词**: 党建问答、党务咨询、发展党员、入党积极分子、党支部会议、党建知识、党史问答、政治审查、党建材料、学习台账  

---

## 一、技能定位

面向基层党支部的党建AI助手，提供从**知识问答→安全审查→人工确认→归档沉淀**的全链路党建服务。所有输出必须基于知识库原文，禁止AI编造党务内容。

### 核心能力

| 能力 | 说明 |
|------|------|
| 有据问答 | 基于党建知识库回答，强制标注来源出处 |
| 政治安全审查 | 自动检测政治敏感表述、核实领导人讲话来源 |
| 历史人物核查 | 对提到的历史人物姓名进行交叉验证 |
| 人工确认把关 | 关键内容经人工审批后方可生效 |
| 归档沉淀 | 将确认后的内容沉淀为可检索的党建素材库 |
| 月度台账汇总 | 自动汇总当月学习/会议/活动记录 |

---

## 二、安全规则（红线，不可绕过）

### SR-1 禁止编造讨论内容
- 会议记录、学习心得等**必须基于知识库原文或用户提供的事实**
- AI不得生成虚构的"讨论发言""表态内容""心得体会"
- 如知识库无相关内容，回答"未在知识库中找到相关依据，请补充材料后再生成"

### SR-2 领导人讲话必须有来源
- 涉及领导人讲话、指示、批示的内容，必须标注**原文出处**（文件名+章节/日期）
- 来源不明或知识库未收录的，标注"（待核实——来源未确认）"
- 严禁AI概括、改写或推断领导人讲话原意

### SR-3 素材读取失败不得用AI概括替代
- 知识库读取失败时，**禁止AI凭自身知识生成替代内容**
- 必须向用户报告读取失败，并提供降级方案（见各Phase降级策略）

### SR-4 政治表述一致性
- 所有政治表述须与知识库原文一致，不得擅自简化或改写
- 党的指导思想、路线方针政策等必须完整引用，不得省略

### SR-5 人工确认不可跳过
- Phase 4（人工确认）为强制性环节
- 任何涉及会议记录、决议、学习台账的终稿，未经人工确认不得归档

---

## 三、Phase 编排定义

```
用户请求
   │
   ▼
┌─────────────────────────────────────────┐
│  Phase 1: 知识库问答（knowledge-rag）      │
│  输出: answer + sources + confidence     │
└─────────────┬───────────────────────────┘
              │ sources为空 → 拒绝进入Phase2
              ▼
┌─────────────────────────────────────────┐
│  Phase 2: 政治敏感词审查（security-guard） │
│  输出: review_result + risk_items        │
└─────────────┬───────────────────────────┘
              │ 存在HIGH风险 → 阻断+人工介入
              ▼
┌─────────────────────────────────────────┐
│  Phase 3: 历史人物姓名核查（info-extractor  │
│           + web-search 交叉验证）          │
│  输出: name_check_report                 │
└─────────────┬───────────────────────────┘
              │ 姓名核查失败 → 标注"待核实"
              ▼
┌─────────────────────────────────────────┐
│  Phase 4: 人工确认（human-in-loop）        │
│  输出: approved_content + signer          │
└─────────────┬───────────────────────────┘
              │ 未确认 → 终止，不进入Phase5
              ▼
┌─────────────────────────────────────────┐
│  Phase 5: 归档沉淀（archive-manager）      │
│  输出: archive_id + tags                  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Phase 6: 月度台账汇总（scheduler +        │
│  data-analyst + report-generator）        │
│  输出: monthly_ledger                     │
└─────────────────────────────────────────┘
```

---

## 四、各Phase详细定义

### Phase 1: 知识库问答

| 项目 | 说明 |
|------|------|
| **调用组件** | `knowledge-rag` |
| **输入** | `{"query": "用户问题", "kb_scope": "party_building"}` |
| **输出** | `{"answer": "回答内容", "sources": [{"title": "来源文档名", "section": "章节", "quote": "原文引用"}], "confidence": 0.0~1.0}` |
| **准入条件** | query 非空 |
| **退出条件** | sources 非空（至少1条来源） |

**核心规则**:
1. 必须返回 `sources` 字段，每条来源包含 `title`、`section`、`quote` 三要素
2. 回答中引用的知识点必须与 `sources[].quote` 原文对应
3. 如知识库无匹配结果，`answer` 固定返回: "未在知识库中找到相关依据，请补充材料后再生成"，`sources` 为空

**降级策略**:
- 知识库不可用 → 返回错误信息，**禁止AI自行概括**，提示用户检查知识库配置
- 知识库部分匹配 → 返回已有匹配，对未覆盖部分明确标注"知识库未收录此内容"

---

### Phase 2: 政治敏感词审查

| 项目 | 说明 |
|------|------|
| **调用组件** | `security-guard`（扩展政治审查规则） |
| **输入** | `{"content": Phase1的answer, "check_mode": "political_review"}` |
| **输出** | `{"review_result": "PASS|WARN|BLOCK", "risk_items": [{"text": "风险文本", "risk_level": "HIGH|MEDIUM|LOW", "reason": "风险原因", "suggestion": "修改建议"}]}` |

**审查规则（按优先级）**:

| 规则ID | 检查内容 | 风险等级 | 处置 |
|--------|---------|---------|------|
| PR-01 | 领导人姓名+职务是否准确完整 | HIGH | BLOCK |
| PR-02 | 党的指导思想表述是否完整（不得省略"三个代表"重要思想、科学发展观等） | HIGH | BLOCK |
| PR-03 | 政治术语用词是否规范（如"两个确立""两个维护"不可简写） | MEDIUM | WARN |
| PR-04 | 是否包含未经引用的领导人讲话 | HIGH | BLOCK |
| PR-05 | 历史事件定性表述是否与权威文献一致 | MEDIUM | WARN |
| PR-06 | 是否含AI编造的讨论/发言/表态内容 | HIGH | BLOCK |

**处置逻辑**:
- `BLOCK` → 阻断流水线，向用户展示风险项，等待人工修正后重新进入Phase 2
- `WARN` → 标注风险项，附修改建议，继续进入Phase 3（保留警告记录）
- `PASS` → 无风险，直接进入Phase 3

**降级策略**:
- security-guard 不可用 → **阻止继续执行**，向用户报告"政治审查组件不可用，为安全起见暂停处理"，交由人工审查

---

### Phase 3: 历史人物姓名核查

| 项目 | 说明 |
|------|------|
| **调用组件** | `info-extractor`（提取姓名实体） + `web-search`（交叉验证） |
| **输入** | `{"content": Phase1的answer, "check_mode": "name_verification"}` |
| **输出** | `{"name_check_report": {"names_found": ["姓名1", "姓名2"], "verification_results": [{"name": "姓名", "status": "VERIFIED|MISMATCH|UNCERTAIN", "source": "验证来源", "note": "备注"}]}}` |

**核查流程**:
1. `info-extractor` 从 content 中提取所有人物姓名
2. 若姓名列表为空 → 直接通过，输出 `names_found: []`
3. 对每个提取的姓名，用 `web-search` 搜索官方来源交叉验证
4. 验证维度：
   - 姓名用字是否正确（如"邓小平"非"邓小萍"）
   - 职务/身份是否在对应语境中准确
   - 引述的讲话/事迹是否有可靠来源

**输出标注**:
- `VERIFIED` → 有权威来源确认，通过
- `MISMATCH` → 姓名/职务与权威来源不符，标注"（姓名有误，请核实）"
- `UNCERTAIN` → 无法确认，标注"（待核实）"

**降级策略**:
- web-search 不可用 → 所有姓名统一标注 `UNCERTAIN`（待核实），不删除不修改，继续进入Phase 4
- info-extractor 不可用 → 跳过姓名提取，生成警告"人物姓名未经验证"，交Phase 4人工确认

---

### Phase 4: 人工确认

| 项目 | 说明 |
|------|------|
| **调用组件** | `human-in-loop` |
| **输入** | `{"content": Phase1回答, "sources": Phase1来源, "review_result": Phase2审查结果, "name_check": Phase3姓名核查结果}` |
| **输出** | `{"approved": true|false, "approved_content": "确认后的内容", "signer": "确认人", "modifications": ["修改说明1", "修改说明2"]}` |

**审批单内容**:
1. **内容预览**: 展示完整的回答内容
2. **来源列表**: 展示所有知识库来源
3. **安全审查结果**: 展示Phase 2的风险项（如有）
4. **姓名核查结果**: 展示Phase 3的验证状态（如有UNCERTAIN/MISMATCH）
5. **确认选项**: 
   - ✅ 确认通过（可附修改意见）
   - ❌ 驳回重做
   - ⏸️ 暂存待议

**强制规则**:
- 未经 `approved: true` 的内容**绝对禁止**进入Phase 5归档
- 人工修改后的内容视为最终版本，AI不得再次自动修改
- 确认人信息必须记录（`signer` 字段）

**降级策略**:
- human-in-loop 不可用 → **终止流水线**，将内容暂存为草稿（draft），提示用户手动确认后重新触发

---

### Phase 5: 归档沉淀

| 项目 | 说明 |
|------|------|
| **调用组件** | `archive-manager` |
| **输入** | `{"content": Phase4确认后的内容, "sources": 来源信息, "metadata": {"type": "会议记录|学习心得|党务问答|政策解读", "date": "归档日期", "branch": "党支部名称", "signer": "确认人", "tags": ["党建", 自动生成标签]}}` |
| **输出** | `{"archive_id": "唯一归档ID", "tags": ["标签列表"], "status": "ARCHIVED"}` |

**归档规则**:
1. 归档类型自动识别：会议记录、学习心得、党务问答、政策解读
2. 自动生成标签：从内容中提取关键词（如"发展党员""入党积极分子"等）
3. 归档内容必须包含：
   - 原文内容（Phase 4确认版）
   - 知识库来源
   - 安全审查记录
   - 人工确认记录
4. 支持按标签、日期、类型检索

**降级策略**:
- archive-manager 不可用 → 将确认内容临时保存为本地文件（`.temp/party-building-archive-pending/`），标注"待归档"，等组件恢复后补归档

---

### Phase 6: 月度学习台账自动汇总

| 项目 | 说明 |
|------|------|
| **调用组件** | `scheduler`（定时触发）+ `data-analyst`（统计分析）+ `report-generator`（报告生成） |
| **输入** | `{"period": "2026-06", "scope": "party_building", "archive_ids": [Phase5归档ID列表]}` |
| **输出** | `{"monthly_ledger": {"period": "月份", "summary": {"total_activities": N, "by_type": {"会议记录": N, "学习心得": N, "党务问答": N, "政策解读": N}, "key_topics": ["主题1", "主题2"]}, "report_path": "台账文件路径"}}` |

**汇总逻辑**:
1. `scheduler` 每月1日自动触发（ cron: `0 9 1 * *` ）
2. `data-analyst` 从归档库中提取上月所有党建素材，按类型/主题/频次统计分析
3. `report-generator` 生成月度学习台账，包含：
   - 本月学习活动统计
   - 重点学习主题
   - 参与情况
   - 下月学习建议（基于主题覆盖分析）

**台账报告格式**:
```
XX党支部20XX年X月学习台账
──────────────────────
一、本月学习概况
  - 组织学习活动：N次
  - 学习内容覆盖：[主题列表]
  - 参与人次：N人

二、分类统计
  | 类型     | 数量 | 占比  |
  |---------|-----|-------|
  | 会议记录 | N   | XX%   |
  | 学习心得 | N   | XX%   |
  | 党务问答 | N   | XX%   |
  | 政策解读 | N   | XX%   |

三、重点主题回顾
  （基于归档内容自动提炼）

四、下月学习建议
  （基于主题覆盖缺口自动建议）

签字：___________  日期：___________
```

**降级策略**:
- scheduler 不可用 → 提示用户手动触发汇总指令
- data-analyst 不可用 → 用基础统计（计数+分类）代替深度分析，标注"分析功能降级"
- report-generator 不可用 → 输出JSON格式统计数据，提示用户手动排版

---

## 五、Phase 间数据传递规范

所有Phase间通信使用结构化JSON，通过Phase-Orchestrator在sub-Agent间传递：

```json
{
  "request_id": "唯一请求ID",
  "current_phase": 1,
  "phase_results": {
    "phase1": { "...Phase1输出..." },
    "phase2": { "...Phase2输出..." },
    "phase3": { "...Phase3输出..." },
    "phase4": { "...Phase4输出..." },
    "phase5": { "...Phase5输出..." },
    "phase6": { "...Phase6输出..." }
  },
  "error_log": [],
  "status": "RUNNING|COMPLETED|BLOCKED|FAILED"
}
```

**流转条件**:

| Phase | 通过条件 | 阻断条件 |
|-------|---------|---------|
| 1→2 | `sources` 非空 | `sources` 为空 |
| 2→3 | `review_result` ≠ BLOCK | `review_result` = BLOCK |
| 3→4 | 无硬性阻断（UNCERTAIN可进入Phase4） | — |
| 4→5 | `approved` = true | `approved` = false 或未确认 |
| 5→6 | 归档成功 | 归档失败 |
| 6 | 汇总完成 | — |

---

## 六、触发场景与示例

### 场景1：知识问答
```
用户: "入党积极分子的培养考察期是多久？"
→ Phase1: 从知识库检索，返回答案+来源
→ Phase2: 审查政治表述是否规范
→ Phase3: 无历史人物姓名，直接通过
→ Phase4: 展示确认单，用户确认
→ Phase5: 归档为"党务问答"类素材
```

### 场景2：会议记录生成
```
用户: "帮我生成一份发展党员专题会议记录"
→ Phase1: 从知识库提取相关法规条款
→ Phase2: 检查是否含编造的讨论内容、领导人讲话是否有来源
→ Phase3: 核查会议中提到的历史人物姓名
→ Phase4: 人工确认会议内容真实性
→ Phase5: 归档为"会议记录"类素材
→ Phase6: 纳入当月学习台账
```

### 场景3：月度台账汇总
```
用户: "生成本月党建学习台账"
→ 直接进入Phase6: 从归档库提取本月素材
→ data-analyst 统计分析
→ report-generator 生成台账
→ Phase4: 人工确认后归档
```

---

## 七、依赖组件清单

| 组件 | 用途 | Phase | 必须 |
|------|------|-------|------|
| `knowledge-rag` | 知识库问答 | 1 | ✅ |
| `security-guard` | 政治敏感词审查 | 2 | ✅ |
| `info-extractor` | 姓名实体提取 | 3 | ✅ |
| `web-search` | 姓名交叉验证 | 3 | ⬜ 降级可用 |
| `human-in-loop` | 人工确认 | 4 | ✅ |
| `archive-manager` | 归档沉淀 | 5 | ✅ |
| `scheduler` | 定时触发 | 6 | ⬜ 降级可手动 |
| `data-analyst` | 统计分析 | 6 | ⬜ 降级为基础统计 |
| `report-generator` | 报告生成 | 6 | ⬜ 降级输出JSON |
| `phase-orchestrator` | Phase编排调度 | 全程 | ✅ |

---

## 八、错误处理与日志

### 错误分级

| 等级 | 含义 | 处置 |
|------|------|------|
| CRITICAL | 安全规则违反（编造内容、无来源领导人讲话） | 立即阻断，记录日志 |
| ERROR | 组件不可用、知识库读取失败 | 降级或阻断，记录日志 |
| WARN | 审查警告（MEDIUM风险、UNCERTAIN姓名） | 标注后继续，记录日志 |
| INFO | 正常流程节点 | 记录日志 |

### 日志格式
```
[时间] [等级] [PhaseN] 消息内容 | request_id=xxx
```

---

## 九、配置项

```yaml
party_building_assistant:
  knowledge_base:
    scope: "party_building"          # 知识库范围标识
    min_confidence: 0.6              # 最低置信度阈值
    fallback_on_no_match: "reject"   # 无匹配时拒绝而非AI生成
  
  political_review:
    leader_speech_source_required: true  # 领导人讲话必须标注来源
    full_ideology_required: true         # 指导思想必须完整引用
    block_on_high_risk: true             # HIGH风险自动阻断
  
  name_verification:
    enabled: true
    search_sources: ["gov.cn", "12371.cn", "people.com.cn"]  # 验证来源白名单
  
  human_confirmation:
    required_for_archive: true       # 归档前必须人工确认
    timeout_hours: 72                # 确认超时时间
  
  monthly_ledger:
    cron: "0 9 1 * *"                # 每月1日9:00自动触发
    report_format: "docx"            # 台账输出格式
```

---

## 十、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-06-26 | 初始版本，6-Phase完整流水线 |

> AI生成