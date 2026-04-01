import { jsPDF } from "jspdf";
import { 
  Document, Packer, Paragraph, TextRun, HeadingLevel, 
  AlignmentType 
} from "docx";
import { saveAs } from "file-saver";

export const parseMarkdownToParts = (text) => {
  if (!text) return [];
  // Pre-clean: Remove bold/italic markers to make plain text output cleaner
  const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1');
  const lines = cleanText.split('\n');
  const parts = [];
  
  lines.forEach(line => {
    const trimmed = line.trim();
    if (!trimmed) {
      parts.push({ type: 'empty' });
      return;
    }
    
    if (trimmed.startsWith('###')) {
      parts.push({ type: 'h3', text: trimmed.replace(/^###\s*/, '') });
    } else if (trimmed.startsWith('##')) {
      parts.push({ type: 'h2', text: trimmed.replace(/^##\s*/, '') });
    } else if (trimmed.startsWith('#')) {
      parts.push({ type: 'h1', text: trimmed.replace(/^#\s*/, '') });
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      parts.push({ type: 'list', text: trimmed.replace(/^[-*]\s*/, '') });
    } else {
      parts.push({ type: 'p', text: trimmed });
    }
  });
  return parts;
};

export const handleExportPDF = async (text, query, onComplete) => {
  try {
    const doc = new jsPDF({ orientation: "p", unit: "mm", format: "a4" });
    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);
    let pageNum = 1;
    let y = 25;

    const addHeaderFooter = () => {
      // Header
      doc.setFont("helvetica", "italic");
      doc.setFontSize(9);
      doc.setTextColor(150, 150, 150);
      doc.text("EnergyMind AI - Research Division", margin, 12);
      doc.text(new Date().toLocaleDateString(), pageWidth - margin - 20, 12);
      doc.line(margin, 15, pageWidth - margin, 15);
      
      // Footer
      doc.line(margin, pageHeight - 15, pageWidth - margin, pageHeight - 15);
      doc.text(`Page ${pageNum}`, pageWidth / 2 - 5, pageHeight - 10);
    };

    const checkPageBreak = (needed) => {
      if (y + needed > pageHeight - 25) {
        doc.addPage();
        pageNum++;
        y = 25;
        addHeaderFooter();
        return true;
      }
      return false;
    };

    addHeaderFooter();

    // Title Block
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.setTextColor(79, 70, 229); // Brand Indigo
    doc.text("Research Report", margin, y);
    y += 12;

    doc.setFontSize(14);
    doc.setTextColor(100, 116, 139);
    const queryLines = doc.splitTextToSize(`Subject: ${query}`, contentWidth);
    doc.text(queryLines, margin, y);
    y += (queryLines.length * 7) + 5;
    
    doc.setDrawColor(79, 70, 229);
    doc.setLineWidth(0.5);
    doc.line(margin, y, margin + 40, y);
    y += 10;

    const parts = parseMarkdownToParts(text);
    
    parts.forEach(part => {
      if (part.type === 'empty') {
        y += 3;
        return;
      }

      if (part.type.startsWith('h')) {
        const size = part.type === 'h1' ? 17 : (part.type === 'h2' ? 14 : 12);
        checkPageBreak(size + 10);
        y += 4; // Extra space before heading
        
        doc.setFont("helvetica", "bold");
        doc.setFontSize(size);
        doc.setTextColor(79, 70, 229);
        
        const lines = doc.splitTextToSize(part.text, contentWidth);
        doc.text(lines, margin, y);
        y += (lines.length * (size * 0.4)) + 6;
      } 
      else if (part.type === 'list') {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(11);
        doc.setTextColor(40, 40, 40);
        
        const lines = doc.splitTextToSize(`• ${part.text}`, contentWidth - 8);
        if (checkPageBreak(lines.length * 6)) y += 5;
        doc.text(lines, margin + 8, y);
        y += (lines.length * 6) + 1;
      }
      else {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(11);
        doc.setTextColor(50, 50, 50);
        
        const lines = doc.splitTextToSize(part.text, contentWidth);
        if (checkPageBreak(lines.length * 6)) y += 5;
        doc.text(lines, margin, y, { align: 'justify', maxWidth: contentWidth });
        y += (lines.length * 6) + 3;
      }
    });

    doc.save(`EnergyMind_Report_${Date.now()}.pdf`);
    if (onComplete) onComplete();
  } catch (err) {
    console.error("PDF Export failed:", err);
  }
};

export const handleExportDocs = async (text, query, onComplete) => {
  try {
    const parts = parseMarkdownToParts(text);
    const children = [
      new Paragraph({
        children: [
          new TextRun({ text: "EnergyMind AI Research Report", bold: true, size: 48, color: "4f46e5" }),
        ],
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 400 },
      }),
      new Paragraph({
        children: [
          new TextRun({ text: `Subject: ${query}`, bold: true, size: 28, color: "64748b" }),
        ],
        alignment: AlignmentType.CENTER,
        spacing: { after: 800 },
      }),
    ];

    parts.forEach(part => {
      if (part.type === 'empty') return;

      if (part.type.startsWith('h')) {
        children.push(new Paragraph({
          text: part.text,
          heading: part.type === 'h1' ? HeadingLevel.HEADING_1 : (part.type === 'h2' ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3),
          spacing: { before: 400, after: 200 }
        }));
      } else if (part.type === 'list') {
        children.push(new Paragraph({
          text: part.text,
          bullet: { level: 0 },
          spacing: { after: 120 }
        }));
      } else {
        children.push(new Paragraph({
          children: [new TextRun({ text: part.text, size: 24 })],
          alignment: AlignmentType.JUSTIFY,
          spacing: { line: 360, after: 200 }
        }));
      }
    });

    const doc = new Document({
      sections: [{ 
        properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
        children 
      }],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, `EnergyMind_Report_${Date.now()}.docx`);
    if (onComplete) onComplete();
  } catch (err) {
    console.error("DOCS Export failed:", err);
  }
};
