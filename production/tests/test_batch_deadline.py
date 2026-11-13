import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import Models, BatchPause

class BatchDeadlineTests(unittest.TestCase):
    def test_pause_before_starting_late_request(self):
        config={'max_api_calls_per_run':12,'providers':[{'kind':'ollama','base_url':'http://localhost','model':'reviewer','roles':['reviewer'],'authorized_free':True}]}
        with patch('engine.time.monotonic',return_value=100):
            models=Models(config)
        with patch('engine.time.monotonic',return_value=2800), patch('engine.request_json') as request:
            with self.assertRaises(BatchPause):
                models.ask('reviewer','question')
            request.assert_not_called()
            self.assertEqual(models.calls,0)
