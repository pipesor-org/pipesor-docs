# Platform identity contract v1

Status: approved MVP contract under [ADR-022](../decisions/ADR-022-platform-identity-without-entra-app-registrations.md).
Applies to every Pipesor HTTP API in local and Azure environments.

All tokens are compact JWS, `alg=RS256`, RSA ≥ 2048 bits, with a `kid` header that
resolves in the issuer's JWKS. Verifiers reject `alg=none`, symmetric algorithms,
unknown `kid` after one JWKS refresh, missing `exp`/`iat`/`nbf`, and clock skew above
60 seconds.

## 1. Identifiers

| Value | Rule |
|---|---|
| Tenant `tid` | Deployment value `PIPESOR_TENANT_ID` (UUID). One per environment. |
| Workload `oid` = `azp` | UUIDv5, URL namespace, name `urn:pipesor:v1:workload:<workload-id>`. |
| Dashboard client `azp` | UUIDv5, URL namespace, name `urn:pipesor:v1:client:dashboard` = `777ec465-1e81-5415-8dd4-c34c64d038e9`. |
| Human `oid` | UUIDv5, URL namespace, name `urn:pipesor:v1:github-user:<numeric GitHub user id>`. |
| API audience | `urn:pipesor:api:<workload-id>` |
| Workload issuer | `urn:pipesor:workload:<workload-id>` |
| Session issuer | `urn:pipesor:session` (keys published by Ingestion) |

| Workload id | `oid`/`azp` |
|---|---|
| `ingestion` | `80cd5bc2-abc2-5171-b8bc-b9c6b846610e` |
| `pipeline` | `272263cd-a442-5ddc-a58a-64a8bb61734d` |
| `log-event` | `b0b9b288-0e8f-566e-985e-4d2e685dd827` |
| `nlp` | `7c3b75a2-74cf-59a0-babf-1c0415d48762` |
| `correlation` | `e790fc63-c636-5471-b10f-8dd0b9733fe5` |
| `recommendation` | `970e0ca6-7657-5cc0-a671-ee41c78a5214` |
| `rag` | `bf0e7005-d464-528d-ba1b-97439ea01dab` |

## 2. Workload tokens

Issued by the calling service for exactly one target audience and one role.

| Claim | Value |
|---|---|
| `iss` | `urn:pipesor:workload:<caller>` |
| `aud` | single string `urn:pipesor:api:<target>` |
| `tid` | environment tenant |
| `oid`, `azp`, `sub` | caller workload UUID |
| `roles` | array with exactly one role from the catalog below |
| `idtyp` | `app` |
| `ver` | `2.0` |
| `iat`, `nbf`, `exp` | `exp - iat` ≤ 300 s |
| `jti` | random UUID |

`scp` must be absent. Callers cache a token until 60 s before expiry.

### Route catalog

| Caller → target | Route | Role |
|---|---|---|
| nlp → correlation | `POST /internal/v1/processed-evidence` | `Nlp.ProcessedEvidence.Send` |
| correlation → pipeline | `POST /internal/v1/evidence/operational-reference-checks` | `Correlation.OperationalReferences.Check` |
| log-event → pipeline | `POST /internal/v1/evidence/operational-reference-checks` | `Evidence.Check` |
| correlation → log-event | `POST /internal/v1/evidence/membership-checks` | `Correlation.EvidenceMembership.Check` |
| correlation → recommendation | `POST /internal/v1/correlated-contexts` | `Correlation.Contexts.Deliver` |
| recommendation → rag | `POST /internal/v1/retrieval/query` | `Rag.Query` |
| pipeline → ingestion | `POST /internal/v1/capture/machine-scope-checks` | `Pipeline.MachineScope.Check` |
| pipeline → ingestion | `PUT /internal/v1/capture/workflow-scopes/{repositoryId}/{workflowId}` | `Pipeline.CaptureScope.Write` (ADR-023) |
| pipeline → ingestion | `POST /internal/v1/github/access-verifications` (access facts) | `Pipeline.GitHubFacts.Read` + subject token (§4) |
| pipeline → ingestion | `POST /internal/v1/github/workflow-verifications` (workflow verification, operation `REGISTER` only) | `Pipeline.GitHubFacts.Read` + subject token (§4) |
| recommendation → pipeline | `POST /internal/v1/diagnosis-read-entitlements` | `Recommendation.DiagnosisEntitlements.Resolve` + subject token (§4) |
| recommendation → pipeline | `PUT /internal/v1/incidents/{incidentId}/diagnosis-summary` | `Recommendation.DiagnosisSummaries.Write` (ADR-027) |

A route accepts only the callers listed for it. Adding a caller is a contract change.

Known divergence (audit 2026-11-24): `Evidence.Check` (log-event → pipeline) does not follow
the `<Caller>.<Resource>.<Action>` naming of the other roles; code, local stack and IaC use it
consistently — pending owner decision.

### Owner checks

`POST /internal/v1/evidence/operational-reference-checks` (Pipeline) and
`POST /internal/v1/evidence/membership-checks` (Log/Event) are bounded read-only checks with
the same wire rules: exactly one `X-Correlation-Id` (`[A-Za-z0-9._:-]{1,128}`) equal to the
body `correlationId`; `Content-Type: application/json` (UTF-8 only); no `Content-Encoding`
other than `identity`, no query string and no `Cookie`; a JSON object with exactly the listed
fields (missing, unknown or duplicate fields are `400`); canonical, non-nil UUIDs;
`deadlineAt` in UTC (`Z`). The effective deadline is the earliest of `deadlineAt`, the caller token's `exp` and the
server budget.

| Route | Request fields | `decision` |
|---|---|---|
| `operational-reference-checks` | `requestId`, `correlationId`, `deadlineAt`, `tenantId`, `githubAccountId`, `githubInstallationId`, `githubRepositoryId`, `githubWorkflowId`, `scopeRevision`, `githubRunId`, `runAttempt` (integer), `pipelineId`, `executionId`, `incidentId` | `AUTHORIZED`: Ingestion's machine-scope check admits the scope and the stored pipeline, execution and incident match (the execution failed and is the incident's `ORIGIN`). `DENIED`: the machine scope is refused. `MISMATCH`: the ids are not the deterministic ones or contradict stored references. `NOT_READY`: pipeline, execution or incident is not stored yet. |
| `membership-checks` | `requestId`, `correlationId`, `deadlineAt`, `evidenceId`, `executionId`, `incidentId`, `source` (`github_actions`), `tenantId`, `githubInstallationId`, `scopeRevision` | `AUTHORIZED`: the evidence is stored with that scope, execution, incident and source. `MISMATCH`: same, with another source. `NOT_READY`: no such evidence for that scope, execution and incident. `DENIED`: `tenantId` is not the environment tenant. |

`200` returns `{"requestId", "correlationId", "decision"}`. Errors are
`application/problem+json` with `code`: `400 INVALID_REQUEST`, `413 REQUEST_TOO_LARGE`
(configured byte limit), `415 UNSUPPORTED_MEDIA_TYPE`, `429 OVERLOADED` (in-flight limit) and
`503 UNAVAILABLE` (dependency failure, exhausted deadline or expired caller token). All
responses set `Cache-Control: no-store`. `NOT_READY` and `503` are transient: Log/Event
abandons the message for redelivery and Correlation answers NLP `503 UNAVAILABLE`. `DENIED`
and `MISMATCH` are final: Log/Event dead-letters the message and Correlation answers
`RESOURCE_DENIED` (status configurable, `422` by default) or `400 REFERENCE_MISMATCH`. Neither check receives the source locator,
which is provenance, not authorization ([protected evidence 2.1](protected-evidence-v2.1.md)).

## 3. Session tokens (human)

Issued by Ingestion after the GitHub OAuth flow in §5.

| Claim | Value |
|---|---|
| `iss` | `urn:pipesor:session` |
| `aud` | array: `urn:pipesor:api:ingestion`, `urn:pipesor:api:pipeline`, `urn:pipesor:api:log-event`, `urn:pipesor:api:recommendation` |
| `tid` | environment tenant |
| `oid`, `sub` | human UUID (GitHub user) |
| `azp` | dashboard client UUID |
| `scp` | `GitHub.Self Pipeline.Access Evidence.Read Diagnosis.Read Diagnosis.Review` |
| `github_user_id` | numeric GitHub user id (string) |
| `ver` | `2.0` |
| `iat`, `nbf`, `exp` | `exp - iat` ≤ 3600 s |
| `jti` | random UUID |

`idtyp` and `roles` must be absent. Each API checks that its own audience is present
and that the required scope is in `scp`. The token proves who the user is; every
protected request still applies ADR-020's grant and current GitHub access checks.

Required scope per API: Ingestion `GitHub.Self` (`POST /api/v1/auth/logout` and
`/api/v1/github/**`); Pipeline `Pipeline.Access` (`/api/v1/**`); Recommendation
`Diagnosis.Read` for reads and `Diagnosis.Review` for
`POST /api/v1/diagnoses/{diagnosisId}/reviews`. Routes are detailed in the
[MVP HTTP API v1](mvp-http-api-v1.md). In the MVP no route requires `Evidence.Read` or the
`urn:pipesor:api:log-event` audience, because Log/Event exposes no human API; both remain
in the token as reserved values.

## 4. Subject tokens

When a workload acts for a user, it sends its workload token in `Authorization` and
the user's unmodified session token in `X-Pipesor-Subject-Token`. The target validates
both: the workload token per §2 and the session token per §3 with its own audience.
The subject is the session `oid`. A subject token is never accepted alone. It may be
forwarded only to the owner of the facts the target needs and only along these paths:
dashboard → Pipeline → Ingestion, dashboard → Recommendation → Pipeline, and
Recommendation → Pipeline → Ingestion (Pipeline resolving GitHub facts for a diagnosis
entitlement). Each hop presents its own workload token; the session token is never
modified and its audiences limit where it is accepted.

## 5. Login flow (Ingestion)

1. `GET /api/v1/auth/github/start?return_to=<allowed dashboard path>` creates a
   one-time attempt (random `state`, PKCE S256 verifier kept server-side, 10 min
   expiry) and redirects to GitHub's authorize URL for the App's client id.
   `return_to` is optional (default `/`) and must match
   `^/(?!/)[A-Za-z0-9/_.~-]{0,255}$`; an invalid value returns `400 INVALID_REQUEST`
   without redirecting.
2. `GET /api/v1/auth/github/callback?code&state` consumes the attempt once,
   exchanges the code server-side, verifies the GitHub user (any GitHub user who
   authorizes the App may sign in, ADR-025; repository access is checked per
   repository afterwards), stores the user token in custody, and
   redirects to `<dashboard origin>/auth/complete?handoff=<one-time opaque value>`.
   The handoff value is single-use and expires in 60 s. On failure it redirects to
   `<dashboard origin>/auth/complete?error=<code>`, where `code` is `invalid_state`,
   `access_denied` or `unavailable`.
3. The dashboard calls `POST /api/v1/auth/session` with `{"handoff": "..."}` and
   receives `{"accessToken", "expiresAt", "user": {"githubUserId", "login"}, "returnTo"}`
   with `Cache-Control: no-store`; `returnTo` is the path validated in step 1. An
   unknown, used or expired handoff is `400 INVALID_HANDOFF`, a malformed body
   `400 INVALID_REQUEST` and a storage or link failure `503 LOGIN_UNAVAILABLE`.
4. When the session expires the dashboard repeats step 1. There is no refresh token
   in the browser. `POST /api/v1/auth/logout` (session with `GitHub.Self`) invalidates
   the server-side link generation and returns `204`. It does not revoke the session
   token, which stays valid until `exp` (there is no revocation list, ADR-022);
   requests that need the user's GitHub link fail from then on.

Callback and dashboard origins are explicit configuration. Tokens, codes and handoff
values are never logged or placed in fragments.

Known divergence (audit 2026-11-24): ADR-022 keeps browser tokens in memory; the
dashboard also stores the session in the tab's `sessionStorage`, so it survives reloads
of that tab — pending owner decision.

## 6. GitHub Actions OIDC tokens

Accepted only by Recommendation's report route.

| Check | Value |
|---|---|
| `iss` | `https://token.actions.githubusercontent.com` |
| JWKS | `https://token.actions.githubusercontent.com/.well-known/jwks` |
| `aud` | `urn:pipesor:api:recommendation` |
| `repository_id` | must equal the path repository and a registered Pipesor repository |
| `repository_owner_id` | must equal an admitted installation account |

The workflow requests the token with `permissions: id-token: write`.

Known divergence (audit 2026-11-24): the report route
(`GET /api/v1/github-actions/repositories/{repositoryId}/runs/{runId}/attempts/{attempt}/report`)
compares `repository_id` with the path but validates `repository_owner_id` only as a
positive decimal, without comparing it with an admitted installation account; the
registered repository is implied by an admitted diagnosis for it; tokens with a lifetime
up to 1 h are accepted and `nbf` is not required — pending owner decision.

## 7. Keys and JWKS

| Environment | Signing key | Public keys |
|---|---|---|
| Azure | Key Vault RSA key `pipesor-<workload>-signing` (non-exportable), referenced with its version by `PIPESOR_SIGNING_KEY_ID`; identity has `Key Vault Crypto User` on that key only | `GET /.well-known/jwks.json` on the service |
| Local | PKCS#8 PEM file referenced by `PIPESOR_SIGNING_KEY_FILE`, mode 0600 or 0400, accepted only with the `local` profile | same route |

Session keys use `pipesor-session-signing` (`PIPESOR_SESSION_SIGNING_KEY_ID`, or
`PIPESOR_SESSION_SIGNING_KEY_FILE` locally), held by Ingestion. JWKS responses contain
public keys only, are unauthenticated and set `Cache-Control: public, max-age=300`.
Rotation creates a new key version; the JWKS publishes the old and new keys for at
least 15 minutes before the old version is disabled.

Known divergence (audit 2026-11-24): each service signs with one pinned key version and
its JWKS publishes only the keys it loaded; IaC pins the version and rotates by
redeploying a single replica, so the old key is not published for 15 minutes and tokens
signed with it are rejected at once — pending owner decision.

Known divergence (audit 2026-11-24): IaC and the local stack also provision a signing key
for `rag`, which issues no tokens and publishes no JWKS. Ingestion issues no workload
tokens, and its JWKS publishes its workload key together with the session key, so session
verifiers accept either — pending owner decision.

Known divergence (audit 2026-11-24): IaC gives every Container App a user-assigned managed
identity (`id-pipesor-<env>-<workload>`, selected through `AZURE_CLIENT_ID`), while ADR-021
and the [RAG integration contract v0.1](rag-integration-v0.1.md) require RAG's
system-assigned identity for its Foundry access — pending owner decision.

Service configuration (Java services bind it from environment variables such as
`PIPESOR_TENANT_ID` or `PIPESOR_SECURITY_TRUSTEDWORKLOADS_<n>_{ID,JWKSURI,ROLES}`; the
Python services read the variables they need; see the
[runtime manifest](../../development/runtime-manifest.md)):

```yaml
pipesor:
  workload-id: <self>
  tenant-id: <uuid>
  signing-key-file: <pem path>        # local profile; or
  signing-key-id: <Key Vault key URI with version>   # azure
  security:
    audience: urn:pipesor:api:<self>
    clock-skew: 60s                   # optional, at most 60 s
    trusted-workloads:
      - id: correlation
        jwks-uri: https://correlation.internal.<env-domain>/.well-known/jwks.json
        roles: [Correlation.Contexts.Deliver]
    session:
      jwks-uri: https://ingestion.<env-domain>/.well-known/jwks.json
```

Exactly one of `signing-key-file` and `signing-key-id` is set. Recommendation also reads
`pipesor.security.github-actions.jwks-uri` (default: the §6 JWKS).

## 8. Transport rule

HTTPS is required. Plain HTTP is accepted for outbound and JWKS URIs only when the
host is `127.0.0.1`, `::1` or `localhost` **and** the `local` profile is active.
Any other combination fails at startup.

## 9. Errors

`401` for missing or invalid tokens, `403` for a valid token without the required
role, scope, caller or resource grant. Bodies are `application/problem+json` without
token details. Both responses set `Cache-Control: no-store`.

Known divergence (audit 2026-11-24): Ingestion and Recommendation answer `400`
(`INVALID_REQUEST`, `invalid_request`) to a duplicated or malformed `Authorization`
header, and the `code` of `401`/`403` differs per service (`UNAUTHENTICATED`/`DENIED` in
Ingestion, `UNAUTHENTICATED`/`ACCESS_DENIED` in Pipeline, `unauthenticated`/`forbidden` in
Recommendation, none in RAG) — pending owner decision.

## 10. Routes without platform tokens

Only these routes accept requests without a platform token: liveness and readiness
health (`/actuator/health/liveness` and `/actuator/health/readiness` in Java services,
`/health/live` and `/health/ready` in Python services), `GET /.well-known/jwks.json`,
steps 1–3 of §5, CORS preflight requests on `/api/v1/**` and, in the `local` profile
only, the OpenAPI document. Spring's `/.well-known/oauth-protected-resource` metadata is
not exposed. Ingestion's `POST /webhooks/v1/github/workflow-runs` is authenticated with
GitHub's webhook signature (`X-Hub-Signature-256`), not with platform tokens, and exists
only when the webhook is enabled (`PIPESOR_GITHUB_WEBHOOK_ENABLED`). Every other route is
denied unless this contract allows it.
