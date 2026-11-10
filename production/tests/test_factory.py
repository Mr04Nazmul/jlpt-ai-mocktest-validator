import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import *
class Checks(unittest.TestCase):
 def setUp(self):
  self.b=read(ROOT/'blueprints/N5.json')
  self.q={'id':'test-001','level':'N5','category':'grammar_form','question':'きのう、学校（　）行きました。','passage_id':'','passage':'','choices':['へ','を','が','の'],'answer':1,'explanation':'移動の方向を表す助詞「へ」を使います。','tags':['direction'],'provenance':{'kind':'original_ai_generation','model':'fixture'}}
 def test_counts(self):
  for level,total in [('N5',43),('N4',57),('N3',74),('N2',75),('N1',70)]:
   b=read(ROOT/f'blueprints/{level}.json');self.assertEqual(total,sum(c['count'] for c in b['categories']))
 def test_valid_item(self):self.assertEqual([],check_questions([self.q],self.b,False))
 def test_normalized_choices(self):
  self.q['choices']=['へ',' へ ','が','の'];self.assertIn('normalized repeated choices',check_questions([self.q],self.b,False))
 def test_answer_bounds(self):
  self.q['answer']=0;self.assertTrue(check_questions([self.q],self.b,False))
 def test_missing_section(self):self.assertIn('blueprint count mismatch',check_questions([self.q],self.b))
 def test_duplicate(self):self.assertEqual('test-001',near_duplicate(self.q,[self.q]))
 def test_passage_length(self):
  self.q.update(category='reading_mid',passage='短い文。',passage_id='a');self.assertTrue(check_questions([self.q],self.b,False))
 def test_no_credentials(self):
  models=Models({'providers':[]});self.assertRaises(Blocked,models.choose,'generator')
 def test_independent_model(self):
  p={'kind':'ollama','base_url':'http://localhost:11434','model':'same','authorized_free':True,'roles':['generator','reviewer']}
  self.assertRaises(Blocked,Models({'providers':[p]}).choose,'reviewer',('http://localhost:11434','same'))
 def test_atomic_state(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x.json';write(p,{'a':1});write(p,{'a':2});self.assertEqual(2,read(p)['a']);self.assertFalse(p.with_suffix('.json.tmp').exists())
 def test_renderer_and_corruption(self):
  from renderer import render,verify_pdf
  with tempfile.TemporaryDirectory() as t:
   b=copy.deepcopy(self.b);b['categories']=[{'id':'grammar_form','count':1}]
   render('FIXTURE',[self.q],b,t,draft=True)
   self.assertEqual([],verify_pdf(Path(t)/'questions.pdf',[self.q])['errors'])
   self.assertEqual([],verify_pdf(Path(t)/'answer_key.pdf',[self.q],True)['errors'])
   wrong=copy.deepcopy(self.q);wrong['answer']=2
   self.assertRaises(ValueError,verify_pdf,Path(t)/'answer_key.pdf',[wrong],True)
if __name__=='__main__':unittest.main()

class CompletionGuards(unittest.TestCase):
 def test_no_false_completion(self):
  from unittest.mock import Mock
  f=Factory.__new__(Factory);f.manifest={'exams':{'N5-001':{'state':'RENDERING'}}};f.checkpoint=Mock()
  self.assertRaises(ReviewNeeded,f.transition,'N5-001','STORED',receipts=[])
 def test_cannot_mutate_completed(self):
  from unittest.mock import Mock
  f=Factory.__new__(Factory);f.manifest={'exams':{'N5-001':{'state':'STORED'}}};f.checkpoint=Mock()
  self.assertRaises(ReviewNeeded,f.transition,'N5-001','GENERATING')
 def test_review_hash_changes(self):
  q={'question':'昨日、行きました。','choices':['a','b','c','d']};before=content_hash(q);q['choices'][0]='変更';self.assertNotEqual(before,content_hash(q))
