import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import near_duplicate
class SharedPassageTests(unittest.TestCase):
 def setUp(self):
  self.a={'id':'N5-001-text_grammar-01','passage_id':'N5-001-text-A','passage':'昨日、友達と買い物に行きました。'*20,'question':'文章の【1】に入るものはどれですか。','choices':['でも','だから','それから','では']}
  self.b=copy.deepcopy(self.a);self.b.update(id='N5-001-text_grammar-02',question='文章の【2】に入るものはどれですか。',choices=['まで','だけ','から','より'])
 def test_distinct_gaps_in_shared_passage(self):
  self.assertIsNone(near_duplicate(self.b,[self.a]))
 def test_repeated_question_still_rejected(self):
  self.b=copy.deepcopy(self.a);self.b['id']='N5-001-text_grammar-02'
  self.assertEqual(self.a['id'],near_duplicate(self.b,[self.a]))
 def test_reordered_choices_still_rejected(self):
  self.b=copy.deepcopy(self.a);self.b['choices'].reverse()
  self.assertEqual(self.a['id'],near_duplicate(self.b,[self.a]))
 def test_reused_passage_in_other_exam_rejected(self):
  self.b['id']='N5-002-text_grammar-02'
  self.assertEqual(self.a['id'],near_duplicate(self.b,[self.a]))
 def test_reused_passage_with_different_id_rejected(self):
  self.b['passage_id']='N5-001-text-B'
  self.assertEqual(self.a['id'],near_duplicate(self.b,[self.a]))
