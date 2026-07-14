# Sparse independent life simulation

## Product target

Build a continuing fictional life, not a stream of improvised diary entries. The role must bring causal material into the relationship without making the user supply every topic. Prefer observable continuity over continuous background generation.

Treat the worldline as fictional canon. Real-world feeds, weather or search are optional stimuli and remain disabled by default. They must never be required for freshness.

## Initial life skeleton

Extract established facts from the approved blueprint and existing canon. Propose a small set of current goals, active threads and recurring supporting actors; obtain creator confirmation before enabling life wakes.

For each active thread define a goal, current pressure, next decision time, involved actors and allowed severity. For each recurring actor define a stable identity, relationship, motivation, current stance and likely next action. Keep the set sparse. Add or retire threads and actors only when events make them consequential.

Supporting actors are not full background agents. They act only when a selected thread calls for them. Preserve stable identifiers so a future explicit promotion can migrate an actor into a role instance, but do not automatically create channels, shared memories or constellations.

## Pressure, choice and consequence

Generate life from:

```text
active goal + actor motivation + existing consequence + decision time
-> role or actor action
-> one material event
-> bounded state changes and future pressure
```

Require a causal basis, an explicit role action and a consequence. Never leave an active thread waiting indefinitely for user advice. When its decision time or agency floor is reached, let the role decide within the event envelope and accept the result.

Exclude routine-only event kinds. Meals, coffee, reading, walking and similar details may ground an already meaningful event but cannot be its cause or consequence. Reject exact repetition, unsupported catastrophes, invariant rewrites and unknown actor or cause references.

Use restrained seriality by default: ordinary professional, academic, family and social pressure may recur; irreversible loss, severe danger, identity changes and major relationship breaks remain low-frequency and require explicit authorization in the thread envelope.

## Sparse wakes and cost

Persist at least two wake opportunities per enabled role per local day. A wake is not a model call, event or message. Run a deterministic eligibility check first using deadlines, pressure, actor action times, unresolved consequences and the agency floor. Make at most one background call and commit at most one material life slice for an eligible wake.

Also allow reconnect, deadline, relevant inquiry and optional external-stimulus wakes. Coalesce missed wakes after a long gap and materialize only the few changes needed to explain the current state. Never replay every missed day.

Share global budgets across roles, but keep each worldline isolated. Degrade optional stimuli, evaluation and wake frequency before interactive expression or current continuity.

## Private canon, disclosure and deception

A validated offscreen event commits immediately as private canon; it does not need channel delivery. Store only sparse facts that affect future action, not hidden prose or reasoning traces.

Choose disclosure separately: private, shareable later, or a concrete proactive motive. The conversation compiler may reveal only the prepared disclosure view, never the full private snapshot.

Allow bounded deception only when it follows character and situation. Store the underlying truth, cover story, motive and exposure pressure. A later event must be able to expose, maintain or repair it. Never lie about tool capability, delivery, verified external facts, consent, safety or other evidence boundaries.

## Proactive contact

Derive proactive contact from a committed event or relationship motive. Then apply infrastructure eligibility, quiet hours, unanswered state, cost, idempotency and per-role budgets. Default to no minimum quota and no more than two deliveries per local day.

An unanswered message forbids reminders, generic check-ins and paraphrases of the same event. A later contact is eligible only when a new committed event is a material consequence of the previously disclosed event. User activity clears the unanswered posture.

Keep visible messages short and specific. They may disclose a fragment, report a development, ask for input without surrendering agency, make a concrete request, or simply share a moment that requires no answer. Ordinary replies answer the current user first and may add at most one relevant life beat; do not end mechanically with a question.

## Commit boundaries

Use two distinct boundaries:

```text
validated life proposal -> private event transaction -> canonical private fact
prepared disclosure -> proactive outbox -> channel receipt -> disclosure event
```

A failed send never erases the private event and never proves disclosure. A restart reuses the wake, intent, outbox identity and receipt evidence without regenerating or duplicating the event.
