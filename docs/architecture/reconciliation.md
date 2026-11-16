# Reconciliación documental del Charter, drift y ADRs

La matriz siguiente conserva el corte histórico de etapa 2. Para el estado
integrado al 06/11/2026, las revisiones vecinas y las discrepancias MVP de
perímetro, Blob, AI y preparación operativa, consultar la
[reconciliación entre repositorios](cross-repository-reconciliation.md).
Ese seguimiento no reescribe las fuentes ni acredita despliegue.

Informe descriptivo de la etapa 2, de 31/10/2026. Base Git inspeccionada: `c1e7e5f4ac2775d0eeb929328d24eb98b2a13265`, junto con los documentos suministrados localmente y los cambios documentales de la etapa 1. Se contrastaron las 50 resoluciones del drift, los 18 ADRs y los modelos existentes. Este informe no cambia decisiones, estados, tecnologías, topologías ni alcance; no resuelve TMD ni CF-001 y no altera documentos propietarios.

## Fuentes y criterio de lectura

- [Registro de procedencia e integridad](../sources/README.md): hashes, fechas, autoridad declarada y límites de aprobación verificable.
- [Project Charter v1.3](<../sources/P202620027 - Project Charter v.1.3.docx>): 23/09/2026 según historial. Se cita por sección y, cuando exista, identificador OE; para párrafos sin ID se añade su inicio. La paginación depende del renderizador.
- [Drift original archivado][D]: cada fila numerada de la matriz corresponde exactamente a su sección §1–§50. Se conservan también sus diagramas y bloques finales históricos.
- [Índice de los 18 ADRs y evolución](decisions/index.md): los ADRs declaran `Accepted` y fecha 03/10/2026. Eso acredita el estado registrado, no por sí solo el acto de aprobación externo. Las relaciones se basan en disposiciones explícitas, no solo en numeración o fecha.
- [Arquitectura][A]: se citan IDs de elementos, relaciones, controles, invariantes o claves de sección. [Dominio][M] y [diseño propuesto][C] conservan sus estados y preguntas; DD identifica secciones de [domain_decisions.md][DD].

Clasificaciones: **Compatible** significa concordancia documental; **Concretado** identifica una especificación adicional respaldada por la fuente citada; **Histórico/sustituido** se limita al punto afectado; **Alcance delimitado** distingue capacidades de integraciones o límites del MVP; **Pendiente** identifica evidencia o mecanismo no acreditado; **Discrepancia** registra enunciados no equivalentes sin resolverlos. Ninguna clasificación demuestra implementación ni aprueba decisiones nuevas.

El Charter determina objetivos, alcance y restricciones; los ADRs documentan decisiones específicas y evolución. El drift registra discrepancias y no invalida automáticamente decisiones posteriores. Los documentos académicos históricos no se usan para sustituir decisiones posteriores. CF-001 conserva una descripción de override que debe tratarse como discrepancia, no como una instrucción para reescribir el original archivado.

## Matriz de las 50 resoluciones

En cada fila, el número remite a la sección del [drift][D] con ese número. Las referencias adicionales identifican la evidencia de contraste y el punto del modelo afectado.

| D§ | Tema | Clasificación | Evidencia de contraste y límite |
|---|---|---|---|
| 1 | Repositorio y CI/CD principal | Compatible | Charter, «Alcance del Proyecto»: integración GitHub Actions. A: github, github_actions, CF-002. |
| 2 | Integración CI/CD | Compatible / concretado | A: rel_github_actions_ingestion_event, rel_ingestion_github_actions_read. [ADR-016][A16], Decision, concreta publicación del artifact. |
| 3 | Acceso a GitHub | Concretado | [ADR-005][A05], Decision: GitHub App e installation tokens. [ADR-016][A16] separa publicación nativa del workflow. A: INV-003. |
| 4 | Posicionamiento no invasivo | Compatible | Charter, «Resumen ejecutivo» y exclusiones de «Alcance». [ADR-010][A10]/[ADR-014][A14] mantienen Actions como frontera. |
| 5 | Scanners opcionales | Alcance delimitado | [ADR-014][A14], Decision, admite evidencia indirecta de workflows y excluye APIs directas del MVP. Fuente de evidencia no equivale a integración directa. |
| 6 | Scanners en lower | Compatible | Charter excluye producción crítica obligatoria; A: deployment.validation_environment. [ADR-014][A14] no exige despliegue productivo. |
| 7 | Captura e ingesta | Compatible | A: ingestion_normalization_service y CF-003. No autoriza nuevos conectores automáticamente. |
| 8 | Privacy Gateway | Compatible | A: CF-004 e ingestion_normalization_service integran protección; no existe ese microservicio activo. |
| 9 | Protección previa de datos | Compatible | Charter, «Suposiciones y Restricciones»; A: INV-001, INV-002 y CTRL-002. |
| 10 | Retención por política | Concretado / evidencia pendiente | [ADR-013][A13], Decision/Basis: 365 días comunicados por stakeholder; política original ausente. A: retention, INV-009. No atribuir ese valor al Charter. |
| 11 | Microsoft Azure | Compatible | A: deployment.cloud; [ADR-001][A01]/[ADR-015][A15] concretan hosting. Charter permite entorno cloud controlado sin imponer proveedor distinto. |
| 12 | Capacidades lógicas y Azure físico | Compatible | A: layers y deployment. La separación conceptual no acredita portabilidad implementada. |
| 13 | Orquestador no seleccionado | Concretado | [ADR-001][A01], Decision, selecciona Container Apps; [ADR-015][A15] concreta NLP/RAG. El estado abierto del drift es histórico para este punto. |
| 14 | Broker de eventos | Compatible / evidencia pendiente | A: azure_service_bus y CF-005. El drift respalda Azure Service Bus; acto original de aprobación no acreditado por separado. |
| 15 | Mensajería asíncrona | Compatible / especificación adicional | A: azure_service_bus.topology y rel_service_bus_pipeline_service, rel_service_bus_log_event_service, rel_service_bus_nlp. D§15 respalda patrón, no acredita la aprobación exacta de un topic y tres suscripciones. |
| 16 | Parsing de logs | Concretado | [ADR-007][A07], Decision, selecciona Drain3; [ADR-015][A15] lo conserva. A: nlp_log_processor.parser. No reabrir por las opciones del drift. |
| 17 | Representación semántica | Concretado parcialmente | [ADR-007][A07] selecciona Azure OpenAI Embeddings; ADR-021 fija text-embedding-3-small/1536 para RAG. NLP conserva modelo concreto pendiente. A: nlp_log_processor.embedding_model, rag_retrieval.semantic_representation. |
| 18 | Detector y LogBERT | Histórico para el MVP | [ADR-010][A10], Decision, retira detector y LogBERT del MVP; no son selecciones pendientes del core actual. |
| 19 | Detector OPEN_DECISION | Sustituido para el MVP | [ADR-010][A10] elimina nodo y OQ-001. A no mantiene el detector activo. |
| 20 | Responsabilidad del detector | Histórico para el MVP | [ADR-010][A10] retira el componente. Separar detección de diagnóstico no autoriza restaurarlo. |
| 21 | Correlación de evidencia | Compatible | A: evidence_correlation_engine.correlation_dimensions; DD-014 conserva IDs de evidencia sin inventar algoritmo implementado. |
| 22 | correlationId transversal | Compatible | Charter, «Fases e hitos»: ingesta y normalización. A: CTRL-003, audit_trail.correlation; M usa correlation_id. |
| 23 | Identificador de incidente | Compatible / concretado | Charter, «Alcance»: reporte y dashboard comparten ID. A: recommendation_service.diagnostic_output; M: ops.incidents.id. |
| 24 | Persistencia estructurada | Compatible / concretado | [ADR-018][A18], Decision, concreta una instancia PostgreSQL y ownership. A: postgresql_operational_store. |
| 25 | Recuperación vectorial | Compatible | A: pgvector_knowledge_store. [ADR-018][A18] prescribe una instancia física; dos roles lógicos no implican dos bases físicas. |
| 26 | Almacenamiento separado | Compatible / procedencia parcial | Charter, «Software» y «Alcance»; DD-006 mantiene evidencia extensa por referencia. A: object_evidence_store selecciona Blob con fuentes Excel ausentes. El Charter y drift no acreditan esa selección concreta. |
| 27 | Corpus RAG | Compatible | Charter, «Recursos de Datos y Evidencias»; A: rag_retrieval.knowledge_scope; [ADR-015][A15] y DD-007 conservan autorización/provenance. |
| 28 | Conocimiento y evaluación separados | Compatible | Charter, «Recursos de Datos y Evidencias»; A: INV-010 y CTRL-006. No prueba saneamiento de corpus real. |
| 29 | LLM integrado | Concretado | [ADR-004][A04]/[ADR-015][A15] seleccionan Azure OpenAI gestionado por API; no hosting del modelo en Container Apps. |
| 30 | Entrada del LLM | Compatible | A: pretrained_llm_diagnostic_service.input_contract; C: SanitizedDiagnosticContext representa evidencia saneada, contexto y RAG como diseño propuesto. |
| 31 | Resultado automático | Compatible | [ADR-009][A09]; A: recommendation_service.diagnostic_output y output diagnostic_hypothesis. Causa probable con evidencia y limitaciones. |
| 32 | Causa raíz y probable | Compatible | Charter, «Glosario → Causa raíz / Causa probable»; A: INV-005 distingue hipótesis de causa confirmada. |
| 33 | Human-in-the-Loop | Concretado | [ADR-011][A11]/[ADR-016][A16] conservan revisión; DD-005 distingue CONFIRMED/CORRECTED/REJECTED y deriva PENDING. |
| 34 | Actores de validación | Compatible | Charter, «Stakeholders, Beneficiarios o Usuarios»; A: technical_users.roles. |
| 35 | Remediación automática | Compatible / límite más general en modelo | Charter excluye automatización crítica autónoma; A: INV-007 excluye remediación autónoma del MVP. No ampliar alcance por interpretar excepciones. |
| 36 | Observabilidad sin producto fijado | Concretado | [ADR-002][A02] selecciona Azure Monitor/Application Insights; [ADR-011][A11] distingue auditoría funcional. A: observability_sources. |
| 37 | Dashboard | Concretado | [ADR-008][A08] selecciona React/Static Web Apps; [ADR-018][A18] añade TypeScript; [ADR-016][A16] concreta acceso. |
| 38 | Reporte de diagnóstico | Concretado | Charter, «Alcance», párrafo «Por cada incidente analizado…». [ADR-009][A09] retira reporting_service sin perder capacidad; [ADR-016][A16] concreta consulta y publicación por workflow. |
| 39 | Notificaciones | Alcance reducido explícitamente | [ADR-012][A12] excluye Teams/Slack/correo del MVP. Son posibles extensiones futuras, no integraciones activas opcionales. |
| 40 | Entrenamiento de modelos | Compatible | Charter, «Alcance» y «Restricciones → Modelos de IA»; A: INV-008. No entrenamiento propio ni modificación de pesos. |
| 41 | Mantenimiento operacional | Compatible como principio / mecanismo pendiente | Sin política operativa equivalente identificada en ADRs/modelos que acredite implementación o seleccione actualización/sustitución concreta. No convertir el principio en una tecnología o proceso nuevo. |
| 42 | TMD como KPI | Compatible como KPI / discrepancia operacional | Charter, «Enfoques del trabajo» y «Glosario → TMD», frente a DD-015 y M: incidents.detected_at / diagnoses.diagnosis_ready_at. No se acredita equivalencia de intervalos. |
| 43 | Reducción TMD del 30 % | Compatible como meta | Charter OE4-I1; A: validation_contract.primary_time_metric. Comparabilidad condicionada al protocolo y la discrepancia de medición, no resuelta aquí. |
| 44 | Acierto del 80 % | Compatible | Charter OE3-I2/OE4-I1; A: validation_contract.diagnostic_accuracy. Metas, no resultados medidos. |
| 45 | F1-score auxiliar | Histórico para el detector del MVP | [ADR-010][A10] retira detector. No sustituye acierto diagnóstico ni crea obligación actual de medir F1. |
| 46 | Evidencia antes de inferencia | Compatible | A: INV-001/002; [ADR-015][A15] concreta flujo de orquestación y llamadas. |
| 47 | Contrato canónico con detector | Parcialmente sustituido | [ADR-010][A10] elimina tramo del detector; [ADR-015][A15]/[ADR-016][A16] concretan diagnóstico/revisión/consumo. Conservar flujo original como histórico, sin reutilizarlo aislado como vigente. |
| 48 | Stack físico resumido | Compatible / resumen incompleto | [ADR-001][A01]/[ADR-002][A02]/[ADR-003][A03]/[ADR-004][A04]/[ADR-008][A08]/[ADR-015][A15]/[ADR-018][A18] añaden selecciones. El resumen no las invalida. |
| 49 | Componentes sin fijar | Mixto | [ADR-001][A01]/[ADR-007][A07]/[ADR-002][A02] concretan orquestador/parser/observabilidad; [ADR-010][A10] retira detector; ADR-021 fija embeddings para RAG, no para NLP. D§49 admite decisiones posteriores aprobadas. |
| 50 | Source of Truth DaC | Discrepancia de gobernanza | Cabecera y §50 del drift reconocen decisiones posteriores; A: CF-001 describe override y pide modificar cabecera. Registrar ambos enunciados sin modificar fuentes ni resolver CF-001. |

El «Baseline canónico para nuevos diagramas» y `open_decisions` del drift también conservan detector y decisiones luego tratadas en ADRs. Son parte íntegra del snapshot histórico. La sección «Decisiones tecnológicas cerradas» no acredita por sí sola el acto de aprobación. La ausencia de APIs directas de scanners no impide su evidencia indirecta, conforme a ADR-014.

## Discrepancias y diferencias de cobertura

| Asunto | Evidencia concreta | Estado y límite |
|---|---|---|
| CF-001 | A: conflicts.resolved, id CF-001, resolution/action_required, frente a cabecera y D§50. | Discrepancia de gobernanza confirmada. CF-001 describe un override y pide actualizar la cabecera; no se ejecuta esa acción ni se altera el registro original. Este informe no reabre ni cambia su estado en YAML. |
| TMD | Charter, «Enfoques del trabajo», párrafo «Antes de las pruebas comparativas…»: evidencia disponible → diagnóstico final, incluyendo revisión humana cuando corresponda. «Glosario → TMD» remite al protocolo comparativo. DD-015 fija diagnosis_ready_at − detected_at; M describe detected_at como detección del fallo y diagnosis_ready_at como disponibilidad de esa versión. | Desalineación semántica confirmada; equivalencia no demostrada. No se elige una fórmula ni se cambian timestamps. Falta aprobación del protocolo y revisión de su correspondencia con los campos existentes. |
| Cobertura de evaluación | Charter OE2-I2 pide matriz de requisitos no funcionales y registro de revisión; OE3-I2 exige al menos 1000 logs y 10 escenarios iniciales; OE4-I1 exige al menos 20 escenarios comparativos y rúbrica aprobada. A: validation_contract registra metas resumidas. | Diferencia de cobertura documental, no cambio tecnológico. Falta trazabilidad de criterios y evidencia de validación; no se afirma incumplimiento de un producto desplegado. |
| Topología de mensajería | D§14/15 respalda producto/patrón. A: azure_service_bus.topology define un topic y tres suscripciones. | Aprobación de esa especificación exacta no trazada. Se conserva sin alteración. |
| Selección de Blob | D§26 y Charter, «Software», respaldan objetos separados. A: object_evidence_store.source remite a backlog/historias/plan Excel ausentes. | La selección concreta está declarada en el modelo; no se acredita su aprobación original con Charter/drift. No se reabre ni sustituye. |

Las menciones teóricas de anomalías en el Charter no demuestran una obligación de incorporar un detector propio. ADR-010 documenta expresamente su exclusión del MVP; no se resuelve una supuesta contradicción reintroduciéndolo. Las menciones de «causa raíz» se contrastan con el propio glosario del Charter y sus objetivos de causa probable, no se usan aisladas para atribuir certeza automática.

## Referencias desactualizadas y evidencia pendiente

Este registro es externo: no modifica documentos propietarios, sus estados ni artefactos derivados. Disponibilidad local y aprobación verificable son cuestiones distintas.

| Referencia o evidencia | Situación observada | Pendiente sin resolver |
|---|---|---|
| A-011 en model/domain.yml | Declara ausentes Charter/TI/drift. Charter y drift ya están disponibles; TI no. | Actualización de la assumption fuera de esta etapa; no regenerar para ocultar la diferencia. |
| model/domain_decisions.md, introducción | Conserva ausencia de Charter/TI/drift. | Se registra aquí como parcialmente desactualizada; el documento propietario permanece intacto. |
| Overview.md | Inspección fechada que documenta ausencia de fuentes y gobernanza de su revisión. | Conservar como evidencia histórica; no interpretar sus resultados ni limitaciones como certificación del checkout actual. |
| Referencias SRC_*#… | Localizadores lógicos sin mapa completo a títulos originales. Ejemplo: SRC_CHARTER#Marco-Teorico-RAG corresponde temáticamente a «Generación aumentada por recuperación». | Correspondencia explícita completa todavía no establecida. La matriz aporta localizadores de contraste, sin reescribir IDs ni afirmar resolución automática de todos los enlaces del modelo. |
| Aprobación Charter v1.3 | Tabla de aprobación vacía y sin partes de firma digital identificadas en la copia. | Acta, firma o registro verificable de aprobación de esta versión. No se concluye que nunca haya sido aprobada. |
| Aprobación y procedencia drift | Sin versión, fecha, autoría formal ni aprobador identificados. | Identificar responsables, historial y evidencia de aceptación de sus resoluciones; no inferirlos de «Definitivo». |
| Aceptación de ADR-001 a ADR-018 | Cada archivo declara Accepted y 03/10/2026. | Evidencia individual del acto de aprobación y responsable. No se borran ni cambian sus estados declarados. |
| Política corporativa ADR-013 | El ADR registra comunicación del stakeholder sobre 365 días. | Política original o comunicación identificable. No atribuir el valor al Charter ni a fuentes académicas. |
| Prompts citados por DD-001 a DD-017 | DD cita «Prompt aprobado §…» sin documento identificable incorporado. | Recuperar o referenciar esa evidencia de aprobación; no fabricarla a partir del modelo resultante. |
| TI, backlog, historias y plan | Archivos originales todavía ausentes; citados por A y otras fuentes. | Recuperación/procedencia y contraste posterior, sin usarlos para sustituir decisiones posteriores sin autorización. |
| Charter OE2-I2 y OE4-I1 | Se dispone del requisito documental, no del registro de revisión ni protocolo/rúbrica aprobados. | Evidencia de revisión arquitectónica, matriz de requisitos y aprobación de reglas comparativas antes de afirmar su cumplimiento. |
| Mecanismos y preguntas | DQ-001 a DQ-006 en dominio; DCQ-001/002/003 y referencia a DQ-002 en diseño. | Se conservan abiertas. Esta incorporación no selecciona modelos, dimensión, RBAC, contratos ni mecanismos operativos. |

El [índice de decisiones](decisions/index.md#evolución-inequívocamente-respaldada) registra únicamente relaciones explícitas de evolución y sustituciones parciales. No existe evidencia suficiente en esta reconciliación para marcar un ADR completo como totalmente sustituido.

[D]: ../sources/tech_drift_resolutions.md
[A]: ../../model/architecture.yml
[M]: ../../model/domain.yml
[C]: ../../model/design.yml
[DD]: ../../model/domain_decisions.md
[A01]: decisions/ADR-001-azure-container-apps.md#decision
[A02]: decisions/ADR-002-azure-observability.md#decision
[A03]: decisions/ADR-003-identity-api-perimeter.md#decision
[A04]: decisions/ADR-004-azure-openai.md#decision
[A05]: decisions/ADR-005-github-app-authentication.md#decision
[A07]: decisions/ADR-007-log-processing-and-embeddings.md#decision
[A08]: decisions/ADR-008-react-azure-static-web-apps.md#decision
[A09]: decisions/ADR-009-remove-reporting-service.md#decision
[A10]: decisions/ADR-010-remove-anomaly-detector-from-mvp.md#decision
[A11]: decisions/ADR-011-audit-trail-without-audit-service.md#decision
[A12]: decisions/ADR-012-remove-notification-channels-from-mvp.md#decision
[A13]: decisions/ADR-013-retention-365-days.md#decision
[A14]: decisions/ADR-014-devsecops-scanners-outside-mvp.md#decision
[A15]: decisions/ADR-015-diagnostic-runtime-boundaries-and-orchestration.md#decision
[A16]: decisions/ADR-016-identity-api-human-review-and-artifact-flow.md#decision
[A18]: decisions/ADR-018-application-architecture-ddd-cqrs.md#decision
