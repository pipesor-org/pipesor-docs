**Informe de investigación — Etapa 5: contratos de consumo para backend e IaC**

**Resultado:** existe una base arquitectónica suficiente para iniciar trabajo acotado en repositorios independientes, pero todavía no un conjunto completo de contratos que permita integrar y desplegar el MVP sin decisiones adicionales. Los bloqueos afectan fronteras concretas; no justifican detener todo el desarrollo.

La investigación se limita a `pipesor-org/pipesor-docs`, rama `feature/architecture-refinement`, fijada en la revisión [`7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e`](https://github.com/pipesor-org/pipesor-docs/commit/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e). Se consultaron los modelos declarativos, los 18 ADRs, el Charter v1.3, el drift y los registros de reconciliación y pendientes.

No se modificaron archivos ni se crearon ramas, worktrees, commits o PRs. No se ejecutaron generadores ni pruebas de implementación. El checkout local correspondía a una revisión anterior; las conclusiones utilizan la revisión remota indicada. **No se presupone completada la etapa 4.**

**Actualización documental local — etapa 5.** Informe de Codex Cloud aportado por el usuario; fecha y versión originales no declaradas. Se conserva la revisión original `7c0bd1f` y sus enlaces. La revisión de contraste local es `c0871ac9a62bad62b8c679255fe0a4b9c6574d2e`, con la etapa 4 y su corrección WSL2 ya integradas mediante los PRs #1 y #3. Los modelos normativos, las DD/DC, los 18 ADRs y el registro de pendientes no presentan cambios entre esas revisiones; las conclusiones de contratos siguen siendo aplicables.

Las comprobaciones registradas en la sesión WSL2 anterior fueron: `make validate_design`, 98 pruebas, `make all`, seis pruebas PostgreSQL 16.15/pgvector 0.8.7 y `make verify-artifacts` (34 artefactos vigentes y 53 salidas reproducibles en ese perfil). Son evidencia histórica de herramientas, no pruebas ejecutadas durante esta revisión ni acreditación de contratos implementados. El [perfil de reproducibilidad](../development/reproducibility.md) conserva los límites entre Cloud y WSL2. La reserva sobre etapa 4 del párrafo anterior describe el momento de la investigación original.

La [ampliación del registro de pendientes](pending-decisions.md#ampliación-de-etapa-5-contratos-de-consumo) identifica las brechas nuevas y sus criterios documentales de cierre. El usuario identificó a los CODEOWNERS **Jhon Galvez y Ramiro Guzman** como autoridad para aprobar los contratos de eventos, APIs, acceso del workflow y coordinación backend–IaC. Esta indicación no aprueba contratos concretos ni acredita una configuración de CODEOWNERS o una regla de revisiones en GitHub.

**Contraste posterior con el remoto del 06/11/2026.** La [reconciliación entre repositorios](cross-repository-reconciliation.md), incorporada en `f02f7cf8b902be80a07e4653d8389fef50e815d0` (PR #4), registra evidencia de IaC y consumidores posterior al baseline de este informe. Identifica este informe y el registro ampliado por hashes que coinciden exactamente con los archivos locales previos a la presente integración. Su recuperación no acredita aprobación de contratos.

Las afirmaciones originales sobre APIM y Blob describen el modelo canónico todavía sin modificar: IaC registra native ingress sin APIM (XR-001) y exclusión de Blob de workload (XR-002), con reconciliación model-first pendiente. Por ello, las filas APIM y PD-036 no se usan como instrucción de aprovisionar un gateway. IaC también aporta Terraform, fundaciones Foundry/PostgreSQL/SWA y preparación dev-only (XR-003/005); ya no corresponde tratar todo su inventario o configuración como inexistente. Eso no demuestra recursos desplegados ni cierra modelos/deployments AI, contratos runtime o readiness de servicios. Las brechas y prioridades de este informe se aplican junto con XR-001–008, preservando ambas revisiones y sin elegir automáticamente entre decisiones contradictorias.

**Evolución aprobada posterior — ADR-019.** Tras el contraste remoto, el usuario confirmó alinear native ingress sin APIM, exclusión de Blob de workload, fundación Foundry y preparación dev-only. [ADR-019](decisions/ADR-019-align-mvp-with-iac.md) incorpora esa dirección en el modelo. Las menciones originales de APIM/Blob de este informe se conservan como antecedente: ya no prescriben el MVP activo. PD-034/036 describen APIs y acceso del workflow por ingress nativo; no se cierra su contrato. Se mantienen los bloqueos de acceso, modelos AI, corpus, entrega y garantías de evidencia; la base Terraform no autoriza despliegue.

**1. Fuentes de autoridad y estado de las decisiones**

La autoridad es **por materia**, conforme a ADR-018 y `AGENTS.md`; no corresponde imponer una precedencia lineal nueva.

| Materia | Fuente que deben consumir backend e IaC | Alcance y límites |
|---|---|---|
| Objetivos, alcance, exclusiones y evaluación | Project Charter v1.3 | Define el problema y los entregables; no selecciona por sí solo todo el stack físico. |
| Arquitectura, componentes y comunicaciones | `model/architecture.yml`, invariantes y ADRs `Accepted` aplicables | Los ADRs históricos deben leerse con sus sustituciones parciales. |
| Tecnología | Drift y ADRs tecnológicos aplicables | El drift aislado conserva decisiones históricas que ya no rigen el MVP. |
| Persistencia y ownership | `model/domain.yml`, explicado por `model/domain_decisions.md`, dentro de ADR-018 | Preserva supuestos y preguntas abiertas. |
| Diseño interno del servicio diagnóstico | `model/design.yml` y `model/design_decisions.md` | Las clases siguen siendo `proposed`; no equivalen a contratos aprobados. |
| Necesidades funcionales derivadas | `docs/research/arquitectura-informacion.md` | Su API v0.1 es una propuesta; no aprueba endpoints ni DTOs. |
| Vigencia, discrepancias y pendientes | Índice de ADRs, reconciliación y `pending-decisions.md` | Son registros descriptivos; no cierran preguntas ni sustituyen documentos propietarios. |
| Diagramas y artefactos de datos | Modelos de presentación, DBML y salidas generadas | Son proyecciones o derivados; no autoridades arquitectónicas independientes. |

Referencias verificables:

- [Gobernanza y reglas para consumidores: AGENTS.md](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/AGENTS.md).
- [Índice de los 18 ADRs y sustituciones explícitas](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/docs/architecture/decisions/index.md).
- [Procedencia, hashes y enlaces al Charter y drift](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/docs/sources/README.md).
- [Reconciliación de las 50 resoluciones del drift](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/docs/architecture/reconciliation.md).
- [Registro agregado de 32 pendientes](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/docs/architecture/pending-decisions.md).

Los estados deben conservarse: `confirmed` significa confirmado en el modelo, no implementado; la arquitectura global sigue `draft`. Los 18 ADRs declaran `Accepted`, aunque falta evidencia independiente de sus actos individuales de aprobación. Esa carencia no autoriza a cambiar sus estados ni a reabrir sus selecciones.

**2. Matriz de contratos por repositorio consumidor**

“Backend” comprende varios repositorios: ADR-018 establece uno por microservicio desplegable. La distribución siguiente expresa responsabilidades existentes, sin proponer nombres de repositorios.

| Consumidor | Responsabilidad y límites vigentes | Dependencias y contratos consumidos | Preparación |
|---|---|---|---|
| `ingestion_normalization_service` | Java/Spring Boot. Captura autorizada, normalización, protección de datos y asignación de `correlationId`. Sin Privacy Gateway separado. | Webhooks/API de GitHub Actions; fuentes autorizadas de observabilidad; publicación de evidencia protegida en Service Bus. | Frontera clara; falta precisar contrato de eventos, seguridad operativa y credenciales. |
| `pipeline_service` | Java/Spring Boot. Workflows monitorizados, ejecuciones, etapas, estados e incidentes; propietario de `ops`. | Suscripción de Service Bus, PostgreSQL y consultas vía APIM. | Dominio base utilizable; alta de workflows y RBAC granular siguen abiertos. |
| `log_event_service` | Java/Spring Boot. Registro y consulta de evidencia normalizada; propietario de `evidence.evidence_items`. | Service Bus, PostgreSQL, Blob y consultas vía APIM. | Ownership claro; faltan interoperabilidad del evento y condiciones de acceso al almacenamiento. |
| `nlp_log_processor` | Python/FastAPI. Procesamiento semántico y parsing con Drain3. Sin detector propio. | Service Bus; Azure OpenAI Embeddings; entrega síncrona REST/HTTPS a correlación. | Puede comenzar procesamiento acotado; embeddings y contrato de salida requieren precisión. |
| `evidence_correlation_engine` | Java/Spring Boot. Correlación conservando procedencia y separación de ejecuciones; propietario de `evidence.correlated_contexts`. | Entrada síncrona desde NLP, PostgreSQL y entrega síncrona al servicio diagnóstico. | Frontera clara; falta resolver intercambio de IDs, disponibilidad de referencias y contrato de contexto. |
| `recommendation_service` | Java/Spring Boot. Orquesta diagnóstico, produce `diagnostic_output` y conserva revisión humana; propietario de `diagnosis`. | Correlación, RAG, Azure OpenAI por API, PostgreSQL y APIM. | Puede comenzar dominio interno; recepción, proyección de consulta y políticas requieren cierre. |
| `rag_retrieval` | Python/FastAPI. Recupera conocimiento autorizado y conserva provenance; propietario de `knowledge`. | Solicitudes del servicio diagnóstico y PostgreSQL/pgvector. | Frontera clara; recuperación real depende de embeddings, corpus y mecanismo de carga. |
| IaC | Materializa hosting y capacidades físicas declaradas, preservando fronteras, accesos y ownership. | Container Apps, APIM, PostgreSQL/pgvector, Blob, Service Bus, Monitor/Application Insights y configuración de integraciones. Static Web Apps cuando corresponda al alcance del repositorio. | Inventario tecnológico suficiente; faltan contratos operativos para un despliegue integrado. |

La separación entre backend e IaC tampoco está totalmente definida en aspectos como ejecución de migraciones, configuración compartida y promoción de versiones. No debe atribuirse automáticamente a IaC la propiedad del esquema funcional ni al backend la selección de infraestructura.

Fuentes: [modelo arquitectónico](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/model/architecture.yml), claves `elements`, `relationships`, `deployment`; y [ADR-018](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/docs/architecture/decisions/ADR-018-application-architecture-ddd-cqrs.md), sección `Decision`.

**3. Contratos suficientemente definidos**

**Integración y ejecución.** Está definido el recorrido arquitectónico:

GitHub Actions → ingesta y protección → Service Bus → consumidores Pipeline, Log/Event y NLP. Desde NLP continúa el flujo síncrono hacia correlación → servicio diagnóstico → RAG e inferencia LLM.

El modelo declara un topic y tres suscripciones. La aprobación exacta de esa topología no está trazada, según PD-015; esto no permite sustituirla por otra.

ADR-015 fija la orquestación en `recommendation_service`. ADR-017 establece cuatro componentes internos: API, orquestador, compositor de salida y Human Review. No son cuatro microservicios.

**Datos y persistencia.** ADR-018 y el modelo de dominio fijan:

- Una instancia física PostgreSQL con pgvector, sin bases separadas de lectura y escritura.
- Ownership por schema y tabla; compartir `evidence` no permite escritura entre propietarios.
- Referencias cross-schema mediante IDs lógicos, sin FK PostgreSQL ni navegación ORM entre contextos.
- CQRS lógico, sin Event Sourcing ni Event Store.
- Diagnósticos versionados e inmutables; la versión actual es la mayor.
- Un incidente con exactamente un origen fallido y posibles ejecuciones de verificación.
- Evidencia extensa en almacenamiento de objetos; PostgreSQL conserva metadatos y referencias.
- Revisión `CONFIRMED`, `CORRECTED` o `REJECTED`; `CORRECTED` exige causa corregida. `PENDING` deriva de ausencia de revisión.

Estas reglas son consumibles, preservando los supuestos físicos documentados y la evidencia pendiente de los prompts citados en las DD. Fuente: [modelo de dominio](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/model/domain.yml) y [DD-001–017](https://github.com/pipesor-org/pipesor-docs/blob/7c0bd1f9eaa47d6e48e5bffb8c1a5d5b49fb405e/model/domain_decisions.md).

**Salida diagnóstica.** `recommendation_service.diagnostic_output` identifica: incidente, contexto de ejecución, resumen del fallo, causa probable, evidencia sustentante, fuentes consultadas, recomendaciones, limitaciones y confianza. Es suficiente como contrato semántico; todavía no como especificación completa de intercambio.

**Seguridad y gobierno.**

- INV-001/002 y CTRL-002 exigen protección previa a NLP/RAG/LLM; el LLM no recibe logs crudos.
- GitHub App read-only con installation tokens y mínimo privilegio.
- Dashboard autenticado mediante Entra ID; consumo por APIM hacia Pipeline, Log/Event y Diagnostic.
- Auditoría funcional transversal en PostgreSQL, separada de observabilidad técnica.
- Revisión humana con identificador diagnóstico, revisor, decisión, tiempo y correlación.
- Corpus autorizado, con procedencia y separado de evaluación.
- Retención de 365 días para logs, diagnósticos y evidencias; no se extiende implícitamente a configuración, corpus o auditoría.

**Despliegue y consumo.** Los siete servicios backend vigentes utilizan Container Apps. APIM es infraestructura gestionada; Entra ID es proveedor externo y Azure OpenAI es servicio externo por API, sin hosting propio.

ADR-016 define que GitHub Actions consulta el diagnóstico mediante APIM y publica el artifact con un paso nativo. El prototipo no obtiene permisos de escritura para subirlo.

**4. Brechas que requieren precisión**

Las siguientes son necesidades de contrato detectadas por esta investigación. Las que no tienen ID PD propio no se presentan como nuevas decisiones aprobadas.

| Brecha | Evidencia | Precisión necesaria antes de implementar la parte afectada |
|---|---|---|
| PD-033 — Evento normalizado y entrega asíncrona | `canonical_event_context`, relaciones de Service Bus | Estructura intercambiable, identidad, compatibilidad de versiones y tratamiento acordado de duplicación, fallos y reentrega. El contexto conceptual no define todo el mensaje. |
| PD-031 — Disponibilidad e identidad entre consumidores | Tres suscripciones independientes; DD-008/014; PD-031 | Cómo se obtienen y validan IDs de incidente, ejecución y evidencia, y qué sucede cuando aún no existen. No está garantizado que Pipeline/Log hayan persistido antes de continuar NLP. |
| PD-034 — Contratos REST internos y públicos | Relaciones REST/HTTPS; PD-010 | Forma final de recepción y respuesta, errores y comportamiento de integración. Las firmas propuestas no resuelven el contrato. |
| Reconstrucción de consultas diagnósticas | PD-011/DCQ-003 | Fuente de `executionContext` y `failureSummary`, dentro de comunicaciones y ownership existentes. |
| Semántica de confianza | PD-004/DQ-002 | Escala, significado y representación para API, inferencia y visualización. JSONB no aprueba una escala 0–1. |
| Embeddings y corpus | PD-005/006/023 | Modelo, dimensión, carga/actualización, autorización y separación efectiva de evaluación. |
| Autorización y alta de workflows | PD-007/008 | Política final. `pipeline_access_grants` sigue `ia_only`/`inferred`; no constituye RBAC aprobado. |
| Clasificación de riesgo | PD-009 | Política y criterios para recomendaciones críticas. No equivale a severidad del incidente. |
| PD-036 — Credenciales y acceso entre actores | PD-027; ADR-005/016 | Mecanismo autorizado de secretos y contratos de acceso, incluido workflow → APIM. La identidad del usuario del dashboard no resuelve la del workflow. |
| PD-035 — Entrega backend–IaC | `deployment`; ADR-001/018 | Artefacto desplegable, configuración requerida, accesos, disponibilidad, migraciones y compatibilidad entre versiones. No están especificados integralmente. |
| Retención operativa | PD-030; DD-003/015 | Aplicación de los 365 días compatible con snapshots inmutables, vínculos y evidencias. Las fuentes consultadas no definen un procedimiento operativo de purga. |
| Artifact | PD-028 | Formato y coordinación entre consulta y publicación. El flujo de responsabilidades sí está definido. |

PD-034 cubre la especificación de intercambios REST usados; PD-010 conserva el pendiente específico de recepción del contexto correlacionado y PD-011 el de reconstrucción de consultas. PD-036 cubre identidad/autorización del workflow ante APIM; PD-027 conserva almacenamiento de secretos. La coordinación de disponibilidad de IDs se sigue en PD-031, sin abrir otra entrada. Los criterios de cierre y dependencias se mantienen en el registro central; esta matriz no los sustituye.

No se identificó una selección de herramienta IaC en las fuentes revisadas. Tampoco corresponde inferir SKU, red, región, escalado o mecanismos de secretos a partir del nombre de un servicio Azure. Debe precisarse únicamente lo requerido para el siguiente incremento autorizado.

**5. Priorización y dependencias de cierre**

Esta clasificación es una evaluación de preparación, no un cambio de estado de los pendientes.

| Prioridad y momento | Asuntos | Dependencia y recomendación de cierre |
|---|---|---|
| **Bloqueante para integrar el flujo** | Evento normalizado, IDs/referencias, recepción diagnóstica PD-010 y contratos REST utilizados | Acordar productor y consumidores sobre las relaciones existentes. No resolver carencias con nuevas comunicaciones, acceso directo a tablas ajenas o componentes adicionales. |
| **Bloqueante para acceso real** | Autorización aplicable, identidad workflow → APIM y secretos PD-027 | Documentar política y mecanismo autorizado antes de conectar credenciales y evidencia real. No seleccionar Key Vault por inferencia: ADR-005 lo deja expresamente sin definir. |
| **Bloqueante para embeddings/RAG reales** | PD-005/006/023 | Fijar modelo y dimensión antes de generar vectores o índices dependientes; disponer de corpus autorizado antes de cargarlo. |
| **Bloqueante para inferencia real** | Variante LLM PD-026 y contrato de respuesta utilizable | Obtener selección explícita; conservar proveedor, familia y modo API existentes. ADR-004 prohíbe fijar aún una variante por iniciativa del implementador. |
| **Bloqueante para funciones concretas** | PD-007/008 para autorización/alta; PD-009 para clasificación de riesgo; PD-011 para consulta completa | Cerrar cada contrato antes de entregar esa función como terminada; no impide trabajo independiente en otros dominios. |
| **Bloqueante para despliegue integrado** | Contrato backend–IaC, configuración, accesos y migraciones | Delimitar responsabilidades y entradas/salidas necesarias para desplegar versiones compatibles. |
| **Antes de operar datos sujetos a conservación** | PD-030, respaldado por PD-017 | Precisar ejecución de retención sin contradecir inmutabilidad ni ampliar el plazo a otras categorías. |
| **Antes de evaluación comparativa** | PD-001/021/022/023 | Protocolo, rúbrica, corpus y trazabilidad de mediciones; no bloquean el inicio general del backend. |

Pueden resolverse durante el desarrollo, antes de su uso correspondiente:

- **Severidad, PD-003:** puede permanecer nullable; no derivarla de criticality o nivel de log.
- **Confianza, PD-004:** no impide conservar un valor opaco nullable; sí impide interpretarlo o fijar umbrales.
- **Formato del artifact, PD-028:** puede cerrarse junto con su consumidor, antes de completar publicación.
- **Versiones y algoritmos, PD-032:** concretarlos cuando los necesite la implementación y registrar su fundamento.
- **Mantenimiento operacional, PD-029:** concretarlo antes de operar actualizaciones, sin convertirlo en entrenamiento propio.
- **Referencias desactualizadas, PD-025:** corregirlas en una tarea autorizada; no obligan a detener implementación.

Las brechas de procedencia PD-012–020 y de cobertura PD-024 requieren seguimiento, pero **no son automáticamente bloqueantes técnicos universales**. Para topología y Blob, PD-015/016, debe preservarse la selección modelada y quedar visible la evidencia faltante; no sustituirla ni presentarla como aprobación independiente acreditada.

CF-001/PD-002 permanece como discrepancia de gobernanza. No debe ejecutarse su `action_required` ni usarse para que cada agente invente su propia jerarquía.

**6. Consumo y versionado por agentes independientes**

`AGENTS.md` ya exige identificar revisión consultada, IDs relevantes, invariantes y ADRs, conservar estados y reportar contratos ausentes. Para hacerlo operativo, se recomienda:

1. **Fijar una revisión inmutable de `pipesor-docs`.** Registrar SHA y rutas relevantes; la rama móvil sirve para descubrir actualizaciones.
2. **Declarar el subconjunto consumido por servicio:** componentes, relaciones, tablas, invariantes, ADRs y preguntas que afectan al incremento.
3. **Separar versión documental y versión del contrato implementado.** `model_version` no acredita compatibilidad de una API o evento.
4. **Registrar las decisiones de implementación pendientes de aprobación.** Conservar `proposed`, `assumption`, `inferred` e `ia_only`; una copia local no cambia su autoridad.
5. **Revisar cada actualización de arquitectura por impacto:** comunicaciones, datos, permisos, configuración y migraciones.
6. **Escalar cambios de frontera al documento propietario.** Cambiar stack, ownership, separación física o comunicaciones requiere la decisión correspondiente; no se resuelve unilateralmente en un repositorio consumidor.

La investigación original no identificó aprobador verificable para muchos asuntos. La actualización local registra la autoridad indicada por el usuario para los contratos citados; las demás asignaciones siguen pendientes cuando no hay respaldo. Ser owner de implementación no otorga automáticamente autoridad arquitectónica. Cada cierre requerirá evidencia identificable de la decisión y de su aprobación.

**7. Verificaciones mínimas para detectar desviaciones**

| Verificación | Evidencia mínima esperada |
|---|---|
| Trazabilidad de revisión | SHA documental y relación entre incremento, IDs, ADRs y pendientes aplicables. |
| Inventario y fronteras | Servicios y comunicaciones alineados con `elements`/`relationships`; componentes diagnósticos internos conservados como tales. |
| Ownership y persistencia | Migraciones y accesos sin escrituras ajenas, FK cross-schema ni navegación ORM entre contextos. |
| Invariantes del dominio | Un origen fallido consistente; snapshots inmutables y versionados; revisión humana con semántica y campos obligatorios. |
| Compatibilidad entre repositorios | Verificación productor–consumidor de los contratos acordados, incluidos duplicación, reentrega y referencias todavía no disponibles. |
| Privacidad | Evidencia sensible bloqueada antes de NLP/RAG/LLM; ausencia de secretos en payloads, auditoría y referencias Blob. |
| Perímetro y publicación | Dashboard y workflow consumen por APIM; GitHub App read-only; publicación del artifact por el workflow. |
| Corpus y trazabilidad | Procedencia/autorización verificables y separación de casos de evaluación. |
| Auditoría y observabilidad | Auditoría funcional persistida y correlacionada, diferenciada de Monitor/Application Insights. |
| Conformidad IaC | Hosting y productos vigentes, instancia PostgreSQL única con pgvector, accesos por ownership y ausencia de decisiones tecnológicas implícitas. |
| Conservación | Aplicación verificable de 365 días dentro del alcance establecido, compatible con referencias e inmutabilidad. |

Los validadores documentales del Makefile —`make validate`, `make validate-domain` y `make validate_design`— pueden comprobar coherencia de modelos en su contexto autorizado. No prueban seguridad, interoperabilidad ni comportamiento desplegado. No se ejecutaron en esta investigación.

Debe verificarse también la ausencia de capacidades excluidas: detector/LogBERT, reporting o audit como servicios, Privacy Gateway independiente, notificaciones Teams/Slack/correo, APIs directas de scanners, remediación autónoma y entrenamiento propio. Los quality gates y la evidencia indirecta de scanners mediante Actions permanecen permitidos.

**8. Evaluación explícita de preparación**

| Ámbito | Evaluación |
|---|---|
| **Backend: inicio acotado** | **Preparado con condiciones.** Stack, repositorios independientes, responsabilidades, ownership e invariantes permiten comenzar dominio y procesamiento dentro de límites conocidos. |
| **Backend: integración completa** | **Todavía no preparado.** Faltan contratos de eventos/REST, coordinación de IDs y referencias, seguridad aplicable y cierres específicos de RAG/LLM y consultas. |
| **IaC: inicio acotado** | **Preparado con condiciones.** Existe inventario físico suficiente para desarrollar las partes que no dependan de configuraciones o selecciones pendientes. |
| **IaC: despliegue integrado operable** | **Todavía no preparado.** Requiere contrato backend–IaC, accesos, secretos autorizados, migraciones y configuración concreta; conserva además las salvedades de evidencia de topología y Blob. |
| **Validación comparativa** | **No acreditada como preparada.** Faltan protocolo/rúbrica y evidencia de corpus y medición. DD-015 mide detección → versión diagnóstica; el TMD del Charter mide evidencia disponible → diagnóstico final, incluida revisión cuando corresponda. |

**Los bloqueantes reales son los contratos necesarios para el siguiente intercambio, acceso o despliegue efectivo.** No es necesario cerrar todos los pendientes para iniciar todo trabajo. Sí es necesario impedir que los agentes completen esos vacíos con decisiones propias y que declaren el MVP integrado antes de cerrar las dependencias señaladas.
