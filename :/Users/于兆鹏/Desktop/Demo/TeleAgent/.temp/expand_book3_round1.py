# -*- coding: utf-8 -*-
"""Book3 Round 1 Expansion - using JSON to avoid quote issues"""
import re
import json

ms_path = r"C:\Users\于兆鹏\Desktop\Demo\TeleAgent\.temp\book-cluster\manuscript.md"
json_path = r"C:\Users\于兆鹏\Desktop\Demo\TeleAgent\.temp\book3_round1_insertions.json"

with open(ms_path, "r", encoding="utf-8") as f:
    content = f.read()

with open(json_path, "r", encoding="utf-8") as f:
    insertions = json.load(f)

for item in insertions:
    anchor = item["anchor"]
    new_text = item["text"]
    if anchor in content:
        content = content.replace(anchor, new_text, 1)
        print(f"OK: {anchor[:40]}...")
    else:
        print(f"MISS: {anchor[:40]}...")

with open(ms_path, "w", encoding="utf-8") as f:
    f.write(content)

cc = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"\nBook3 Round1: {cc:,} Chinese chars")
print(f"Added: {cc - 46191:,} chars")
print(f"Need: {max(0, 100000 - cc):,} more")
