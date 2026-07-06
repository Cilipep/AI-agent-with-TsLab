---
name: tslab-api-auth
description: "Obtain and use Bearer tokens for TSLab Web API when auth is enabled: handle 401, run CLI browser-handoff flow, and avoid logging secrets. Use for /api auth/JWT token issues."
---

# TSLab Web API: Auth (Bearer)

## Hard Rules

- If any `/api/*` call returns `401`, stop and do the auth flow; do not keep retrying unauthenticated.
- Always send `Authorization: Bearer <token>` on `/api/*` unless trusted clients are explicitly enabled.
- Never log or persist full access tokens.

## Minimal Workflow (CLI)

1. Start CLI session:
   - `POST /api/auth/cli/sessions`
2. User opens `authorizeUrl` in browser and completes login.
3. Poll session:
   - `GET /api/auth/cli/sessions/{sessionId}?secret={secret}`
4. Use the token:
   - `Authorization: Bearer {accessToken}`

## Docs Pointer

- Full CLI flow + troubleshooting: `AGENTS-Auth.md`
