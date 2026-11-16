<!-- GENERATED — DO NOT EDIT. SSOT: model/domain.yml -->
# Diccionario de datos

Modelo: `1.3.0`. Una instancia PostgreSQL; 25 tablas.

Los tipos enum se materializan en el schema propietario de cada tabla.
FK significa constraint físico intra-schema; logical_ref significa ID sin FK física.

## Schema `ops`

Operación de workflows e incidentes.

Owners permitidos: pipeline_service.

### `ops.repositories`

Repositorio GitHub autorizado; entidad distinta del workflow monitorizado.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_CHARTER#Alcance-del-Proyecto, architecture.yml#github, DD-001.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_CHARTER#Alcance-del-Proyecto; architecture.yml#github; DD-001 | A-001 |
| github_repository_id | text | No | — | — | No | Sí | — | ID externo del repositorio GitHub. | SRC_CHARTER#Alcance-del-Proyecto; architecture.yml#github; DD-001 | A-003 |
| full_name | text | No | — | — | No | No | — | Nombre owner/repository para presentación. | SRC_CHARTER#Alcance-del-Proyecto; architecture.yml#github; DD-001 | — |
| default_branch | text | No | — | — | Sí | No | — | Rama por defecto suministrada por GitHub. | SRC_CHARTER#Alcance-del-Proyecto; architecture.yml#github; DD-001 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.pipelines`

Pipeline equivale directamente a un GitHub Actions workflow monitorizado.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_018, architecture.yml#pipeline_service, docs/research/arquitectura-informacion.md, DD-001.

Claves únicas compuestas: `(repository_id, github_workflow_id)`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | A-001 |
| repository_id | uuid | No | ops.repositories.id | — | No | Compuesto: (repository_id, github_workflow_id) | — | Repositorio del workflow. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | — |
| github_workflow_id | text | No | — | — | No | Compuesto: (repository_id, github_workflow_id) | — | ID externo del workflow, único dentro de su repositorio. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | A-003 |
| workflow_name | text | No | — | — | No | No | — | Nombre del workflow monitorizado. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | — |
| workflow_file | text | No | — | — | No | No | — | Ruta declarada del workflow. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | — |
| environment | text | No | — | — | Sí | No | — | Entorno operacional suministrado por configuración autorizada. | SRC_ADR_018; architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-001 | — |
| criticality | ops.PipelineCriticality | No | — | — | No | No | PipelineCriticality | Criticidad del pipeline; distinta de la severidad del incidente. | docs/research/arquitectura-informacion.md | — |
| monitoring_status | ops.MonitoringStatus | No | — | — | No | No | MonitoringStatus | Estado de monitorización. | docs/research/arquitectura-informacion.md | — |
| responsible_team_ref | text | No | — | — | Sí | No | — | Referencia externa al equipo responsable; sin tabla teams. | docs/research/arquitectura-informacion.md | — |
| responsible_team_name_snapshot | text | No | — | — | Sí | No | — | Nombre del equipo al registrar configuración. | docs/research/arquitectura-informacion.md | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.pipeline_executions`

Ejecución de un workflow; conserva contexto GitHub Actions y resultado de fallo autorizado.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#pipeline_service, SRC_ADR_010, DD-002.

Claves únicas compuestas: `(pipeline_id, github_run_id, run_attempt)`.

Checks: `run_attempt > 0`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-001 |
| pipeline_id | uuid | No | ops.pipelines.id | — | No | Compuesto: (pipeline_id, github_run_id, run_attempt) | — | Pipeline que fue ejecutado. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | — |
| github_run_id | text | No | — | — | No | Compuesto: (pipeline_id, github_run_id, run_attempt) | — | ID externo del run. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-003 |
| run_attempt | integer | No | — | — | No | Compuesto: (pipeline_id, github_run_id, run_attempt) | — | Intento del run; distingue reejecuciones del mismo ID externo. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-003 |
| branch | text | No | — | — | No | No | — | Rama ejecutada. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | — |
| commit_sha | text | No | — | — | No | No | — | Referencia al commit ejecutado. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | — |
| external_status | text | No | — | — | No | No | — | Estado del run suministrado por GitHub; no define un enum interno nuevo. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | — |
| external_conclusion | text | No | — | — | Sí | No | — | Conclusión externa cuando está disponible. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | — |
| failed | boolean | No | — | — | No | No | — | Indica un fallo identificado por GitHub Actions; no representa detección AIOps. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-004 |
| started_at | timestamptz | No | — | — | Sí | No | — | Inicio de ejecución. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-002 |
| completed_at | timestamptz | No | — | — | Sí | No | — | Fin de ejecución. | architecture.yml#pipeline_service; SRC_ADR_010; DD-002 | A-002 |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.execution_stages`

Etapas de una ejecución; los jobs pueden suministrar evidencia sin tablas adicionales.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#pipeline_service, docs/research/arquitectura-informacion.md, DD-013.

Claves únicas compuestas: `(execution_id, stage)`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | A-001 |
| execution_id | uuid | No | ops.pipeline_executions.id | — | No | Compuesto: (execution_id, stage) | — | Ejecución a la que pertenece la etapa. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | — |
| stage | ops.PipelineStage | No | — | — | No | Compuesto: (execution_id, stage) | PipelineStage | Etapa operacional normalizada; no es nivel de log. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | — |
| external_status | text | No | — | — | Sí | No | — | Estado de etapa suministrado por evidencia autorizada. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | — |
| started_at | timestamptz | No | — | — | Sí | No | — | Inicio observado de la etapa. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | A-002 |
| completed_at | timestamptz | No | — | — | Sí | No | — | Fin observado de la etapa. | architecture.yml#pipeline_service; docs/research/arquitectura-informacion.md; DD-013 | A-002 |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.incidents`

Incidente originado en una ejecución fallida, con asignación y tiempos operacionales.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_018, architecture.yml#INV-007, docs/research/arquitectura-informacion.md, DD-002.

Constraints complementarias: exactly_one_failed_origin, origin_pipeline_consistency.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-001 |
| pipeline_id | uuid | No | ops.pipelines.id | — | No | No | — | Pipeline del incidente; debe coincidir con el de su ORIGIN. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| status | ops.IncidentStatus | No | — | — | No | No | IncidentStatus | Estado operacional del incidente. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| severity | ops.Severity | No | — | — | Sí | No | Severity | Severidad operacional; nullable hasta disponer de regla aprobada de derivación. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-005 |
| stage | ops.PipelineStage | No | — | — | No | No | PipelineStage | Etapa del fallo. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| summary | text | No | — | — | No | No | — | Resumen saneado del fallo observado. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| assignee_ref | text | No | — | — | Sí | No | — | Referencia externa a identidad corporativa Entra ID; distinta de ownership del pipeline. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| assignee_display_name_snapshot | text | No | — | — | Sí | No | — | Nombre del assignee al asignar; no es maestro de identidad. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | — |
| detected_at | timestamptz | No | — | — | No | No | — | Instante de detección del fallo; origen del cálculo TMD. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-002 |
| remediation_started_at | timestamptz | No | — | — | Sí | No | — | Start remediation registra estado y tiempo; no ejecuta correcciones. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-002 |
| verification_started_at | timestamptz | No | — | — | Sí | No | — | Inicio de verificación bajo control humano. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-002 |
| resolved_at | timestamptz | No | — | — | Sí | No | — | Resolución operacional del incidente. | SRC_ADR_018; architecture.yml#INV-007; docs/research/arquitectura-informacion.md; DD-002 | A-002 |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.incident_runs`

Vincula un incidente con exactamente un ORIGIN fallido y cero o más VERIFICATION.

Owner: `pipeline_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_018, model/domain_decisions.md, DD-002.

Claves únicas compuestas: `(incident_id, execution_id)`.

Constraints complementarias: at_most_one_origin.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_018; model/domain_decisions.md; DD-002 | A-001 |
| incident_id | uuid | No | ops.incidents.id | — | No | Compuesto: (incident_id, execution_id) | — | Incidente propietario de la relación. | SRC_ADR_018; model/domain_decisions.md; DD-002 | — |
| execution_id | uuid | No | ops.pipeline_executions.id | — | No | Compuesto: (incident_id, execution_id) | — | Ejecución ORIGIN o VERIFICATION; no fija política adicional del workflow de verificación. | SRC_ADR_018; model/domain_decisions.md; DD-002 | — |
| role | ops.IncidentRunRole | No | — | — | No | No | IncidentRunRole | Rol del run en el incidente. | SRC_ADR_018; model/domain_decisions.md; DD-002 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `ops.pipeline_access_grants`

Representación provisional de capacidades por pipeline; no requisito core ni implementación definitiva RBAC.

Owner: `pipeline_service`. scope_basis: `ia_only`. status: `inferred`.

Fuentes: docs/research/arquitectura-informacion.md, SRC_ADR_003, DD-017.

Claves únicas compuestas: `(pipeline_id, principal_ref, capability)`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | docs/research/arquitectura-informacion.md; SRC_ADR_003; DD-017 | A-001 |
| pipeline_id | uuid | No | ops.pipelines.id | — | No | Compuesto: (pipeline_id, principal_ref, capability) | — | Pipeline al que corresponde la capacidad. | docs/research/arquitectura-informacion.md; SRC_ADR_003; DD-017 | — |
| principal_ref | text | No | — | — | No | Compuesto: (pipeline_id, principal_ref, capability) | — | Referencia controlada a principal corporativo Entra ID; sin tabla users/roles. | docs/research/arquitectura-informacion.md; SRC_ADR_003; DD-017 | — |
| capability | ops.AccessCapability | No | — | — | No | Compuesto: (pipeline_id, principal_ref, capability) | AccessCapability | Capacidad funcional propuesta por arquitectura de información. | docs/research/arquitectura-informacion.md; SRC_ADR_003; DD-017 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

## Schema `evidence`

Evidencia normalizada y contexto; ownership por tabla.

Owners permitidos: log_event_service, evidence_correlation_engine.

### `evidence.evidence_items`

Metadata y extracto normalizado en PostgreSQL; logs originales en GitHub Actions. Recuperación y conservación independientes siguen pendientes (ADR-019).

Owner: `log_event_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#log_event_service, SRC_ADR_019, architecture.yml#INV-001, SRC_ADR_013, DD-006.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

Checks: `size_bytes IS NULL OR size_bytes >= 0`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | A-001 |
| incident_id | uuid | No | — | ops.incidents.id | No | No | — | Incidente asociado por ID lógico. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| execution_id | uuid | No | — | ops.pipeline_executions.id | No | No | — | Ejecución observada por ID lógico. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| source | text | No | — | — | No | No | — | Procedencia operacional autorizada, independiente de provenance RAG. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| stage | evidence.PipelineStage | No | — | — | No | No | PipelineStage | Etapa operacional observada. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| job | text | No | — | — | Sí | No | — | Job externo cuando existe. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| summary | text | No | — | — | No | No | — | Resumen normalizado y saneado. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| excerpt | text | No | — | — | Sí | No | — | Extracto minimizado y enmascarado; nunca payload sensible crudo. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| observed_at | timestamptz | No | — | — | No | No | — | Instante observado en la fuente. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | A-002 |
| sequence | bigint | No | — | — | Sí | No | — | Orden de evidencia cuando la fuente lo proporciona. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| content_hash | text | No | — | — | Sí | No | — | Hash del objeto cuando existe; algoritmo no fijado. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| size_bytes | bigint | No | — | — | Sí | No | — | Tamaño externo en bytes cuando está disponible. | architecture.yml#log_event_service; SRC_ADR_019; architecture.yml#INV-001; SRC_ADR_013; DD-006 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `evidence.correlated_contexts`

Snapshot saneado del contexto correlacionado; conserva los IDs de evidencia utilizados.

Owner: `evidence_correlation_engine`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#evidence_correlation_engine, SRC_ADR_015, DD-014.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#evidence_correlation_engine; SRC_ADR_015; DD-014 | A-001 |
| incident_id | uuid | No | — | ops.incidents.id | No | No | — | Incidente del contexto. | architecture.yml#evidence_correlation_engine; SRC_ADR_015; DD-014 | — |
| execution_id | uuid | No | — | ops.pipeline_executions.id | No | No | — | Ejecución correlacionada; no fusionar ejecuciones no relacionadas. | architecture.yml#evidence_correlation_engine; SRC_ADR_015; DD-014 | — |
| evidence_ids | uuid[] | No | — | evidence.evidence_items.id | No | No | — | Colección de IDs lógicos de evidencia; otro servicio no modifica evidence_items. | architecture.yml#evidence_correlation_engine; SRC_ADR_015; DD-014 | A-006 |
| summary | text | No | — | — | No | No | — | Síntesis saneada del contexto operacional. | architecture.yml#evidence_correlation_engine; SRC_ADR_015; DD-014 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

## Schema `diagnosis`

Diagnósticos, recomendaciones y revisión.

Owners permitidos: recommendation_service.

### `diagnosis.diagnoses`

Snapshot diagnóstico versionado append-only; actual = versión mayor por incidente.

Owner: `recommendation_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#recommendation_service, architecture.yml#INV-005, SRC_ADR_013, DD-003.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

Claves únicas compuestas: `(incident_id, version)`.

Checks: `version > 0`; `status <> 'DIAGNOSIS_READY' OR (probable_cause IS NOT NULL AND btrim(probable_cause) <> '' AND diagnosis_ready_at IS NOT NULL)`.

Constraints complementarias: append_only.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | A-001 |
| incident_id | uuid | No | — | ops.incidents.id | No | Compuesto: (incident_id, version) | — | Incidente por referencia lógica; sin asociación JPA cross-context. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | — |
| version | integer | No | — | — | No | Compuesto: (incident_id, version) | — | Versión positiva, única por incidente; cada nuevo snapshot se inserta. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | — |
| status | diagnosis.DiagnosisStatus | No | — | — | No | No | DiagnosisStatus | Estado diagnóstico del snapshot. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | — |
| probable_cause | text | No | — | — | Sí | No | — | Hipótesis de causa probable; obligatoria cuando DIAGNOSIS_READY. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | A-007 |
| explanation | text | No | — | — | Sí | No | — | Explicación saneada del diagnóstico. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | — |
| limitations | text | No | — | — | Sí | No | — | Limitaciones de evidencia/inferencia. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | — |
| confidence | jsonb | No | — | — | Sí | No | — | Valor informado por el proveedor, sin imponer tipo numérico, escala ni rango. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | A-008 |
| diagnosis_ready_at | timestamptz | No | — | — | Sí | No | — | Instante de disponibilidad de esta versión; TMD se calcula con detected_at del incidente. | architecture.yml#recommendation_service; architecture.yml#INV-005; SRC_ADR_013; DD-003 | A-002 |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `diagnosis.recommendations`

Recomendación como entidad propia de una versión diagnóstica; no ejecuta remediación.

Owner: `recommendation_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#recommendation_service, SRC_ADR_016, SRC_ADR_013, DD-004.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#recommendation_service; SRC_ADR_016; SRC_ADR_013; DD-004 | A-001 |
| diagnosis_id | uuid | No | diagnosis.diagnoses.id | — | No | No | — | Versión que propone la recomendación. | architecture.yml#recommendation_service; SRC_ADR_016; SRC_ADR_013; DD-004 | — |
| description | text | No | — | — | No | No | — | Procedimiento o acción recomendada para evaluación humana. | architecture.yml#recommendation_service; SRC_ADR_016; SRC_ADR_013; DD-004 | — |
| critical | boolean | No | — | — | No | No | — | Marcado de recomendación crítica para gobierno humano. | architecture.yml#human_review_component | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `diagnosis.diagnosis_evidence_links`

Traza qué evidencia operacional sustenta una versión diagnóstica.

Owner: `recommendation_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#diagnostic_output_component, SRC_ADR_013, DD-006.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

Claves únicas compuestas: `(diagnosis_id, evidence_id)`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#diagnostic_output_component; SRC_ADR_013; DD-006 | A-001 |
| diagnosis_id | uuid | No | diagnosis.diagnoses.id | — | No | Compuesto: (diagnosis_id, evidence_id) | — | Versión diagnóstica sustentada. | architecture.yml#diagnostic_output_component; SRC_ADR_013; DD-006 | — |
| evidence_id | uuid | No | — | evidence.evidence_items.id | No | Compuesto: (diagnosis_id, evidence_id) | — | Evidencia operacional consultada por ID lógico. | architecture.yml#diagnostic_output_component; SRC_ADR_013; DD-006 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `diagnosis.diagnosis_source_links`

Traza consulted_sources: Diagnosis → KnowledgeChunk → KnowledgeDocument.

Owner: `recommendation_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#diagnostic_output_component, architecture.yml#rag_retrieval, SRC_ADR_013, DD-007.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

Claves únicas compuestas: `(diagnosis_id, knowledge_chunk_id)`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#diagnostic_output_component; architecture.yml#rag_retrieval; SRC_ADR_013; DD-007 | A-001 |
| diagnosis_id | uuid | No | diagnosis.diagnoses.id | — | No | Compuesto: (diagnosis_id, knowledge_chunk_id) | — | Versión diagnóstica que consultó RAG. | architecture.yml#diagnostic_output_component; architecture.yml#rag_retrieval; SRC_ADR_013; DD-007 | — |
| knowledge_chunk_id | uuid | No | — | knowledge.knowledge_chunks.id | No | Compuesto: (diagnosis_id, knowledge_chunk_id) | — | Chunk consultado; documento reconstruible mediante FK de knowledge_chunks. | architecture.yml#diagnostic_output_component; architecture.yml#rag_retrieval; SRC_ADR_013; DD-007 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `diagnosis.human_reviews`

Revisión humana: ausencia = PENDING derivado; decision solo CONFIRMED, CORRECTED o REJECTED.

Owner: `recommendation_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_011, SRC_ADR_016, architecture.yml#INV-006, SRC_ADR_013, DD-005.

Retención: 365 días (ADR-013), anclada en `created_at`; no hay purge jobs.

Checks: `decision <> 'CORRECTED' OR (actual_cause IS NOT NULL AND btrim(actual_cause) <> '')`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | A-001 |
| diagnostic_id | uuid | No | diagnosis.diagnoses.id | — | No | No | — | Versión revisada; conserva el nombre contractual diagnostic_id de ADR-011. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | — |
| reviewer_ref | text | No | — | — | No | No | — | Identidad externa del revisor corporativo; mapea reviewer del contrato. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | — |
| decision | diagnosis.HumanReviewDecision | No | — | — | No | No | HumanReviewDecision | CONFIRMED acepta; CORRECTED aporta causa corregida; REJECTED rechaza sin alternativa validada. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | — |
| timestamp | timestamptz | No | — | — | No | No | — | Instante de revisión del contrato. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | A-002 |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| actual_cause | text | No | — | — | Sí | No | — | Causa corregida suministrada por el revisor; requerida semánticamente en CORRECTED. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | — |
| comment | text | No | — | — | Sí | No | — | Comentario saneado del revisor. | SRC_ADR_011; SRC_ADR_016; architecture.yml#INV-006; SRC_ADR_013; DD-005 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

## Schema `knowledge`

Corpus autorizado recuperable.

Owners permitidos: rag_retrieval.

### `knowledge.knowledge_documents`

Corpus autorizado; prohíbe casos de evaluación y soluciones de referencia conforme a INV-010.

Owner: `rag_retrieval`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: architecture.yml#rag_retrieval, architecture.yml#INV-010, SRC_ADR_007, DD-007, DD-022.

Claves únicas compuestas: `(tenant_id, github_repository_id, source_id, source_version)`.

Checks: `btrim(provenance) <> ''`; `corpus_kind <> 'reviewed_incidents' OR reviewed_incident_id IS NOT NULL`; `content_hash ~ '^[0-9a-f]{64}$'`; `btrim(authorization_reference) <> ''`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | A-001 |
| corpus_kind | knowledge.KnowledgeCorpusKind | No | — | — | No | No | KnowledgeCorpusKind | Clase de corpus autorizado. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| title | text | No | — | — | No | No | — | Título de la fuente autorizada. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| provenance | text | No | — | — | No | No | — | Referencia obligatoria de origen autorizado; nunca URL con tokens o secretos. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| reviewed_incident_id | uuid | No | — | ops.incidents.id | Sí | No | — | Incidente revisado cuando el corpus es reviewed_incidents; elegibilidad RAG requiere separación evaluación. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| tenant_id | uuid | No | — | — | No | Compuesto: (tenant_id, github_repository_id, source_id, source_version) | — | Tenant autorizado del documento; no se deriva de similitud semÃ¡ntica. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| github_installation_id | text | No | — | — | No | No | — | InstalaciÃ³n GitHub verificada para el alcance del corpus. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| github_repository_id | text | No | — | — | No | Compuesto: (tenant_id, github_repository_id, source_id, source_version) | — | Repositorio GitHub verificado para el alcance del corpus. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| pipeline_id | uuid | No | — | ops.pipelines.id | Sí | No | — | Pipeline opcional del alcance; referencia lÃ³gica, sin FK cross-schema. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| scope_revision | text | No | — | — | No | No | — | RevisiÃ³n opaca del alcance autorizado entregado por Recommendation. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| source_id | text | No | — | — | No | Compuesto: (tenant_id, github_repository_id, source_id, source_version) | — | Identidad estable de la fuente administrativa autorizada. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| source_version | text | No | — | — | No | Compuesto: (tenant_id, github_repository_id, source_id, source_version) | — | VersiÃ³n opaca usada para importaciÃ³n idempotente. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| content_hash | text | No | — | — | No | No | — | SHA-256 hexadecimal del contenido canÃ³nico importado. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| authorization_reference | text | No | — | — | No | No | — | Evidencia no secreta de autorizaciÃ³n de la fuente. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| active | boolean | No | — | — | No | No | — | Solo la versiÃ³n activa participa en recuperaciÃ³n. | architecture.yml#rag_retrieval; architecture.yml#INV-010; SRC_ADR_007; DD-007; DD-022 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

### `knowledge.knowledge_chunks`

Chunks recuperables de documentos autorizados; conserva provenance y pgvector sin dimensión fija.

Owner: `rag_retrieval`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_007, architecture.yml#INV-010, DD-009.

Claves únicas compuestas: `(document_id, chunk_index)`.

Checks: `chunk_index >= 0`; `btrim(provenance) <> ''`.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_007; architecture.yml#INV-010; DD-009 | A-001 |
| document_id | uuid | No | knowledge.knowledge_documents.id | — | No | Compuesto: (document_id, chunk_index) | — | Documento de procedencia; permite reconstruir fuentes. | SRC_ADR_007; architecture.yml#INV-010; DD-009 | — |
| chunk_index | integer | No | — | — | No | Compuesto: (document_id, chunk_index) | — | Posición del chunk dentro del documento. | SRC_ADR_007; architecture.yml#INV-010; DD-009 | A-009 |
| content | text | No | — | — | No | No | — | Fragmento autorizado y saneado; nunca casos/soluciones de evaluación. | SRC_ADR_007; architecture.yml#INV-010; DD-009 | — |
| provenance | text | No | — | — | No | No | — | Procedencia obligatoria del fragmento dentro de su documento. | SRC_ADR_007; architecture.yml#INV-010; DD-009 | — |
| embedding | vector | No | — | — | Sí | No | — | Embedding pgvector; dimensión abierta, sin vector(n). | SRC_ADR_007; architecture.yml#INV-010; DD-009 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

## Schema `audit`

Auditoría transversal funcional.

Owners permitidos: shared.

### `audit.audit_events`

Auditoría funcional transversal; before/after contienen solo metadata sanitizada, jamás logs crudos, secretos, tokens o credenciales.

Owner: `shared`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_011, architecture.yml#audit_trail, architecture.yml#CTRL-002, DD-016.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | Identificador estable asignado por el servicio propietario. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | A-001 |
| category | audit.AuditCategory | No | — | — | No | No | AuditCategory | Categoría funcional declarada en architecture.yml. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| correlation_id | text | No | — | — | No | No | — | Identificador de correlación end-to-end; no contiene información sensible. | architecture.yml#CTRL-003 | — |
| actor_ref | text | No | — | — | Sí | No | — | Identidad externa del actor cuando está disponible. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| entity_type | text | No | — | — | No | No | — | Tipo de objeto auditado; referencia polimórfica lógica. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| entity_id | text | No | — | — | No | No | — | ID lógico del objeto auditado; sin FK polimórfica. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| action | text | No | — | — | No | No | — | Acción funcional observada. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| before_state | jsonb | No | — | — | Sí | No | — | Solo metadata sanitizada previa; prohíbe raw logs/payload sensible no enmascarado. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| after_state | jsonb | No | — | — | Sí | No | — | Solo metadata sanitizada posterior; prohíbe secrets, tokens y credentials. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | — |
| occurred_at | timestamptz | No | — | — | No | No | — | Instante de ocurrencia del evento funcional. | SRC_ADR_011; architecture.yml#audit_trail; architecture.yml#CTRL-002; DD-016 | A-002 |
| created_at | timestamptz | No | — | — | No | No | — | Instante de persistencia; permite aplicar retención cuando corresponde. | SRC_ADR_013; DD-015 | A-002 |

## Schema `ingestion`

Metadata de conector GitHub (DD-020), ledger de captura/publicación y buffer temporal de bytes protegidos (DD-021); sin credenciales ni entradas crudas.

Owners permitidos: ingestion_normalization_service.

### `ingestion.github_connections`

Metadata técnica del conector GitHub: github_connections

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_020, DD-020, github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada.

Claves únicas compuestas: `(tenant_id, entra_object_id)`; `(id, tenant_id, entra_object_id)`.

FK compuesta `github_connections_active_generation_fk`: (id, active_generation_id) → ingestion.github_connection_generations (connection_id, id); diferida al commit en extras.sql.

Checks: `revision >= 0`; `updated_at >= created_at`.

Constraints complementarias: connector_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | Compuesto: (id, tenant_id, entra_object_id) | — | id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| tenant_id | uuid | No | — | — | No | Compuesto: (tenant_id, entra_object_id); (id, tenant_id, entra_object_id) | — | tenant id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| entra_object_id | uuid | No | — | — | No | Compuesto: (tenant_id, entra_object_id); (id, tenant_id, entra_object_id) | — | entra object id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| revision | bigint | No | — | — | No | No | — | revision | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| active_generation_id | uuid | No | — | — | Sí | No | — | active generation id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |

### `ingestion.github_connection_generations`

Metadata técnica del conector GitHub: github_connection_generations

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_020, DD-020, github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada.

Claves únicas compuestas: `(connection_id, id)`; `(secret_object_ref)`.

Unicidad parcial `github_generations_one_active_uq`: (connection_id) WHERE `state = 'ACTIVE'`; extras.sql.

Checks: `state IN ('PREPARING','ACTIVE','BLOCKED','INVALIDATED')`; `revision >= 0`; `(activated_at IS NULL AND state IN ('PREPARING','INVALIDATED')) OR (activated_at IS NOT NULL AND github_user_id IS NOT NULL AND active_secret_version_ref IS NOT NULL AND access_expires_at IS NOT NULL AND refresh_expires_at IS NOT NULL)`; `btrim(secret_object_ref) <> ''`; `github_user_id IS NULL OR btrim(github_user_id) <> ''`; `active_secret_version_ref IS NULL OR (btrim(active_secret_version_ref) <> '' AND lower(btrim(active_secret_version_ref)) <> 'latest')`; `updated_at >= created_at`; `secret_object_ref = 'generation:' || id::text`.

Constraints complementarias: connector_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | Compuesto: (connection_id, id) | — | id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| connection_id | uuid | No | ingestion.github_connections.id | — | No | Compuesto: (connection_id, id) | — | connection id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| github_user_id | text | No | — | — | Sí | No | — | github user id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| state | text | No | — | — | No | No | — | state | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| secret_object_ref | text | No | — | — | No | Compuesto: (secret_object_ref) | — | secret object ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| active_secret_version_ref | text | No | — | — | Sí | No | — | active secret version ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| access_expires_at | timestamptz | No | — | — | Sí | No | — | access expires at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| refresh_expires_at | timestamptz | No | — | — | Sí | No | — | refresh expires at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| activated_at | timestamptz | No | — | — | Sí | No | — | activated at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| revision | bigint | No | — | — | No | No | — | revision | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |

### `ingestion.github_authorization_attempts`

Metadata técnica del conector GitHub: github_authorization_attempts

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_020, DD-020, github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada.

Claves únicas compuestas: `(target_generation_id)`; `(state_digest)`; `(pkce_secret_object_ref)`.

FK compuesta `github_attempts_identity_fk`: (connection_id, tenant_id, entra_object_id) → ingestion.github_connections (id, tenant_id, entra_object_id); diferida al commit en extras.sql.

FK compuesta `github_attempts_expected_generation_fk`: (connection_id, expected_generation_id) → ingestion.github_connection_generations (connection_id, id); diferida al commit en extras.sql.

FK compuesta `github_attempts_target_generation_fk`: (connection_id, target_generation_id) → ingestion.github_connection_generations (connection_id, id); diferida al commit en extras.sql.

Checks: `phase IN ('PREPARING','READY','CLAIMED','COMPLETED','FAILED','EXPIRED')`; `pkce_cleanup_state IN ('HELD','PENDING','COMPLETED','BLOCKED')`; `pkce_cleanup_result IS NULL OR pkce_cleanup_result IN ('CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE')`; `expected_connection_revision >= 0`; `phase NOT IN ('READY','CLAIMED','COMPLETED') OR pkce_secret_version_ref IS NOT NULL`; `phase NOT IN ('CLAIMED','COMPLETED') OR consumed_at IS NOT NULL`; `phase NOT IN ('PREPARING','READY') OR consumed_at IS NULL`; `phase NOT IN ('COMPLETED','FAILED','EXPIRED') OR pkce_cleanup_state <> 'HELD'`; `pkce_cleanup_state <> 'COMPLETED' OR (pkce_cleanup_result IS NOT NULL AND pkce_cleanup_result IN ('CONFIRMED','NOT_APPLICABLE'))`; `btrim(pkce_secret_object_ref) <> ''`; `pkce_secret_version_ref IS NULL OR (btrim(pkce_secret_version_ref) <> '' AND lower(btrim(pkce_secret_version_ref)) <> 'latest')`; `btrim(approved_return_ref) <> ''`; `btrim(correlation_id) <> ''`; `expires_at > created_at`; `updated_at >= created_at`; `pkce_cleanup_state <> 'COMPLETED' OR phase IN ('COMPLETED','FAILED','EXPIRED')`; `pkce_secret_object_ref = 'pkce:' || id::text`.

Constraints complementarias: connector_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| connection_id | uuid | No | — | — | No | No | — | connection id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| tenant_id | uuid | No | — | — | No | No | — | tenant id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| entra_object_id | uuid | No | — | — | No | No | — | entra object id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| expected_connection_revision | bigint | No | — | — | No | No | — | expected connection revision | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| expected_generation_id | uuid | No | — | — | Sí | No | — | expected generation id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| target_generation_id | uuid | No | — | — | No | Compuesto: (target_generation_id) | — | target generation id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| state_digest | bytea | No | — | — | No | Compuesto: (state_digest) | — | state digest | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| expires_at | timestamptz | No | — | — | No | No | — | expires at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| phase | text | No | — | — | No | No | — | phase | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| consumed_at | timestamptz | No | — | — | Sí | No | — | consumed at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| pkce_secret_object_ref | text | No | — | — | No | Compuesto: (pkce_secret_object_ref) | — | pkce secret object ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| pkce_secret_version_ref | text | No | — | — | Sí | No | — | pkce secret version ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| pkce_cleanup_state | text | No | — | — | No | No | — | pkce cleanup state | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| pkce_cleanup_result | text | No | — | — | Sí | No | — | pkce cleanup result | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| approved_return_ref | text | No | — | — | No | No | — | approved return ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| correlation_id | text | No | — | — | No | No | — | correlation id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |

### `ingestion.github_credential_operations`

Metadata técnica del conector GitHub: github_credential_operations

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: SRC_ADR_020, DD-020, github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada.

FK compuesta `github_operations_generation_fk`: (connection_id, generation_id) → ingestion.github_connection_generations (connection_id, id); diferida al commit en extras.sql.

Unicidad parcial `github_operations_one_refresh_uq`: (generation_id) WHERE `kind = 'REFRESH' AND phase <> 'COMPLETED'`; extras.sql.

Checks: `kind IN ('REFRESH','CLEANUP')`; `(kind = 'REFRESH' AND phase IN ('PENDING','CLAIMED','REQUEST_MAY_BE_IN_FLIGHT','VERSION_SAVED','COMPLETED','BLOCKED')) OR (kind = 'CLEANUP' AND phase IN ('PENDING','CLAIMED','COMPLETED','BLOCKED'))`; `fence >= 0 AND expected_connection_revision >= 0 AND expected_generation_revision >= 0`; `(phase = 'PENDING' AND owner_id IS NULL AND started_at IS NULL AND deadline_at IS NULL) OR (phase <> 'PENDING' AND owner_id IS NOT NULL AND started_at IS NOT NULL AND deadline_at IS NOT NULL AND deadline_at >= started_at)`; `(phase = 'COMPLETED') = (completed_at IS NOT NULL)`; `(kind = 'REFRESH' AND cleanup_scope IS NULL AND cleanup_target_version_ref IS NULL AND upstream_result IS NULL AND vault_result IS NULL) OR (kind = 'CLEANUP' AND candidate_secret_version_ref IS NULL AND cleanup_scope IS NOT NULL AND cleanup_scope IN ('EXACT_VERSION','INVALIDATED_GENERATION') AND upstream_result IS NOT NULL AND upstream_result IN ('PENDING','CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE') AND vault_result IS NOT NULL AND vault_result IN ('PENDING','CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE'))`; `kind <> 'CLEANUP' OR ((cleanup_scope = 'EXACT_VERSION' AND cleanup_target_version_ref IS NOT NULL) OR (cleanup_scope = 'INVALIDATED_GENERATION' AND cleanup_target_version_ref IS NULL))`; `(candidate_secret_version_ref IS NULL OR (btrim(candidate_secret_version_ref) <> '' AND lower(btrim(candidate_secret_version_ref)) <> 'latest')) AND (cleanup_target_version_ref IS NULL OR (btrim(cleanup_target_version_ref) <> '' AND lower(btrim(cleanup_target_version_ref)) <> 'latest'))`; `kind <> 'REFRESH' OR phase NOT IN ('VERSION_SAVED','COMPLETED') OR candidate_secret_version_ref IS NOT NULL`; `kind <> 'CLEANUP' OR phase <> 'COMPLETED' OR (upstream_result IN ('CONFIRMED','NOT_APPLICABLE') AND vault_result IN ('CONFIRMED','NOT_APPLICABLE'))`; `updated_at >= created_at`.

Constraints complementarias: connector_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| connection_id | uuid | No | — | — | No | No | — | connection id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| generation_id | uuid | No | — | — | No | No | — | generation id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| expected_connection_revision | bigint | No | — | — | No | No | — | expected connection revision | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| expected_generation_revision | bigint | No | — | — | No | No | — | expected generation revision | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| kind | text | No | — | — | No | No | — | kind | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| phase | text | No | — | — | No | No | — | phase | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| owner_id | uuid | No | — | — | Sí | No | — | owner id | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| fence | bigint | No | — | — | No | No | — | fence | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| started_at | timestamptz | No | — | — | Sí | No | — | started at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| deadline_at | timestamptz | No | — | — | Sí | No | — | deadline at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| candidate_secret_version_ref | text | No | — | — | Sí | No | — | candidate secret version ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| cleanup_target_version_ref | text | No | — | — | Sí | No | — | cleanup target version ref | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| cleanup_scope | text | No | — | — | Sí | No | — | cleanup scope | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| upstream_result | text | No | — | — | Sí | No | — | upstream result | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| vault_result | text | No | — | — | Sí | No | — | vault result | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| completed_at | timestamptz | No | — | — | Sí | No | — | completed at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | SRC_ADR_020; DD-020; github-connector-draft-0.2 — aprobación local 2026-11-07: Propuesta aprobada | — |

### `ingestion.capture_receipts`

Captura/publicación durable de Ingestion: capture_receipts

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: DD-021, capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello.

Claves únicas compuestas: `(capture_domain, source, body_digest)`; `(capture_domain, source, id)`.

FK compuesta `capture_receipts_observation_fk`: (capture_domain, source, observation_id) → ingestion.capture_observations (capture_domain, source, id); diferida al commit en extras.sql.

Checks: `btrim(capture_domain) <> ''`; `btrim(source) <> ''`; `btrim(body_digest) <> ''`; `body_digest ~ '^[0-9a-f]{64}$'`; `btrim(app_id) <> ''`; `app_id ~ '^[1-9][0-9]*$'`; `btrim(account_id) <> ''`; `account_id ~ '^[1-9][0-9]*$'`; `btrim(installation_id) <> ''`; `installation_id ~ '^[1-9][0-9]*$'`; `btrim(repository_id) <> ''`; `repository_id ~ '^[1-9][0-9]*$'`; `btrim(workflow_id) <> ''`; `workflow_id ~ '^[1-9][0-9]*$'`; `btrim(run_id) <> ''`; `run_id ~ '^[1-9][0-9]*$'`; `run_attempt > 0`; `btrim(scope_revision) <> ''`; `btrim(correlation_id) <> ''`; `btrim(phase) <> ''`; `revision >= 0`; `claim_fence >= 0`; `updated_at >= created_at`; `(claim_owner IS NULL) = (lease_until IS NULL)`; `(phase = 'BLOCKED') = (blocked_reason IS NOT NULL) AND (blocked_reason IS NULL OR btrim(blocked_reason) <> '')`; `phase IN ('ACCEPTED','PREPARED','PUBLISHED','BLOCKED')`; `snapshot_message_id <> evidence_message_id`; `(phase NOT IN ('PREPARED','PUBLISHED') OR (observation_id IS NOT NULL AND prepared_at IS NOT NULL AND replay_until IS NOT NULL)) AND (phase <> 'ACCEPTED' OR (observation_id IS NULL AND prepared_at IS NULL AND published_at IS NULL))`; `(phase = 'PUBLISHED') = (published_at IS NOT NULL)`; `(prepared_at IS NULL OR prepared_at >= created_at) AND (published_at IS NULL OR published_at >= prepared_at) AND replay_until > created_at`; `claim_owner IS NULL OR phase = 'ACCEPTED'`.

Constraints complementarias: capture_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | Compuesto: (capture_domain, source, id) | — | id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| capture_domain | text | No | — | — | No | Compuesto: (capture_domain, source, body_digest); (capture_domain, source, id) | — | capture domain | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| tenant_id | uuid | No | — | — | No | No | — | tenant id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| source | text | No | — | — | No | Compuesto: (capture_domain, source, body_digest); (capture_domain, source, id) | — | source | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| body_digest | text | No | — | — | No | Compuesto: (capture_domain, source, body_digest) | — | body digest | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| app_id | text | No | — | — | No | No | — | app id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| account_id | text | No | — | — | No | No | — | account id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| installation_id | text | No | — | — | No | No | — | installation id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| repository_id | text | No | — | — | No | No | — | repository id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| workflow_id | text | No | — | — | No | No | — | workflow id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| run_id | text | No | — | — | No | No | — | run id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| run_attempt | integer | No | — | — | No | No | — | run attempt | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| scope_revision | text | No | — | — | No | No | — | scope revision | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| correlation_id | text | No | — | — | No | No | — | correlation id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| snapshot_message_id | uuid | No | — | — | No | Sí | — | snapshot message id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| evidence_message_id | uuid | No | — | — | No | Sí | — | evidence message id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| phase | text | No | — | — | No | No | — | phase | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| revision | bigint | No | — | — | No | No | — | revision | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| claim_fence | bigint | No | — | — | No | No | — | claim fence | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| claim_owner | uuid | No | — | — | Sí | No | — | claim owner | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| lease_until | timestamptz | No | — | — | Sí | No | — | lease until | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| observation_id | uuid | No | — | — | Sí | No | — | observation id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| blocked_reason | text | No | — | — | Sí | No | — | blocked reason | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| prepared_at | timestamptz | No | — | — | Sí | No | — | prepared at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| published_at | timestamptz | No | — | — | Sí | No | — | published at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| replay_until | timestamptz | No | — | — | No | No | — | replay until | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |

### `ingestion.capture_delivery_aliases`

Captura/publicación durable de Ingestion: capture_delivery_aliases

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: DD-021, capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello.

Claves únicas compuestas: `(capture_domain, source, delivery_id)`.

FK compuesta `capture_aliases_receipt_fk`: (capture_domain, source, receipt_id) → ingestion.capture_receipts (capture_domain, source, id); diferida al commit en extras.sql.

Checks: `btrim(capture_domain) <> ''`; `btrim(source) <> ''`; `btrim(delivery_id) <> ''`.

Constraints complementarias: capture_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| capture_domain | text | No | — | — | No | Compuesto: (capture_domain, source, delivery_id) | — | capture domain | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| source | text | No | — | — | No | Compuesto: (capture_domain, source, delivery_id) | — | source | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| delivery_id | text | No | — | — | No | Compuesto: (capture_domain, source, delivery_id) | — | delivery id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| receipt_id | uuid | No | — | — | No | No | — | receipt id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |

### `ingestion.capture_observations`

Captura/publicación durable de Ingestion: capture_observations

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: DD-021, capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello.

Claves únicas compuestas: `(capture_domain, source, observation_key)`; `(capture_domain, source, id)`.

FK compuesta `capture_observations_origin_fk`: (capture_domain, source, origin_receipt_id) → ingestion.capture_receipts (capture_domain, source, id); diferida al commit en extras.sql.

Checks: `btrim(capture_domain) <> ''`; `btrim(source) <> ''`; `observation_key ~ '^[0-9a-f]{64}$'`; `btrim(protected_content_digest) <> ''`; `protected_content_digest ~ '^[0-9a-f]{64}$'`; `btrim(repository_id) <> ''`; `repository_id ~ '^[1-9][0-9]*$'`; `btrim(workflow_id) <> ''`; `workflow_id ~ '^[1-9][0-9]*$'`; `btrim(run_id) <> ''`; `run_id ~ '^[1-9][0-9]*$'`; `run_attempt > 0`; `btrim(normalizer_version) <> ''`; `btrim(protection_policy_version) <> ''`; `btrim(correlation_id) <> ''`; `required_output_count IN (1,2)`; `observed_at_submicro BETWEEN 0 AND 999`; `source_updated_at_submicro BETWEEN 0 AND 999`.

Constraints complementarias: capture_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | Compuesto: (capture_domain, source, id) | — | id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| capture_domain | text | No | — | — | No | Compuesto: (capture_domain, source, observation_key); (capture_domain, source, id) | — | capture domain | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| source | text | No | — | — | No | Compuesto: (capture_domain, source, observation_key); (capture_domain, source, id) | — | source | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| observation_key | text | No | — | — | No | Compuesto: (capture_domain, source, observation_key) | — | observation key | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| protected_content_digest | text | No | — | — | No | No | — | protected content digest | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| origin_receipt_id | uuid | No | — | — | No | No | — | origin receipt id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| repository_id | text | No | — | — | No | No | — | repository id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| workflow_id | text | No | — | — | No | No | — | workflow id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| run_id | text | No | — | — | No | No | — | run id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| run_attempt | integer | No | — | — | No | No | — | run attempt | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| observed_at | timestamptz | No | — | — | No | No | — | observed at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| observed_at_submicro | integer | No | — | — | No | No | — | observed at submicro | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| source_updated_at | timestamptz | No | — | — | No | No | — | source updated at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| source_updated_at_submicro | integer | No | — | — | No | No | — | source updated at submicro | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| normalizer_version | text | No | — | — | No | No | — | normalizer version | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| protection_policy_version | text | No | — | — | No | No | — | protection policy version | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| correlation_id | text | No | — | — | No | No | — | correlation id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| required_output_count | integer | No | — | — | No | No | — | required output count | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |

### `ingestion.publication_outputs`

Captura/publicación durable de Ingestion: publication_outputs

Owner: `ingestion_normalization_service`. scope_basis: `approved_domain`. status: `confirmed`.

Fuentes: DD-021, capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello.

FK compuesta `publication_outputs_observation_fk`: (observation_id) → ingestion.capture_observations (id); diferida al commit en extras.sql.

Unicidad parcial `publication_outputs_snapshot_uq`: (observation_id) WHERE `event_type = 'execution.snapshot'`; extras.sql.

Unicidad parcial `publication_outputs_fragment_uq`: (observation_id, fragment_locator) WHERE `event_type = 'protected_workflow_evidence'`; extras.sql.

Checks: `btrim(event_type) <> ''`; `btrim(payload_digest) <> ''`; `payload_digest ~ '^[0-9a-f]{64}$'`; `btrim(phase) <> ''`; `revision >= 0`; `claim_fence >= 0`; `attempt_count >= 0`; `updated_at >= created_at`; `(claim_owner IS NULL) = (lease_until IS NULL)`; `(phase = 'BLOCKED') = (blocked_reason IS NOT NULL) AND (blocked_reason IS NULL OR btrim(blocked_reason) <> '')`; `(event_type = 'execution.snapshot' AND schema_major = 1 AND fragment_locator IS NULL) OR (event_type = 'protected_workflow_evidence' AND schema_major = 2 AND fragment_locator IS NOT NULL AND btrim(fragment_locator) <> '')`; `phase IN ('PENDING','CLAIMED','CONFIRMED','BLOCKED')`; `(phase = 'CLAIMED') = (claim_owner IS NOT NULL)`; `(phase = 'CONFIRMED') = (confirmed_at IS NOT NULL)`; `(payload IS NOT NULL AND payload_removed_at IS NULL) OR (payload IS NULL AND phase = 'CONFIRMED' AND payload_removed_at IS NOT NULL AND payload_recover_until IS NOT NULL AND payload_removed_at >= payload_recover_until)`; `(confirmed_at IS NULL OR confirmed_at >= created_at) AND (payload_removed_at IS NULL OR payload_removed_at >= confirmed_at) AND (payload_recover_until IS NULL OR payload_recover_until > created_at)`; `phase <> 'CLAIMED' OR (last_attempt_at IS NOT NULL AND lease_until > last_attempt_at AND attempt_count > 0)`.

Constraints complementarias: capture_lifecycle.

| Columna | Tipo | PK | FK | logical_ref | Nullable | Unique | Enum | Descripción | Fuente | Assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | Sí | — | — | No | No | — | id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| observation_id | uuid | No | — | — | No | No | — | observation id | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| event_type | text | No | — | — | No | No | — | event type | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| schema_major | integer | No | — | — | No | No | — | schema major | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| fragment_locator | text | No | — | — | Sí | No | — | fragment locator | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| payload | bytea | No | — | — | Sí | No | — | payload | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| payload_digest | text | No | — | — | No | No | — | payload digest | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| phase | text | No | — | — | No | No | — | phase | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| revision | bigint | No | — | — | No | No | — | revision | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| claim_fence | bigint | No | — | — | No | No | — | claim fence | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| attempt_count | bigint | No | — | — | No | No | — | attempt count | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| claim_owner | uuid | No | — | — | Sí | No | — | claim owner | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| lease_until | timestamptz | No | — | — | Sí | No | — | lease until | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| next_attempt_at | timestamptz | No | — | — | Sí | No | — | next attempt at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| last_attempt_at | timestamptz | No | — | — | Sí | No | — | last attempt at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| confirmed_at | timestamptz | No | — | — | Sí | No | — | confirmed at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| payload_removed_at | timestamptz | No | — | — | Sí | No | — | payload removed at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| payload_recover_until | timestamptz | No | — | — | Sí | No | — | payload recover until | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| blocked_reason | text | No | — | — | Sí | No | — | blocked reason | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| created_at | timestamptz | No | — | — | No | No | — | created at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |
| updated_at | timestamptz | No | — | — | No | No | — | updated at | DD-021; capture-publication-draft-0.1 — adopción local 2026-11-08: Vamos a por ello | — |

## Enums

- `IncidentStatus`: OPEN, IN_REMEDIATION, VERIFICATION, RESOLVED.
- `DiagnosisStatus`: ANALYZING, DIAGNOSIS_READY, INCONCLUSIVE.
- `HumanReviewDecision`: CONFIRMED, CORRECTED, REJECTED.
- `IncidentRunRole`: ORIGIN, VERIFICATION.
- `PipelineStage`: BUILD, TESTING, QUALITY_GATE, DEPLOYMENT, CONTAINER, INFRASTRUCTURE.
- `MonitoringStatus`: ACTIVE, PAUSED.
- `AccessCapability`: VIEW, OPERATE, CONFIGURE.
- `Severity`: CRITICAL, HIGH, MEDIUM, LOW.
- `PipelineCriticality`: CRITICAL, HIGH, MEDIUM, LOW.
- `KnowledgeCorpusKind`: reviewed_incidents, authorized_technical_documentation, authorized_response_procedures.
- `AuditCategory`: diagnostic_generation, evidence_usage, human_review, access_and_governance_events.

## Decisiones de diseño

### DD-001 — Repository separado + Pipeline = monitored GitHub Actions workflow

- id: DD-001
- contexto: La IA presenta repositorio y workflow; el prompt aprueba su identidad de dominio.
- decisión: Repository es entidad propia, con relación 1:N Pipeline. Pipeline representa directamente un workflow monitorizado; no existe workflows.
- fuentes: Prompt aprobado §6.A; architecture.yml#pipeline_service; arquitectura-informacion.md.
- impacto: repositories y pipelines en ops, propiedad de pipeline_service; sin nuevas fronteras C4.
- reversibilidad: Separar workflows requeriría una nueva decisión y migración explícita.

### DD-002 — Incident con 1 ORIGIN + N VERIFICATION

- id: DD-002
- contexto: El incidente nace de exactamente una ejecución fallida; la verificación admite varias ejecuciones.
- decisión: incident_runs usa ORIGIN/VERIFICATION. Un índice parcial garantiza como máximo un ORIGIN; triggers diferidos exigen exactamente uno fallido al commit, con ORIGIN consistente con el pipeline del incidente. No se impone un workflow concreto a VERIFICATION. Se bloquea TRUNCATE de vínculos para preservar el invariante.
- fuentes: Prompt aprobado §6.B; SRC_ADR_010; SRC_ADR_018.
- impacto: Crear incidente y ORIGIN en la misma transacción; cambiar el ORIGIN o el pipeline revalida consistencia. La ejecución fallida es dato de GitHub, no un detector propio.
- reversibilidad: Cambiar cardinalidad o requisito de fallo requiere decisión aprobada y reemplazar constraints.

### DD-003 — Diagnosis append-only versionado

- id: DD-003
- contexto: El diagnóstico evoluciona sin reemplazar las hipótesis anteriores.
- decisión: Cada snapshot tiene versión positiva y única por incidente; actual = mayor versión. UPDATE/DELETE/TRUNCATE se rechazan. Cambiar estado también añade una versión. probable_cause puede ser null en ANALYZING/INCONCLUSIVE; DIAGNOSIS_READY exige causa probable y diagnosis_ready_at.
- fuentes: Prompt aprobado §6.C; architecture.yml#INV-005; SRC_ADR_013.
- impacto: Historial inmutable y lectura de última versión en aplicación. Una futura operación de retención necesita procedimiento controlado explícito; no se crea purge job.
- reversibilidad: Cambiar mutabilidad requiere nueva decisión; las hipótesis históricas pueden migrarse sin perder versiones.

### DD-004 — Recommendation entidad propia

- id: DD-004
- contexto: Una versión puede proponer varias recomendaciones trazables.
- decisión: diagnoses 1:N recommendations, con descripción y marcado crítico conforme al componente de gobierno humano. No se ejecuta remediación automática.
- fuentes: Prompt aprobado §6.D; SRC_ADR_016; architecture.yml#INV-007.
- impacto: FK dentro de diagnosis; recomendaciones no embebidas en un único payload diagnóstico.
- reversibilidad: Puede cambiar representación con migración que conserve diagnóstico y trazabilidad.

### DD-005 — Human review CONFIRMED/CORRECTED/REJECTED

- id: DD-005
- contexto: La IA antigua mezclaba rechazo con causa alternativa; el prompt y Human-in-the-Loop distinguen tres decisiones.
- decisión: CONFIRMED acepta; CORRECTED requiere causa corregida no vacía; REJECTED rechaza sin alternativa validada. PENDING se deriva de ausencia de revisión. Mapping contractual: diagnostic_id → diagnoses.id, reviewer → reviewer_ref, decision → decision, timestamp → timestamp, correlationId → correlation_id. actual_cause/comment son opcionales salvo la semántica CORRECTED.
- fuentes: Prompt aprobado §6.E; SRC_ADR_011; SRC_ADR_016; INV-006.
- impacto: No se persiste ValidationStatus ni PENDING. Se permite historial de revisiones sin imponer una decisión final de cardinalidad adicional. REJECTED con causa alternativa validada debe registrarse como CORRECTED.
- reversibilidad: Cambiar enum o cardinalidad exige decisión funcional y migración; la IA histórica se conserva.

### DD-006 — Blob por referencia, no contenido grande en PostgreSQL

Nota de evolución: representación histórica de Blob sustituida parcialmente por ADR-019 y DD-018 para el MVP; se conserva el texto original como trazabilidad.

- id: DD-006
- contexto: Los logs extensos viven en Azure Blob Storage; el diagnóstico debe conservar evidencia sustentante.
- decisión: evidence_items almacena metadata, summary y excerpt normalizados. storage_container/blob_object_key se informan juntos cuando existen. diagnosis_evidence_links identifica evidencia sustentante por ID lógico. No se guardan SAS, secretos, credenciales ni payload sensible crudo.
- fuentes: Prompt aprobado §6.F-G; architecture.yml#object_evidence_store; INV-001; INV-002; SRC_ADR_013.
- impacto: Permite recuperar el objeto externo con controles existentes; el hash no fija algoritmo. El saneamiento de contenido corresponde a aplicación.
- reversibilidad: Puede evolucionar la localización externa mediante migración de referencias sin duplicar logs en la base.

### DD-007 — diagnosis_source_links para trazabilidad RAG

- id: DD-007
- contexto: consulted_sources debe ser reconstruible por versión.
- decisión: diagnosis_source_links apunta lógicamente a knowledge_chunks; su FK intra-schema conduce a knowledge_documents. Documentos y chunks exigen provenance. Corpus limitado a reviewed_incidents, authorized_technical_documentation y authorized_response_procedures.
- fuentes: Prompt aprobado §6.H-I; architecture.yml#rag_retrieval; diagnostic_output; INV-010.
- impacto: No se incluyen casos de evaluación ni soluciones de referencia en knowledge. Elegibilidad del corpus se verifica en aplicación; texto/provenance no puede validarse semánticamente por una FK.
- reversibilidad: Puede añadirse otra estrategia de provenance mediante decisión posterior conservando la traza existente.

### DD-008 — Cross-schema logical references, sin FK física

- id: DD-008
- contexto: Una instancia compartida no implica ownership compartido ni acoplamiento entre contextos.
- decisión: Todas las referencias cross-schema son logical_ref. DBML no emite Ref ni SQL FOREIGN KEY para ellas. Se permite FK física intra-schema. No hay navegación JPA/ORM cross-context; referencias se resuelven por contratos existentes.
- fuentes: Prompt aprobado §10; SRC_ADR_018.
- impacto: La base no garantiza existencia de IDs remotos; cada owner valida referencias por APIs/eventos de architecture.yml. No se diseñan nuevas relaciones de comunicación.
- reversibilidad: Reversible: una futura decisión Accepted y migraciones podrían introducir FK cross-schema; nunca implícitamente.

### DD-009 — Vector sin dimensión fija

- id: DD-009
- contexto: Azure OpenAI Embeddings está aprobado, pero el modelo concreto no se ha fijado.
- decisión: knowledge_chunks.embedding usa vector sin dimensión. Se genera CREATE EXTENSION IF NOT EXISTS vector. embedding_dimension: null sigue en open_questions. chunk_index se supone base cero; embedding puede quedar null durante carga.
- fuentes: Prompt aprobado §6.I; SRC_ADR_007; DQ-003.
- impacto: No hay vector(1536), índice vectorial dependiente de dimensión ni mecanismo de actualización seleccionado.
- reversibilidad: Una futura elección de embedding requiere decisión y migración de tipo/datos/índices.

### DD-022 — Alcance e importaciÃ³n administrativa del corpus RAG

- id: DD-022
- contexto: El 16/11/2026 el usuario aprobÃ³ el contrato Recommendation → RAG v1 con identidades GitHub canÃ³nicas, alcance verificado por Recommendation y defensa adicional en RAG, ademÃ¡s de un importador administrativo idempotente sin API pÃºblica ni aprendizaje automÃ¡tico.
- decisiÃ³n: knowledge_documents conserva tenant, instalaciÃ³n, repositorio, pipeline opcional y revisiÃ³n de scope. La carga exige source_id/source_version, hash canÃ³nico, provenance y referencia de autorizaciÃ³n; una versiÃ³n activa sustituye a la anterior. Los casos de evaluaciÃ³n se rechazan. Azure OpenAI permanece simulado hasta aprobar modelo, dimensiÃ³n, deployment, regiÃ³n y permisos.
- fuentes: AprobaciÃ³n explÃ­cita del usuario del 16/11/2026; architecture.yml#rel_recommendation_rag; INV-010; DD-007/DD-009.
- impacto: Recommendation entrega scope previamente verificado y RAG vuelve a filtrar. No se crea relaciÃ³n nueva, crawler, API pÃºblica ni acceso a tablas ajenas.
- reversibilidad: Nuevas fuentes o mecanismos requieren decisiÃ³n posterior; las versiones y hashes preservan procedencia para migraciÃ³n controlada.

### DD-010 — Confidence sin escala cerrada

- id: DD-010
- contexto: La IA muestra un ejemplo numérico que no fija escala de persistencia.
- decisión: confidence JSONB nullable conserva valor o estructura recibidos; no tiene CHECK de rango ni escala numérica cerrada. La representación física es una suposición reversible, no la resolución de DQ-002.
- fuentes: Prompt aprobado §6.C; arquitectura-informacion.md#Confidence; DQ-002.
- impacto: No impone 0..1; consultas interpretan el valor solo conforme a un contrato posterior aprobado.
- reversibilidad: Puede migrarse a un tipo más específico cuando se aprueben escala y semántica.

### DD-011 — CQRS lógico, sin Event Sourcing

- id: DD-011
- contexto: Se aprueba separar commands y queries en aplicación manteniendo persistencia común.
- decisión: Command → Handler/Service → Domain → Repository → PostgreSQL. Query → Handler/Service → Query Repository/Projection → PostgreSQL. Sin Event Sourcing ni Event Store, sin bases físicas de lectura/escritura.
- fuentes: Prompt aprobado §0.E-F; SRC_ADR_018.
- impacto: No se crean SQL views CQRS ni v_incident_queue. Historial diagnóstico y audit_events no son un Event Store.
- reversibilidad: Cambiar a separación física o Event Sourcing requiere nueva decisión arquitectónica.

### DD-012 — Ownership de datos por Bounded Context

- id: DD-012
- contexto: Se aprueban cinco schemas y repositorios independientes por microservicio.
- decisión: ops: pipeline_service; evidence_items: log_event_service; correlated_contexts: evidence_correlation_engine; diagnosis: recommendation_service; knowledge: rag_retrieval; audit: shared. Cada owner escribe solo sus tablas; compartir evidence no permite escribir las del otro servicio.
- fuentes: Prompt aprobado §0.D-G y §5; SRC_ADR_018; SRC_ADR_011.
- impacto: Schema/table ownership se valida contra containers/component parents existentes. No se crean servicios, users, teams ni roles PostgreSQL en esta iteración. Ingesta y NLP pueden mantener dominio ligero sin Aggregates artificiales.
- reversibilidad: Mover ownership requiere decisión explícita y migración; multirepo no se convierte a monorepo.

### DD-013 — Tipos, identidad y claves físicas mínimas

- id: DD-013
- contexto: El prompt aprueba conceptos, pero no concreta todos los tipos y claves físicas.
- decisión: UUID de servicio para PK, text para IDs externos y correlation_id, timestamptz para tiempos, boolean para marcado crítico/fallo, bigint para secuencia/tamaño. Claves compuestas previenen duplicación de workflows, intentos, etapas, chunks y vínculos. Severity y PipelineCriticality son enums distintos. PipelineStage reutilizado se materializa como enum local en cada schema para evitar dependencia física de tipos.
- fuentes: Prompt aprobado §6 y §8; SRC_ADR_018; A-001/A-002/A-003/A-004/A-009.
- impacto: No se fijan versiones Java/Spring/Python ni algoritmo UUID/hash. Solo se genera SQL con tipos PostgreSQL y constraints simples expresables en DBML. No hay taxonomía de log levels interna nueva.
- reversibilidad: Tipos y claves pueden revisarse con migración; identidad y alcance de entidades requieren aprobación explícita.

### DD-014 — Contexto correlacionado mínimo y ownership de evidencia

- id: DD-014
- contexto: Se requiere persistir contexto sin añadir una tabla de asociación no aprobada ni permitir escritura de evidencia ajena.
- decisión: correlated_contexts guarda incident_id/execution_id lógicos, evidence_ids UUID[] lógicos, summary y correlation_id. La colección conserva provenance operacional por los IDs de evidence_items. No se agrega payload crudo ni contexto sensible JSON.
- fuentes: architecture.yml#evidence_correlation_engine; SRC_ADR_015; Prompt §5; A-006.
- impacto: FK de arrays no se generan; aplicación valida referencias y evita fusionar ejecuciones no relacionadas. En ER toda referencia lógica es discontinua, incluida esta relación intra-schema entre owners.
- reversibilidad: Una relación normalizada exigiría aprobación para una tabla adicional y migración; colección es reversible.

### DD-015 — Retención y tiempos sin métricas duplicadas

- id: DD-015
- contexto: ADR-013 define 365 días para logs, diagnósticos y evidencias; TMD se deriva de timestamps.
- decisión: created_at permite retención de evidence_items, correlated_contexts, diagnoses, recommendations y vínculos/revisiones diagnósticas dependientes. detected_at/remediation_started_at/verification_started_at/resolved_at están en incidents; diagnosis_ready_at está en cada versión diagnóstica. TMD = diagnosis_ready_at − detected_at; MTTR puede calcularse secundariamente.
- fuentes: SRC_ADR_013; INV-009; Prompt §6.J y §12; A-002.
- impacto: No se persisten TMD/MTTR. No se extiende silenciosamente el plazo a configuración, corpus ni auditoría. Las consultas escogen la versión/periodo; no se fija una política nueva de agregación KPI. No hay purge jobs.
- reversibilidad: Cambiar retención necesita fuente corporativa/decisión; cambiar timestamps requiere migración explícita.

### DD-016 — Auditoría transversal sanitizada

- id: DD-016
- contexto: La auditoría persiste en PostgreSQL sin audit_service.
- decisión: audit_events conserva categorías exactas de architecture.yml, correlation_id, referencia externa al actor, referencia polimórfica a entidad, acción, estados JSONB opcionales y tiempos. before_state/after_state contienen exclusivamente metadata sanitizada.
- fuentes: SRC_ADR_011; architecture.yml#audit_trail; CTRL-002; Prompt §11.
- impacto: No se registran logs crudos, secretos, tokens, credenciales ni payload sensible no enmascarado. No hay FK polimórfica; saneamiento se valida en aplicación y no se presume garantizado por el tipo JSONB.
- reversibilidad: El formato sanitizado puede evolucionar con contratos aprobados; no habilita Event Sourcing.

### DD-017 — Pipeline access grants IA-only/inferred

- id: DD-017
- contexto: Las capacidades VIEW/OPERATE/CONFIGURE derivan principalmente de arquitectura de información.
- decisión: pipeline_access_grants conserva scope_basis: ia_only y status: inferred; referencia principal Entra ID sin users/roles internos. Es representación provisional, no implementación final RBAC ni requisito core.
- fuentes: arquitectura-informacion.md; SRC_ADR_003; Prompt §7; DQ-005/DQ-006.
- impacto: Se muestra con borde punteado y etiqueta IA-only / inferred; la política de alta de workflows y RBAC seguían abiertas en este corte. DD-019/ADR-020 aprueban después la política MVP; representación física y contratos pendientes conservan su estado.
- reversibilidad: Puede retirarse o cambiarse cuando se apruebe implementación definitiva; nunca promoverla automáticamente.

### DD-018 — Evidencia MVP sin almacenamiento Blob de workload

- fuente y autoridad: ADR-019, Accepted por confirmación explícita del usuario en la reconciliación local de 06/11/2026.
- decisión: evidencia saneada y metadata permanecen en evidence_items; los logs originales se obtienen de GitHub Actions. Se retiran storage_container/blob_object_key y su CHECK conjunto. No se introduce otro formato de localizador, copia completa de logs ni mecanismo de recuperación.
- impacto: DBML/SQL/diccionario se regeneran desde domain.yml; no se ejecuta migración sobre una base existente. Size/hash y referencias lógicas conservan su semántica. Ownership, saneamiento y trazabilidad siguen vigentes.
- pendiente: retención independiente de logs originales, pérdida de acceso/borrado en GitHub y recuperación permanecen en PD-017/030/031; la exclusión no reduce ni demuestra los 365 días de ADR-013.
- reversibilidad: cualquier consumidor existente necesita evaluación de migración y contrato; reincorporar Blob requiere una nueva decisión explícita. El backend Blob de state Terraform no es almacenamiento de workload.

### DD-019 — Alta verificada y capacidades condicionadas al acceso GitHub

- autoridad: confirmación explícita del usuario del 06/11/2026, registrada en [ADR-020](../docs/architecture/decisions/ADR-020-github-user-access-and-workflow-onboarding.md).
- decisión: Pipeline crea/reutiliza Repository y registra Pipeline con datos GitHub verificados por el conector de Ingestion. Grants AIOps no conceden acceso fuera del alcance GitHub vigente; VIEW/OPERATE requieren lectura y CONFIGURE/alta administración efectiva. CONFIGURE incluye VIEW, no OPERATE. El creador recibe CONFIGURE con auditoría atómica; un duplicado no concede grants.
- impacto: complementa DD-001/DD-017 y acota DQ-005/006 a detalles pendientes. Se conserva pipeline_access_grants como ia_only/inferred; no se aprueban columnas, tablas, users/roles/teams, pipeline owners ni asociaciones ORM nuevas. Credenciales/vinculaciones pertenecen lógicamente a Ingestion, nunca a ops ni a audit; su schema y custodia siguen pendientes.
- límites: las APIs humanas de evidencia y diagnóstico requieren contrato para aplicar la restricción sin accesos cross-context. No hay grants automáticos por rol GitHub ni reescritura de IDs/filas históricas. Política aprobada no equivale a implementación ni modifica la retención.


<a id="DD-020"></a>

### DD-020 — Metadata física y custodia del conector GitHub

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

### DD-021 — Captura/publicación durable — capture-publication-draft-0.1

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

## Assumptions

- **A-001** (assumption): UUID asignados por cada servicio; no default ni extensión generadora de UUID.
- **A-002** (assumption): Tiempos en timestamptz; created_at asignado por el owner. diagnosis_ready_at pertenece a cada versión; no se duplica en ops.incidents ni se almacena TMD.
- **A-003** (assumption): IDs externos GitHub como text, run_attempt positivo; claves únicas por repositorio/workflow y pipeline/run/attempt.
- **A-004** (assumption): failed representa el fallo ya identificado por GitHub Actions; no fija un algoritmo nuevo de detección ni una taxonomía interna de resultados.
- **A-005** (assumption): Severity nullable mientras no exista regla aprobada de derivación; no derivar de criticality ni de log level.
- **A-006** (assumption): correlated_contexts conserva evidence_ids UUID[] como referencias lógicas al owner log_event_service; validación y saneamiento en aplicación, sin tabla de asociación adicional.
- **A-007** (assumption): probable_cause nullable para snapshots ANALYZING/INCONCLUSIVE; DIAGNOSIS_READY exige causa probable y diagnosis_ready_at. Cambiar estado añade una versión inmutable.
- **A-008** (assumption): confidence JSONB nullable conserva el valor recibido sin fijar escala, unidad ni representación numérica obligatoria.
- **A-009** (assumption): chunk_index empieza en cero y es único por documento; embedding nullable durante carga, sin resolver mecanismo de actualización.
- **A-010** (assumption): El corpus elegible y las referencias lógicas son verificados por los owners en aplicación; constraints estructurales no pueden detectar texto de evaluación ni datos sensibles dentro de texto/JSON.
- **A-011** (assumption): No hay originales Charter/TI/drift en el checkout; las referencias a alcance provienen del modelo canónico vigente y del prompt aprobado, sin atribuir nuevos requisitos literales al Charter.
- **A-012** (assumption): Sin cardinalidad final adicional para revisiones: se admite historial de human_reviews por versión; la ausencia implica PENDING y no se agrega enum persistido de validación.

## Open Questions

- **DQ-001 / incident_severity_derivation** (open_question): Regla concreta de derivación de severidad del incidente.
- **DQ-002 / confidence_semantics** (open_question): Escala y semántica exacta de confidence.
- **DQ-003 / embedding_dimension** (open_question): Dimensión del embedding; el modelo concreto sigue sin fijarse. `embedding_dimension: null`.
- **DQ-005 / pipeline_rbac** (open_question): ADR-020 aprueba la política MVP de capacidades condicionadas al acceso GitHub. Pendientes representación física definitiva, recuperación de acceso y contratos de autorización; no reabrir la política ni promover grants inferred automáticamente.
- **DQ-006 / monitored_workflow_registration** (open_question): ADR-020 aprueba el alta con administración GitHub verificada y creación/reutilización de Repository por Pipeline. Pendientes contrato REST versionado, custodia y esquema técnico del conector; la política funcional MVP ya está aprobada.

## IA-only / inferred

- `ops.pipeline_access_grants`: ia_only / inferred. Representación provisional de capacidades por pipeline; no requisito core ni implementación definitiva RBAC. Fuentes: docs/research/arquitectura-informacion.md, SRC_ADR_003, DD-017.
