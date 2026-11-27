# Figuras para documentos

Variantes de impresión de las vistas de presentación, del C4 (contexto, contenedores y componentes), del
modelo de datos por contexto, de las clases, de las secuencias y del despliegue. Se generan desde los mismos
modelos que las vistas completas. El color y una marca de texto indican el estado de implementación según
model/implementation_status.yml (rojo: modelado, no implementado; ámbar: en parte; violeta: de otra forma);
la figura no acredita comportamiento en runtime. Cuando una vista no cabe legible en una página se divide
en partes numeradas; la vista completa sigue en out/.

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
| [c4_context](c4_context.png) ([SVG](c4_context.svg)) | C4 Level 1 — System Context | apaisada | tabla en esta guía | 24.5 × 12.2 | 9.0 |
| [c4_component_diagnostic](c4_component_diagnostic.png) ([SVG](c4_component_diagnostic.svg)) | C4 Level 3 — Diagnostic Components | apaisada | tabla en esta guía | 23.8 × 14.0 | 8.7 |
| [c4_component_ingestion_capture](c4_component_ingestion_capture.png) ([SVG](c4_component_ingestion_capture.svg)) | C4 Level 3 — Ingestion Components (1/2: capture and publication) | apaisada | tabla en esta guía | 24.6 × 12.7 | 8.2 |
| [c4_component_ingestion_identity](c4_component_ingestion_identity.png) ([SVG](c4_component_ingestion_identity.svg)) | C4 Level 3 — Ingestion Components (2/2: sign-in and GitHub connector) | vertical | en la figura | 14.1 × 22.0 | 8.4 |
| [er_ops_catalog](er_ops_catalog.png) ([SVG](er_ops_catalog.svg)) | ER — ops (1/2: catalog, executions and access grants) | vertical | en la figura | 13.2 × 18.6 | 9.0 |
| [er_ops_incidents](er_ops_incidents.png) ([SVG](er_ops_incidents.svg)) | ER — ops (2/2: incidents and the incident queue read model) | apaisada | en la figura | 16.3 × 10.5 | 9.0 |
| [er_evidence_audit](er_evidence_audit.png) ([SVG](er_evidence_audit.svg)) | ER — evidence (Log/Event and Correlation) and audit | apaisada | en la figura | 24.6 × 12.7 | 8.8 |
| [er_diagnosis_intake](er_diagnosis_intake.png) ([SVG](er_diagnosis_intake.svg)) | ER — diagnosis (1/3: correlated context intake and diagnosis job queue) | vertical | en la figura | 15.1 × 7.7 | 9.0 |
| [er_diagnosis](er_diagnosis.png) ([SVG](er_diagnosis.svg)) | ER — diagnosis (2/3: diagnoses, human reviews and summary outbox) | apaisada | en la figura | 24.6 × 10.4 | 8.6 |
| [er_diagnosis_modeled](er_diagnosis_modeled.png) ([SVG](er_diagnosis_modeled.svg)) | ER — diagnosis (3/3: tables modeled but not created by any migration) | vertical | en la figura | 15.0 × 13.6 | 9.0 |
| [er_knowledge](er_knowledge.png) ([SVG](er_knowledge.svg)) | ER — knowledge (RAG Knowledge Retrieval) | vertical | en la figura | 15.7 × 8.2 | 9.0 |
| [er_ingestion_connection](er_ingestion_connection.png) ([SVG](er_ingestion_connection.svg)) | ER — ingestion (1/2: GitHub connection, sign-in and consent) | vertical | en la figura | 15.6 × 22.0 | 8.9 |
| [er_ingestion_capture](er_ingestion_capture.png) ([SVG](er_ingestion_capture.svg)) | ER — ingestion (2/2: admission, capture and publication) | apaisada | en la figura | 17.2 × 14.0 | 8.3 |
| [CD-1a](CD-1a.png) ([SVG](CD-1a.svg)) | CD-1a — Diagnostic API and CQRS (1/4: diagnosis command side) | vertical | en la figura | 15.6 × 18.6 | 9.0 |
| [CD-1b](CD-1b.png) ([SVG](CD-1b.svg)) | CD-1b — Diagnostic API and CQRS (2/4: diagnosis query contract) | vertical | en la figura | 15.4 × 16.3 | 9.0 |
| [CD-1c](CD-1c.png) ([SVG](CD-1c.svg)) | CD-1c — Diagnostic API and CQRS (3/4: diagnosis query projection) | vertical | en la figura | 15.6 × 14.3 | 9.0 |
| [CD-1d](CD-1d.png) ([SVG](CD-1d.svg)) | CD-1d — Diagnostic API and CQRS (4/4: human review entry points) | apaisada | en la figura | 16.8 × 13.0 | 9.0 |
| [CD-2a](CD-2a.png) ([SVG](CD-2a.svg)) | CD-2a — Diagnostic Orchestration, RAG and LLM (1/6: RAG retrieval port and adapter) | vertical | en la figura | 14.8 × 19.8 | 9.0 |
| [CD-2b](CD-2b.png) ([SVG](CD-2b.svg)) | CD-2b — Diagnostic Orchestration, RAG and LLM (2/6: LLM gateway and Azure OpenAI adapter) | vertical | en la figura | 15.1 × 22.0 | 8.1 |
| [CD-2c](CD-2c.png) ([SVG](CD-2c.svg)) | CD-2c — Diagnostic Orchestration, RAG and LLM (3/6: output composition) | vertical | en la figura | 11.5 × 22.0 | 8.5 |
| [CD-2d](CD-2d.png) ([SVG](CD-2d.svg)) | CD-2d — Diagnostic Orchestration, RAG and LLM (4/6: response translation and probable cause) | vertical | en la figura | 15.6 × 21.0 | 9.0 |
| [CD-2e](CD-2e.png) ([SVG](CD-2e.svg)) | CD-2e — Diagnostic Orchestration, RAG and LLM (5/6: snapshot persistence) | apaisada | en la figura | 24.0 × 14.0 | 8.4 |
| [CD-2f](CD-2f.png) ([SVG](CD-2f.svg)) | CD-2f — Diagnostic Orchestration, RAG and LLM (6/6: repository port) | vertical | en la figura | 13.2 × 21.1 | 9.0 |
| [CD-3a](CD-3a.png) ([SVG](CD-3a.svg)) | CD-3a — Human Review and Diagnostic Governance (1/5: review command) | vertical | en la figura | 15.9 × 19.1 | 8.6 |
| [CD-3b](CD-3b.png) ([SVG](CD-3b.svg)) | CD-3b — Human Review and Diagnostic Governance (2/5: audit trail) | vertical | en la figura | 13.0 × 18.9 | 9.0 |
| [CD-3c](CD-3c.png) ([SVG](CD-3c.svg)) | CD-3c — Human Review and Diagnostic Governance (3/5: review query contract) | apaisada | en la figura | 17.3 × 12.1 | 9.0 |
| [CD-3d](CD-3d.png) ([SVG](CD-3d.svg)) | CD-3d — Human Review and Diagnostic Governance (4/5: review query projection) | vertical | en la figura | 15.1 × 21.2 | 9.0 |
| [CD-3e](CD-3e.png) ([SVG](CD-3e.svg)) | CD-3e — Human Review and Diagnostic Governance (5/5: review aggregate and persistence) | vertical | en la figura | 14.3 × 21.4 | 9.0 |
| [CD-4a](CD-4a.png) ([SVG](CD-4a.svg)) | CD-4a — Pipeline: Incident aggregate (1/5: root and its value objects) | vertical | en la figura | 15.9 × 19.1 | 9.0 |
| [CD-4b](CD-4b.png) ([SVG](CD-4b.svg)) | CD-4b — Pipeline: Incident aggregate (2/5: transitions) | vertical | en la figura | 12.4 × 19.2 | 9.0 |
| [CD-4c](CD-4c.png) ([SVG](CD-4c.svg)) | CD-4c — Pipeline: Incident aggregate (3/5: enums and repository catalog) | vertical | en la figura | 15.0 × 22.0 | 8.8 |
| [CD-4d](CD-4d.png) ([SVG](CD-4d.svg)) | CD-4d — Pipeline: Incident aggregate (4/5: store port) | vertical | en la figura | 15.4 × 20.9 | 9.0 |
| [CD-4e](CD-4e.png) ([SVG](CD-4e.svg)) | CD-4e — Pipeline: Incident aggregate (5/5: JPA rows) | vertical | en la figura | 14.4 × 21.3 | 9.0 |
| [CD-5a](CD-5a.png) ([SVG](CD-5a.svg)) | CD-5a — Ingestion: GitHubConnection aggregate (1/7: root record) | vertical | en la figura | 15.4 × 16.4 | 9.0 |
| [CD-5b](CD-5b.png) ([SVG](CD-5b.svg)) | CD-5b — Ingestion: GitHubConnection aggregate (2/7: repository) | vertical | en la figura | 15.4 × 21.7 | 9.0 |
| [CD-5c](CD-5c.png) ([SVG](CD-5c.svg)) | CD-5c — Ingestion: GitHubConnection aggregate (3/7: generations) | vertical | en la figura | 15.9 × 14.2 | 8.4 |
| [CD-5d](CD-5d.png) ([SVG](CD-5d.svg)) | CD-5d — Ingestion: GitHubConnection aggregate (4/7: generation and root value objects) | vertical | en la figura | 15.2 × 22.0 | 8.1 |
| [CD-5e](CD-5e.png) ([SVG](CD-5e.svg)) | CD-5e — Ingestion: GitHubConnection aggregate (5/7: authorization attempts) | vertical | en la figura | 15.9 × 15.0 | 8.6 |
| [CD-5f](CD-5f.png) ([SVG](CD-5f.svg)) | CD-5f — Ingestion: GitHubConnection aggregate (6/7: attempt value objects) | vertical | en la figura | 15.9 × 16.8 | 8.1 |
| [CD-5g](CD-5g.png) ([SVG](CD-5g.svg)) | CD-5g — Ingestion: GitHubConnection aggregate (7/7: credential operations) | apaisada | en la figura | 21.2 × 14.0 | 8.0 |
| [CD-6a](CD-6a.png) ([SVG](CD-6a.svg)) | CD-6a — Ingestion: CaptureReceipt aggregate and WorkflowObservation (1/8: receipt and scope) | vertical | en la figura | 13.8 × 22.0 | 8.6 |
| [CD-6b](CD-6b.png) ([SVG](CD-6b.svg)) | CD-6b — Ingestion: CaptureReceipt aggregate and WorkflowObservation (2/8: ledger port) | vertical | en la figura | 13.7 × 21.2 | 9.0 |
| [CD-6c](CD-6c.png) ([SVG](CD-6c.svg)) | CD-6c — Ingestion: CaptureReceipt aggregate and WorkflowObservation (3/8: prepared observation check) | apaisada | en la figura | 21.2 × 14.0 | 8.6 |
| [CD-6d](CD-6d.png) ([SVG](CD-6d.svg)) | CD-6d — Ingestion: CaptureReceipt aggregate and WorkflowObservation (4/8: observation persistence) | vertical | en la figura | 13.7 × 21.3 | 9.0 |
| [CD-6e](CD-6e.png) ([SVG](CD-6e.svg)) | CD-6e — Ingestion: CaptureReceipt aggregate and WorkflowObservation (5/8: scope to capture context) | vertical | en la figura | 13.7 × 17.8 | 9.0 |
| [CD-6f](CD-6f.png) ([SVG](CD-6f.svg)) | CD-6f — Ingestion: CaptureReceipt aggregate and WorkflowObservation (6/8: capture context and pipeline) | vertical | en la figura | 13.8 × 19.6 | 9.0 |
| [CD-6g](CD-6g.png) ([SVG](CD-6g.svg)) | CD-6g — Ingestion: CaptureReceipt aggregate and WorkflowObservation (7/8: execution and stages) | apaisada | en la figura | 24.0 × 14.0 | 8.6 |
| [CD-6h](CD-6h.png) ([SVG](CD-6h.svg)) | CD-6h — Ingestion: CaptureReceipt aggregate and WorkflowObservation (8/8: failure and evidence) | vertical | en la figura | 13.7 × 19.9 | 9.0 |
| [CD-7a](CD-7a.png) ([SVG](CD-7a.svg)) | CD-7a — Log/Event: evidence registration without an aggregate (1/2: registration) | vertical | en la figura | 13.4 × 22.0 | 8.3 |
| [CD-7b](CD-7b.png) ([SVG](CD-7b.svg)) | CD-7b — Log/Event: evidence registration without an aggregate (2/2: evidence value objects) | vertical | en la figura | 15.9 × 16.9 | 9.0 |
| [CD-8a](CD-8a.png) ([SVG](CD-8a.svg)) | CD-8a — Correlation: CorrelationGroup aggregate (1/4: group and contribution) | apaisada | en la figura | 24.4 × 12.7 | 9.0 |
| [CD-8b](CD-8b.png) ([SVG](CD-8b.svg)) | CD-8b — Correlation: CorrelationGroup aggregate (2/4: contribution value objects) | vertical | en la figura | 14.8 × 16.5 | 9.0 |
| [CD-8c](CD-8c.png) ([SVG](CD-8c.svg)) | CD-8c — Correlation: CorrelationGroup aggregate (3/4: durable store) | apaisada | en la figura | 24.6 × 10.7 | 8.3 |
| [CD-8d](CD-8d.png) ([SVG](CD-8d.svg)) | CD-8d — Correlation: CorrelationGroup aggregate (4/4: correlated context snapshot) | vertical | en la figura | 12.3 × 22.0 | 8.8 |
| [CD-9a](CD-9a.png) ([SVG](CD-9a.svg)) | CD-9a — Recommendation: implemented records against the proposed aggregates (1/6: diagnosis record, hypothesis and model) | vertical | en la figura | 13.4 × 22.0 | 8.5 |
| [CD-9b](CD-9b.png) ([SVG](CD-9b.svg)) | CD-9b — Recommendation: implemented records against the proposed aggregates (2/6: cited evidence and sources) | vertical | en la figura | 14.3 × 16.6 | 9.0 |
| [CD-9c](CD-9c.png) ([SVG](CD-9c.svg)) | CD-9c — Recommendation: implemented records against the proposed aggregates (3/6: review record) | vertical | en la figura | 14.2 × 20.5 | 9.0 |
| [CD-9d](CD-9d.png) ([SVG](CD-9d.svg)) | CD-9d — Recommendation: implemented records against the proposed aggregates (4/6: review submission) | vertical | en la figura | 14.2 × 11.0 | 9.0 |
| [CD-9e](CD-9e.png) ([SVG](CD-9e.svg)) | CD-9e — Recommendation: implemented records against the proposed aggregates (5/6: correlated context receipts) | vertical | en la figura | 15.6 × 14.0 | 9.0 |
| [CD-9f](CD-9f.png) ([SVG](CD-9f.svg)) | CD-9f — Recommendation: implemented records against the proposed aggregates (6/6: jobs and outbox) | vertical | en la figura | 14.8 × 11.0 | 9.0 |
| [CD-10a](CD-10a.png) ([SVG](CD-10a.svg)) | CD-10a — NLP: protected evidence value objects (1/3: inbound protected evidence) | vertical | en la figura | 14.2 × 22.0 | 8.1 |
| [CD-10b](CD-10b.png) ([SVG](CD-10b.svg)) | CD-10b — NLP: protected evidence value objects (2/3: outbound correlation evidence) | vertical | en la figura | 15.9 × 19.7 | 9.0 |
| [CD-10c](CD-10c.png) ([SVG](CD-10c.svg)) | CD-10c — NLP: protected evidence value objects (3/3: log processing) | vertical | en la figura | 13.2 × 13.1 | 9.0 |
| [CD-11a](CD-11a.png) ([SVG](CD-11a.svg)) | CD-11a — RAG: knowledge chunks and SQLAlchemy records (1/5: knowledge chunk) | vertical | en la figura | 15.8 × 17.6 | 9.0 |
| [CD-11b](CD-11b.png) ([SVG](CD-11b.svg)) | CD-11b — RAG: knowledge chunks and SQLAlchemy records (2/5: retrieval repository) | apaisada | en la figura | 24.3 × 12.7 | 9.0 |
| [CD-11c](CD-11c.png) ([SVG](CD-11c.svg)) | CD-11c — RAG: knowledge chunks and SQLAlchemy records (3/5: SQLAlchemy records) | vertical | en la figura | 15.4 × 21.4 | 9.0 |
| [CD-11d](CD-11d.png) ([SVG](CD-11d.svg)) | CD-11d — RAG: knowledge chunks and SQLAlchemy records (4/5: corpus store) | apaisada | en la figura | 24.6 × 13.8 | 8.6 |
| [CD-11e](CD-11e.png) ([SVG](CD-11e.svg)) | CD-11e — RAG: knowledge chunks and SQLAlchemy records (5/5: corpus import) | vertical | en la figura | 15.6 × 22.0 | 8.4 |
| [seq_a1_capture_p1](seq_a1_capture_p1.png) ([SVG](seq_a1_capture_p1.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 1 of 11) | vertical | en la figura | 15.1 × 12.8 | 9.0 |
| [seq_a1_capture_p2](seq_a1_capture_p2.png) ([SVG](seq_a1_capture_p2.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 2 of 11) | vertical | en la figura | 15.1 × 20.7 | 9.0 |
| [seq_a1_capture_p3](seq_a1_capture_p3.png) ([SVG](seq_a1_capture_p3.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 3 of 11) | vertical | en la figura | 15.1 × 16.1 | 9.0 |
| [seq_a1_capture_p4](seq_a1_capture_p4.png) ([SVG](seq_a1_capture_p4.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 4 of 11) | vertical | en la figura | 15.5 × 22.0 | 9.0 |
| [seq_a1_capture_p5](seq_a1_capture_p5.png) ([SVG](seq_a1_capture_p5.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 5 of 11) | vertical | en la figura | 15.1 × 21.1 | 9.0 |
| [seq_a1_capture_p6](seq_a1_capture_p6.png) ([SVG](seq_a1_capture_p6.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 6 of 11) | vertical | en la figura | 15.6 × 18.8 | 9.0 |
| [seq_a1_capture_p7](seq_a1_capture_p7.png) ([SVG](seq_a1_capture_p7.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 7 of 11) | vertical | en la figura | 15.4 × 22.0 | 8.2 |
| [seq_a1_capture_p8](seq_a1_capture_p8.png) ([SVG](seq_a1_capture_p8.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 8 of 11) | vertical | en la figura | 15.9 × 21.7 | 9.0 |
| [seq_a1_capture_p9](seq_a1_capture_p9.png) ([SVG](seq_a1_capture_p9.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 9 of 11) | vertical | en la figura | 15.1 × 12.3 | 9.0 |
| [seq_a1_capture_p10](seq_a1_capture_p10.png) ([SVG](seq_a1_capture_p10.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 10 of 11) | vertical | en la figura | 15.9 × 19.4 | 9.0 |
| [seq_a1_capture_p11](seq_a1_capture_p11.png) ([SVG](seq_a1_capture_p11.svg)) | CI/CD failure capture: from the GitHub Actions webhook to the Recommendation receipt (part 11 of 11) | vertical | en la figura | 15.9 × 22.0 | 8.9 |
| [seq_a2_diagnosis_p1](seq_a2_diagnosis_p1.png) ([SVG](seq_a2_diagnosis_p1.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 1 of 6) | vertical | en la figura | 15.1 × 15.8 | 9.0 |
| [seq_a2_diagnosis_p2](seq_a2_diagnosis_p2.png) ([SVG](seq_a2_diagnosis_p2.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 2 of 6) | vertical | en la figura | 15.1 × 15.4 | 9.0 |
| [seq_a2_diagnosis_p3](seq_a2_diagnosis_p3.png) ([SVG](seq_a2_diagnosis_p3.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 3 of 6) | vertical | en la figura | 14.8 × 22.0 | 8.5 |
| [seq_a2_diagnosis_p4](seq_a2_diagnosis_p4.png) ([SVG](seq_a2_diagnosis_p4.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 4 of 6) | vertical | en la figura | 15.5 × 20.4 | 9.0 |
| [seq_a2_diagnosis_p5](seq_a2_diagnosis_p5.png) ([SVG](seq_a2_diagnosis_p5.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 5 of 6) | vertical | en la figura | 15.1 × 21.1 | 9.0 |
| [seq_a2_diagnosis_p6](seq_a2_diagnosis_p6.png) ([SVG](seq_a2_diagnosis_p6.svg)) | Assisted diagnosis: job, RAG retrieval, Azure OpenAI inference and summary projection (part 6 of 6) | vertical | en la figura | 14.8 × 22.0 | 8.8 |
| [seq_a3_review_p1](seq_a3_review_p1.png) ([SVG](seq_a3_review_p1.svg)) | Human review and diagnosis report: dashboard, Pipeline entitlement and GitHub Actions artifact (part 1 of 5) | vertical | en la figura | 15.1 × 14.8 | 9.0 |
| [seq_a3_review_p2](seq_a3_review_p2.png) ([SVG](seq_a3_review_p2.svg)) | Human review and diagnosis report: dashboard, Pipeline entitlement and GitHub Actions artifact (part 2 of 5) | vertical | en la figura | 15.9 × 19.6 | 8.8 |
| [seq_a3_review_p3](seq_a3_review_p3.png) ([SVG](seq_a3_review_p3.svg)) | Human review and diagnosis report: dashboard, Pipeline entitlement and GitHub Actions artifact (part 3 of 5) | vertical | en la figura | 15.1 × 14.7 | 9.0 |
| [seq_a3_review_p4](seq_a3_review_p4.png) ([SVG](seq_a3_review_p4.svg)) | Human review and diagnosis report: dashboard, Pipeline entitlement and GitHub Actions artifact (part 4 of 5) | vertical | en la figura | 15.1 × 20.7 | 9.0 |
| [seq_a3_review_p5](seq_a3_review_p5.png) ([SVG](seq_a3_review_p5.svg)) | Human review and diagnosis report: dashboard, Pipeline entitlement and GitHub Actions artifact (part 5 of 5) | vertical | en la figura | 15.8 × 22.0 | 8.5 |
| [seq_b_login_p1](seq_b_login_p1.png) ([SVG](seq_b_login_p1.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 1 of 10) | vertical | en la figura | 15.9 × 17.3 | 8.6 |
| [seq_b_login_p2](seq_b_login_p2.png) ([SVG](seq_b_login_p2.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 2 of 10) | vertical | en la figura | 15.1 × 16.2 | 9.0 |
| [seq_b_login_p3](seq_b_login_p3.png) ([SVG](seq_b_login_p3.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 3 of 10) | vertical | en la figura | 15.3 × 12.0 | 9.0 |
| [seq_b_login_p4](seq_b_login_p4.png) ([SVG](seq_b_login_p4.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 4 of 10) | vertical | en la figura | 15.1 × 12.1 | 9.0 |
| [seq_b_login_p5](seq_b_login_p5.png) ([SVG](seq_b_login_p5.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 5 of 10) | vertical | en la figura | 15.1 × 15.2 | 9.0 |
| [seq_b_login_p6](seq_b_login_p6.png) ([SVG](seq_b_login_p6.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 6 of 10) | vertical | en la figura | 15.9 × 21.7 | 8.1 |
| [seq_b_login_p7](seq_b_login_p7.png) ([SVG](seq_b_login_p7.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 7 of 10) | vertical | en la figura | 15.9 × 21.8 | 8.4 |
| [seq_b_login_p8](seq_b_login_p8.png) ([SVG](seq_b_login_p8.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 8 of 10) | vertical | en la figura | 15.1 × 18.9 | 9.0 |
| [seq_b_login_p9](seq_b_login_p9.png) ([SVG](seq_b_login_p9.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 9 of 10) | vertical | en la figura | 15.9 × 14.3 | 8.1 |
| [seq_b_login_p10](seq_b_login_p10.png) ([SVG](seq_b_login_p10.svg)) | GitHub sign-in with recorded consent, PKCE and Pipesor session token (part 10 of 10) | vertical | en la figura | 15.1 × 18.9 | 9.0 |
| [deploy_dev_runtime](deploy_dev_runtime.png) ([SVG](deploy_dev_runtime.svg)) | Despliegue del entorno dev en Azure | apaisada | tabla en [despliegue_guia.md](../despliegue_guia.md) | 24.6 × 13.9 | 8.5 |
| [deploy_environments_delivery](deploy_environments_delivery.png) ([SVG](deploy_environments_delivery.svg)) | Entornos y entrega de imágenes | apaisada | tabla en [despliegue_guia.md](../despliegue_guia.md) | 22.4 × 14.0 | 8.4 |

## Relaciones de fisica_expo_01

Physical View 01 — Sources, Ingestion and Messaging. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Workflow events | HTTPS/Webhook |
| 02 | Azure Service Bus → Pipeline Service | Execution context | Azure Service Bus |
| 03 | Azure Service Bus → Log/Event Service | Normalized evidence | Azure Service Bus |
| 04 | Ingestion and Normalization Service → GitHub Actions | Queries runs, jobs and logs | GitHub API/HTTPS |
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

C4 Level 2A — Ingestion and AIOps Processing. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Without stereotypes: blue boxes are containers of the prototype, gray boxes are people and external systems, the green cylinder is a data container and the dashed frame is the system boundary. Implementation state (model/implementation_status.yml): red = modeled, not implemented; amber = partially implemented; violet = implemented differently; unmarked = implemented or external. PostgreSQL/pgvector: one physical instance (ADR-018).

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Workflow events | HTTPS/Webhook |
| 02 | Azure Service Bus → Pipeline Service | Execution context | Azure Service Bus |
| 03 | Azure Service Bus → Log/Event Service | Normalized evidence | Azure Service Bus · partial |
| 04 | Ingestion and Normalization Service → PostgreSQL | Metadata / protected buffer | PostgreSQL |
| 05 | Pipeline Service → PostgreSQL | Persists pipeline context | PostgreSQL |
| 06 | Log/Event Service → PostgreSQL | Evidence references | PostgreSQL |
| 07 | Diagnostic & Recommendation Service → PostgreSQL | Diagnosis and recommendations | PostgreSQL |
| 08 | Ingestion and Normalization Service → GitHub Actions | Queries runs, jobs and logs | GitHub API/HTTPS |
| 09 | Ingestion and Normalization Service → Azure Service Bus | Publishes protected evidence | Azure Service Bus |
| 10 | Azure Service Bus → NLP Log Processing | Events for NLP | Azure Service Bus |
| 11 | NLP Log Processing → Evidence Correlation Service | Processed evidence | REST/HTTPS |
| 12 | Evidence Correlation Service → PostgreSQL | Context and traceability | PostgreSQL |
| 13 | RAG Knowledge Retrieval → PostgreSQL | Semantic retrieval | PostgreSQL/pgvector |
| 14 | RAG Knowledge Retrieval → Azure OpenAI Service | Generates embeddings | Azure OpenAI API v1/HTTPS |
| 15 | Compatible Observability and Runtime Sources → Ingestion and Normalization Service | Authorized telemetry | REST/HTTPS · not implemented |
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
| 27 | Diagnostic & Recommendation Service → Pipeline Service | Projects diagnosis summary | REST/HTTPS · differs |

## Relaciones de c4_expo_2b

C4 Level 2B — Consumption, Governance and Persistence. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Without stereotypes: blue boxes are containers of the prototype, gray boxes are people and external systems, the green cylinder is a data container and the dashed frame is the system boundary. Implementation state (model/implementation_status.yml): red = modeled, not implemented; amber = partially implemented; violet = implemented differently; unmarked = implemented or external.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Ingestion and Normalization Service | Workflow events | HTTPS/Webhook |
| 02 | Ingestion and Normalization Service → PostgreSQL | Metadata / protected buffer | PostgreSQL |
| 03 | Pipeline Service → PostgreSQL | Persists pipeline context | PostgreSQL |
| 04 | Log/Event Service → PostgreSQL | Evidence references | PostgreSQL |
| 05 | Diagnostic & Recommendation Service → PostgreSQL | Diagnosis and recommendations | PostgreSQL |
| 06 | Ingestion and Normalization Service → GitHub Actions | Queries runs, jobs and logs | GitHub API/HTTPS |
| 07 | GitHub → GitHub Actions | Repository and workflows | GitHub API/HTTPS |
| 08 | Technical Users → AIOps Web Dashboard | Querying and human review | HTTPS |
| 09 | AIOps Web Dashboard → GitHub | GitHub sign-in (OAuth + PKCE) | OAuth 2.0/HTTPS (authorization code + PKCE S256) · partial |
| 10 | AIOps Web Dashboard → Pipeline Service | Queries pipelines and executions | REST/HTTPS |
| 11 | AIOps Web Dashboard → Log/Event Service | Queries logs and evidence | REST/HTTPS · not implemented |
| 12 | AIOps Web Dashboard → Diagnostic & Recommendation Service | Diagnosis and review | REST/HTTPS |
| 13 | Diagnostic & Recommendation Service → PostgreSQL | Persists human review | PostgreSQL |
| 14 | GitHub Actions → Diagnostic & Recommendation Service | Queries result for artifact | REST/HTTPS |
| 15 | AIOps Web Dashboard → Ingestion and Normalization Service | Sign-in, session and GitHub discovery | REST/HTTPS |
| 16 | Ingestion and Normalization Service → GitHub | PKCE code exchange and access checks | OAuth/HTTPS + REST/HTTPS |
| 17 | Ingestion and Normalization Service → Azure Key Vault | Session signing, App material, custody | Azure Key Vault API/HTTPS |
| 18 | Pipeline Service → Azure Key Vault | Signs workload tokens | Azure Key Vault API/HTTPS |
| 19 | Log/Event Service → Azure Key Vault | Signs workload tokens | Azure Key Vault API/HTTPS |
| 20 | Diagnostic & Recommendation Service → Azure Key Vault | Signs workload tokens | Azure Key Vault API/HTTPS |
| 21 | Pipeline Service → Ingestion and Normalization Service | Verifies GitHub user access | REST/HTTPS |
| 22 | Log/Event Service → Pipeline Service | Checks ORIGIN membership | REST/HTTPS |
| 23 | Pipeline Service → Ingestion and Normalization Service | Checks capture scope | REST/HTTPS |
| 24 | Diagnostic & Recommendation Service → Pipeline Service | Resolves diagnosis access | REST/HTTPS |
| 25 | Diagnostic & Recommendation Service → Pipeline Service | Projects diagnosis summary | REST/HTTPS · differs |

## Relaciones de c4_context

C4 Level 1 — System Context. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Implementation state (model/implementation_status.yml): red = modeled, not implemented; amber = partially implemented; violet = implemented differently; unmarked = implemented or external. Context aggregation: each arrow joins the relationships between the system and that external element.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → AIOps Prototype for CI/CD Failure Diagnosis | Emits authorized workflow events / Queries diagnostic_output to publish the workflow artifact | HTTPS/Webhook / REST/HTTPS |
| 02 | AIOps Prototype for CI/CD Failure Diagnosis → GitHub Actions | Retrieves authorized run metadata, jobs and logs | GitHub API/HTTPS |
| 03 | AIOps Prototype for CI/CD Failure Diagnosis → Azure OpenAI Service | Generates compatible document and query embeddings / Requests diagnostic inference with sanitized evidence and RAG context | Azure OpenAI API v1/HTTPS / Azure OpenAI API/HTTPS |
| 04 | GitHub → GitHub Actions | Provides the repository, commits and CI/CD workflow definitions | GitHub API/HTTPS |
| 05 | Compatible Observability and Runtime Sources → AIOps Prototype for CI/CD Failure Diagnosis | Provides authorized telemetry and operational evidence | REST/HTTPS · not implemented |
| 06 | Technical Users → AIOps Prototype for CI/CD Failure Diagnosis | Queries results and records human review | HTTPS |
| 07 | AIOps Prototype for CI/CD Failure Diagnosis → GitHub | Sends users to GitHub to authorize sign-in / Exchanges sign-in codes with the PKCE verifier and verifies GitHub identity, installations, repository access and collaborators | OAuth 2.0/HTTPS (authorization code + PKCE S256) / OAuth/HTTPS + REST/HTTPS · partial |

## Relaciones de c4_component_diagnostic

C4 Level 3 — Diagnostic Components. Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Implementation state (model/implementation_status.yml): red = modeled, not implemented; amber = partially implemented; violet = implemented differently; unmarked = implemented or external.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | AIOps Web Dashboard → Diagnostic API | Reads diagnoses and records human reviews | REST/HTTPS |
| 02 | Evidence Correlation Service → Diagnostic API | Delivers correlated context for diagnosis | REST/HTTPS · partial |
| 03 | Diagnostic Orchestrator → RAG Knowledge Retrieval | Requests authorized contextual knowledge | REST/HTTPS |
| 04 | Diagnostic Orchestrator → Azure OpenAI Service | Requests diagnostic inference with RAG context | Azure OpenAI API/HTTPS |
| 05 | Diagnostic Output Composer → PostgreSQL | Persists diagnoses with their recommendation and cited evidence | PostgreSQL · partial |
| 06 | Diagnostic API → Human Review & Diagnostic Governance | Delegates diagnosis recording and human validation | in-process · partial |
| 07 | GitHub Actions → Diagnostic API | Queries diagnostic output for native artifact publication | REST/HTTPS |
| 08 | Human Review & Diagnostic Governance → PostgreSQL | Persists human review decisions and traceability | PostgreSQL |
| 09 | Diagnostic API → Diagnostic Orchestrator | Delegates diagnosis generation | in-process · differs |
| 10 | Diagnostic Orchestrator → Diagnostic Output Composer | Delivers inference results and contextual evidence | in-process · partial |

## Relaciones de c4_component_ingestion_capture

C4 Level 3 — Ingestion Components (1/2: capture and publication). Blue: prototype · Gray: actors and external systems · Green: persistence · Solid: synchronous · Dashed: asynchronous · Dotted: event. Implementation state (model/implementation_status.yml): red = modeled, not implemented; amber = partially implemented; violet = implemented differently; unmarked = implemented or external. Part of c4_component_ingestion; the complete view is out/c4_component_ingestion.svg.

| Nº | Origen → destino | Relación | Protocolo |
|---|---|---|---|
| 01 | GitHub Actions → Workflow Webhook Intake | Delivers signed workflow_run events | HTTPS/Webhook |
| 02 | Capture Preparation → GitHub Actions | Reads run metadata, jobs and logs with an installation token | GitHub API/HTTPS |
| 03 | Capture Preparation → Azure Key Vault | Reads GitHub App signing material | Azure Key Vault API/HTTPS |
| 04 | Evidence Publication → Azure Service Bus | Publishes execution snapshots and protected evidence | Azure Service Bus |
| 05 | Capture Authority & Ledger → PostgreSQL | Persists admissions, workflow scopes and the capture/publication ledger | PostgreSQL |
| 06 | Pipeline Service → Capture Authority & Ledger | Synchronizes workflow capture scopes | REST/HTTPS |
| 07 | Pipeline Service → Capture Authority & Ledger | Verifies the machine scope of a protected evidence capture | REST/HTTPS |
| 08 | AIOps Web Dashboard → Capture Authority & Ledger | Requests analysis of a chosen workflow run | REST/HTTPS |
| 09 | Workflow Webhook Intake → Capture Authority & Ledger | Records the admitted delivery as a durable receipt | in-process |
| 10 | Capture Preparation → Capture Authority & Ledger | Claims accepted receipts and freezes the publication plan | in-process |
| 11 | Capture Preparation → Normalization & Protection | Normalizes and protects the failed-run observation | in-process |
| 12 | Evidence Publication → Capture Authority & Ledger | Claims frozen outputs and confirms their publication | in-process |
