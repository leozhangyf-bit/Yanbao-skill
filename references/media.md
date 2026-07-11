# Bidirectional media method

## Inbound images

1. Accept only bound users/chats and supported single-image events.
2. Deduplicate by stable message ID plus attachment index.
3. Download to an isolated task directory; reject absolute or parent-escaping output paths.
4. Limit bytes and decoded pixels; accept only declared formats; reject truncation, zero size, animation and multi-frame input.
5. Re-encode to a canonical image and strip EXIF, GPS, comments and unnecessary profiles. Delete the raw download after canonicalization.
6. Before remote full-image vision, combine local layout heuristics with a strongly blurred, low-resolution risk thumbnail.
7. Auto-release only high-confidence ordinary photos. Treat documents/IDs, work/finance, chats/screens and uncertainty as confirmation-required.
8. Bind confirmation to one task and exact short token. Missing or mismatched tokens authorize nothing; cancellation or expiry deletes the image.
9. Send only approved canonical images to a restricted vision profile. Produce factual visible observations without identity, address, health or account-number guesses.
10. Convert the observation into a synthetic user input for the role model. The observation alone is not canon.
11. Enforce a documented retention period and never store image binaries or Base64 in canonical state.

Risk classification reduces accidental disclosure; it cannot guarantee detection. Tell users not to send real unredacted sensitive material.

## Outbound role images

A role turn may propose at most one media intent with scene, framing, wardrobe, mood, post-delivery caption and failure fallback. The ordinary text reply cannot claim generation or delivery.

For every depicted role:

- Verify explicit adult status.
- Require the role-specific canonical appearance reference.
- Verify its path and expected digest in trusted code.
- Inspect the image before generation.
- Pass it as an actual referenced image input; text-only recreation is forbidden.
- Preserve recognizable identity while allowing scene, pose, clothing, expression and lighting changes.
- Stop if the anchor is absent, unreadable or cannot be attached.

Generate only on durable demand. Prefer on-demand invocation to empty periodic polling. Validate a unique real output file under a trusted generation root, decode and normalize it, and record its digest.

## Upload and delivery

```text
validated file
-> upload
-> receive provider resource key
-> persist resource key
-> send image with stable idempotency key
-> receive channel message ID
-> persist receipt
-> commit image_shared
-> send caption independently
```

Reopening after upload reuses the resource key. Reopening after send reuses the same key and idempotency identity. Caption or fallback failure never resends the image. No image receipt means no shared-image event.

