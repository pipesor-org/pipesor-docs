# Navegación C4 → diseño de clases

Modelo 1.2.0 — CD-1..CD-3: diseño propuesto; CD-4 en adelante: código implementado

SSOT: `model/design.yml`. Las figuras C4 existentes conservan su modelo y membresía. Cada clase marca su
estado de implementación (`implementation.status`) con la evidencia de `model/implementation_status.yml`.

## CD-1 — Diagnostic API and CQRS

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → [`c4_component_diagnostic`](c4_component_diagnostic.svg) → `diagnostic_api_component` → [CD-1](CD-1.svg)

Zoom-In: `diagnostic_api_component`; 15 clases/nodos, incluidos proxies.

## CD-2 — Diagnostic Orchestration, RAG and LLM

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → [`c4_component_diagnostic`](c4_component_diagnostic.svg) → `diagnostic_orchestrator_component` → [CD-2](CD-2.svg)

Zoom-In: `diagnostic_orchestrator_component`; 15 clases/nodos, incluidos proxies.

## CD-3 — Human Review and Diagnostic Governance

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → [`c4_component_diagnostic`](c4_component_diagnostic.svg) → `human_review_component` → [CD-3](CD-3.svg)

Zoom-In: `human_review_component`; 14 clases/nodos, incluidos proxies.

## CD-4 — Pipeline: Incident aggregate

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `pipeline_service` → [CD-4](CD-4.svg)

Zoom-In: `pipeline_service`; 15 clases/nodos, incluidos proxies.

## CD-5 — Ingestion: GitHubConnection aggregate

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `ingestion_normalization_service` → [CD-5](CD-5.svg)

Zoom-In: `ingestion_normalization_service`; 14 clases/nodos, incluidos proxies.

## CD-6 — Ingestion: CaptureReceipt aggregate and WorkflowObservation

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `ingestion_normalization_service` → [CD-6](CD-6.svg)

Zoom-In: `ingestion_normalization_service`; 12 clases/nodos, incluidos proxies.

## CD-7 — Log/Event: evidence registration without an aggregate

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `log_event_service` → [CD-7](CD-7.svg)

Zoom-In: `log_event_service`; 7 clases/nodos, incluidos proxies.

## CD-8 — Correlation: CorrelationGroup aggregate

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `evidence_correlation_engine` → [CD-8](CD-8.svg)

Zoom-In: `evidence_correlation_engine`; 8 clases/nodos, incluidos proxies.

## CD-9 — Recommendation: implemented records against the proposed aggregates

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `recommendation_service` → [CD-9](CD-9.svg)

Zoom-In: `recommendation_service`; 15 clases/nodos, incluidos proxies.

## CD-10 — NLP: protected evidence value objects

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `nlp_log_processor` → [CD-10](CD-10.svg)

Zoom-In: `nlp_log_processor`; 10 clases/nodos, incluidos proxies.

## CD-11 — RAG: knowledge chunks and SQLAlchemy records

[C4 Context (`c4_context`)](c4_context.svg) → [`c4_container_processing`](c4_container_processing.svg) → `rag_retrieval` → [CD-11](CD-11.svg)

Zoom-In: `rag_retrieval`; 12 clases/nodos, incluidos proxies.

`diagnostic_output_component` se realiza dentro de CD-2 por `DiagnosticOutputComposer` y su dominio interno.

La vista `c4_component_diagnostic` amplía `recommendation_service` desde `c4_container_processing`.

Las clases compartidas de CD-1 son referencias al mismo diseño detallado en CD-2/CD-3; se cuentan en cada figura.

CD-4..CD-11 amplían cada contenedor desde `c4_container_processing`: raíces de agregado, entidades y value
objects del código, con su persistencia en `model/domain.yml` y referencias `archivo:línea`.
