const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
        HeadingLevel, Header, Footer, PageNumber } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: border, bottom: border, left: border, right: border };
const headerShading = { fill: "1F4E79", type: ShadingType.CLEAR };
const altShading = { fill: "F2F7FB", type: ShadingType.CLEAR };
const noShading = { fill: "FFFFFF", type: ShadingType.CLEAR };

function headerCell(text, width) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: headerShading, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20, font: "Microsoft YaHei" })] })]
  });
}

function dataCell(text, width, shading) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: shading || noShading, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ children: [new TextRun({ text, size: 20, font: "Microsoft YaHei" })] })]
  });
}

function labelCell(text, width, shading) {
  return new TableCell({
    borders: cellBorders, width: { size: width, type: WidthType.DXA },
    shading: shading || noShading, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, size: 20, font: "Microsoft YaHei" })] })]
  });
}

const col1 = 2400, col2 = 6960;
const rows = [
  ["归档编号", "ARCH-20260627-0001"],
  ["归档类型", "ticket（巡检记录）"],
  ["归档目标", "巡检案例库"],
  ["负责人", "张工"],
  ["同行人员", "李明、王芳"],
  ["巡检地点", "某区九龙湖基站"],
  ["巡检日期", "2026-06-26"],
  ["发现问题", "空调外机异响"],
  ["处理措施", "已拍照记录"],
  ["预计处理时长", "2小时"],
  ["处理状态", "处理中"],
  ["标签", "基站巡检 | 空调故障 | 某区 | 异响"],
  ["隐私等级", "department_only"],
  ["保留策略", "1y"],
];

const tableRows = [
  new TableRow({ tableHeader: true, children: [headerCell("字段", col1), headerCell("内容", col2)] }),
  ...rows.map((r, i) => new TableRow({
    children: [labelCell(r[0], col1, i % 2 === 0 ? altShading : noShading), dataCell(r[1], col2, i % 2 === 0 ? altShading : noShading)]
  }))
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "1F4E79", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 240, after: 120 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: "2E75B6", font: "Microsoft YaHei" },
        paragraph: { spacing: { before: 180, after: 100 } } }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "巡检案例库 | 归档记录", size: 18, color: "888888", font: "Microsoft YaHei" })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "第 ", size: 18, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888" }), new TextRun({ text: " 页", size: 18, color: "888888" })]
      })] })
    },
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("巡检归档记录")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "文件名：", bold: true, size: 22 }), new TextRun({ text: "20260627_张工_李明王芳_某区基站", size: 22 })
      ] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "归档时间：", bold: true, size: 22 }), new TextRun({ text: "2026-06-26", size: 22 })
      ] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("脱敏信息")] }),
      new Paragraph({ spacing: { after: 100 }, children: [
        new TextRun({ text: "已脱敏字段：", bold: true, size: 22 }),
        new TextRun({ text: "\"红谷滩区\" → \"某区\"（区级脱敏）", size: 22, color: "C00000" })
      ] }),
      new Table({ columnWidths: [col1, col2], rows: tableRows }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 300 }, children: [new TextRun("原始消息（脱敏后）")] }),
      new Paragraph({ spacing: { after: 200 }, shading: { fill: "FFF2CC", type: ShadingType.CLEAR },
        children: [new TextRun({ text: "@张工 早上好！今天去某区九龙湖基站巡检，同行人员：李明、王芳，发现空调外机异响，已拍照记录，预计2小时处理完毕。", size: 20, italics: true })] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("人工确认记录")] }),
      new Paragraph({ numbering: { reference: "confirm-list", level: 0 },
        children: [new TextRun({ text: "空调外机异响是否升级为故障工单 → 用户确认：不升级，按巡检记录归档", size: 22 })] }),
      new Paragraph({ numbering: { reference: "confirm-list", level: 0 },
        children: [new TextRun({ text: "归档文件名确认 → 20260627_张工_李明王芳_某区基站", size: 22 })] }),
      new Paragraph({ numbering: { reference: "confirm-list", level: 0 },
        children: [new TextRun({ text: "脱敏范围确认 → 仅\"红谷滩区\"做区级脱敏，\"九龙湖\"为地标保留", size: 22 })] }),
    ]
  }],
  numbering: {
    config: [{
      reference: "confirm-list",
      levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  }
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\于兆鹏\\Desktop\\Demo\\TeleAgent\\巡检案例库\\20260627_张工_李明王芳_某区基站.docx", buffer);
  console.log("归档文件已生成");
});
