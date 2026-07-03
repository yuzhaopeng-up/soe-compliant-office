from pptx import Presentation
from pptx.util import Pt, Emu
from lxml import etree

path = r'D:\Training\1.培训\课程\数字化\培训\260422-23_浙江农商银行_支行长AI落地实战\1.PPT\浙江农商银行系统支行行长AI决策沙盘实战培训.pptx'
prs = Presentation(path)
slides = list(prs.slides)

# Detailed analysis of key layout types' placeholders
# Focus on: 封面页, 目录页, 章节页, key 正文页 layouts, 结束页
key_layout_names = [
    '封面页_1_5', '目录页-1-5_6', '章节页_1_4', '结束页_1_5',
    '正文页-3_19', '正文页-6_69', '正文页-34_20', '正文页-35_20',
    '正文页-27_35', '正文页-26_18',
    '上左标下左内后右背景-有背景-有间隙-3',
    '仅标题', '标题和内容', '空白'
]

for layout in prs.slide_layouts:
    if layout.name in key_layout_names:
        print('\n=== Layout: %s ===' % layout.name)
        for ph in layout.placeholders:
            idx = ph.placeholder_format.idx
            name = ph.name
            ptype = ph.placeholder_format.type
            # Convert EMU to inches for readability
            x_in = ph.left / 914400
            y_in = ph.top / 914400
            w_in = ph.width / 914400
            h_in = ph.height / 914400
            print('  PH[%d] %s type=%s pos=(%.2f,%.2f) size=(%.2f,%.2f)' % (
                idx, name, ptype, x_in, y_in, w_in, h_in))

# Also check what text is in key slides to understand layout usage
print('\n\n=== EXAMPLE SLIDES PER LAYOUT ===')
layout_examples = {}
for i, slide in enumerate(slides):
    ln = slide.slide_layout.name
    if ln not in layout_examples and ln in key_layout_names:
        layout_examples[ln] = i + 1
        
for ln, slide_num in sorted(layout_examples.items(), key=lambda x: x[1]):
    print('\n%s -> Slide %d' % (ln, slide_num))
