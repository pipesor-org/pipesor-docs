Title: Capture admission and workflow scope owned in Ingestion and driven by registrations
Status: Accepted
Date: 2026-11-22

## Context

ADR-020 requires that only installations and repositories expressly admitted for a tenant
can be connected and captured, and that Pipeline owns monitored-workflow registration. The
implementation kept both decisions in an operator-owned JSON file (`authority.json`): human
admissions (tenant, installation, repositories) and machine capture scopes (one entry per
workflow with scope revision, allowed actions and replay window). Registering or pausing a
workflow in Pipeline therefore never changed what Ingestion captured, the file had to be edited
and redeployed for every workflow, and Azure would need it mounted as a secret. The project
owner approved replacing it on 2026-11-22.

## Decision

- Ingestion owns two tables in its `ingestion` schema: `repository_admissions` (operator
  decision: tenant, App, account, installation, repository) and `capture_workflow_scopes`
  (capture domain, tenant, App, account, installation, repository, workflow, pipeline id,
  status `ACTIVE|PAUSED`, allowed actions, replay window, numeric revision and the derived
  `scope_revision`). The runtime authority for human admission, repository resolution,
  machine capture, webhook routing and Pipeline's machine-scope checks reads only these tables.
- Admissions remain an explicit operator act. An operator command imports a reviewed
  authority file once (idempotent upsert) and exits; the file is not read at runtime.
- Pipeline drives workflow scopes through the existing Pipeline → Ingestion relation of
  ADR-020: `PUT /internal/v1/capture/workflow-scopes/{repositoryId}/{workflowId}` with a
  workload token (role `Pipeline.CaptureScope.Write`). Pipeline calls it after a registration
  commits and after any monitoring-status change, and reconciles all pipelines at startup and
  periodically because the call happens outside its transaction. Ingestion refuses scopes for
  repositories that are not admitted.
- A status change increments the revision and therefore `scope_revision`; repeating the same
  status is idempotent. Captures, replays and Pipeline's machine-scope checks compare the exact
  scope revision, so pausing a workflow revokes in-flight capture authority as before.

## Consequences

- Registering a workflow makes it capturable without operator file edits; pausing stops
  capture. Admitting new repositories still needs the operator command.
- The platform identity route catalog gains one route and role. No new service, relation
  direction or data copy between owners is introduced; Pipeline keeps ownership of
  registrations and Ingestion of capture authority.
- Until Pipeline's first successful sync, a newly registered workflow is not capturable; the
  analysis request reports that state instead of capturing.
- `model/domain.yml` must add both tables (tracked with the other MVP tables).
