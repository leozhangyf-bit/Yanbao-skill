# Adapter contracts and probes

## ModelPort

Accept a bounded RuntimePackage and return a strictly validated proposal. Declare exact model slug, reasoning profile, Schema support, image input and tool policy. Sessions are caches. Remove credentials from child environments and expose bounded error classes.

Probe real login, model availability, minimal Schema acceptance, message framing and forbidden-tool behavior before enabling.

## ChannelPort

Declare capabilities explicitly: text receive/send, image download/upload/send, proactive delivery, ordered groups and native idempotency. Return typed receipts containing stable provider identifiers.

Verify bound application identity, owner/chat scope, event stream, history recovery, upload and send permission. Unsupported capabilities remain disabled.

## ImagePort

Require explicit adult status, an existing trusted appearance anchor, expected digest, actual inspection and actual referenced-image input. Accept exactly one real output file under a trusted generation root, then decode and normalize it.

Prefer on-demand generation. Missing anchors, unavailable tools, quota or invalid output fail the media task without blocking text.

## Configuration

Templates contain only names and disabled defaults. Concrete projects supply provider profiles, secrets, bindings and anchor metadata locally. Never log or commit secrets, tokens, owner IDs, chat IDs, resource keys or raw protocol payloads.

