# Authorization For CLI And Agents

Use this file only when the server requires Bearer auth for `/api/*` routes.

## Hard rules

- If any `/api/*` request returns `401`, stop and perform the CLI auth flow.
- Include `Authorization: Bearer <token>` on every protected `/api/*` request.
- Never log or persist full access tokens.
- Verify the callback URL is the localhost auth callback before trusting the browser handoff.

## Trusted localhost mode

Some environments allow trusted localhost clients to call `/api/*` without a Bearer token.
If that mode is enabled, follow the configured trusted-client rule instead of OAuth.
Otherwise expect `401 Unauthorized` without a token.

## Recommended CLI flow

1. `POST /api/auth/cli/sessions`
2. Show the returned `authorizeUrl` to the user.
3. The user completes login in the browser.
4. Poll `GET /api/auth/cli/sessions/{sessionId}?secret={secret}` until the session is completed.
5. Use the returned `accessToken` as a Bearer token.

## Completion checks

- The callback must go to the localhost auth callback route.
- The browser page should briefly show a completion state and then a success state.
- If the session stays pending, inspect the browser network log for the completion request.

## Failure cases

- If the session expires, start a new one.
- If the secret is wrong, the server returns an auth or not-found error.

## Recommended client behavior

- Treat auth as a prerequisite, not as a recoverable retry loop.
- Keep the token in memory unless you have secure storage.
- Mask tokens in logs and user-visible output.