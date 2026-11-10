# JLPT AI Mock Test Collector & Validator

CPU-only Qwen via Ollama, running inside GitHub Codespaces. No paid AI API,
external hosting, GPU, listening, or changes to Nihongo Path Books.

## Setup
1. Keep GitHub Codespaces paid usage budget at $0 with usage blocking enabled.
   Check remaining included compute/storage in GitHub Billing. Free is quota-limited,
   not unlimited. This repository cannot enforce your account billing settings.
2. Code → Codespaces → create a 2-core codespace. Keep forwarded port 8501 PRIVATE.
3. The devcontainer installs Python dependencies and Ollama. If setup needs retry:
   `bash scripts/setup.sh`
4. Run `bash scripts/start.sh`, then `bash scripts/model.sh`.
   Model selection uses available RAM: 2.5–6 GB: qwen2.5:0.5b;
   6–12 GB: qwen2.5:1.5b; 12+ GB: qwen2.5:3b.
   Below 2.5 GB: refuse. These are conservative heuristics, not benchmarks.
5. Open private port 8501 in iPhone Safari and authenticate with GitHub.
   Ollama port 11434 must never be forwarded.
6. Stop the codespace when finished. Stored codespaces still consume storage quota.
   Download question JSON backups before deleting a codespace.

Ollama/model downloads come from the official vendor; application compute and data
remain in Codespaces. No other cloud service or paid inference endpoint is used.

## Workflow
Upload a text-layer PDF, specify title and permission evidence, and attest reuse rights.
Automatic segmentation recognizes only explicit Q1:/Q2: question blocks, four numbered
choices, and optional `Answer: 1` lines. Other layouts show extracted page text for
manual segmentation. Preserve entire reading passages. Japanese text extraction may
misorder furigana or columns: compare with the original. Scanned, encrypted, >100-page,
and >20-MB files are rejected; OCR is not implemented.

Every item starts in manual review. Structural checks flag keys, options, broken
encoding and listening. Unicode-normalized exact and >=0.90 text-similarity duplicates
are shown across stored items. This is not semantic duplicate detection.

Ask Qwen for separate vocabulary, grammar, reading, kanji, hiragana, furigana and
answer checks. Prompt: [prompts/validator.txt](prompts/validator.txt).
Responses must pass schema checks. All responses, errors, uncertainty and proposed
corrections require human review. Small CPU models can be wrong, especially N1/N2.
No level or linguistic correctness is certified automatically. JLPT level estimates
are not official word-list checks. A named human must verify and approve every
exported question. Original text/key/level is retained in audit history.
PDF exports contain only human-reviewed items, ordered N5→N1; answer keys included.
CID Japanese font rendering can depend on the PDF viewer; inspect exported PDFs.

## Permitted collection
The source registry starts EMPTY: no third-party collection is claimed.
Add exact GitHub HTTPS PDF URLs to sources.json with title, license and rights_evidence.
Accepted licenses: CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0, or permission.
Verify evidence yourself before adding; a registry claim is not legal verification.
Preserve attribution and share-alike obligations when applicable.
Only GitHub-hosted PDF sources are fetched, with redirects disabled and size capped.
No paywall bypass, unrestricted scraping, copyrighted-book bundling or listening.
All five JLPT levels are supported by import and review filters.

Example source entry (replace placeholders; do not treat as an actual source):
```json
{"title":"Owner-authorized N5 paper","url":"https://raw.githubusercontent.com/OWNER/REPO/COMMIT/paper.pdf","license":"permission","rights_evidence":"Owner permission reference"}
```

## Testing
`python -m unittest discover -s tests -v`
`PYTHONPATH=. python scripts/smoke.py`
The smoke script creates an actual original CC0 Japanese text PDF, extracts it,
parses an answer key, checks duplicates, persists it and requests Qwen.
It is a technical fixture, not a full official exam or linguistic benchmark.
See TEST_REPORT.md for observed results and untested requirements.

## Data
SQLite and generated PDFs/logs live in ignored data/. Nothing is uploaded to GitHub
automatically. Source code is public: do not commit private tests, tokens or permissions.
Model changes never automatically overwrite an approved item. Re-review after edits.
