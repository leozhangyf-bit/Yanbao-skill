# Architecture contract

## First principles

- Optimize for a continuous relationship, not an isolated convincing response.
- Make ownership explicit. A model session is a cache, never canonical identity or history.
- Separate authored truth, mutable state, observed events, derived summaries, and delivery infrastructure.
- Prefer observable continuity over continuous simulation.
- Preserve reversibility through blueprint versions, append-only events, and explicit retcons.
- Keep roles isolated even when infrastructure, caches, or budgets are shared.
- Keep external effects outside canon until durable receipts prove delivery.

## Planes

### Control plane

Create, inspect, version, migrate, evaluate, publish, roll back, or explicitly connect roles. Never expose control fields in immersive conversation.

### Canonical state plane

Own the model-independent blueprint, role instance, user avatar, world, relationship, private state, event ledger, and constellation membership.

### Derived state plane

Build hot snapshots, cold indexes, topic summaries, retrieval candidates, runtime bundles, and research packets. Rebuild these from canonical state when possible.

### Runtime plane

Serialize turns per instance, compile bounded context, call logical model profiles, validate proposals, stage delivery, and commit only receipt-backed facts.

### Infrastructure plane

Own channel identities, model adapters, media generation, scheduling, caches, observability, provider resources, and delivery receipts. Infrastructure can coordinate without sharing role content.

## Conceptual contracts

- **RoleBlueprint:** versioned identity, explicit adult status, values, contradictions, agency floor, life skeleton, staged facets, growth boundary, reality contract, event envelope and invariants.
- **RoleInstance:** isolated worldline with user avatar, state versions, event cursor, bindings, profiles and optional constellation.
- **RelationshipState:** evidence-linked dimensions, milestones, preferences, tensions, repair, consent and proactive posture.
- **WorldState:** time anchor, location, sparse people/places/routines, ongoing threads and materialized events.
- **PrivateState:** sparse unspoken attitudes, intentions and tensions; never full reasoning traces.
- **LifeThread:** a current goal under pressure, with involved actors, a next decision time, an event envelope and unresolved consequences.
- **SupportingActor:** a stable sparse person with relationship, motivation, stance and next likely action; not an always-running agent.
- **LifeWake:** a durable opportunity to evaluate progression; never synonymous with a model call, event or message.
- **EventRecord:** append-only fact with source, visibility, canon status, consequence and supersession links.
- **MemoryView:** derived hot snapshot and cold retrieval archive; retrieval never changes canon.
- **RuntimePackage:** bounded static bundle, current snapshot, relevant retrieval and optional verified facts.
- **ChannelBinding:** maps an instance to an identity and explicit capabilities; channels never own truth.
- **DeliveryRecord:** durable intent, idempotency identity, effect state and provider/channel receipt.
- **ProactiveIntent:** a committed role motive derived from a private event, still subject to channel eligibility and delivery evidence.
- **RelationshipConstellation:** explicit membership and shared events without merging private or bilateral state.

## Event and version semantics

Use private, bilateral and named-constellation visibility. Distinguish candidate, staged-for-delivery, committed, and withdrawn/superseded events. A user-visible event commits only at its declared evidence boundary.

Apply blueprint changes prospectively. Use explicit patch, retcon, migration, fork and rollback operations. A model or channel adapter change must preserve world facts.

Commit a validated offscreen event as private canon in its own transaction. Commit its disclosure only after a channel receipt. Delivery failure changes what the user knows, not what happened in the role's life.

## Normal turn

1. Resolve channel identity to one role instance.
2. Durably deduplicate and serialize the event.
3. Compile cached state plus bounded relevant context.
4. Ask the interactive profile for reply and proposed changes.
5. Validate content, visibility, blueprint permissions and media intent.
6. Stage the reply and proposals in an outbox transaction.
7. Deliver through the channel using a stable idempotency identity.
8. Persist the receipt.
9. Commit the events/state whose evidence boundary is that receipt.
