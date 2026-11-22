Title: Platform identity without Entra app registrations for the academic MVP
Status: Accepted
Date: 2026-11-22

## Context

ADR-003, ADR-019, ADR-020 and ADR-021 rely on Microsoft Entra ID for human
authentication (dashboard login, delegated scopes) and for service-to-service
authorization (single-tenant app-only tokens with exclusive audiences and app
roles). Every one of those audiences, scopes and app roles requires an Entra app
registration.

On 2026-11-22 a read-only Microsoft Graph check of the only available tenant
(the university tenant that owns the Azure for Students subscription) returned
`allowedToCreateApps: false` and `allowedToCreateTenants: false`, and the project
operator holds no administrative directory role. The operator is `Owner` of the
subscription and resource group. Consequently:

- managed identities, Azure RBAC and Entra authentication **to Azure resources**
  (PostgreSQL, Service Bus, Key Vault, Foundry) are available;
- custom API audiences, app roles, delegated scopes and an MSAL dashboard client
  are **not** available, so no Pipesor HTTP API can be protected with
  Entra-issued tokens.

The MVP closing date (Charter Hito 9) does not allow waiting for a tenant change
or for an external administrator. The project owner selected option B on
2026-11-22: keep the subscription, keep Entra wherever it works, and replace only
the token issuance that requires app registrations.

## Decision

### Scope of the change

- Entra remains the identity for Azure resource access. Each Container App uses a
  managed identity with least-privilege Azure RBAC on PostgreSQL, Service Bus,
  Key Vault and Foundry. ADR-021's provider access (RAG → Foundry) is unchanged.
- Pipesor HTTP APIs accept **Pipesor platform tokens** defined in the
  [platform identity contract v1](../contracts/platform-identity-v1.md) instead of
  Entra-issued tokens. Their claim shape is deliberately Entra-compatible
  (`iss`, `aud`, `tid`, `oid`, `azp`, `ver`, `idtyp`, `roles`, `scp`) so the
  existing validation rules keep their meaning. Returning to Entra is a
  configuration change (issuer, JWKS URI, audience and identifier values), not a
  code change.
- No new microservice and no gateway are introduced. ADR-019's native ingress
  model is preserved.

### Workload (service-to-service) identity

- Each service holds its own asymmetric signing key and issues short-lived
  client-assertion tokens (RFC 7523 style) for one target audience and one role.
- In Azure the key is a non-exportable Key Vault key used through the service's
  managed identity (`sign` operation only). Locally it is an operator-owned PEM
  file. Both are adapters of the same signing port.
- Each service publishes its current public keys at `/.well-known/jwks.json`.
  Verifiers trust an explicit allow-list of callers (workload identifier, JWKS
  URI, allowed roles) per route. Unknown callers, wrong audience, wrong role,
  `scp` on a machine token or a lifetime above the contract maximum are rejected.

### Human identity

- The human identity is the GitHub user verified through the existing GitHub App
  user authorization. ADR-020 already requires a current GitHub link for every
  human operation; this decision makes that link the authentication itself
  instead of a binding to an Entra object.
- Ingestion completes the server-side OAuth authorization-code flow with
  one-time `state` and PKCE S256 already decided in ADR-020, keeps the GitHub user
  token in its custody, and issues a short-lived **Pipesor session token** to the
  dashboard through a one-time code exchange. GitHub tokens never reach the
  browser, Pipeline or any other service.
- ADR-020's capability policy is unchanged: AIOps grants plus current effective
  GitHub access are checked on every protected request; a session token alone
  never authorizes a resource.
- Pipeline's calls to Ingestion that need the human subject (the former OBO
  path) carry Pipeline's workload token plus the caller's session token as a
  subject token; Ingestion validates both.

### GitHub Actions identity

- The GitHub Actions workflow that publishes the diagnostic artifact (ADR-016,
  PD-036) authenticates to Recommendation with the GitHub Actions OIDC token.
  Recommendation validates the GitHub issuer, the Pipesor audience and the
  repository identity, and authorizes only the report of a run in that same
  registered repository.

### Transport

- In Azure every call uses HTTPS (external or internal Container Apps ingress).
- Locally, plain HTTP is accepted only for loopback hosts and only when the
  service runs with the explicit `local` profile. This single rule replaces the
  package-private test constructors and per-service loopback exceptions.

## Consequences

- The services' token validators are reconfigured to the platform issuers and
  JWKS URIs; duplicated hand-written JWT checks are consolidated into one
  resource-server configuration per service following the contract.
- The dashboard does not use MSAL. Its login starts at Ingestion and its API
  calls carry the session bearer token. Tokens are kept in memory and are not
  placed in URLs.
- Ingestion gains the OAuth start/callback/exchange routes already anticipated by
  ADR-020 and the deployment contract. The GitHub App client secret is stored in
  Key Vault.
- Signing keys, their rotation and their JWKS publication become operational
  responsibilities recorded in the runtime manifest.
- Security limits accepted for the MVP: tokens are bearer tokens without
  sender-constraining; the session token carries several Pipesor API audiences;
  there is no central revocation list, so lifetime limits are the revocation
  window; Entra Conditional Access and MFA policies do not apply to the platform
  tokens. GitHub's own account security (MFA, SSO of the organization) applies to
  login.
- ADR-003, ADR-019, ADR-020 and ADR-021 remain Accepted. This ADR supersedes only
  their requirement that Pipesor HTTP APIs validate **Entra-issued** tokens, for
  the academic MVP environment where app registrations are unavailable. In an
  environment that allows app registrations, the Entra configuration of the same
  validators is the default.
- This ADR does not authorize Azure writes by itself; IaC changes keep their
  explicit authorization gates.
