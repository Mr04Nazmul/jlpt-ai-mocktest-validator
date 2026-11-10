# Production status — 2026-11-10

**Complete: 0/150.** 150 still require independent validation and verified permanent final storage.

- Original N5-001 draft: 43 questions; 14-page question PDF with answer sheets; separate 2-page answer/explanation PDF.
- Draft schema, counts, passage lengths, PDF numbering, font embedding, page bounds and key checks pass. Representative pages inspected visually.
- Independent AI review: not run. Human verification: not claimed.
- Software: 15 automated tests pass locally. Initial GitHub Actions software checks and durable checkpoint push passed; generation was blocked at credential preflight.
- Credentials required: authorized free generator/reviewer models plus persistent Drive OAuth for the runner. Production remains disabled until configured and verified.
- Existing Drive tests are excluded and unchanged. New destination is JLPT_150_MOCK_TESTS.
- Workflow scheduled every six hours and manually restartable; installed schedule does not imply operational generation or uninterrupted execution.

See README.md for secure setup and recovery. Do not send API secrets in chat.
