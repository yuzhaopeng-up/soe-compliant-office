from pptx import Presentation
from lxml import etree

path = r'D:\Training\1.培训\课程\数字化\培训\260422-23_浙江农商银行_支行长AI落地实战\1.PPT\浙江农商银行系统支行行长AI决策沙盘实战培训.pptx'
prs = Presentation(path)
slides = list(prs.slides)

# Analyze custom layouts: 封面页, 目录页, 章节页, 正文页 types, 结束页
# Find slides using these layouts and extract their placeholder structures
layouts_to_check = [
    '封面页_1_5', '目录页-1-5_6', '章节页_1_4', '结束页_1_5',
    '正文页-3_19', '正文页-6_69', '正文页-34_20', '正文页-35_20',
    '正文页-27_35', '正文页-26_18', '正文页-27_20',
    '上左标下左内后右背景-有背景-有间隙-3'
]

nsmap = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
         'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
         'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

# Analyze the slide layout XML for key custom layouts
import zipfile
with zipfile.ZipFile(path, 'r') as z:
    layout_files = sorted([f for f in z.namelist() if 'slideLayout' in f and f.endswith('.xml')])
    
    for lf in layout_files:
        root = etree.fromstring(z.read(lf))
        # Get layout name
        cSld = root.find('.//p:cSld', nsmap)
        if cSld is None:
            continue
        
        # Find the layout name from the XML
        name_elem = root.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}cNvPr')
        
        # Check all placeholders
        ph_elems = root.findall('.//p:sp/p:nvSpPr/p:nvPr/p:ph', nsmap)
        if not ph_elems:
            continue
        
        # Check if this layout has a recognizable name
        # Read the relationship to find layout name from slideMaster
        pass

# Simpler approach: just look at the slides themselves
for i, slide in enumerate(slides):
    layout_name = slide.slide_layout.name
    if layout_name in layouts_to_check:
        print('\n=== Slide %d [%s] ===' % (i+1, layout_name))
        # Get all placeholder texts
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame'):
                for para in shape.text_frame.paragraphs:
                    text = para.text.strip()
                    if text:
                        # Get font info
                        for run in para.runs:
                            sz = run.font.size
                            sz_pt = sz / 12700 if sz else 'inherit'
                            bold = run.font.bold
                            fname = run.font.name
                            print('  [%s] %s (font=%s, sz=%s, bold=%s)' % (
                                shape.name, text[:80], fname, sz_pt, bold))
                            break  # Just first run for reference
