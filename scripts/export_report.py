#!/usr/bin/env python3
"""Export canonical report; requires reportlab. Run from any working directory."""
from pathlib import Path
import html, re
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/phase2-report.md'
TARGET = ROOT / 'docs/phase2-report.pdf'
BASE = 'https://github.com/Shreyaa6/dracarys-cn-project/blob/main/'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportBody', fontName='Helvetica', fontSize=10.2, leading=14.5, spaceAfter=8, textColor=colors.HexColor('#233448')))
styles.add(ParagraphStyle(name='ReportTitle', fontName='Helvetica-Bold', fontSize=25, leading=30, spaceAfter=18, textColor=colors.HexColor('#123e59')))
styles.add(ParagraphStyle(name='ReportHeading', fontName='Helvetica-Bold', fontSize=15, leading=20, spaceBefore=17, spaceAfter=10, keepWithNext=True, textColor=colors.HexColor('#126576')))

def inline(s):
    # Report uses simple inline formatting, no tables or fenced blocks.
    s=s.replace('→',' -> ').replace('↔',' <-> ').replace('—','-').replace('–','-').replace('“','"').replace('”','"').replace('’',"'")
    s=html.escape(s)
    def link(m):
        label, path=m.groups()
        target=(SOURCE.parent / html.unescape(path)).resolve().relative_to(ROOT).as_posix()
        return f'<link href="{BASE+target}" color="#126576"><u>{label}</u></link>'
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    return s

def page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#cad8df'))
    canvas.line(48, A4[1]-37, A4[0]-48, A4[1]-37)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#526879'))
    canvas.drawString(48,A4[1]-28,'DRACARYS / COMPUTER NETWORKS / PHASE 2')
    canvas.drawString(48,28,'Evidence: 24 Nov 2026 | Report: 25 Nov 2026 | Markdown is canonical')
    canvas.drawRightString(A4[0]-48,28,str(doc.page))
    canvas.restoreState()

story=[]
for block in SOURCE.read_text().split('\n\n'):
    block=block.strip()
    if not block:continue
    if block.startswith('# '):story.append(Paragraph(inline(block[2:]),styles['ReportTitle']))
    elif block.startswith('## '):story.append(Paragraph(inline(block[3:]),styles['ReportHeading']))
    else:story.append(Paragraph(inline(block).replace('  \n','<br/>').replace('\n',' '),styles['ReportBody']))
doc=SimpleDocTemplate(str(TARGET),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=52,bottomMargin=48,title='Dracarys - Phase 2 Final Report',author='Team Dracarys')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(TARGET)
