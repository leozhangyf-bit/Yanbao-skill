# Project structure and dependency direction

## Layers

### Domain

Own immutable contracts and model-independent concepts: blueprint versions, role instances, user avatars, events, relationship/world/private state and delivery receipts. Domain imports no provider, database, subprocess or filesystem implementation.

### Application

Own RuntimePackage compilation, turn orchestration, media pipelines, validation and recovery policies. Depend on domain contracts and typed ports only.

### Infrastructure

Implement SQLite stores, model adapters, channel adapters, image adapters, media files and configuration loading. Translate provider payloads into domain types and bounded error classes.

### Entrypoints

Own CLI parsing, dependency assembly, service lifecycle and operator commands. Do not contain relationship or provider logic.

## Default tree

    schemas/
    src/<project_package>/
      contracts.py
      ports.py
      schema.sql
      store.py
      service.py
      cli.py
    tests/
    runtime_profile/
    assets/<role-name>/
    data/

Blueprints, anchors, databases, logs and local configuration belong to the concrete project, never the skill template.

## Dependency rules

- contracts.py uses the standard library only.
- ports.py depends on contracts.
- store.py implements persistence without importing model/channel implementations.
- service.py depends on ports and store interfaces.
- cli.py assembles concrete dependencies and exposes safe operator commands.
- Provider-specific modules may depend inward; inward modules never import them.

Keep files focused. Split media, runtime compilation and provider implementations when they become non-trivial rather than growing one service module.

