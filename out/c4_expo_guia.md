# C4 de contenedores para diapositivas

Modelo de presentación: `model/c4_container_presentation.yml`. Arquitectura: `model/architecture.yml`.
Se conserva la proyección C4 canónica: todos sus nodos, fronteras, relaciones, protocolos y estilos.
PostgreSQL/pgvector conserva la agrupación de C4 2A; Human Review se proyecta en su contenedor padre.
Los nombres y tecnologías completos permanecen en las cajas. Las flechas usan números y una leyenda lateral.
SVG y PNG: 1920×1080, formato 16:9. Diseño propuesto, sin acreditar implementación.

## C4 Level 2A — Ingestion and AIOps Processing

[SVG](c4_expo_2a.svg) · [PNG](c4_expo_2a.png)

Las fuentes externas entregan evidencia a ingesta, que la protege antes del topic de Service Bus. Tres suscripciones alimentan Pipeline, Log/Event y NLP. NLP entrega evidencia a correlación y esta al servicio diagnóstico, que orquesta RAG e inferencia con Azure OpenAI y fundación Foundry. PostgreSQL/pgvector conservan datos y evidencias. La causa probable requiere revisión humana.

### Contenedores, actores y sistemas externos

| Nombre exacto | Tipo / frontera | Tecnologías | Responsabilidades del modelo |
|---|---|---|---|
| Ingestion and Normalization Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | authorized_capture, canonical_event_mapping, validation, parsing, cleaning, normalization, operational_noise_filtering, masking, anonymization, secret_filtering, data_minimization, correlation_id_assignment, evidence_metadata_capture, github_user_connection, github_user_access_verification, github_repository_workflow_discovery |
| Azure Service Bus | container / dentro del prototipo | Azure Service Bus | persistent_asynchronous_messaging |
| Pipeline Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | register_pipeline, authorize_pipeline_with_verified_github_access, register_execution, maintain_pipeline_stages, maintain_execution_state, maintain_execution_metadata |
| Log/Event Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | register_normalized_evidence, query_logs_by_incident, query_events_by_incident, query_evidence_by_correlation_id, preserve_source_metadata, resolve_external_evidence_references |
| NLP Log Processing | container / dentro del prototipo | Azure Container Apps, Python / FastAPI, Drain3 | semantic_representation, log_preprocessing, signal_preparation |
| Evidence Correlation Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | Incident context |
| Diagnostic & Recommendation Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | generate_initial_recommendations, associate_recommendation_with_probable_cause, associate_recommendation_with_evidence, expose_evidence_limitations, orchestrate_diagnostic_flow |
| RAG Knowledge Retrieval | container / dentro del prototipo | Azure Container Apps, Python / FastAPI | retrieve_authorized_knowledge, semantic_search, preserve_provenance, interact_with_vector_store |
| PostgreSQL | datastore / dentro del prototipo | PostgreSQL / pgvector | pipelines, incidents, diagnoses, human_reviews, recommendations, metrics, audit_metadata, evidence_references, traceability_metadata |
| GitHub Actions | external_system / externo al prototipo | GitHub Actions | ci_cd_execution_and_evidence_source |
| Compatible Observability and Runtime Sources | external_system / externo al prototipo | Azure Monitor, Application Insights | Authorized telemetry |
| Azure OpenAI Service | external_system / externo al prototipo | gpt-6-luna 2026-09-22, Microsoft Foundry account/project | gpt-6-luna in dev (ADR-026) |

### Relaciones

| Nº | Origen → destino | Relación completa | Protocolo | Estilo |
|---|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Emits authorized workflow events | HTTPS/Webhook | event |
| 02 | Azure Service Bus → Pipeline Service | Delivers execution events to register pipeline context | Azure Service Bus | async |
| 03 | Azure Service Bus → Log/Event Service | Delivers normalized evidence for registration and querying | Azure Service Bus | async |
| 04 | Ingestion and Normalization Service → PostgreSQL | Persists connector metadata and durable capture/publication ledger with temporary protected output bytes; no credential values | PostgreSQL | sync |
| 05 | Pipeline Service → PostgreSQL | Persists pipelines, stages, states and execution metadata | PostgreSQL | sync |
| 06 | Log/Event Service → PostgreSQL | Persists and queries normalized evidence metadata and references | PostgreSQL | sync |
| 07 | Diagnostic & Recommendation Service → PostgreSQL | Persists diagnoses with their recommendation and cited evidence | PostgreSQL | sync |
| 08 | Ingestion and Normalization Service → GitHub Actions | Retrieves authorized run metadata, jobs and logs | GitHub API/HTTPS | sync |
| 09 | Ingestion and Normalization Service → Azure Service Bus | Publishes normalized and protected evidence | Azure Service Bus | async |
| 10 | Azure Service Bus → NLP Log Processing | Delivers normalized events for processing | Azure Service Bus | async |
| 11 | NLP Log Processing → Evidence Correlation Service | Delivers logs and processed evidence for correlation | REST/HTTPS | sync |
| 12 | Evidence Correlation Service → PostgreSQL | Records correlated context and traceability | PostgreSQL | sync |
| 13 | RAG Knowledge Retrieval → PostgreSQL | Retrieves semantically related operational knowledge | PostgreSQL/pgvector | sync |
| 14 | RAG Knowledge Retrieval → Azure OpenAI Service | Generates compatible document and query embeddings | Azure OpenAI API v1/HTTPS | sync |
| 15 | Compatible Observability and Runtime Sources → Ingestion and Normalization Service | Provides authorized telemetry and operational evidence | REST/HTTPS | sync |
| 16 | Evidence Correlation Service → Diagnostic & Recommendation Service | Delivers correlated incident context for assisted diagnosis | REST/HTTPS | sync |
| 17 | Diagnostic & Recommendation Service → RAG Knowledge Retrieval | Requests authorized contextual knowledge for the incident | REST/HTTPS | sync |
| 18 | Diagnostic & Recommendation Service → Azure OpenAI Service | Requests diagnostic inference with sanitized evidence and RAG context | Azure OpenAI API/HTTPS | sync |
| 19 | Diagnostic & Recommendation Service → PostgreSQL | Persists human review decisions and traceability | PostgreSQL | sync |
| 20 | GitHub Actions → Diagnostic & Recommendation Service | Queries diagnostic_output to publish the workflow artifact | REST/HTTPS | sync |
| 21 | Pipeline Service → Ingestion and Normalization Service | Requests verified user access and workflow metadata without GitHub credentials; synchronizes workflow capture scopes | REST/HTTPS | sync |
| 22 | Log/Event Service → Pipeline Service | Checks committed operational membership before evidence registration | REST/HTTPS | sync |
| 23 | Pipeline Service → Ingestion and Normalization Service | Verifies current machine permission for an exact protected evidence capture scope | REST/HTTPS | sync |
| 24 | Evidence Correlation Service → Pipeline Service | Checks current scope and committed ORIGIN membership before correlation | REST/HTTPS | sync |
| 25 | Evidence Correlation Service → Log/Event Service | Verifies committed evidence membership in the authorized capture and attempt | REST/HTTPS | sync |
| 26 | Diagnostic & Recommendation Service → Pipeline Service | Resolves the user's diagnosis read entitlement and the incident's ORIGIN execution | REST/HTTPS | sync |
| 27 | Diagnostic & Recommendation Service → Pipeline Service | Projects the incident diagnosis summary into Pipeline's incident queue read model | REST/HTTPS | sync |

## C4 Level 2B — Consumption, Governance and Persistence

[SVG](c4_expo_2b.svg) · [PNG](c4_expo_2b.png)

El usuario accede al dashboard, inicia sesión con GitHub (OAuth con PKCE, mediante Ingesta; ADR-022) y consume APIs mediante ingress nativo de ACA. Pipeline, Log/Event y diagnóstico conservan los datos y la revisión humana en PostgreSQL; Log/Event conserva evidencia saneada en PostgreSQL; los logs originales permanecen en GitHub Actions. GitHub Actions consulta el diagnóstico mediante ingress nativo de ACA y publica su artifact. La revisión pertenece al servicio diagnóstico, sin otro microservicio. Ingesta firma las sesiones, y cada servicio sus tokens de workload, con claves no exportables de Key Vault.

### Contenedores, actores y sistemas externos

| Nombre exacto | Tipo / frontera | Tecnologías | Responsabilidades del modelo |
|---|---|---|---|
| AIOps Web Dashboard | container / dentro del prototipo | Azure Container Apps, TypeScript / React, SPA | incident_query, diagnosis_query, evidence_query, recommendation_query, pipeline_status_query, tmd_metrics, comparative_diagnosis_metrics, human_review_registration, human_review_status_display, distinguish_generated_hypothesis_from_validated_diagnosis, role_protected_access, github_account_connection, authorized_workflow_selection |
| Pipeline Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | register_pipeline, authorize_pipeline_with_verified_github_access, register_execution, maintain_pipeline_stages, maintain_execution_state, maintain_execution_metadata |
| Log/Event Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | register_normalized_evidence, query_logs_by_incident, query_events_by_incident, query_evidence_by_correlation_id, preserve_source_metadata, resolve_external_evidence_references |
| Diagnostic & Recommendation Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | generate_initial_recommendations, associate_recommendation_with_probable_cause, associate_recommendation_with_evidence, expose_evidence_limitations, orchestrate_diagnostic_flow |
| PostgreSQL | datastore / dentro del prototipo | PostgreSQL | pipelines, incidents, diagnoses, human_reviews, recommendations, metrics, audit_metadata, evidence_references, traceability_metadata |
| Ingestion and Normalization Service | container / dentro del prototipo | Azure Container Apps, Java / Spring Boot | authorized_capture, canonical_event_mapping, validation, parsing, cleaning, normalization, operational_noise_filtering, masking, anonymization, secret_filtering, data_minimization, correlation_id_assignment, evidence_metadata_capture, github_user_connection, github_user_access_verification, github_repository_workflow_discovery |
| Azure Key Vault | datastore / dentro del prototipo | Azure Key Vault | workload_token_signing_keys, session_token_signing_key, github_app_material, github_user_credential_custody |
| Technical Users | actor / externo al prototipo | No aplica | Querying and validation |
| GitHub | external_system / externo al prototipo | GitHub | source_control |
| GitHub Actions | external_system / externo al prototipo | GitHub Actions | ci_cd_execution_and_evidence_source |

### Relaciones

| Nº | Origen → destino | Relación completa | Protocolo | Estilo |
|---|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Emits authorized workflow events | HTTPS/Webhook | event |
| 02 | Ingestion and Normalization Service → PostgreSQL | Persists connector metadata and durable capture/publication ledger with temporary protected output bytes; no credential values | PostgreSQL | sync |
| 03 | Pipeline Service → PostgreSQL | Persists pipelines, stages, states and execution metadata | PostgreSQL | sync |
| 04 | Log/Event Service → PostgreSQL | Persists and queries normalized evidence metadata and references | PostgreSQL | sync |
| 05 | Diagnostic & Recommendation Service → PostgreSQL | Persists diagnoses with their recommendation and cited evidence | PostgreSQL | sync |
| 06 | Ingestion and Normalization Service → GitHub Actions | Retrieves authorized run metadata, jobs and logs | GitHub API/HTTPS | sync |
| 07 | GitHub → GitHub Actions | Provides the repository, commits and CI/CD workflow definitions | GitHub API/HTTPS | event |
| 08 | Technical Users → AIOps Web Dashboard | Queries results and records human review | HTTPS | sync |
| 09 | AIOps Web Dashboard → GitHub | Sends users to GitHub to authorize sign-in | OAuth 2.0/HTTPS (authorization code + PKCE S256) | sync |
| 10 | AIOps Web Dashboard → Pipeline Service | Queries pipelines, executions, the incident queue and insights; registers workflows, grants access and changes incident state | REST/HTTPS | sync |
| 11 | AIOps Web Dashboard → Log/Event Service | Queries logs, events and evidence | REST/HTTPS | sync |
| 12 | AIOps Web Dashboard → Diagnostic & Recommendation Service | Reads diagnoses and records human reviews | REST/HTTPS | sync |
| 13 | Diagnostic & Recommendation Service → PostgreSQL | Persists human review decisions and traceability | PostgreSQL | sync |
| 14 | GitHub Actions → Diagnostic & Recommendation Service | Queries diagnostic_output to publish the workflow artifact | REST/HTTPS | sync |
| 15 | AIOps Web Dashboard → Ingestion and Normalization Service | Starts GitHub sign-in with recorded consent, exchanges it for a session, discovers repositories, workflows and collaborators, and requests run analysis | REST/HTTPS | sync |
| 16 | Ingestion and Normalization Service → GitHub | Exchanges sign-in codes with the PKCE verifier and verifies GitHub identity, installations, repository access and collaborators | OAuth/HTTPS + REST/HTTPS | sync |
| 17 | Ingestion and Normalization Service → Azure Key Vault | Signs workload and session tokens, reads GitHub App material and keeps GitHub user tokens and PKCE verifiers in custody | Azure Key Vault API/HTTPS | sync |
| 18 | Pipeline Service → Azure Key Vault | Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS | sync |
| 19 | Log/Event Service → Azure Key Vault | Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS | sync |
| 20 | Diagnostic & Recommendation Service → Azure Key Vault | Signs its workload tokens with its own non-exportable key | Azure Key Vault API/HTTPS | sync |
| 21 | Pipeline Service → Ingestion and Normalization Service | Requests verified user access and workflow metadata without GitHub credentials; synchronizes workflow capture scopes | REST/HTTPS | sync |
| 22 | Log/Event Service → Pipeline Service | Checks committed operational membership before evidence registration | REST/HTTPS | sync |
| 23 | Pipeline Service → Ingestion and Normalization Service | Verifies current machine permission for an exact protected evidence capture scope | REST/HTTPS | sync |
| 24 | Diagnostic & Recommendation Service → Pipeline Service | Resolves the user's diagnosis read entitlement and the incident's ORIGIN execution | REST/HTTPS | sync |
| 25 | Diagnostic & Recommendation Service → Pipeline Service | Projects the incident diagnosis summary into Pipeline's incident queue read model | REST/HTTPS | sync |
