import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import Factory, ReviewNeeded

class SemanticPayloadTests(unittest.TestCase):
 def check_payload(self,uncertain):
  q={'id':'new','category':'context','question':'雨が ふっています。','passage':'','passage_id':'','choices':['かさ','くつ','時計','皿'],'answer':1,'explanation':'test','provenance':{}}
  prior={**q,'id':'prior','question':'パンを 食べます。','choices':['パン','水','空','駅']}
  review={'answer':1,'defensible_choices':[1],'checks':dict.fromkeys(['japanese','level','mondai','reading','distractors','passage'],True),'explanation':'This test review contains sufficiently detailed reasoning.','issues':[]}
  with tempfile.TemporaryDirectory() as td:
   f=Factory.__new__(Factory);f.state=Path(td);f.bank=[prior];f.models=Mock()
   f.models.choose.return_value=[{'base_url':'local','model':'reviewer'}]
   f.models.ask.side_effect=[(review,('local','reviewer')),({'duplicate_ids':[],'uncertain':uncertain,'reason':'test'},('local','reviewer'))]
   if uncertain:
    with self.assertRaisesRegex(ReviewNeeded,'Semantic duplicate'):
     f.review('exam',[q],{'new':('local','generator')},{'version':'test'})
   else:
    result=f.review('exam',[q],{'new':('local','generator')},{'version':'test'})
    self.assertEqual(result['reviews'][0]['semantic_policy_version'],'2')
   prompt=f.models.ask.call_args.args[1]
   candidates=json.loads(prompt.split(' Prior items ',1)[1])
   self.assertEqual(candidates[0]['choices'],prior['choices'])
   self.assertEqual(candidates[0]['category'],'context')
 def test_complete_comparison_payload(self): self.check_payload(False)
 def test_uncertainty_still_blocks(self): self.check_payload(True)
