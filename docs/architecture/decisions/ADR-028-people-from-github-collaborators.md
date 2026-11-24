Title: Grant recipients from GitHub collaborators; explicit grants and a guaranteed CONFIGURE holder
Status: Accepted
Date: 2026-11-23
Amends: ADR-020 (how grant recipients are found; recovery of the last CONFIGURE); keeps ADR-025 open sign-in, DD-012 ownership and the DD-019 limits

## Context

A monitored workflow is visible only to whoever registered it. In the demo, a teammate who
reads or administers the same repository signed in and saw nothing; trying to register the
workflow again returned `409`. The code does what ADR-020 designed: VIEW needs an explicit
grant plus current GitHub read access. The gap is that nobody can choose another person:
a grant targets an opaque `tenantId:objectId` principal and there was no way to find it, so
the dashboard only offered "grant me OPERATE". In addition, revoking the last `CONFIGURE`
grant left a pipeline that nobody could administer, and ADR-020 keeps that recovery pending
with no implicit administrator.

Options considered:

1. **Derive VIEW from GitHub read access.** With open sign-in (ADR-025) and public
   repositories, anyone with a GitHub account would see incidents and diagnoses of every
   public monitored repository. It would also mean verifying every registered repository of
   the shared tenant on each list. Rejected.
2. **A directory of Pipesor users to search.** Discloses who uses Pipesor across the tenant and
   needs a users table, which DD-012/DD-019 exclude. Rejected.
3. **Candidates from the repository's GitHub collaborators, grants still explicit.** GitHub
   decides *who* can be a candidate; Pipesor decides *what* each person can do. Chosen.

## Decision

- **Candidates come from GitHub.** Ingestion exposes
  `GET /api/v1/github/repositories/{repositoryId}/collaborators` to a current administrator of
  an admitted repository. It reads `GET /repos/{owner}/{repo}/collaborators` with the
  administrator's own user token. That endpoint needs the App's existing **Metadata: read**
  permission, so the App and its installations do not change. For each person it returns
  the GitHub id, login, avatar, base role (`READ|TRIAGE|WRITE|MAINTAIN|ADMIN`), the
  `principalRef` that the grant routes expect (tenant plus UUIDv5 of the GitHub user id,
  platform identity contract v1) and `pipesorConnection` (`ACTIVE|NONE`, whether the person
  has an active GitHub link in Pipesor). Nothing is stored: no copy of collaborators and no
  users table.
- **Pipesor decides what they can do.** Grants remain explicit `VIEW`/`OPERATE`/`CONFIGURE`
  through the existing `PUT`/`DELETE /api/v1/pipelines/{id}/grants/{principalRef}/{capability}`.
  The recipient's eligibility is still verified with the recipient's own token when the grant
  is made and each time it is used (ADR-020). A GitHub role never creates a grant; the list is a
  picker, not an authorization source.
- **A pipeline always keeps one CONFIGURE grant.** Revoking the pipeline's last local
  `CONFIGURE` grant, also one's own, is `409 LAST_CONFIGURE_GRANT`. The guard counts stored
  grants, not current GitHub administrators, and grant changes of one pipeline are serialized,
  so two administrators revoking each other cannot both succeed. Recovering a pipeline whose
  only CONFIGURE holder lost GitHub administration stays pending, as in ADR-020.
- **Disclosure accepted.** `pipesorConnection` tells a repository administrator which
  collaborators have a Pipesor link. This is accepted because grants can only target linked
  people and the eligibility check of a grant attempt already reveals it. Login, avatar and role
  are what the administrator already sees on GitHub.
- **Approved follow-up, not yet specified (P1).** A reader of the repository without a grant
  may learn that a workflow is monitored (existence only, as the `409` of a second registration
  already reveals), and may request access without email (ADR-012); a CONFIGURE holder
  approves (the existing grant plus closing the request) or rejects, and both are audited.
  Their routes, storage and audit actions are added to the contract when implemented. Teams
  (named sets of people) stay deferred because DD-012/DD-019 exclude users, roles and teams.

## Consequences

- Administrators can share a pipeline without knowing opaque identifiers. A collaborator
  must sign in to Pipesor once (`pipesorConnection: NONE` cannot receive grants).
- GitHub requires the caller to have write, maintain or admin access, and organization
  membership for organization repositories; Pipesor requires current admin. An administrator
  who is an outside collaborator of an organization gets `503 VERIFICATION_UNAVAILABLE`.
- In organizations with a base permission every member is a collaborator, so lists can be
  long. Pages hold up to 100 people in GitHub's order, and the list can change between pages.
  GitHub offers no search; an exact `login` lookup
  (`GET /repos/{owner}/{repo}/collaborators/{username}/permission`, same permission) is the
  next step if needed.
- "No longer a collaborator" shown next to a grant is informative; the authority remains the
  per-request verification of ADR-020, which already hides a pipeline from someone who lost
  read access.
- DD-017 and DD-019 record the amendment; P0 adds no table.

Implementation: pipesor-ingestion-normalization-service (collaborators route) and
pipesor-pipeline-service (last CONFIGURE guard). Contract:
[MVP HTTP API v1](../contracts/mvp-http-api-v1.md#repository-collaborators).
