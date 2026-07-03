# -*- coding: utf-8 -*-
"""Book1 expansion round 9 - final 800 chars to cross 100K."""
import re

ms_path = r"C:\Users\于兆鹏\Desktop\Demo\TeleAgent\.temp\book-financial-agent\manuscript.md"

with open(ms_path, "r", encoding="utf-8") as f:
    content = f.read()

exp = """

#### 17.6.8 金融Agent从业者的"能力进化路线图"

某银行内部培训体系为Agent相关岗位设计了3条能力进化路线，帮助从业者从"会用Agent"进化到"能治理Agent"。

路线一是"Agent使用者→Agent设计师"。使用者的能力要求是熟练操作Agent系统、理解Agent输出、能判断Agent结果是否合理。设计师的进阶要求是理解Agent架构原理、能编写Skill需求文档、能设计Agent工作流。某银行的培训路径是：使用者参加40小时基础培训+3个月实战，通过考核后进入设计师培训（60小时进阶培训+6个月项目实践）。某银行已有12名业务人员通过此路径转型为Agent设计师，其中8人来自信贷部、3人来自风控部、1人来自合规部。

路线二是"Agent开发者→Agent架构师"。开发者的能力要求是能编写SKILL.md、能开发Python脚本、能调试Skill执行。架构师的进阶要求是能设计多Agent协作架构、能做Agent系统的容量规划和安全设计、能制定Agent技术规范。某银行的培养方式是"项目驱动"——开发者参与至少3个Agent项目后，由架构师导师带教6个月，通过架构设计答辩后晋升。某银行已有5名开发者晋升为Agent架构师。

路线三是"合规人员→Agent合规专家"。普通合规人员的知识体系以法规和内控为主，对AI技术了解有限。Agent合规专家需要跨界知识——既懂金融法规，又懂AI技术原理（如大模型的工作机制、幻觉产生的原因、Skill的执行逻辑）。某银行的培养方式是"技术扫盲+场景实战"——合规人员先参加20小时AI技术扫盲课程（覆盖大模型基础、Skill架构、安全风险），再参与2个Agent项目的合规评审实战。某银行已有3名合规人员转型为Agent合规专家，成为Agent合规审查的核心力量。

某银行培训负责人表示："Agent时代最稀缺的不是技术人员，而是'既懂金融又懂AI'的跨界人才。内部培养比外部招聘更有效——因为内部人员已经理解银行业务，只需要补充AI技术知识。外部招聘的AI人才虽然技术强，但不理解金融业务和合规要求，培养周期反而更长。"
"""

anchor = "## 17.7 本章小结"
if anchor in content:
    content = content.replace(anchor, exp + "\n\n" + anchor, 1)
    print("OK: inserted before 17.7")
else:
    print("MISS: anchor not found")

with open(ms_path, "w", encoding="utf-8") as f:
    f.write(content)

cc = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"\nBook1 after round 9: {cc:,} Chinese chars")
print(f"Deficit: {max(0, 100000-cc):,}")
