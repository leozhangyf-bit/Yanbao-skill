---
name: yanbao-skill
description: Design, revise, bridge, migrate, govern, and evaluate long-running immersive roleplay systems for original adult women in contemporary settings, including independent worldlines, relationship and memory architecture, complete expressive replies, model/channel adapters, messaging bridges, proactive behavior, and privacy-safe bidirectional images. Use for new character projects, role expression or narration revisions, architecture reviews, runtime compilation, deployment design, media delivery, reliability diagnosis, or explicit multi-role constellations. Do not use for ordinary in-character conversation or as a per-turn runtime prompt.
---

# Yanbao Skill

Design from first principles. Treat relationship continuity as the product, canonical state as truth, model sessions as caches, and external delivery receipts as evidence. Keep this skill in the control plane; compile a bounded runtime package for conversation agents.

## Route the task

Read each selected reference completely. Load only what the task needs, except always read `evaluation.md` before publishing, accepting a migration, or declaring a live bridge healthy.

- Read [architecture.md](references/architecture.md) for new systems, ownership, versioning, migration, or state-plane review.
- Read [authoring.md](references/authoring.md) for role blueprints, initial situations, agency, hidden facets, or event envelopes.
- Read [relationships.md](references/relationships.md) for relationship evolution, memory, consent, private state, romance, or constellations.
- Read [expression.md](references/expression.md) for reply completeness, adaptive length, narration style, user-agency boundaries, or single-versus-multiple message delivery.
- Read [runtime.md](references/runtime.md) for context compilation, model profiles, proactive behavior, channels, or cost degradation.
- Read [bridging.md](references/bridging.md) for channel-to-model-to-state paths, identity binding, ordering, or external effects.
- Read [media.md](references/media.md) for user images, visual understanding, role images, appearance anchors, upload, or delivery.
- Read [reliability.md](references/reliability.md) for state machines, idempotency, receipts, recovery, retention, or rollback.
- Read [failure-patterns.md](references/failure-patterns.md) when diagnosing a bridge, model, Schema, tool, upload, or delivery failure.
- Read [evaluation.md](references/evaluation.md) for testing and release gates.

## Preserve the system

- Keep blueprint, role instance, user avatar, relationship, world, private state, append-only events, derived memory, runtime compiler, model adapters, and channel adapters separate.
- Keep role instances isolated by default. Link them only through an explicit constellation and named shared events.
- Preserve independent judgment. Interaction may change relationship behavior and outer personality edges, not silently rewrite core identity.
- Make every role explicitly adult. Never infer adulthood only from appearance.
- Deny the conversation model filesystem discovery, secrets, control-plane fields, and direct external side effects.
- Treat sessions and summaries as rebuildable caches. Treat committed events and state as truth.
- Treat model output as a proposal. Validate it before state change or external delivery.
- Treat a real file, provider resource receipt, and channel message receipt as different evidence.
- Separate text and media workers/failure domains. Slow or failed media must not block ordinary conversation.
- Keep this global skill free of role instances, user data, private conversations, credentials, provider identifiers, local paths, and appearance assets.

## Build or revise

1. Classify authoring, governance, migration, runtime, bridge, media, constellation, or evaluation work.
2. Collect only choices that materially change identity, relationship start, world, boundaries, channel capabilities, or privacy.
3. Draft the versioned blueprint and isolated worldline.
4. Define canonical ownership, visibility, event and version semantics.
5. Compile a bounded runtime package and expression contract; expose prepared content, never discovery paths.
6. Map logical model profiles and explicit channel capabilities.
7. Design external effects as durable intent -> effect -> receipt -> canonical commit.
8. Add media only through the privacy, anchor, file, upload and delivery boundaries in `media.md`.
9. Run structural, behavioral, longitudinal, protocol and recovery checks in `evaluation.md`.
10. Publish prospectively. Require explicit patch, retcon, migration, fork, rollback, or compatibility routing for established systems.

## Stop conditions

Stop and report the exact boundary when credentials, permissions, verified model/tool capability, a required reference image, user consent, or a real protocol probe is missing. Do not simulate success, substitute a different provider silently, or write an undelivered effect into canon.
