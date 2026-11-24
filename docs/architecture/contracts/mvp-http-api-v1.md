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
| `GET /api/v1/github/repositories?pageSize=&pageToken=&q=` | `GitHub.Self` | extended | admitted + readable only; reconciles admissions first (ADR-024); paged form below. The legacy `?limit=` form is unchanged (503 above `limit`) |
| `GET /api/v1/github/installations` | `GitHub.Self` | new | pipesor installations visible to the user, reconciled (ADR-024); shape below |
| `GET /api/v1/github/repositories/{repositoryId}/workflows?pageSize=&pageToken=&q=` | `GitHub.Self` | extended | paged form below; the legacy `?limit=` form is unchanged |
| `GET /api/v1/github/repositories/{repositoryId}/collaborators?pageSize=&pageToken=` | `GitHub.Self` | new | GitHub collaborators of a repository the caller currently administers, to choose grant recipients (ADR-028); shape below |
| `GET /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs?conclusion=failure|success` | `GitHub.Self` | new | `items[]: {runId, attempt, conclusion, headBranch, headSha, createdAt, htmlUrl}`; `failure` (default) lists runs to analyse, `success` runs to record as verification; other values 400 |
| `POST /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs/{runId}/attempts/{attempt}/analysis` | `GitHub.Self` | generalized | replaces the configured single run; requires OPERATE conditions of ADR-020; returns `202 {analysisId, phase}` and only records durable intent; accepts failed runs (analysis) and successful runs (verification capture) |
| `GET /api/v1/github/repositories/{repositoryId}/workflows/{workflowId}/runs/{runId}/attempts/{attempt}/analysis` | `GitHub.Self` | existing (pilot) | `{analysisId, phase: ACCEPTED|PREPARING|PUBLISHED|BLOCKED, blockedReason?: SCOPE_CHANGED|SOURCE_EXPIRED, executionId?, incidentId?}`. `BLOCKED` is terminal; `SOURCE_EXPIRED` means GitHub no longer retains the run's logs (410 Gone). |

`GET /api/v1/github/installations` returns `200`:

```json
{
  "context": { "…": "same discovery context object as GET /api/v1/github/repositories" },
  "installations": [
    {
      "installationId": "string",
      "account": { "id": "string", "login": "string | null" },
      "suspended": false,
      "repositories": [
        { "repositoryId": "string", "fullName": "owner/name", "admitted": true, "userIsAdmin": true }
      ]
    }
  ]
}
```

`admitted` means Pipesor may monitor the repository (after reconciliation); `userIsAdmin` is the
user's GitHub role. Reading this route or the repository list admits repositories the user
administers in a pipesor installation and revokes admissions the installation no longer lists
(ADR-024); browser-supplied installation data is never used. Errors are `problem+json` with
`code` (`CONNECTION_REQUIRED`, `UNAVAILABLE`, …) as for the other GitHub routes.

### Paged discovery

`GET /api/v1/github/repositories` and `GET /api/v1/github/repositories/{repositoryId}/workflows`
accept exactly one of two forms:

- **Paged (new):** `pageSize` (1–100, required for this form), `pageToken` (opaque, optional) and
  `q` (optional, 2–100 characters after trimming; case-insensitive partial match on the
  repository `fullName`, or on the workflow `name` or `file`). The response is the existing body
  plus `nextPageToken` (string or `null`); more results than `pageSize` produce a page and a
  token, never a 503. Order: repositories by `fullName` (case-insensitive), then `repositoryId`;
  workflows by `name` (case-insensitive), then `workflowId`. Every page carries the same
  `context` object (`tenantId`, `subjectObjectId`, …); repository pages repeat the ADR-024
  reconciliation and workflow pages re-check the repository's admission and readability.
- **Legacy:** `limit` (1–100) with no `pageSize`/`pageToken`/`q`: unchanged, including
  `503 VERIFICATION_UNAVAILABLE` when the user sees more than `limit` items.

Sending both forms, neither form, or `cursor` is `400 INVALID_REQUEST`. A `pageToken` that is
malformed or was issued for another route, repository, user or `q` is `400 INVALID_PAGE_TOKEN`.
Ingestion still reads at most 500 repositories per user from GitHub
(`pipesor.github.limits.user-max-items`); beyond that the read is `503` in both forms.

`executionId` and `incidentId` are the deterministic Pipeline identifiers derived from
the same repository, workflow, run and attempt, so the dashboard can navigate without
asking for internal UUIDs. Both appear once the phase is `PUBLISHED`; `incidentId` only
when the run failed. A successful run yields only `executionId`, which the dashboard
passes to Pipeline's `POST /api/v1/incidents/{id}/verification`.

### Repository collaborators

`GET /api/v1/github/repositories/{repositoryId}/collaborators` lists the people GitHub reports
as collaborators of the repository, so an administrator can choose grant recipients (ADR-028).
It is read with the caller's own GitHub token and requires an active link, a repository admitted
in a pipesor installation and readable, and the caller's current GitHub administration of it.
Nothing is stored.

- `pageSize`: 1–100, default 30. `pageToken`: opaque `nextPageToken` of the previous page,
  valid only for the same route, repository, user and `pageSize`.
- Order is GitHub's. Only accounts of type `User` are listed (bots are skipped), so a page may
  hold fewer than `pageSize` items; only `nextPageToken` (`null` on the last page) signals more.
  There is no `q`: GitHub cannot search collaborators. Pending invitations are not listed.

```json
{
  "repository": {"repositoryId": "123", "fullName": "acme/payments-api"},
  "items": [{
    "githubUserId": "583231",
    "login": "octocat",
    "avatarUrl": "https://avatars.githubusercontent.com/u/583231?v=4",
    "role": "ADMIN",
    "principalRef": "<tenantId>:<objectId>",
    "pipesorConnection": "ACTIVE"
  }],
  "nextPageToken": null
}
```

- `role`: `READ|TRIAGE|WRITE|MAINTAIN|ADMIN`, the highest base role from every source (direct,
  teams, organization base permission, owners); a custom role is reported as its base role.
- `principalRef`: exactly the `tenantId:objectId` of
  `PUT /api/v1/pipelines/{id}/grants/{principalRef}/{capability}` (caller's tenant plus UUIDv5
  of the GitHub user id, platform identity contract v1).
- `pipesorConnection`: `ACTIVE` when the person has an active GitHub link in Pipesor, else
  `NONE`. It does not prove the link still works: granting still verifies the recipient and can
  return `403 GITHUB_CONNECTION_REQUIRED`.
- `avatarUrl` is an absolute `https` URL or `null`.

Errors (`problem+json`, `code`): `400 INVALID_REQUEST` (non-numeric `repositoryId`, `pageSize`
out of range, repeated parameter), `400 INVALID_PAGE_TOKEN` (malformed, or issued for another
repository, user or `pageSize`), `401`, `403 DENIED` (repository not admitted or not readable,
or the caller is not its administrator), `409 CONNECTION_REQUIRED` (no active link or
reconnection needed), `503 VERIFICATION_UNAVAILABLE` (GitHub unavailable or rate limited,
SSO not authorized, or GitHub refuses the list, for instance to an outside collaborator of an
organization). As on the other repository routes, a repository that is not admitted is `403 DENIED`
before the link is checked.

## Pipeline — operations (external ingress)

Existing routes (`/api/v1/pipelines`, `/pipelines/{id}`, `/pipelines/{id}/executions`,
`/pipelines/{id}/incidents`, `/executions/{id}`, `/executions/{id}/stages`,
`/incidents/{id}`, `/incidents/{id}/runs`, settings, policy, ownership, grants and
incident lifecycle commands) keep their shapes and require `Pipeline.Access`.
`DELETE /api/v1/pipelines/{id}/grants/{principalRef}/CONFIGURE` refuses to remove the
pipeline's last `CONFIGURE` grant, also the caller's own: `409 LAST_CONFIGURE_GRANT`
(ADR-028). It counts stored grants; grant changes of one pipeline are serialized.

New:

| Method and route | Notes |
|---|---|
| `GET /api/v1/incidents?state=OPEN|RESOLVED` | cross-pipeline lifecycle queue, filtered by VIEW grants and current GitHub access before paging; removes the per-pipeline N+1 fan-out. `OPEN` is every active incident (`OPEN`, `IN_REMEDIATION`, `VERIFICATION`). Filters, `total` and enriched items below (ADR-027) |
| `GET /api/v1/pipelines/registrations?repositoryId=` | monitored workflows of a repository the caller can currently read on GitHub, with or without a grant (ADR-028); existence only, shape below |
| `GET /api/v1/incidents/summary?state=OPEN|RESOLVED` | counts of the same filtered, visible set per severity, status and diagnosis (ADR-027) |
| `GET /api/v1/insights?from=&to=` | History Insights over visible resolved incidents (ADR-027) |

Incident `severity` (nullable) is seeded when the incident is opened from its pipeline's
criticality at that moment (same `CRITICAL|HIGH|MEDIUM|LOW` scale, MVP rule); criticality
remains a pipeline property and later criticality changes do not alter existing incidents.
Human reads reuse a successful `VIEW` access verification for up to 30 s (ADR-020
amendment); commands always verify live.

Incident reads (`/incidents`, `/incidents/{id}`, `/pipelines/{id}/incidents`) include
`displayNumber`, a database-assigned sequence shown as `INC-<n>`. It is presentation only:
routes and contracts keep the UUID as identity.

Diagnosis validation is not a lifecycle state, so Pipeline has no validation queue. The
dashboard's *Needs validation* view is `GET /api/v1/incidents?state=RESOLVED&diagnosis=PENDING`:
Pipeline filters on its diagnosis projection (ADR-027), which replaces the browser-side join of
decision D03.

### Repository registrations

`GET /api/v1/pipelines/registrations?repositoryId={githubRepositoryId}` tells a reader of the
repository which of its workflows are monitored, so the dashboard can offer to ask for access
(ADR-028). It needs current GitHub read access to the admitted repository and no AIOps grant.
It returns existence only, which a second registration's `409` already reveals:

```json
{
  "repositoryId": "123",
  "items": [
    {"pipelineId": "83a4c7b9-e2d5-5076-820f-3240ce5b1af8", "githubWorkflowId": "918001", "accessible": false}
  ]
}
```

Items are ordered by numeric `githubWorkflowId`, with no paging. `accessible` is `true` when the
caller already has an effective capability on that pipeline (stored grant plus current read).
Errors: `400 INVALID_REQUEST` (missing, non-numeric or repeated `repositoryId`),
`403 ACCESS_DENIED` (no current read access or repository not admitted),
`403 GITHUB_CONNECTION_REQUIRED`, `503 GITHUB_VERIFICATION_UNAVAILABLE`.

### Incident queue filters

`GET /api/v1/incidents` and `GET /api/v1/incidents/summary` take `state` (required) and these
optional filters. Each filter may repeat (`?severity=CRITICAL&severity=HIGH`): values of one
filter are OR-ed, different filters are AND-ed. Filters are applied together with the
authorization (VIEW grant and current GitHub read) in SQL before paging and counting, and the
queue order (`createdAt` descending, then `id`) does not change.

| Parameter | Values |
|---|---|
| `pipelineId` | pipeline UUID |
| `repositoryId` | GitHub numeric repository id (string of digits), as returned by discovery |
| `severity` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNCLASSIFIED` (severity `null`) |
| `stage` | `BUILD`, `TESTING`, `QUALITY_GATE`, `DEPLOYMENT`, `CONTAINER`, `INFRASTRUCTURE` |
| `status` | with `state=OPEN`: `OPEN`, `IN_REMEDIATION`, `VERIFICATION`; with `state=RESOLVED`: `RESOLVED` |
| `diagnosis` | `PENDING`, `CONFIRMED`, `CORRECTED`, `REJECTED`, `ABSENT` (no admitted diagnosis projected) |
| `q` | single value, normalized (NFKC, trimmed, inner whitespace collapsed), at most 100 characters. `INC-123` or `123` (case-insensitive prefix, digits only, from one digit) matches `displayNumber` exactly. Any other text needs at least 2 characters and is split into words: an incident matches when **every** word is a case-insensitive substring of the repository `fullName` or of the workflow name (each word may match a different field; `%` and `_` are literal) |

With `state=RESOLVED` two more single-value parameters apply:

| Parameter | Values |
|---|---|
| `resolvedFrom`, `resolvedTo` | RFC 3339 instants, inclusive bounds of `resolvedAt` (list and summary); `resolvedFrom` may not follow `resolvedTo` |
| `sort` (list only) | `createdAt` (default) or `resolvedAt`: newest resolution first, then `id` (History) |

`sort=resolvedAt` with `state=OPEN`, or another `sort` value, is `400 INVALID_REQUEST`; the
resolution bounds with `state=OPEN` are `400 INVALID_FILTER`.

At most 100 values per filter. A value outside these sets, an empty value, a malformed UUID or
repository id, a `status` not valid for `state`, or a `q` out of bounds is
`400 INVALID_FILTER` (`problem+json` with `code`). `state`/`pageSize` errors keep
`400 INVALID_REQUEST`. A `pageToken` is bound to the normalized `state`, filters and `sort`: reusing it
with other values, or sending a malformed token, is `400 INVALID_PAGE_TOKEN`.

`GET /api/v1/incidents` response:

```json
{
  "items": [IncidentView],
  "nextPageToken": "opaque | null",
  "total": 57,
  "appliedFilters": {
    "state": "RESOLVED",
    "pipelineId": [], "repositoryId": ["825001"], "severity": ["CRITICAL", "HIGH"],
    "stage": [], "status": [], "diagnosis": ["PENDING"],
    "q": null, "qMatch": null, "resolvedFrom": null, "resolvedTo": null, "sort": "createdAt"
  }
}
```

- `total`: exact number of incidents that match and the caller may view (independent of the
  page). It is computed on every request, so it can change between pages if incidents change.
- `appliedFilters`: normalized echo (deduplicated, sorted arrays; `[]` when absent; `q` normalized
  or `null`; `qMatch` is `DISPLAY_NUMBER`, `TEXT` or `null`; `sort` only on the list). Spring ignores unknown query
  parameters, so clients use its presence to know that the server applied the filters.

Every incident read (`/incidents`, `/incidents/{id}`, `/pipelines/{id}/incidents`) adds, without
removing fields:

```json
{
  "repository": { "repositoryId": "825001", "fullName": "owner/name" },
  "workflow": { "workflowId": "926001", "name": "CI" },
  "diagnosis": { "status": "PENDING | CONFIRMED | CORRECTED | REJECTED", "probableCause": "string | null", "createdAt": "RFC 3339" }
}
```

`repositoryId` and `workflowId` are GitHub ids (strings). `diagnosis` is `null` while no admitted
diagnosis is projected; it is the summary of the version the Workspace shows (ADR-027), and
`probableCause` is inferred model output, truncated to 1000 characters.

### Incident summary

`GET /api/v1/incidents/summary` takes the same parameters except `pageSize`/`pageToken`, with
the same authorization and `400` codes, and returns counts over the same filtered set (every
filter applies to every map, so each map sums to `total`; keys are always present):

```json
{
  "total": 31,
  "bySeverity": { "CRITICAL": 4, "HIGH": 20, "MEDIUM": 5, "LOW": 0, "UNCLASSIFIED": 2 },
  "byStatus": { "OPEN": 25, "IN_REMEDIATION": 4, "VERIFICATION": 2 },
  "byDiagnosis": { "PENDING": 9, "CONFIRMED": 3, "CORRECTED": 1, "REJECTED": 0, "ABSENT": 18 },
  "appliedFilters": { "…": "as in the list" }
}
```

`byStatus` lists the statuses of the requested `state` (`RESOLVED` only for `state=RESOLVED`).

### Insights

`GET /api/v1/insights?from=&to=&top=` computes History Insights in the server over the
resolved incidents the caller may view (same authorization as the queue) whose `resolvedAt` is in
`[from, to]`. `from`/`to` are RFC 3339 instants; defaults: `to` = now, `from` = start of the UTC
day 29 days before `to` (30 calendar days). `from` must precede `to` and the window may not exceed
366 days; `top` (1–50, default 10) bounds `recurring`. Invalid values are `400 INVALID_FILTER`.

```json
{
  "window": { "from": "RFC 3339", "to": "RFC 3339" },
  "summary": {
    "resolvedIncidents": 12, "confirmed": 5, "rejected": 2, "pending": 3, "confirmationRate": 0.714,
    "meanDiagnosis": { "meanMs": 81234, "sampleSize": 10 },
    "meanResolution": { "meanMs": 5400000, "sampleSize": 12 }
  },
  "outcomes": { "PENDING": 3, "CONFIRMED": 5, "CORRECTED": 1, "REJECTED": 1, "ABSENT": 2 },
  "stages": [{ "stage": "TESTING", "count": 7 }],
  "recurring": [{ "pipelineId": "uuid", "repository": { "repositoryId": "825001", "fullName": "owner/name" },
                  "workflow": { "workflowId": "926001", "name": "CI" }, "stage": "TESTING", "count": 4 }],
  "trend": [{ "start": "RFC 3339", "end": "RFC 3339", "incidentCount": 3, "meanDiagnosisMs": 70000 }]
}
```

Definitions (as the dashboard computed them): mean diagnosis time is
`diagnosis.createdAt − detectedAt` over incidents with a projected diagnosis (negative samples
ignored); MTTR is `resolvedAt − detectedAt`; confirmation rate is
`confirmed / (confirmed + rejected)` where `rejected` counts `CORRECTED` and `REJECTED` and
`PENDING`/`ABSENT` are excluded (human reviews, not model accuracy; `null` without reviews);
`outcomes` is the diagnosis distribution; `stages` is sorted by count, then stage order;
`recurring` groups by pipeline and stage, sorted by count, then repository, workflow and stage
(not a root-cause taxonomy); `trend` has 7-day buckets from `from`, the last one ending at `to`.
Means are `null` without samples and are never coerced to zero.

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

## Internal: diagnosis summaries (ADR-027)

`PUT /internal/v1/incidents/{incidentId}/diagnosis-summary` on Pipeline — workload
`recommendation`, role `Recommendation.DiagnosisSummaries.Write`, no subject token,
`X-Correlation-ID` with the diagnosis correlation id.

Request (unknown fields rejected):

```json
{
  "diagnosisId": "uuid", "version": 1, "executionId": "uuid",
  "pipelineId": "uuid", "githubRepositoryId": "825001",
  "status": "PENDING | CONFIRMED | CORRECTED | REJECTED", "reviewRevision": 0,
  "reviewedAt": "RFC 3339 | null", "probableCause": "string | null", "createdAt": "RFC 3339"
}
```

`status` is `PENDING` exactly when `reviewRevision` is `0` (then `reviewedAt` is `null`);
`probableCause` is at most 1000 characters. `200`:
`{"incidentId", "diagnosisId", "version", "reviewRevision", "status", "applied"}`; `applied` is
`false` when the stored summary is already at the same or a later `(version, reviewRevision)`.
`404 INCIDENT_NOT_FOUND`; `409 SCOPE_MISMATCH` when the execution is not the incident's ORIGIN
execution or the pipeline/repository differ from the incident's; `400 INVALID_REQUEST`.
Recommendation retries any other outcome with backoff and drops `400`/`409`.

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
