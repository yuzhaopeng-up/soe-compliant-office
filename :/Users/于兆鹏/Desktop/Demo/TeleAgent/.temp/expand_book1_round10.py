# -*- coding: utf-8 -*-
"""Book1 expansion round 10 - final 200 chars."""
import re

ms_path = r"C:\Users\于兆鹏\Desktop\Demo\TeleAgent\.temp\book-financial-agent\manuscript.md"

with open(ms_path, "r", encoding="utf-8") as f:
    content = f.read()

exp = """

某银行培训负责人最后补充道："能力进化路线图不是固定不变的。随着Agent技术本身在快速迭代——从单Agent到多Agent协作、从规则驱动到自治进化——从业者需要持续学习。我们要求所有Agent相关岗位每年完成不少于40小时的继续教育，内容涵盖最新的技术趋势、监管动态和行业案例。不完成继续教育的人员，其Agent系统操作权限将被暂停。"
"""

anchor = "## 17.7 本章小结"
if anchor in content:
    content = content.replace(anchor, exp + "\n\n" + anchor, 1)
    print("OK: inserted")
else:
    print("MISS")

with open(ms_path, "w", encoding="utf-8") as f:
    f.write(content)

cc = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"\nBook1 FINAL: {cc:,} Chinese chars")
print(f"Status: {'PASS' if cc >= 100000 else f'STILL SHORT by {100000-cc}'}")
