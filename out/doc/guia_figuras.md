# Figuras para documentos

Variantes de impresión de las vistas de presentación y del C4 de componentes. Generado desde los
mismos modelos que las vistas para diapositivas; diseño propuesto, sin acreditar implementación.

Cada figura se comprobó para A4 con márgenes de 2,54 cm: vertical 15.9 × 22.0 cm o apaisada 24.6 × 14.0 cm como máximo.
Insertada al ancho indicado, ningún texto queda por debajo de 8 pt. El PNG declara 300 ppp; insertarlo al 100 % conserva ese tamaño. Reducirlo más baja la legibilidad.

Las flechas llevan números. Si la leyenda cabe legible, va bajo el dibujo; si no, la tabla de
relaciones de esa figura está al final de esta guía para colocarla junto a la figura.

| Figura | Vista | Página | Leyenda | Ancho × alto (cm) | Texto mínimo (pt) |
|---|---|---|---|---|---|
| [logica_expo_01](logica_expo_01.png) ([SVG](logica_expo_01.svg)) | Logical View 01 — Evidence Intake and Distribution | vertical | en la figura | 12.4 × 22.0 | 8.3 |
| [logica_expo_02](logica_expo_02.png) ([SVG](logica_expo_02.svg)) | Logical View 02 — Assisted Diagnosis | vertical | en la figura | 12.6 × 19.1 | 9.0 |
| [logica_expo_03](logica_expo_03.png) ([SVG](logica_expo_03.svg)) | Logical View 03 — Consumption and Human Review | vertical | en la figura | 14.1 × 22.0 | 8.2 |
| [fisica_expo_01](fisica_expo_01.png) ([SVG](fisica_expo_01.svg)) | Physical View 01 — Sources, Ingestion and Messaging | apaisada | tabla en esta guía | 20.2 × 13.6 | 9.0 |
| [fisica_expo_02](fisica_expo_02.png) ([SVG](fisica_expo_02.svg)) | Physical View 02 — Assisted Diagnosis Runtime | vertical | en la figura | 15.5 × 21.9 | 9.0 |
| [fisica_expo_03](fisica_expo_03.png) ([SVG](fisica_expo_03.svg)) | Physical View 03 — Access, Persistence and Human Review | vertical | en la figura | 15.9 × 21.9 | 8.7 |
| [c4_expo_2a](c4_expo_2a.png) ([SVG](c4_expo_2a.svg)) | C4 Level 2A — Ingestion and AIOps Processing | apaisada | tabla en esta guía | 24.2 × 14.0 | 8.1 |
| [c4_expo_2b](c4_expo_2b.png) ([SVG](c4_expo_2b.svg)) | C4 Level 2B — Consumption, Governance and Persistence | apaisada | tabla en esta guía | 24.2 × 14.0 | 8.1 |
| [c4_component_diagnostic](c4_component_diagnostic.png) ([SVG](c4_component_diagnostic.svg)) | C4 Level 3 — Diagnostic Components | apaisada | tabla en esta guía | 24.4 × 13.0 | 9.0 |

## Relaciones de fisica_expo_01

Physical View 01 — Sources, Ingestion and Messaging. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Workflow events | HTTPS/Webhook |
| 02 | Azure Service Bus → Pipeline Service | Execution context | Azure Service Bus |
| 03 | Azure Service Bus → Log/Event Service | Normalized evidence | Azure Service Bus |
| 04 | Ingestion and Normalization Service → GitHub Actions | Queries logs and artifacts | GitHub API/HTTPS |
| 05 | Ingestion and Normalization Service → Azure Service Bus | Protected evidence | Azure Service Bus |
| 06 | GitHub → GitHub Actions | Repository and workflows | GitHub API/HTTPS |
| 07 | Compatible Observability and Runtime Sources → Ingestion and Normalization Service | Authorized telemetry | REST/HTTPS |
| 08 | Ingestion and Normalization Service → GitHub | Connects and verifies GitHub access | OAuth/HTTPS + REST/HTTPS |
| 09 | Ingestion and Normalization Service → Azure Key Vault | Signing keys, App material, token custody | Azure Key Vault API/HTTPS |
| 10 | Pipeline Service → Azure Key Vault | Signs workload tokens | Azure Key Vault API/HTTPS |
| 11 | Log/Event Service → Azure Key Vault | Signs workload tokens | Azure Key Vault API/HTTPS |
| 12 | Pipeline Service → Ingestion and Normalization Service | Verifies GitHub user access | REST/HTTPS |
| 13 | Log/Event Service → Pipeline Service | Checks ORIGIN membership | REST/HTTPS |
| 14 | Pipeline Service → Ingestion and Normalization Service | Checks capture scope | REST/HTTPS |

## Relaciones de c4_expo_2a

C4 Level 2A — Ingestion and AIOps Processing. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Without stereotypes: blue boxes are containers of the prototype, gray boxes are people and external systems, the green cylinder is a data container and the dashed frame is the system boundary. PostgreSQL/pgvector: one physical instance (ADR-018).

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Workflow events | HTTPS/Webhook |
| 02 | Azure Service Bus → Pipeline Service | Execution context | Azure Service Bus |
| 03 | Azure Service Bus → Log/Event Service | Normalized evidence | Azure Service Bus |
| 04 | Ingestion and Normalization Service → PostgreSQL | Metadata / protected buffer | PostgreSQL |
| 05 | Pipeline Service → PostgreSQL | Persists pipeline context | PostgreSQL |
| 06 | Log/Event Service → PostgreSQL | Evidence references | PostgreSQL |
| 07 | Diagnostic & Recommendation Service → PostgreSQL | Diagnosis and recommendations | PostgreSQL |
| 08 | Ingestion and Normalization Service → GitHub Actions | Queries logs and artifacts | GitHub API/HTTPS |
| 09 | Ingestion and Normalization Service → Azure Service Bus | Publishes protected evidence | Azure Service Bus |
| 10 | Azure Service Bus → NLP Log Processing | Events for NLP | Azure Service Bus |
| 11 | NLP Log Processing → Evidence Correlation Service | Processed evidence | REST/HTTPS |
| 12 | Evidence Correlation Service → PostgreSQL | Context and traceability | PostgreSQL |
| 13 | RAG Knowledge Retrieval → PostgreSQL | Semantic retrieval | PostgreSQL/pgvector |
| 14 | RAG Knowledge Retrieval → Azure OpenAI Service | Generates embeddings | Azure OpenAI API v1/HTTPS |
| 15 | Compatible Observability and Runtime Sources → Ingestion and Normalization Service | Authorized telemetry | REST/HTTPS |
| 16 | Evidence Correlation Service → Diagnostic & Recommendation Service | Correlated context | REST/HTTPS |
| 17 | Diagnostic & Recommendation Service → RAG Knowledge Retrieval | Requests RAG knowledge | REST/HTTPS |
| 18 | Diagnostic & Recommendation Service → Azure OpenAI Service | Inference with evidence and RAG | Azure OpenAI API/HTTPS |
| 19 | Diagnostic & Recommendation Service → PostgreSQL | Persists human review | PostgreSQL |
| 20 | GitHub Actions → Diagnostic & Recommendation Service | Queries result for artifact | REST/HTTPS |
| 21 | Pipeline Service → Ingestion and Normalization Service | Verifies GitHub user access | REST/HTTPS |
| 22 | Log/Event Service → Pipeline Service | Checks ORIGIN membership | REST/HTTPS |
| 23 | Pipeline Service → Ingestion and Normalization Service | Checks capture scope | REST/HTTPS |
| 24 | Evidence Correlation Service → Pipeline Service | Verifies ORIGIN | REST/HTTPS |
| 25 | Evidence Correlation Service → Log/Event Service | Verifies scoped evidence | REST/HTTPS |
| 26 | Diagnostic & Recommendation Service → Pipeline Service | Resolves diagnosis access | REST/HTTPS |
| 27 | Diagnostic & Recommendation Service → Pipeline Service | Projects diagnosis summary | REST/HTTPS |

## Relaciones de c4_expo_2b

C4 Level 2B — Consumption, Governance and Persistence. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Without stereotypes: blue boxes are containers of the prototype, gray boxes are people and external systems, the green cylinder is a data container and the dashed frame is the system boundary.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | Pipeline Service → PostgreSQL | Persists pipeline context | PostgreSQL |
| 02 | Log/Event Service → PostgreSQL | Evidence references | PostgreSQL |
| 03 | Diagnostic & Recommendation Service → PostgreSQL | Diagnosis and recommendations | PostgreSQL |
| 04 | GitHub → GitHub Actions | Repository and workflows | GitHub API/HTTPS |
| 05 | Technical Users → AIOps Web Dashboard | Querying and human review | HTTPS |
| 06 | AIOps Web Dashboard → GitHub | GitHub sign-in (OAuth + PKCE) | OAuth 2.0/HTTPS (authorization code + PKCE S256) |
| 07 | AIOps Web Dashboard → Pipeline Service | Queries pipelines and executions | REST/HTTPS |
| 08 | AIOps Web Dashboard → Log/Event Service | Queries logs and evidence | REST/HTTPS |
| 09 | AIOps Web Dashboard → Diagnostic & Recommendation Service | Diagnosis and review | REST/HTTPS |
| 10 | Diagnostic & Recommendation Service → PostgreSQL | Persists human review | PostgreSQL |
| 11 | GitHub Actions → Diagnostic & Recommendation Service | Queries result for artifact | REST/HTTPS |
| 12 | Log/Event Service → Pipeline Service | Checks ORIGIN membership | REST/HTTPS |
| 13 | Diagnostic & Recommendation Service → Pipeline Service | Resolves diagnosis access | REST/HTTPS |
| 14 | Diagnostic & Recommendation Service → Pipeline Service | Projects diagnosis summary | REST/HTTPS |

## Relaciones de c4_component_diagnostic

C4 Level 3 — Diagnostic Components. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | AIOps Web Dashboard → Diagnostic API | Routes diagnosis and review queries and operations | REST/HTTPS |
| 02 | Evidence Correlation Service → Diagnostic API | Delivers correlated context for diagnosis | REST/HTTPS |
| 03 | Diagnostic Orchestrator → RAG Knowledge Retrieval | Requests authorized contextual knowledge | REST/HTTPS |
| 04 | Diagnostic Orchestrator → Azure OpenAI Service | Requests diagnostic inference with RAG context | Azure OpenAI API/HTTPS |
| 05 | Diagnostic Output Composer → PostgreSQL | Persists diagnosis, recommendations and evidence links | PostgreSQL |
| 06 | Diagnostic API → Human Review & Diagnostic Governance | Delegates diagnosis recording and human validation | in-process |
| 07 | GitHub Actions → Diagnostic API | Queries diagnostic output for native artifact publication | REST/HTTPS |
| 08 | Human Review & Diagnostic Governance → PostgreSQL | Persists human review decisions and traceability | PostgreSQL |
| 09 | Diagnostic API → Diagnostic Orchestrator | Delegates diagnosis generation | in-process |
| 10 | Diagnostic Orchestrator → Diagnostic Output Composer | Delivers inference results and contextual evidence | in-process |
