# Arquitectura física para sustentación

Generado desde `model/physical_presentation.yml`; hechos de `model/architecture.yml`.

Diseño propuesto; las figuras no acreditan implementación o despliegue actual.
Los iconos proceden del paquete diagrams instalado; los SVG los incluyen embebidos.
Las agrupaciones son columnas de lectura, no subredes ni nuevos recursos Azure.
Cada nodo declara su propia tecnología. Los componentes internos del diagnóstico se agrupan explícitamente en su contenedor.
PostgreSQL/pgvector representan roles de una sola instancia física (ADR-018); no se confirma un producto Azure para PostgreSQL.
Los protocolos están en los tooltips SVG y en la tabla inferior. Las respuestas síncronas regresan por la misma llamada.

## Physical View 01 — Sources, Ingestion and Messaging

[SVG](fisica_expo_01.svg) · [PNG para diapositivas](fisica_expo_01.png)

8 nodos. GitHub Actions y Azure Monitor aportan evidencia autorizada. Ingesta, cuyo diseño especifica Java y Spring Boot sobre Azure Container Apps, protege y normaliza los datos antes de Service Bus. Un topic distribuye los eventos a tres suscripciones: Pipeline Service, Log/Event Service y NLP; este último continúa en la segunda vista. El acceso a GitHub es read-only. Key Vault guarda claves de firma no exportables y la custodia de credenciales GitHub.

Service Bus also delivers events to NLP (view 02). Persistence and access: view 03.

| Relación canónica | Protocolo |
|---|---|
| Emits authorized workflow events | HTTPS/Webhook |
| Delivers execution events to register pipeline context | Azure Service Bus |
| Delivers normalized evidence for registration and querying | Azure Service Bus |
| Retrieves authorized logs, artifacts and metadata | GitHub API/HTTPS |
| Publishes normalized and protected evidence | Azure Service Bus |
| Provides the repository, commits and CI/CD workflow definitions | GitHub API/HTTPS |
| Provides authorized telemetry and operational evidence | REST/HTTPS |
| Exchanges sign-in codes with the PKCE verifier and verifies GitHub identity, installations, repository access and collaborators | OAuth/HTTPS + REST/HTTPS |
| Signs workload and session tokens, reads GitHub App material and keeps GitHub user tokens and PKCE verifiers in custody | Azure Key Vault API/HTTPS |
| Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS |
| Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS |
| Requests verified user access and workflow metadata without GitHub credentials; synchronizes workflow capture scopes | REST/HTTPS |
| Checks committed operational membership before evidence registration | REST/HTTPS |
| Verifies current machine permission for an exact protected evidence capture scope | REST/HTTPS |

## Physical View 02 — Assisted Diagnosis Runtime

[SVG](fisica_expo_02.svg) · [PNG para diapositivas](fisica_expo_02.png)

7 nodos. NLP y RAG usan Python y FastAPI; correlación y diagnóstico usan Java y Spring Boot. Los cuatro servicios tienen runtime propio en Azure Container Apps. NLP utiliza Drain3. Diagnóstico orquesta RAG, que consulta pgvector sobre PostgreSQL, y solicita inferencia a Azure OpenAI con fundación Microsoft Foundry: gpt-6-luna en dev y en la evaluación OE3-I2 (ADR-026). Azure OpenAI es externo y no se aloja en Container Apps.

Input from view 01. PostgreSQL/pgvector: the same physical instance. Consumption and review: view 03.

| Relación canónica | Protocolo |
|---|---|
| Delivers normalized events for processing | Azure Service Bus |
| Delivers logs and processed evidence for correlation | REST/HTTPS |
| Retrieves semantically related operational knowledge | PostgreSQL/pgvector |
| Generates compatible document and query embeddings | Azure OpenAI API v1/HTTPS |
| Delivers correlated incident context for assisted diagnosis | REST/HTTPS |
| Requests authorized contextual knowledge for the incident | REST/HTTPS |
| Requests diagnostic inference with sanitized evidence and RAG context | Azure OpenAI API/HTTPS |

## Physical View 03 — Access, Persistence and Human Review

[SVG](fisica_expo_03.svg) · [PNG para diapositivas](fisica_expo_03.png)

8 nodos. El dashboard React y TypeScript se sirve desde Azure Container Apps (ADR-030). El inicio de sesión es con GitHub (OAuth con PKCE, mediante Ingesta; ADR-022); las APIs usan ingress nativo de ACA y autorización en los servicios. PostgreSQL conserva evidencia saneada; los logs originales permanecen en GitHub Actions. La revisión humana se registra dentro del servicio diagnóstico. El workflow publica el artifact con su paso nativo.

Actions retrieves the diagnosis through ACA native ingress and publishes its artifact. Human review is within the diagnostic service.

| Relación canónica | Protocolo |
|---|---|
| Persists pipelines, stages, states and execution metadata | PostgreSQL |
| Persists and queries normalized evidence metadata and references | PostgreSQL |
| Persists diagnosis, recommendations and evidence links | PostgreSQL |
| Provides the repository, commits and CI/CD workflow definitions | GitHub API/HTTPS |
| Queries results and records human review | HTTPS |
| Sends users to GitHub to authorize sign-in | OAuth 2.0/HTTPS (authorization code + PKCE S256) |
| Routes pipeline, execution, incident queue and insights queries, registration, grants and incident lifecycle commands | REST/HTTPS |
| Routes log, event and evidence queries | REST/HTTPS |
| Routes diagnosis and review queries and operations | REST/HTTPS |
| Persists human review decisions and traceability | PostgreSQL |
| Queries diagnostic_output to publish the workflow artifact | REST/HTTPS |
| Checks committed operational membership before evidence registration | REST/HTTPS |
| Resolves the user's diagnosis read entitlement and the incident's ORIGIN execution | REST/HTTPS |
| Projects the incident diagnosis summary into Pipeline's incident queue read model | REST/HTTPS |

## Relaciones entre vistas

- `rel_ingestion_postgresql_connector_metadata`: Ingestion and Normalization Service → PostgreSQL: Persists connector metadata and durable capture/publication ledger with temporary protected output bytes; no credential values (PostgreSQL).
- `rel_correlation_postgresql`: Evidence Correlation Service → PostgreSQL: Records correlated context and traceability (PostgreSQL).
- `rel_dashboard_ingestion_github_connection`: AIOps Web Dashboard → Ingestion and Normalization Service: Starts GitHub sign-in with recorded consent, exchanges it for a session, discovers repositories, workflows and collaborators, and requests run analysis (REST/HTTPS).
- `rel_nlp_key_vault`: NLP Log Processing → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_correlation_key_vault`: Evidence Correlation Service → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_recommendation_key_vault`: Diagnostic & Recommendation Service → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_correlation_pipeline_operational_references`: Evidence Correlation Service → Pipeline Service: Checks current scope and committed ORIGIN membership before correlation (REST/HTTPS).
- `rel_correlation_log_event_evidence_membership`: Evidence Correlation Service → Log/Event Service: Verifies committed evidence membership in the authorized capture and attempt (REST/HTTPS).

## Advertencias

Iconos de fallback: []

Modelo de diagnóstico gpt-6-luna solo para dev y la evaluación OE3-I2 (ADR-026); PD-026 sigue abierta para otros entornos. No se introduce otra selección.
