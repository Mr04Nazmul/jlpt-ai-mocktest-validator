"""Provider failures must be actionable without leaking request secrets."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib import error

spec = importlib.util.spec_from_file_location("factory_network_test", Path(__file__).resolve().parents[1] / "engine.py")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

class ProviderFailureTests(unittest.TestCase):
    def check_failure(self, exc, expected):
        with patch.object(engine.request, "urlopen", side_effect=exc) as send, patch.object(engine.time, "sleep") as sleep:
            with self.assertRaisesRegex(engine.Blocked, expected) as result:
                engine.request_json("http://localhost/private", headers={"Authorization": "secret"}, timeout=7, attempts=2)
            self.assertEqual(send.call_count, 2)
            sleep.assert_called_once_with(1)
            self.assertNotIn("secret", str(result.exception))
            self.assertNotIn("private", str(result.exception))

    def test_direct_timeout(self):
        self.check_failure(TimeoutError("secret"), "timeout after 7s; 2 attempts")

    def test_wrapped_timeout(self):
        self.check_failure(error.URLError(TimeoutError("secret")), "timeout after 7s; 2 attempts")

    def test_connection_refused(self):
        self.check_failure(error.URLError(ConnectionRefusedError("secret")), "ConnectionRefusedError; 2 attempts")

    def test_untrusted_reason_is_not_printed(self):
        self.check_failure(error.URLError("secret private"), "str; 2 attempts")

if __name__ == "__main__":
    unittest.main()
