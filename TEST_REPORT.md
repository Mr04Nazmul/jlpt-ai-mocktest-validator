# Test report — 2026-11-10

This is a technically tested MVP, not a certified autonomous JLPT examiner.

| Check | Observed result |
|---|---|
| Six unit tests in Codespaces | PASS: reports/unit-tests.txt |
| Actual original Japanese PDF extraction | PASS |
| Numbered question and answer parsing | PASS for fixture format |
| Unicode duplicate check and SQLite storage | PASS |
| Human approval gate and Japanese PDF round-trip | PASS |
| Registered GitHub CC0 PDF collection | PASS: reports/collector.txt |
| Ollama Qwen 0.5B and 1.5B plain JSON | Inference ran; invalid review schema rejected |
| Qwen 1.5B with enforced JSON schema | PASS transport/schema: reports/ollama-smoke.txt |
| Japanese linguistic reliability | NOT PASSED / NOT CERTIFIED |
| Browser interface | Opened; review controls observed |
| Physical iPhone Safari test | NOT PERFORMED |

The schema-valid AI result had confidence 0 and uncertain=true, with an unhelpful
issue saying the untrusted question should be ignored. This is a real small-model
quality limitation. Schema validity does not establish correctness; every proposal
requires manual review. No automatic answer correction or approval is claimed.

## Remaining limitations
- One original one-question CC0 technical fixture; no full mock exam corpus.
- No third-party N5–N1 papers approved or collected.
- All five level labels and review categories are implemented, but independent
  linguistic evaluation across N5–N1 is not complete.
- No OCR. Arbitrary PDF layouts require manual segmentation.
- Similarity detection is textual, not semantic.
- Japanese CID PDF text round-trip passed; actual iOS rendering remains unverified.
- Rights evidence requires human verification.
- Initial optional system font download was slow; unnecessary system packages
  were removed from final setup.
- Final devcontainer disables automatic forwarding of model/worker ports.
  Rebuild to apply those settings if using an older container.

## Reproduce
```bash
bash scripts/setup.sh
bash scripts/start.sh
bash scripts/model.sh
python -m unittest discover -s tests -v
PYTHONPATH=. python scripts/smoke.py
```

Only the original sample and non-private technical test logs are committed under
samples/ and reports/. Runtime data remains ignored.
