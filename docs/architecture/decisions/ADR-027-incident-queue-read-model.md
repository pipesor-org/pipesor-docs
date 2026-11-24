Title: Server-side incident queue filters with a diagnosis summary projected into Pipeline
Status: Accepted
Date: 2026-11-23
Amends: decision D03 of the MVP HTTP API (Needs validation joined in the browser); keeps ADR-018 ownership and ADR-020 authorization

## Context

The dashboard pages every list (24 items) and could only filter or aggregate what it had
loaded. Pipeline filters the cross-pipeline incident queue by VIEW grants and current GitHub
access before paging (ADR-020), so only the server knows the real visible set. As a result
the operator could not find an incident of a given repository, badges such as "Critical 24"
counted only the loaded page, *Needs validation* missed `PENDING` diagnoses of older
incidents (a false "0"), Insights computed MTTR and confirmation rates over loaded rows only,
and the dashboard issued one pipeline read and one diagnosis read per row (N+1).

Filtering by diagnosis status, counting it and computing Insights before paging requires the
diagnosis status where the queue is served. That status is owned by Recommendation
(`diagnosis.diagnoses` and the append-only `diagnosis.human_reviews`), while the queue, its
authorization and its paging are owned by Pipeline. ADR-018 keeps one PostgreSQL instance
with ownership per schema and only logical cross-schema references; the conventions forbid
foreign writes, ORM navigation and cross-schema foreign keys.

Options considered:

1. **Pipeline reads Recommendation's tables.** Couples Pipeline to Recommendation's private
   schema and database grants; rejected by ADR-018 ownership.
2. **Pipeline asks Recommendation per page.** Removes the browser N+1 but cannot filter,
   count or page by diagnosis status before paging; rejected.
3. **Service Bus event from Recommendation.** Needs a new topic, subscription and IaC for a
   few hundred small updates; not justified for the MVP timeline.
4. **Recommendation pushes a minimal diagnosis summary to Pipeline** (transactional outbox,
   idempotent PUT, Pipeline-owned projection). Chosen.

## Decision

- **Projection owned by Pipeline.** Pipeline keeps `ops.incident_diagnoses`, one row per
  incident: diagnosis id and version, origin execution, status
  (`PENDING|CONFIRMED|CORRECTED|REJECTED`), review revision, last review time, diagnosis
  creation time and a bounded `probableCause`. It is a read model, not an authority: the full
  diagnosis, its evidence and its reviews stay in Recommendation, and the Incident Workspace
  keeps reading them from Recommendation. An incident without a row is `ABSENT`.
- **Recommendation feeds it through a transactional outbox.** Admitting a diagnosis and
  appending a review enqueue `(incidentId, executionId)` in `diagnosis.incident_summary_outbox`
  in the same transaction. A worker claims due rows (`FOR UPDATE SKIP LOCKED`, lease), reads the
  current state with the same selection the Workspace uses (highest admitted version for the
  incident and execution, status = last review decision or `PENDING`) and calls
  `PUT /internal/v1/incidents/{incidentId}/diagnosis-summary` on Pipeline with a workload token
  (role `Recommendation.DiagnosisSummaries.Write`, no subject token). A row is removed only when
  Pipeline acknowledged the generation it read; transport and 5xx failures retry with backoff,
  so the projection converges after outages. A migration enqueues every existing admitted
  diagnosis once (backfill).
- **Pipeline validates the binding.** The summary is applied only when the incident exists, the
  execution is its single failed ORIGIN execution and the pipeline and GitHub repository in the
  diagnosis authorization scope are the incident's; otherwise it is refused (`409`), as the
  Workspace would refuse a stale diagnosis. Writes are monotonic on
  `(version, reviewRevision)`: replays and out-of-order deliveries never move it backwards.
- **Filters, totals and facets in Pipeline.** `GET /api/v1/incidents` accepts repeatable
  filters (pipeline, repository, severity, stage, status, diagnosis) and a text query,
  intersected with the visible repository set and the actor's grants in SQL before paging. It
  returns the exact `total`, an `appliedFilters` echo and items enriched with repository,
  workflow and diagnosis summary. `GET /api/v1/incidents/summary` returns the counts per
  severity, status and diagnosis for the same set; `GET /api/v1/insights` computes the History
  Insights over visible resolved incidents with the definitions the dashboard used.
- **Page tokens are bound to the filters.** A token carries a digest of the normalized state and
  filters; reusing it with other filters is `400 INVALID_PAGE_TOKEN`.

## Consequences

- *Needs validation*, badges and Insights reflect every visible incident, not only the loaded
  page, and the dashboard drops the per-row pipeline and diagnosis reads.
- The queue shows a review a few seconds after it is committed in Recommendation (worker poll
  interval plus one HTTP call); the Workspace, which reads Recommendation directly, shows it
  immediately. During a Pipeline outage the queue keeps the last projected status until the
  outbox drains.
- The platform identity route catalog gains one route and role; the deployment must add the
  role to Pipeline's trusted `recommendation` caller (IaC `modules/workloads`, local stack).
  Until then Recommendation's pushes are refused (403), retried, and every incident reads as
  `ABSENT` in the queue.
- `probableCause` is model output (inferred) copied for display only, bounded to 1000
  characters and readable under the same VIEW authorization as the incident.
- Without the new parameters the queue's behavior and order are unchanged; the response only
  gains fields.
- `model/domain.yml` must add `ops.incident_diagnoses` and `diagnosis.incident_summary_outbox`
  (tracked with the other MVP tables).

Implementation: pipesor-pipeline-service migration V9 and `incident` read side;
pipesor-recommendation-service migration V9 and the summary publisher. Contract:
[MVP HTTP API v1](../contracts/mvp-http-api-v1.md#pipeline--operations-external-ingress).
