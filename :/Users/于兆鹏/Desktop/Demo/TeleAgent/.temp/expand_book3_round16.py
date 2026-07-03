# -*- coding: utf-8 -*-
"""Book3 Round 16 - last 200 chars."""
import re

path = 'book-cluster/manuscript.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

insertions = [
    {
        "anchor": "安全左移和成本前置",
        "text": "。安全左移意味着在设计阶段就把安全需求纳入架构，而不是开发完成后打补丁。成本前置意味着在任务提交时就开始做预算分配和模型路由，而不是执行完才统计成本。两者共同构成了金融智能体集群与其他行业智能体集群的根本差异：金融集群的安全和成本不是附加约束而是设计基线"
    },
]

count = 0
for ins in insertions:
    anchor = ins["anchor"]
    new_text = ins["text"]
    if anchor in text:
        text = text.replace(anchor, anchor + new_text, 1)
        count += 1
        print(f"OK: {anchor[:30]}...")
    else:
        print(f"MISS: {anchor[:30]}...")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

cc = len(re.findall(r'[\u4e00-\u9fff]', text))
print(f"\nApplied: {count} insertions")
print(f"Book3 Round16: {cc} Chinese chars")
print(f"PASS!" if cc >= 100000 else f"Need {100000 - cc} more")
