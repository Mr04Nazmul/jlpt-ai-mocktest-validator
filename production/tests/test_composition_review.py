import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import Factory, ReviewNeeded, read, ROOT

class CompositionReviewTests(unittest.TestCase):
    def run_review(self, order):
        q = read(ROOT/'state/drafts/N5-001/sentence_composition.json')['questions'][2]
        verdict = {'answer':1,'defensible_choices':[1],'checks':dict.fromkeys(['japanese','level','mondai','reading','distractors','passage'],True),'explanation':'四つの語を順番に並べ、星印の位置の選択肢を確認しました。','issues':[]}
        if order is not None: verdict['composition_order']=order
        with tempfile.TemporaryDirectory() as td:
            f=Factory.__new__(Factory);f.bank=[];f.state=Path(td);f.models=Mock()
            f.models.choose.return_value=[{'base_url':'local','model':'reviewer'}]
            f.models.ask.return_value=(verdict,('local','reviewer'))
            result=f.review('N5-001',[q],{q['id']:('local','generator')},{'version':'test'})
            self.assertIn('composition_order',f.models.ask.call_args.kwargs['schema']['required'])
            self.assertEqual(result['reviews'][0]['review_policy_version'],'3')
            return result

    def test_matching_order(self):
        self.run_review([3,1,2,4])

    def test_correct_answer_but_contradictory_order_rejected(self):
        with self.assertRaisesRegex(ReviewNeeded,'contradicts'):
            self.run_review([3,4,2,1])

    def test_missing_order_rejected(self):
        with self.assertRaisesRegex(ReviewNeeded,'Malformed'):
            self.run_review(None)

    def test_repeated_fragment_rejected(self):
        with self.assertRaisesRegex(ReviewNeeded,'Malformed'):
            self.run_review([3,1,1,4])
