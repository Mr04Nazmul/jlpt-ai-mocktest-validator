import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import pipeline as p
class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.patch=patch.object(p,"DB",Path(self.tmp.name)/"q.db"); self.patch.start()
        self.text="「学生」の 読み方は どれですか。\n1. がくせい\n2. せんせい\n3. いしゃ\n4. かいしゃいん"
        self.q=p.make_question(self.text,"N5",{"title":"Original CC0 fixture"},answer=1)
    def tearDown(self): self.patch.stop(); self.tmp.cleanup()
    def test_roundtrip_and_duplicates(self):
        p.save(self.q); self.assertEqual(len(p.all_questions()),1)
        self.assertEqual(p.duplicates(self.text.replace(" ",""),[self.q])[0]["score"],1)
    def test_export_requires_review(self):
        with self.assertRaises(ValueError): p.export_pdf([self.q])
        q=p.approve(self.q,self.text,1,"N5","test reviewer")
        data=p.export_pdf([q]); self.assertTrue(data.startswith(b"%PDF"))
        self.assertIn("学生",p.extract_pdf(data)[0]["text"])
    def test_bad_key_and_listening(self):
        q={**self.q,"answer":None}; self.assertTrue(p.validate(q))
        with self.assertRaises(ValueError): p.validate({**self.q,"text":"聴解"})
    def test_parser(self):
        qs=p.parse_questions([{"page":1,"text":"Q1: "+self.text+"\nAnswer: 1"}],"N5",{})
        self.assertEqual(qs[0]["answer"],1)
    def test_source_rights(self):
        with self.assertRaises(ValueError): p.collect({"url":"https://example.com/a.pdf","license":"CC0-1.0","rights_evidence":"x"})
    def test_wrong_level(self):
        with self.assertRaises(ValueError): p.make_question("x","N6",{})
if __name__=="__main__": unittest.main()
