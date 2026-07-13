# Persistence and transaction contract

## Canonical records

Persist blueprint version, role instance, user avatar, relationship/world/private state and append-only events separately. Derived memory and sessions are rebuildable caches.

## Delivery records

Use durable inbox, outbox and media-job records. Assign stable identities before external effects. Store provider resource receipts and channel message receipts as typed text fields; never store image binaries or Base64.

## Transaction rule

Every transition includes an expected old state inside BEGIN IMMEDIATE and requires exactly one affected row. Persist a receipt before the next external effect. Stage candidate events and deltas with the outbox; commit them only after the declared delivery receipt.

## Recovery

On startup:
- return interrupted inbox claims to retryable work;
- retain staged outbox and its idempotency key;
- reuse existing resource/upload receipts;
- never resend an effect with a durable channel receipt;
- retry only caption/fallback when the image is already committed;
- clear or archive active error state after successful progress.

## Migrations and backup

Version schemas monotonically. Back up and run integrity_check before migration or release. Migrations are transactional and preserve unknown/newer state rather than destructively guessing. Restore-check validates a backup without replacing live data. Rollback preserves the event ledger and worldline.

