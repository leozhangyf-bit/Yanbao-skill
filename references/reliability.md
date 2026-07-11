# Reliability and recovery

## State machines

Represent every externally visible workflow as explicit states. Each claim and transition includes the expected old state and must affect exactly one row. Keep attempts, next retry time, bounded error class, expiry, and receipts.

Separate inbound media stages (received, downloaded, validated, risk checked, awaiting confirmation, approved, understood, completed/rejected/expired/failed) from outbound stages (planned, waiting for generation, generated, uploading, uploaded, sending, delivered, committed/failed).

## Idempotency and evidence

Choose stable identities before side effects: provider message plus attachment index for inbound media; job ID and stage for generation; persistent resource key for upload; stable idempotency key for message send.

Persist each external receipt before the next effect. Canon commits occur only at declared evidence boundaries. A successful text receipt cannot prove image delivery.

## Crash recovery

Recover from the latest durable evidence:

- downloaded but unvalidated: validate the same isolated file;
- approved but undescribed: retry restricted vision;
- generated file present: do not regenerate;
- resource key present: do not upload again;
- message receipt present: do not send again;
- committed image: retry only pending caption;
- expired task: send at most the declared fallback and commit no image event.

Use bounded exponential backoff and a terminal expiry. Clear or archive the active error when a task advances successfully so health checks do not report stale failures.

## Isolation, retention and rollback

Text and media workers must fail independently; a stream failure cancels related workers visibly rather than silently dying. Keep raw inbound media briefly, generated outbound media only long enough for retry/audit, and metadata/event receipts per policy.

Provide a reversible media disable switch that preserves text chat and existing tables. Back up canonical state before schema/runtime changes. Rollback must never delete a worldline merely because a newer adapter failed.

