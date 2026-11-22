Title: Repository administrators admit their repositories by selecting them in the pipesor App
Status: Accepted
Date: 2026-11-22
Amends: ADR-023 (admission is no longer only an operator act); keeps ADR-020's guarantees

## Context

ADR-023 made repository admission an explicit operator import. With the `pipesor-dev` GitHub
App now public (Setup URL `https://dashboard.<domain>/pipelines/new`), a user who installs the
App on their own account and selects repositories still sees none of them in Pipesor until an
operator imports an authority document. That blocks a realistic onboarding demo and adds an
operator round trip to every repository. The project owner decided on 2026-11-22 to admit
repositories automatically when the authenticated user administers them on GitHub.

## Decision

- **Reconciliation on read.** `GET /api/v1/github/repositories` and the new
  `GET /api/v1/github/installations` reconcile admissions from facts Ingestion reads in the
  server with the subject's own user-to-server token: the installation belongs to the pipesor
  App (any other `app_id` is rejected), GitHub lists the repository in that installation, and
  the subject is the repository's administrator (`permissions.admin`). Only then Ingestion
  inserts into `repository_admissions` with `source = repository_administrator`,
  `admitted_by` = subject and `admitted_at`, and logs `repository_admitted`.
- **Browser data grants nothing.** `installation_id` and `setup_action` received by the Setup
  URL are never used; the dashboard only links to the installation and then reads the endpoints.
- **Conservative and idempotent.** Reconciliation creates a missing admission or reactivates a
  revoked one. An active admission bound to another account or installation is never rebound:
  that remains an operator decision. Readers who are not administrators admit nothing and see
  only already-admitted repositories.
- **Revocation.** For each active installation, admissions of repositories GitHub no longer
  lists (deselected) are marked `revoked_at`/`revoked_by` and logged as
  `repository_admission_revoked`; rows stay for audit. Revoked admissions are excluded from
  listing, Pipeline scope sync and capture (`completedScope`, scope verification). An
  uninstalled App stops listing its repositories and its machine token can no longer capture.
- **Operator import remains** (ADR-023) for repositories whose administrator is not the person
  onboarding, and restores a revoked admission.

## Consequences

- A repository appears in "Add workflow" as soon as its administrator selects it in GitHub.
- Revocation of a deselected repository is applied at the next read by a user who sees that
  installation; until then capture already fails at GitHub because the App lost access. A
  webhook-driven revocation (`installation_repositories`) can be added without changing this
  decision.
- Admission now writes during a GET; the reconciliation is idempotent and bounded by the
  existing discovery limits.

Implementation: pipesor-ingestion-normalization-service `GitHubQueryHandler.reconcile`,
`JdbcCaptureAuthority.admitByAdministrator/revokeAbsent`, migration V5.
