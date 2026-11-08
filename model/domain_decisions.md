# Decisiones del modelo de dominio persistente

SSOT: `model/domain.yml`. `model/db.dbml` es una salida generada en esta iteración, al igual que SQL, el único ER y el diccionario. Las decisiones de aplicación aprobadas están en ADR-018 (Accepted, 2026-10-03).

Autoridad por materia: Project Charter para alcance; INV-*, ADR Accepted y architecture.yml para arquitectura vigente; tech_drift_resolutions y ADR tecnológicos para tecnología; arquitectura-informacion.md para derivaciones funcionales dentro de esos límites. No se usa una precedencia lineal ni se promueven propuestas IA a requisitos core. Los originales Charter/TI/drift no están presentes en este checkout (A-011); no se afirma haberlos leído ni se les atribuyen requisitos adicionales.

Las decisiones físicas adicionales DD-013 a DD-017 y las assumptions se explicitan como implementaciones reversibles dentro del alcance aprobado. Las seis preguntas abiertas permanecen en domain.yml.

Generación: `make validate` y `make db`; `make all` conserva physical/logical/C4 y añade db. Dependencias presentes: PyYAML 6.0.3, D2 0.9.0, @dbml/cli 10.2.0 sobre Node 24.21.0. Reproducibilidad exige las mismas versiones. No se instala PostgreSQL ni pgvector. Sintaxis de referencia: [DBML](https://dbml.dbdiagram.io/docs/) y [D2 SQL tables](https://d2lang.com/tour/sql-tables/).

## DD-001 — Repository separado + Pipeline = monitored GitHub Actions workflow

- id: DD-001
- contexto: La IA presenta repositorio y workflow; el prompt aprueba su identidad de dominio.
- decisión: Repository es entidad propia, con relación 1:N Pipeline. Pipeline representa directamente un workflow monitorizado; no existe workflows.
- fuentes: Prompt aprobado §6.A; architecture.yml#pipeline_service; arquitectura-informacion.md.
- impacto: repositories y pipelines en ops, propiedad de pipeline_service; sin nuevas fronteras C4.
- reversibilidad: Separar workflows requeriría una nueva decisión y migración explícita.

## DD-002 — Incident con 1 ORIGIN + N VERIFICATION

- id: DD-002
- contexto: El incidente nace de exactamente una ejecución fallida; la verificación admite varias ejecuciones.
- decisión: incident_runs usa ORIGIN/VERIFICATION. Un índice parcial garantiza como máximo un ORIGIN; triggers diferidos exigen exactamente uno fallido al commit, con ORIGIN consistente con el pipeline del incidente. No se impone un workflow concreto a VERIFICATION. Se bloquea TRUNCATE de vínculos para preservar el invariante.
- fuentes: Prompt aprobado §6.B; SRC_ADR_010; SRC_ADR_018.
- impacto: Crear incidente y ORIGIN en la misma transacción; cambiar el ORIGIN o el pipeline revalida consistencia. La ejecución fallida es dato de GitHub, no un detector propio.
- reversibilidad: Cambiar cardinalidad o requisito de fallo requiere decisión aprobada y reemplazar constraints.

## DD-003 — Diagnosis append-only versionado

- id: DD-003
- contexto: El diagnóstico evoluciona sin reemplazar las hipótesis anteriores.
- decisión: Cada snapshot tiene versión positiva y única por incidente; actual = mayor versión. UPDATE/DELETE/TRUNCATE se rechazan. Cambiar estado también añade una versión. probable_cause puede ser null en ANALYZING/INCONCLUSIVE; DIAGNOSIS_READY exige causa probable y diagnosis_ready_at.
- fuentes: Prompt aprobado §6.C; architecture.yml#INV-005; SRC_ADR_013.
- impacto: Historial inmutable y lectura de última versión en aplicación. Una futura operación de retención necesita procedimiento controlado explícito; no se crea purge job.
- reversibilidad: Cambiar mutabilidad requiere nueva decisión; las hipótesis históricas pueden migrarse sin perder versiones.

## DD-004 — Recommendation entidad propia

- id: DD-004
- contexto: Una versión puede proponer varias recomendaciones trazables.
- decisión: diagnoses 1:N recommendations, con descripción y marcado crítico conforme al componente de gobierno humano. No se ejecuta remediación automática.
- fuentes: Prompt aprobado §6.D; SRC_ADR_016; architecture.yml#INV-007.
- impacto: FK dentro de diagnosis; recomendaciones no embebidas en un único payload diagnóstico.
- reversibilidad: Puede cambiar representación con migración que conserve diagnóstico y trazabilidad.

## DD-005 — Human review CONFIRMED/CORRECTED/REJECTED

- id: DD-005
- contexto: La IA antigua mezclaba rechazo con causa alternativa; el prompt y Human-in-the-Loop distinguen tres decisiones.
- decisión: CONFIRMED acepta; CORRECTED requiere causa corregida no vacía; REJECTED rechaza sin alternativa validada. PENDING se deriva de ausencia de revisión. Mapping contractual: diagnostic_id → diagnoses.id, reviewer → reviewer_ref, decision → decision, timestamp → timestamp, correlationId → correlation_id. actual_cause/comment son opcionales salvo la semántica CORRECTED.
- fuentes: Prompt aprobado §6.E; SRC_ADR_011; SRC_ADR_016; INV-006.
- impacto: No se persiste ValidationStatus ni PENDING. Se permite historial de revisiones sin imponer una decisión final de cardinalidad adicional. REJECTED con causa alternativa validada debe registrarse como CORRECTED.
- reversibilidad: Cambiar enum o cardinalidad exige decisión funcional y migración; la IA histórica se conserva.

## DD-006 — Blob por referencia, no contenido grande en PostgreSQL

Nota de evolución: representación histórica de Blob sustituida parcialmente por ADR-019 y DD-018 para el MVP; se conserva el texto original como trazabilidad.

- id: DD-006
- contexto: Los logs extensos viven en Azure Blob Storage; el diagnóstico debe conservar evidencia sustentante.
- decisión: evidence_items almacena metadata, summary y excerpt normalizados. storage_container/blob_object_key se informan juntos cuando existen. diagnosis_evidence_links identifica evidencia sustentante por ID lógico. No se guardan SAS, secretos, credenciales ni payload sensible crudo.
- fuentes: Prompt aprobado §6.F-G; architecture.yml#object_evidence_store; INV-001; INV-002; SRC_ADR_013.
- impacto: Permite recuperar el objeto externo con controles existentes; el hash no fija algoritmo. El saneamiento de contenido corresponde a aplicación.
- reversibilidad: Puede evolucionar la localización externa mediante migración de referencias sin duplicar logs en la base.

## DD-007 — diagnosis_source_links para trazabilidad RAG

- id: DD-007
- contexto: consulted_sources debe ser reconstruible por versión.
- decisión: diagnosis_source_links apunta lógicamente a knowledge_chunks; su FK intra-schema conduce a knowledge_documents. Documentos y chunks exigen provenance. Corpus limitado a reviewed_incidents, authorized_technical_documentation y authorized_response_procedures.
- fuentes: Prompt aprobado §6.H-I; architecture.yml#rag_retrieval; diagnostic_output; INV-010.
- impacto: No se incluyen casos de evaluación ni soluciones de referencia en knowledge. Elegibilidad del corpus se verifica en aplicación; texto/provenance no puede validarse semánticamente por una FK.
- reversibilidad: Puede añadirse otra estrategia de provenance mediante decisión posterior conservando la traza existente.

## DD-008 — Cross-schema logical references, sin FK física

- id: DD-008
- contexto: Una instancia compartida no implica ownership compartido ni acoplamiento entre contextos.
- decisión: Todas las referencias cross-schema son logical_ref. DBML no emite Ref ni SQL FOREIGN KEY para ellas. Se permite FK física intra-schema. No hay navegación JPA/ORM cross-context; referencias se resuelven por contratos existentes.
- fuentes: Prompt aprobado §10; SRC_ADR_018.
- impacto: La base no garantiza existencia de IDs remotos; cada owner valida referencias por APIs/eventos de architecture.yml. No se diseñan nuevas relaciones de comunicación.
- reversibilidad: Reversible: una futura decisión Accepted y migraciones podrían introducir FK cross-schema; nunca implícitamente.

## DD-009 — Vector sin dimensión fija

- id: DD-009
- contexto: Azure OpenAI Embeddings está aprobado, pero el modelo concreto no se ha fijado.
- decisión: knowledge_chunks.embedding usa vector sin dimensión. Se genera CREATE EXTENSION IF NOT EXISTS vector. embedding_dimension: null sigue en open_questions. chunk_index se supone base cero; embedding puede quedar null durante carga.
- fuentes: Prompt aprobado §6.I; SRC_ADR_007; DQ-003.
- impacto: No hay vector(1536), índice vectorial dependiente de dimensión ni mecanismo de actualización seleccionado.
- reversibilidad: Una futura elección de embedding requiere decisión y migración de tipo/datos/índices.

## DD-010 — Confidence sin escala cerrada

- id: DD-010
- contexto: La IA muestra un ejemplo numérico que no fija escala de persistencia.
- decisión: confidence JSONB nullable conserva valor o estructura recibidos; no tiene CHECK de rango ni escala numérica cerrada. La representación física es una suposición reversible, no la resolución de DQ-002.
- fuentes: Prompt aprobado §6.C; arquitectura-informacion.md#Confidence; DQ-002.
- impacto: No impone 0..1; consultas interpretan el valor solo conforme a un contrato posterior aprobado.
- reversibilidad: Puede migrarse a un tipo más específico cuando se aprueben escala y semántica.

## DD-011 — CQRS lógico, sin Event Sourcing

- id: DD-011
- contexto: Se aprueba separar commands y queries en aplicación manteniendo persistencia común.
- decisión: Command → Handler/Service → Domain → Repository → PostgreSQL. Query → Handler/Service → Query Repository/Projection → PostgreSQL. Sin Event Sourcing ni Event Store, sin bases físicas de lectura/escritura.
- fuentes: Prompt aprobado §0.E-F; SRC_ADR_018.
- impacto: No se crean SQL views CQRS ni v_incident_queue. Historial diagnóstico y audit_events no son un Event Store.
- reversibilidad: Cambiar a separación física o Event Sourcing requiere nueva decisión arquitectónica.

## DD-012 — Ownership de datos por Bounded Context

- id: DD-012
- contexto: Se aprueban cinco schemas y repositorios independientes por microservicio.
- decisión: ops: pipeline_service; evidence_items: log_event_service; correlated_contexts: evidence_correlation_engine; diagnosis: recommendation_service; knowledge: rag_retrieval; audit: shared. Cada owner escribe solo sus tablas; compartir evidence no permite escribir las del otro servicio.
- fuentes: Prompt aprobado §0.D-G y §5; SRC_ADR_018; SRC_ADR_011.
- impacto: Schema/table ownership se valida contra containers/component parents existentes. No se crean servicios, users, teams ni roles PostgreSQL en esta iteración. Ingesta y NLP pueden mantener dominio ligero sin Aggregates artificiales.
- reversibilidad: Mover ownership requiere decisión explícita y migración; multirepo no se convierte a monorepo.

## DD-013 — Tipos, identidad y claves físicas mínimas

- id: DD-013
- contexto: El prompt aprueba conceptos, pero no concreta todos los tipos y claves físicas.
- decisión: UUID de servicio para PK, text para IDs externos y correlation_id, timestamptz para tiempos, boolean para marcado crítico/fallo, bigint para secuencia/tamaño. Claves compuestas previenen duplicación de workflows, intentos, etapas, chunks y vínculos. Severity y PipelineCriticality son enums distintos. PipelineStage reutilizado se materializa como enum local en cada schema para evitar dependencia física de tipos.
- fuentes: Prompt aprobado §6 y §8; SRC_ADR_018; A-001/A-002/A-003/A-004/A-009.
- impacto: No se fijan versiones Java/Spring/Python ni algoritmo UUID/hash. Solo se genera SQL con tipos PostgreSQL y constraints simples expresables en DBML. No hay taxonomía de log levels interna nueva.
- reversibilidad: Tipos y claves pueden revisarse con migración; identidad y alcance de entidades requieren aprobación explícita.

## DD-014 — Contexto correlacionado mínimo y ownership de evidencia

- id: DD-014
- contexto: Se requiere persistir contexto sin añadir una tabla de asociación no aprobada ni permitir escritura de evidencia ajena.
- decisión: correlated_contexts guarda incident_id/execution_id lógicos, evidence_ids UUID[] lógicos, summary y correlation_id. La colección conserva provenance operacional por los IDs de evidence_items. No se agrega payload crudo ni contexto sensible JSON.
- fuentes: architecture.yml#evidence_correlation_engine; SRC_ADR_015; Prompt §5; A-006.
- impacto: FK de arrays no se generan; aplicación valida referencias y evita fusionar ejecuciones no relacionadas. En ER toda referencia lógica es discontinua, incluida esta relación intra-schema entre owners.
- reversibilidad: Una relación normalizada exigiría aprobación para una tabla adicional y migración; colección es reversible.

## DD-015 — Retención y tiempos sin métricas duplicadas

- id: DD-015
- contexto: ADR-013 define 365 días para logs, diagnósticos y evidencias; TMD se deriva de timestamps.
- decisión: created_at permite retención de evidence_items, correlated_contexts, diagnoses, recommendations y vínculos/revisiones diagnósticas dependientes. detected_at/remediation_started_at/verification_started_at/resolved_at están en incidents; diagnosis_ready_at está en cada versión diagnóstica. TMD = diagnosis_ready_at − detected_at; MTTR puede calcularse secundariamente.
- fuentes: SRC_ADR_013; INV-009; Prompt §6.J y §12; A-002.
- impacto: No se persisten TMD/MTTR. No se extiende silenciosamente el plazo a configuración, corpus ni auditoría. Las consultas escogen la versión/periodo; no se fija una política nueva de agregación KPI. No hay purge jobs.
- reversibilidad: Cambiar retención necesita fuente corporativa/decisión; cambiar timestamps requiere migración explícita.

## DD-016 — Auditoría transversal sanitizada

- id: DD-016
- contexto: La auditoría persiste en PostgreSQL sin audit_service.
- decisión: audit_events conserva categorías exactas de architecture.yml, correlation_id, referencia externa al actor, referencia polimórfica a entidad, acción, estados JSONB opcionales y tiempos. before_state/after_state contienen exclusivamente metadata sanitizada.
- fuentes: SRC_ADR_011; architecture.yml#audit_trail; CTRL-002; Prompt §11.
- impacto: No se registran logs crudos, secretos, tokens, credenciales ni payload sensible no enmascarado. No hay FK polimórfica; saneamiento se valida en aplicación y no se presume garantizado por el tipo JSONB.
- reversibilidad: El formato sanitizado puede evolucionar con contratos aprobados; no habilita Event Sourcing.

## DD-017 — Pipeline access grants IA-only/inferred

- id: DD-017
- contexto: Las capacidades VIEW/OPERATE/CONFIGURE derivan principalmente de arquitectura de información.
- decisión: pipeline_access_grants conserva scope_basis: ia_only y status: inferred; referencia principal Entra ID sin users/roles internos. Es representación provisional, no implementación final RBAC ni requisito core.
- fuentes: arquitectura-informacion.md; SRC_ADR_003; Prompt §7; DQ-005/DQ-006.
- impacto: Se muestra con borde punteado y etiqueta IA-only / inferred; la política de alta de workflows y RBAC seguían abiertas en este corte. DD-019/ADR-020 aprueban después la política MVP; representación física y contratos pendientes conservan su estado.
- reversibilidad: Puede retirarse o cambiarse cuando se apruebe implementación definitiva; nunca promoverla automáticamente.

## DD-018 — Evidencia MVP sin almacenamiento Blob de workload

- fuente y autoridad: ADR-019, Accepted por confirmación explícita del usuario en la reconciliación local de 06/11/2026.
- decisión: evidencia saneada y metadata permanecen en evidence_items; los logs originales se obtienen de GitHub Actions. Se retiran storage_container/blob_object_key y su CHECK conjunto. No se introduce otro formato de localizador, copia completa de logs ni mecanismo de recuperación.
- impacto: DBML/SQL/diccionario se regeneran desde domain.yml; no se ejecuta migración sobre una base existente. Size/hash y referencias lógicas conservan su semántica. Ownership, saneamiento y trazabilidad siguen vigentes.
- pendiente: retención independiente de logs originales, pérdida de acceso/borrado en GitHub y recuperación permanecen en PD-017/030/031; la exclusión no reduce ni demuestra los 365 días de ADR-013.
- reversibilidad: cualquier consumidor existente necesita evaluación de migración y contrato; reincorporar Blob requiere una nueva decisión explícita. El backend Blob de state Terraform no es almacenamiento de workload.

## DD-019 — Alta verificada y capacidades condicionadas al acceso GitHub

- autoridad: confirmación explícita del usuario del 06/11/2026, registrada en [ADR-020](../docs/architecture/decisions/ADR-020-github-user-access-and-workflow-onboarding.md).
- decisión: Pipeline crea/reutiliza Repository y registra Pipeline con datos GitHub verificados por el conector de Ingestion. Grants AIOps no conceden acceso fuera del alcance GitHub vigente; VIEW/OPERATE requieren lectura y CONFIGURE/alta administración efectiva. CONFIGURE incluye VIEW, no OPERATE. El creador recibe CONFIGURE con auditoría atómica; un duplicado no concede grants.
- impacto: complementa DD-001/DD-017 y acota DQ-005/006 a detalles pendientes. Se conserva pipeline_access_grants como ia_only/inferred; no se aprueban columnas, tablas, users/roles/teams, pipeline owners ni asociaciones ORM nuevas. Credenciales/vinculaciones pertenecen lógicamente a Ingestion, nunca a ops ni a audit; su schema y custodia siguen pendientes.
- límites: las APIs humanas de evidencia y diagnóstico requieren contrato para aplicar la restricción sin accesos cross-context. No hay grants automáticos por rol GitHub ni reescritura de IDs/filas históricas. Política aprobada no equivale a implementación ni modifica la retención.


<a id="DD-020"></a>

## DD-020 — Metadata física y custodia del conector GitHub

- autoridad: aprobación explícita local del usuario del 07/11/2026: «Propuesta aprobada», referida a `github-connector-draft-0.2`. No equivale a integración en main, permisos, recursos ni despliegue.
- decisión: cuatro tablas de metadata en schema `ingestion`, ownership de Ingestion, y principios OBO, Key Vault Secrets y validez limitada a petición. `model/domain.yml` 1.2.0 es la SSOT de columnas/restricciones; el contrato semántico pertenece a Ingestion.
- concreción necesaria: FK compuestas de pertenencia diferidas, índices parciales para generación activa/refresh no terminado, CHECKs por fase y triggers de revisión/identidad inmutable. Constraint triggers diferidos al commit comprueban puntero/ACTIVE serializando por la raíz; se rechaza TRUNCATE para conservar invariantes e intenciones. El límite persistente pasa de hasta 18 a hasta 21 tablas por las cuatro aprobadas sobre las 17 anteriores, sin alterar presupuestos ni membresías de vistas.
- matriz física: READY pasa a CLAIMED antes de completar; refresh pasa por REQUEST_MAY_BE_IN_FLIGHT antes de VERSION_SAVED/COMPLETED. BLOCKED no permite repetir el refresh; solo reconcilia a VERSION_SAVED con evidencia del par exacto. Cleanup PKCE completo exige intento terminal. Ninguna referencia exacta acepta el alias `latest`, tampoco vacío o variantes de mayúsculas/espacios; no se inventa formato de versión Azure. Estas guardas no prueban efectos remotos ni recuperación operativa.
- exclusividad: referencias lógicas `generation:<UUID de generación>` y `pkce:<UUID de intento>`, con CHECK de pertenencia y UNIQUE por campo. Prefijos disjuntos y PK impiden reutilización entre raíces/clases sin quinta tabla o dependencia de aislamiento MVCC. No son nombres/URI de vault: el futuro adaptador debe resolverlas inyectivamente al objeto privado y verificar pertenencia de cada versión exacta.
- límites: identificadores/scopes/presupuestos runtime, admisión administrativa, navegador/callback, runner productivo y custodia/retención/backups/restore operativo siguen sin definición. La actualización no almacena tokens/verifier/códigos ni altera grants o datos ajenos. La evidencia de implementación se reporta aparte.

El refresh incierto en `BLOCKED` permanece no terminal, incluso después de registrar una versión exacta tardía y de revincular al usuario. Los resultados de cleanup confirmados o una observación `noLateWrite` no cierran por sí solos esa incertidumbre ni autorizan completar cleanup. El protocolo de reconciliación terminal sigue pendiente: las guardas y el acuse durable de metadata no acreditan recuperación completa ni borrado definitivo de credenciales.

La auditoría funcional compartida de ADR-011 conserva sus contratos de escritura/entrega pendientes en PD-035. Revisiones, timestamps, progreso y `correlation_id` de estas tablas no sustituyen eventos de auditoría funcional ni autorizan escribir un almacén de otro owner.


<a id="github-connector-draft-0.2"></a>

## Definición física del conector GitHub — revisión 0.2 aceptada localmente

**Identificador conservado: `github-connector-draft-0.2`. Aceptada localmente el 07/11/2026 por «Propuesta aprobada», registrada en DD-020; no integrada ni desplegada.** Base de preparación Docs `af9e4d6` (entonces PR #8 abierta y main `18dacfb`). Revalidación del 08/11/2026: PR #8 integrada en main `2f14b36a60ccec0c9d87d2aa2b505e309fc44995`; ADR-020/DD-019 ya están integrados. DD-020 y su modelo físico se preparan por separado para revisión desde ese main; no se atribuyen a PR #8 ni se presentan como integrados. ADR-020/DD-019 definen las fronteras; DD-020 concreta las cuatro tablas en `model/domain.yml`, SSOT de campos/restricciones. Este apartado conserva su explicación y límites; los derivados se producen por generadores.

Selección puntual del usuario el 06/11/2026: «Para PD-027 usaremos Key Vault». La revisión 0.2 adopta ahora localmente OBO, Key Vault Secrets, validez limitada a petición y modelo físico; sus configuraciones operativas siguen pendientes. El [contrato semántico de Ingestion](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/blob/main/docs/deployment-contract.md#connector-contract-proposal-for-decision) desarrolla binding/API y adaptación del consumidor, sin duplicar aquí su diccionario. Esa revisión permanece local/no publicada: el enlace sigue main y no acredita que el borrador ya esté disponible allí.

### Raíz e invariantes de representación

La raíz conceptual es una conexión de `(tenant_id, entra_object_id)`, con revisión y generación actual. Generaciones delimitan identidad GitHub y custodia; intentos y operaciones soportan exclusión/recuperación. Cuatro tablas no implican cuatro agregados: activación/desconexión comparten invariantes y transacciones de la conexión. `GitHubLink` en el código local de Ingestion sigue siendo un snapshot Value Object de lectura; no se lo convierte en entidad JPA por esta propuesta.

Se adopta metadata PostgreSQL de ownership exclusivo `ingestion_normalization_service`, en el namespace **`ingestion`**. Nombres, tipos, nulabilidad y restricciones están aceptados localmente en DD-020 y materializados en el modelo, no inferidos de una implementación. UUID identifica registros internos sin elegir algoritmo; IDs externos GitHub y correlación permanecen texto. Tiempos absolutos usan `timestamptz`/UTC; `created_at` es inmutable y `updated_at` refleja modificación persistida, no observación GitHub ni expiración. No se guardan tokens, códigos OAuth, perfiles, roles, teams o grants ni se crean FK a `ops`, `evidence` o `audit`.

### `ingestion.github_connections` — aceptado localmente

| Campo | Tipo / nulabilidad | Semántica y restricción aceptada localmente |
|---|---|---|
| `id` | `uuid`, no nulo | PK de conexión. |
| `tenant_id`, `entra_object_id` | `uuid`, no nulos | Identidad Entra estable; `UNIQUE(tenant_id, entra_object_id)`. Unicidad adicional adoptada `(id, tenant_id, entra_object_id)` soporta FK compuestas de pertenencia. |
| `revision` | `bigint`, no nulo | Revisión no negativa para CAS; aumenta al modificar estado/puntero de la raíz. No es reloj ni lease. |
| `active_generation_id` | `uuid`, nullable | Una generación publicada actual, o ninguna; FK adoptada `(id, active_generation_id)` a generaciones `(connection_id, id)`, nunca a otra conexión. |
| `created_at`, `updated_at` | `timestamptz`, no nulos | Inserción técnica y última modificación persistida. |

### `ingestion.github_connection_generations` — aceptado localmente

| Campo | Tipo / nulabilidad | Semántica y restricción aceptada localmente |
|---|---|---|
| `id`, `connection_id` | `uuid`, no nulos | PK de generación y FK a conexión; `UNIQUE(connection_id, id)` soporta pertenencia compuesta. |
| `github_user_id` | `text`, nullable solo si nunca se activó | Se fija una vez con la identidad real obtenida del token de usuario; después es inmutable. No hay `UNIQUE(github_user_id)`: no está aprobada la unicidad inversa entre vínculos Entra. |
| `state` | `text`, no nulo | Catálogo cerrado adoptado: `PREPARING`, `ACTIVE`, `BLOCKED`, `INVALIDATED`. `BLOCKED` impide uso incierto; `INVALIDATED` conserva el objetivo de limpieza. |
| `secret_object_ref` | `text`, no nulo | Referencia lógica única e inmutable `generation:<id>`, comprobada y registrada antes de escribir el par. No contiene tokens ni es URL cliente; es intención hasta confirmar una versión. |
| `active_secret_version_ref` | `text`, nullable solo si nunca se activó | Versión **exacta** activada, nunca `latest`; obligatoria en `ACTIVE`, retenida para historia/cleanup al invalidar, sin autorizar uso en otros estados. |
| `access_expires_at`, `refresh_expires_at` | `timestamptz`, nullable solo si nunca se activó | Expiraciones GitHub del mismo par exacto; obligatorias al activar el flujo con expiración, nunca deducidas de `exp` de Key Vault. |
| `activated_at` | `timestamptz`, nullable hasta primera activación | Marca inmutable de primera activación; nunca se borra para simular que la generación no se activó. |
| `revision` | `bigint`, no nulo | Revisión no negativa de estado/versión, comparada con revisión de conexión y generación esperada. |
| `created_at`, `updated_at` | `timestamptz`, no nulos | Fechas técnicas de generación. |

Unicidad parcial adoptada de `connection_id` para `state = ACTIVE`. Puntero de raíz y estado `ACTIVE` deben ser equivalentes al commit: activar/cambiar/invalidar actualiza ambos en una transacción. La FK compuesta solo prueba pertenencia; los constraint triggers diferidos de DD-020 comprueban esa equivalencia bajo lock transaccional de la raíz, sin atribuirla a una FK simple. `ACTIVE` y toda generación con `activated_at` exigen identidad, versión exacta y ambas expiraciones no nulas, conservadas al invalidar. Solo `PREPARING` o `INVALIDATED` nunca activadas admiten valores desconocidos; un aborto termina sin placeholders ni queda `PREPARING` indefinidamente. La aplicación comprueba vigencia al activar/usar; un CHECK no reevalúa el paso del tiempo.

### `ingestion.github_authorization_attempts` — aceptado localmente

| Campo | Tipo / nulabilidad | Semántica y restricción aceptada localmente |
|---|---|---|
| `id`, `connection_id` | `uuid`, no nulos | PK de intento y conexión destinataria. |
| `tenant_id`, `entra_object_id` | `uuid`, no nulos | FK compuesta `(connection_id, tenant_id, entra_object_id)` a la misma identidad/conexión, no a un directorio externo. |
| `expected_connection_revision` | `bigint`, no nulo | Revisión esperada al finalizar; disconnect/relink posterior invalida activación tardía. |
| `expected_generation_id` | `uuid`, nullable | Generación publicada esperada; null cuando se espera ninguna. FK compuesta con `connection_id` cuando existe. |
| `target_generation_id` | `uuid`, no nulo | Nueva generación `PREPARING`; FK compuesta con `connection_id` y unicidad entre intentos. No activa una generación ajena o sustituida. |
| `state_digest` | `bytea`, no nulo | Digest único de state impredecible; algoritmo pendiente de aceptación, sin state en claro. |
| `expires_at` | `timestamptz`, no nulo | Fin del intento; duración pendiente, sin TTL inferido. |
| `phase`, `consumed_at` | `text` no nulo; `timestamptz` nullable | Fases cerradas adoptadas `PREPARING`, `READY`, `CLAIMED`, `COMPLETED`, `FAILED`, `EXPIRED`; consumo se fija una vez al reclamar atómicamente un intento vigente. |
| `pkce_secret_object_ref` | `text`, no nulo | Referencia lógica única `pkce:<id>` dedicada al intento, comprobada y prevista durablemente **antes** de escribir Key Vault. Nunca es el objeto del par de una generación. |
| `pkce_secret_version_ref` | `text`, nullable antes de `READY` o en aborto nunca listo | Versión exacta efímera con el verifier, obligatoria antes de publicar el intento. No se guarda `code_verifier` plaintext ni código OAuth en PostgreSQL; referencia privada fuera de logs, errores y auditoría. |
| `pkce_cleanup_state`, `pkce_cleanup_result` | `text` no nulo; `text` nullable antes de ejecutar | Estado cerrado adoptado `HELD`, `PENDING`, `COMPLETED`, `BLOCKED`; resultado fijo `CONFIRMED`, `UNAVAILABLE`, `SCOPE_UNAPPROVED`, `NOT_APPLICABLE`. Objetivo exclusivo: objeto/versión PKCE registrados. |
| `approved_return_ref` | `text`, no nulo | Referencia a destino previamente admitido, no URL arbitraria del navegador. |
| `correlation_id` | `text`, no nulo | Trazabilidad minimizada; no transporta secretos. |
| `created_at`, `updated_at` | `timestamptz`, no nulos | Fechas técnicas del intento. |

Primero persistir intento `PREPARING`, objeto PKCE previsto y ciclo `HELD`; después escribir Key Vault. Solo un commit local de versión exacta y fase `READY` permite publicar redirect/state. Respuesta Key Vault perdida o fallo antes de `READY` dejan un objetivo durable de recuperación/cleanup, nunca `latest` ni verifier ausente utilizable. Tampoco se escribe el par de generación antes de registrar su objeto previsto. No hay transacción PostgreSQL–Key Vault; el código OAuth solo se canjea en memoria del backend, sin persistirlo ni registrarlo.

Terminalizar/abandonar/expirar intento y marcar cleanup PKCE `PENDING` es una transacción local. El protocolo aceptado determinará cuándo el consumo da paso a limpieza sin interrumpir un canje legítimo; `CLAIMED` no permite borrar verifier mientras se necesite. Conservar intento, referencias/progreso y objetivo previsto hasta completar limpieza y retención aceptada. Una escritura incierta aún capaz de crear material tardío impide declarar cleanup completo. No hace falta una quinta tabla ni operación polimórfica para el objetivo PKCE.

El callback consume una vez desde `READY`, comprobando expiración, fase, identidad Entra esperada y revisiones antes del canje remoto; `code`/`installation_id` no autentican al actor. Luego verifica identidad GitHub real y activa solo target generation bajo CAS y con intento aún `CLAIMED`. Dos intentos pueden compartir revisión esperada: gana la primera activación CAS válida, no necesariamente el último intento iniciado. El perdedor termina/limpia su propio material. [State y PKCE S256 de GitHub](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app) no definen el binding del navegador: origen, redirects, sesión y finalización necesitan contrato. No se asumen cookies cross-origin de una SPA ni se reutiliza el actor workflow de PD-036. State y el challenge se transportan solo en el protocolo controlado; el challenge es público, mientras state se minimiza/protege y no se registra. Verifier/tokens/códigos no se copian a resultados genéricos, errores o logs.

### `ingestion.github_credential_operations` — aceptado localmente

| Campo | Tipo / nulabilidad | Semántica y restricción aceptada localmente |
|---|---|---|
| `id`, `connection_id`, `generation_id` | `uuid`, no nulos | PK y objetivo; FK `(connection_id, generation_id)` a generaciones de la misma conexión. |
| `expected_connection_revision`, `expected_generation_revision` | `bigint`, no nulos | Guardas de activación; no convierten refresh remoto en transacción local. |
| `kind`, `phase` | `text`, no nulos | Tipos cerrados `REFRESH`, `CLEANUP`. Refresh: `PENDING`, `CLAIMED`, `REQUEST_MAY_BE_IN_FLIGHT`, `VERSION_SAVED`, `COMPLETED`, `BLOCKED`; cleanup: `PENDING`, `CLAIMED`, `COMPLETED`, `BLOCKED`. No motor genérico ni payload JSON. |
| `owner_id`, `fence` | `uuid` nullable antes de claim; `bigint` no nulo | Dueño y fencing monotónico de reclamación. Un ejecutor obsoleto no activa metadata. |
| `started_at`, `deadline_at` | `timestamptz`, nullable antes de claim | Inicio/deadline de reclamación; vencer no autoriza repetir refresh remoto. |
| `candidate_secret_version_ref` | `text`, nullable, solo `REFRESH` | Versión exacta nueva confirmada por Key Vault, ligada a operación/generación. Nunca objetivo implícito de cleanup ni búsqueda de `latest`. |
| `cleanup_target_version_ref` | `text`, no nulo en `CLEANUP`/`EXACT_VERSION`; null en otros casos | Objetivo exacto e inmutable, separado del adoptado de refresh y ligado al mismo objeto/generación. No se infiere una versión anterior. |
| `cleanup_scope` | `text`, nullable salvo `CLEANUP` | Catálogo adoptado `EXACT_VERSION` o `INVALIDATED_GENERATION`; conserva el objetivo original tras cambiar generación activa. |
| `upstream_result`, `vault_result` | `text`, nullable salvo `CLEANUP` | Códigos fijos `PENDING`, `CONFIRMED`, `UNAVAILABLE`, `SCOPE_UNAPPROVED`, `NOT_APPLICABLE`; sin cuerpos/mensajes de proveedor. |
| `completed_at` | `timestamptz`, nullable | Solo tras resultado terminal conocido; `BLOCKED` mantiene recuperación/cleanup pendientes. |
| `created_at`, `updated_at` | `timestamptz`, no nulos | Fechas técnicas de operación. |

Restricción parcial adoptada: **un solo refresh no terminado por generación**, incluyendo `BLOCKED` hasta resolución explícita. No abrir otra operación para eludir lease vencido. CHECKs por kind/fase y triggers exigen owner/fence/fechas y referencias apropiadas conforme al modelo; no permiten omitir CLAIMED o la marca de posible envío. Cleanup solo termina con resultados acordados para cada sistema: si una operación remota incierta puede crear material tardío, conserva intención/progreso hasta reconciliarlo. Ese límite también aplica a PKCE y no lo resuelve un fence de PostgreSQL. No basta un lock en memoria.

### Atomicidad y recuperación adoptadas

- Relink crea generación nueva. Identidad GitHub fijada al verificarla nunca cambia en una generación activa. Activar compara conexión, generación, usuario, revisiones y referencias exactas; puntero/estados/revisiones cambian en una transacción local.
- Claim refresh es transacción breve con exclusión durable. Antes de enviar, persistir `REQUEST_MAY_BE_IN_FLIGHT` bajo owner/fence vigente; desde ahí un crash no prueba que no se envió. Durante refresh no terminal no se publican/cargan pares anteriores; indisponibilidad transitoria no finge desconexión definitiva.
- Orden: claim → marca de posible envío → GitHub → par completo en versión Key Vault exacta → referencia adoptada durable → activación CAS. Sin locks/transacciones SQL durante red ni transacción distribuida GitHub–Key Vault–PostgreSQL. Fencing protege metadata, no efectos remotos de GitHub o Key Vault; lease vencido no autoriza reenvío.
- [GitHub refresh invalida el refresh token usado y su access token anterior](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/refreshing-user-access-tokens): perder respuesta puede perder el único par usable. No hay retry ciego, rollback al par anterior o fallback a instalación.
- Disconnect invalida generación/puntero e incrementa revisiones **junto con la intención durable de cleanup en una transacción**. Conservar la generación hasta resolver limpieza/retención. Informar estado local aparte del resultado upstream/Key Vault; un fallo no reactiva contexto ni cambia grants, ACTIVE/PAUSED, monitoreo compartido o retención.

| Fallo | Recuperación adoptada y límite |
|---|---|
| Preparación PKCE/metadata o guardado Key Vault antes de redirect | No publicar intento incompleto. Objeto previsto durable permite limpiar respuesta perdida o fallo antes de `READY`; terminalización y cleanup PKCE atómicos, nunca borrar el par de generación. |
| Callback consumido; canje puede haber ocurrido sin par recuperable | No reutilizar intento/código. Terminalizar y exigir reconexión; no inferir identidad del callback. |
| Refresh reclamado y prueba durable de que no alcanzó posible envío | Unavailable; liberar/reclamar solo bajo guardas. No aplicar esta recuperación cuando envío sea incierto. |
| Refresh puede estar en vuelo, lease vencido o respuesta perdida | No nuevo refresh ni uso incierto. Sin par nuevo duraderamente recuperable, bloquear generación, retirar puntero usable y exigir reconexión. |
| Par recibido, guardado Key Vault fallido/incierto | Recuperar solo con evidencia durable de versión exacta y operación/generación; sin ella, bloquear/reconectar. Nada de `latest` ni par invalidado. |
| Versión guardada; commit/CAS de metadata falla | Reconciliar esa versión/operación solo si generación/revisiones/fence autorizan; si no hay evidencia, bloquear/reconectar. Sin rollback distribuido. |
| Revocación usuario o credenciales definitivamente inválidas | Invalidar uso y requerir reconexión, conservando cleanup; no confundir con outage transitorio. |
| Disconnect/relink gana a trabajo tardío | Rechazar activación por CAS y conservar cleanup de origen. No tocar generación nueva ni otro vínculo del mismo usuario GitHub. Escritura remota incierta aún pendiente impide declarar limpieza finalizada. |
| Restauración de backup de metadata | **No servir automáticamente filas restauradas `ACTIVE`**: el backup puede resucitar un vínculo invalidado aunque GitHub/Key Vault sigan permitiendo sus credenciales. Mantener acceso no disponible/desconectado hasta reconciliación autoritativa o nueva conexión del usuario bajo protocolo aceptado. Un check exitoso de GitHub por sí solo no acredita que no hubo disconnect. |

La detección de restore, su guarda antes de servir y la fuente de evidencia autoritativa deben definirse y probarse en el contrato de recuperación antes de activar persistencia. No se inventa un checkpoint store remoto ni se confía en un flag dentro del mismo backup para demostrar ausencia de invalidaciones. Recuperar Key Vault tampoco vuelve vigente una generación invalidada.

### Custodia y cleanup sin efectos cruzados

El modo aceptado localmente usa un objeto Key Vault Secrets por generación y un par access/refresh con expiraciones proveedor por versión atómica. Metadata guarda referencias exactas, no tokens. [Key Vault Secrets](https://learn.microsoft.com/en-us/azure/key-vault/secrets/about-secrets) no define semántica del par y permite get fuera de `exp`; la aplicación comprueba vigencia/estado/generación. El verifier efímero usa el mismo producto con objeto/referencia separados. No se aplica automáticamente a la clave privada de la GitHub App o installation tokens de máquina: sus ciclos requieren definición propia.

`EXACT_VERSION` usa solo `cleanup_target_version_ref`, sin autorizar borrar un objeto que contiene otra versión activa de la generación. No existe aquí promesa de borrar versiones individuales: el tratamiento admitido de versiones obsoletas sigue pendiente. Borrar objeto completo requiere generación invalidada y ausencia de referencias activas que lo necesiten. `INVALIDATED_GENERATION` conserva su objetivo original y comprueba pertenencia/referencias antes de actuar.

No inferir revocación App-wide de autorización GitHub ni unicidad inversa. Demostrar alcance e idempotencia upstream antes del adaptador; una operación que afecte otro vínculo o credencial activa necesita aprobación explícita de ese impacto. [Soft-delete y purge protection](https://learn.microsoft.com/en-us/azure/key-vault/general/soft-delete-overview) distinguen borrado lógico, material recuperable y purge; no se promete borrado inmediato o de backups. Retención/TTL de credenciales y PKCE no derivan de los 365 días de evidencia.

### Verificación y límites operativos pendientes

Criterios de verificación (evidencia ejecutada reportada en cada entrega; casos remotos no probados por checks locales): unicidad tenant/objeto y FK de pertenencia cruzadas; equivalencia puntero/estado al commit; CAS concurrente/rollback de intenciones; dos intentos con igual revisión, consumo/expiry; crash PKCE entre guardado y `READY`, limpieza durable sin tocar par de generación; refresh paralelo, crash antes/después de marca de envío y lease vencido con llamada en vuelo; respuesta perdida, guardado/activación parcial y escritura Key Vault tardía sin cleanup falsamente completo; errores/logs/auditoría sin tokens/código/verifier/referencias privadas. Con dos vínculos del mismo usuario GitHub y generaciones/versiones sucesivas, probar que cleanup viejo no afecta par nuevo, generación nueva u otro vínculo. Restaurar metadata previa a disconnect, con tokens aún válidos, debe dejar la guarda bloqueada hasta reconciliación/nueva conexión, nunca autorizar por la antigua fila `ACTIVE`.

No se añade allowlist table: fuente administrativa, owner y configuración versionada de admisión siguen pendientes. Tampoco se fijan permisos SQL/Key Vault, identidad runtime, runner de migraciones, plazos/leases, digest, retención/borrado/backups o responsables de custodia/criptografía. Navegador/callback y recuperación operativa tras restore requieren definición antes de sus adaptadores; modelo/DDL local concretan solo las invariantes de metadata aceptadas. No se incluyen grants ni la política de capacidad de Pipeline.

[PD-027/034/035](../docs/architecture/pending-decisions.md) conservan los detalles operativos pendientes sin reabrir DD-020. La autoridad continua de PD-027 no está asignada por esta aprobación puntual. Jhon Galvez y Ramiro Guzman constan para PD-034/035, sin regla documentada de uno/ambos. El modelo y derivados permiten migraciones/verificación local de metadata en Ingestion; runner/identidades productivos, recursos, permisos, secretos y ejecución cloud no están autorizados aquí.
