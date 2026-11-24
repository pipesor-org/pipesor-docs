# MVP demonstration guide

Reproducible walkthrough of the main flow required by the Charter (OE3-I2, OE4-I2) on the
local runtime. The same images and settings run in Azure dev with the `azure` profile
([runtime manifest](runtime-manifest.md)). Every step lists the observable evidence to
capture for the validation record. Never record tokens, session URLs, secrets or raw private
logs; use identifiers, statuses and sanitized excerpts only.

| Step | Status on 2026-11-22 |
|---|---|
| 1–7 | Executed with the authentic run `43055757606` |
| 8–12 | Ready in the services; pending NLP and RAG integration (Codex) and the dashboard |

**Update 2026-11-24.** As recorded in the validation report (this audit did not verify the
deployment), the official OE3-I2 runs of 2026-11-23 exercised the automatic chain on
the deployed dev images, with webhook capture instead of step 5's manual request (steps 6–9 and 12)
and gpt-6-luna ([ADR-026](../architecture/decisions/ADR-026-diagnosis-model-gpt-6-luna.md)):
28/28 runs as designed, 26/26 diagnoses and published reports
([validation report](../research/informe-validacion-oe3.md), §1;
`pipesor-validation-scenarios/results/2026-11-23-oe3-test-r2`). Steps 10–11 are implemented in the
dashboard; their recorded evidence is still pending in that report.

## 0. Prerequisites

- `pipesor-workspace`: `python3 tools/local_stack.py init && python3 tools/local_stack.py up`.
- Java services built (`./mvnw -B -ntp -DskipTests package` in each) and started with
  `python3 tools/local_stack.py services-start`; NLP and RAG started from their repositories
  with `~/.config/pipesor-local/env/{nlp,rag}.env`.
- `az login` with access to the Foundry account (diagnosis and embeddings deployments). ADR-026
  selects `pipesor-dev-diagnostics-luna` (gpt-6-luna) for dev; `local_stack.py init` still writes
  `PIPESOR_INFERENCE_DEPLOYMENT=pipesor-dev-diagnostics` (gpt-4o) into
  `~/.config/pipesor-local/env/recommendation.env`, so change it there to reproduce the dev model.
- `pipesor-frontend`: `bun install --frozen-lockfile` and
  `bun run dev -- --host 127.0.0.1 --port 5173 --strictPort` (the services accept only that
  dashboard origin).
- GitHub App `pipesor-dev`: callback `http://127.0.0.1:8081/api/v1/auth/github/callback`,
  client secret in `~/.config/pipesor-local/github-client-secret`, user tokens with
  expiration. Any GitHub user who authorizes the App can sign in (ADR-025); registering a
  workflow requires administering its repository, which is admitted when selected in the App
  installation (ADR-024).

Readiness check: `curl -s http://127.0.0.1:<port>/actuator/health/readiness` returns `UP` for
8081, 8082, 8083, 8085, 8086, and `/health/ready` for 8084 and 8087.

## 1. Login (identity)

Open `http://127.0.0.1:5173/login` (the dashboard starts
`http://127.0.0.1:8081/api/v1/auth/github/start?return_to=…`) and approve the App. The dashboard
receives a one-time handoff at `/auth/complete` and exchanges it at `POST /api/v1/auth/session`.

Evidence: GitHub user login shown by the dashboard; session lifetime ≤ 1 h; no token in any URL.

## 2. Discovery (GitHub user access)

Dashboard → repositories → workflows → failed runs (Ingestion routes in the
[MVP HTTP API](../architecture/contracts/mvp-http-api-v1.md)).

Evidence: repository `pipesor-org/pipesor-ingestion-normalization-service`, workflow `CI`
(`414901007`; the former `Verify` workflow no longer exists) and failed runs listed from GitHub
with the user's own access. A repository the user administers appears once it is selected in the
pipesor App installation (ADR-024); `GET /api/v1/github/installations` shows `admitted` and
`userIsAdmin` per repository.

## 3. Register the workflow (ADR-020)

`POST /api/v1/pipelines` with `githubRepositoryId`, `githubWorkflowId`, `criticality`,
`monitoringStatus=ACTIVE`. Pipeline verifies current admin/admitted/readable facts through
Ingestion before its transaction.

Evidence: pipeline id `83a4c7b9-e2d5-5076-820f-3240ce5b1af8` (deterministic), `CONFIGURE`
grant for the creator, one `audit.audit_events` row. A second registration returns 409.

## 4. Grant OPERATE to the reviewer

ADR-020: `CONFIGURE` includes `VIEW` but not `OPERATE`, and human review requires `OPERATE`.
The creator grants it explicitly. To grant it to a teammate, the creator lists the repository's
GitHub collaborators (ADR-028):
`GET /api/v1/github/repositories/{repositoryId}/collaborators?pageSize=100` → each person's
`login`, `role`, `principalRef` and `pipesorConnection`. Only people with
`pipesorConnection: ACTIVE` (they signed in to Pipesor once) can receive grants:
`PUT /api/v1/pipelines/{pipelineId}/grants/{principalRef}/OPERATE` → 204.

Revoking the pipeline's last `CONFIGURE` grant is refused with `409 LAST_CONFIGURE_GRANT`.

Evidence: the diagnosis entitlement reports `["VIEW","OPERATE"]`.

## 5. Request the analysis of a failed run

`POST /api/v1/github/repositories/{r}/workflows/{w}/runs/{run}/attempts/{a}/analysis` → 202;
poll the same route with `GET` until `PUBLISHED`.

Evidence: receipt `PUBLISHED`; two outputs `CONFIRMED` (snapshot schema 1, evidence schema 2.2
with locator `v2:job:…:member:…:lines:…:sha256:…`).

## 6. Pipeline: execution and incident

Evidence: failed execution for the run and attempt; incident `OPEN` with stage and summary;
`ORIGIN` link; incident visible in `GET /api/v1/incidents?state=OPEN`.

## 7. Log/Event: protected evidence

Evidence: `evidence.evidence_items` row with the same execution, incident and locator, registered
only after Pipeline answered `Evidence.Check`.

## 8. NLP and Correlation

Evidence: NLP log `accepted` for the evidence message; `evidence.correlated_contexts` row with the
same execution, incident and locator; Correlation returned 200 only after Recommendation's receipt.

## 9. Recommendation: automatic diagnosis (RAG + gpt-6-luna)

Evidence: `diagnosis.correlated_context_receipts` row; `diagnosis.diagnosis_jobs` completed; RAG
`200` for the query (with or without matching knowledge); model request id and token usage in the
Recommendation log; `diagnosis.diagnoses` row with citations restricted to supplied evidence and
chunk ids. Redelivery of the same message creates no new row and no new inference.

## 10. Dashboard: diagnosis and observed vs inferred

`GET /api/v1/incidents/{incidentId}/diagnosis` behind the incident workspace.

Evidence: probable cause, recommendation and limitations labelled as model output; sanitized
excerpt and locator labelled as observed evidence; knowledge sources with provenance; reload
shows the same diagnosis version without new inference.

## 11. Human review

`POST /api/v1/diagnoses/{diagnosisId}/reviews` with `expectedRevision`, decision
(`CONFIRMED|CORRECTED|REJECTED`) and comment; the reviewer is the session subject.

Evidence: review revision and status visible in the workspace; a user without `OPERATE` gets 403.
A few seconds after the review, the incident's `diagnosis.status` in `GET /api/v1/incidents`
shows the decision instead of `PENDING` (ADR-027 projection); `GET /api/v1/incidents/summary`
counts it in `byDiagnosis`.

## 12. Downloadable report (GitHub Actions artifact)

A `pipesor-report` workflow triggered by `workflow_run` requests a GitHub Actions OIDC token with
audience `urn:pipesor:api:recommendation`, calls
`GET /api/v1/github-actions/repositories/{r}/runs/{run}/attempts/{a}/report` until it stops
returning `404 diagnosis_absent`, and uploads the markdown as a run artifact. In local
demonstrations Recommendation is not reachable from GitHub; this step needs the Azure
deployment or a tunnel approved for the demo.

Evidence: artifact attached to the report run, naming the failed run, attempt and incident id.

## Security checks for the record

- A GitHub user without grants can sign in (ADR-025), lists no pipelines and gets the generic 404
  for the incident; `GET /api/v1/pipelines/registrations?repositoryId=` only reveals that a
  workflow of a repository they can read is monitored (ADR-028).
- Internal routes reject a session token and accept only the catalogued workload and role.
- `/.well-known/oauth-protected-resource` returns 404; only health, JWKS, Ingestion's sign-in
  routes and the HMAC-signed GitHub webhook accept requests without a bearer token.
