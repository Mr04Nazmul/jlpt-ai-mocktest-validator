"""Real generated text-PDF fixture, not an official or externally collected exam."""
import json
from pathlib import Path
import pipeline as p
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
Path("data").mkdir(exist_ok=True)
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
c=canvas.Canvas("data/sample.pdf"); c.setFont("HeiseiKakuGo-W5",12)
for i,line in enumerate(["Q1: 「学生」の 読み方は どれですか。","1. がくせい","2. せんせい","3. いしゃ","4. かいしゃいん","Answer: 1"]): c.drawString(40,780-i*24,line)
c.save()
pages=p.extract_pdf(Path("data/sample.pdf").read_bytes())
qs=p.parse_questions(pages,"N5",{"title":"Original smoke fixture","license":"CC0-1.0"})
assert len(qs)==1 and qs[0]["answer"]==1
assert p.duplicates(qs[0]["text"],qs)
p.save(qs[0])
print("PDF extraction / parser / answer key / duplicates / storage: PASS")
try:
    out=p.ai_review(qs[0]); print("OLLAMA_RESULT="+json.dumps(out,ensure_ascii=False))
    print("AI response schema: PASS (linguistic accuracy NOT certified)")
except Exception as e:
    print("AI integration: FAIL",str(e)); raise
