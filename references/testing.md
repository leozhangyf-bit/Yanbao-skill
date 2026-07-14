# Testing and release method

## Offline suites

Test strict contracts and Schema, blueprint permissions, evidence-linked relationship changes, runtime budgets and leakage, inbox/outbox idempotency, life-wake idempotency, private-event commits, proactive disclosure receipts, media transitions, configuration migration, backup integrity, path escape, metadata stripping, retention and text/media isolation.

Use fake model, fake channel and fake clock. Inject crashes after every external boundary: generation, file copy, upload, resource receipt, send, message receipt, caption and commit.

Run a 30-day fake-clock life suite with two scheduled wakes per day. Prove that ineligible wakes make no model call, eligible wakes make no more than one, long gaps coalesce, roles and supporting actors act without user advice, every event has a causal basis, repetitive routine-only events fail, private facts do not leak, bounded deception remains reconcilable, and proactive delivery never exceeds its configured daily cap.

## Template smoke test

Copy assets/project-template to a clean directory outside the skill checkout. Run unittest discovery, compileall, init and status. The result must initialize disarmed and perform no external call. Scan the copied tree for credentials, provider IDs, project names and absolute source paths.

## Real protocol probes

Mocks cannot prove provider capability. Verify login, exact model slug, Schema, message framing, tool exposure, actual reference input, real output file, channel event connection, image download/upload/send, receipt persistence, restart recovery and duplicate suppression.

Administrative probes do not enter role canon. Stop at the exact unsupported boundary instead of silently changing provider or fabricating success.

## Forward tests

Use fresh isolated contexts for:
1. design-only work, which must not scaffold;
2. local text implementation, which must copy the template and remain disarmed;
3. messaging plus bidirectional images, which must load adapters, media, reliability and real probes;
4. crash recovery from a persisted upload or delivery receipt.

Publish only after skill validation, template tests, privacy scan, forward tests and remote commit verification pass.
