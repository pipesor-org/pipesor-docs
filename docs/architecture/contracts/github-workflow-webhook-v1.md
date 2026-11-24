# GitHub workflow webhook v1

Status: contract of the webhook implemented in Ingestion
([`pipesor-ingestion-normalization-service@a41188a`](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/tree/a41188aa16e1d85903c80d9162d69986dd0b4a5e)),
recorded on 24/11/2026 at the project owner's request: the webhook was configured to take
information from GitHub Actions, and no contract described it. It documents behaviour, not a
deployment. A change to the route, its responses or its limits needs a reviewed change here and in
Ingestion.

The webhook is the push path of [ADR-023](../decisions/ADR-023-capture-scope-from-registrations.md):
GitHub tells Ingestion that a monitored workflow run completed, and Ingestion captures it through
the same receipt, preparation and publication pipeline as a manual analysis. The model represents
it as `rel_github_actions_ingestion_event` (HTTPS/Webhook, event) in
[`architecture.yml`](../../../model/architecture.yml).

## 1. Route and exposure

`POST /webhooks/v1/github/workflow-runs` on Ingestion's external ingress
(`https://ingestion.<env-domain>/webhooks/v1/github/workflow-runs`).

- **Disabled by default** (`pipesor.github.webhook-enabled: false`). Enabled, Ingestion refuses to
  start without a webhook secret. In Azure, IaC enables it only when
  `workloads.github.webhook_secret_version` is set, and then grants Ingestion read access to that
  one Key Vault secret. The local stack leaves it disabled.
- **Disabled means absent**: no servlet, no OpenAPI entry. A request falls through to the
  platform chain, which denies it.
- **Authentication is GitHub's signature, not a platform token**
  ([identity contract §10](platform-identity-v1.md#10-routes-without-platform-tokens)). The route
  has its own stateless security chain. Only `POST` is allowed; any other method gets `403`.
  A query string gets `400`.

## 2. Request

Headers. A header sent twice, blank or longer than 512 characters is rejected with the status in
the table:

| Header | Rule | Otherwise |
|---|---|---|
| `X-Hub-Signature-256` | Required, `sha256=` followed by 64 hex digits | `403` |
| `X-GitHub-Event` | Required, `[a-z][a-z0-9_]*` | `400` |
| `X-GitHub-Delivery` | Required, `[A-Za-z0-9._:-]{1,128}` | `400` |
| `X-Correlation-Id` | Optional, same pattern; generated when absent | `400` |
| `Content-Type` | Required, `application/json`, charset absent or UTF-8 | `415` |
| `Content-Encoding` | Absent or `identity` | `415` |

The four context headers (signature, event, delivery, correlation) together cannot exceed 512
characters (`400`).

Body: one JSON object in strict UTF-8. Duplicate keys and trailing content are invalid. The body is
non-empty and at most 1 MiB; a larger `Content-Length`, or a streamed body that grows past the
limit, gets `413`.

## 3. Signature

- The HMAC-SHA256 of the exact body bytes, keyed with the webhook secret, must equal the
  signature. The comparison is constant-time and runs **before** the body is parsed. A wrong
  signature gets `403` and nothing is stored.
- The secret is read on every delivery and is never cached:
  - in Azure, Key Vault secret `github-webhook-secret` at the exact version configured (`latest`
    is refused);
  - locally, a `0600`/`0400` file.
- Ignored events (§4) also need a valid signature.

## 4. Events and selection

Order of checks after the signature:

1. A body with a top-level `workflow_run` under any event other than `workflow_run` → `400`
   (the unsigned header cannot hide a signed run).
2. Any other event, `ping` included → `204`, nothing stored.
3. `action` must be a non-blank string (`400`). Only `completed` is captured; `requested` and
   `in_progress` → `204`, nothing stored.
4. Fields read from a `workflow_run`/`completed` delivery:
   - `installation.id`, `repository.id` and `repository.owner.id`;
   - `workflow_run.id`, `workflow_run.workflow_id` and `workflow_run.run_attempt` (integer ≥ 1);
   - `workflow_run.repository.id` and `.owner.id`, which must equal the top-level ones.

   IDs must be JSON integers. Anything else → `400`.
5. **Scope.** The tenant, capture domain and App ID come from Ingestion's configuration, never from
   the request. The delivery must match an `ACTIVE` row of `ingestion.capture_workflow_scopes`
   (ADR-023, kept in sync by Pipeline) that allows `completed`. The capture then rechecks the scope
   revision and a non-revoked repository admission (ADR-024). No match, a changed scope or a revoked
   admission → `403`.

Not read: `conclusion`, `status`, branch, commit, timestamps and `sender`; the sender is never an
actor. Preparation, not the webhook, decides what each conclusion produces (§6).

## 5. Responses

Every response has an empty body, `Content-Length: 0` and `Cache-Control: no-store`. There is no
`application/problem+json` body and no receipt ID.

| Status | Meaning |
|---|---|
| `204` | Captured and committed, already captured (duplicate), or a validly signed delivery that is ignored |
| `400` | Malformed or ambiguous delivery: headers, query string, empty or invalid JSON, event/body mismatch, invalid `action` or IDs |
| `403` | Not `POST`; signature missing, duplicated, malformed or wrong; scope missing or changed; admission revoked |
| `409` | The same `X-GitHub-Delivery` already belongs to another body, or the body already belongs to another scope, run or attempt |
| `413` | Body over 1 MiB |
| `415` | Content type or encoding not accepted |
| `503` | Capacity (16 deliveries in flight), 5 s deadline, secret or database unavailable, or a capture failure after the checks above |

A `503` may follow a commit whose outcome Ingestion cannot confirm. GitHub's retry is safe: the
receipt is deduplicated (§6), and a redelivery of a committed body answers `204`.

## 6. Idempotency and what happens next

- **Receipt identity** is the SHA-256 of the exact body, unique per capture domain and source
  (`ingestion.capture_receipts`).
  - The same body under a new delivery ID adds an alias to the same receipt and keeps its
    correlation.
  - Concurrent redeliveries commit one receipt.
  - Delivery IDs are unique and immutable (`ingestion.capture_delivery_aliases`).
- **Not stored:** the raw body, the signature and the sender.
- **Asynchronous capture.** Nothing is published during the request. Ingestion's preparation
  worker reads the run and its logs from GitHub with the App's installation token. It freezes an
  `execution.snapshot` v1 for every run and, for `failure` and `timed_out`,
  `protected_workflow_evidence` v2 ([protected evidence 2.2](protected-evidence-v2.2.md)). The
  publication worker sends both to the Service Bus topic `workflow-evidence`.
- A webhook delivery and a manual analysis of the same run are separate receipts. Duplicates are
  removed when the observation is recorded.

## 7. Limits of this contract

- **Not implemented:** the webhooks ADR-020 and ADR-024 mention for revocation and
  `installation_repositories` changes. Only `workflow_run` is handled.
- **Deployment state:** whether dev has the webhook enabled, and which events the GitHub App
  subscribes to, is configuration outside the repositories. It is not verified here.
- **Unverified on GitHub's side:** other events that may carry a top-level `workflow_run` would get
  `400` under §4.1 if the App subscribed to them.
- **Responses without a problem body** differ from the [MVP HTTP API](mvp-http-api-v1.md)
  conventions on purpose: the caller is GitHub, which only records the status.
