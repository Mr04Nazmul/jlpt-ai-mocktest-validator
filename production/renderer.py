"""A4 Japanese PDF rendering with embedded Japanese glyphs and extraction QA."""
from pathlib import Path
from xml.sax.saxutils import escape
import io,re
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether,Table,TableStyle
FONT='FactoryJapanese'
LABELS={'kanji_reading':'漢字の読み方','orthography':'表記','word_formation':'語形成','context':'文脈に合う言葉','paraphrase':'言い換え','usage':'言葉の使い方','grammar_form':'文法形式','sentence_composition':'文の組み立て','text_grammar':'文章の文法','reading_short':'内容理解（短文）','reading_mid':'内容理解（中文）','reading_long':'内容理解（長文）','reading_integrated':'統合理解','reading_thematic':'主張理解','information':'情報検索'}
def setup():
 if FONT not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(FONT,io.BytesIO(fitz.Font('japan').buffer)))
def render(exam_id,items,b,out,draft=False):
 setup();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 style=ParagraphStyle('Japanese',fontName=FONT,fontSize=10.5,leading=18,wordWrap='CJK',spaceAfter=8)
 heading=ParagraphStyle('Heading',parent=style,fontSize=14,leading=23,spaceAfter=14,keepWithNext=True)
 small=ParagraphStyle('Small',parent=style,fontSize=8,leading=13)
 def p(s,st=style):return Paragraph(escape(s).replace('\n','<br/>'),st)
 def footer(can,doc):
  can.saveState();can.setFont(FONT,8);can.setFillColor(colors.HexColor('#555555'))
  can.drawString(42,24,exam_id+' | Independently created JLPT-style practice')
  can.drawRightString(A4[0]-42,24,str(doc.page));can.restoreState()
 def build(name,story):
  SimpleDocTemplate(str(out/name),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=43,bottomMargin=43,title=exam_id+' '+name,author='Independent JLPT-style Mock Test Factory').build(story,onFirstPage=footer,onLaterPages=footer)
 status='DRAFT — AI REVIEW PENDING' if draft else 'AI-reviewed original practice; not human-verified'
 story=[p(exam_id+' 日本語 練習試験',heading),p(status),p('聴解は含まれていません。'),p('Independent JLPT-style practice. Not an official JLPT paper or endorsement.',small),p('試験時間：'+' ＋ '.join(map(str,b['timing_minutes']))+' 分'),Spacer(1,16),p('名前：________________________________'),Spacer(1,16),p('注意'),p('答えは、１・２・３・４から一つ選んでください。答えは、最後の解答用紙に書いてください。'),p('N3・N4・N5では、文字・語彙の時間が終わってから、文法・読解を始めてください。',small),PageBreak()]
 n=0;passages=set();previous_section=None
 for mondai,c in enumerate(b['categories'],1):
  section='vocabulary' if c['id'] in ['kanji_reading','orthography','word_formation','context','paraphrase','usage'] else 'grammar_reading'
  if previous_section=='vocabulary' and section=='grammar_reading':story+=[PageBreak(),p('言語知識（文法）・読解',heading)]
  previous_section=section
  story+=[p(f'問題 {mondai}　'+LABELS[c['id']],heading)]
  for q in [x for x in items if x['category']==c['id']]:
   n+=1
   if q['passage'] and q['passage_id'] not in passages:
    story+=[p('次の文章を読んで、質問に答えてください。'),p(q['passage'])];passages.add(q['passage_id'])
   block=[p(f'Q{n:03}　'+q['question'])]
   block += [p(f'{i}　{choice}') for i,choice in enumerate(q['choices'],1)]
   # A question and all options stay together. Long passages may flow across pages.
   story+=[KeepTogether(block),Spacer(1,8)]
 story += [PageBreak(),p('解答用紙',heading),p(exam_id)]
 rows=[['番号','答え']]+[[str(i),'１　２　３　４'] for i in range(1,len(items)+1)]
 table=Table(rows,colWidths=[65,190],repeatRows=1)
 table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),FONT),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),.4,colors.grey),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 story.append(table);build('questions.pdf',story)
 keys=[p(exam_id+' 解答・解説',heading),p(status),p('Answers are 1-based. This practice paper does not estimate an official scaled JLPT score.',small)]
 for i,q in enumerate(items,1):keys.append(p(f'Q{i:03}　正解：{q["answer"]}　'+q['explanation']))
 build('answer_key.pdf',keys)

def verify_pdf(path,items,is_key=False):
 doc=fitz.open(path);errors=[]
 if doc.is_encrypted or not len(doc):errors.append('encrypted or empty')
 alltext=''
 for n,page in enumerate(doc):
  if abs(page.rect.width-A4[0])>1 or abs(page.rect.height-A4[1])>1:errors.append('not A4')
  text=page.get_text();alltext+=text
  if len(text.strip())<10:errors.append(f'blank page {n+1}')
  if '\ufffd' in text:errors.append('replacement glyph')
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     x0,y0,x1,y1=span['bbox']
     if x0<0 or y0<0 or x1>page.rect.width+1 or y1>page.rect.height+1:errors.append('text outside page')
 for i,q in enumerate(items,1):
  token=f'Q{i:03}'
  if alltext.count(token)!=1:errors.append(token+': missing or repeated')
  if is_key and not re.search(token+r'\s*正解：\s*'+str(q['answer']),alltext):errors.append(token+': key mismatch')
 fonts={f[0] for page in doc for f in page.get_fonts() if f[3]!='Helvetica'}
 if not fonts or not all(doc.extract_font(x)[3] for x in fonts):errors.append('unembedded font')
 result={'pages':len(doc),'a4':True,'embedded_fonts':True,'question_count':len(items),'errors':errors}
 if errors:raise ValueError('PDF verification failed: '+str(errors[:10]))
 return result
