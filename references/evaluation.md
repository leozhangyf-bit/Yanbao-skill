# Evaluation and release gates

## Structural checks

Verify explicit adult original roles; distinct ownership for blueprint, instance, relationship, world, private state, events, memory and delivery; default isolation; prospective versions; bounded runtime; explicit capabilities; and no model-owned filesystem or secrets.

## Behavioral and longitudinal checks

Test ordinary talk, silence, disagreement, preference, vulnerability, boundaries, repair, long gaps, lazy life, repeated behavior, session rotation, old-topic retrieval, blueprint patch/retcon/fork, adapter replacement, close cross-channel events and attempted cross-role leakage.

Test expression with at least four distinct cases: a multi-question message covers every important question; a complex question contains a conclusion, reasons and necessary detail; enabled narration remains grounded and does not control the user; a simple greeting stays proportionate. Reject scene description that substitutes for an answer or a fixed action-expression-dialogue template that appears regardless of context.

Judge coherence from values and contradictions, not one expected sentence. Relationship changes cite evidence and preserve core identity.

## Bridge and media checks

- Ordinary text remains available during slow or failed media.
- Provider event redelivery does not duplicate a turn.
- A complete single-message reply is committed only after its channel receipt. If replies use multiple messages, verify ordering, per-part receipts, partial-delivery recovery and the declared group commit boundary.
- Ordinary images normalize, lose metadata, pass the privacy gate and produce bounded observations.
- Risky/uncertain images require an exact task-bound token; wrong tokens authorize nothing.
- Every role image uses the actual canonical reference and explicit adult declaration.
- Generation success means one verified file, not prose.
- An upload crash reuses the persisted resource key.
- A send crash reuses the same key and idempotency identity.
- Caption failure never resends the image.
- No image_shared event exists before a channel message receipt.
- Retention and path-escape protections work.
- Disabling media preserves text and canonical history.

## Real protocol gates

In addition to mocks, verify login, model slug, Schema acceptance, message framing, tool exposure, reference attachment, output file path, upload permission, send permission, message receipt and restart recovery. Keep administrative tests out of role canon unless initiated naturally in-world.

## Skill isolation

Scan the skill for project/person names, user data, conversations, absolute paths, credentials, provider IDs and appearance assets. Forward-test with a neutral new-role seed and a neutral bridge/media request in fresh contexts.

## Release decision

Publish only when structural invariants, behavioral continuity, isolation, bridge receipts, media recovery and real probes pass. Record unsupported capabilities explicitly. Never downgrade providers, fabricate delivery, or hide a failed gate behind prose.
