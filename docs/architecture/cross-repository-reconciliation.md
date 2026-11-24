# Reconciliación entre repositorios — 06/11/2026

Corte de evidencia: 06/11/2026 (America/Lima). Informe documental, no ADR ni
aprobación de arquitectura/despliegue. Distingue lo declarado en decisiones, código
integrado, propuestas y recursos realmente observados. Las fuentes vecinas se
consultaron en copias temporales de sus ramas por defecto; no se modificaron.

## Evolución posterior: alineación canónica MVP

La [decisión ADR-019](decisions/ADR-019-align-mvp-with-iac.md) registra la confirmación explícita del usuario del 06/11/2026 y la alineación model-first de native ingress, exclusión de Blob de workload, Foundry y preparación dev-only. Resuelve el desfase de representación canónica de XR-001/002/003/005; no cierra contratos, autenticación, grants/modelos AI, conservación/recuperación ni preparación de despliegue. Los datos de IaC se contrastaron también con `4b42c0c8e66578dfb890ae1cca8c9c31c774026e` (incluye el ciclo de identidad por aplicación).

Las tablas siguientes conservan el corte histórico previo a esa alineación. Sus expresiones «modelo conserva APIM/Blob» y «reflejo canónico pendiente» describen ese corte, no el modelo activo posterior a ADR-019. El Blob de state y las autorizaciones específicas de operaciones Azure permanecen separados.

## Actualización acotada: piloto CI/CD — 08/11/2026

El corte siguiente conserva sus revisiones históricas. Pipeline ya dispone de
aplicación local en su main consultado `0e7eed9420e7e54d7b336c22b0452c8b6fb722ba`;
la entrega CI/CD en revisión añade workflows, imagen y recuperación inactiva.
La [guía actual del piloto](../development/cicd.md) distingue código preparado,
pruebas locales, verificación hosted del PR y publicación/cloud pendientes, y
remite al README del servicio.
No extrapola la evolución de Pipeline al estado de los otros servicios ni cierra
XR-004/PD-035. No se reescriben las tablas del corte previo.

## Auditoría documental frente a origin/main — 24/11/2026

Corte independiente de las tablas de 06/11 y 08/11, que se conservan como historia.
Objetivo: alinear pipesor-docs con lo implementado en `origin/main` de cada repositorio
y con sus propias decisiones, dentro de la autorización del responsable del 24/11/2026.
Es un informe documental: no aprueba decisiones, no cierra PD ni `open_questions`, no
edita ADR Accepted y no acredita despliegue.

Revisiones consultadas (lectura con `git show`/`git archive` de `origin/main`, sin
modificar checkouts): docs `da552d8`, pipeline `dcaa002`, ingestion `6ecca4c`,
log-event `31a86e0`, correlation `533fa53`, recommendation `3d53d26`, NLP `73451c3`,
RAG `4fd400f`, frontend `ad0e135`, IaC `388e5a7`, workspace `038ba20`,
validation-scenarios `c8cafb4`, pipesor-ci `df3b5fc`.

Método:

- **Base de datos:** se aplicaron todas las migraciones Flyway en PostgreSQL 16.15/pgvector 0.8.7 desechable, y en otra base `schema.sql` + `extras.sql`; después se compararon ambas por introspección. Flyway se emuló con psql, por schema y versión. Las tres revisiones Alembic de RAG se tradujeron a SQL a mano porque Alembic no está instalado.
- **APIs e interacciones:** se leyeron los controladores, los clientes HTTP y la configuración de seguridad en el código. El OpenAPI vivo del stack local (8081, 8082) solo sirvió de contraste.
- **Resto:** se revisaron los modelos, ADR, DD, PD, guías y enlaces.

### Matriz resumida

Severidad: A alta, M media, B baja. Acción: el PR que lo corrige, o «decisión» si
queda en las preguntas siguientes.

| ID | Artefacto | Qué dice | Qué hay en origin/main | Sev. | Acción |
|---|---|---|---|---|---|
| A-01 | `domain.yml` `ops.incidents` | Sin `display_number` | pipeline@dcaa002 `V7__add_incident_display_number.sql:4-25` | M | #54 |
| A-02/03 | `evidence_items`, `correlated_contexts` | Sin localizador | log-event@31a86e0 `V3__retain_aggregate_source_locator.sql:1`; correlation@533fa53 `V5__retain_signal_source_locator.sql:1` | M | #54 |
| A-04 | `correlated_context_receipts.signals` | Exactamente 6 claves | recommendation@3d53d26 `V4…:14-15`, `V5__relax_signal_locator_to_shape.sql:20-22` (7.ª clave opcional) | M | #54 |
| A-05/07 | `diagnosis.diagnoses` | Sin `authorization_scope`, `output`, `admission_fingerprint`, `context_id`, `execution_id` | recommendation@3d53d26 `V2…:1-10`, `V3…:1-3`, `V6…:3-23` | A | #54 |
| A-08, C-01..05 | `diagnoses` y 3 tablas de `diagnosis` | `status`, `probable_cause`… y `recommendations`, `diagnosis_evidence_links`, `diagnosis_source_links`, trigger append-only | Ninguna migración V1–V9 los crea; el contenido va en `diagnoses.output` | A | decisión |
| A-09/10 | `diagnosis.human_reviews` | Sin `revision` ni `corrected_recommendation` | recommendation@3d53d26 `V2…:15,23-27` | M | #54 |
| A-11 | `human_reviews.comment` / DD-005 | Comentario opcional | `V8__make_review_comment_optional.sql:3-6` lo exige en REJECTED | M | decisión |
| A-12 | `knowledge_chunks.document_id` | FK sin acción | rag@4fd400f `20261111_01…py:52-57` `ON DELETE CASCADE` | M | decisión |
| A-13/14 | `knowledge.*` | `text`, sin CHECK de contenido | rag@4fd400f `01…py:21-30,66`; `02…py:19-25`; `03…py:34-43` (`varchar(n)`) | B | #54 |
| O-01 | DQ-001, A-005, PD-003 | Severidad sin regla aprobada | pipeline@dcaa002 `V8__seed_incident_severity_from_criticality.sql`; `mvp-http-api-v1.md` «MVP rule» | A | decisión |
| O-03 | `audit_events` `owner_container: shared` | Owner compartido | pipeline@dcaa002 `V6__create_audit_events_if_absent.sql` (owner MVP: Pipeline) | M | decisión |
| B-01 | `architecture.yml` | Sin Recommendation → Pipeline (ADR-027) | recommendation@3d53d26 `PipelineDiagnosisSummaryPublisher.java:29-33`; pipeline@dcaa002 `DiagnosisSummaryController.java` | A | #55 |
| B-02 | `architecture.yml` | Sin la consulta de entitlements | recommendation@3d53d26 `PipelineDiagnosisEntitlements.java:26-40`; pipeline@dcaa002 `DiagnosisEntitlementController.java` | A | #55 |
| B-03..08, B-14 | Etiquetas y autenticación de 6 relaciones | Previas a ADR-022–028 | Captura por workflow, sign-in, colaboradores, cola e insights, token de plataforma y OIDC | M/B | #55 |
| B-05 | `rel_dashboard_entra` | Dashboard autentica con Entra | Sin MSAL; login GitHub vía Ingestion (ADR-022) | A | decisión |
| B-11 | Elementos | Sin Key Vault | Claves de firma y secretos en Key Vault (iac@388e5a7 `modules/workloads/main.tf:46-58`; ADR-022) | M | decisión |
| B-09/10, B-16/17 | Relaciones de diseño | Dashboard → Log/Event, Monitor → Ingestion, orquestador `in-process sync` | Sin implementación; cola `diagnosis_jobs` con worker; API v1 | M/B | decisión |
| C1-01 | `mvp-http-api-v1.md` §Conventions | `pageSize`/`pageToken`, 24 por defecto | Listas de Pipeline con `offset`/`limit` (25): pipeline@dcaa002 `PipelineController.java:83-123`, `PageResource.java:5` | A | #56 |
| C1-02 | `mvp-http-api-v1.md` análisis | Condiciones OPERATE de ADR-020 | Ingestion exige administración GitHub: ingestion@6ecca4c `GitHubAnalysisHandler.java:96-97` | A | decisión |
| C1-03..24 | `mvp-http-api-v1.md` | Parámetros, errores, CORS, reviews, `activities` | Comportamiento real documentado | M/B | #56 |
| C1-10/12/21/25 | `mvp-http-api-v1.md` | — | Historial de reviews con `reviewer`; 400 por `X-Correlation-ID`; errores de capture-scope; webhook sin contrato | M/B | decisión |
| C2-01..10, C2-23 | `platform-identity-v1.md` | Catálogo y login incompletos | Rutas, `returnTo`, sin token, membership/operational checks | M/B | #57 |
| C2-15 | `rag-integration-v0.1.md` | Tokens Entra | Tokens de plataforma (ADR-022) | M | #56 |
| C2-17 | ADR-021, `rag-integration-v0.1.md` | Identidades PostgreSQL separadas, sin DDL en runtime | Una sola identidad `rag` con `CREATE` (iac@388e5a7 `main.tf:324,328,402-431`) | A | decisión |
| C2-05/06/12/16/18/19 | Identidad y RAG | §6, §7, ADR-022 memoria, system-assigned, valores por entorno, timeouts | Sin comprobar `repository_owner_id`; sin solapamiento de claves; `sessionStorage`; user-assigned; endpoint dev fijo; reintentos 401/403/422 | M | decisión |
| D-01..08 | `decisions/index.md` | 21 ADR; faltan filas y enmiendas | 28 ADR; enmiendas de ADR-019..028 | A | #57 |
| D-04 | ADR-020 | Accepted | Editado tras su aceptación (PR #32, #34) | M | #57 (registro) / decisión |
| D-09, E-01 | ADR-008, `runtime-manifest.md` | Dashboard en Static Web Apps | Container App: iac@388e5a7 `modules/workloads/main.tf:30,247-300` | A | decisión |
| D-22 | `README.md` estado 06/11 | Servicios en readiness, frontend con fixtures | Servicios implementados; frontend con login GitHub y API reales | A | #58 |
| E-* | `docs/development/*` | Modelo, roles, rutas públicas, demo, CI | ADR-024..028, gpt-6-luna, catálogo real | M | #57 |
| F-* | `design.yml` | Clases `proposed` | Sin referencias rotas; deriva esperable (JDBC, paquetes, cola asíncrona) | B | informe |
| G-01 | `pending-decisions.md:248` | Enlace a `docs/local-product-mvp.md` | Borrado en frontend `2c3a851` | B | #57 |

### Corregido

- **#54 — `fix(domain)`:**
  - [DD-027](../../model/domain_decisions.md#DD-027) y `domain.yml` 1.10.0 reconcilian siete tablas modeladas con sus migraciones;
  - el validador admite `varchar(n)`;
  - los registros congelados, las pruebas y `design.yml` (atributos espejo) se actualizan.
- **#55 — `fix(architecture)`:**
  - añade las dos relaciones Recommendation → Pipeline;
  - corrige etiquetas y autenticación de seis relaciones;
  - registra ADR-022..028 como fuentes;
  - añade etiquetas y rutas de presentación.
- **#56 — `docs(contracts)`:** alinea `mvp-http-api-v1.md`, `rag-integration-v0.1.md` y `protected-evidence-v2.1.md` con el comportamiento real. Las divergencias quedan anotadas sin adoptarlas.
- **#57 — `docs`:** alinea `platform-identity-v1.md`, el índice de ADR, las guías de `docs/development/`, la nota de CI del README y el enlace roto de PD.
- **#58 — `docs(reconciliation)`:** este apartado y el estado del README.

### Preguntas para el responsable

**Datos (DD-027):**

1. `diagnosis.diagnoses`: ¿adopta el modelo el snapshot `output` (retirando `status`, `probable_cause`, `explanation`, `limitations`, `confidence` y `diagnosis_ready_at`, y sustituyendo DD-003, DD-010 y el cálculo de TMD de DD-015), o debe Recommendation materializar esas columnas?
2. ¿Se retiran del modelo `diagnosis.recommendations` (con su marcado `critical`), `diagnosis_evidence_links` y `diagnosis_source_links`, o se implementan?
3. ¿Se exige a Recommendation el trigger append-only de `diagnoses` (DD-003), o basta la inmutabilidad por aplicación?
4. ¿Se enmienda DD-005 para exigir comentario en REJECTED (Recommendation V8), o se retira esa regla?
5. ¿Se amplía `domain.yml` con acciones referenciales (`ON DELETE CASCADE` de RAG)?
6. `audit.audit_events`: ¿Pipeline como owner MVP (su V6) o `shared` (DD-012, DD-016, PD-035)?
7. ¿Se cierran DQ-001, A-005 y PD-003 con la regla MVP «severidad inicial = criticidad del pipeline» que ya aplican Pipeline V8 y el contrato?

**Arquitectura:**

8. ¿Se retira o reetiqueta `rel_dashboard_entra` (y la narración de la vista 2B), ya que ADR-022 sustituye el login Entra en el MVP?
9. ¿Se modela Key Vault como elemento, con relaciones desde las siete cargas? ADR-022 lo nombra.
10. Dashboard en Container App frente a ADR-008 (Static Web Apps): propongo un ADR nuevo que enmiende ADR-008. ¿Se redacta?
11. `pretrained_llm_diagnostic_service` dice `model_family: GPT-4` y ADR-026 fija gpt-6-luna solo para dev y OE3-I2. ¿Cómo se refleja? Los generadores y las pruebas tienen «GPT-4 family» fijo en el código.
12. ¿Se mantienen como diseño `rel_dashboard_log_event_service` y `rel_observability_sources_ingestion`, que no tienen implementación?
13. ¿Pasa `rel_diagnostic_api_orchestrator` a asíncrona con cola durable, y se promueve `diagnosis_jobs` desde `inferred`?

**API e identidad:**

14. Análisis y captura de verificación: ¿rige OPERATE más lectura GitHub (ADR-020, contrato) o administración GitHub (implementación de Ingestion)?
15. ¿Debe el historial de reviews ocultar `reviewer` y los textos libres a quien solo tiene VIEW, como hace la proyección de diagnóstico?
16. Ante un `X-Correlation-ID` inválido, ¿400 (Ingestion) o generar uno nuevo (contrato)?
17. ¿Qué contrato documenta el webhook `/webhooks/v1/github/workflow-runs`, que IaC activa? ¿Hace falta un ADR?
18. ¿Se migran las listas antiguas de Pipeline a `pageSize`/`pageToken`, o la convención admite `offset`/`limit`?
19. RAG: ¿se separan las identidades de consulta, importación y migración, sin DDL en runtime (ADR-021), y se pasa a identidades system-assigned? ¿Cómo se parametrizan endpoint y deployment por entorno?
20. ¿Se fijan el timeout externo, los reintentos y la no-degradación de Recommendation ante RAG (pregunta abierta 5)? Hoy se reintentan también 401/403/422.
21. Identidad: comprobación de la cuenta de instalación en OIDC (§6), solapamiento de claves al rotar (§7) y tokens del dashboard en `sessionStorage` frente a ADR-022. ¿Se corrige la implementación o el contrato?

**Decisiones y diseño:**

22. ADR-020 se editó tras su aceptación (PR #32 y #34). ¿Se confirman esas enmiendas o se registran en un ADR nuevo?
23. PD que parecen resueltos para el MVP: PD-011, PD-028 y PD-036. Parcialmente: PD-007, PD-008, PD-010, PD-015, PD-022/023/024, PD-026, PD-027, PD-031..035. ¿Se cierran o se actualizan?
24. `design.yml`:
    - ¿Se actualizan paquetes y persistencia (JPA frente a JDBC) a la convención Java vigente?
    - DCQ-002 y DCQ-003 están parcialmente contradichas por contratos aprobados.
    - CD-1 ya tiene 15 nodos, justo el máximo, para añadir la API del informe de Actions.

### Respuestas del responsable — 24/11/2026

El responsable respondió parte de las preguntas el mismo día y pidió atender las observaciones de
la revisión del Capstone v1.2:

- P3: hosting del dashboard sin ADR; las Figuras 1 y 4 siguen mostrando Static Web Apps.
- Las Figuras 1 y 7 son idénticas a las de entregas anteriores, y la 7 trunca rótulos.
- Las figuras se ven poco.
- Retirar Entra ID como autenticación y usar GitHub OAuth con PKCE.

La revisión de `origin/main` se repitió sobre:

| Repositorio | Revisión |
|---|---|
| docs | `c240269` |
| pipesor-iac | `318af56` |
| frontend | `2806ae1` |
| workspace | `168d72d` |
| Ingestion | `a41188a` |
| Pipeline | `f6b64c3` |
| Log/Event | `5f3475f` |
| Correlation | `be231a0` |
| Recommendation | `c3ce559` |
| NLP | `d70a81a` |
| RAG | `312b520` |

#54–#58 ya estaban fusionados.

| Pregunta | Respuesta | Acción |
|---|---|---|
| 4. Comentario en REJECTED | Opcional en este semestre, para no contaminar el corpus de validación. En OE4 cada REJECTED podría alimentar el RAG. | [DD-029](../../model/domain_decisions.md#DD-029) conserva DD-005. Quedan por alinear la CHECK de Recommendation V8 y el contrato MVP, que aún lo exigen. La idea de OE4 queda en PD-037, que sigue abierta. |
| 5. `ON DELETE CASCADE` | «Propón algo». | Propuesta abajo, no implementada. |
| 6. Owner de `audit.audit_events` | Pidió la opción más coherente. | Recomendación abajo; la decisión sigue abierta. |
| 8. `rel_dashboard_entra` | Se retira. | #63: sin `entra_id`; inicio de sesión con GitHub (OAuth + PKCE S256 mediante Ingesta, ADR-022/029). Entra queda como identidad administrada ante recursos Azure, como decide ADR-022. |
| 9. Key Vault | Debe modelarse: está en Terraform y guarda secretos. | #63: `azure_key_vault` con seis relaciones de firma, más la custodia y el material de la App de Ingesta. |
| 10. Dashboard en Container App | Redactar el ADR. Static Web Apps se descartó por la suscripción Azure for Students. | #63: [ADR-030](decisions/ADR-030-dashboard-on-azure-container-apps.md). Static Web Apps no se ofrece en las regiones permitidas. |
| 11. Modelo LLM | gpt-6-luna. | #63: `gpt-6-luna` 2026-09-22, con el alcance de ADR-026 (dev y OE3-I2). PD-026 sigue abierta para otros entornos. |
| 15. Historial de reviews | «Verifícalo». | Verificado: **sí** se expone (detalle abajo). #64 lo registra en el contrato; decidir si se oculta sigue pendiente. |
| 17. Webhook | Debe estar en un contrato. | #64: [contrato del webhook v1](contracts/github-workflow-webhook-v1.md). No hace falta ADR: el enrutamiento ya lo decide ADR-023 y la admisión ADR-024. |
| Figuras del Capstone | Confirmar la poca visibilidad y mejorarla. | Confirmado (detalle abajo). #63 añade variantes de impresión en `out/doc/` y corrige el contenido de las Figuras 1, 4 y 7. |

Siguen sin respuesta las preguntas 1–3, 7, 12–14, 16 y 18–24.

**15. Historial de reviews.**

- Recommendation `c3ce559` exige OPERATE solo en `POST /api/v1/diagnoses/{id}/reviews`.
- El `GET` responde a quien tiene VIEW con cada entrada de `history[]`, que incluye:
  - `reviewer`: el sujeto de plataforma, UUIDv5 del ID de usuario GitHub; no es el login, pero es estable entre diagnósticos;
  - `comment`, `actualCause` y `correctedRecommendation`.
- La proyección del diagnóstico por incidente no los incluye.
- El dashboard descarta `reviewer`, pero muestra la causa y el comentario a usuarios VIEW.
- Ninguna prueba cubre una lectura VIEW con revisiones existentes.

**5. Propuesta para acciones referenciales.**

- `domain.yml` tendría un atributo opcional `on_delete` (`restrict`, como hoy, o `cascade`).
  - Solo en relaciones `fk` intra-schema; nunca en `logical_ref`, que no tiene FK física.
- El validador rechazaría cualquier otro valor o uso.
- Los generadores lo emitirían:
  - `to_sql`: `ON DELETE CASCADE`;
  - `to_dbml`: `[delete: cascade]`;
  - el diccionario de datos.
- El registro congelado de referencias y una prueba en PostgreSQL lo fijarían.
- El primer uso sería `knowledge.knowledge_chunks.document_id` → `knowledge.knowledge_documents.id` (migración RAG `20261111_01`), registrado en un DD nuevo.
- Es un cambio acotado de validador, generadores y pruebas. Se implementa en un PR propio si se aprueba.

**6. Recomendación sobre `audit.audit_events`.**

Estado actual:

- Pipeline es el único servicio que la crea (V6, `IF NOT EXISTS`), la escribe (`SqlAuditLog`) y la lee.
- Los demás servicios guardan su trazabilidad en sus propios schemas, por ejemplo `diagnosis.human_reviews` e `ingestion.consent_records`.

Lo más coherente con ADR-011 y ADR-018, que hacen de `audit` una capacidad transversal sin `audit_service`:

- conservar `owner_container: shared` como propiedad lógica;
- registrar a Pipeline como custodio físico en el MVP: dueño de la migración y único escritor;
- que otro servicio que necesite esta tabla escriba mediante Pipeline y no con permisos directos.

Registrarlo exige un DD y, si se quiere en `domain.yml`, un campo de custodio que el validador hoy no admite.

**Figuras del Capstone v1.2.** Las figuras extraídas del documento coinciden byte a byte con exportaciones antiguas de `out/`:

| Figura | Archivo | Exportación |
|---|---|---|
| 1 | `c4_expo_2a.png` | 09/11 |
| 2 | `fisica_expo_01.png` | 08/11 |
| 3 | `fisica_expo_02.png` | 06/11 |
| 4 | `fisica_expo_03.png` | 06/11 |
| 6 | `logica_expo_02.png` | 04/11 |
| 7 | render de `c4_component_diagnostic.svg` | — |

Por eso las Figuras 1 y 7 repiten huella. Al ancho de inserción del documento (15,8 cm y 23,6 cm en la Figura 1), los textos se imprimen entre 3,3 y 5,6 pt; solo los títulos superan 7 pt.

Las variantes de `out/doc/` se comprueban para que ningún texto baje de 8 pt en A4. La [guía de figuras](../../out/doc/guia_figuras.md) indica la orientación y el tamaño de inserción de cada una. Reinsertarlas en el Capstone es tarea de sus autores.

**Hallazgo nuevo.** pipesor-iac crea la clave `pipesor-rag-signing`, le da a RAG el rol Crypto User y le pasa `PIPESOR_SIGNING_KEY_ID`, pero RAG no firma tokens: solo valida JWKS. Además, `docs/key-vault-integration.md` de pipesor-iac contradice el módulo `workloads` en:

- tipo de identidad;
- credencial;
- rol Secrets Officer;
- referencias de Key Vault.

Se reporta aquí y no se corrige: pipesor-iac está fuera de este repositorio.

### Límites de esta auditoría

- No se compilaron los servicios ni se levantó el stack local.
  - El stack en marcha se arrancó desde checkouts locales, y Pipeline estaba en `local/adr-028`.
  - Log/Event y Correlation no tienen springdoc, y los servicios Python no sirven `/openapi.json`.
  - Por eso la comparación de APIs se basa en el código de origin/main.
- La comparación de base de datos es estructural sobre tablas vacías. Flyway se emuló con psql; Alembic se tradujo a mano.
- No se ejecutaron operaciones en Azure ni en Terraform, ni pruebas de los servicios. No se verificó despliegue.
- `make test-postgres` conserva el fallo conocido `test_open_vector_and_review_correction` (3 frente a 1536 dimensiones), que también falla en main.
- `pipesor-landing` quedó fuera del alcance.

## Baseline verificable

El checkout de docs comenzó limpio en `main@c0871ac9a62bad62b8c679255fe0a4b9c6574d2e`.
Se obtuvo `origin/main` y el fast-forward no requirió cambios: ya coincidían.
La reconciliación parte de esa revisión en una rama corta `fix/` hacia `main`,
siguiendo la [política de contribución][contribution]. Las ramas locales previas
`work` y `fix/stage4-validation-reproducibility` se preservaron. No se tomó su
contenido como evidencia adicional de lo integrado en main.

| Repositorio | Revisión exacta consultada | Estado observado |
|---|---|---|
| [pipesor-docs](https://github.com/pipesor-org/pipesor-docs/tree/c0871ac9a62bad62b8c679255fe0a4b9c6574d2e) | `c0871ac9a62bad62b8c679255fe0a4b9c6574d2e` | Modelos/ADRs/herramientas documentales |
| [pipesor-iac](https://github.com/pipesor-org/pipesor-iac/tree/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d) | `6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d` | Fundaciones Terraform opt-in y preparación de despliegue |
| [pipesor-frontend](https://github.com/pipesor-org/pipesor-frontend/tree/3c0ccd31d66d9b71fc58453b513faaa5ffa56def) | `3c0ccd31d66d9b71fc58453b513faaa5ffa56def` | React con fixtures; CI produce dist, sin integración backend |
| [pipesor-ingestion-normalization-service](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/tree/2ec47eec58fb4d67ca4c40911ebd7def95162b5c) | `2ec47eec58fb4d67ca4c40911ebd7def95162b5c` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-pipeline-service](https://github.com/pipesor-org/pipesor-pipeline-service/tree/844d27303022c39bea5e14d0e7f42046c8638421) | `844d27303022c39bea5e14d0e7f42046c8638421` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-log-event-service](https://github.com/pipesor-org/pipesor-log-event-service/tree/8cdf18496c737c6fb636ccc4e45c6ec036b0e865) | `8cdf18496c737c6fb636ccc4e45c6ec036b0e865` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-evidence-correlation-engine](https://github.com/pipesor-org/pipesor-evidence-correlation-engine/tree/47f258fef692d5aac23268ed79c12b50a73050e6) | `47f258fef692d5aac23268ed79c12b50a73050e6` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-recommendation-service](https://github.com/pipesor-org/pipesor-recommendation-service/tree/3f947cca216f38e4fecae3a4c80993385d46b397) | `3f947cca216f38e4fecae3a4c80993385d46b397` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-nlp-log-processor](https://github.com/pipesor-org/pipesor-nlp-log-processor/tree/4b19e69a7a95e768fb337de9ba6c344a6c59d465) | `4b19e69a7a95e768fb337de9ba6c344a6c59d465` | Guías y contrato de readiness; sin aplicación ejecutable |
| [pipesor-rag-retrieval](https://github.com/pipesor-org/pipesor-rag-retrieval/tree/0d5c17fac2c538bbe4b61104b4718705118af9c8) | `0d5c17fac2c538bbe4b61104b4718705118af9c8` | Guías y contrato de readiness; sin aplicación ejecutable |
| [.github](https://github.com/pipesor-org/.github/tree/36691787bb9d0c9fd6b78c76bfe82adffa0c1c87) | `36691787bb9d0c9fd6b78c76bfe82adffa0c1c87` | Política de contribución y template de PR |
| [pipesor-landing](https://github.com/pipesor-org/pipesor-landing/tree/7f9c74c7b5b392c594971591c781fad3afb32eaa) | `7f9c74c7b5b392c594971591c781fad3afb32eaa` | Landing Astro/React y configuración estática Workers; publicación requiere autorización. |
| [pipesor-workspace](https://github.com/pipesor-org/pipesor-workspace/tree/61eb94c0f02beb63665c785dba2fa4c721e2e699) | `61eb94c0f02beb63665c785dba2fa4c721e2e699` | Inventario de repositorios y utilidad local de sincronización segura; no release integrado ni despliegue. |
| `pipesor-landing-page` | Nombre solicitado no accesible | Git/API devolvieron not found/404; el inventario y la organización identifican la landing accesible como `pipesor-landing`. No inferir una migración o cambio de nombre histórico. |

La API de la organización y el [inventario de workspace][workspace-inventory]
permitieron identificar `pipesor-landing`; el 404 inicial no se trató como prueba
de inexistencia de la landing. Las copias accesibles usaban `main`. IaC solo anunció `main` al consultar sus ramas;
docs anunció además `fix/design-open-questions@397ee43bfe63a4ecb0ddc53f9c40341d16153694`
y `fix/repository-reference@454f0b9b8a7b92cb3dfccdaf67a449081d14f455`.
No se presupone contenido adicional integrado por la existencia de esas ramas.
No hay acceso a los worktrees WSL ni a cambios no publicados de otros operadores.
Las revisiones son un corte de lectura, no una garantía de que los remotos no
cambien después. Los enlaces externos de este informe fijan ese corte.

### Evidencia local no recuperable

Los siete servicios y [architecture-consumption de IaC][consumption] identifican
un suplemento fuera de `pipesor-docs@c0871ac`:

- `docs/architecture/pending-decisions.md`, modificado localmente, SHA-256
  `3e153d9a467cef72caa937fc2b2e2e7642ebcbee1f98465edc8951df8c799c42`.
- `docs/architecture/stage-5-result.md`, entonces sin seguimiento, SHA-256
  `1a1228c6869cbe602ff78c0ba0c87466db4b6c7cc9d3500f6b6c3e9e7d86d6a0`.

En el checkout sincronizado usado para este corte ese contenido no estaba disponible. Los hashes y las
menciones externas no recuperan sus bytes ni prueban aprobación. PD-033–036 se
usan en los servicios para eventos, APIs, entrega backend–IaC y acceso de workflows;
este informe registra esas referencias externas sin reconstruir las entradas ni
atribuirlas al registro de 32 PD integrado. La autoridad Jhon Galvez/Ramiro Guzman
es reportada por esos documentos; no se verificó CODEOWNERS ni la regla de una o
ambas aprobaciones. Recuperar una revisión revisada y publicable sigue pendiente.

### Recuperación posterior en la rama local de etapa 5

Al reconciliar esta rama con `origin/main@f02f7cf8b902be80a07e4653d8389fef50e815d0`, se comprobaron los dos archivos locales antes de integrarlos: sus SHA-256 coincidían exactamente con los citados arriba. El [registro ampliado](pending-decisions.md#ampliación-de-etapa-5-contratos-de-consumo) y el [informe de etapa 5](stage-5-result.md) quedan recuperados en el árbol local; su publicación/revisión y la aprobación de contratos concretos siguen siendo asuntos diferentes. Las modificaciones de reconciliación posteriores cambian sus hashes; los hashes anteriores identifican el suplemento previo a esta integración, preservado en la copia de seguridad local.

La autoridad de aprobación de contratos Jhon Galvez/Ramiro Guzman está respaldada por la indicación del usuario en esta conversación, transcrita en el registro ampliado. No se ha establecido si deben aprobar ambos ni se ha verificado una configuración equivalente en GitHub. XR-004 se actualiza en ese sentido: recuperar bytes deja de ser un bloqueo local; disponer de una revisión publicable y aprobaciones concretas sigue pendiente. Las filas XR siguientes conservan el corte remoto original, con esta actualización de disponibilidad para XR-004.

PD-033/034/035/036 corresponden respectivamente a eventos, APIs, entrega backend–IaC y acceso de workflows. Complementan XR-007/004; PD-034/036 deben leerse junto con la discrepancia de perímetro XR-001. La recuperación no aplica automáticamente las decisiones externas a los modelos/ADRs ni resuelve XR-001/002/003.

## Estados que no deben confundirse

| Estado | Evidencia necesaria y límite |
|---|---|
| Decisión registrada como aprobada | ADR Accepted o baseline que registra aceptación del owner; conservar materia, alcance y limitaciones. No equivale a aprobación de cada plan. |
| Propuesta | Candidato/ADR propuesto, clases propuestas, endpoints o parámetros pendientes. No pasa a default aprobado. |
| Código implementado | Archivos en el SHA consultado; no implica ejecución, configuración real ni deployabilidad. |
| Infraestructura desplegada | Requiere evidencia de operación/recursos para el entorno exacto. No se inspeccionó Azure, state, planes ni facturación. IaC declara que no ha desplegado recursos/backends mediante este flujo. |
| Requisito o evidencia sin resolver | Contrato, fuente o verificación faltante; bloquea el incremento afectado, no todo trabajo independiente. |

## Cambios integrados y límites actuales

### Infraestructura

IaC supera la antigua fundación limitada a resource groups. Los cuatro callers
`environments/{dev,qa,preprod,prod}` mantienen roots/estados separados y componen
los módulos opcionales siguientes. Objetos null y flags desactivados mantienen el
comportamiento por defecto sin esas fundaciones; declararlos no provisiona nada.

| Implementación inspeccionada | Configuración de código/decisión local | Lo que sigue ausente o sin verificar |
|---|---|---|
| `modules/resource-group` | Un grupo inicial por root; naming AVM | No constituye una landing zone ni evidencia de recursos existentes. |
| `modules/container-platform` | VNet/subnet delegada, ambiente ACA externo, un perfil Consumption, sin redundancia zonal, workspace y diagnostic setting | Sin aplicaciones, imágenes, ingress por servicio, Dedicated profiles, identidades/grants ni escalado de aplicaciones. |
| `modules/service-bus` | Namespace Standard público, Entra-only, TLS 1.2 | Sin topics/subscriptions, filtros, permisos runtime ni contratos; la [topología candidata][messaging] está explícitamente diferida. |
| `modules/postgresql` | PG17/B2s/32 GiB, red privada con subnet/DNS, Entra-only, siete días de backups locales, sin HA/replicas; parámetro `azure.extensions=vector` | Configurar el parámetro no ejecuta `CREATE EXTENSION`; sin schemas/tablas/migraciones/grants. Conectividad privada del operador y drivers/token refresh pendientes. |
| `modules/application-insights` | Componente compartido ligado al workspace, Entra-only, endpoints públicos | Sin instrumentación, identidades de ingesta, alertas ni retención efectiva de cada tabla verificada. Connection string no concede acceso. |
| `modules/foundry` | Cuenta AIServices S0/proyecto, identidades propias, acceso público Entra-only | Sin modelos, deployments, agentes, AI Search ni grants para ACA. La cuenta vacía no produce inferencia. |
| `modules/static-web-app` | SWA Free público, sin preview ni enlace de repositorio, hostname predeterminado | Sin contenido, autenticación, dominios, API links ni workflow de despliegue. Free no acredita seguridad o SLA de producción. |
| `modules/state-store`, `bootstrap/*` | Stores de state separados; nuevo `bootstrap/admin` para subscription controls | No se confundirá con Blob de evidencia. Sin bootstrap aplicado, acceso/leases/restauración verificados ni migración de state. |
| `subscription-controls` | Root/state independiente para un presupuesto mensual 300, alertas Actual 50/80/100 y Forecast 100, email-only | No corta gasto. Fechas, destinatarios, oferta/moneda/scope requieren revalidación; no se activó el presupuesto. |

Fuentes: [baseline][baseline], [callers de entorno][environments], [módulos][modules],
[state bootstrap][state], [subscription controls][budget]. Terraform 1.17.1,
AzAPI 2.9.0 y locks/versiones de módulos son dependencias de IaC; no fijan versiones
Java/Python de aplicaciones. [IaC ADR 002][iac-adr2] de composición sigue **propuesto**; la
extracción de red/workspace se difiere para preservar direcciones y lifecycle.

El baseline selecciona **GHCR**, sin ACR para el MVP. No hay imágenes publicadas
ni private-pull configurado en estas fundaciones; identidad, material de acceso,
custodia y rotación siguen pendientes. Entra-only en los recursos compartidos no
resuelve por sí solo GitHub App, private-pull ni autenticación entre servicios.
No se infiere Key Vault ni otro almacén de secretos (PD-027), ni se dan a las
identidades de cuenta/proyecto Foundry los permisos de los callers ACA.

### Servicios e interfaces

Los siete repositorios siguen siendo scaffolds documentales, sin código de
aplicación, Dockerfiles, manifests de build ni imágenes. Su actualización más
reciente enlaza guías actuales sin convertir readiness en contrato aprobado.
El primer consumo histórico de `c0871ac` y el overlay se conservan como procedencia;
los enlaces móviles a `main` no identifican una revisión nueva de contrato.

| Servicio / runtime documentado | Relaciones y ownership canónicos conservados | Readiness pendiente |
|---|---|---|
| Ingesta / Java–Spring Boot | GitHub/observabilidad → protección → broker; GitHub read-only; sin tablas propias | Webhook/auth, secretos, eventos, imágenes/probes y configuración. |
| Pipeline / Java–Spring Boot | Suscripción broker y queries; posee `ops` | Topología, acceso y contratos runtime; grants de pipeline continúan inferred/ia_only. |
| Log/Event / Java–Spring Boot | Suscripción y consultas; posee `evidence_items` | La relación canónica con Blob contradice su exclusión del MVP en IaC (XR-002). |
| Correlación / Java–Spring Boot | NLP → correlación → diagnóstico; posee `correlated_contexts` | Contrato REST, referencias lógicas y llegada independiente de datos. |
| Diagnóstico / Java–Spring Boot | Orquesta RAG/LLM; posee `diagnosis`, revisión humana interna | El contrato aún describe APIM (XR-001); contexto/read model y workflow access siguen pendientes. |
| NLP / Python–FastAPI | Suscripción → Drain3 → correlación; sin tablas propias | Activación, estado del parser y acceso operativo de embeddings sin relación explícita adicional. |
| RAG / Python–FastAPI | Diagnóstico → recuperación pgvector; posee `knowledge` | ADR-021 fija embeddings/dimensión/acceso lógico; valores Azure, grants efectivos y corpus real siguen pendientes. |

Fuentes: [contrato de ingesta][ingestion], [Pipeline][pipeline], [Log/Event][log],
[Correlación][correlation], [Diagnóstico][recommendation], [NLP][nlp], [RAG][rag].
La configuración real de puertos, probes, CPU/memoria, identidades, migraciones y
escalado no se deduce de defaults de frameworks. Auditoría funcional sigue siendo
transversal en PostgreSQL; no se crea audit_service. Los cuatro componentes de
ADR-017 permanecen internos a recommendation_service. No se reintroducen detector,
LogBERT, reporting_service, notificaciones o APIs directas de scanners.

### Frontend, landing y entrega

[Frontend][frontend] implementa vistas React/TypeScript sobre fixtures Zod. No
implementa auth/authz, integración backend ni persistencia de operaciones. Su
[workflow Quality][frontend-ci] valida hooks, tipos, lint y build; solo push a main
sube `dist/` como artifact `frontend-<SHA>` con 90 días de retención. No hay deploy
Azure/SWA ni promoción implementados. Su retención de artifacts CI no sustituye
la política de un día para planes cifrados de IaC.

IaC reporta una landing ya alojada en Cloudflare Workers, pero no la verificó.
El repositorio real [pipesor-landing][landing] contiene Astro/React bilingüe,
`wrangler.jsonc` para servir `dist/`, configuración SEO y formulario early-access
desactivado; las capturas/métricas son ilustrativas. Su README advierte que la
configuración no confirma sitio productivo. El [CI Quality de landing][landing-ci]
hace checks/tests/build y `wrangler deploy --dry-run`, no publicación. La
[guía de deployment][landing-deploy] documenta Workers Builds separado (main para
producción, otras ramas para previews); ni sus settings efectivos, ni runs remotos,
ni DNS/TLS/publicación fueron inspeccionados. No se certifica sitio live.

La licencia MIT observada aplica al código de landing con exclusiones de marca,
capturas/arte y materiales ajenos. No se propaga a otros repositorios: la política
organizacional mantiene licensing por repositorio y no permite presumirlo.

La
[reconciliación de dominios][domains] mantiene Workers, SWA y ACA como capacidades
distintas; dominios/DNS/TLS, routing y CORS no quedan implementados al elegir SWA
Free. Un CNAME no distribuye paths entre servicios. `VITE_*` es público y se
integra al build; runtime config/promoción del mismo artifact sigue pendiente.

### Workspace y seguridad de sincronización

El [inventario][workspace-inventory] confirma repositorios hermanos y `services/`;
no es un monorepo ni fija una release compatible. Su herramienta distingue status
local de sync preview (que obtiene/prunea refs) y sync apply (que puede cambiar
branch, fast-forward y eliminar ramas con evidencia de squash integrado). No se
ejecutó sobre vecinos en esta tarea: se preservó la restricción read-only mediante
copias temporales. El workspace no se autosincroniza ni convierte sus tests de Git
en pruebas de integración de servicios. Sus procedimientos no autorizan reset,
limpieza de trabajo local ni modificación de repositorios vecinos aquí.

### Identidad, estado, recuperación y costes

[IaC ADR 004][iac-adr4] registra aceptación **para preparación local** de:

- Solo dev en la suscripción temporal Azure for Students de Ramiro/tenant UPC;
  qa/preprod/prod conservan raíces aisladas pero no se provisionan en el MVP.
- No desplegar ni bootstrap ni controles hasta implementación, integración local
  y validación de servicios, más autorización explícita posterior de target/acción.
- Ramiro autoriza acceso y límites iniciales; Jhon opera y autoriza planes dev
  concretos. Entra/RBAC/OIDC y acceso real no están establecidos por el ADR.
- Stores workload/admin separados, LRS, versionado y soft deletion 30 días;
  state bootstrap en custodia local cifrada fuera de Git, copias cifradas en
  OneDrive Personal y almacenamiento externo independiente. Primario Jhon,
  respaldo Ramiro; claves, rutas, recuperación y restore drill pendientes.
- Backups cifrados de state 90 días; planes cifrados un día; objetivo de recovery
  de state 24–48 h, no probado. Versionado no implica expiración a los 30 días.
- Actions/OIDC como destino futuro sobre VM Debian VirtualBox de Jhon propuesta
  (2 vCPU/4 GiB/20 GiB), efímera por job y descartable. Capacidad, aislamiento,
  egress, custodia age y activación no verificados. No modificar aquí WSL/VM.

El [scaffold][scaffold] está fuera de `.github/workflows`, con sufijo `.example`,
job desactivado y parada fail-closed. No concede `id-token: write` ni ejecuta
plan/apply/Azure/state. El [CI Terraform activo][iac-ci] solo hace fmt,
init backend-disabled, validate y pruebas mocked/plan-only, sin login cloud.
No se ejecutó ese CI ni sus pruebas Terraform durante esta reconciliación.

ADR 004 refina ADR 001: aprobaciones dev procedimentales aceptadas para el MVP,
no un gate independiente impuesto por GitHub Free/private. No extender esta
excepción a prod; permanece el target secuencial con controles independientes para
entornos futuros. OIDC autentica un job, no prueba aprobación humana. La política
organizacional conserva trunk-based e identidad inmutable de artifacts; no se
promueven planes Terraform entre estados ni se infiere activación automática.

La [proyección de coste][cost] es un cálculo fechado PAYG/USD/East US ilustrativo,
no factura ni cotización revalidada para Students. Estima un subtotal parcial de
~89 USD/mes para un stack de fundaciones habilitadas, omitiendo aplicaciones,
AI/tokens, uso real de logs, state/runner y otros cargos. El componente LB/IP es
condicional a recursos/reglas facturables; no describir Consumption como coste
cero de toda la plataforma. Defaults opt-out de las fundaciones tampoco prueban
coste cero en la suscripción real. ADR 004 sustituye la premisa de suscripción
propia/dedicada/USD: hay que revalidar oferta, moneda, región, cuotas y forecast
completo, manteniendo el presupuesto nominal y sus umbrales. Alertas y caps de
telemetría no son límites duros de gasto. Cambiar un objeto opt-in a null propone
eliminación; no es pause ni autoriza destrucción de datos.

No confundir recuperación de state, siete días de backups PostgreSQL, retención
CI/planes o logs técnicos con los 365 días de logs/diagnósticos/evidencias de
ADR-013. El mecanismo de retención de aplicación sigue pendiente (PD-030).

## Discrepancias y dependencias que quedan abiertas

XR-* son localizadores de esta reconciliación, no nuevos ADR ni IDs PD/DQ.
Registrar una decisión externa aceptada no la convierte en propuesta, pero tampoco
modifica automáticamente su reflejo canónico ni autoriza despliegues.

| ID | Evidencia y contradicción/límite | Acción independiente y gate pendiente |
|---|---|---|
| XR-001 — Perímetro | [IaC ADR 003][iac-adr3] registra aceptación del owner para ACA native ingress sin APIM/gateway/WAF; docs ADR-003/006/008/016, relaciones y diagramas siguen APIM. Contratos de servicios aún remiten a APIM. | Registrar ambas fuentes y la aceptación limitada al MVP. Requiere reconciliación autorizada model-first y contratos/exposición/auth por servicio; no editar diagramas para ocultarlo ni asumir cumplimiento corporativo/WAF equivalente. |
| XR-002 — Evidencia/Blob | [Baseline][baseline] registra exclusión de Blob **de workload** del MVP el 05/11; modelo/domain DD-006 y contrato Log/Event conservan referencias a objetos. | Reconciliar retrieval/retención, fuente GitHub y campos/contratos antes de implementar el tramo afectado. No restaurar Blob por inferencia ni eliminar historia/modelo. Blob de state sigue en scope. |
| XR-003 — AI | [Foundry][baseline] registra aceptación de cuenta/proyecto Entra-only, en vez del candidato de cuenta OpenAI independiente; ADR-021 añade el acceso RAG explícito y su contrato v0.1. | Validar endpoint/deployment/región/cuota y aplicar grants por separado. NLP/modelo diagnóstico conservan sus pendientes; no autoriza Search/agentes/nuevos servicios. |
| XR-004 — Fuente y entrega | PD-033–036/stage-5 solo constan como overlay reportado; todos los deployment-contracts son readiness no aprobado. | Obtener revisión reproducible/aceptada y regla de aprobaciones; luego imágenes, probes/config/access, migraciones, delivery y contratos de eventos/APIs. No reconstruir el overlay ni clausurar preguntas YAML. |
| XR-005 — Target/coste/gates | ADR 004 fija dev temporal Students, mientras textos previos de coste/subscription-controls/prioridades conservan premisas dedicadas USD o gates anteriores. La corrección posterior está explícita en ADR 004/README. | Usar ADR 004 para su alcance de preparación sin inferir upgrade/créditos/moneda/acceso. Registrar discrepancia residual en fuentes vecinas, sin editarlas. Revalidar forecast y autorización antes de cualquier Azure write. |
| XR-006 — Dominios/frontend | SWA Free ya aceptado/implementado como hosting-only; assessment de dominios conserva pasajes previos de selección de tier. La landing accesible es `pipesor-landing`, con código y dry-run CI; Workers live solo reportado y no verificado. | Distinguir cronología del assessment y decisión posterior. Resolver el nombre en los consumidores y recuperar evidencia de publicación; resolver routing, Entra/CORS, runtime config/delivery, DNS/TLS antes de bindings. No afirmar endpoint operativo. |
| XR-007 — Mensajería/datos | Namespace implementado, entidades diferidas; fan-out candidato puede entregar NLP antes de datos de Pipeline/Log/Event. SQL/grants/extension no ejecutados. | PD-015/031 y contratos referidos PD-033: nombres, schemas, filtros/TTL/settlement, idempotencia, DLQ, permisos y consistencia temporal. Preservar ownership y referencias lógicas. |
| XR-008 — Representaciones/validación | Diagramas/SQL representan el baseline documental, no recursos desplegados; perfil gráfico versionado WSL2 difiere del cloud disponible. AGENTS ya preserva las proyecciones C4 existentes. | Mantener SVG/modelos intactos en esta tarea documental; validar enlaces/coherencia y registrar reproducibilidad real sin normalizar diferencias ni declarar despliegue. |

Las preguntas DQ/DCQ y CF-001 siguen en sus fuentes; aceptación de fundaciones no
resuelve severidad, confidence, corpus/dimensión, RBAC, read model ni política de
riesgo. Se conserva PD-001: intervalo técnico DD-015 y KPI comparativo Charter
con objetivos/límites distintos, con protocolo comparativo aún pendiente.
La aprobación independiente de fuentes y la vigencia de A-011 mantienen los
límites del registro original. No se relabelan todos los ADR históricos como
obsoletos ni se presume que modelos propuestos sean implementación backend.

## Verificación de esta reconciliación

La revisión documental contrasta fuentes, enlaces/rutas, revisiones y diff.
Los resultados de checks actuales se consignan en el PR; no se reutilizan los
resultados históricos de tests como prueba del corte actual. `make validate` y
`make validate_design` son checks de consistencia de los modelos; no prueban
alineamiento con decisiones vecinas todavía no incorporadas. La comprobación
`make verify-artifacts` genera en copias temporales y compara bytes estrictos;
no repara los derivados del checkout. Las diferencias de perfil deben reportarse,
no eliminarse mediante regeneración ajena al alcance.

No se ejecutaron Terraform init/plan/apply/tests, operaciones de state, cloud ni
cuentas, pruebas de aplicaciones vecinas, despliegue, DNS ni publicación de sitios.
Ningún estado desplegado o coste real queda certificado por este informe.

[consumption]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/architecture-consumption.md
[baseline]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/mvp-resource-baseline.md
[environments]: https://github.com/pipesor-org/pipesor-iac/tree/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/environments
[modules]: https://github.com/pipesor-org/pipesor-iac/tree/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/modules
[state]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/state-bootstrap.md
[budget]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/subscription-controls.md
[messaging]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/messaging-topology-assessment.md
[domains]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/domain-hosting-reconciliation.md
[iac-adr3]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/adr-003-mvp-native-ingress.md
[iac-adr4]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/adr-004-mvp-state-and-deployment.md
[iac-adr2]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/adr-002-terraform-module-composition.md
[scaffold]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/.github/workflow-templates/terraform-dev.yml.example
[iac-ci]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/.github/workflows/terraform.yml
[cost]: https://github.com/pipesor-org/pipesor-iac/blob/6666fb8cc3bc2fcce370c2cdc93c3348bdc64e8d/docs/mvp-cost-projection.md
[ingestion]: https://github.com/pipesor-org/pipesor-ingestion-normalization-service/blob/2ec47eec58fb4d67ca4c40911ebd7def95162b5c/docs/deployment-contract.md
[pipeline]: https://github.com/pipesor-org/pipesor-pipeline-service/blob/844d27303022c39bea5e14d0e7f42046c8638421/docs/deployment-contract.md
[log]: https://github.com/pipesor-org/pipesor-log-event-service/blob/8cdf18496c737c6fb636ccc4e45c6ec036b0e865/docs/deployment-contract.md
[correlation]: https://github.com/pipesor-org/pipesor-evidence-correlation-engine/blob/47f258fef692d5aac23268ed79c12b50a73050e6/docs/deployment-contract.md
[recommendation]: https://github.com/pipesor-org/pipesor-recommendation-service/blob/3f947cca216f38e4fecae3a4c80993385d46b397/docs/deployment-contract.md
[nlp]: https://github.com/pipesor-org/pipesor-nlp-log-processor/blob/4b19e69a7a95e768fb337de9ba6c344a6c59d465/docs/deployment-contract.md
[rag]: https://github.com/pipesor-org/pipesor-rag-retrieval/blob/0d5c17fac2c538bbe4b61104b4718705118af9c8/docs/deployment-contract.md
[frontend]: https://github.com/pipesor-org/pipesor-frontend/blob/3c0ccd31d66d9b71fc58453b513faaa5ffa56def/README.md
[frontend-ci]: https://github.com/pipesor-org/pipesor-frontend/blob/3c0ccd31d66d9b71fc58453b513faaa5ffa56def/.github/workflows/quality.yml
[contribution]: https://github.com/pipesor-org/.github/blob/36691787bb9d0c9fd6b78c76bfe82adffa0c1c87/CONTRIBUTING.md

[workspace-inventory]: https://github.com/pipesor-org/pipesor-workspace/blob/61eb94c0f02beb63665c785dba2fa4c721e2e699/mani.yaml
[landing]: https://github.com/pipesor-org/pipesor-landing/blob/7f9c74c7b5b392c594971591c781fad3afb32eaa/README.md
[landing-ci]: https://github.com/pipesor-org/pipesor-landing/blob/7f9c74c7b5b392c594971591c781fad3afb32eaa/.github/workflows/quality.yml
[landing-deploy]: https://github.com/pipesor-org/pipesor-landing/blob/7f9c74c7b5b392c594971591c781fad3afb32eaa/docs/deployment.md
