# Implementation workflow

## Entry gate

Use this workflow only when the user asks to build, implement, scaffold, connect, test, deploy or operate a role project. For design-only requests, produce the approved specification and stop before copying code.

## Phases

1. Inspect the target directory, existing files, repository state and project instructions.
2. Produce and obtain approval for a role/system specification.
3. Write a task-level implementation plan with exact files, contracts and tests.
4. Copy assets/project-template into an approved empty or reviewed target. Never copy its Git metadata.
5. Rename the generic package only when the project naming convention requires it.
6. Create project-owned blueprint, appearance anchor metadata and configuration schema. Keep them outside this global skill.
7. Implement provider adapters behind the template ports. Probe capabilities before enabling them.
8. Run offline contract, persistence, recovery, privacy and concurrency tests.
9. Run real protocol probes without writing administrative traffic into role canon.
10. Back up canonical data, verify integrity, start disarmed, then arm only with explicit confirmation.
11. Perform channel acceptance, record the release and preserve rollback instructions.

## Safety defaults

The template is not production-ready until real adapters and probes pass. It starts disarmed, contains no provider credentials or identifiers, creates no autostart entry and performs no network effects. Unsupported capabilities remain disabled rather than simulated.

## Completion

A project is complete only when canonical state ownership, runtime compilation, provider capability, durable receipts, recovery, privacy, backup, rollback and live acceptance are verified. Model prose cannot replace a file, provider receipt or channel receipt.

