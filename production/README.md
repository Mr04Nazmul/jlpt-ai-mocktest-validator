# Original JLPT Mock Test Factory

Target: 30 original non-listening examinations per level, 150 question PDFs plus 150 separate keys. Existing Drive tests are EXCLUDED by explicit user instruction (2026-11-10). Existing app, Supabase and old papers are untouched.

## Current truth

0/150 complete. N5-001 has 43 original questions and DRAFT PDFs. Schema, category counts, passages and PDF integrity checks pass. Independent AI review and production Drive download verification have not run. The draft is not certified or complete. No authorized inference or persistent Drive credential was found locally. Production stays disabled until setup is verified.

## Blueprints

N5: 43 = 21 vocabulary + 17 grammar + 5 reading, 20+40 minutes.
N4: 57 = 28+21+8, 25+55 minutes.
N3: 74 = 35+23+16, 30+70 minutes.
N2: 75 = 32+22+21, 105 minutes.
N1: 70 = 25+20+25, 110 minutes.

N4/N5 use revised 2020 official counts. N1-N3 use the explicit Official Practice Workbook Vol.2 (2018) distribution. The N1 workbook has two integrated-reading questions (63-64), whereas the old approximate guidebook lists three. Project uses the workbook reference. Actual official sessions may vary. Character-length bands are project tolerance limits around official approximate lengths, not official cutoffs. All categories, counts, references and evidence hashes live in blueprints/. No endorsement or official scaled-score equivalence is claimed.

## Run

Python 3.11; from repository root:

```
python -m pip install -r production/requirements.txt
python -m unittest discover -s production/tests -v
python production/engine.py status
python production/engine.py preflight
python production/engine.py run
```

Workflow: scheduled every six hours, push-triggered and manually restartable. GitHub can delay schedules, disable inactive schedules or exhaust included quotas. Set GitHub paid budget to zero yourself; code cannot inspect billing. No paid API or cloud service is activated.

## Configure existing authorized free resources

Add JLPT_GENERATOR_API_KEY and JLPT_REVIEWER_API_KEY as repository Actions secrets. Workflow maps them to GENERATOR_API_KEY and REVIEWER_API_KEY. Never put secrets in Git, config or chat.

Populate config.json providers with kind (openai_compatible or ollama), base_url, model, key_env, roles (generator/reviewer), authorized_free:true. Set authorized_free only after confirming existing included/free quota and no billable overages. Empty providers are intentional. Distinct endpoint+model is required for independent blind review. Add authorized alternatives for failover. OpenAI-compatible APIs and local Ollama are implemented; other providers can use their documented compatibility endpoint. No dummy keys or automatic account activation.

## Persistent Drive authorization

ChatGPT connector authentication cannot be transferred to Actions. For personal My Drive use an approved user OAuth refresh credential saved as JLPT_DRIVE_OAUTH_JSON, containing client_id, client_secret, refresh_token and authorized drive.file scope. Ensure this OAuth app is actually authorized for the configured folder (drive.file does not grant arbitrary existing-folder access). User OAuth app testing mode can expire refresh tokens; choose a properly authorized durable setup. Alternative: JLPT_DRIVE_SERVICE_ACCOUNT_JSON for a service account with access to a Shared Drive. Sharing a personal My Drive folder with a service account alone does not solve its ownership/storage-quota restriction. Never enable paid storage automatically.

Set production_enabled:true only after verifying both independent providers and persistent Drive authentication. Manually resume the workflow. Current connector-created folder IDs are in config.json; ensure the runner identity can access them.

## Durability and recovery

Canonical Git-tracked state: state/manifest.json, state/drafts/, state/reviews/, state/question_bank.json, state/duplicate_index.json and output/. SQLite is a rebuildable query index. The workflow commits checkpoints on success or failure. Outputs also persist in Drive; temporary Actions artifacts are not relied upon. The first N5 integration exam must reach STORED before other tests proceed. Each run completes at most one test, with serialized workflows, fixed exam IDs, cached category generation and content-hashed review records.

States: PENDING → GENERATING → VALIDATING → RENDERING → VERIFIED → STORED. Content failure goes to NEEDS_REVIEW. Transient failure goes to RETRY_PENDING with exponential retry time and capped attempts. Completed artifacts are never deleted. Uploads use content hashes and appProperties for idempotency and verify downloaded bytes against SHA-256. Four verified uploads (paper, key, JSON, validation report) are required before STORED. Source bank is rebuilt from stored source JSON on recovery, preventing a partial checkpoint from losing uniqueness records. Checkpoints are saved as immutable Drive files; newest timestamp is authoritative.

For NEEDS_REVIEW, inspect question/error/review evidence. Correct the category draft JSON in state/drafts/<exam>/, preserve original evidence in Git, reset only that exam to RETRY_PENDING and attempts:0, then rerun checks and workflow. Modified hashes invalidate previous review. Never manually set VERIFIED or STORED. A failed Git checkpoint push, branch protection, revoked OAuth, runner quota or provider outage is an external blocker. Restore latest committed state; previously stored work remains intact.

## Validation scope

Checks: schema/Unicode, four distinct choices, exact category counts, passage groups/lengths, sentence-composition slots, exact/near duplication, blind independent model solution and distractor review, bounded-window semantic duplication review, answer-key consistency, A4 page bounds, embedded Japanese fonts, numbered questions and nonempty pages. AI review is never labeled human verification. These checks do not prove linguistic correctness or official difficulty equivalence. Representative PDF page images are visually inspected during development; production papers still benefit from human editorial review.

Official PDFs are structural references only, not copied content. All production questions are original. Candidate open dataset references are listed in sources.json but not imported.
