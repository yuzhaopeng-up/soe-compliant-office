---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '413e3170-9640-4d72-b7b0-6526072f30a3'
  PropagateID: '413e3170-9640-4d72-b7b0-6526072f30a3'
  ReservedCode1: 'c3377973-ea51-466e-9a75-a5fcd6c80c92'
  ReservedCode2: 'c3377973-ea51-466e-9a75-a5fcd6c80c92'
---

# SQL Quality Diagnostic — SQL 质量诊断系统

**核心理念**：6-Phase流水线化SQL质量诊断——从慢查询采集到DDL建议输出，性能/安全/合规三线并行，每Phase由独立sub-Agent执行，Phase间结构化JSON透传。

## 适用场景

- 线上慢查询告警，需快速定位根因并输出优化建议
- 上线前SQL Review，检查索引缺失、全表扫描、敏感字段泄漏等风险
- DDL变更审批，需评估索引建议的影响范围与合规性
- 定期SQL健康巡检，扫描全量slow_log生成质量报告
- 安全审计，检测SQL中PII字段暴露、越权访问、注入风险

## 触发词

`SQL诊断`、`慢查询分析`、`SQL优化`、`SQL审查`、`索引建议`、`SQL质量`、`EXPLAIN分析`、`SQL安全检查`、`DDL建议`、`慢SQL`

## 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `sql_input` | string | 是 | - | 待诊断SQL文本，或多条SQL以`;`分隔 |
| `input_source` | enum | 否 | `manual` | 输入来源：`slow_log` / `manual` / `explain_output` |
| `schema_info` | object | 否 | `null` | 数据库schema元信息（表结构/索引/字段类型），用于交叉验证 |
| `db_dialect` | enum | 否 | `mysql` | 数据库方言：`mysql` / `postgresql` / `hive` / `clickhouse` |
| `pii_field_map` | object | 否 | `{}` | PII敏感字段映射，如 `{"phone":"L3","id_card":"L4","email":"L2"}` |
| `desensitize_level` | enum | 否 | `standard` | 脱敏等级：`strict` / `standard` / `light` |
| `diagnosis_depth` | enum | 否 | `standard` | 诊断深度：`quick`(仅P1+P2) / `standard`(P1-P5) / `full`(P1-P6含归档) |
| `max_sql_count` | integer | 否 | `10` | 单次诊断最大SQL条数，防止批量输入撑爆上下文 |
| `output_format` | enum | 否 | `html` | 输出格式：`html` / `markdown` / `json` |

## 6-Phase 编排总览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SQL Quality Diagnostic · 6-Phase Pipeline                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │ Phase 1  │──▶│ Phase 2  │──▶│ Phase 3  │──▶│ Phase 5  │──▶│ Phase 6  │  │
│  │ SQL解析  │   │ 执行计划  │   │ 根因图谱  │   │ 报告告警  │   │ 归档沉淀  │  │
│  │          │   │  分析     │   │    ∥     │   │          │   │          │  │
│  │          │   │          │   │ Phase 4  │   │          │   │          │  │
│  │          │   │          │   │ 敏感脱敏  │   │          │   │          │  │
│  ├──────────┤   ├──────────┤   ├──────────┤   ├──────────┤   ├──────────┤  │
│  │Info-     │   │SQL大师   │   │Root-     │   │Report-   │   │Archive-  │  │
│  │Extractor │   │          │   │Cause-    │   │Generator │   │Manager   │  │
│  │          │   │          │   │Mapper +  │   │+ diagram │   │          │  │
│  │          │   │          │   │Data-     │   │-drawing  │   │          │  │
│  │          │   │          │   │Analyst   │   │          │   │          │  │
│  │          │   │          │   │──────────│   │          │   │          │  │
│  │          │   │          │   │Security- │   │          │   │          │  │
│  │          │   │          │   │Guard +   │   │          │   │          │  │
│  │          │   │          │   │Info-     │   │          │   │          │  │
│  │          │   │          │   │Extractor │   │          │   │          │  │
│  ├──────────┤   ├──────────┤   ├──────────┤   ├──────────┤   ├──────────┤  │
│  │output:   │   │output:   │   │P3:root_  │   │output:   │   │output:   │  │
│  │sql_list  │   │diagnosis │   │cause_    │   │report_   │   │archive_  │  │
│  │          │   │_result   │   │result    │   │result    │   │result    │  │
│  │          │   │          │   │P4:desens │   │          │   │          │  │
│  │          │   │          │   │_result   │   │          │   │          │  │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
│                                                                                 │
│  P3 ∥ P4 并行 │ Phase间数据流: structured JSON │ 每Phase独立sub-Agent         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

> Phase 3（根因图谱推理）和 Phase 4（敏感字段脱敏）**无数据依赖，可并行执行**，随后在 Phase 5 汇聚。

---

## Phase 1: 慢查询采集与SQL解析

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P1 |
| Phase名称 | 慢查询采集与SQL解析 |
| 调用组件 | `skill(name="info-extractor")` |
| 执行模式 | 同步，单Agent |
| 超时阈值 | 30s |
| 失败策略 | 标记`parse_error`，跳过P2-P6，直接输出错误报告 |

### 输入JSON

```json
{
  "sql_input": "SELECT o.*, c.customer_name, c.phone FROM orders o LEFT JOIN customers c ON o.customer_id = c.id WHERE o.create_time > '2024-01-01' AND o.status IN ('pending','processing') ORDER BY o.create_time DESC LIMIT 100",
  "input_source": "manual",
  "schema_info": {
    "tables": {
      "orders": {
        "columns": ["id","customer_id","status","create_time","amount"],
        "indexes": ["PRIMARY(id)","idx_customer_id(customer_id)"],
        "row_count": 5200000
      },
      "customers": {
        "columns": ["id","customer_name","phone","region"],
        "indexes": ["PRIMARY(id)"],
        "row_count": 1200000
      }
    }
  },
  "db_dialect": "mysql",
  "pii_field_map": {"phone": "L3", "id_card": "L3", "email": "L2"},
  "max_sql_count": 10
}
```

### 处理逻辑

```
输入校验
  ├─ sql_input为空或空白 → 抛出错误 {error: "E001", message: "sql_input不可为空"}
  ├─ sql_input条数 > max_sql_count → 截断并追加warning
  └─ schema_info格式校验 → 无效则置null，降级为纯语法解析

SQL语法解析（按条处理）
  ├─ SELECT列提取
  │   ├─ 检测 SELECT * → 标记 risk_flag: SELECT_STAR
  │   └─ 逐列与pii_field_map交叉 → 标记 risk_flag: PII_EXPOSED:{level}
  │
  ├─ FROM/JOIN表提取
  │   ├─ 提取表名、别名、JOIN类型
  │   └─ 与schema_info交叉 → 标记 risk_flag: TABLE_NOT_IN_SCHEMA
  │
  ├─ WHERE条件提取
  │   ├─ 提取过滤列、操作符、值
  │   ├─ 检测函数包裹列（如 WHERE DATE(col)=...）→ risk_flag: FUNC_INDEX_INVALID
  │   ├─ 检测 LIKE '%xxx%' → risk_flag: LEADING_LIKE
  │   └─ 检测 OFFSET > 10000 → risk_flag: DEEP_PAGINATION
  │
  ├─ ORDER BY提取
  │   ├─ 提取排序列和方向
  │   └─ 检测排序列无对应索引 → risk_flag: FILESORT_RISK
  │
  └─ LIMIT提取
      └─ 检测无WHERE的LIMIT → risk_flag: UNCONDITIONAL_LIMIT

schema交叉验证（当schema_info非null时）
  ├─ 列是否存在于表定义
  ├─ WHERE/JOIN列是否有索引覆盖
  └─ 标记缺失索引到 risk_flag: MISSING_INDEX:{column}
```

### 输出JSON

```json
{
  "phase": "P1",
  "status": "success",
  "sql_list": [
    {
      "sql_id": "SQL_001",
      "sql_text": "SELECT o.*, c.customer_name, c.phone FROM orders o LEFT JOIN customers c ON o.customer_id = c.id WHERE o.create_time > '2024-01-01' AND o.status IN ('pending','processing') ORDER BY o.create_time DESC LIMIT 100",
      "tables": [
        {"name": "orders", "alias": "o", "role": "driving"},
        {"name": "customers", "alias": "c", "role": "joined", "join_type": "LEFT"}
      ],
      "columns": [
        {"table": "orders", "column": "*", "is_star": true},
        {"table": "customers", "column": "customer_name", "pii_level": null},
        {"table": "customers", "column": "phone", "pii_level": "L3"}
      ],
      "join_info": [
        {
          "left_table": "orders",
          "left_column": "customer_id",
          "right_table": "customers",
          "right_column": "id",
          "join_type": "LEFT",
          "index_covered": true
        }
      ],
      "where_info": [
        {"table": "orders", "column": "create_time", "operator": ">", "value": "2024-01-01", "index_covered": false},
        {"table": "orders", "column": "status", "operator": "IN", "value": "['pending','processing']", "index_covered": false}
      ],
      "order_by": [
        {"table": "orders", "column": "create_time", "direction": "DESC", "index_covered": false}
      ],
      "limit": {"offset": 0, "count": 100},
      "risk_flags": [
        {"flag": "SELECT_STAR", "severity": "medium", "detail": "orders表使用SELECT *，触发全列回表"},
        {"flag": "PII_EXPOSED:L3", "severity": "high", "detail": "customers.phone为L3级PII，SELECT直接暴露"},
        {"flag": "MISSING_INDEX:create_time,status", "severity": "high", "detail": "WHERE条件列(create_time,status)无联合索引覆盖"},
        {"flag": "FILESORT_RISK", "severity": "medium", "detail": "ORDER BY create_time DESC无索引，触发Using filesort"}
      ],
      "execution_plan": null,
      "source_metadata": {
        "input_source": "manual",
        "db_dialect": "mysql",
        "parse_timestamp": "2026-06-27T10:00:00Z",
        "schema_validated": true
      }
    }
  ],
  "parse_errors": [],
  "stats": {
    "total_sql_count": 1,
    "parsed_count": 1,
    "error_count": 0,
    "risk_flag_count": 4
  }
}
```

### 异常处理

| 错误码 | 触发条件 | 处理方式 |
|---|---|---|
| E001 | `sql_input`为空或空白 | 终止流水线 |
| E002 | SQL语法解析失败 | 该条SQL标记`parse_error`跳过，其余SQL继续 |
| E003 | `input_source=slow_log`但格式不符 | 尝试正则提取SQL片段，失败则按E002处理 |
| E004 | `input_source=explain_output`无法匹配 | 降级为`manual`模式解析，追加warning |
| W001 | SQL条数超过`max_sql_count` | 截断至max，追加warning |
| W002 | `schema_info`格式异常 | 置null，降级为纯语法解析 |

---

## Phase 2: 执行计划分析与性能诊断

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P2 |
| Phase名称 | Execution Plan Analysis & Performance Diagnosis |
| 调用组件 | SQL大师（EXPLAIN解读）+ Data-Analyst（性能模式识别）+ Security-Guard（DDL风险标注） |
| 执行模式 | 串行（逐条SQL → EXPLAIN → 诊断 → 建议） |
| 超时 | 120s/条，总超时 = min(600s, sql_list.length x 120s) |

### 输入JSON

Phase 1 的 `sql_list` 输出，附加 `db_connection` 配置。

### 处理逻辑

#### Step 1: 执行计划获取

对每条SQL，按以下优先级获取执行计划：

| 优先级 | 方式 | 适用条件 |
|--------|------|----------|
| 1 | `EXPLAIN FORMAT=JSON` | MySQL 5.6+ / db可用 |
| 2 | `EXPLAIN` | 任何MySQL版本 / db可用 |
| 3 | **静态推理** | db不可用，基于P1解析结构推断，标注`[静态推理]` |

#### Step 2: 逐表EXPLAIN字段分析

| 字段 | 关注值 | 判定规则 |
|------|--------|----------|
| **type** | `ALL` | 全表扫描 → `full_table_scan`（high） |
| **type** | `index` | 全索引扫描 → 若非覆盖索引则 `full_index_scan`（medium） |
| **key** | `NULL` | 且有WHERE → `missing_index`（high） |
| **rows** | > 表行数x0.3 | 扫描占比过高，标注在detail |
| **Extra** | `Using filesort` | `filesort`（medium） |
| **Extra** | `Using temporary` | `temporary_table`（medium） |

#### Step 3: 8种性能问题模式识别

| 编号 | 模式 | 触发条件 | severity |
|------|------|---------|----------|
| P2-01 | full_table_scan | type=ALL | high |
| P2-02 | missing_index | key=NULL + WHERE非空 | high |
| P2-03 | filesort | Extra含Using filesort | medium |
| P2-04 | temporary_table | Extra含Using temporary | medium |
| P2-05 | select_star_overflow | SELECT * + 需回表 | low→medium |
| P2-06 | deep_pagination | LIMIT offset > 10000 | medium |
| P2-07 | implicit_type_conversion | 列类型与值类型不匹配 | high |
| P2-08 | or_column_mismatch | OR连接不同列 | medium |

#### Step 4: 索引建议生成

所有 `suggested_index` 必须标注：

```json
{
  "suggested_index": "ALTER TABLE orders ADD INDEX idx_uid_ctime (user_id, create_time)",
  "ddl_risk": "⚠️需DBA审批",
  "ddl_risk_reason": "线上ALTER TABLE可能导致锁表，需在低峰期执行或使用pt-osc/gh-ost工具"
}
```

当表行数 > 100万时，`ddl_risk_reason`追加：`"大表(预估>100万行)风险更高，强烈建议使用gh-ost或pt-online-schema-change"`

#### Step 5: SQL改写建议

| 问题类型 | 改写策略 |
|----------|---------|
| select_star_overflow | 列裁剪：SELECT * → 具体列 |
| deep_pagination | 延迟关联/书签法 |
| implicit_type_conversion | 类型对齐 |
| or_column_mismatch | OR → UNION ALL |
| filesort + missing_index | 索引覆盖ORDER BY |

### 输出JSON

```json
{
  "phase": "P2",
  "degraded_mode": false,
  "diagnosis_result": {
    "sql_diagnoses": [
      {
        "sql_id": "SQL_001",
        "issues": [
          {
            "issue_id": "SQL_001-I01",
            "type": "full_table_scan",
            "severity": "high",
            "table": "orders",
            "affected_columns": ["status", "create_time"],
            "detail": {"description": "WHERE条件列status+create_time均无法利用索引"},
            "current_index": null,
            "suggested_index": "ALTER TABLE orders ADD INDEX idx_status_createtime (status, create_time DESC)",
            "ddl_risk": "⚠️需DBA审批",
            "ddl_risk_reason": "线上ALTER TABLE可能导致锁表，大表建议使用gh-ost"
          }
        ],
        "severity_summary": {"high": 1, "medium": 2, "low": 0},
        "rewrite_suggestion": {
          "strategy": "列裁剪 + 联合索引覆盖",
          "rewritten_sql": "SELECT o.id, o.amount, o.create_time, o.status, c.customer_name FROM ...",
          "expected_improvement": "扫描行数从全表降至5%，filesort消除",
          "confidence": "high"
        }
      }
    ]
  }
}
```

### 异常处理

| 异常场景 | 处理策略 |
|----------|---------|
| 数据库连接失败 | 降级为静态推理，severity降一级并标注`[静态推理]` |
| EXPLAIN执行超时 | 跳过该SQL，记录到skipped_sqls |
| Phase 1 sql_list为空 | 直接输出空结果 |

---

## Phase 3: 根因图谱推理

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P3 |
| Phase名称 | Root-Cause Topology Reasoning |
| 调用组件 | `skill(name="root-cause-mapper")` + `skill(name="data-analyst")` |
| 上游依赖 | Phase 1(元数据) + Phase 2(性能诊断) |
| 可与P4并行 | 是 |
| 超时阈值 | 30s |

### 处理逻辑

#### 3.1 拓扑构建

将P2的issues映射为有向无环图(DAG)的节点和因果边。

**因果规则库**（按优先级匹配）：

```
R1: INDEX_MISS      → SCAN_BLOAT      # 无索引→全表扫描
R2: SCAN_BLOAT      → SORT_SPILL      # 全表扫描→filesort
R3: SORT_SPILL      → LIMIT_FAIL      # filesort→LIMIT无法提前终止
R4: SELECT_STAR     → COVER_MISS      # SELECT *→回表放大
R5: INDEX_MISS      → COVER_MISS      # 无索引→回表放大
R6: DEEP_PAGE       → SCAN_BLOAT      # 深分页→扫描放大
```

#### 3.2 三层推理框架

**层1：时间最早原则** — 同一连通分量内timestamp最早的节点优先级最高

```
earliest_node.layer1_score = 1.0
other_node.layer1_score = 0.3
```

**层2：下游依赖分析** — 从根因候选出发遍历下游，计算覆盖率

```
cascade_coverage = len(下游可达节点) / (连通分量节点数 - 1)
layer2_score = cascade_coverage
```

实战示例：N1(缺失索引) → downstream={N3,N4,N5}， cascade_coverage = 3/5 = 0.60

**层3：独立故障排除** — 识别不依赖主根因的独立问题

```
入度=0且出度=0 → is_independent=true
入度=0且出度>0 → 源头节点，layer3_adjust=+0.1
其他 → 中间/末端节点，layer3_adjust=-0.1
```

#### 3.3 根因综合判定

**置信度合成**：`confidence = 0.30 * layer1_score + 0.70 * layer2_score + layer3_adjust`

| 置信度区间 | 等级 | 含义 |
|---|---|---|
| >= 0.85 | 🔴 主根因 | 高确信，必须立即修复 |
| 0.60 - 0.84 | 🟡 次根因 | 中等确信，纳入修复计划 |
| 0.40 - 0.59 | 🟢 疑似原因 | 低确信，待进一步验证 |
| < 0.40 | ⚪ 独立问题 | 独立于主因果链 |

**故障类型判定**：单源级联型 / 多源级联型 / **多源混合型** / 独立离散型

#### 3.4 建议动作分类

| 等级 | 动作前缀 | 修复模板 |
|---|---|---|
| 🔴优先 | `URGENT:` | ALTER TABLE ADD INDEX / 重写SQL |
| 🟡计划 | `PLAN:` | 加入下个迭代Sprint |
| 🟢暂缓 | `DEFER:` | 观察监控指标后再决策 |

### 输出JSON

```json
{
  "phase": "P3",
  "root_cause_result": {
    "fault_topology": {
      "nodes": [
        {"node_id": "N1", "type": "INDEX_MISS", "detail": "缺失联合索引idx(status,create_time)", "severity": "high", "confidence": 0.82}
      ],
      "edges": [
        {"from": "N1", "to": "N3", "rule": "R1", "rule_desc": "无索引→全表扫描"}
      ]
    },
    "root_causes": [
      {"node_id": "N1", "confidence": 0.82, "cascade_coverage": 0.60, "level": "secondary", "level_icon": "🟡"}
    ],
    "fault_type": "多源混合型",
    "independent_issues": ["N2", "N7"],
    "cascade_paths": [
      {"path": ["N1", "N3", "N4", "N5"], "type": "primary", "description": "缺失索引→全表扫描→filesort→LIMIT失效"},
      {"path": ["N2"], "type": "independent", "description": "SELECT *写法缺陷"}
    ],
    "recommendations": [
      {"level": "PLAN", "action": "ALTER TABLE orders ADD INDEX idx(status,create_time)", "expected_improvement": "扫描行数降至5%，filesort消除"},
      {"level": "DEFER", "action": "SELECT *改为指定列，利用覆盖索引"}
    ],
    "mermaid_code": "graph TD\n    N1[\"N1:缺失索引 idx(status,create_time)\"] -->|R1| N3[\"N3:全表扫描\"]\n    N3 -->|R2| N4[\"N4:filesort\"]\n    N4 -->|R3| N5[\"N5:LIMIT失效\"]\n    N2[\"N2:SELECT *\"] -.->|R4| N5\n    style N1 fill:#ff6b6b\n    style N2 fill:#ffd93d"
  }
}
```

### 异常处理

| 异常场景 | 处理策略 |
|----------|---------|
| Phase 2无issues | 输出空拓扑，fault_type="healthy" |
| 图环路检测 | 拆除severity最低的边 |
| 置信度全部<0.40 | fault_type="待定"，全部recommendations标记DEFER |
| 推理超时 | 截断层3，以层1+层2结果输出，degraded=true |

---

## Phase 4: 敏感字段检测与脱敏

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P4 |
| Phase名称 | Sensitive Field Detection & Desensitization |
| 调用组件 | `skill(name="security-guard")` + `skill(name="info-extractor")` |
| 前置依赖 | Phase 1 (parsed_queries) + Phase 2 (diagnosis_result) |
| 可与P3并行 | 是 |
| 失败策略 | **阻断Pipeline**（脱敏复核不通过则P5不执行） |

### 处理逻辑

#### 4.1 敏感字段分级表

| 字段名模式 | 分级 | 标签 | 脱敏规则 | 示例 |
|---|:---:|:---:|---|---|
| phone / mobile / tel / cell | **L3** | 🔴 | PARTIAL_MASK | 138****8000 |
| id_card / identity / sfz | **L3** | 🔴 | FULL_REDACT | [REDACTED] |
| address / addr | **L3** | 🔴 | RANGE_MASK | 北京市**** |
| password / secret / token | **L3** | 🔴 | FULL_REDACT | [REDACTED] |
| bank_card / card_no | **L3** | 🔴 | PARTIAL_MASK | 6222****1234 |
| email / mail | **L2** | 🟡 | DOMAIN_KEEP | z***@qq.com |
| customer_name / real_name / 姓名 | **L2** | 🟡 | FIRST_CHAR_KEEP | 张** |
| amount / balance / salary | **L1** | 🟢 | NOP | 100.50 |
| order_id / status / create_time | **L1** | 🟢 | NOP | — |

#### 4.2 desensitize_level等级对照

| 等级 | L3 🔴 处理 | L2 🟡 处理 | L1 🟢 处理 | 适用场景 |
|:---:|---|---|---|---|
| `strict` | FULL_REDACT | HASH_REPLACE | NOP | 生产环境报告、外部交付 |
| `standard` | PARTIAL_MASK | FIRST_CHAR_KEEP | NOP | 内部技术评审 |
| `light` | PARTIAL_MASK | NOP | NOP | 开发调试 |

#### 4.3 安全审查5项检查

| 编号 | 检查项 | 不通过动作 |
|:---:|---|---|
| C1 | SELECT * 暴露风险 | 标记select_star_risk，安全SQL中展开为显式字段 |
| C2 | PII出现在WHERE条件 | 标记pii_in_where，参数化替换WHERE值为? |
| C3 | DDL缺少审批提示 | 标记ddl_without_approval，DDL前插入⚠️需DBA审批 |
| C4 | 验证步骤使用真实数据 | 标记raw_data_in_test，替换为脱敏占位符 |
| C5 | 报告输出含明文PII | **二次脱敏，阻断直到扫描通过** |

#### 4.4 只读性审查

| SQL类型 | 审查策略 |
|---|---|
| SELECT / EXPLAIN | ✅ 只读，安全通过 |
| CREATE INDEX / ALTER / DROP | ⚠️ DDL，需DBA审批 |
| INSERT / UPDATE / DELETE | ❌ 本系统不处理 |

### 输出JSON

```json
{
  "phase": "P4",
  "desensitization_result": {
    "query_id": "SQL_001",
    "desensitize_level_applied": "standard",
    "field_risks": [
      {"field": "c.phone", "risk_level": "L3", "risk_label": "🔴", "category": "个人敏感PII", "mask_rule": "PARTIAL_MASK", "masked_display": "c.phone_masked", "mask_example": "138****8000"},
      {"field": "c.customer_name", "risk_level": "L2", "risk_label": "🟡", "category": "内部信息", "mask_rule": "FIRST_CHAR_KEEP", "masked_display": "c.customer_name_masked", "mask_example": "张*"}
    ],
    "safe_sql_text": "SELECT o.id, o.amount, o.create_time, o.status, c.customer_name_masked, c.phone_masked FROM orders o LEFT JOIN customers c ON o.customer_id = c.id WHERE o.create_time > '2024-01-01' AND o.status IN ('pending','processing') ORDER BY o.create_time DESC LIMIT 100",
    "ddl_approval_required": true,
    "compliance_check": {
      "select_star_risk": true,
      "pii_in_where": false,
      "ddl_without_approval": true,
      "raw_data_in_test": false,
      "report_contains_plaintext_pii": false
    }
  }
}
```

### 安全强制规则

**MUST DO**：
1. L3字段必须脱敏后才能出现在任何输出中
2. DDL建议必须附加⚠️需DBA审批标注
3. SELECT * 必须展开为显式字段列表
4. C5二次脱敏扫描通过后才允许输出
5. EXPLAIN验证步骤禁止用真实业务库执行

**MUST NOT**：
1. 禁止在safe_sql_text中保留真实客户数据
2. 禁止将L3字段降级处理
3. 禁止直接执行DDL语句
4. 禁止在日志中记录明文PII
5. 禁止跳过compliance_check任何检查项

### 异常处理

| 异常场景 | 处理方式 |
|----------|---------|
| C5二次脱敏扫描不通过 | **阻断Pipeline**，P5不执行 |
| PII识别规则未覆盖新字段 | 降级为L2标记unclassified，触发人工复核 |
| SELECT * 展开失败 | 标注⚠️不可控暴露，保留* |
| 脱敏复核超时 | **阻断Pipeline** |

---

## Phase 5: HTML巡检报告生成与告警推送

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P5 |
| Phase名称 | 报告生成与告警推送 |
| 调用组件 | `skill(name="report-generator")` + `skill(name="diagram-drawing")` |
| 输入来源 | 汇聚 P1-P4 全部输出 |

### 处理逻辑

#### 5.1 拓扑图渲染

从P3的`mermaid_code`渲染PNG。渲染失败→报告嵌入Mermaid源码块并标注`[拓扑图渲染降级]`。

#### 5.2 告警判定规则

| 条件 | 告警等级 | 推送通道 |
|------|----------|---------|
| 存在critical severity | 🔴 P0 紧急 | im + sms + email |
| high severity + 根因置信度 >= 0.7 | 🟠 P1 重要 | im + email |
| high/medium severity + 置信度 < 0.7 | 🟡 P2 提醒 | im |
| 仅low severity | 🔵 P3 通知 | report_only |

**铁律：告警消息中出现的SQL必须使用P4脱敏版本，禁止包含明文PII。**

#### 5.3 HTML报告8模块结构

| 模块 | 内容 | 数据来源 |
|------|------|---------|
| 模块1 | 执行摘要（关键发现，1页内） | P2+P3 |
| 模块2 | 诊断概览（脱敏SQL+问题总数+严重度分布） | P1+P2+P4 |
| 模块3 | 性能问题清单（表格：问题/严重度/表/列） | P2 |
| 模块4 | 根因图谱（拓扑图PNG+级联路径+置信度） | P3 |
| 模块5 | 敏感字段审查（字段/风险等级/脱敏规则） | P4 |
| 模块6 | 优化建议（按🔴🟡🟢优先级排列） | P2+P3 |
| 模块7 | 行动计划（紧急/短期/中期+负责人+预期效果） | P2+P3 |
| 模块8 | 阶段溯源（6个Phase执行状态✓/⚠️降级） | 全Phase |

#### 5.4 报告样式

- 深色主题（#1a1a2e + #e0e0e0）
- 表格斑马纹 | 代码块深灰背景
- 严重度色值：critical=#ff4757 / high=#ff6348 / medium=#ffa502 / low=#2ed573
- 响应式布局 + 打印切换浅色主题

### 输出JSON

```json
{
  "phase": "P5",
  "report_result": {
    "html_report_path": "/path/to/sql_diagnosis_report_SQL001_20260627.html",
    "diagram_files": [{"type": "topology", "path": "/path/to/topology_SQL001.png", "status": "rendered|fallback_mermaid"}],
    "alert": {
      "level": "P1",
      "title": "[SQL质量诊断] P1 orders表 发现全表扫描+索引缺失",
      "message": "orders表缺少联合索引idx(status,create_time)，根因置信度0.82(中高)。建议：创建联合索引（需DBA审批）。",
      "channel": ["im", "email"]
    }
  }
}
```

### 异常处理

| 异常场景 | 处理策略 |
|----------|---------|
| Mermaid渲染超时 | 降级输出源码，diagram_status=fallback_mermaid |
| P4脱敏输出缺失但P2检出security issue | 拦截报告生成，返回failed |
| P2诊断结果为空 | 正常生成报告，告警level=none |
| 告警推送通道不可用 | 降级至report_only |

---

## Phase 6: 诊断记录归档

### 基本信息

| 项目 | 值 |
|---|---|
| Phase编号 | P6 |
| Phase名称 | 诊断记录归档 |
| 调用组件 | `skill(name="archive-manager")` |
| 前置依赖 | P1-P5全部完成 |
| 超时阈值 | 30s |

### 处理逻辑

#### Step 1: 归档前脱敏复核

```
FOR each field IN P4.fields_processed:
    IF field.risk_level == "L3" AND field.desensitization_applied == false:
        REJECT_ARCHIVE("L3字段未脱敏: {field}, 归档终止")
IF P4.applied == false:
    REJECT_ARCHIVE("脱敏方案未执行, 归档终止")
IF P1标记L3字段但P4未处理:
    REJECT_ARCHIVE("L3字段脱敏遗漏")
VERIFY SQL指纹SHA256校验通过
```

#### Step 2: 标签生成

| 标签类型 | 示例 | 来源 |
|---------|------|------|
| 数据库 | `db:mysql` | P1输入 |
| 问题类型 | `issue:full_table_scan` | P2诊断 |
| 根因类型 | `root:index_missing` | P3推理 |
| 严重度 | `severity:P1` | P2诊断 |
| 敏感字段 | `pii:phone` | P4脱敏 |
| 日期 | `date:2026-06-27` | 系统 |

#### Step 3: 元数据补全

- 诊断ID：`SQD-{YYYYMMDD}-{SEQ}`（如SQD-20260627-001）
- SQL指纹：SHA256标准化哈希（替代SQL原文归档）
- 保留策略：P0/P1→180天，P2/P3→90天

#### Step 4: 归档写入

调用Archive-Manager写入，路径：`/archive/sql-diagnosis/{date}/{archive_id}.json`

### 输出JSON

```json
{
  "phase": "P6",
  "archive_result": {
    "archive_id": "SQD-20260627-001",
    "sql_fingerprint": "sha256:a1b2c3d4...",
    "tags": ["db:mysql", "issue:full_table_scan", "root:index_missing", "severity:P1", "pii:phone", "date:2026-06-27"],
    "desensitization_verified": true,
    "retention_days": 180,
    "archive_path": "/archive/sql-diagnosis/2026-06-27/SQD-20260627-001.json"
  }
}
```

### 异常处理

| 异常场景 | 处理方式 |
|----------|---------|
| L3字段明文 | 拒绝归档，emit CRITICAL告警 |
| 脱敏方案未执行 | 拒绝归档，回退P4重新执行 |
| SQL指纹篡改 | 拒绝归档，标记数据完整性风险 |
| Archive-Manager写入失败 | 暂存本地.temp/，30分钟内补归档 |
| P5报告路径无效 | 归档继续，标记report_missing:true |

---

## 全局安全规范

### Phase间数据流总览

```
                                    ┌──────────────┐
                                    │   用户输入    │
                                    │  SQL + 上下文 │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   P1: 解析    │
                                    │ Info-Extractor │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   P2: 诊断    │
                                    │   SQL大师     │
                                    └──────┬───────┘
                                           │
                              ┌────────────┴────────────┐
                              │          ∥ 并行          │
                              ▼                         ▼
                     ┌──────────────┐          ┌──────────────┐
                     │  P3: 根因推理 │          │  P4: 脱敏    │
                     │ Root-Cause-  │          │ Security-    │
                     │ Mapper       │          │ Guard        │
                     └──────┬───────┘          └──────┬───────┘
                              │                         │
                              └────────────┬────────────┘
                                           │ 汇聚P3+P4
                                           ▼
                                    ┌──────────────┐
                                    │  P5: 报告告警  │
                                    │ Report-Gen    │
                                    │ + diagram     │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  P6: 归档     │
                                    │ Archive-Mgr   │
                                    └──────────────┘
```

### MUST DO（6条）

| 编号 | 规范 | 适用Phase |
|---|---|---|
| MD-1 | DDL/DML修改类SQL禁止自动执行，必须经DBA审批 | P2, P5 |
| MD-2 | L3字段强制脱敏后方可流出P4 | P4 |
| MD-3 | 报告与告警中禁止包含明文PII | P5 |
| MD-4 | 归档前必须完成脱敏复核 | P6 |
| MD-5 | EXPLAIN验证步骤只读，禁止用真实业务库执行 | P2 |
| MD-6 | SQL指纹替代原文归档 | P6 |

### MUST NOT（6条）

| 编号 | 禁止行为 | 风险等级 |
|---|---|---|
| MN-1 | 禁止自动执行DDL/DML修复建议 | CRITICAL |
| MN-2 | 禁止L3字段明文跨Phase传递 | CRITICAL |
| MN-3 | 禁止报告中呈现未脱敏的敏感字段值 | HIGH |
| MN-4 | 禁止归档未通过脱敏复核的记录 | HIGH |
| MN-5 | 禁止在生产库执行EXPLAIN ANALYZE | HIGH |
| MN-6 | 禁止归档中存储SQL原文 | MEDIUM |

---

## 降级策略

| 编号 | 场景 | 降级处理 | 恢复条件 |
|---|---|---|---|
| DG-1 | SQL解析失败 | 跳过P2-P4，仅生成基础报告 | 用户提供修正SQL后重新触发 |
| DG-2 | EXPLAIN获取超时 | 降级为纯静态规则诊断，标注`explain_timeout` | 只读副本恢复或手动EXPLAIN |
| DG-3 | 根因推理置信度不足(<0.5) | 输出多条候选根因按置信度排序，标注`root_cause_uncertain` | 人工确认后补录根因 |
| DG-4 | 脱敏规则匹配失败 | 对未识别字段应用默认全掩码`***`，触发安全审查工单 | 安全团队确认后更新规则 |
| DG-5 | 归档存储不可用 | 暂存本地`.temp/sqd-pending/`，每5分钟重试，最长24小时 | 存储服务恢复后自动补归档 |
| DG-6 | P3∥P4并行中某一Phase失败 | 失败Phase降级输出，另一Phase正常完成，P5合并降级结果 | 重新触发失败Phase |
| DG-7 | P5报告生成失败 | 降级输出纯文本摘要，告警切换为直接消息通知 | 模板修复或路径恢复 |
| DG-8 | 全局Phase超时(>120s) | 强制终止，输出已完成Phase摘要+标注`global_timeout` | 优化瓶颈Phase或调大阈值 |

---

## 课堂演示脚本

### 开场话术

> "不是单点优化，而是全链路闭环——普通DBA看'这条SQL慢在哪'，高级诊断看'慢查询从哪来、根因是什么、数据安不安全、报告怎么出、谁该知道、记录怎么存'。6个Phase从采集到归档，缺一不可。"

### 演示7步

1. **投喂SQL** — 触发P1解析，展示敏感字段标注和风险标记
2. **诊断出问题** — P2匹配8种性能问题，索引建议标注⚠️需DBA审批
3. **并行分叉** — P3根因推理 ∥ P4脱敏同时启动，省时约40%
4. **脱敏展示** — P4输出脱敏方案（phone→138****8000 / id_card→[REDACTED]）
5. **合并报告** — P5生成HTML报告+告警，报告中引用脱敏版SQL
6. **归档闸门** — 故意制造脱敏遗漏，P6复核拦截：`L3字段脱敏遗漏: t_user.id_card, 归档终止`
7. **正常归档** — 恢复完整脱敏后正常归档，展示archive_id和SQL指纹

### 技术爆点

> "6个Phase是6个独立Agent——采集、诊断、推理、脱敏、报告、归档各司其职，不是一个人演6个角色，而是6个专家各干各的。P3和P4可以并行——根因推理和脱敏检查同时进行。P6的脱敏复核是整个安全链的最后一道闸门——P4漏了，P6得拦住。"

### 互动提问

| 问题 | 答案要点 |
|---|---|
| 为什么P3和P4可以并行，但P5不行？ | P3和P4仅依赖P2输出，互不依赖；P5需P3根因+P4脱敏合并 |
| 如果P4脱敏规则库没有覆盖某种L3字段模式？ | DG-4降级：默认全掩码，触发安全审查工单 |
| P6脱敏复核和P4脱敏执行有什么区别？ | P4是运动员（执行脱敏），P6是裁判员（验证脱敏完整性） |
| 为什么要用SHA256指纹替代SQL原文归档？ | SQL原文可能含WHERE中的业务参数（手机号等），存原文扩大暴露面 |

### 变体场景

| 变体 | SQL特征 | 预期P2诊断 | P4脱敏重点 |
|---|---|---|---|
| 多表JOIN笛卡尔积 | 3表JOIN无ON条件 | cartesian_product (P0) | 3表敏感字段交叉暴露 |
| 隐式类型转换 | WHERE varchar_col = 123 | implicit_cast (P2) | 无L3字段时常规处理 |
| N+1查询 | 循环中逐条SELECT | n_plus_one (P1) | 循环SQL中参数值脱敏 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0.0 | 2026-06-27 | 初始版本：6-Phase完整Pipeline，通过Phase-Orchestrator由6个独立sub-Agent并行/串行执行 |

---

> 本Skill基于2026-06-27实际SQL诊断session的经验提炼，根因图谱来自3层推理结果，脱敏规则来自安全审查发现的phone字段暴露风险。P3∥P4并行设计为Pipeline唯一并行点，P4脱敏复核失败阻断Pipeline为安全红线。

> AI生成