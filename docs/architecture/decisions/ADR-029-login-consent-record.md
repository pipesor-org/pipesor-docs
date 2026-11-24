Title: Require and record the consent given at sign-in
Status: Accepted
Date: 2026-11-24
Amends: ADR-022 and the platform identity contract v1 §5 (login flow); complements ADR-025 (open sign-in)

## Context

The dashboard's sign-in screen has an unchecked box. By ticking it the person accepts the
Privacy Policy and the Terms of Use, which share one version (today `2026-11-24`), and the
transfer of their data to the United States (Microsoft Azure, Azure OpenAI and GitHub).
Without the box ticked the dashboard does not start the login. The server, however, kept no
trace of that acceptance.

The regulation of Peru's personal data law (Ley 29733, D.S. 016-2024-JUS) requires consent
*before* data is collected (art. 4) and puts the burden of proving it on the controller
(art. 9). A check that only exists in the browser proves nothing. The project owner approved
recording it on the server and requiring it, on 24/11/2026.

## Decision

- **Consent travels with the start of the login**, before GitHub hands over any data:
  `GET /api/v1/auth/github/start` requires `consent_version` (an ISO date naming the accepted
  version of both documents). If it is missing, malformed, repeated or later than the next
  UTC day, Ingestion creates no attempt, does not contact GitHub and redirects to
  `<dashboard>/auth/complete?error=consent_required`. The server does not hold the texts: the
  dashboard owns the documents and decides which version is current.
- **One record per successful login.** Ingestion stores the version and the acceptance time
  on the login attempt. In the same transaction that completes a successful callback, it
  appends a row to `ingestion.consent_records` with the tenant, the principal (the same
  `tenantId:objectId` used by grants), the GitHub user id, the version, the acceptance and
  recording times, the source (`LOGIN_CHECKBOX`), the attempt and the correlation id. If the
  record cannot be written the login fails: there is no login without proof. "Reconnect" is
  also a login and records consent the same way.
- **The dashboard can ask again.** The session response carries the consent of that login,
  and `GET /api/v1/auth/consent` returns the person's latest non-revoked consent, or
  `404 CONSENT_NOT_FOUND`. When the current documents change, the dashboard asks again.
- **Revocation is manual for the MVP.** Requests arrive by email; an operator marks
  `revoked_at` and a request reference with the documented SQL procedure, and disconnects the
  GitHub link. The table is append-only: a trigger allows only that one transition.
- **Retention:** the record is kept while the person has data in Pipesor and up to one year
  after revoking consent or after their last access, so the consent can be proved. As for the
  other personal data, the period is documented but no purge is implemented (PD-030).

## Consequences

- Deployment order matters: the dashboard that sends `consent_version` must be deployed
  before this Ingestion version. The current Ingestion ignores the parameter, so deploying
  the dashboard first breaks nothing. The reverse order makes every login fail with
  `consent_required`.
- One more table in the `ingestion` schema, modeled in `model/domain.yml` with DD-028. The
  owner authorized raising the validator's table limit from 35 to 40.
- The privacy policy must declare this record, its purpose (proof of consent) and its
  retention.
- Revocation does not stop other processing by itself; the manual procedure also disconnects
  the link, and the next sign-in asks for consent again.

Implementation: pipesor-ingestion-normalization-service (login flow, migration and
`GET /api/v1/auth/consent`). Contract:
[platform identity v1 §5](../contracts/platform-identity-v1.md#5-login-flow-ingestion).
