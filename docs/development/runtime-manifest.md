# Runtime manifest — MVP

Status: approved MVP runtime inputs. It is the hand-off between service repositories,
`pipesor-iac` and the local stack in `pipesor-workspace`. Identity rules come from
[ADR-022](../architecture/decisions/ADR-022-platform-identity-without-entra-app-registrations.md)
and the [platform identity contract](../architecture/contracts/platform-identity-v1.md);
routes from the [MVP HTTP API](../architecture/contracts/mvp-http-api-v1.md).
A change to a row is a contract change for both the service and IaC.

## One runtime, two profiles

Every service ships one image and selects adapters by profile. No code path exists only
for local use.

| Concern | `local` profile | `azure` profile |
|---|---|---|
| Messaging | Azure Service Bus emulator (connection string) | Service Bus namespace, managed identity |
| PostgreSQL | `pgvector/pgvector:pg17` container, password auth | Flexible Server, Entra auth with managed identity (passwordless JDBC / token) |
| Signing key | PEM file `PIPESOR_SIGNING_KEY_FILE` (0600) | Key Vault key `PIPESOR_SIGNING_KEY_ID`, managed identity |
| Azure AI | `DefaultAzureCredential` (developer `az login`) | managed identity |
| Secrets | files under `~/.config/pipesor-local/` | Key Vault secret references |
| Transport | HTTP allowed only to loopback hosts | HTTPS only |

Startup fails when a required value is missing or when a `local`-only setting appears
under `azure`. Simulated backends (in-memory stores, deterministic embeddings,
simulated caller auth) are allowed only in automated tests.

## Common settings

| Variable | Meaning |
|---|---|
| `SPRING_PROFILES_ACTIVE` / `PIPESOR_ENVIRONMENT` | `local` or `azure` |
| `SERVER_ADDRESS` / `SERVER_PORT` | bind address and port: `127.0.0.1` and the local host port below (`local`), `0.0.0.0` and `8080` (`azure`) |
| `AZURE_CLIENT_ID` | client id of the workload's user-assigned managed identity (`azure`) |
| `PIPESOR_TENANT_ID` | environment tenant UUID |
| `PIPESOR_WORKLOAD_ID` | workload id from the identity contract |
| `PIPESOR_SIGNING_KEY_FILE` or `PIPESOR_SIGNING_KEY_ID` | signing key (see profiles) |
| `PIPESOR_SECURITY_AUDIENCE` | own audience `urn:pipesor:api:<workload>` |
| `PIPESOR_SECURITY_TRUSTEDWORKLOADS_<n>_ID`, `_JWKSURI`, `_ROLES` (comma-separated) | inbound callers (Spring relaxed binding of `pipesor.security.trusted-workloads[n]`) |
| `PIPESOR_SECURITY_SESSION_JWKSURI` | session JWKS (services with human APIs) |
| `PIPESOR_SESSION_SIGNING_KEY_FILE` or `PIPESOR_SESSION_SIGNING_KEY_ID` | session key (Ingestion only) |
| `PIPESOR_ENDPOINTS_<TARGET>` | outbound base URL per target workload, e.g. `PIPESOR_ENDPOINTS_LOGEVENT` |
| `PIPESOR_SERVICE_BUS_TOPIC` / `PIPESOR_SERVICE_BUS_SUBSCRIPTION` | `workflow-evidence` / own subscription |
| `PIPESOR_DASHBOARD_ORIGIN` | CORS origin (services with human APIs) |
| `PIPESOR_DATABASE_URL` / `PIPESOR_DATABASE_USERNAME` / `PIPESOR_DATABASE_PASSWORD` (password local only) | PostgreSQL, database `pipesor`; in `azure` Java services use the workload identity name as username and append the Entra token plugin to the JDBC URL, and RAG puts that principal in its URL |
| `PIPESOR_SERVICE_BUS_NAMESPACE` or `PIPESOR_SERVICE_BUS_CONNECTION_STRING` (local only) | messaging |
| `PIPESOR_INFERENCE_ENDPOINT`, `PIPESOR_INFERENCE_DEPLOYMENT` | Recommendation only: Foundry account origin (`https://<account>.services.ai.azure.com`) and chat deployment (`pipesor-dev-diagnostics-luna`, gpt-6-luna, [ADR-026](../architecture/decisions/ADR-026-diagnosis-model-gpt-6-luna.md); `pipesor-dev-diagnostics`, gpt-4o, was the earlier DEV smoke-test baseline) |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | optional telemetry (azure) |

Container port is `8080` for every service. Java health: `/actuator/health/liveness`,
`/actuator/health/readiness`. Python health: `/health/live`, `/health/ready`. Routes without
a bearer token: health, `/.well-known/jwks.json`, Ingestion's sign-in flow
(`GET /api/v1/auth/github/start`, `GET /api/v1/auth/github/callback`,
`POST /api/v1/auth/session`) and, when enabled, the GitHub webhook
`POST /webhooks/v1/github/workflow-runs`, authenticated by its HMAC signature
([webhook contract](../architecture/contracts/github-workflow-webhook-v1.md)).

## Service-specific settings

| Service | Variables |
|---|---|
| `ingestion` | `PIPESOR_GITHUB_APP_ID`, `PIPESOR_GITHUB_CAPTURE_DOMAIN`, `PIPESOR_GITHUB_CALLBACK_URL`; `local`: `PIPESOR_GITHUB_PRIVATE_KEY_FILE`, `PIPESOR_GITHUB_PRIVATE_KEY_SHA256`, `PIPESOR_GITHUB_CLIENT_SECRET_FILE`, `PIPESOR_GITHUB_CUSTODY_DIRECTORY`; `azure`: `PIPESOR_GITHUB_KEY_VAULT_URL`, `PIPESOR_GITHUB_PRIVATE_KEY_SECRET_NAME`/`_VERSION`, `PIPESOR_GITHUB_CLIENT_SECRET_NAME`/`_VERSION`, `PIPESOR_GITHUB_CUSTODY_VAULT_URL`; optional webhook `PIPESOR_GITHUB_WEBHOOK_ENABLED` with `PIPESOR_GITHUB_WEBHOOK_SECRET_NAME`/`_VERSION` (or `_SECRET_FILE` locally); `PIPESOR_GITHUB_AUTHORITY_FILE` only for the operator admission import (ADR-023/024) |
| `rag` | `PIPESOR_RAG_AUTHENTICATION_MODE=platform`, `PIPESOR_RAG_STORAGE_BACKEND=postgresql`, `PIPESOR_RAG_EMBEDDING_BACKEND=azure_openai`, `PIPESOR_RAG_AZURE_OPENAI_ENDPOINT`, `PIPESOR_RAG_AZURE_OPENAI_DEPLOYMENT` (`pipesor-dev-embeddings`), `PIPESOR_RAG_EMBEDDING_MODEL_VERSION` |
| dashboard image | `PIPESOR_INGESTION_URL`, `PIPESOR_PIPELINE_URL`, `PIPESOR_RECOMMENDATION_URL` (bare HTTPS origins) and optional `PIPESOR_GITHUB_APP_INSTALL_URL`, rendered into `/config.js` and the CSP at startup; `VITE_PIPESOR_*_URL` is only a local development override |

Each service README lists its complete settings.

## Services

| Workload | Ingress | Local host port | Schema (owner) | Migrations | Messaging | Outbound |
|---|---|---|---|---|---|---|
| `ingestion` | external | 8081 | `ingestion` | Flyway at startup | sends to topic `workflow-evidence` | GitHub API/OAuth, Key Vault, pipeline JWKS |
| `pipeline` | external | 8082 | `ops`, `audit.audit_events` (MVP owner of the audit table, ADR-011) | Flyway at startup | receives subscription `pipeline` | ingestion |
| `log-event` | internal | 8083 | `evidence.evidence_items` | Flyway at startup, history `flyway_history_log_event` | receives subscription `log-event` | pipeline |
| `nlp` | internal (health + JWKS only) | 8084 | none | none | receives subscription `nlp` | correlation |
| `correlation` | internal | 8085 | `evidence` correlation tables | Flyway at startup, history `flyway_history_correlation` | none | pipeline, log-event, recommendation |
| `recommendation` | external | 8086 | `diagnosis` | Flyway at startup | none | rag, pipeline, Foundry chat |
| `rag` | internal | 8087 | `knowledge` | Alembic job `job-rag-migrations` (ADR-021 principal split; see the divergence below) | none | Foundry embeddings |
| dashboard | Static Web Apps (ADR-008; see the divergence below) | 5173 (Vite) | — | — | — | ingestion, pipeline, recommendation |

Ingress hosts in Azure: `https://<workload>.<env-domain>` (external) and
`https://<workload>.internal.<env-domain>` (internal). Local hosts: `http://127.0.0.1:<port>`.

**Divergences pending decision (24/11/2026).** These rows describe the decisions; the
[pipesor-iac `workloads` module](https://github.com/pipesor-org/pipesor-iac/blob/388e5a7252bd70650e6715a4e6591cb5a5f2ab7e/modules/workloads/main.tf) differs and no ADR records the change:

- **Dashboard hosting.** IaC serves the dashboard as an external Container App
  (`https://dashboard.<env-domain>`, unprivileged nginx on port 8080, identity
  `id-pipesor-<env>-dashboard`) because Static Web Apps is not offered in the allowed regions;
  ADR-008 selects Static Web Apps.
- **RAG database principals.** [ADR-021](../architecture/decisions/ADR-021-rag-runtime-contract-v0.1.md)
  separates runtime read, administrative import write and migration DDL principals and names a
  system-assigned identity. IaC runs `job-rag-migrations` and the RAG app with the same
  user-assigned `rag` identity.

## Messaging topology

One topic, `workflow-evidence`, with three subscriptions. The publisher sets
application properties `eventType` and `schemaMajor`.

| Subscription | SQL filter | Max delivery | Lock | Notes |
|---|---|---|---|---|
| `pipeline` | `eventType = 'execution.snapshot'` | 10 | 60 s | `UNKNOWN_WORKFLOW` is abandoned for redelivery, never dead-lettered immediately |
| `log-event` | `eventType = 'protected_workflow_evidence'` | 10 | 60 s | `NOT_READY` from Pipeline is abandoned for redelivery |
| `nlp` | `eventType = 'protected_workflow_evidence'` | 10 | 120 s | Correlation `503` is abandoned for redelivery |

Dead-lettered messages keep their reason; replay is an operator action.

## Azure identities and roles

| Workload | Role assignments |
|---|---|
| `ingestion` | Service Bus Data Sender (topic); Key Vault Crypto User (keys `pipesor-ingestion-signing`, `pipesor-session-signing`); Key Vault Secrets User (`github-app-private-key`, `github-app-client-secret`, the authority document secret used by the admission import job, `github-webhook-secret` when the webhook is enabled); Key Vault Secrets Officer on the separate OAuth custody vault |
| `pipeline` | Service Bus Data Receiver (`pipeline`); Key Vault Crypto User (`pipesor-pipeline-signing`) |
| `log-event` | Service Bus Data Receiver (`log-event`); Key Vault Crypto User (`pipesor-log-event-signing`) |
| `nlp` | Service Bus Data Receiver (`nlp`); Key Vault Crypto User (`pipesor-nlp-signing`) |
| `correlation` | Key Vault Crypto User (`pipesor-correlation-signing`) |
| `recommendation` | Key Vault Crypto User (`pipesor-recommendation-signing`); Cognitive Services OpenAI User (Foundry account) |
| `rag` | Key Vault Crypto User (`pipesor-rag-signing`); Cognitive Services OpenAI User (Foundry account) |
| dashboard | Key Vault Secrets User (registry token secret only) |
| `db-admin` | Additional Entra administrator of the PostgreSQL server, used only by the manual `job-database-setup` (principals, database, `vector` extension and schema grants) |

Every workload and the dashboard also hold Key Vault Secrets User on the registry token
secret (`registry.password_secret_name` in IaC). Each workload identity is an Entra
PostgreSQL principal that owns only its schema(s); RAG also creates Alembic's version table in
`public`. All apps pull images from GHCR with that registry credential, referenced from Key
Vault as a Container Apps secret.

## Local stack

`pipesor-workspace` provides `docker compose` with:

- `postgres`: `pgvector/pgvector:pg17`, host port `55432`, database `pipesor`, the
  `vector` extension created at init;
- the Service Bus emulator with its SQL Server dependency (compose service `sqledge`),
  configured with the topology above, AMQP on host port `5672`;
- `tools/local_stack.py init`, which writes one PEM per workload plus the session key
  under `~/.config/pipesor-local/keys/`, stack credentials, and one
  `~/.config/pipesor-local/env/<workload>.env` per service with the settings above
  (all mode 0600, directories 0700). `up`, `down` and `status` manage the containers;
  `services-start`, `services-stop` and `services-ps` run the Java services built in sibling
  checkouts.

Services run from their repositories with the `local` profile against this stack. The
historical `pipesor-local-postgres` container (port `55433`) is not part of the stack.
