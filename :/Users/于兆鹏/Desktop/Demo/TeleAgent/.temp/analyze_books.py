# -*- coding: utf-8 -*-
import re, os, glob

book_dirs = [d for d in os.listdir('.') if d.startswith('book-') and os.path.isdir(d)]
book_dirs.sort()

print(f"{'目录名':<28} | {'汉字数':>8} | {'达标':>4} | {'DOCX':>6} | DOCX文件名")
print("-" * 100)

results = []
for bd in book_dirs:
    md_path = os.path.join(bd, 'manuscript.md')
    has_md = os.path.exists(md_path)
    cc = 0
    if has_md:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        cc = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    docx_files = glob.glob(os.path.join(bd, '*.docx'))
    has_docx = len(docx_files) > 0
    docx_name = os.path.basename(docx_files[0]) if docx_files else '-'
    docx_size = ''
    if docx_files:
        fsize = os.path.getsize(docx_files[0]) / 1024
        docx_size = f'({fsize:.0f}KB)'
    
    cc_str = str(cc) if has_md else 'N/A'
    pass_str = 'Y' if cc >= 100000 else 'N'
    docx_str = 'Y' if has_docx else 'N'
    
    print(f"{bd:<28} | {cc_str:>8} | {pass_str:>4} | {docx_str:>6} | {docx_name} {docx_size}")
    results.append((bd, cc, cc >= 100000, has_docx))

print()
print("=" * 100)
total = len(results)
passed = sum(1 for r in results if r[2])
has_docx = sum(1 for r in results if r[3])
print(f"总计: {total} 个书籍目录, {passed} 本达标(>=10万汉字), {has_docx} 本有DOCX")
