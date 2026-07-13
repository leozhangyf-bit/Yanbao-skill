# Complete and expressive role replies

## Priority order

Design user-visible expression in this order:

1. Answer every important user question or explicitly state why the role cannot answer.
2. Preserve role judgment, knowledge limits, current relationship and user agency.
3. Match length to complexity.
4. Apply the chosen narration and messaging style.

Do not sacrifice conclusions, reasons or necessary detail to imitate short instant messages. A greeting, confirmation or natural close may remain short. A complex, emotional, explanatory or multi-question turn must expand enough to be complete.

## Completeness contract

Compile these behaviors into the trusted interactive prompt and the versioned blueprint expression logic:

- Identify the main request and all important direct questions.
- Cover related questions naturally without requiring numbered answers.
- Do not answer only the final sentence.
- Do not replace an answer with an emotional reaction, rhetorical question or unnecessary request for clarification.
- When information is insufficient or the role is unwilling to answer, say so and identify the missing information or boundary.
- Keep the total output within the verified channel and Schema boundary; treat the maximum as a safety limit, not a target length.

Publish expression changes prospectively by incrementing the blueprint or runtime-rules version and rotating session caches. Do not rewrite canonical history merely to change style.

## Narration contract

When the selected style uses third-person novel narration, let brief narration describe only:

- the role's observable actions, posture, expression or tone;
- established time, place and surroundings supplied in the runtime package;
- outward behavior consistent with current relationship evidence.

Connect narration to substantive dialogue. Narration must not:

- decide the user's actions, feelings, thoughts or reaction;
- invent an uncommitted meeting, touch, promise, crisis, third party or shared event;
- expose the role's complete private state;
- pad length or replace an answer;
- repeat a fixed action-expression-dialogue template in every turn.

Choose frequency explicitly. A useful default for a narration-forward role is one brief grounded beat in non-trivial replies, while pure confirmations and very short greetings may omit it. Serious analysis still keeps the answer as the main content.

## Delivery choice

Default to one complete channel message. This preserves a simple evidence boundary:

```text
complete proposal -> one outbox item -> channel receipt -> canonical commit
```

Use multiple visible messages only when the bridge supports an ordered message group with stable group and part identities, durable per-part receipts, restart recovery, duplicate suppression and a declared commit rule. Otherwise, visual chat rhythm is not worth the risk of sending only the first part of an answer.

## Evaluation set

Add behavioral scenarios for:

- multiple questions: every important question receives a substantive response;
- complex explanation: conclusion, reasons and necessary detail are present;
- grounded narration: narration uses established state, then provides the answer;
- user agency: no action or inner state is assigned to the user;
- proportional greeting: a simple greeting is not expanded into empty prose;
- uncertainty: unknown or refused content is acknowledged without fabrication;
- delivery: length, Schema, idempotency and receipt boundaries remain valid.

Before release, run deterministic prompt/compiler tests, the full offline behavioral suite and a real model probe that is not externally delivered. Inspect the probe for question coverage, proportional length, narration grounding and user-agency violations. Then back up canonical state, restart only the scoped role service, and verify runtime hash/session rotation and channel health.
