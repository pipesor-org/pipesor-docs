Title: Any GitHub user may sign in; access stays governed per repository
Status: Accepted
Date: 2026-11-22
Amends: ADR-020 (installation/account allowlist), ADR-024 (completes self-service onboarding)

## Context

ADR-020 was written for a closed deployment: "admit only installations/accounts expressly
authorized for the tenant", and "administering a personal repository does not authorize its
corporate import". The login callback enforced it by requiring the user to administer a
repository already admitted by the operator. With the `pipesor-dev` App public and ADR-024's
self-service admission, that gate became the only obstacle for anyone outside the project
owner's organization: people who installed the App on their own repositories received
`not_admitted` and could never reach the onboarding step that would admit their repositories.
The project owner decided on 2026-11-22 that Pipesor must be usable by anyone on their own
repositories, without belonging to `pipesor-org`.

## Decision

- **Open sign-in.** Any GitHub user who authorizes the pipesor App may sign in. The callback
  still verifies the GitHub user with the token it just exchanged, keeps the token in custody
  and issues the session; it no longer requires a prior repository admission.
- **Signing in grants no data.** Authorization stays where ADR-020 put it: every read and command
  re-checks the user's current GitHub access to each repository; only a repository's
  administrator registers its workflows; pipelines, incidents and diagnoses are visible only with
  pipeline grants (VIEW/OPERATE/CONFIGURE).
- **Repositories** enter Pipesor when their administrator selects them in a pipesor installation
  (ADR-024); the operator import remains for other cases.
- ADR-020's allowlist bullet is superseded by this decision; its per-repository checks remain.

## Consequences

- A new user installs the App, signs in and sees their administered repositories in
  "Add workflow" without operator action. A user without any installation signs in and is guided
  to install the App.
- The single platform tenant is shared by all users; isolation relies on GitHub access and
  pipeline grants, which every service already enforces.
- `not_admitted` no longer exists as a login error; the dashboard should drop its message.

Implementation: pipesor-ingestion-normalization-service `GitHubLoginHandler` (HumanAdmissions removed).
