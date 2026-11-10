"""Verify connector-downloaded final files before completing an examination.
Never accept mere upload success or metadata as a download integrity proof.
"""
import argparse,json
from pathlib import Path
from engine import Factory,ROOT,Blocked,read,write,sha,content_hash,check_questions
from renderer import verify_pdf

def complete(exam_id,downloads):
 f=Factory();e=f.manifest['exams'][exam_id]
 if e['state']!='VERIFIED':raise Blocked('Connector bridge requires VERIFIED state')
 out=ROOT/'output'/exam_id;items=read(out/'questions.json');report=read(out/'validation.json')
 b=read(ROOT/'blueprints'/(e['level']+'.json'))
 if check_questions(items,b) or report['status']!='AI_REVIEWED_NOT_HUMAN_VERIFIED' or report['question_hashes']!=[content_hash(q) for q in items] or len(report['reviews'])!=len(items):raise Blocked('Question/review evidence mismatch')
 for name,is_key in [('questions.pdf',False),('answer_key.pdf',True)]:verify_pdf(out/name,items,is_key)
 expected={'questions.pdf','answer_key.pdf','questions.json','validation.json'}
 if {r['kind'] for r in downloads}!=expected or len(downloads)!=4:raise Blocked('Four downloaded artifacts required')
 receipts=[]
 for r in downloads:
  original=(out/r['kind']).read_bytes();download=Path(r['downloaded_path']).read_bytes()
  if sha(original)!=sha(download) or not r.get('drive_file_id'):raise Blocked('Drive round-trip SHA mismatch')
  receipts.append({'name':exam_id+'_'+r['kind'],'drive_file_id':r['drive_file_id'],'sha256':sha(download),'download_verified':True,'bytes':len(download)})
 write(out/'storage_receipts.json',receipts);f.bank.extend(items)
 f.transition(exam_id,'STORED',receipts=receipts,storage_status='CONNECTOR_ROUND_TRIP_VERIFIED')
 return {'exam_id':exam_id,'state':'STORED','complete':f.manifest['complete'],'remaining':f.manifest['remaining']}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('exam_id');p.add_argument('downloads_json');a=p.parse_args();print(json.dumps(complete(a.exam_id,read(a.downloads_json))))
