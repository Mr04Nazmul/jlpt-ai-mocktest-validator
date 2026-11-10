import json
from pathlib import Path
import streamlit as st
from pipeline import *
st.set_page_config(page_title="JLPT AI Review",page_icon="🌸",layout="centered")
st.title("🌸 JLPT Collector & Validator")
st.caption("N5–N1 • No listening • CPU Qwen • Human approval required")
st.warning("AI suggestions are unverified. Approve only after checking the original PDF and answer key.")
level=st.selectbox("Import level",LEVELS)
title=st.text_input("Source title")
rights=st.text_input("License / written permission reference")
consent=st.checkbox("I own this content or have permission to reuse it")
upload=st.file_uploader("Upload text PDF (max 20 MB, 100 pages)",type=["pdf"])
def ingest(data,source):
    pages=extract_pdf(data)
    st.session_state["pages"]=pages
    questions=parse_questions(pages,level,source)
    for q in questions: save(q)
    st.success(f"{len(pages)} pages extracted; {len(questions)} structured questions imported.")
    if not questions: st.info("Layout not recognized. Segment each question below; keep its reading passage and four choices together.")
if st.button("Extract uploaded PDF",disabled=not(upload and consent and rights and title)):
    try: ingest(upload.getvalue(),dict(title=title,rights=rights))
    except Exception as e: st.error(str(e))
sources=json.loads(Path("sources.json").read_text())["sources"]
st.subheader("Approved source collector")
if sources:
    selected=st.selectbox("Registered source",sources,format_func=lambda x:x["title"])
    if st.button("Collect source"):
        try: ingest(collect(selected),selected)
        except Exception as e: st.error(str(e))
else: st.info("No third-party source is approved yet. Add documented reusable GitHub PDF URLs to sources.json.")
pages=st.session_state.get("pages",[])
if pages:
    page=st.selectbox("Extracted page",pages,format_func=lambda x:str(x["page"]))
    st.text_area("Original extracted text",page["text"],height=220,disabled=True)
    with st.form("segment"):
        text=st.text_area("One complete question, passage and choices (1. through 4.)",height=200)
        key=st.selectbox("Supplied answer (0 = unknown)",[0,1,2,3,4])
        if st.form_submit_button("Save question for review"):
            if not (consent and title and rights and text.strip()): st.error("Source permission and question required")
            else:
                save(make_question(text,level,dict(title=title,rights=rights),page["page"],key or None)); st.rerun()
st.subheader("Review queue")
questions=all_questions()
filter_level=st.selectbox("Show level",["All"]+LEVELS)
for q in questions:
    if filter_level!="All" and q["level"]!=filter_level: continue
    with st.expander(f"{q['level']} · {q['id']} · {q['status']}"):
        st.text(q["text"])
        st.write("Source",q["source"],"Page",q["page"],"Key",q["answer"])
        st.write("Structural issues",validate(q))
        st.write("Possible duplicates",duplicates(q["text"],[x for x in questions if x["id"]!=q["id"]]))
        if st.button("Ask local Qwen",key="ai"+q["id"]):
            try:
                with st.spinner("CPU review may take several minutes"):
                    q["ai"]=ai_review(q); q["status"]="manual_review"; save(q)
                st.rerun()
            except Exception as e: st.error(f"AI review failed; manual review required: {e}")
        if q["ai"]: st.json(q["ai"])
        with st.form("review"+q["id"]):
            corrected=st.text_area("Human-reviewed text",q["text"])
            answer=st.selectbox("Verified answer",[1,2,3,4],index=(q["answer"] or 1)-1)
            reviewed_level=st.selectbox("Verified level",LEVELS,index=LEVELS.index(q["level"]))
            reviewer=st.text_input("Reviewer name")
            confirmed=st.checkbox("I checked Japanese, level, readings, passage, unique correct answer and source PDF")
            if st.form_submit_button("Approve reviewed version"):
                try:
                    if not confirmed: raise ValueError("Human check required")
                    save(approve(q,corrected,answer,reviewed_level,reviewer)); st.rerun()
                except Exception as e: st.error(str(e))
if questions:
    st.download_button("Backup all questions (JSON)",json.dumps(questions,ensure_ascii=False,indent=2),"questions.json","application/json")
    try: st.download_button("Export reviewed PDF",export_pdf(questions),"jlpt-reviewed.pdf","application/pdf")
    except ValueError: st.info("Reviewed PDF becomes available after human approval.")
