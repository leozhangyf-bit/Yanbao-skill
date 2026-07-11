# Failure patterns and diagnostic probes

## Diagnose by boundary

Determine whether the event was received, claimed, model-called, validated, staged, uploaded, sent, receipt-persisted or canon-committed. Inspect the narrowest relevant state before restarting. Never infer “not received” merely from “no reply.”

## Schema failure

Some structured-output endpoints reject `const` without an explicit `type`. Validate the exact Schema against the real endpoint with a minimal probe. Unit parser tests are insufficient.

## Message framing failure

Some bridge commands interpret embedded newlines as multiple messages and complete only the first. Observe the raw user-message event. When the API expects one argument/message, normalize trusted prompt whitespace into one frame and test that the final instruction arrived.

## Tool-rule conflict

“Read the skill and inspect the reference” conflicts with “use no other tool.” Name allowed read-only prerequisites, require exactly one generation call, and forbid only unrelated mutating/network tools. Confirm tool exposure in a real run.

## Redaction versus diagnosis

Production records should retain bounded error classes, not secrets, prompts or raw provider output. Provide an isolated, privileged probe that captures raw events locally, filters relevant errors/tool calls, has short retention, and never writes role canon.

## Mock-real gap

Before release, probe real login, exact model slug, structured Schema acceptance, tool availability, reference attachment, actual output file, resource upload, message send and receipt persistence. A mock success cannot establish provider capability.

## Stale errors and retry loops

Clear/archive active errors after successful progress. Bound retries and expiry. Prefer on-demand generation over empty periodic polling that consumes quota without work.

## Credential exposure

Treat any credential pasted into chat, logs or source as compromised. Rotate it, update the secret profile, and scan history/artifacts before publication. Never echo secrets in reports.

