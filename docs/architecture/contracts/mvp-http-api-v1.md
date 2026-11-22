# MVP HTTP API v1

Status: approved MVP contract for the dashboard and the GitHub Actions report.
Authentication follows the [platform identity contract v1](platform-identity-v1.md).
It resolves, for the MVP, the read contract left open by PD-011/PD-034 within the
guarantees recorded in [pending decisions](../pending-decisions.md).

## Conventions (all services)

- JSON over HTTPS, UTF-8. Errors use `application/problem+json` with `type`, `title`,
  `status`, `code` and `correlationId`; no stack traces, tokens or internal messages.
- Every request may send `X-Correlation-ID` (`[A-Za-z0-9._:-]{1,128}`); the service
  echoes it or generates one.
- Every authenticated response sets `Cache-Control: no-store`.
- Lists use `?pageSize=` (1–100, default 24) and an opaque `?pageToken=`; responses
  return `items` and `nextPageToken` (nullable). Authorization filters are applied
  before paging (ADR-020).
- CORS allows only the configured dashboard origin, methods in use, headers
  `Authorization`, `Content-Type`, `X-Correlation-ID`; no credentials mode.
- Each service exposes its OpenAPI document at `/v3/api-docs` (Java) or
  `/openapi.json` (Python) in the `local` profile. Existing routes keep their
  current shapes; this document lists them and defines the new ones.

## Ingestion — authentication and GitHub discovery (external ingress)

| Method and route | Scope | Status | Notes |
|---|---|---|---|
| `GET /api/v1/auth/github/start?return_to=` | none | new | §5 of the identity contract |
| `GET /api/v1/auth/github/callback` | none | new | redirects to the dashboard |
| `POST /api/v1/auth/session` | none | new | `{handoff}` → `{accessToken, expiresAt, user, returnTo}`; the callback redirects with `?error=<code>` on failure |
| `POST /api/v1/auth/logout` | `GitHub.Self` | new | 204 |
| `GET /api/v1/github/connection` | `GitHub.Self` | existing | |
| `DELETE /api/v1/github/connection` | `GitHub.Self` | existing | |
| `GET /api/v1/github/repositories?limit=&cursor=` | `GitHub.Self` | existing | admitted + readable only; `limit` required |
| `GET /api/v1/github/repositories/{repositoryId}/workflows?limit=&cursor=` | `GitHub.Self` | existing | `limit` required |
| `GET /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs?conclusion=failure` | `GitHub.Self` | new | `items[]: {runId, attempt, conclusion, headBranch, headSha, createdAt, htmlUrl}` |
| `POST /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs/{runId}/attempts/{attempt}/analysis` | `GitHub.Self` | generalized | replaces the configured single run; requires OPERATE conditions of ADR-020; returns `202 {analysisId, phase}` and only records durable intent |
| `GET /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs/{runId}/attempts/{attempt}/analysis` | `GitHub.Self` | existing (pilot) | `{analysisId, phase: ACCEPTED|PREPARING|PUBLISHED|BLOCKED, blockedReason?, executionId?, incidentId?}` |

`executionId` and `incidentId` are the deterministic Pipeline identifiers derived from
the same repository, workflow, run and attempt, so the dashboard can navigate without
asking for internal UUIDs.

## Pipeline — operations (external ingress)

Existing routes (`/api/v1/pipelines`, `/pipelines/{id}`, `/pipelines/{id}/executions`,
`/pipelines/{id}/incidents`, `/executions/{id}`, `/executions/{id}/stages`,
`/incidents/{id}`, `/incidents/{id}/runs`, settings, policy, ownership, grants and
incident lifecycle commands) keep their shapes and require `Pipeline.Access`.

New:

| Method and route | Notes |
|---|---|
| `GET /api/v1/incidents?state=OPEN|NEEDS_VALIDATION|RESOLVED` | cross-pipeline queue for Operations, filtered by VIEW grants and current GitHub access before paging; removes the per-pipeline N+1 fan-out |

`POST /api/v1/pipelines` performs real registration: GitHub facts come from Ingestion
(`Pipeline.GitHubFacts.Read` + subject token), never from the browser.

## Recommendation — diagnosis, review and report

| Method and route | Auth | Status |
|---|---|---|
| `GET /api/v1/incidents/{incidentId}/diagnosis` | session, `Diagnosis.Read` | new |
| `GET /api/v1/diagnoses/{diagnosisId}/reviews` | session, `Diagnosis.Read` | moved from `/local-demo/v1/...` |
| `POST /api/v1/diagnoses/{diagnosisId}/reviews` | session, `Diagnosis.Review` | moved from `/local-demo/v1/...` |
| `GET /api/v1/github-actions/repositories/{repositoryId}/runs/{runId}/attempts/{attempt}/report` | GitHub Actions OIDC | new |

### Diagnosis by incident

Authorization: Recommendation resolves the entitlement with Pipeline
(`POST /internal/v1/diagnosis-read-entitlements`, workload token + subject token),
which confirms the subject's VIEW capability, current GitHub access and the
incident's single failed ORIGIN execution. Recommendation then selects the highest
admitted diagnosis version whose admitted context matches that incident and
execution. It never falls back to an older version.

`200` body:

```json
{
  "diagnosisId": "uuid",
  "version": 1,
  "incidentId": "uuid",
  "executionId": "uuid",
  "contextId": "uuid",
  "correlationId": "string",
  "createdAt": "RFC 3339",
  "status": "PENDING | CONFIRMED | CORRECTED | REJECTED",
  "hypothesis": {
    "probableCause": "string",
    "recommendation": "string",
    "limitations": "string",
    "evidenceIds": ["uuid"],
    "chunkIds": ["uuid"]
  },
  "evidence": [{ "evidenceId": "uuid", "stage": "string", "sourceLocator": "v2:…", "content": "sanitized excerpt" }],
  "sources": [{ "documentId": "uuid", "chunkId": "uuid", "provenance": "string" }],
  "model": { "deployment": "string", "modelVersion": "string" },
  "reviews": [{ "revision": 1, "decision": "CONFIRMED | CORRECTED | REJECTED", "timestamp": "RFC 3339" }]
}
```

`hypothesis` is model output (inferred); `evidence` is observed and sanitized;
`sources` lists retrieved knowledge. The dashboard labels them accordingly.
Errors: `404 incident_not_found` (also used when the subject lacks access),
`404 diagnosis_absent` (processing not finished or no diagnosis),
`409 diagnosis_stale`, `503 authority_unavailable`, `503 diagnosis_unavailable`.

### Reviews

`GET` returns the existing review view (status, revision, history). `POST` body:
`{ "expectedRevision": n, "decision": "CONFIRMED|CORRECTED|REJECTED", "comment": "…",
"actualCause": "…"|null, "correctedRecommendation": "…"|null }`. The reviewer is the
session subject, never a body field. Requires OPERATE conditions on the incident's
pipeline. `409` on revision mismatch.

### GitHub Actions report

Returns `200` with `{ "report": <diagnosis projection without reviews>,
"markdown": "string" }` once an admitted diagnosis exists, `404 diagnosis_absent`
while processing (the workflow retries with backoff), `403` if the OIDC repository
does not match. The report workflow uploads the markdown as a run artifact and links
the failed run id and attempt.

## Internal: capture workflow scopes (ADR-023)

`PUT /internal/v1/capture/workflow-scopes/{repositoryId}/{workflowId}` — workload `pipeline`,
role `Pipeline.CaptureScope.Write`.

Request: `{"requestId": "uuid", "correlationId": "string", "pipelineId": "uuid",
"monitoringStatus": "ACTIVE|PAUSED"}`.

`200`: `{"repositoryId", "workflowId", "pipelineId", "status", "scopeRevision", "revision"}`.
Repeating the same status returns the same revision. `404 REPOSITORY_NOT_ADMITTED` when the
repository has no operator admission for the tenant; `409 PIPELINE_MISMATCH` when the scope is
already bound to another pipeline id; `400` for invalid identifiers; `503` when storage is
unavailable. Responses set `Cache-Control: no-store`.

The analysis request (`POST …/analysis`) returns `409 CAPTURE_SCOPE_PENDING` while the workflow
has no `ACTIVE` scope.
