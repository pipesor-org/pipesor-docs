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
| pipeline → ingestion | `/internal/v1/github/**` (access facts, workflow verification) | `Pipeline.GitHubFacts.Read` + subject token (§4) |
| recommendation → pipeline | `POST /internal/v1/diagnosis-read-entitlements` | `Recommendation.DiagnosisEntitlements.Resolve` + subject token (§4) |
| recommendation → pipeline | `PUT /internal/v1/incidents/{incidentId}/diagnosis-summary` | `Recommendation.DiagnosisSummaries.Write` (ADR-027) |

A route accepts only the callers listed for it. Adding a caller is a contract change.

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
2. `GET /api/v1/auth/github/callback?code&state` consumes the attempt once,
   exchanges the code server-side, verifies the GitHub user (any GitHub user who
   authorizes the App may sign in, ADR-025; repository access is checked per
   repository afterwards), stores the user token in custody, and
   redirects to `<dashboard origin>/auth/complete?handoff=<one-time opaque value>`.
   The handoff value is single-use and expires in 60 s.
3. The dashboard calls `POST /api/v1/auth/session` with `{"handoff": "..."}` and
   receives `{"accessToken", "expiresAt", "user": {"githubUserId", "login"}}`.
4. When the session expires the dashboard repeats step 1. There is no refresh token
   in the browser. `POST /api/v1/auth/logout` invalidates the server-side link
   generation.

Callback and dashboard origins are explicit configuration. Tokens, codes and handoff
values are never logged or placed in fragments.

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

## 7. Keys and JWKS

| Environment | Signing key | Public keys |
|---|---|---|
| Azure | Key Vault RSA key `pipesor-<workload>-signing` (non-exportable); identity has `Key Vault Crypto User` on that key only | `GET /.well-known/jwks.json` on the service |
| Local | PEM file referenced by `PIPESOR_SIGNING_KEY_FILE`, mode 0600 | same route |

Session keys use `pipesor-session-signing`, held by Ingestion. JWKS responses contain
public keys only, are unauthenticated and set `Cache-Control: public, max-age=300`.
Rotation creates a new key version; the JWKS publishes the old and new keys for at
least 15 minutes before the old version is disabled.

Verifier configuration per trusted issuer:

```yaml
pipesor:
  security:
    tenant-id: <uuid>
    audience: urn:pipesor:api:<self>
    trusted-workloads:
      - id: correlation
        jwks-uri: https://correlation.internal.<env-domain>/.well-known/jwks.json
        roles: [Correlation.Contexts.Deliver]
    session:
      jwks-uri: https://ingestion.<env-domain>/.well-known/jwks.json
```

## 8. Transport rule

HTTPS is required. Plain HTTP is accepted for outbound and JWKS URIs only when the
host is `127.0.0.1`, `::1` or `localhost` **and** the `local` profile is active.
Any other combination fails at startup.

## 9. Errors

`401` for missing or invalid tokens, `403` for a valid token without the required
role, scope, caller or resource grant. Bodies are `application/problem+json` without
token details. Both responses set `Cache-Control: no-store`.
