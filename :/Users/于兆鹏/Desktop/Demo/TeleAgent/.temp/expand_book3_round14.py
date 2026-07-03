# -*- coding: utf-8 -*-
"""Book3 Round 14 - final push to cross 100K."""
import re

path = 'book-cluster/manuscript.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

insertions = [
    # 1. Ch1 - after AI困境 intro
    {
        "anchor": "金融AI从",
        "text": "概念热",
        "text_replacement": None
    },
    # 2. Ch2.4 - after three cluster modes
    {
        "anchor": "集群架构的三种模式",
        "text": "\n\n三种模式的选择不是非此即彼的。在实际部署中，龙马集群同时使用了三种模式：核心风控场景使用主从模式确保一致性，营销推荐场景使用对等模式追求高吞吐，夜间批处理场景使用管道模式串联多步骤任务。混合模式的关键是Hermes的任务路由逻辑能够识别任务的特征并自动选择合适的执行模式。任务提交时携带模式提示字段，Hermes根据提示和当前集群负载状态决定最终执行模式。如果提示的模式当前不可用（如对等模式的某些节点离线），Hermes会自动降级到可用模式并记录降级日志。这种弹性模式选择机制使集群能够在不同业务场景下自动切换到最优执行策略。\n\n"
    },
    # 3. Ch4.7 - after collaboration graph
    {
        "anchor": "高频协作的节点之间建立直连通道",
        "text": "。直连通道的建立基于历史协作频率分析。Hermes统计每对节点之间的任务交接次数，超过日均50次的节点对建立直连通道。当前龙马集群中有4对直连通道：Hermes-KimiClaw、Hermes-ArkClaw、KimiClaw-ArkClaw、ArkClaw-MyOpenClaw。这4对覆盖了80%以上的协作流量。其余20%的低频协作走Hermes中转，虽然多一跳但绝对延迟增加不到10毫秒，对业务无感。直连通道的维护成本不高：通道建立后自动保持，只在节点重启时重建。重建时间约200毫秒，期间的任务自动走中转通道，不会丢失。\n\n"
    },
    # 4. Ch15.2 - after evaluation metrics
    {
        "anchor": "节点级评估关注单个节点的能力边界和稳定性",
        "text": "。节点级评估有一个重要的配套机制：能力档案。每个节点维护一份能力档案，记录其在各项评估指标上的历史趋势。能力档案的用途是发现能力的渐进退化——如果某个节点的任务完成率从99%缓慢下降到95%再到91%，虽然每次下降都在可接受范围内，但趋势线清楚地显示了退化信号。没有能力档案的话，这种缓慢退化很难被察觉，直到某天降到不可接受的阈值才触发告警。能力档案每月更新一次，趋势分析使用最近12个月的数据。当退化趋势的斜率超过阈值时，系统自动通知节点维护者进行排查。\n\n"
    },
]

# Remove entries with text_replacement = None
insertions = [ins for ins in insertions if ins.get("text")]

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
print(f"Book3 Round14: {cc} Chinese chars")
print(f"Added: {cc - 98962} chars this round")
print(f"Total added: {cc - 46191} chars")
print(f"Need: {100000 - cc} more")
