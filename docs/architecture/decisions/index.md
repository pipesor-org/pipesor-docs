# Índice de decisiones por tema y evolución documental

Este índice describe la vigencia documental resultante de leer conjuntamente los 21 ADRs, el [Charter y el drift archivados](../../sources/README.md), y los modelos existentes. No aprueba decisiones, no modifica estados y no sustituye sus fuentes. ADR-001–018 declaran `Accepted` y fecha 03/10/2026; sus actos individuales no tienen evidencia independiente disponible. ADR-019 registra la confirmación explícita del usuario del 06/11/2026 para alinear las decisiones MVP con IaC. ADR-020 registra la aprobación explícita del usuario de la conexión GitHub y la política de alta/acceso. ADR-021 registra la aprobación explícita del contrato RAG–Recommendation–IaC v0.1 del 16/11/2026; no acredita despliegue ni disponibilidad Azure. La numeración y la fecha común no bastan para inferir cronología: las relaciones siguientes se apoyan en disposiciones explícitas.

El Charter determina objetivos, alcance y restricciones. El drift registra cambios frente a documentación histórica; su cabecera y §50 reconocen decisiones posteriores confirmadas. Las discrepancias TMD y CF-001 permanecen abiertas en la [reconciliación](../reconciliation.md#discrepancias-y-diferencias-de-cobertura); este índice no las dirime. Las clases de `model/design.yml` siguen propuestas.

## Decisiones por tema

El cuadro describe los ADRs **de este repositorio**. Los ADR 003/004 de
`pipesor-iac` tienen numeración y alcance propios: no son estos ADR-003/004.
El [contraste entre repositorios](../cross-repository-reconciliation.md#discrepancias-y-dependencias-que-quedan-abiertas)
registra la aceptación MVP de native ingress, la exclusión de Blob de workload,
Foundry y la preparación dev-only. [ADR-019](ADR-019-align-mvp-with-iac.md) incorpora ahora esas decisiones al modelo: sustituye parcialmente el enrutamiento APIM de ADR-003/006/008/016 y la representación Blob de DD-006. Conserva identidad, hosting, revisión humana y publicación nativa; contratos, permisos, modelos AI y recuperación/retención siguen pendientes. Los enlaces y estados históricos se preservan; las menciones de APIM/Blob en sus filas se leen como antecedentes, no instrucciones MVP vigentes.

Cada enlace de ADR identifica su sección `Decision`; los límites de la última columna deben leerse junto con esa decisión. «Vigente» se refiere al estado documentado, no a despliegue ni a ratificación independiente.

| ADR | Tema y decisión documentada | Lectura vigente y límites |
|---|---|---|
| [ADR-001](ADR-001-azure-container-apps.md#decision) | Hosting backend en Azure Container Apps. | Conservar para servicios vigentes; ADR-009/010/011 retiran reporting/detector/audit como servicios. ADR-015 concreta NLP/RAG; ADR-008 trata dashboard. |
| [ADR-002](ADR-002-azure-observability.md#decision) | Azure Monitor y Application Insights. | Observabilidad técnica; ADR-011 conserva auditoría funcional separada. Drift §36 no reabre la selección. |
| [ADR-003](ADR-003-identity-api-perimeter.md#decision) | Entra ID y Azure API Management. | ADR-016 refina la representación histórica; ADR-019 conserva Entra y sustituye APIM por ingress nativo de ACA para el MVP. |
| [ADR-004](ADR-004-azure-openai.md#decision) | Azure OpenAI por API, familia GPT-4. | Variante sin fijar. ADR-015 concreta sistema externo gestionado, sin hosting propio. |
| [ADR-005](ADR-005-github-app-authentication.md#decision) | GitHub App read-only con installation tokens. | ADR-020 añade tokens de usuario y conector en Ingestion; conserva installation tokens para máquina. Gestión de secretos sin seleccionar. ADR-016 separa consumo del prototipo y publicación nativa del workflow. |
| [ADR-006](ADR-006-dashboard-api-contract.md#decision) | Dashboard consume backend existente mediante APIM. | Lista histórica actualizada por ADR-009/011/016; ADR-019 retira el salto APIM. No restaurar reporting_service ni audit_service. |
| [ADR-007](ADR-007-log-processing-and-embeddings.md#decision) | Drain3 y Azure OpenAI Embeddings para RAG. | ADR-021 fija para RAG text-embedding-3-small/1536 y acceso v1; NLP conserva sus decisiones propias. ADR-010 retira detector, candidatura activa y OQ-001 del MVP. |
| [ADR-008](ADR-008-react-azure-static-web-apps.md#decision) | React SPA en Azure Static Web Apps. | ADR-018 concreta TypeScript; ADR-019 sustituye el acceso por APIM con ingress nativo de ACA. |
| [ADR-009](ADR-009-remove-reporting-service.md#decision) | Retirar reporting_service y conservar diagnostic_output. | ADR-016 concreta quién produce y quién publica el artifact. Formato sigue siendo detalle de implementación. |
| [ADR-010](ADR-010-remove-anomaly-detector-from-mvp.md#decision) | Retirar detector y LogBERT del MVP. | NLP → correlación síncrona. LogBERT solo como posible extensión futura; OQ-001 eliminada por la decisión. |
| [ADR-011](ADR-011-audit-trail-without-audit-service.md#decision) | Auditoría transversal en PostgreSQL, sin audit_service. | Mantener correlación y revisión humana. ADR-016 concreta Human Review; ADR-018 ownership compartido de audit. |
| [ADR-012](ADR-012-remove-notification-channels-from-mvp.md#decision) | Notificaciones fuera del MVP. | Teams, Slack y correo solo como posibles extensiones; no son integraciones opcionales activas del MVP. |
| [ADR-013](ADR-013-retention-365-days.md#decision) | 365 días para logs, diagnósticos y evidencias. | Fuente declarada: política comunicada por stakeholder, original no disponible. ADR-016/018 conservan duración y alcance. No atribuir el valor al Charter. |
| [ADR-014](ADR-014-devsecops-scanners-outside-mvp.md#decision) | Sin APIs directas de Checkmarx/Mend/Wiz en MVP. | Evidencia indirecta mediante logs, eventos y artifacts de Actions. Quality gates se conservan. |
| [ADR-015](ADR-015-diagnostic-runtime-boundaries-and-orchestration.md#decision) | Runtime NLP/RAG y orquestación diagnóstica. | NLP/RAG propios en Container Apps; LLM externo por API; recommendation_service orquesta. ADR-017 añade zoom interno. |
| [ADR-016](ADR-016-identity-api-human-review-and-artifact-flow.md#decision) | Identidad, perímetro, revisión y artifact. | ADR-019 sustituye el enrutamiento APIM por acceso directo a los servicios; conserva Human Review interno, publicación nativa, GitHub App read-only y retención. |
| [ADR-017](ADR-017-diagnostic-service-component-boundaries.md#decision) | Cuatro componentes internos del servicio diagnóstico. | Zoom C4 Level 3; no nuevos microservicios ni sustitución de relaciones canónicas entre contenedores. |
| [ADR-018](ADR-018-application-architecture-ddd-cqrs.md#decision) | Multirepo, Java/Spring Boot, Python/FastAPI, React/TypeScript, DDD y CQRS lógico. | Una instancia PostgreSQL y ownership por schema/tabla; referencias cross-schema lógicas. Sin Event Sourcing ni bases separadas de lectura/escritura. |
| [ADR-021](ADR-021-rag-runtime-contract-v0.1.md#decision) | Contrato RAG–Recommendation–IaC v0.1. | Fija embeddings, Entra, permisos y resiliencia; región, cuota, valores reales, corpus productivo y despliegue siguen pendientes. |

Otros temas no tienen un ADR específico que acredite por sí solo todas sus declaraciones:

| Tema | Localizador en las fuentes | Límite de evidencia |
|---|---|---|
| Objetivos, alcance y evaluación | Charter: «Objetivos», «Indicadores de Éxito», «Alcance», «Enfoques del trabajo», «Glosario → TMD». | Aprobación formal y correspondencia operacional TMD pendientes. |
| GitHub/Actions, ingesta y privacidad | Drift §1–4, §7–9, §22; arquitectura: github, github_actions, ingestion_normalization_service, INV-001/002/003. | No inferir nuevos conectores o controles implementados de estas declaraciones. |
| Service Bus y asincronía | Drift §14/15; arquitectura: azure_service_bus y sus relaciones. | Producto y patrón respaldados documentalmente; aprobación de topología exacta no trazada. |
| Correlación | Drift §21/22/23; arquitectura: evidence_correlation_engine; DD-014. | Preservar dimensiones e IDs, sin inferir algoritmo implementado. |
| Corpus y separación de evaluación | Charter: «Recursos de Datos y Evidencias»; drift §27/28; arquitectura: rag_retrieval, INV-010. | Corpus y aplicación de controles no acreditados como implementación. |
| Objetos y conocimiento vectorial | Drift §25/26; arquitectura: pgvector_knowledge_store; DD-006/009/018; ADR-019/021. | Blob de workload excluido por ADR-019; ADR-021 fija dimensión/modelo RAG. Recuperación/retención y corpus real siguen pendientes. |

Los localizadores de arquitectura y DD corresponden respectivamente a [architecture.yml](../../../model/architecture.yml) y [domain_decisions.md](../../../model/domain_decisions.md). El [dominio](../../../model/domain.yml) y el [diseño propuesto](../../../model/design.yml) conservan sus propias preguntas abiertas.

## Evolución inequívocamente respaldada

Las referencias de esta tabla remiten a los ADRs enlazados arriba, sección `Decision`, salvo ADR-001, cuyo pendiente del dashboard también figura en `Consequences`. Las sustituciones son parciales: no se marca ningún ADR completo como totalmente sustituido.

| Decisión | Fuente afectada | Relación y evidencia concreta |
|---|---|---|
| ADR-008 | ADR-001 | Cierra el pendiente de hosting del dashboard con Static Web Apps; no sustituye hosting backend. |
| ADR-009 | ADR-001 y ADR-006 | Sustitución parcial de hosting/consumo de reporting_service. ADR-009 declara que sustituye decisiones previas que dependan específicamente de ese servicio. |
| ADR-010 | ADR-001 y ADR-007 | Sustitución parcial: elimina detector del MVP y OQ-001. Conserva hosting de otros servicios, Drain3 y embeddings. |
| ADR-011 | ADR-001 y ADR-006 | Sustitución parcial: retira audit_service. Conserva capacidad de auditoría transversal en PostgreSQL y el principio de acceso por APIM. |
| ADR-015 | ADR-001, ADR-004 y ADR-007 | Concreta/extiende hosting NLP/RAG, LLM gestionado por API y orquestación. Declara conservar Drain3, embeddings y familia GPT-4. |
| ADR-016 | ADR-003 | Sustitución parcial de representación: retira access_and_governance_controls y separa entra_id, api_management y Human Review. Conserva selección tecnológica. |
| ADR-016 | ADR-006 | Actualiza recorrido de consumo: APIM enruta a pipeline_service, log_event_service y recommendation_service. Conserva backend existente por APIM. |
| ADR-016 | ADR-009 y ADR-011 | Concreta producción/publicación del artifact y revisión humana interna con auditoría. No elimina esas capacidades. |
| ADR-016 | ADR-013 | Aplica y corrige INV-009; declara no cambiar duración, alcance ni fuente de la política. No sustituye la retención. |
| ADR-017 | ADR-009, ADR-015 y ADR-016 | Descompone responsabilidades existentes dentro del mismo servicio; declara no sustituir relaciones entre contenedores. |
| ADR-018 | Decisiones anteriores aplicables | Complementa stack, multirepo, DDD/CQRS y persistencia conservando fronteras, relaciones e invariantes. No declara sustitución general. |

ADR-012 retira notificaciones y ADR-014 limita integraciones directas de scanners. No se identifica entre los otros ADRs una decisión que deba marcarse sustituida por ellos; su relación con el drift se documenta en la [matriz de 50 resoluciones](../reconciliation.md#matriz-de-las-50-resoluciones). ADR-002, ADR-004 y ADR-005 concretan selecciones sin justificar sustituciones completas de otros ADRs.

Las diferencias de cobertura y la evidencia de aprobación faltante están registradas [externamente](../reconciliation.md#referencias-desactualizadas-y-evidencia-pendiente). Este índice no reabre decisiones, no resuelve preguntas y no autoriza cambios de arquitectura.

## Alineación MVP posterior — ADR-019

| Decisión | Evolución y alcance vigente | Pendientes preservados |
|---|---|---|
| [ADR-019](ADR-019-align-mvp-with-iac.md) | Native ingress de ACA sin APIM; sin Blob de workload; fundación Foundry; Terraform y preparación dev-only temporal. Actualización autorizada model-first. | Exposición/auth por servicio, contratos, migraciones de consumidores existentes, modelos/grants AI, garantías de recuperación/retención y autorización de despliegue. |

La aprobación de esta dirección se documenta en ADR-019 y no reemplaza los actos individuales de aprobación de fuentes históricas. Los 365 días de ADR-013 y la separación de datos de ADR-018 permanecen. El Blob de state Terraform no se excluye.

## Conexión GitHub y acceso de usuario — ADR-020

| Decisión | Evolución y alcance vigente | Pendientes preservados |
|---|---|---|
| [ADR-020](ADR-020-github-user-access-and-workflow-onboarding.md#decision) | Amplía ADR-005 con user access tokens, componente técnico en Ingestion, conexión/descubrimiento del dashboard y verificación interna desde Pipeline. Aprueba alta y capacidades condicionadas al acceso GitHub; amplía de forma limitada ADR-006/016/019. | Contratos REST/auth, custodia, almacenamiento técnico, recuperación de acceso y entrega. Log/Event y Recommendation tienen impacto de seguridad en APIs humanas sin relaciones nuevas implícitas; correlación/Python conservan sus flujos. |

Aprobación de política en sesión del 06/11/2026; los modelos siguen draft/proposed donde corresponde y las implementaciones existentes no se declaran conformes por esta actualización. Consultar la matriz de servicios y los límites en ADR-020.
