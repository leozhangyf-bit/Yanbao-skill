---
name: yanbao-skill
description: Design, implement, scaffold, test, deploy, revise, bridge, migrate, govern, and evaluate long-running immersive roleplay systems for original adult women in contemporary settings, including independent fictional offscreen lives, autonomous goals and supporting characters, sparse time progression, relationship and memory architecture, proactive storytelling, complete expressive replies, adaptive reply budgets, model/channel adapters, reliable Windows/Feishu multi-paragraph delivery, privacy-safe bidirectional images, and a safe disarmed Python project template. Use for new character projects, passive-companion diagnosis, life-simulation or proactive-behavior design, coding or deployment, role expression revisions, architecture reviews, runtime compilation, media delivery, reliability diagnosis, or multi-role constellations. Do not use for ordinary in-character conversation or as a per-turn runtime prompt.
---

# Yanbao Skill

Design from first principles. Treat relationship continuity as the product, canonical state as truth, model sessions as caches, and external delivery receipts as evidence. Keep this skill in the control plane; compile a bounded runtime package for conversation agents.

## Route the task

Read each selected reference completely. Load only what the task needs, except always read `evaluation.md` before publishing, accepting a migration, or declaring a live bridge healthy.

- Read [architecture.md](references/architecture.md) for new systems, ownership, versioning, migration, or state-plane review.
- Read [authoring.md](references/authoring.md) for role blueprints, initial situations, agency, hidden facets, or event envelopes.
- Read [life-simulation.md](references/life-simulation.md) for independent offscreen life, goals, supporting actors, sparse wakes, consequences, privacy, deception, disclosure, or proactive motives.
- Read [relationships.md](references/relationships.md) for relationship evolution, memory, consent, private state, romance, or constellations.
- Read [expression.md](references/expression.md) for reply completeness, adaptive length, narration style, user-agency boundaries, or single-versus-multiple message delivery.
- Read [feishu-text-delivery.md](references/feishu-text-delivery.md) for every new character project's expression-and-delivery design, and whenever choosing saturated reply budgets, connecting Windows to Feishu, diagnosing first-paragraph truncation, or verifying that provider-visible text matches the final model draft. Treat its 300–500 normal and 100–200 closing budgets as an optional user-approved profile, not a universal character default.
- Read [runtime.md](references/runtime.md) for context compilation, model profiles, proactive behavior, channels, or cost degradation.
- Read [bridging.md](references/bridging.md) for channel-to-model-to-state paths, identity binding, ordering, or external effects.
- Read [media.md](references/media.md) for user images, visual understanding, role images, appearance anchors, upload, or delivery.
- Read [reliability.md](references/reliability.md) for state machines, idempotency, receipts, recovery, retention, or rollback.
- Read [failure-patterns.md](references/failure-patterns.md) when diagnosing a bridge, model, Schema, tool, upload, or delivery failure.
- Read [implementation.md](references/implementation.md) for build, scaffold, implement, deploy, release, or rollback requests.
- Read [project-structure.md](references/project-structure.md) for code layout, module boundaries, dependency direction, or template specialization.
- Read [persistence.md](references/persistence.md) for database schemas, migrations, transactions, inbox/outbox/media jobs, backup, or recovery.
- Read [adapters.md](references/adapters.md) for model, channel, image, configuration, capability, or real protocol work.
- Read [testing.md](references/testing.md) for offline suites, crash injection, template smoke tests, forward tests, or live release probes.
- Read [evaluation.md](references/evaluation.md) for testing and release gates.

## Preserve the system

- Keep blueprint, role instance, user avatar, relationship, world, private state, append-only events, derived memory, runtime compiler, model adapters, and channel adapters separate.
- Keep role instances isolated by default. Link them only through an explicit constellation and named shared events.
- Preserve independent judgment. Interaction may change relationship behavior and outer personality edges, not silently rewrite core identity.
- Keep life progression separate from conversation and disclosure. A role and supporting actors must act from goals, pressure and consequences without waiting for user prompts.
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
3. Draft the versioned blueprint, sparse life skeleton and isolated fictional worldline; confirm the initial goals, active threads and recurring actors before enabling life progression.
4. Define canonical ownership, visibility, private-event commit, disclosure, event and version semantics.
5. Define persistent wakes, deterministic eligibility and a bounded life-advance proposal. Default to two wake opportunities per local day, zero or one material slice per eligible wake, and no daily backfill.
6. Compile a bounded runtime package and role-specific expression contract; expose prepared content, never discovery paths. Choose one explicit length metric and budget profile. Preserve the reusable content-density and rewrite rules in `feishu-text-delivery.md` without copying another character's voice, pet names, intimacy or joke style.
7. Map logical interactive/background profiles and explicit channel capabilities. For Windows/Feishu text, use the ASCII-safe single-JSON-frame adapter and its multiline Unicode tests from `feishu-text-delivery.md`. Keep optional real-world stimuli disabled unless the project explicitly enables them.
8. Design external effects as durable intent -> effect -> receipt -> canonical commit. Do not require a channel receipt for a validated private offscreen event.
9. Add media only through the privacy, anchor, file, upload and delivery boundaries in `media.md`.
10. Run structural, behavioral, longitudinal, cost, protocol and recovery checks in `evaluation.md`.
11. Publish prospectively. Require explicit patch, retcon, migration, fork, rollback, or compatibility routing for established systems.

For implementation work, continue only after an approved specification and written plan: inspect the target, copy `assets/project-template` without Git metadata, retain its project-local delivery-method document, specialize project-owned blueprint/configuration and expression budget, implement adapters, run offline tests and real probes, back up state, start disarmed, then perform explicit channel acceptance.

## Stop conditions

Stop and report the exact boundary when credentials, permissions, verified model/tool capability, a required reference image, user consent, or a real protocol probe is missing. Do not simulate success, substitute a different provider silently, or write an undelivered effect into canon.
