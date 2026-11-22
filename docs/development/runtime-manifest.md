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
| `PIPESOR_DATABASE_URL` / user / password (local only) | PostgreSQL, database `pipesor` |
| `PIPESOR_SERVICE_BUS_NAMESPACE` or `PIPESOR_SERVICE_BUS_CONNECTION_STRING` (local only) | messaging |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | optional telemetry (azure) |

Container port is `8080` for every service. Java health: `/actuator/health/liveness`,
`/actuator/health/readiness`. Python health: `/health/live`, `/health/ready`. Health and
`/.well-known/jwks.json` are the only unauthenticated routes.

## Services

| Workload | Ingress | Local host port | Schema (owner) | Migrations | Messaging | Outbound |
|---|---|---|---|---|---|---|
| `ingestion` | external | 8081 | `ingestion` | Flyway at startup | sends to topic `workflow-evidence` | GitHub API/OAuth, Key Vault, pipeline JWKS |
| `pipeline` | external | 8082 | `ops`, `audit.audit_events` (MVP owner of the audit table, ADR-011) | Flyway at startup | receives subscription `pipeline` | ingestion |
| `log-event` | internal | 8083 | `evidence.evidence_items` | Flyway at startup, history `flyway_history_log_event` | receives subscription `log-event` | pipeline |
| `nlp` | internal (health + JWKS only) | 8084 | none | none | receives subscription `nlp` | correlation |
| `correlation` | internal | 8085 | `evidence` correlation tables | Flyway at startup, history `flyway_history_correlation` | none | pipeline, log-event, recommendation |
| `recommendation` | external | 8086 | `diagnosis` | Flyway at startup | none | rag, pipeline, Foundry chat |
| `rag` | internal | 8087 | `knowledge` | Alembic job (ADR-021 principal split) | none | Foundry embeddings |
| dashboard | Static Web Apps | 5173 | — | — | — | ingestion, pipeline, recommendation |

Ingress hosts in Azure: `https://<workload>.<env-domain>` (external) and
`https://<workload>.internal.<env-domain>` (internal). Local hosts: `http://127.0.0.1:<port>`.

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
| `ingestion` | Service Bus Data Sender (topic); Key Vault Crypto User (keys `pipesor-ingestion-signing`, `pipesor-session-signing`); Key Vault Secrets User (`github-app-private-key`, `github-app-client-secret`, `github-webhook-secret`); Key Vault Secrets Officer on the separate OAuth custody vault |
| `pipeline` | Service Bus Data Receiver (`pipeline`); Key Vault Crypto User (`pipesor-pipeline-signing`) |
| `log-event` | Service Bus Data Receiver (`log-event`); Key Vault Crypto User (`pipesor-log-event-signing`) |
| `nlp` | Service Bus Data Receiver (`nlp`); Key Vault Crypto User (`pipesor-nlp-signing`) |
| `correlation` | Key Vault Crypto User (`pipesor-correlation-signing`) |
| `recommendation` | Key Vault Crypto User (`pipesor-recommendation-signing`); Cognitive Services OpenAI User (Foundry account) |
| `rag` | Cognitive Services OpenAI User (Foundry account) |

Each identity is an Entra PostgreSQL principal that owns only its schema(s). All apps
pull images from GHCR with a registry credential stored as a Container Apps secret.

## Local stack

`pipesor-workspace` provides `docker compose` with:

- `postgres`: `pgvector/pgvector:pg17`, host port `55432`, database `pipesor`, the
  `vector` extension created at init;
- `servicebus-emulator` with its SQL Edge dependency, configured with the topology
  above, AMQP on host port `5672`;
- `tools/local_stack.py init`, which writes one PEM per workload plus the session key
  under `~/.config/pipesor-local/keys/`, stack credentials, and one
  `~/.config/pipesor-local/env/<workload>.env` per service with the settings above
  (all mode 0600, directories 0700). `up`, `down` and `status` manage the containers.

Services run from their repositories with the `local` profile against this stack. The
historical `pipesor-local-postgres` container (port `55433`) is not part of the stack.
