# Registro agregado de decisiones pendientes

Etapa 3, inspección del 04/11/2026 sobre `1879fc6feee772361dd40283f743e0076c509eb7`. Registro descriptivo: agrega preguntas, discrepancias, evidencia faltante y detalles expresamente no especificados. No aprueba decisiones, no cambia estados de las fuentes y no certifica implementación. La aprobación de la etapa 2 autoriza sus cambios documentales; no acredita por sí misma los actos de aprobación de las fuentes que esa etapa declaró no verificables.

Actualización documental del 06/11/2026: las 32 entradas originales se conservan.
El [corte entre repositorios](cross-repository-reconciliation.md) añade evidencia
integrada de IaC/servicios/frontend y seguimiento XR-001–008. En ese corte remoto
el overlay PD-033–036/stage-5 no estaba disponible. La reconciliación local de
esta rama recupera los archivos con los hashes exactos citados allí y conserva
las cuatro entradas en la ampliación de etapa 5. Disponibilidad del contenido
no implica aprobación de contratos ni cierre de preguntas de los modelos.

## Evolución posterior de las decisiones MVP

[ADR-019](decisions/ADR-019-align-mvp-with-iac.md), aprobado por confirmación explícita del usuario del 06/11/2026, alinea el modelo con IaC: ingress nativo sin APIM, exclusión de Blob de workload, fundación Foundry y preparación Terraform dev-only. Las 36 entradas y XR conservan trazabilidad de sus cortes originales. Las referencias a APIM en PD-034/036 se leen ahora como acceso directo al servicio por ACA; el mecanismo de autenticación/autorización del workflow sigue **detalle no especificado**. PD-010 conserva la recepción del contexto de correlación; PD-011 la reconstrucción de consultas.

PD-016 conserva la carencia histórica de procedencia de la antigua selección Blob, pero no exige recuperar o desplegar ese recurso excluido. PD-017/030/031 siguen abiertos: exclusión de Blob no demuestra recuperación independiente ni los 365 días. ADR-021 cierra PD-005 para RAG y concreta parte de PD-006/035; PD-023/026 y los valores Azure reales siguen pendientes. XR-001/002/003/005 quedan reconciliados solo en su reflejo canónico, con sus dependencias operativas todavía abiertas. Las filas históricas siguientes no revierten ADR-019.

## Actualización aprobada de acceso GitHub — ADR-020

[ADR-020](decisions/ADR-020-github-user-access-and-workflow-onboarding.md), aprobado expresamente por el usuario el 06/11/2026, cierra la política funcional MVP de PD-007/008: Entra vinculado con GitHub, alta por administración efectiva, grants AIOps más acceso GitHub vigente y conector técnico en Ingestion. No implica cumplimiento del código, aprobación de ambos CODEOWNERS, cierre de contratos ni despliegue.

Impacto directo: dashboard, Ingestion y Pipeline. Impacto de seguridad a contratar: APIs humanas de Log/Event y Recommendation que exponen recursos del repositorio. Correlación/NLP/RAG mantienen sus flujos de máquina; IaC recibe dependencias de configuración, no autorización de ejecución. No agregar relaciones downstream por inferencia.

Los pendientes de PD-007/008 y DQ-005/006 se limitan a representación/contratos y recuperación, no a una política funcional por inventar. PD-027 registra la selección local puntual «Para PD-027 usaremos Key Vault», sin cierre de custodia ni protocolo físico; PD-034 debe concretar endpoints, acceso interno y propagación verificable del sujeto, incluida autorización de evidencia/diagnóstico; PD-035 conserva ingress/callbacks, configuración de instalaciones por tenant, permisos y rollout. PD-033 conserva el tratamiento de eventos de revocación y datos en tránsito cuando afecte consumidores; la política no autoriza purgar ni descartar el broker. PD-036 sigue referido al actor workflow, distinto del usuario conectado.

Las filas históricas siguientes se leen con esta actualización. Conservar ia_only/inferred para la representación de grants; implementación, modelo físico y contratos no se promueven automáticamente.

Actualización local del 07/11/2026: «Propuesta aprobada» acepta `github-connector-draft-0.2`. [DD-020](../../model/domain_decisions.md#DD-020) y `domain.yml` adoptan metadata PostgreSQL propia de Ingestion, modo Key Vault Secrets y principios OBO/validez de petición; el [contrato semántico de Ingestion](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/blob/main/docs/deployment-contract.md#connector-contract-proposal-for-decision) conserva binding/API. No equivale a integración en main ni cierre operativo de PD-027/034/035. Permanecen pendientes scopes/audiences/budgets concretos, admisión, navegador/callback, custodia/retención/backups, restore operativo y runner/identidades de entrega. La aprobación puntual no asigna autoridad continua de PD-027 ni autoriza recursos/permisos.

## Contrato RAG aprobado el 16/11/2026

El usuario aprobó [RAG–Recommendation–IaC v0.1](contracts/rag-integration-v0.1.md):
`text-embedding-3-small`, 1536 dimensiones, deployment DEV `pipesor-dev-embeddings`,
API v1, identidad system-assigned de RAG, rol consumidor `Rag.Query`, separación de
permisos SQL y presupuesto total de consulta de 15 segundos con hasta dos reintentos.
PD-005 tiene selección aprobada para RAG; su adopción en modelos/migraciones y la
compatibilidad real siguen pendientes. No extiende automáticamente el cambio a NLP.
PD-006 conserva el mecanismo aprobado y PD-023 requiere corpus real acreditado.
PD-034/035 tienen esta base contractual, con binding Entra/SQL, región, cuota, SDK,
responsables y degradación de Recommendation todavía por completar. PD-026 no cambia.
Las filas y fuentes anteriores conservan su corte histórico; los modelos canónicos
y artefactos generados no se modifican en este PR documental. El contrato enumera
las preguntas y entregas necesarias antes de activar Azure o datos reales.

## Uso y referencias

No existía un registro agregado independiente. La [reconciliación][R] conserva la matriz histórica de 50 resoluciones y sus pendientes; el [índice de decisiones][I] conserva la evolución de los 18 ADRs; el [registro de fuentes][S] conserva procedencia, hashes y límites de aprobación. Este archivo centraliza el seguimiento sin copiar esos registros ni sustituir a los propietarios. Los IDs `PD-*` son localizadores documentales de este agregado, no nuevos IDs de modelos o ADRs.

Cada fila contiene categoría (indicada por su sección), asunto, referencia verificable, estado/evidencia, acción de cierre y autoridad/impacto. **No identificada** significa que la documentación inspeccionada no asigna autoridad para cerrar ese asunto; no se deduce una asignación por afinidad técnica. Los owners de implementación citados no se convierten por ello en aprobadores. Las acciones de cierre describen trabajo pendiente y no lo autorizan en esta etapa.

Estados de este registro: **abierta en fuente**, **discrepancia confirmada**, **evidencia no verificable**, **referencia desactualizada** y **detalle no especificado**. No se aplican retroactivamente a los estados originales. No se considera pregunta pendiente cada `null`, campo nullable o configuración no descrita: solo se agregan vacíos explícitos o sustentados por las fuentes.

Los localizadores YAML se expresan como ruta e ID/clave en [arquitectura][A], [dominio][M] y [diseño][C], no como anclas Markdown inexistentes. DD/DC designan los encabezados numerados de las decisiones de [dominio][DD] y [diseño][DC]. Los ADRs se localizan por número y sección en los enlaces individuales del [índice de los 18 ADRs][I]. Para el [Charter][CH] se usa sección, indicador OE o inicio de párrafo; su hash está en [procedencia][S]. No se usa paginación dependiente del renderizador. D§ identifica la sección numerada del [drift archivado][D].

## Discrepancias documentales

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-001 — TMD: distinción de intervalos | Charter, «Enfoques del trabajo», «Antes de las pruebas comparativas…», y «Glosario → TMD»; DD-015; dominio: `incidents.detected_at`, `diagnoses.diagnosis_ready_at`; R: «Discrepancias y diferencias de cobertura», TMD; instrucción del usuario registrada debajo. | **Discrepancia confirmada** de nomenclatura/documentación: DD-015 llama TMD al intervalo técnico detección → disponibilidad de una versión diagnóstica; el Charter define el KPI comparativo evidencia disponible → diagnóstico final, incluida revisión humana cuando corresponda. Por instrucción del usuario, se conservan con objetivos y límites temporales diferentes, sin exigir equivalencia. DD-015 no persiste TMD/MTTR ni fija una política nueva de agregación KPI. | Obtener el protocolo comparativo aprobado y documentar la trazabilidad de sus límites, revisión humana y agregación. Explicitar en su uso la versión/período de la medición técnica y distinguir ambas denominaciones, sin modificar ahora DD-015 ni sus timestamps. | El usuario instruyó conservar y distinguir los intervalos en esta etapa; aprobador del protocolo **no identificado**. Depende de PD-021/022 para evidencia de validación; la meta del 30 % corresponde al KPI comparativo del Charter, no se acredita con el intervalo técnico por sí solo. |
| PD-002 — CF-001: autoridad y acción de override | Arquitectura: `conflicts.resolved[CF-001]`, `governance.technology_override`; D: cabecera y §50; ADR-018, Context; R: fila CF-001. | **Discrepancia confirmada**. YAML lo registra `resolved` y pide cambiar la cabecera; drift reconoce Charter y decisiones posteriores. Este registro conserva el estado original y la autoridad por materia documentada. | Solicitar aclaración autorizada de la discrepancia y del destino de `action_required`, con referencia a la directiva de ingesta citada. Preservar el snapshot original. | Autoridad de esa directiva **no identificada**. PD-013/014 aportan trazabilidad; impacta interpretación de fuentes por agentes. No ejecutar el override ni reabrir automáticamente el conflicto. |


### Distinción de intervalos para PD-001

Instrucción del usuario durante la etapa 3: «Conservar DD-015 como medición técnica y documentar expresamente que ambos intervalos tienen objetivos y límites temporales diferentes». Esta instrucción respalda la distinción registrada aquí; no acredita aprobación del protocolo comparativo ni modifica las fuentes históricas de la etapa 2.

| Medición | Objetivo | Inicio | Final |
|---|---|---|---|
| Intervalo técnico de DD-015, denominado TMD en esa fuente | Observar el tiempo transcurrido desde la detección del fallo hasta la disponibilidad de una versión diagnóstica. | `incidents.detected_at` | `diagnoses.diagnosis_ready_at` de la versión escogida por la consulta. |
| KPI comparativo TMD del Charter | Evaluar el tiempo de diagnóstico manual frente al asistido con límites equivalentes para ambos procedimientos. | Puesta a disposición de la evidencia. | Entrega del diagnóstico final, incluyendo revisión humana cuando corresponda. |

La fórmula técnica `diagnosis_ready_at − detected_at` se conserva. DD-015 deja a las consultas escoger versión/período y no fija una política nueva de agregación KPI. Este intervalo no acredita por sí solo el TMD comparativo ni la reducción del 30 %. La distinción no exige igualar los intervalos ni prueba incompatibilidad entre ellos; permanece pendiente la evidencia del protocolo y la trazabilidad de la medición comparativa (PD-022).

## Preguntas abiertas de los modelos

En [arquitectura][A], `open_questions: []` y `conflicts.unresolved: []` no cierran los asuntos de esta sección. Los tres modelos de presentación no declaran preguntas abiertas adicionales. DQ-002 se registra una sola vez aunque aparece también en diseño.

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-003 — DQ-001: severidad del incidente | Dominio: `open_questions[DQ-001]`, A-005; DD-002/DD-013. | **Abierta en fuente** (`open_question`): no existe regla aprobada de derivación; severity es nullable y distinta de criticality/log level. | Documentar regla y evidencia de aprobación, con trazabilidad a los campos afectados. | **No identificada**. Afecta clasificación de incidentes; no se equipara a política de riesgo PD-009. |
| PD-004 — DQ-002: confidence | Dominio: `open_questions[DQ-002]`, A-008; diseño: `open_questions[DQ-002]`, DA-003; DD-010. | **Abierta en fuente**: escala y semántica no fijadas; JSONB/Object conservan el valor recibido sin imponer 0..1. | Obtener contrato aprobado de semántica, escala y representación; evaluar cambios posteriores de persistencia/proyección. | **No identificada**. Afecta interpretación de `diagnostic_output`, API y dashboard. |
| PD-005 — DQ-003: modelo y dimensión de embeddings | Dominio: DD-009; arquitectura: `rag_retrieval.semantic_representation`; ADR-007/021. | **Cerrada para RAG el 16/11/2026**: text-embedding-3-small, 1536 dimensiones para documentos/consultas, modelo/versión persistidos y vectores incompatibles rechazados. DQ-003 se retira. NLP no hereda automáticamente esta selección. | Validar disponibilidad/cuota y re-embedding explícito ante cambios de modelo, dimensión o versión. | Aprobación explícita del usuario; ADR-021. Relacionada con PD-006/023. |
| PD-006 — DQ-004: carga/actualización del corpus | Dominio: `open_questions[DQ-004]`, A-009/A-010; DD-007/DD-009/DD-022; D§27/28/41. | **Mecanismo MVP aprobado el 16/11/2026**: importador administrativo idempotente, sin API pública ni aprendizaje automático; requiere alcance, provenance, autorización, versión y hash. ADR-021 habilita embeddings configurables bajo el contrato v0.1. | Mantener inventario real y evidencia de separación bajo PD-023; validar endpoint/región/cuota antes de activar Azure. | Aprobación explícita del usuario; ADR-021. PD-023 sigue abierto para corpus efectivo; se relaciona con PD-029. |
| PD-007 — DQ-005: RBAC por pipeline | Dominio: `open_questions[DQ-005]`, `pipeline_access_grants`, DD-017; ADR-003/016. | **Política MVP aprobada por ADR-020**; grants conservan `ia_only`/`inferred`. Pendientes representación definitiva, recuperación y contratos; no acredita implementación. | Aplicar ADR-020; acordar contratos de autorización humana, recuperación y representación provisional antes de integrar. | **No identificada**. Relacionada con PD-008; afecta autorización y consumo desde backend/IaC; no crea users/roles internos. |
| PD-008 — DQ-006: alta de workflows | Dominio: `open_questions[DQ-006]`; DD-017; arquitectura: `pipeline_service`. | **Política MVP aprobada por ADR-020**: alta con administración GitHub verificada; contrato REST y dependencias del conector pendientes. | Concretar contratos y pruebas conforme a ADR-020, sin deducir permiso de creación de grants sobre otro pipeline. | **No identificada**. Relacionada con PD-007; afecta configuración de monitorización. |
| PD-009 — DCQ-001: clasificación de riesgo | Diseño: `open_questions[DCQ-001]`; arquitectura: `human_review_component`; ADR-016, Decision. | **Abierta en fuente** (diseño propuesto): existe responsabilidad de revisión/riesgo, sin algoritmo, categorías ni umbrales. | Obtener política concreta aprobada y trazarla al contrato de Human Review. | **No identificada**. Afecta recomendaciones críticas y control humano; no sustituye DQ-001. |
| PD-010 — DCQ-002: recepción del contexto correlacionado | Diseño: `open_questions[DCQ-002]`, DA-001; arquitectura: `rel_correlation_diagnostic_api`; DC-001. | **Abierta en fuente** (diseño propuesto): REST/HTTPS declarado, sin URI ni DTO final. Las firmas de controller son abreviaturas. | Documentar contrato autorizado de recepción y su trazabilidad a la relación existente. | CODEOWNERS Jhon Galvez y Ramiro Guzman, según indicación del usuario registrada en la ampliación de etapa 5. Afecta interoperabilidad de correlation/diagnostic; no autoriza un endpoint o comunicación adicional. |
| PD-011 — DCQ-003: rehidratación del read model | Diseño: `open_questions[DCQ-003]`; arquitectura: `recommendation_service.diagnostic_output`; DC-004; ADR-018, Decision. | **Abierta en fuente** (diseño propuesto): fuente de `executionContext`/`failureSummary` al consultar no especificada. | Aclarar fuente y contrato para componer la consulta dentro de las fronteras existentes; registrar decisión si corresponde. | **No identificada**. Afecta proyección de consulta; no autoriza tablas, joins entre contextos ni comunicaciones nuevas. |

## Procedencia, aprobaciones y respaldo pendiente

La evidencia no verificable expresa un límite del checkout, no que nunca haya existido aprobación. Los 18 estados `Accepted` se conservan y se leen con las sustituciones parciales del índice.

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-012 — Aprobación y procedencia del Charter v1.3 | S: «Project Charter v1.3»; Charter: historial 1.3, 23/09/2026, y tabla «Aprobación». | **Evidencia no verificable**: tabla vacía, sin firma digital identificada; copia de entrega local sin cadena de custodia previa acreditada. | Recuperar acta/firma/registro verificable de esa versión y su procedencia. | Firmante requerido **no identificado** en la tabla vacía. Charter asigna al Project Manager consolidación de gestión; eso no prueba aprobación. Impacta respaldo del alcance. |
| PD-013 — Identidad y aceptación del drift | S: «Registro de drift»; D: cabecera, §50 y «Decisiones tecnológicas cerradas»; R: evidencia pendiente. | **Evidencia no verificable**: sin versión, fecha, autoría formal ni aprobador; hash identifica el snapshot, «Definitivo» no prueba aceptación. | Identificar historia, procedencia, responsables y evidencia de aceptación de las resoluciones correspondientes. | **No identificada**. Relacionada con PD-002/015/016; no invalida automáticamente ADRs posteriores. |
| PD-014 — Actos de aprobación de ADR-001–018 | Cada ADR, cabecera `Status: Accepted`, `Date: 2026-10-03`; [índice][I]; R: «Aceptación de ADR-001 a ADR-018». | **Evidencia no verificable** por separado para los 18 actos individuales. ADR-001, Rationale, declara aprobación del Architecture Owner; ADR-018, Context, declara aprobación del equipo. | Vincular cada ADR a su registro identificable de aceptación y responsable, preservando alcance y evolución. No tratar evidencia de uno como aprobación de los 18. | Architecture Owner solo está explícito en ADR-001; equipo en ADR-018, sin aprobador individual identificable. Los demás no tienen responsable individual verificable. Impacta trazabilidad, no altera `Accepted`. |
| PD-015 — Topología exacta de mensajería | Arquitectura: `azure_service_bus.topology`; D§14/15; R: «Topología de mensajería». | **Evidencia no verificable** de aprobación de un topic y tres suscripciones. Producto y patrón sí tienen respaldo documental. | Localizar aprobación de esa especificación exacta y vincularla; si no existe, elevar la carencia sin elegir otra topología. | **No identificada**. Depende de PD-013; afecta trazabilidad de IaC, no autoriza cambiar el modelo. |
| PD-016 — Procedencia de la selección de Blob | Arquitectura histórica en `c0871ac`: `object_evidence_store.source`; D§26; Charter: «Software»; R: «Selección de Blob». | **Evidencia no verificable** para la aprobación concreta, con respaldo parcial: objetos separados respaldados; modelo declara Blob con fuentes Excel ausentes. | Recuperar fuentes citadas y evidencia de aprobación de la selección concreta. | **No identificada**. Depende de PD-019; afecta respaldo de almacenamiento de evidencias. |
| PD-017 — Política corporativa de 365 días | ADR-013, Basis; ADR-016, Decision; arquitectura: INV-009; R: «Política corporativa ADR-013». | **Evidencia no verificable**: ADR registra comunicación del stakeholder, sin política original o comunicación identificable. | Incorporar referencia verificable a política/comunicación aplicable y su alcance. | Stakeholder es la fuente declarada por ADR-013; no identifica a la persona ni al aprobador de la política. Afecta PD-030; no se atribuye el plazo al Charter. |
| PD-018 — Prompts aprobados citados en DD | DD-001–017, apartados `fuentes` y referencias «Prompt aprobado §…»/«Prompt §…»; R: «Prompts citados». | **Evidencia no verificable**: no hay documento identificable incorporado que acredite esas aprobaciones y secciones. | Recuperar prompt, revisión, secciones y registro de aprobación, o señalar formalmente la evidencia que no pueda recuperarse. | **No identificada**. Afecta respaldo de decisiones físicas y assumptions; no reconstruir el prompt desde el resultado. |
| PD-019 — TI y hojas de cálculo ausentes | Arquitectura: `sources[SRC_TI]`, `object_evidence_store.source`, `deployment.validation_environment.source`; R: «TI, backlog, historias y plan». | **Evidencia no verificable** por ausencia local de las fuentes: `TI_Galvez_Jhon_Guzman_Ramiro.docx`, `TP202620027 - Product Backlog v.1.0.xlsx`, `TP202620027 - Historias de Usuario v.1.0.xlsx`, `TP202620027 - Plan de trabajo v.1.0.xlsx`. Las celdas/hojas citadas no son comprobables localmente. | Recuperar originales, versión/procedencia y contrastar localizadores sin reemplazar decisiones posteriores por documentación histórica. | Custodio/aprobador **no identificado**. Afecta PD-016/020/024 y trazabilidad funcional/entorno; no atribuir contenido a fuentes ausentes. |
| PD-020 — Mapa de localizadores lógicos SRC | Arquitectura: referencias `SRC_*#…`; R: «Referencias SRC_*#…», ejemplo `SRC_CHARTER#Marco-Teorico-RAG`. | **Evidencia no verificable** para el mapa completo de localizadores: hay contraste temático con «Generación aumentada por recuperación», sin mapa completo de títulos originales. | Construir y revisar correspondencias verificables por fuente/versión; distinguir localizador lógico de ancla real o evidencia ausente. | **No identificada**. Depende de PD-019 cuando la fuente falta. Afecta recuperación de contexto por agentes; no renombrar IDs ni declarar todos los enlaces resueltos. |
| PD-021 — Revisión arquitectónica y matriz no funcional | Charter OE2-I2; arquitectura: `validation_contract`; R: «Cobertura de evaluación» y «Charter OE2-I2 y OE4-I1». | **Evidencia no verificable** de matriz requisitos → decisiones/controles/criterios y registro de revisión. Modelo resume metas sin esa trazabilidad completa. | Referenciar matriz y registro de revisión/aprobación del diseño exigidos por OE2-I2. | Charter, «Organización → Stakeholders», atribuye al Asesor Especializado revisión de arquitectura, no acredita aprobación concreta ni exclusiva. Afecta respaldo de controles. |
| PD-022 — Protocolo y rúbrica comparativos | Charter OE4-I1 y «Enfoques del trabajo», «Antes de las pruebas comparativas…»; R: cobertura de evaluación. | **Evidencia no verificable** de aprobación previa del protocolo, criterios y rúbrica; se requieren ≥20 escenarios, reducción TMD 30 % y acierto ≥80 %. | Referenciar protocolo, causas de referencia, límites comparables, criterios y rúbrica aprobados antes de afirmar cumplimiento; documentar resultados y limitaciones cuando existan. | Aprobador específico **no identificado**. Depende de PD-001/023; afecta validez de evaluación y seguridad/pertinencia de recomendaciones. |
| PD-023 — Corpus autorizado y separación efectiva de evaluación | Charter: «Recursos de Datos y Evidencias»; D§27/28; arquitectura: `rag_retrieval.knowledge_scope`, INV-010, CTRL-006; dominio: A-010. | **Evidencia no verificable** de aplicación operativa: reglas documentadas, sin corpus real/procedencia/autorización ni demostración de separación identificados en las fuentes inspeccionadas. | Referenciar inventario autorizado y evidencia de saneamiento, procedencia y separación al preparar corpus/evaluación. | Dominio A-010 asigna verificación en aplicación a owners; no asigna aprobador de autorización. Depende de PD-006; afecta privacidad y validez de resultados. |
| PD-024 — Cobertura de entregables e indicadores del Charter | Charter: «Indicadores de Éxito», OE1-I1/I2, OE2-I1, OE3-I1/I2 y OE4-I2; R: cobertura de evaluación. | **Evidencia no verificable** en las fuentes inspeccionadas, sin afirmar incumplimiento: estado del arte (≥25 fuentes, 80 % de 2021–2026), inventario (5 fuentes/10 eventos/5 métricas), benchmarking (3 alternativas/6 criterios/≥80 puntos), backlog (≥30 historias), prueba inicial (≥1000 logs/10 escenarios, 80 % acierto), verificación funcional/no funcional y presentación final (3 escenarios/flujo completo/80 % rúbrica). No se confunden las 10 pruebas iniciales con las ≥20 comparativas. | Localizar entregables, revisiones, aprobaciones y evidencias de cada indicador; mantener trazabilidad por OE. Esto no exige ejecutarlos ahora ni repetir selecciones tecnológicas. | Charter asigna diseño/implementación/validación al Equipo de Desarrollo y evaluación de hitos al Comité; no prueba aprobación de esos entregables. Relacionado con PD-019/021/022/023; diferencia de cobertura documental. |

## Referencias parcialmente desactualizadas

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-025 — Disponibilidad de fuentes y lectura histórica | Dominio A-011; DD, introducción; [Overview][O]; R: primeras tres filas de evidencia pendiente; S: ubicación e integridad. | **Referencia desactualizada** en A-011/DD: Charter y drift ya están disponibles; TI sigue ausente. Overview es inspección fechada, no certificación actual. | En una tarea posterior autorizada, actualizar referencias de disponibilidad en sus propietarios conservando límites de lectura y estado de supuestos; preservar Overview como histórico. | **No identificada** para cambios de estado/gobernanza. Depende de PD-019 para TI; afecta confianza del contexto consumido por agentes. |

## Detalles expresamente no especificados

Estas entradas no convierten opciones en tecnologías aprobadas ni obligan a resolver todo antes de implementar cualquier componente. Las dependencias se aplican solo a la parte afectada. Las versiones o configuraciones omitidas sin una pregunta o restricción explícita no se inventarían aquí como decisiones adicionales.

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-026 — Variante concreta del LLM | ADR-004, Constraint; ADR-015, Decision; arquitectura: `pretrained_llm_diagnostic_service.model`, `deployment.llm.model`. | **Detalle no especificado** intencionalmente: familia GPT-4/proveedor/API registrados, modelo `null`; ADR-004 prohíbe fijar variante aún. **Propuesta DEV, 2026-11-18:** Azure OpenAI `gpt-4o` versión `2024-11-20`, US Data Zone Standard en `westus3`. La API de capacidad informó 300 unidades disponibles en el corte de revisión. El catálogo lo marca Legacy, con retiro de inferencia el 2027-04-14. Pendientes aprobación explícita del propietario y verificación final de capacidad para un despliegue nuevo. No se fija un valor por defecto. | Obtener instrucción y decisión explícitas antes de seleccionar variante; registrar alcance y evidencia. | **No identificada**. Afecta configuración de inferencia, sin reabrir proveedor ni hosting. |
| PD-027 — Almacenamiento de secretos | ADR-005, Constraint; ADR-020; arquitectura: `deployment.github_authentication`; [DD-020, revisión `github-connector-draft-0.2`](../../model/domain_decisions.md#github-connector-draft-0.2). | **Detalle no especificado**, con selección local puntual del 06/11/2026: «Para PD-027 usaremos Key Vault». ADR-005 se conserva como antecedente histórico por trazabilidad; la elección explícita de Key Vault ya está autorizada localmente y no se reabre. El 07/11/2026 «Propuesta aprobada» adopta schema/metadata y modo Secrets en DD-020; no acredita implementación ni detalles operativos. | Consumir DD-020 y el [contrato semántico de Ingestion](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/blob/main/docs/deployment-contract.md#connector-contract-proposal-for-decision), con DD-020 pendiente de integración y contrato de Ingestion aún local/no publicado; completar custodia operativa, restore, revocación/borrado y responsables sin reabrir modelo/principios de exclusión/recuperación aceptados. Persistir metadata local no implica guardar tokens ni desplegar. | Autoridad continua **no identificada**; la selección puntual del usuario no la asigna. Coordinar PD-034/035 sin inferir una autoridad distinta de sus CODEOWNERS ni autorizar recursos/permisos. |
| PD-028 — Formato del artifact diagnóstico | ADR-009, Decision; ADR-016, Decision; arquitectura: `github_actions.diagnostic_artifact`, output `github_actions_diagnostic_artifact`. | **Detalle no especificado** de implementación: consulta/publicación por workflow definidas, formato concreto diferido. | Documentar formato y contrato compatible al implementar el consumo, con aceptación verificable correspondiente. | Aprobador **no identificado**. ADR-016 asigna producción a recommendation_service y publicación a github_actions, sin darles autoridad decisoria. Relacionado con PD-010/011 según el contrato afectado. |
| PD-029 — Mantenimiento ante degradación operacional | D§41; R: matriz fila 41. | **Detalle no especificado** del mecanismo operativo: principio de monitoreo, versionado y actualización controlada sin política operativa equivalente identificada en ADRs/modelos. | Aclarar mecanismo y evidencia de aplicación dentro del alcance existente cuando corresponda; no convertirlo en entrenamiento ni proceso nuevo sin autorización. | **No identificada**. Relacionado con PD-006/026; no reactiva detector ni LogBERT. |
| PD-030 — Aplicación operativa de retención | ADR-018, Consequences and reversibility; DD-015; dominio: RET-001 y `retention_policy`. | **Detalle no especificado** del mecanismo operativo, no implementado por estas fuentes: 365 días declarados para logs/diagnósticos/evidencias, sin tareas de purga; no extender duración a corpus, configuración o auditoría. | Documentar mecanismo y evidencia de aplicación cuando se autorice implementación, conforme a política verificable. | Aprobador **no identificado**. Depende de PD-017; afecta ciclo de vida de datos sin cambiar duración/alcance. |
| PD-031 — Consistencia de referencias lógicas | ADR-018, Consequences and reversibility; DD-014; dominio A-006/A-010. | **Detalle no especificado** del mecanismo adicional: owners validan referencias por contratos existentes; ADR no elige consistencia distribuida adicional. | Precisar contratos y evidencia de validación de referencias al implementar, dentro de los límites actuales; elevar cualquier necesidad de arquitectura nueva. | Owners responsables de implementación según ADR-018; aprobación del contrato por los CODEOWNERS Jhon Galvez y Ramiro Guzman, según indicación del usuario registrada en la ampliación de etapa 5. Impacta integridad entre contextos; no autoriza FK cross-schema ni escritura ajena. |
| PD-032 — Algoritmos de identidad/hash y versiones de aplicación | DD-013, impacto; dominio: `evidence_items.content_hash`, A-001; ADR-018, Decision. | **Detalle no especificado** (algoritmos y versiones): DD-013 no selecciona algoritmo UUID/hash ni versiones Java/Spring/Python. No confundirlos con SHA-256 de archivo documental o versiones de herramientas de generación. | Precisar solo lo requerido por la implementación autorizada y registrar su respaldo sin presentarlo como decisión ya tomada. | **No identificada**. Afecta compatibilidad/reproducibilidad del backend; no amplía tecnologías aprobadas ni modifica dependencias aquí. |

## Ampliación de etapa 5: contratos de consumo

Ampliación descriptiva sobre `c0871ac9a62bad62b8c679255fe0a4b9c6574d2e`, a partir del [informe de Codex Cloud y su revisión local](stage-5-result.md), §4–6. Las 32 entradas originales se conservan; se agregan cuatro asuntos con estado **detalle no especificado**. Son necesidades de precisión sobre relaciones existentes, no contratos aprobados, preguntas añadidas al YAML ni autorización para ampliar el MVP.

**Autoridad indicada por el usuario:** los CODEOWNERS Jhon Galvez y Ramiro Guzman aprueban contratos de eventos, APIs, acceso del workflow y coordinación backend–IaC. Esta asignación se aplica a PD-033–036 y al alcance contractual de PD-010/031. No implica aprobación de ninguna solución ni delegación para cambiar fronteras arquitectónicas. No se infiere que baste uno de los dos o que se requieran ambos: esa regla de revisión no está especificada. Tampoco se acredita aquí la existencia/configuración de un archivo CODEOWNERS en GitHub.

Los criterios siguientes permiten revisar el cierre documental: documento de contrato versionado, trazabilidad a fuentes/IDs, evidencia identificable de aprobación y actualización autorizada de los propietarios afectados. No prueban por sí solos interoperabilidad o seguridad runtime. Las prioridades se refieren únicamente al intercambio o despliegue afectado; no detienen todo trabajo independiente.

| ID y asunto | Fuente y referencia | Estado actual y evidencia | Acción necesaria para cierre | Autoridad documentada, dependencias e impacto |
|---|---|---|---|---|
| PD-033 — Evento normalizado e intercambio asíncrono | Informe §4, evento normalizado; arquitectura: `ingestion_normalization_service.canonical_event_context`, `azure_service_bus.topology`, `rel_ingestion_service_bus`, `rel_service_bus_pipeline_service`, `rel_service_bus_log_event_service`, `rel_service_bus_nlp`. | **Detalle no especificado**: contexto conceptual y recorridos declarados, sin contrato completo del mensaje, compatibilidad ni comportamiento de duplicación/reentrega. | Documentar productor/consumidores, campos y semántica, identidad/correlación, versión/compatibilidad y tratamiento acordado de duplicación, fallos y reentrega. Cierre documental: contrato versionado aprobado y trazado a esas relaciones, sin seleccionar ahora mecanismos concretos. | CODEOWNERS indicados arriba. Prioridad: antes de integrar el flujo asíncrono. Depende de PD-031 para IDs/referencias; relacionado con PD-015, cuya evidencia de topología sigue pendiente. No cambia topic/suscripciones. |
| PD-034 — Especificación de intercambios REST | Informe §4, contratos REST; arquitectura: `rel_nlp_correlation`, `rel_correlation_recommendation`, `rel_dashboard_pipeline_service`, `rel_dashboard_log_event_service`, `rel_dashboard_recommendation_service`; ADR-015/016/019. | **Detalle no especificado**: protocolos y responsabilidades definidos, sin especificación completa de solicitudes, respuestas y errores para todos los intercambios utilizados. PD-010 conserva la recepción diagnóstica específica. | Identificar cada intercambio del incremento y documentar su forma de solicitud/respuesta, errores y compatibilidad. Cierre documental: especificaciones versionadas aprobadas y vinculadas a relaciones existentes; referencias a PD-010/011 donde corresponda, sin duplicar sus cierres. | CODEOWNERS indicados arriba. Prioridad: antes de integrar cada productor/consumidor. Depende de PD-010/031 según intercambio; PD-004/011 afectan las salidas diagnósticas correspondientes. No crea endpoints ni comunicaciones adicionales. |
| PD-035 — Entrega entre backend e IaC | Informe §2/4/5, separación y entrega backend–IaC; arquitectura: `deployment.container_hosts`; ADR-001/018. | **Detalle no especificado**: hosting y ownership registrados, sin contrato integral de entrega, configuración, migraciones ni responsabilidades de promoción. | Documentar artefactos e identificadores de versión, entradas/salidas de configuración, accesos requeridos, ejecución de migraciones y responsabilidades backend/IaC necesarias para el incremento. Cierre documental: contrato de entrega aprobado con responsabilidades explícitas y trazabilidad al modelo. | CODEOWNERS indicados arriba. Prioridad: antes del despliegue integrado. Depende de los contratos PD-033/034/036 usados y PD-027 cuando requiera secretos. El corte remoto acredita código Terraform y decisiones de preparación en IaC (XR-004/005), sin cerrar la entrega runtime; esta entrada no introduce selecciones de SKU, red, región o promoción. |
| PD-036 — Identidad y autorización del workflow ante ingress nativo ACA | Informe §4/5, credenciales y acceso real; arquitectura: `rel_github_actions_diagnostic`; ADR-005/016/019. | **Detalle no especificado**: consulta por ingress nativo ACA y publicación nativa por workflow definidas; identidad/autorización de esa consulta no concretadas. Entra ID del dashboard y GitHub App read-only no definen por sí solos ese acceso. | Documentar actor, mecanismo de autenticación/autorización, permisos y condiciones de acceso de la consulta existente. Cierre documental: contrato aprobado, trazado a la relación y compatible con mínimo privilegio/publicación nativa; remitir gestión de secretos a PD-027 si corresponde. | CODEOWNERS indicados arriba. Prioridad: antes de conectar ese actor a APIs/evidencia reales. Relacionado con PD-027/028/034/035. No asigna escritura a la GitHub App ni presupone proveedor o mecanismo nuevo. |

La disponibilidad e identidad entre consumidores se mantiene en **PD-031**; la recepción de contexto en **PD-010** y la reconstrucción de consultas en **PD-011**. La política de retención permanece en **PD-030** y su evidencia en **PD-017**. No se duplican ni cierran esas entradas. Las brechas de secretos y autorización funcional PD-027/007/008 conservan su alcance propio.

La lectura de estas entradas debe incluir el corte remoto `f02f7cf8b902be80a07e4653d8389fef50e815d0`: XR-001 registra native ingress sin APIM aceptado en IaC y aún no reflejado en el modelo; PD-034/036 describen el contrato canónico histórico, no una instrucción de desplegar APIM. XR-002 registra la exclusión de Blob de workload frente al modelo/DD-006; afecta PD-016/030/031. XR-003 aporta fundación Foundry; ADR-021 concreta el contrato RAG sin acreditar valores ni disponibilidad Azure y conserva PD-023/026. XR-004/005 aportan preparación Terraform y decisiones dev-only que deben consumirse con PD-035; no acreditan contratos runtime ni despliegue. XR-007 complementa PD-033/031 sobre mensajería y llegada independiente. Estas relaciones no resuelven las discrepancias ni sustituyen ADRs automáticamente.

### Propuesta pendiente PD-011/PD-034 — Consulta de diagnóstico por incidente

**Estado: propuesta para aprobación.** La consulta humana de solo lectura usa la relación existente `rel_dashboard_recommendation_service` (ADR-016 con el perímetro actualizado por ADR-019). Recommendation conserva diagnóstico, citas y revisiones. Pipeline conserva incidente, ejecuciones y sus asociaciones. ADR-018 conserva las referencias lógicas y ADR-020 exige acceso vigente al repositorio. Este corte registra un contrato candidato sin cerrar PD-011/PD-034 ni autorizar una ruta, despliegue o permiso.

| Aspecto | Contrato mínimo propuesto |
| --- | --- |
| Consulta | `GET /api/v1/incidents/{incidentId}/diagnosis` en Recommendation, con UUID opaco asignado por Pipeline. La aplicación conserva su navegación actual y obtiene el UUID del listado autorizado. El cliente no suministra tenant, instalación, repositorio, ejecución, contexto, versión ni UUID de diagnóstico. El contrato se limita al dashboard humano. La consulta de GitHub Actions de PD-036 permanece independiente. |
| Sujeto autenticado | Token delegado de Entra con issuer, audience de Recommendation, scope explícito de lectura diagnóstica, tenant admitido, identificador de sujeto y validez comprobados por Recommendation. El token de Pipeline no es intercambiable. La aprobación debe fijar audience, scope, propagación del sujeto, identidad del servicio llamador y configuración. |
| Entitlement vigente | En cada petición, Recommendation exige un resultado de autoridad de propietario ligado al sujeto autenticado, operación de lectura diagnóstica, UUID de incidente, pipeline, tenant, instalación, repositorio y ejecución autorizada. Pipeline verifica identidad operativa y capacidad efectiva. El hecho vigente de acceso GitHub para usuario y App e instalación admitida procede de Ingestion. Recommendation valida que esos hechos, junto con su propio scope delegado y la política aprobada para evidencia/revisión, autorizan **su** proyección. Un `VIEW` o una respuesta REST de Pipeline por sí solos no autorizan la consulta. Se propone validar los hechos vía un resolvedor de propietario con identidad de servicio y sujeto verificable, sin confiar en cabeceras libres ni copiar grants. El owner y transporte de ese resolvedor, los permisos y la regla de acceso a revisión requieren aprobación antes de conectar servicios. |
| Selección de versión | Primer corte: para la ejecución de fallo original que el owner confirma para el incidente, seleccionar el mayor número de versión **admitida** de esa ejecución. No elegir por fecha, revisión humana reciente, ejecución de verificación ni versión aportada por cliente. Verificar vínculo y scope de la versión seleccionada antes de devolverla. Una versión más reciente denegada o incoherente impide la respuesta; no se retrocede a otra. Una referencia original ambigua, vínculo no verificable o selección ambigua falla cerrada. La versión no convierte la hipótesis en veredicto. |
| Identidad y reconstrucción | Comprobar el UUID de incidente y el vínculo incidente→pipeline→ejecución con datos del owner. Usar únicamente los registros de Recommendation para reconstruir una versión inmutable. Validar que el contexto admitido contiene los mismos UUIDs de incidente/ejecución y coincide con el scope de tenant, instalación, repositorio y pipeline. Conservar el UUID y versión de diagnóstico, el UUID de contexto y el correlation ID de su receipt; la correlación sirve para trazabilidad. No imponer igualdad al correlation ID del incidente cuando la política admita múltiples contextos. Versiones viejas sin evidencia de admisión o sin un binding requerido no son elegibles. Sin joins de esquemas ni lectura de la base de otro owner. |
| Revocación y frescura | Verificación vigente por petición, con timeout y vida útil acotados. Evitar caché positiva entre peticiones, y `Cache-Control: no-store` en todas las respuestas. Validar que el scope histórico puede seguir exponiéndose con hechos actuales y la regla de reconciliación de revisiones aprobada. Una revocación o acceso indeterminado impide entregar la proyección. Mantener versión y revisión visibles como procedencia de los datos. En el dashboard, descartar respuestas de una selección o sesión anterior y limpiar datos al recibir denegación o indisponibilidad. |
| Resultados públicos | `401` para identidad inválida y `400` para forma inválida. `404` genérico para incidente inexistente o inaccesible, incluido acceso revocado, sin metadatos que distingan esos casos. Solo con incidente y scope ya autorizados, `404 diagnosis_absent` indica que no hay versión admitida para la ejecución solicitada implícitamente. `409 diagnosis_stale` se reserva para binding/versiones no reconciliables una vez comprobado el acceso; no incluye campos del snapshot. `503 authority_unavailable` o `503 diagnosis_unavailable` ante verificación indeterminada o fallo del almacenamiento. Los detalles de denegación se conservan fuera de la respuesta pública. |
| Proyección | En `200`, devolver identidad de incidente, ejecución, contexto y diagnóstico, versión, correlation ID aprobado, hipótesis original, recomendación, limitaciones, extractos saneados y citas de evidencia y conocimiento con procedencia autorizada. Incluir estado, revisión e historial P3 de esa versión solo con la política de lectura de revisión aprobada. Acordar la exposición de identidad del revisor y aplicar minimización. Autorizar el original y cada referencia expuesta bajo la política vigente; evitar una respuesta parcial que deje citas sin respaldo. No incluir credenciales, logs brutos, hechos internos de entitlement, documentos completos ni mutaciones de revisión. |

**Base comprobable.** Recommendation `3b4a8a4` admite versiones con incident UUID, scope y output persistidos. La identidad de contexto determina el UUID de admisión para redelivery; la versión se asigna dentro de una transacción y el historial se vincula al diagnóstico. Un fingerprint distinto de la misma identidad se rechaza. P3 tiene lectura independiente por UUID de diagnóstico, con verificación de scope. Pipeline `0f9b440` mantiene sus consultas y autorización por workflow/incident UUID. [Registro del piloto E02](https://github.com/pipesor-org/pipesor-frontend/blob/main/docs/local-product-mvp.md#increment-8-operational-discovery) y [fixture de cadena local](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/local-diagnostic-demo.md#operational-discovery-in-the-e02-review-run) distinguen descubrimiento real de Pipeline y la prueba P3 por UUID explícito. Los receipts y el alcance de Correlation descritos en [decisiones de dominio](../../model/domain_decisions.md) preservan referencias y procedencia; no son una autorización humana.

**Aprobación necesaria.** Registrar el acuerdo explícito sobre selección de ejecución y versión, composición del resolver y su nueva interacción si corresponde, representación de sujeto y hechos actuales, reconciliación del scope histórico, exposición de historial/revisor y errores. PD-034 requiere revisión de los CODEOWNERS indicados arriba con participación de Pipeline, Ingestion y Recommendation en su alcance. Confirmar quién puede cerrar PD-011 y la regla de aprobación de PD-034; la fuente actual no los especifica. Una aprobación contractual no autoriza habilitación de producción, infraestructura ni modificación de P3. Mantener el piloto y su runbook como línea base hasta que la aprobación se registre.

**Baseline verificada.** El replay E02 del 19/11/2026 pasó con Frontend `0d5092c` y Correlation `5e8fa8d`. Seguir el runbook del piloto citado arriba para reproducirlo. Chromium abrió y recargó el incidente persistido por Pipeline. La prueba P3 separada reconstruyó las revisiones mediante UUID explícito. La ruta propuesta todavía no forma parte de esta evidencia.

**Aceptación después de aprobar.** Ejecutar E02 determinista con PostgreSQL y Chromium. Descubrir la fila por las API de Pipeline y abrir el Workspace. Obtener por la consulta nueva, con autorización independiente, el original, limitaciones, evidencia, citas e historial de la versión. Repetir tras reload y reinicio con almacenamiento retenido. Probar tenant/repositorio ajenos, revocación después de un 200, autoridad caída, ejecución y contexto incongruentes, ausencia autorizada, selección ambigua, respuesta obsoleta y redelivery. Las pruebas deben preservar la vista vacía al fallar. Los tests P3 existentes cubren persistencia y autorización por UUID de diagnóstico y sirven como línea base, con un alcance distinto a esta consulta.

## Contrato de validación de máquina — PD-031/034

El usuario autorizó continuar la validación previa al registro de evidencia por
el recorrido Log/Event → Pipeline → Ingestion. El incremento integrado aporta la
consulta de pertenencia de Pipeline, la comprobación de revisión exacta de
Ingestion y la propagación de correlación de Log/Event. Una prueba local conectó
las tres implementaciones con autoridad de archivo y PostgreSQL aislado. La
[implementación y su verificación](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/deployment-contract.md#logevent-registration-before-correlation)
registra el alcance. El
[contrato versionado de intercambio v1](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/contracts/owner-validation-v1.openapi.yaml)
concreta las dos operaciones REST autorizadas localmente por el usuario.

La actualización arquitectónica local incorpora una relación síncrona de
solo lectura Log/Event → Pipeline para confirmar que pipeline, ejecución/intento
e incidente automático ORIGIN pertenecen al contexto autorizado. Incorpora además
una relación de máquina Pipeline → Ingestion para comprobar el permiso vigente
sobre la revisión exacta de captura. Esta segunda operación requiere identidad
de máquina y una ruta de captura resuelta mediante configuración confiable. La
relación existente `rel_pipeline_ingestion_github_access` conserva su semántica de
acceso humano verificado bajo ADR-020. El contrato nuevo necesita una relación
diferenciada en el modelo para evitar atribuir esa autoridad al intercambio
humano.

La indicación del usuario «Aprobado, procede con la implementacion» autoriza
localmente el contrato y el registro de estas relaciones. El modelo incorpora
`rel_log_event_pipeline_operational_evidence` y
`rel_pipeline_ingestion_machine_scope`. Su estado confirmado en el modelo
acredita esa frontera de diseño. La entrega efectiva sigue sujeta a revisión
de los propietarios y configuración de identidad, plazos y límites. Esta
aprobación local conserva la regla de autoridad contractual registrada en
la ampliación de etapa 5.

La confianza del publicador, los reintentos por llegada tardía de las filas
propietarias y la disposición de mensajes agotados continúan en PD-033. El
registro de estas relaciones precede al cableado runtime del recorrido. Los
permisos efectivos y parámetros de despliegue continúan bajo PD-035.

### Consultas de propietario para Correlation

La aprobación local de DD-025 agrega las relaciones de solo lectura
`rel_correlation_pipeline_operational_references` y
`rel_correlation_log_event_evidence_membership`. Pipeline reutiliza la consulta
operativa con un permiso de Correlation separado. Log/Event verifica el UUID
de evidencia dentro de la ejecución e incidente autorizados y el vínculo de
captura persistido. El contrato de recepción desde NLP, los valores de identidad
y el tratamiento de reentregas del broker conservan sus acuerdos y pendientes.
Véase [DD-025](../../model/domain_decisions.md#DD-025).

## Acuerdos locales de Correlation — 11/11/2026

En la continuación de implementación de Evidence Correlation Engine, el usuario
adoptó explícitamente estos cortes de las decisiones pendientes; no cierran
PD-010/031/034 ni acreditan implementación, interoperabilidad o integración en main.
Se conservan DD-014, los IDs operacionales acordados y el ownership existente.

- **Agrupación:** revisiones acumulativas e inmutables por scope de máquina
  confiable, ejecución/intento exacto e incidente automático ORIGIN. Cada evidencia
  verificada nueva amplía el conjunto; repetir un miembro no crea otra revisión.
  No hay ventana temporal, cierre por silencio ni afirmación de cobertura completa.
  No se seleccionó el corte de un snapshot independiente por evidencia.
- **Reentrega NLP:** separar fuente protegida estable de enriquecimiento mutable
  (incluida la plantilla Drain3), conservando el primer resultado aceptado por
  mensaje. Cambiar la fuente bajo la misma identidad scoped sigue siendo conflicto.
  NLP no adquiere almacenamiento propio. El usuario pidió evaluar solapamiento
  antes de elegir un nuevo digest de bytes; ese formato/cálculo no está aprobado.
- **Alcance de edición:** cambios locales en Correlation, NLP y este repositorio
  para remediación de reentrega y documentación de contrato/modelo. No se autorizan
  publicación, merge, despliegue, recursos, secretos o cambios a otros owners.

El [contrato de Correlation](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/deployment-contract.md)
y su [plan de arquitectura](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/architecture.md)
son los documentos de trabajo propietarios; sus cambios de esta sesión siguen
locales y no se presumen disponibles en esos enlaces hasta integración autorizada.
Antes de implementar persistencia/entrega de grupos deben concretarse modelo
físico group/head/receipts, trazabilidad por mensaje y semántica de orden/recepción
de revisiones en Recommendation. El mecanismo de validación de referencias y
propagación del scope máquina sigue pendiente; dos consultas a owners son una
propuesta arquitectónica, no una relación aprobada por este acuerdo.

### Adopción posterior del modelo durable — 11/11/2026

Tras revisar existencia y redundancia de datos, el usuario indicó «apruebo la
propuesta» y autorizó continuar hasta el siguiente punto de decisión. Este
acuerdo amplía el corte local anterior: adopta [DD-023](../../model/domain_decisions.md#DD-023),
las dos tablas técnicas de Correlation, snapshots existentes como revisiones,
ordinal derivado de membresía, receipts por mensaje y un único puntero confirmado
por grupo. También adopta preparar la siguiente revisión solo después de confirmar
la recepción de la anterior. No requiere nueva tabla de revisiones/membresía,
UUID de operación, hash/caché NLP ni cambios en tablas de otros owners.

El modelo físico se concreta y comprueba localmente antes de V2; la migración
rehúsa datos anteriores sin scope/procedencia demostrable en vez de fabricarlos.
No se autoriza migración viva, publicación, merge, recursos, permisos o despliegue.
El próximo punto de decisión es la representación diagnóstica segura mínima que
Recommendation necesita y que debe poder recuperarse idéntica al reintentar; no
reabre el modelo de grupo/receipts aprobado. Los PD mantienen su alcance global
pendiente hasta contratos/evidencia de los owners y aprobación/integración aplicables.

## Cobertura y límites de cierre

### Seguimiento entre repositorios — 06/11/2026

Las fuentes exactas y los gates de cada fila están en la
[matriz XR](cross-repository-reconciliation.md#discrepancias-y-dependencias-que-quedan-abiertas).
Estos localizadores no renumeran PD/DQ ni crean decisiones arquitectónicas.

| Seguimiento | Evidencia actual y límite | Dependencias existentes / acción pendiente |
|---|---|---|
| XR-001 — Ingress | IaC ADR 003 Accepted registra native ingress sin gateway para el MVP; docs/modelo/contratos conservan APIM. | Reconciliación autorizada model-first y exposición/auth por servicio. No se cambia el estado de ADR-003/016 aquí. |
| XR-002 — Blob de workload | IaC registra exclusión aceptada del MVP; modelo/DD-006/Log/Event conservan objetos. Blob de state está fuera de esa exclusión. | PD-016/017/030/031: alinear recuperación/retención y contratos; la exclusión no resuelve disponibilidad de logs originales en GitHub. |
| XR-003 — AI | IaC implementa fundación Foundry account/project Entra-only, sin modelos/grants. | ADR-021 fija el contrato RAG de modelo/dimensión/API/identidad. Endpoint, deployment, región, cuota, grants efectivos, corpus y modelo diagnóstico PD-026 siguen pendientes de validación/entrega. |
| XR-004 — Entrega y fuente | Los siete contratos siguen readiness no aprobado en el corte remoto; el overlay PD-033–036 y la autoridad declarada por el usuario se recuperan ahora en esta rama local con hashes coincidentes. | PD-010/011/027/031/032 y contratos referidos: publicar/revisar los documentos recuperados y concretar regla de aprobación, imágenes/config/probes/access/migraciones. PD-035 se conserva desde sus bytes, no se reconstruye desde menciones. |
| XR-005 — Scope/gates/coste | IaC ADR 004 acepta preparación local dev-only en Students temporal y aprobaciones dev procedimentales; otras premisas de presupuesto/coste y custodia son históricas. Sin despliegue acreditado. | Revalidar oferta/moneda/forecast, acceso, recuperación y activación tras servicios integrados/validados. Planes un día, backups de state 90 días, soft-delete 30 días y backup PG siete días no sustituyen PD-017/030. |
| XR-006 — Frontend/landing | SWA Free hosting-only está aceptado e implementado en IaC; frontend sigue fixtures sin auth/API. La landing accesible es `pipesor-landing` con código y CI dry-run; Workers live solo reportado. | Evidencia de landing/dominios, routing/CORS, Entra y configuración pública de runtime/promoción aún pendiente; no afirmar DNS/TLS ni sitio desplegado. |
| XR-007 — Mensajería/datos | Namespace Standard implementado; entidades/topología siguen diferidas, sin SQL/grants ejecutados. | PD-015/031 y PD-033 reportado: aceptación de topología, schemas/filtros/TTL/settlement, idempotencia/DLQ y llegada independiente de datos. |
| XR-008 — Representaciones | Los modelos/diagramas conservan baseline canónico, no reflejan aún las excepciones MVP ni son inventario cloud. | Mantener historial y perfiles de reproducibilidad; actualizar derivados solo en un cambio autorizado de sus fuentes. |

### Cobertura histórica y ampliación local

- **36 entradas actuales:** las 32 de etapa 3 (2 discrepancias, 9 preguntas únicas, 13 asuntos de evidencia/procedencia, 1 referencia desactualizada y 7 detalles explícitamente diferidos) más 4 detalles de contratos identificados en etapa 5 (PD-033–036).
- **Modelos:** DQ-001–006 → PD-003–008; DCQ-001–003 → PD-009–011; DQ-002 de diseño → PD-004. CF-001 → PD-002; TMD → PD-001. A-001–012 y DA-001–006 conservan su condición de supuestos; su inclusión como evidencia no los aprueba ni exige convertir cada supuesto en otra pregunta.
- **Etapa 2:** aprobación Charter → PD-012; procedencia/aceptación drift → PD-013; los 18 ADRs → PD-014; topología → PD-015; Blob → PD-016; retención → PD-017; prompts → PD-018; TI/Excel → PD-019; localizadores → PD-020; revisión/matriz → PD-021; protocolo/rúbrica → PD-022; corpus → PD-023; cobertura de evaluación → PD-024; A-011/DD/Overview → PD-025; mecanismos/preguntas → PD-003–011/029. Se conserva la matriz de las 50 resoluciones en R.
- **Pendientes históricos que no se reabren:** orquestador OQ-004 → ADR-001; observabilidad OQ-005 → ADR-002; identidad OQ-006 → ADR-003; dashboard → ADR-008; parser → ADR-007. Detector/OQ-001/LogBERT y F1 asociado quedan fuera del MVP por ADR-010. Notificaciones y APIs directas de scanners no son decisiones actuales pendientes: ADR-012/014 delimitan su exclusión. Reporting/audit como servicios no se restauran: ADR-009/011. Consultar I para la evolución completa de los 18 ADRs.
- Ningún vacío prueba por sí solo incumplimiento de un sistema desplegado. La auditoría cubre las fuentes documentales locales, no repositorios de implementación ni registros externos de aprobación ausentes. La política CONTRIBUTING de la organización se consultó para el procedimiento de contribución; no se usa como fuente adicional de decisiones arquitectónicas del producto.

Un cierre futuro requiere evidencia verificable, revisión por autoridad respaldada cuando corresponda y autorización para actualizar el documento propietario. Se conservarán ID, referencia, estado anterior y motivo/evidencia de cierre. Un cambio en este agregado por sí solo no cierra una pregunta de YAML ni modifica un ADR. No se ejecuta aquí ninguna acción de cierre. La inspección original de etapa 3 no inició la etapa 4; la ampliación de etapa 5 no reabre sus correcciones técnicas.

[R]: reconciliation.md
[I]: decisions/index.md
[S]: ../sources/README.md
[CH]: <../sources/P202620027 - Project Charter v.1.3.docx>
[D]: ../sources/tech_drift_resolutions.md
[A]: ../../model/architecture.yml
[M]: ../../model/domain.yml
[C]: ../../model/design.yml
[DD]: ../../model/domain_decisions.md
[DC]: ../../model/design_decisions.md
[O]: ../../Overview.md
