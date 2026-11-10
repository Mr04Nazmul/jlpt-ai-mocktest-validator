"""No external AI API: Ollama is bound to loopback only."""
import io,json,re,hashlib,unicodedata,sqlite3,time
from pathlib import Path
from difflib import SequenceMatcher
import requests
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

LEVELS=["N5","N4","N3","N2","N1"]
DB=Path("data/questions.sqlite3")
def db():
    DB.parent.mkdir(exist_ok=True)
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS questions(id TEXT PRIMARY KEY, body TEXT NOT NULL)")
    return c
def save(q):
    with db() as c: c.execute("INSERT OR REPLACE INTO questions VALUES (?,?)",(q["id"],json.dumps(q,ensure_ascii=False)))
def all_questions():
    with db() as c: return [json.loads(x[0]) for x in c.execute("SELECT body FROM questions ORDER BY id")]
def normalize(s):
    return re.sub(r"\s+","",unicodedata.normalize("NFKC",s)).casefold()
def duplicates(text, existing):
    norm=normalize(text)
    return [{"id":q["id"],"score":round(SequenceMatcher(None,norm,normalize(q["text"])).ratio(),3)}
            for q in existing if SequenceMatcher(None,norm,normalize(q["text"])).ratio()>=.9]
def extract_pdf(data):
    if len(data)>20*1024*1024: raise ValueError("PDF exceeds 20 MB")
    reader=PdfReader(io.BytesIO(data))
    if reader.is_encrypted: raise ValueError("Encrypted PDF unsupported")
    if len(reader.pages)>100: raise ValueError("Maximum 100 pages per upload")
    pages=[]
    for n,p in enumerate(reader.pages,1):
        text=p.extract_text(extraction_mode="layout") or ""
        if not text.strip(): raise ValueError(f"Page {n}: no text layer. OCR/manual transcription required.")
        pages.append({"page":n,"text":text})
    return pages
def parse_questions(pages,level,source):
    # Deliberately narrow format. Arbitrary papers must be segmented manually.
    result=[]
    for page in pages:
        chunks=re.split(r"(?m)^\s*Q\d+[.：:]\s*",page["text"])[1:]
        for chunk in chunks:
            key=re.search(r"(?im)^\s*Answer:\s*([1-4])\s*$",chunk)
            text=re.sub(r"(?im)^\s*Answer:.*$","",chunk).strip()
            result.append(make_question(text,level,source,page["page"],int(key[1]) if key else None))
    return result
def make_question(text,level,source,page=1,answer=None):
    if level not in LEVELS: raise ValueError("Invalid level")
    return dict(id=hashlib.sha256((json.dumps(source,sort_keys=True)+str(page)+text).encode()).hexdigest()[:20],
                text=text,level=level,source=source,page=page,answer=answer,status="manual_review",
                ai=None,history=[])
def validate(q):
    if re.search(r"聴解|Listening",q["text"],re.I): raise ValueError("Listening content excluded")
    issues=[]
    if q.get("answer") not in [1,2,3,4]: issues.append("Missing/invalid answer key")
    if not all(re.search(rf"(?m)^\s*{n}[.．)）]",q["text"]) for n in range(1,5)):
        issues.append("Four option boundaries not confirmed")
    if "�" in q["text"]: issues.append("Broken PDF character encoding")
    return issues
def ai_review(q):
    model=Path("data/model.txt").read_text().strip()
    if not re.fullmatch(r"qwen2\.5:(0\.5b|1\.5b|3b)",model): raise ValueError("Unsupported model")
    prompt=Path("prompts/validator.txt").read_text()
    response=requests.post("http://127.0.0.1:11434/api/chat",json={
        "model":model,"stream":False,"format":"json","keep_alive":"2m",
        "messages":[{"role":"system","content":prompt},{"role":"user","content":json.dumps(q,ensure_ascii=False)}],
        "options":{"temperature":0,"num_ctx":4096,"num_predict":1200,"num_gpu":0}},timeout=240)
    response.raise_for_status()
    raw=response.json()["message"]["content"]
    Path("data/last_ai_response.json").write_text(raw)
    out=json.loads(raw)
    checks=["vocabulary","grammar","reading","kanji","hiragana","furigana","answer_key"]
    if not isinstance(out,dict) or not all(k in out for k in ["suggested_level","checks","issues","proposed_text","proposed_answer","confidence","uncertain"]):
        raise ValueError("Incomplete AI response; manual review required")
    if out["suggested_level"] not in LEVELS or not isinstance(out["checks"],dict) or not all(isinstance(out["checks"].get(k),str) for k in checks):
        raise ValueError("Invalid AI checks")
    if type(out["confidence"]) not in (float,int) or not 0<=out["confidence"]<=1 or type(out["uncertain"]) is not bool:
        raise ValueError("Invalid confidence")
    if not isinstance(out["issues"],list) or not all(isinstance(i,str) for i in out["issues"]) or not isinstance(out["proposed_text"],str):
        raise ValueError("Invalid AI proposal")
    if out["proposed_answer"] is not None and (type(out["proposed_answer"]) is not int or out["proposed_answer"] not in [1,2,3,4]):
        raise ValueError("Invalid proposed answer")
    return out
def approve(q,text,answer,level,reviewer):
    if not reviewer.strip(): raise ValueError("Reviewer name required")
    updated={**q,"text":text,"answer":answer,"level":level}
    issues=validate(updated)
    if issues: raise ValueError("; ".join(issues))
    updated["history"]=q["history"]+[{"at":time.time(),"reviewer":reviewer,"old_text":q["text"],"old_answer":q["answer"],"old_level":q["level"]}]
    updated["status"]="human_reviewed"
    return updated
def export_pdf(items):
    items=[q for q in items if q["status"]=="human_reviewed"]
    if not items: raise ValueError("No human-reviewed questions")
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=(595,842))
    for level in LEVELS:
        for q in [x for x in items if x["level"]==level]:
            c.setFont("HeiseiKakuGo-W5",11); y=800
            lines=[f"{level} | Human-reviewed practice | {q['id']}"]+q["text"].splitlines()+[f"Answer: {q['answer']}",f"Source: {q['source'].get('title','upload')} | page {q['page']}"]
            for line in lines:
                for start in range(0,max(1,len(line)),42):
                    if y<40: c.showPage(); c.setFont("HeiseiKakuGo-W5",11); y=800
                    c.drawString(30,y,line[start:start+42]); y-=18
            c.showPage()
    c.save(); return buf.getvalue()
def collect(source):
    # Registry-only exact URLs, no recursive scraping, redirects or arbitrary hosts.
    from urllib.parse import urlsplit
    url=source["url"]; host=urlsplit(url).hostname
    if urlsplit(url).scheme!="https" or host not in ("raw.githubusercontent.com","github.com"):
        raise ValueError("Collector only accepts HTTPS GitHub sources")
    if source.get("license") not in ["CC0-1.0","CC-BY-4.0","CC-BY-SA-4.0","permission"]:
        raise ValueError("Documented reuse rights required")
    if not source.get("rights_evidence"): raise ValueError("Rights evidence required")
    with requests.get(url,timeout=30,stream=True,allow_redirects=False) as r:
        r.raise_for_status()
        if r.is_redirect: raise ValueError("Use the exact final GitHub URL")
        data=bytearray()
        for part in r.iter_content(65536):
            data.extend(part)
            if len(data)>20*1024*1024: raise ValueError("Source exceeds 20 MB")
    if not data.startswith(b"%PDF"): raise ValueError("Not a PDF")
    return bytes(data)
