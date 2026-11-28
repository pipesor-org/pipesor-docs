# Auditoría de diagramas para el Capstone y la Memoria — 27/11/2026

Informe documental. Registra la petición del responsable, la auditoría de solo lectura (fase 1), las
decisiones que aprobó para la fase 2 y lo que cambió en los modelos y generadores. No es un ADR, no
cierra PD ni `open_questions` y no acredita comportamiento en runtime.

## Autorización y alcance

Petición (asesores y jurados técnicos): C4 de contexto, contenedores y componentes; UML de clases por
bounded context desde `model/design.yml`; modelo de datos desde `model/domain.yml`; secuencias de
(a) fallo en GitHub Actions → captura → correlación → RAG → diagnóstico → revisión humana y (b) login
GitHub OAuth/PKCE vía Ingestion; y diagrama de despliegue con la estrategia de ramas. Con caminos de
error, asincronía e idempotencia, marcando lo propuesto frente a lo implementado y con variantes A4.

El responsable aprobó el 27/11/2026 las siete decisiones propuestas al cerrar la fase 1:

| Nº | Decisión aprobada | Dónde queda |
|---|---|---|
| 1 | Modelos de presentación nuevos para secuencias y despliegue, con generador, validador y pruebas; cada mensaje o nodo cita un `rel_*`/elemento existente o evidencia `repo:ruta:línea`; lo implementado no modelado se marca sin añadirse a `architecture.yml` | `model/sequence_presentation.yml`, `model/deployment_presentation.yml`, `tools/generators/sequences.py`, `tools/generators/deployment.py` |
| 2 | Estado de implementación en un overlay aparte que referencia IDs existentes, sin tocar hechos de arquitectura; alimenta la trazabilidad | `model/implementation_status.yml`, `tools/generators/implementation_status.py`, `tools/generators/evidence.py`, `out/trazabilidad.md` |
| 3 | C4 nivel 3 de Ingestion con componentes `inferred` y fuentes en el código; Recommendation conserva los cuatro componentes de ADR-017 con marcas de divergencia, sin cerrar la pregunta 13 | `model/architecture.yml` (7 componentes, 22 relaciones derivadas o internas, vista `c4_component_ingestion`) |
| 4 | Diagramas de agregados por bounded context con estado por clase y referencias al código; marcar en CD-1..3 las clases que no existen | `model/design.yml`, `model/design_decisions.md`, `tools/validate_design.py`, `tools/generators/classes.py` |
| 5 | Key Vault y Dashboard → Ingestion en una vista de contenedores; corregir las etiquetas que mencionaban artifacts y tablas inexistentes y los verbos «Routes»; las relaciones sin implementación se quedan y se marcan | Vista 2B (`c4_container_consumption`) y `c4_expo_2b`; seis etiquetas de `architecture.yml` y tres de presentación |
| 6 | Variantes A4 del contexto, las clases, el ER (por contexto), las secuencias y el despliegue; lenguaje y framework como tecnología C4; descripciones legibles desde un mapa de presentación | `model/c4_presentation.yml` (tecnología y descripciones). Las variantes A4 de `out/doc/` se sustituyeron el mismo día por las figuras documentales (sección siguiente) |
| 7 | Lectura de solo lectura en Azure para acreditar «desplegado»; sobre ramas, dibujar solo lo definido y marcar el resto como TBD | `deployment_observation` del overlay; figura `deploy_environments_delivery` |

No se cambian `status`, `source` ni invariantes existentes. `deployment.mvp_preparation.deployment_authorized`
sigue en `false`: lo exige `tools/architecture_policy.py` como regla de ADR-019, aunque dev está desplegado
(divergencia registrada, sin resolver). La comprobación de INV-001 trata ahora los componentes de Ingestion
como Ingestion (proyección componente → contenedor), sin relajar el invariante.

## Revisiones consultadas

docs `294fcd7` (base de la rama), Ingestion `a41188a`, Pipeline `f6b64c3`, Log/Event `5f3475f`, NLP `d70a81a`,
Correlation `be231a0`, Recommendation `c3ce559`, RAG `312b520`, frontend `2806ae1`, pipesor-iac `318af56`,
pipesor-ci `43c70cd`, pipesor-demo `2ed10e1`, validation-scenarios `27f0bfb`, workspace `168d72d`. Son las
mismas revisiones de servicio que la auditoría del 24/11; lo desplegado en dev difiere de ellas solo en CI y
README (1 commit por repo).

## Estado final de cada diagrama

| Diagrama | Figura completa · figura para documentos (`out/figuras/`) | Fuente | Qué representa |
|---|---|---|---|
| C4 L1 contexto | `out/c4_context.svg` · `c4-contexto` | `architecture.yml` | Vista `draft` con estado de implementación por relación agregada |
| C4 L2 2A y 2B | `out/c4_container_*.svg`, `out/c4_expo_2a/2b` · `c4-contenedores-procesamiento` y `-consumo` | `architecture.yml`, `c4_container_presentation.yml` | 2B incluye ahora Ingestion y Key Vault; Dashboard → Log/Event y Observability → Ingestion se dibujan como «modeled, not implemented» |
| C4 L3 Recommendation | `out/c4_component_diagnostic.svg` · `componentes-diagnostico` | `architecture.yml` | Componentes de ADR-017; orquestación «implemented differently» (cola `diagnosis_jobs`), composer y API «partial» |
| C4 L3 Ingestion | `out/c4_component_ingestion.svg` · `componentes-ingesta` | `architecture.yml` | Componentes `inferred` del código, todos implementados |
| Clases | `out/CD-*.svg` · `clases-operacion`, `-ingesta`, `-correlacion` y `-diagnostico` | `design.yml` | CD-1..3 propuestos con marca por clase; diagramas de agregados implementados por bounded context |
| ER | `out/er.svg` · `datos-*` (5 figuras, una por esquema) | `domain.yml` + overlay | 33 de 36 tablas implementadas; `diagnoses` en parte; 3 tablas y 6 columnas solo modeladas |
| Secuencias | `out/seq_*.svg` · `secuencia-*` (4 figuras) | `sequence_presentation.yml` | Implementado y desplegado en dev, con divergencias marcadas |
| Despliegue | `out/deploy_*.svg` · `despliegue-dev` y `despliegue-entornos-ramas` | `deployment_presentation.yml` | dev desplegado (observado el 27/11); qa/preprod/prod, la promoción y sus gates previstos para TP2; ramas: lo definido (release inactivo, apply manual autorizado, historial de `images.json` como registro) y dos puntos por definir (aprobaciones de PR y CODEOWNERS, PD-035) |

La matriz de trazabilidad completa (cada elemento → ID de modelo, ADR/DD y `repo:ruta:línea`) está en
[`out/trazabilidad.md`](../../out/trazabilidad.md). Las guías de cada familia: [`out/figuras/README.md`](../../out/figuras/README.md),
`out/secuencias_guia.md`, `out/despliegue_guia.md` y `out/c4_expo_guia.md`.

## Figuras para documentos (segundo nivel) — 27/11/2026

Petición posterior del responsable: las variantes A4 de `out/doc/` partían figuras hasta en ocho partes y no
servían para Word. Se sustituyen por un segundo nivel de figuras con formato APA 7, generado desde un modelo de
presentación nuevo, `model/document_figures.yml`, con `tools/generators/figuras.py` (`make figuras`). El modelo
selecciona y rotula en español hechos ya modelados; no crea arquitectura ni cambia estados, ADR, DD, PD o
preguntas abiertas.

- Reglas que el generador comprueba antes de escribir: una figura por página y sin partes; como máximo
  15,9 × 19,0 cm en vertical (24,6 × 13,0 cm en apaisado solo para figuras exclusivas del Capstone); texto de
  9 pt o más al ancho de inserción; PNG a 300 ppp; nombres en kebab-case sin número de parte; cada PNG en el
  README de su carpeta; SVG intermedios en `build/figuras/` sin `repo:`, hashes, `rel_` ni «Generated».
  `tests/test_figuras.py` y `tools/verify_artifacts.py` repiten esas comprobaciones.
- Límites de contenido por tipo (palabras por relación, componentes, clases, atributos, columnas, líneas de
  vida, mensajes y fragmentos) y nota APA de hasta 60 palabras que explica solo los estados dibujados.
- Tres estados: implementado (continuo), parcial (ámbar discontinuo; agrupa `partial` y `divergent`) y
  propuesto (rojo punteado; agrupa `not_implemented`, `proposed` y `tbd`).
- Veinte figuras, por encima de la guía de 15–18: el responsable aprobó cuatro figuras de clases (una por
  bounded context con agregado implementado) y la división del C4 L2 en dos figuras.
- Se retiraron `out/doc/` (221 archivos: SVG, PNG y `guia_figuras.md`), `tools/generators/document_figures.py`,
  `tools/generators/er_print.py`, las opciones `--document(s)` de clases, secuencias y despliegue y los
  `print_parts` de `model/design.yml` y `model/c4_presentation.yml`. Las vistas completas de `out/*.svg`, las
  guías técnicas y la trazabilidad no cambian, salvo los enlaces que apuntaban a `out/doc/`.
- La sección de destino de cada figura es una propuesta «a confirmar por el equipo».

## Modelo de datos frente a migraciones

Método: PostgreSQL 17.12 con pgvector 0.8.7 desechable (versión mayor de Azure), script de base de la IaC
(`vector` y schema `evidence`), Flyway 12.4 real con la configuración de cada `application.yml` (33
migraciones de cinco servicios) y Alembic 1.20.1 real (tres revisiones de RAG); `pg_dump --schema-only` e
introspección de catálogo frente a `schema.sql` + `extras.sql` generados desde `domain.yml` 1.11.0.

Resultado: columnas, tipos, nulabilidad, PK, únicas (también parciales), CHECK, FK y triggers coinciden salvo:

| Divergencia | Registro |
|---|---|
| `diagnosis.recommendations`, `diagnosis_evidence_links` y `diagnosis_source_links` solo existen en el modelo | [DD-027](../../model/domain_decisions.md#DD-027), divergencia 2 · pregunta 2 |
| Seis columnas de `diagnosis.diagnoses` (`status`, `probable_cause`, `explanation`, `limitations`, `confidence`, `diagnosis_ready_at`), su CHECK y el enum `DiagnosisStatus` | DD-027, divergencia 1 · pregunta 1 |
| Trigger `diagnoses_append_only` y su función | DD-027, divergencia 3 · pregunta 3 |
| `human_reviews_comment_check` exige comentario en REJECTED | DD-027, divergencia 4, y [DD-029](../../model/domain_decisions.md#DD-029) |
| `ON DELETE CASCADE` en `knowledge_chunks.document_id` | DD-027, divergencia 5 · pregunta 5 |
| Enums del modelo frente a `text`/`varchar` con CHECK | DD-027, «no representado» |
| Seis FK diferibles en el modelo y no diferibles en las migraciones | DD-026, DD-027 y DD-028 |
| Secuencia `ops.incident_display_number_seq`, 14 DEFAULT y 17 índices no únicos | DD-026 y DD-027, «no representado» |

No apareció ninguna divergencia nueva. El overlay lleva la línea del `CREATE TABLE` de cada tabla.

## Hallazgos que no constaban en la reconciliación del 24/11 ni en `pending-decisions.md`

Se registran sin resolverlos; cada uno remite a su evidencia en el overlay o en las guías.

1. DD-026 dice que los intentos de login y de autorización usan UUID distintos; Ingestion usa el mismo id y la misma referencia `pkce:` en ambas tablas (`GitHubLoginHandler.java:90-94,122-125`).
2. El vínculo GitHub se activa antes de la transacción del consentimiento: si falla el registro no hay sesión, pero el vínculo queda activo (ADR-029, «no login without proof», se cumple en parte).
3. «Reconectar» reenvía `consent_version` sin mostrar la casilla (`GitHubConnectionStatus.tsx:39-40`); el código lo justifica porque la sesión ya aceptó los documentos.
4. El `state` OAuth se liga al intento y no al navegador (riesgo de login CSRF inferido, sin prueba).
5. El dashboard nunca envía REJECTED: su botón «Reject» envía CORRECTED con causa (`DiagnosisReview.tsx:125`).
6. `replay_window`/`replay_until` se escriben pero nunca se leen y no existe operación de replay (DD-021, ADR-023).
7. Los recibos de captura con fallos no terminales se reintentan sin límite, frente al bloqueo visible que pide DD-021.
8. NLP calcula la plantilla Drain3 y Correlation la descarta; el atributo `embedding_model` de NLP no tiene implementación.
9. Ningún servicio instrumenta Application Insights (ADR-002) y la IaC lo tiene desactivado en dev.
10. `deployment_authorized: false` frente a dev desplegado desde el 22/11 (guardado por la política de ADR-019).
11. RAG exige una `scope_revision` idéntica a la del corpus: si cambia, devuelve `no_match` sin aviso.
12. `out/diccionario_datos.md` estaba desfasado en `main` (faltaba DD-029); se regenera en esta rama.

## Preguntas abiertas y supuestos que afectan a cada diagrama

| Diagrama | Preguntas, PD y supuestos |
|---|---|
| C4 L1/L2 | Preguntas 12 (Dashboard → Log/Event, observabilidad) y 13 (orquestación); PD-015, PD-033, PD-034, PD-026; PD-036 abierta en documentos y resuelta en la práctica con OIDC |
| C4 L3 | Pregunta 13; `diagnosis_jobs` `inferred`; PD-009/DCQ-001, PD-010/DCQ-002, PD-011/DCQ-003, PD-004/DQ-002; componentes de Ingestion `inferred` |
| Clases | Pregunta 24 (paquetes, JPA frente a JDBC); DQ-002, DCQ-001..003; DA-004 y DA-005 suponen tablas y clases que no existen; A-007, A-008 |
| ER | Preguntas 1–3, 5, 6 y 7 (DQ-001, A-005, PD-003); tablas `inferred`: `execution_event_receipts`, `diagnosis_jobs`, `pipeline_access_grants` (`ia_only`) |
| Secuencia (a) | PD-033 (reentrega y mensajes agotados, sin lector de DLQ), PD-031, PD-034, PD-030, PD-037; horizontes de DD-021 sin aprobación registrada; preguntas 13 y 20; A-004 (`cancelled` no abre incidente) |
| Secuencia (b) | Pregunta 21 (sessionStorage, solapamiento de claves, `repository_owner_id`) y pregunta 14; PD-027, PD-030; ingestion#24 (límite de frecuencia y limpieza de custodia) |
| Despliegue | PD-035, PD-015, PD-017/PD-030, PD-021, PD-026; topología de qa/preprod/prod sin definir. Corrección del responsable (27/11/2026): los gates están definidos en IaC ADR 001 y previstos para TP2, los releases están definidos e inactivos mientras solo exista dev, no hay despliegue automático porque cada apply se autoriza (IaC ADR 004) y el historial de `images.json` es el registro de despliegues; siguen por definir las aprobaciones mínimas de PR con CODEOWNERS y el orden de entrega (PD-035) |

## Qué debe validar cada dueño de servicio y qué evidencia falta

Ninguna prueba recorre un flujo entre servicios con los pares reales, ninguna usa el broker real ni su
emulador y el frontend no tiene pruebas E2E. Las secuencias se apoyan en código, pruebas unitarias o de un
solo servicio (Testcontainers con pares simulados) y en la observación de dev del 27/11.

| Dueño | Debe validar | Evidencia que falta |
|---|---|---|
| Ingestion | Pasos 1–9 de la secuencia de captura, la secuencia de login y los siete componentes `inferred`; hallazgos 1–4, 6 y 7 | Prueba servlet → `JdbcCaptureAuthority` → ledger; GitHub real o grabado; tope de reintentos de recibos; logout HTTP con sesión, `consent_required` en el callback, fallo de Key Vault tras el handoff, rotación de claves y kid desconocido |
| Pipeline | Consumo del snapshot, receipts y cola de incidentes; entitlements y resumen de diagnóstico; severidad inicial (pregunta 7) | Prueba con broker; reproceso de eventos `IGNORED_PAUSED`; `IncidentOriginMissing` |
| Log/Event | Registro y comprobación de pertenencia; que no hay API de consulta (relación del dashboard no implementada) | Prueba con broker; carrera NOT_READY con Pipeline real |
| NLP | Consumo, Drain3 y envío a Correlation; pausa ante 401/403 hasta reiniciar; hallazgo 8 | Prueba de recuperación tras la pausa; prueba con broker |
| Correlation | Cadena síncrona hacia Pipeline, Log/Event y Recommendation; 4xx de Recommendation tratado como 503; bloqueo del grupo tras DLQ de NLP | Prueba de `HttpRecommendationDelivery` con `ReceiptStore` real; prueba del bloqueo tras DLQ |
| Recommendation | Cola `diagnosis_jobs`, RAG, LLM, outbox y revisión (pregunta 13); clases propuestas que no existen; comentario en REJECTED (DD-029); hallazgo 5 | Camino de chunks y fuentes integrado; fallos del LLM (timeout, filtro, 128 KiB); bucle del outbox con 404/401; lectura VIEW de reviews con revisiones; validación de `repository_owner_id` |
| RAG | Consulta pgvector y embeddings; identidad user-assigned frente a ADR-021 (pregunta 19); hallazgo 11 | Embeddings contra Azure; 401 y 422 explícitos |
| Frontend | Inicio de sesión, handoff, cola y revisión; sessionStorage (pregunta 21); hallazgos 3 y 5 | Pruebas de `session.ts`, `AuthCompletePage`, `DiagnosisReview` y E2E |
| IaC | Nodos y estados del diagrama de despliegue; App Insights desactivado; clave de firma de RAG sobreaprovisionada; hallazgos 9 y 10 | Pruebas del callback OAuth, `SESSION_JWKSURI` y `DASHBOARD_ORIGIN`; registro de despliegue; topología de qa/preprod/prod |

## Límites

- La evidencia se comprueba en estructura y, con `make evidence WORKSPACE=<dir>`, en existencia de archivo y línea a la revisión fijada; no verifica semántica.
- La observación de Azure fue de solo lectura y puntual (PostgreSQL detenido en ese momento).
- Las figuras no acreditan comportamiento en runtime ni sustituyen pruebas de integración.
