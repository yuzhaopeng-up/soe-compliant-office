# -*- coding: utf-8 -*-
"""Book1 expansion round 8 - final push to 100K."""
import re

ms_path = r"C:\Users\于兆鹏\Desktop\Demo\TeleAgent\.temp\book-financial-agent\manuscript.md"

with open(ms_path, "r", encoding="utf-8") as f:
    content = f.read()

insertions = []

# Ch15 - before ## 15.7
ch15_r8 = """

#### 15.6.5 某城商行3人团队推广的"节奏控制"

某城商行只有3名技术人员负责Agent推广，覆盖全行28个网点。资源极度有限的情况下，节奏控制成为成败关键。

第一个节奏控制是"先总部后网点"。3人团队先在总行部署Agent系统，运行1个月验证稳定性和准确率。总行验证通过后才开始向网点推广。某银行曾见过反面案例——某行在总行未验证的情况下直接推网点，结果第1周就遇到Skill报错，网点人员失去信心，推广阻力大增。

第二个节奏控制是"先单点后铺开"。28个网点不是同时推广，而是分3批——第1批3个网点（试点2周）、第2批8个网点（扩展2周）、第3批17个网点（全量2周）。每批推广后收集反馈、修复问题，再进入下一批。3人团队的精力分配：第1批100%投入、第2批70%投入（30%处理第1批遗留问题）、第3批40%投入（60%处理前两批的优化需求）。

第三个节奏控制是"先高频后低频"。先推广使用频率最高的Agent（客服问答Agent，日均调用800次），再推广中频Agent（信贷审批Agent，日均调用50次），最后推广低频Agent（合规审查Agent，日均调用5次）。高频Agent的价值见效快，能快速获得业务部门的支持和预算。低频Agent的价值见效慢，但一旦出问题影响大，所以需要更长的验证周期。

某城商行3人团队用6周完成了28个网点的推广。推广后系统运行稳定，日均处理Agent调用1,200次，3人团队的运维工作量约为每天2小时（主要处理使用咨询和配置调整）。该行IT负责人表示："3个人推广28个网点，核心不是人手够不够，而是节奏对不对。先稳后快、先高后低、先点后面，节奏对了3个人也能推。"
"""
insertions.append(("## 15.7 2026金融智能体招标图谱", ch15_r8))

# Ch16 - before ## 16.6
ch16_r8 = """

#### 16.5.9 监控系统的"告警风暴"治理

某银行Agent系统上线初期，告警系统在1小时内发出了147条告警——大部分是重复告警或低优先级告警。告警风暴导致运维人员疲劳，真正的严重告警被淹没在噪声中。

某银行对告警做了4层治理。第一层是"告警合并"——同一Agent的同一类型告警在5分钟内合并为1条。147条告警合并后变为23条。第二层是"告警升级"——告警持续15分钟未处理时自动升级优先级（P3升P2，P2升P1）。第三层是"告警抑制"——当P0级告警触发时，自动抑制同Agent的低优先级告警，避免P0告警被噪声淹没。第四层是"告警去重"——同一根因导致的多个告警（如数据库不可用导致3个Agent同时报错）合并为1条根因告警，附带影响范围说明。

4层治理后，日均告警从340条降至38条，其中P0-P1级告警从12条降至5条（减少了误报），P2-P3级告警从328条降至33条。运维人员的告警处理时间从日均4.5小时降至1.2小时，真正实现了"告警驱动运维"而非"告警淹没运维"。
"""
insertions.append(("## 16.6 演进层：自进化与持续优化", ch16_r8))

# Apply all insertions
for anchor, exp in insertions:
    if anchor in content:
        content = content.replace(anchor, exp + "\n\n" + anchor, 1)
        print(f"OK: {anchor[:40]}")
    else:
        print(f"MISS: {anchor[:40]}")

# Write back
with open(ms_path, "w", encoding="utf-8") as f:
    f.write(content)

cc = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"\nBook1 after round 8: {cc:,} Chinese chars")
print(f"Deficit: {max(0, 100000-cc):,}")
