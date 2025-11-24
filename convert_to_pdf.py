"""
Convert IBM Metrics Briefing markdown to PDF using reportlab
"""
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown to PDF"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_LEFT
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=20
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=15
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=6,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        backgroundColor=colors.HexColor('#f4f4f4'),
        leftIndent=10,
        rightIndent=10
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        bulletIndent=10
    )

    # Build story
    story = []

    # Split content into lines
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Title (first H1)
        if line.startswith('# ') and i < 5:
            story.append(Paragraph(line[2:], title_style))
            story.append(Spacer(1, 0.2*inch))

        # H1
        elif line.startswith('# '):
            story.append(PageBreak())
            story.append(Paragraph(line[2:], h1_style))
            story.append(Spacer(1, 0.1*inch))

        # H2
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], h2_style))
            story.append(Spacer(1, 0.08*inch))

        # H3
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h3_style))
            story.append(Spacer(1, 0.06*inch))

        # Bold metadata
        elif line.startswith('**') and '**:' in line:
            story.append(Paragraph(line.replace('**', '<b>').replace('**', '</b>'), body_style))
            story.append(Spacer(1, 0.05*inch))

        # Table
        elif line.startswith('|'):
            # Collect table lines
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            i -= 1  # Back up one

            # Parse table
            if len(table_lines) >= 2:
                # Parse header
                header = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]

                # Skip separator line (index 1)
                # Parse rows
                data = [header]
                for row_line in table_lines[2:]:
                    row = [cell.strip() for cell in row_line.split('|')[1:-1]]
                    data.append(row)

                # Create table
                if data:
                    # Calculate column widths
                    num_cols = len(data[0])
                    col_width = (7.0 * inch) / num_cols
                    col_widths = [col_width] * num_cols

                    table = Table(data, colWidths=col_widths, repeatRows=1)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('TOPPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 0.15*inch))

        # Code blocks
        elif line.startswith('```'):
            # Collect code block
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1

            if code_lines:
                code_text = '\n'.join(code_lines)
                # Escape special characters
                code_text = code_text.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f'<font name="Courier" size="8">{code_text}</font>', code_style))
                story.append(Spacer(1, 0.1*inch))

        # Bullet lists
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:]
            # Convert markdown formatting
            bullet_text = bullet_text.replace('**', '<b>').replace('**', '</b>')
            bullet_text = bullet_text.replace('`', '<font name="Courier">')
            bullet_text = bullet_text.replace('`', '</font>')
            story.append(Paragraph(f'• {bullet_text}', bullet_style))
            story.append(Spacer(1, 0.03*inch))

        # Numbered lists
        elif re.match(r'^\d+\.', line):
            list_text = re.sub(r'^\d+\.\s*', '', line)
            list_text = list_text.replace('**', '<b>').replace('**', '</b>')
            list_text = list_text.replace('`', '<font name="Courier">')
            list_text = list_text.replace('`', '</font>')
            story.append(Paragraph(list_text, bullet_style))
            story.append(Spacer(1, 0.03*inch))

        # Horizontal rule
        elif line.startswith('---'):
            story.append(Spacer(1, 0.1*inch))

        # Regular paragraph
        else:
            # Convert markdown formatting
            para_text = line.replace('**', '<b>').replace('**', '</b>')
            para_text = para_text.replace('`', '<font name="Courier" size="9">')
            para_text = para_text.replace('`', '</font>')
            story.append(Paragraph(para_text, body_style))
            story.append(Spacer(1, 0.08*inch))

        i += 1

    # Build PDF
    doc.build(story)
    print(f"✅ PDF created: {pdf_file}")

if __name__ == '__main__':
    md_file = Path(r'C:\Users\MelvinJones\work\event-governance\poc\IBM-METRICS-BRIEFING.md')
    pdf_file = md_file.with_suffix('.pdf')

    markdown_to_pdf(md_file, pdf_file)
