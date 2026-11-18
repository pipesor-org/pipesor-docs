# Decisiones del modelo de dominio persistente

SSOT: `model/domain.yml`. `model/db.dbml` es una salida generada en esta iteración, al igual que SQL, el único ER y el diccionario. Las decisiones de aplicación aprobadas están en ADR-018 (Accepted, 2026-10-03).

Autoridad por materia: Project Charter para alcance; INV-*, ADR Accepted y architecture.yml para arquitectura vigente; tech_drift_resolutions y ADR tecnológicos para tecnología; arquitectura-informacion.md para derivaciones funcionales dentro de esos límites. No se usa una precedencia lineal ni se promueven propuestas IA a requisitos core. Los originales Charter/TI/drift no están presentes en este checkout (A-011); no se afirma haberlos leído ni se les atribuyen requisitos adicionales.

Las decisiones físicas adicionales DD-013 a DD-017 y las assumptions se explicitan como implementaciones reversibles dentro del alcance aprobado. DQ-003 se cerró mediante el contrato RAG–Recommendation–IaC v0.1 aprobado el 16/11/2026; las demás preguntas abiertas permanecen en domain.yml.

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

## DD-009 — Embeddings RAG dimensionados y versionados

- id: DD-009
- contexto: El contrato RAG–Recommendation–IaC v0.1 aprobado el 16/11/2026 fija el modelo y la dimensión para documentos y consultas.
- decisión: knowledge_chunks.embedding usa vector(1536) para text-embedding-3-small y conserva embedding_model/embedding_model_version. RAG rechaza dimensiones o versiones incompatibles y usa índice coseno HNSW. DQ-003 queda cerrada.
- fuentes: Aprobación explícita del usuario del 16/11/2026; SRC_ADR_007; RAG_RECOMMENDATION_IAC_V0_1.
- impacto: Los vectores anteriores deben reimportarse/re-embedderse; no se reinterpretan. Endpoint, deployment, región y cuota reales continúan como entradas de validación Azure.
- reversibilidad: Cambiar modelo, dimensión o versión requiere migración explícita, re-embedding e índice compatible.

## DD-022 — Alcance e importaciÃ³n administrativa del corpus RAG

- id: DD-022
- contexto: El 16/11/2026 el usuario aprobÃ³ el contrato Recommendation → RAG v1 con identidades GitHub canÃ³nicas, alcance verificado por Recommendation y defensa adicional en RAG, ademÃ¡s de un importador administrativo idempotente sin API pÃºblica ni aprendizaje automÃ¡tico.
- decisiÃ³n: knowledge_documents conserva tenant, instalaciÃ³n, repositorio, pipeline opcional y revisiÃ³n de scope. La carga exige source_id/source_version, hash canÃ³nico, provenance y referencia de autorizaciÃ³n; una versiÃ³n activa sustituye a la anterior. Los casos de evaluaciÃ³n se rechazan. El contrato v0.1 fija text-embedding-3-small/1536, API v1 e identidad administrada; regiÃ³n, endpoint, deployment y cuota se validan en Azure antes de activaciÃ³n.
- fuentes: AprobaciÃ³n explÃ­cita del usuario del 16/11/2026; architecture.yml#rel_recommendation_rag; INV-010; DD-007/DD-009.
- impacto: Recommendation entrega scope previamente verificado y RAG vuelve a filtrar. No se crea relaciÃ³n nueva, crawler, API pÃºblica ni acceso a tablas ajenas.
- reversibilidad: Nuevas fuentes o mecanismos requieren decisiÃ³n posterior; las versiones y hashes preservan procedencia para migraciÃ³n controlada.

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

<a id="capture-publication-draft-0.1"></a>
<a id="DD-021"></a>

## DD-021 — Captura/publicación durable — capture-publication-draft-0.1

**Adopción local del 08/11/2026.** Después de aprobar los contratos de mensajes y revisar el plan concreto de cuatro tablas, evolución del modelo y persistencia JPA/PostgreSQL, el usuario indicó «Vamos a por ello». Esta dirección autoriza concretar `capture-publication-draft-0.1` en `domain.yml` 1.3.0 y sus derivados, migración y checks locales. No constituye integración en main, aprobación de CODEOWNERS, selección de presupuestos numéricos operativos, provisión de recursos, roles o permisos. Conserva snapshot Pipeline v1, evidencia v2, IDs lógicos y at-least-once. Base integrada: `e22627cfee10b0b02edab084b98eb18926c678b5` (PR #9, DD-020). Ownership exclusivo de Ingestion; no ampliar las cuatro tablas de credenciales ni escribir en `ops`, `evidence` o `audit`. El límite persistente/ER pasa de 21 a 25 tablas exclusivamente por estas cuatro adicionales aprobadas; no cambia presupuestos ni membresías de vistas.

**Estado de publicación — 09/11/2026:** DD-020 está integrado mediante PR #9 en `e22627c`; sus estados anteriores se conservan como historial fechado. DD-021 y domain 1.3.0 están publicados para revisión en `feature/capture-publication-contract`, pendientes de integración en main. El contrato y la implementación de Ingestion están publicados para revisión en `feature/github-access-core` de su repositorio; tampoco se acredita integración ni despliegue.

### Representación física adoptada localmente

Se adoptan cuatro tablas en schema `ingestion`. Tres representan recepción, observación y salida; la cuarta conserva aliases de delivery para poder detectar tanto replay con header cambiado como reutilización conflictiva de cualquier delivery registrado. Prescindir de ese alias pierde una de esas garantías: no se sustituye por un array ilimitado ni dedup solo en memoria.

| Tabla | Columnas |
|---|---|
| `capture_receipts` | `id uuid PK`; `capture_domain text NOT NULL`; `tenant_id uuid NOT NULL`; `source text NOT NULL`; `body_digest text NOT NULL`; `app_id`, `account_id`, `installation_id`, `repository_id`, `workflow_id`, `run_id` todos `text NOT NULL`; `run_attempt integer NOT NULL`; `scope_revision text NOT NULL`; `correlation_id text NOT NULL`; `snapshot_message_id`, `evidence_message_id` `uuid NOT NULL UNIQUE`; `phase text NOT NULL`; `revision bigint NOT NULL`; `claim_fence bigint NOT NULL`; `claim_owner uuid NULL`; `lease_until timestamptz NULL`; `observation_id uuid NULL`; `blocked_reason text NULL`; `created_at`, `updated_at` `timestamptz NOT NULL`; `prepared_at`, `published_at` `timestamptz NULL`; `replay_until timestamptz NOT NULL`. |
| `capture_delivery_aliases` | `id uuid PK`; `capture_domain`, `source`, `delivery_id` `text NOT NULL`; `receipt_id uuid NOT NULL`; `created_at timestamptz NOT NULL`. Append-only; no `updated_at`. |
| `capture_observations` | `id uuid PK`; `capture_domain`, `source`, `observation_key`, `protected_content_digest` `text NOT NULL`; `origin_receipt_id uuid NOT NULL`; `repository_id`, `workflow_id`, `run_id` `text NOT NULL`; `run_attempt integer NOT NULL`; `observed_at`, `source_updated_at` `timestamptz NOT NULL`; `observed_at_submicro`, `source_updated_at_submicro` `integer NOT NULL` (0..999); `normalizer_version`, `protection_policy_version`, `correlation_id` `text NOT NULL`; `required_output_count integer NOT NULL` (1 o 2); `created_at timestamptz NOT NULL`. Immutable after preparation; no `updated_at`. |
| `publication_outputs` | `id uuid PK` (public message UUID); `observation_id uuid NOT NULL`; `event_type text NOT NULL`; `schema_major integer NOT NULL`; `fragment_locator text NULL`; `payload bytea NULL`; `payload_digest text NOT NULL`; `phase text NOT NULL`; `revision`, `claim_fence`, `attempt_count` `bigint NOT NULL`; `claim_owner uuid NULL`; `lease_until`, `next_attempt_at`, `last_attempt_at`, `confirmed_at`, `payload_removed_at`, `payload_recover_until` `timestamptz NULL`; `blocked_reason text NULL`; `created_at`, `updated_at` `timestamptz NOT NULL`. |

`capture_domain` es una partición confiable de autorización máquina, nunca un header libre. Su supplier y codificación son inputs pendientes; no se infiere de un token humano ni de IDs webhook. Los IDs externos siguen decimales canónicos positivos textuales, intento entero positivo, tiempos UTC y UUIDs asignados por su owner. `correlation_id` mantiene el valor original seguro y no contiene identidad sensible. `delivery_id` es opaco: su formato no prueba firma ni frescura. Digests privados son SHA-256 lowercase de 64 hex; no se publican como IDs ni incorporan tokens. No guardar body webhook, firma, secret, access/refresh token, verifier, código OAuth ni raw log.

El buffer `payload` contiene exclusivamente bytes JSON finales protegidos, nunca un payload arbitrario de GitHub. No reemplaza la evidencia persistente de Log/Event. Proponer `bytea` evita parsear/reemitir JSON al reintentar; se conserva exactamente lo enviado. Contexto/broker MessageId se derivan de los metadatos inmutables de la observación y del UUID/tipo/major; no se almacenan variantes mutables contradictorias. La validación del contrato y digest ocurre en la aplicación, sin inferir una nueva extensión SQL criptográfica. SQL/logs/bindings y auditoría deben excluir esos bytes.

### Claves y constraints

- Unicidad de recepción `(capture_domain, source, body_digest)`. El digest es del body autenticado exacto; la clave no incluye delivery ID, scope revision ni timestamps de retry. Mismo contenido con otro delivery recupera la misma recepción. El scope actual se revalida igualmente; dedup no concede autorización.
- Unicidad de alias `(capture_domain, source, delivery_id)`. FK de pertenencia `(capture_domain, source, receipt_id)` a la recepción con UNIQUE correspondiente; un delivery previamente registrado no puede apuntar a otro digest/receipt. Registrar recepción y alias de aceptación en una transacción. Ni un alias duplicado ni un body duplicado vuelven a generar IDs de salida.
- Unicidad `(capture_domain, source, observation_key)` para la observación. Recepción y observación declaran explícitamente UNIQUE `(capture_domain, source, id)` para las referencias compuestas. `origin_receipt_id` y `observation_id` usan FK compuestas de pertenencia al mismo dominio/fuente; las dos referencias circulares se validan diferidas dentro de la transacción de preparación. Recepciones equivalentes pueden referir una observación ya preparada solo si su contexto/fingerprint completo coincide.
- `observation_key` y el digest protegido usan la codificación privada v1 del adaptador: JDK `DataOutputStream`, campos UTF-8 prefijados por longitud byte, null explícito, listas con cantidad y campos primitivos en orden estable; SHA-256 lowercase. Incluye dominio/fuente y contexto admitido (tenant/App/account/installation), repositorio/workflow/run/intento, hechos upstream, tiempos fuente como epoch-second+nano y contenido protegido; las etapas tienen orden canónico. La versión del formato canónico (v1) forma parte de la codificación. Excluye UUIDs reservados/generados, correlation, scope revision, reloj técnico y las versiones operativas del normalizador y política de protección; estas últimas se conservan como provenance inmutable. Desplegar una versión nueva con contenido protegido idéntico no crea otra identidad; cambiar el contenido protegido sí cambia su digest. Igual timestamp con distinto contenido no se colapsa; Pipeline conserva su regla de conflicto. El locator público validado es `v1:job:<decimalPositivo>:step:<enteroPositivo>:index:<enteroNoNegativo>`; los números son canónicos sin ceros iniciales salvo index cero. El job ID es identidad GitHub y el locator solo identifica el fragmento seleccionado: no prueba extracción real ni cobertura completa, ni permite adivinar PipelineStage desde nombres job/step.
- Los UUIDv4 de snapshot y evidencia se reservan distintos al aceptar la recepción, antes de normalizar. Una observación usa los UUIDs reservados de su recepción origen; una recepción equivalente conserva sus reservas sin reemplazar los UUIDs/bytes originales. Si no hay evidencia, su UUID reservado queda sin uso. El MVP prepara exactamente un snapshot y cero o una evidencia protegida; `required_output_count IN (1,2)`. Múltiples fragmentos requieren evolución explícita del plan y la reserva de IDs.
- Una salida snapshot por observación, índice único parcial `observation_id` para `execution.snapshot`; una salida por `(observation_id, fragment_locator)` para evidencia. Check de pares `execution.snapshot/1` y `protected_workflow_evidence/2`; locator null solo para snapshot y no vacío para evidencia. Ningún message UUID se reutiliza con otros bytes/contexto. Las filas y `required_output_count` se congelan antes del primer send; un guard diferido verifica exactamente un snapshot y el total acordado.
- Ownership, IDs, digest/contexto original, versiones de protección y plan son inmutables. No FK cross-schema, navegación ORM ajena, DELETE CASCADE ni TRUNCATE que eluda el ledger. Revision/fence/contadores no negativos; claim_owner/lease aparecen juntos solo durante claim; tiempos técnicos coherentes. Fases/claims y limpieza de bytes requieren guardas SQL además del dominio, como en DD-020, no solo setters JPA.

### Fases, transacciones y fallos

Recepción: `ACCEPTED → PREPARED → PUBLISHED`, con `BLOCKED` y razón fija para recuperación explícita. Preparar exige claim exclusivo con owner/fence/lease persistidos; expirar el lease no autoriza un worker viejo a escribir. Revalidar scope antes de lectura y antes de publicación. No mantener una transacción SQL durante GitHub ni broker.

Aceptar verifica firma/body y scope, persiste recepción+alias, y solo después puede devolver 2xx. El trabajo recuperable conserva run/intento y contexto para obtener una observación actual verificable. GitHub puede haber cambiado después del webhook: registrar la versión realmente leída, nunca presentarla como reconstrucción idéntica del pasado. Si no puede recuperarse una observación válida, mantener bloqueo/limitación visible, no éxito vacío.

El MVP adopta **preparación completa antes del primer envío**: una transacción persiste observación, plan cerrado y todas sus salidas protegidas, y cambia la recepción a PREPARED bajo el fence. Una caída antes del commit no deja un plan parcialmente enviable. Fallos de extracción/clasificación/protección no se traducen en cero evidencia correcto. Esto puede retrasar el snapshot de un fallo mientras se recupera su evidencia; publicar snapshot independientemente con evidencia aún pendiente exigiría representar ese segundo plan explícitamente y no forma parte de esta alternativa mínima.

Salida: `PENDING → CLAIMED → CONFIRMED`; un error transitorio o send de resultado incierto vuelve a ser elegible mediante lease/next_attempt_at y siempre conserva UUID, bytes, digest y propiedades. Una salida `BLOCKED` no se borra ni se sustituye por datos nuevos. Solo el claimant/fence vigente confirma resultado. El reenvío estable es correcto por at-least-once; no copiar la prohibición de retry del refresh OAuth a este flujo. Una salida confirmada no se reenvía porque otra falle. La transacción que registra la última confirmación puede marcar PUBLISHED la recepción una vez validado todo el plan.

Confirmación significa aceptación broker, no commit de todos los consumidores ni exactly-once. Claims concurrentes, confirmación perdida, stale acknowledgement y rollback se prueban sobre PostgreSQL real. Procesar evidencia antes del commit del owner remoto sigue requiriendo la recuperación de referencias acordada por Log/Event/Correlation; este ledger no la resuelve con lecturas cross-owner.

### Retención y condiciones previas

`payload_recover_until` y `replay_until` se asignan solo desde una política de horizonte aprobada; `replay_until` es obligatorio, futuro e inmutable desde aceptar la recepción y la falta de un horizonte impide su aceptación durable; no se seleccionan días aquí. Falta de esa política impide activar captura, no autoriza retención infinita ni usar 365 días por analogía. Eliminar bytes permite `payload=NULL` y `payload_removed_at` únicamente cuando la salida está confirmada y venció su horizonte de recuperación; permanecen ID/digest/plan para el horizonte de replay. Pendientes o bloqueados no se purgan silenciosamente. El agotamiento de capacidad produce backpressure/readiness fallida y recuperación operativa. Fuera del horizonte retenido no se promete dedup de replays. Append-only protege el flujo ordinario, no aprueba retención infinita: esta decisión concreta la eliminación de bytes confirmados; la purga controlada de aliases/receipts/observaciones/metadatos y su orden bajo FK todavía necesitan una política aceptada antes de activar captura. No existe operación de purga de metadata aprobada ni implementada aquí.

La representación y canonicalización/locator quedan concretados localmente en esta iteración. `observed_at` y `source_updated_at` guardan la proyección truncada hacia microsegundos; sus compañeros `*_submicro` conservan los nanosegundos restantes (0..999) para reconstruir el `Instant` exacto. Los bytes finales conservan los timestamps originales. La aplicación mantiene digest y claves con precisión completa; no deduplica con una fecha SQL truncada. Antes de activar el runtime hacen falta supplier de scope, corte de revocación, horizontes, capacidad y presupuestos de retry/lease, mapeo job/step→stage y protocolo operativo para bloqueos/material sensible. Las duraciones y horizontes son inputs explícitos de aplicación, sin valores operativos por defecto elegidos aquí. La política aprobada de Key Vault y las cuatro tablas de credenciales no se reabre. Aceptación de este esquema no crea recursos ni permisos; runner y configuración real continúan PD-035.

<a id="DD-023"></a>

## DD-023 — Grupos y recepciones durables de Correlation

**Adopción local del 11/11/2026.** El usuario aprobó explícitamente concretar la
[propuesta revisada de agrupación durable](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/main/docs/deployment-contract.md#durable-grouping-proposal-after-the-reuse-audit)
en el modelo fuente y después en persistencia local. Base integrada consultada:
`65792190d2ee32f0721d22848cd62cee1fd0d630`, más el overlay local de acuerdos
pendientes inspeccionado separadamente. Esta decisión autoriza `domain.yml`
1.4.0, dos tablas técnicas propiedad de `evidence_correlation_engine`, la
asociación del snapshot existente y sus constraints/derivados. No prueba
integración en main ni aprobación de CODEOWNERS o despliegue. El límite del
modelo persistente/ER pasa de 25 a 27 solo por estas dos tablas aprobadas, como
el precedente acotado DD-021; no cambia membresías ni presupuestos C4.


**Reconciliación previa al PR — 16/11/2026.** Main avanzó a `14a71dc44855d60236bdfdeb2d953a2e3edc8de6`, que ya reserva DD-022 para corpus RAG. La decisión local de Correlation se renumera a DD-023 sin cambiar el acuerdo ni el modelo físico; se preservan los cambios de RAG integrados.

### Representación mínima adoptada

| Tabla | Campos y claves adoptados |
|---|---|
| `evidence.correlation_groups` | `id uuid` PK asignada por owner; `scope_key text` no vacío; `execution_id`, `incident_id uuid` lógicos a `ops`; `confirmed_context_id uuid` nullable; `created_at`, `updated_at timestamptz`. UNIQUE `(scope_key, execution_id, incident_id)` y `(id, incident_id, execution_id)` para pertenencia. |
| `evidence.correlated_contexts` | Conserva los siete campos DD-014 y `group_id uuid NOT NULL`; el suplemento del 16/11 añade `signal_stage`, `signal_summary`, `signal_content text NOT NULL`. UNIQUE `(group_id, id)` soporta el puntero del grupo; FK compuesta `(group_id, incident_id, execution_id)` exige la identidad del grupo. La revisión se deriva de `cardinality(evidence_ids)`, sin contador/revision table adicional. |
| `evidence.correlation_receipts` | PK natural compuesta `(scope_key text, producer_key text, message_id uuid)`; `evidence_id uuid` lógico a `evidence_items`; `correlation_id text` original; `context_id uuid` FK al snapshot; `input_fingerprint text`; `created_at timestamptz`. Todos obligatorios. El exportador DBML instalado soporta PK compuesta; no se añade otro UUID de recepción. |

Scope y productor son identidades máquina confiables provistas por la frontera
verificada, nunca autorización deducida de un header/UUID. El grupo particiona
por ejecución exacta de run/intento e incidente ORIGIN. Las referencias
`ops` y `evidence_items` siguen siendo lógicas: no hay FK, consultas SQL ni
navegación ORM a otro owner, aunque comparta schema. La aplicación futura valida
autorización y pertenencia/existencia con los contratos acordados.

### Invariantes y transacciones

- Cada snapshot es un conjunto UUID no vacío, unidimensional, de índice inicial
  1, sin nulls ni duplicados. Su ordinal es cardinalidad positiva, única por
  grupo mediante índice de expresión. La primera revisión tiene un miembro;
  cada siguiente incorpora exactamente uno y conserva los anteriores.
- La preparación bloquea la fila del grupo en una transacción breve. Solo
  permite el siguiente snapshot cuando el último preparado ya es el confirmado.
  La pertenencia compuesta conserva execution/incidente del grupo. Inmutabilidad
  y cadena se comprueban en SQL además del dominio, también para escrituras
  adapter, bulk insert y restauración controlada.
- Un receipt liga scope y evidencia a la revisión donde ese miembro entró por
  primera vez. Varios mensajes/productores pueden compartir ese contexto
  original; no hay regla `evidence_id = message_id`. Cada snapshot exige al
  commit un receipt para su miembro nuevo, insertados atómicamente. Una nueva
  fuente para evidencia existente no genera revisión ni cambia la anterior.
- `confirmed_context_id` empieza null y tiene FK compuesta `(id,
  confirmed_context_id)` a `(group_id, id)` del snapshot. Solo avanza una
  cardinalidad adyacente del mismo grupo; no regresa ni salta. Confirmación
  significa recepción durable downstream, no diagnóstico terminado. El
  snapshot `id` es también la identidad estable de operación downstream.
- ID, scope, execution, incidente y creación del grupo son inmutables.
  `updated_at` inicia igual a creación, nunca retrocede y solo cambia junto con
  un cambio real del puntero. Snapshots y receipts rechazan UPDATE, DELETE y
  TRUNCATE; grupos rechazan DELETE/TRUNCATE y cambios de clave. Las excepciones
  custom usan códigos/mensajes fijos sin IDs, scope, texto o fingerprint.
- Terminar el commit antes de HTTP. Confirmar en otra transacción breve después
  de una recepción autoritativa. Los locks SQL no abarcan I/O ni prueban una
  entrega; repetir el mismo snapshot exige el contrato downstream de contenido
  e identidad. No se crean outbox/worker, retries automáticos ni una ruta de entrega adicional.

El índice técnico `(context_id, evidence_id)` de receipts soporta la comprobación
de miembro al commit y la recuperación por contexto sin escanear todas las
recepciones. No añade otra copia de contenido ni cambia la identidad scoped.

### Suplemento aprobado — señal mínima por miembro, 16/11/2026

El usuario aprobó explícitamente congelar la proyección mínima protegida recibida
de NLP en la primera aceptación de cada miembro. `domain.yml` 1.5.0 incorpora
solo tres columnas a `correlated_contexts`; las 27 tablas, claves, ownership y
referencias permanecen. Esta aprobación local no acredita integración en main,
exposición HTTP ni entrega a servicios vivos.

| Columna | Representación y significado |
|---|---|
| `signal_stage` | `text NOT NULL`, `CHECK` limitado al vocabulario NLP existente: `BUILD`, `TESTING`, `QUALITY_GATE`, `DEPLOYMENT`, `CONTAINER`, `INFRASTRUCTURE`. No crea una taxonomía ni depende del enum de Log/Event. |
| `signal_summary` | `text NOT NULL`, no vacío ni compuesto solo por whitespace; resumen protegido de la señal del miembro nuevo. |
| `signal_content` | `text NOT NULL`, no vacío ni compuesto solo por whitespace; contenido mínimo protegido de esa señal. |

Cada fila de revisión Ri conserva exclusivamente la señal propia del único
miembro que incorporó. `summary` sigue siendo la síntesis del contexto
operacional; no se redefine para guardar señales ni se reemplaza por
`signal_summary`. No se duplican las señales anteriores en arrays acumulativos,
receipts ni una tercera tabla técnica.

El `evidence_id` de esa señal se obtiene como el único valor
`DISTINCT correlation_receipts.evidence_id` cuyo `context_id` es Ri.id. Los guards
de DD-023 ya exigen exactamente un miembro nuevo y receipts anclados a su
contexto original, incluso cuando llegan aliases con otro productor/mensaje.
`correlated_contexts.correlation_id` conserva la traza de incorporación de esa
señal; no selecciona un productor/mensaje canónico ni prueba autenticidad. Las
correlaciones individuales siguen en sus receipts.

Para reconstruir una revisión R se leen los contextos de su mismo grupo con
`cardinality(evidence_ids) <= cardinality(R.evidence_ids)` y sus receipts
originales. Se exige una señal por miembro, identidad de grupo/ejecución/incidente
consistente y membresía exacta respecto de R.evidence_ids; ni orden temporal ni
similitud de contenido sustituyen esas comprobaciones. El alias de un miembro
existente conserva su señal original: contradicción en etapa, resumen o contenido
protegidos produce conflicto. `template` mutable queda fuera de la señal y de la
comparación significativa.

Esta proyección mínima es la excepción explícitamente aprobada a la prohibición
de excerpt duplicado de la decisión inicial. No autoriza `rawLogs` completos,
JSON arbitrario, request/caché íntegros ni hash adicional en NLP. No se incorporan
timestamps fuente u otros campos sin promesa de salida aprobada; `created_at` y
`input_fingerprint` no permiten reconstruir fechas fuente ni contenido perdido.
Las precondiciones de autorización, scope, pertenencia y referencias upstream
siguen vigentes; el suplemento no añade consultas a otros owners, permisos,
clientes RAG/LLM ni orquestación diagnóstica.

Snapshots y receipts existentes permanecen inmutables. La migración de servicio
V3 deberá rechazar filas previas sin señales originales verificables; no fabrica
blancos ni backfill desde fingerprints o evidencia actual. Las pruebas del DDL
fuente se ejecutan sobre un esquema nuevo con texto protegido sintético y no
demuestran una migración de datos existentes.

### Comparación, migración y límites

`input_fingerprint` adopta la envoltura privada versionada
`v1:sha256:<64 hex lowercase>` sobre input protegido significativo. La forma
SQL no selecciona los bytes canónicos: orden, null/ausente, precisión y campos
se concretan antes de habilitar el receptor. Excluye credenciales/trazas y
`template` mutable; una repetición equivalente recupera el primer resultado
aceptado, nunca lo reescribe. El fingerprint no es un hash wire de NLP ni prueba
autenticidad o persistencia del owner. No almacenar request/raw body/log,
excerpt duplicado fuera de la proyección mínima aprobada en el suplemento,
secreto o código de proveedor. Correlaciones individuales
permanecen en sus receipts; la correlación del snapshot no las sustituye.

No se fabrican grupo, scope, productor, mensaje ni receipts para filas V1.
Una migración posterior inspeccionará datos existentes y rechazará el caso sin
mapeo aprobado respaldado por evidencia; V1 no se modifica. Tampoco se elige
backfill, TTL, horizonte de replay, cuotas, purge ni extensión automática de
retención. La retención de evidencia DD-015 permanece; las dos tablas técnicas
no heredan 365 días. Borrar metadata necesita política/operación controlada
posterior que preserve referencias y no reinicie grupos/replays silenciosamente.

La representación segura enviada, la recepción de Recommendation, los límites
operativos, los contratos de referencias, las identidades y la recuperación
externa siguen sus decisiones pendientes. Esta fuente y sus pruebas no aprueban
un receptor REST ni afirman integración con NLP/Recommendation; no crean
recursos, permisos o secretos y no autorizan publicación ni cloud.
<a id="DD-024"></a>

## DD-024 — Recepción durable de contexto en Recommendation

- autoridad: aprobación explícita del usuario del 16/11/2026 del contrato Correlation → Recommendation v1 y aprobación posterior de su tabla técnica durable.
- decisión: `diagnosis.correlated_context_receipts`, propiedad exclusiva de `recommendation_service`, conserva la representación saneada y autocontenida aceptada de Correlation. `operation_id` coincide con `context_id`; el fingerprint SHA-256 versionado determina replay idéntico frente a conflicto. El alcance verificado, identidades lógicas, evidencia, resumen y correlación se insertan atómicamente antes de responder `accepted`.
- idempotencia: el mismo `operation_id` y `context_id` con fingerprint idéntico devuelve `duplicate` sin otra escritura. Reutilizar cualquiera de esas identidades con contenido diferente devuelve conflicto y no modifica la fila. No se usa memoria de proceso ni se crea un diagnóstico como recibo.
- límites: la fila acredita recepción durable, no diagnóstico terminado, autorización histórica perpetua ni existencia de referencias ajenas. No introduce FK cross-context, acceso directo a tablas de otros owners, inferencia LLM, worker o despliegue. Conserva RET-001 por contener contexto/evidencia diagnóstica saneada; el mecanismo de purga sigue pendiente.
- implementación: Recommendation mantiene la migración y transacción funcional. Correlation conserva su snapshot y reenvía la misma operación ante resultado desconocido. La identidad Entra, headers y validación REST pertenecen al contrato aprobado; valores reales y grants continúan separados.


### Suplemento aprobado de DD-023/DD-024 — scope histórico y señales recuperables, 17/11/2026

El usuario aprobó explícitamente la ampliación del modelo para el siguiente
incremento local de Correlation y Docs. Sobre el modelo integrado 1.6.0,
`domain.yml` 1.7.0 añade cinco campos al snapshot propietario de Correlation:
`scope_tenant_id uuid`, `scope_github_installation_id text`,
`scope_github_repository_id text`, `scope_pipeline_id uuid` nullable y
`scope_revision text`. Instalación/repositorio son decimales positivos canónicos
de hasta 32 caracteres; revisión usa el vocabulario opaco seguro de DD-024.
Pipeline sigue siendo referencia lógica, sin FK cross-context.

El scope se congela atómicamente con el snapshot/receipt y se recupera por la
misma operación. El guard rechaza cambios de tenant, instalación, repositorio o
pipeline entre revisiones del mismo grupo; `scope_revision` puede cambiar sólo
en un snapshot nuevo, sin reescribir los anteriores. Esto no modifica ni parsea
`scope_key`, la identidad de grupo o la serialización aprobada. Replays/aliases
no reemplazan el scope original y su comparación significativa se verifica en
el store. La autoridad vigente se comprueba separadamente: ni el envelope ni un
ID acreditan autorización, existencia upstream o permiso tras revocación.

DD-024 conserva su receipt y añade `signals jsonb NOT NULL`: exclusivamente un
array ordenado de objetos con `evidence_id`, `origin_context_id`, `correlation_id`,
`stage`, `summary`, `content`. Todos son strings; IDs tienen forma UUID, etapa
reutiliza el vocabulario NLP, textos protegidos no vacíos y correlación conserva
la forma segura. El DDL comprueba shape, claves exactas, miembros sin duplicados
y coincidencia exacta con `evidence_ids`; la lista de IDs también debe ser un set
UUID unidimensional sin nulos. No prueba que `origin_context_id` exista ni que el
orden represente incorporación: esa validación pertenece al contrato/receiver.
No se permite request crudo, claves extra ni otra copia genérica del payload.

El receipt es append-only; el generador aplica su marcador ya declarado mediante
un trigger a esta tabla. La recepción debe persistir scope/contexto/señales antes
de `accepted`; replay idéntico es `duplicate`, conflicto no tiene efectos y el
recibo no acredita diagnóstico terminado. No se añade tabla ni integración RAG.
El código y la migración de Recommendation quedan para su responsable; este
incremento sólo evoluciona la fuente y sus fixtures, no ese servicio.

Estas modificaciones son aprobación local de persistencia, no integración en
main ni aprobación completa de wire/codec/límites. Correlation usará una nueva
migración sin alterar V1–V3, con mapeo verificable de provenance previa o rechazo
atómico, nunca backfill desde datos actuales/digests. No se inventan autoridad,
permisos, llamadas owner, presupuestos, saneamiento, purga ni activación REST.

<a id="DD-025"></a>

## DD-025 — Vínculo de ámbito de evidencia en Log/Event

**Adopción local.** El usuario aprobó el cambio de modelo y las dos consultas de
Correlation con «Aprobado sigue», tras revisar la propuesta de pertenencia.
Log/Event conserva tenant, instalación y revisión de captura en la propia
fila desde el primer registro autorizado. Los tres campos son completos o
todos nulos para permitir filas anteriores sin procedencia verificada. La
reentrega compara el vínculo y preserva la fila original ante cualquier
conflicto. Nunca se atribuye un ámbito legado desde la petición actual.

Log/Event valida la pertenencia bajo el UUID de evidencia, ejecución,
incidente y los tres campos del vínculo. Consulta únicamente después de
autorizar al caller de Correlation para la operación y el ámbito. Correlation
confirma el ámbito vigente y el intento ORIGIN con Pipeline antes de llamar.
Ausencia y fila fuera de la consulta acotada se devuelven como `NOT_READY`.
Log/Event conserva su propiedad y sus referencias lógicas. El modelo
conserva únicamente la representación protegida y su política de retención.
