# Bridge architecture

## Boundary rule

A bridge translates identities, capabilities, messages, files and receipts. It never owns role truth and never lets a model directly control provider credentials or side effects.

## Inbound path

```text
channel event
-> verify bot/application identity, owner, chat and capability
-> derive stable provider message/attachment identity
-> durably deduplicate
-> route text or media
-> compile bounded role input
-> validate model proposal
-> stage outbox
-> deliver with stable idempotency identity
-> persist channel receipt
-> commit receipt-backed canonical changes
```

Reject unbound senders, unexpected groups, unsupported message types and malformed resource keys before model calls. Preserve provider event IDs for audit, but deduplicate on stable message identity when providers may redeliver with a new event envelope.

## Outbound path

```text
role motivation or validated media intent
-> durable task
-> infrastructure eligibility and capability check
-> external effect
-> durable provider resource receipt
-> channel delivery
-> durable channel receipt
-> canonical event at its declared evidence boundary
```

Role motivation never equals permission or delivery. Channel adapters expose capabilities and typed receipts. The runtime chooses behavior when a capability is absent; it never pretends support.

## Ordering and concurrency

Serialize canonical turns per role instance. Separate slow media workers from text workers. Use conditional claims so only one worker owns a stage. Cross-channel events share one canonical ordering without letting one channel session become the source of truth.

## Security and observability

Keep credentials in provider profiles or secret stores, never prompts, events or repositories. Production state stores bounded error classes; a privileged diagnostic mode may capture raw protocol output locally with redaction and short retention.

