# Arquitectura lógica para sustentación

Generado desde `model/logical_presentation.yml`, con hechos de `model/architecture.yml`.

Diseño propuesto; estas figuras no acreditan implementación. Lectura de izquierda a derecha.

Los componentes internos del servicio diagnóstico se agrupan explícitamente en su contenedor.
Se omiten conexiones que salen de cada vista; las notas indican su continuación.
PostgreSQL y pgvector son roles lógicos de una misma instancia física según ADR-018.

## Logical View 01 — Evidence Intake and Distribution

[Abrir SVG](logica_expo_01.svg) · [PNG para diapositivas](logica_expo_01.png)

8 nodos. GitHub Actions origina eventos de ejecuciones fallidas. Ingesta consulta evidencia autorizada, la normaliza y protege antes de publicarla en Service Bus. Pipeline Service, Log/Event Service y NLP consumen suscripciones independientes; NLP continúa en la segunda vista. Key Vault guarda las claves con que cada servicio firma sus tokens y la custodia de credenciales GitHub de Ingesta.

Service Bus also delivers events to NLP (view 02). Persistence and queries: view 03.

## Logical View 02 — Assisted Diagnosis

[Abrir SVG](logica_expo_02.svg) · [PNG para diapositivas](logica_expo_02.png)

7 nodos. NLP entrega evidencia procesada a correlación. Diagnostic & Recommendation Service recibe el contexto del incidente, recupera conocimiento autorizado mediante RAG y solicita inferencia a Azure OpenAI. La respuesta es una causa probable con evidencia y recomendaciones; no ejecuta remediación autónoma.

Input from view 01. Diagnosis persistence, querying and human review: view 03.

## Logical View 03 — Consumption and Human Review

[Abrir SVG](logica_expo_03.svg) · [PNG para diapositivas](logica_expo_03.png)

8 nodos. Los usuarios inician sesión con GitHub (OAuth con PKCE, mediante Ingesta) y consumen el dashboard mediante APIs con ingress nativo de ACA. Los servicios consultan y conservan contexto, evidencia, diagnósticos y revisión humana. GitHub Actions recupera el diagnóstico mediante ingress nativo de ACA y publica el artifact con un paso nativo.

Services from views 01/02 reappear as the same elements. Actions publishes its own artifact.

## Relaciones representadas y protocolos

Las cajas de agrupación organizan la lectura; no son nuevos elementos arquitectónicos.

| Relación canónica | Protocolo | Vistas |
|---|---|---|
| Emits authorized workflow events | HTTPS/Webhook | logica_expo_01 |
| Delivers execution events to register pipeline context | Azure Service Bus | logica_expo_01 |
| Delivers normalized evidence for registration and querying | Azure Service Bus | logica_expo_01 |
| Persists pipelines, stages, states and execution metadata | PostgreSQL | logica_expo_03 |
| Persists and queries normalized evidence metadata and references | PostgreSQL | logica_expo_03 |
| Persists diagnosis, recommendations and evidence links | PostgreSQL | logica_expo_03 |
| Retrieves authorized logs, artifacts and metadata | GitHub API/HTTPS | logica_expo_01 |
| Publishes normalized and protected evidence | Azure Service Bus | logica_expo_01 |
| Delivers normalized events for processing | Azure Service Bus | logica_expo_02 |
| Delivers logs and processed evidence for correlation | REST/HTTPS | logica_expo_02 |
| Retrieves semantically related operational knowledge | PostgreSQL/pgvector | logica_expo_02 |
| Generates compatible document and query embeddings | Azure OpenAI API v1/HTTPS | logica_expo_02 |
| Provides the repository, commits and CI/CD workflow definitions | GitHub API/HTTPS | logica_expo_01, logica_expo_03 |
| Provides authorized telemetry and operational evidence | REST/HTTPS | logica_expo_01 |
| Queries results and records human review | HTTPS | logica_expo_03 |
| Delivers correlated incident context for assisted diagnosis | REST/HTTPS | logica_expo_02 |
| Requests authorized contextual knowledge for the incident | REST/HTTPS | logica_expo_02 |
| Requests diagnostic inference with sanitized evidence and RAG context | Azure OpenAI API/HTTPS | logica_expo_02 |
| Sends users to GitHub to authorize sign-in | OAuth 2.0/HTTPS (authorization code + PKCE S256) | logica_expo_03 |
| Routes pipeline, execution, incident queue and insights queries, registration, grants and incident lifecycle commands | REST/HTTPS | logica_expo_03 |
| Routes log, event and evidence queries | REST/HTTPS | logica_expo_03 |
| Routes diagnosis and review queries and operations | REST/HTTPS | logica_expo_03 |
| Persists human review decisions and traceability | PostgreSQL | logica_expo_03 |
| Queries diagnostic_output to publish the workflow artifact | REST/HTTPS | logica_expo_03 |
| Exchanges sign-in codes with the PKCE verifier and verifies GitHub identity, installations, repository access and collaborators | OAuth/HTTPS + REST/HTTPS | logica_expo_01 |
| Signs workload and session tokens, reads GitHub App material and keeps GitHub user tokens and PKCE verifiers in custody | Azure Key Vault API/HTTPS | logica_expo_01 |
| Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS | logica_expo_01 |
| Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS | logica_expo_01 |
| Requests verified user access and workflow metadata without GitHub credentials; synchronizes workflow capture scopes | REST/HTTPS | logica_expo_01 |
| Checks committed operational membership before evidence registration | REST/HTTPS | logica_expo_01, logica_expo_03 |
| Verifies current machine permission for an exact protected evidence capture scope | REST/HTTPS | logica_expo_01 |
| Resolves the user's diagnosis read entitlement and the incident's ORIGIN execution | REST/HTTPS | logica_expo_03 |
| Projects the incident diagnosis summary into Pipeline's incident queue read model | REST/HTTPS | logica_expo_03 |

## Relaciones entre vistas

- `rel_ingestion_postgresql_connector_metadata`: Ingestion and Normalization Service → PostgreSQL: Persists connector metadata and durable capture/publication ledger with temporary protected output bytes; no credential values (PostgreSQL).
- `rel_correlation_postgresql`: Evidence Correlation Service → PostgreSQL: Records correlated context and traceability (PostgreSQL).
- `rel_dashboard_ingestion_github_connection`: AIOps Web Dashboard → Ingestion and Normalization Service: Starts GitHub sign-in with recorded consent, exchanges it for a session, discovers repositories, workflows and collaborators, and requests run analysis (REST/HTTPS).
- `rel_nlp_key_vault`: NLP Log Processing → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_correlation_key_vault`: Evidence Correlation Service → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_recommendation_key_vault`: Diagnostic & Recommendation Service → Azure Key Vault: Signs its workload tokens with its own non-exportable key (Azure Key Vault API/HTTPS).
- `rel_correlation_pipeline_operational_references`: Evidence Correlation Service → Pipeline Service: Checks current scope and committed ORIGIN membership before correlation (REST/HTTPS).
- `rel_correlation_log_event_evidence_membership`: Evidence Correlation Service → Log/Event Service: Verifies committed evidence membership in the authorized capture and attempt (REST/HTTPS).
