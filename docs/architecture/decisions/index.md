# Índice de decisiones por tema y evolución documental

Este índice describe la vigencia documental resultante de leer conjuntamente los 28 ADRs, el [Charter y el drift archivados](../../sources/README.md), y los modelos existentes. No aprueba decisiones, no modifica estados y no sustituye sus fuentes. ADR-001–018 declaran `Accepted` y fecha 03/10/2026; sus actos individuales no tienen evidencia independiente disponible. ADR-019 registra la confirmación explícita del usuario del 06/11/2026 para alinear las decisiones MVP con IaC. ADR-020 registra la aprobación explícita del usuario de la conexión GitHub y la política de alta/acceso. ADR-021 registra la aprobación explícita del contrato RAG–Recommendation–IaC v0.1 del 16/11/2026; no acredita despliegue ni disponibilidad Azure. ADR-022 a ADR-028 declaran `Accepted` y fechas 22–23/11/2026: identidad de plataforma, admisión y alcance de captura, inicio de sesión, modelo de diagnóstico, cola de incidentes y destinatarios de grants. ADR-022 a ADR-026 citan la decisión o aprobación del responsable del proyecto; ADR-027 y ADR-028 no citan un acto de aprobación. Tampoco acreditan despliegue. La numeración y la fecha común no bastan para inferir cronología: las relaciones siguientes se apoyan en disposiciones explícitas.

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
| [ADR-003](ADR-003-identity-api-perimeter.md#decision) | Entra ID y Azure API Management. | ADR-016 refina la representación histórica; ADR-019 conserva Entra y sustituye APIM por ingress nativo de ACA para el MVP. ADR-022 sustituye, para el MVP académico, la exigencia de tokens emitidos por Entra en las APIs HTTP de Pipesor; Entra se conserva para recursos Azure. |
| [ADR-004](ADR-004-azure-openai.md#decision) | Azure OpenAI por API, familia GPT-4. | ADR-026 fija gpt-6-luna solo para dev y la evaluación OE3-I2 y enmienda allí la restricción «familia GPT-4»; fuera de ese alcance la variante sigue sin fijar (PD-026). ADR-015 concreta sistema externo gestionado, sin hosting propio. |
| [ADR-005](ADR-005-github-app-authentication.md#decision) | GitHub App read-only con installation tokens. | ADR-020 añade tokens de usuario y conector en Ingestion; conserva installation tokens para máquina. Key Vault seleccionado localmente para PD-027 (DD-020) y usado por ADR-022 para el client secret de la App; custodia operativa pendiente. ADR-022 hace del usuario GitHub verificado la identidad humana de las APIs. ADR-016 separa consumo del prototipo y publicación nativa del workflow. |
| [ADR-006](ADR-006-dashboard-api-contract.md#decision) | Dashboard consume backend existente mediante APIM. | Lista histórica actualizada por ADR-009/011/016; ADR-019 retira el salto APIM. No restaurar reporting_service ni audit_service. |
| [ADR-007](ADR-007-log-processing-and-embeddings.md#decision) | Drain3 y Azure OpenAI Embeddings para RAG. | ADR-021 fija para RAG text-embedding-3-small/1536 y acceso v1; NLP conserva sus decisiones propias. ADR-010 retira detector, candidatura activa y OQ-001 del MVP. |
| [ADR-008](ADR-008-react-azure-static-web-apps.md#decision) | React SPA en Azure Static Web Apps. | ADR-018 concreta TypeScript; ADR-019 sustituye el acceso por APIM con ingress nativo de ACA. **Divergencia pendiente de decisión:** la IaC de dev sirve el dashboard como Container App ([`modules/workloads`](https://github.com/pipesor-org/pipesor-iac/blob/388e5a7252bd70650e6715a4e6591cb5a5f2ab7e/modules/workloads/main.tf), con la nota de que Static Web Apps no está disponible en las regiones permitidas); ningún ADR registra ese cambio de hosting. |
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
| [ADR-019](ADR-019-align-mvp-with-iac.md#decision) | Alinear el MVP controlado con las decisiones aceptadas de IaC: ingress nativo de ACA sin APIM, sin Blob de workload, fundación Microsoft Foundry y preparación dev-only. | Sustituye parcialmente el enrutamiento APIM de ADR-003/006/008/016 y la representación Blob de DD-006; ver la [sección ADR-019](#alineación-mvp-posterior--adr-019). |
| [ADR-020](ADR-020-github-user-access-and-workflow-onboarding.md#decision) | Tokens de usuario de la GitHub App, conector en Ingestion y política de alta y capacidades condicionadas al acceso GitHub. | Amplía ADR-005. ADR-022 (identidad), ADR-025 (inicio de sesión) y ADR-028 (destinatarios de grants) lo enmiendan; ver la [sección ADR-020](#conexión-github-y-acceso-de-usuario--adr-020). |
| [ADR-021](ADR-021-rag-runtime-contract-v0.1.md#decision) | Contrato RAG–Recommendation–IaC v0.1. | Fija embeddings, permisos y resiliencia; región, cuota, valores reales, corpus productivo y despliegue siguen pendientes. ADR-022 sustituye el token app-only emitido por Entra de Recommendation → RAG por un token de workload de plataforma; el rol `Rag.Query` se conserva. |
| [ADR-022](ADR-022-platform-identity-without-entra-app-registrations.md#decision) | Identidad de plataforma sin app registrations de Entra para el MVP académico. | Sustituye solo la exigencia de tokens emitidos por Entra en las APIs HTTP de Pipesor; conserva Entra para recursos Azure, la política de acceso de ADR-020 y el retorno a Entra por configuración. Ver el [contrato de identidad](../contracts/platform-identity-v1.md). |
| [ADR-023](ADR-023-capture-scope-from-registrations.md#decision) | Admisión y alcance de captura en tablas de Ingestion, alcance por workflow sincronizado por Pipeline. | Sustituye `authority.json` en runtime. ADR-024 enmienda la admisión: el administrador del repositorio también la produce; la importación del operador se conserva. |
| [ADR-024](ADR-024-repository-administrator-admission.md#decision) | Los administradores de un repositorio lo admiten al seleccionarlo en la App pipesor; reconciliación al leer y revocación de repos no listados. | Enmienda ADR-023: la admisión deja de ser solo acto del operador; la importación se conserva. |
| [ADR-025](ADR-025-open-sign-in.md#decision) | Cualquier usuario de GitHub que autorice la App puede iniciar sesión; el acceso sigue gobernado por repositorio. | Sustituye la lista de instalaciones/cuentas admitidas de ADR-020 para el inicio de sesión y completa la admisión autoservicio de ADR-024. |
| [ADR-026](ADR-026-diagnosis-model-gpt-6-luna.md#decision) | gpt-6-luna (`pipesor-dev-diagnostics-luna`) como modelo de diagnóstico de Recommendation en dev y para la evaluación OE3-I2, elegido en `dev` según el §6.2 del protocolo. | Enmienda la restricción «familia GPT-4» de ADR-004 en ese alcance; PD-026 sigue abierta para otros entornos. Desviación registrada: decisión sobre el filtro eliminatorio y el indicador automático, sin la rúbrica humana. |
| [ADR-027](ADR-027-incident-queue-read-model.md#decision) | Filtros, totales e Insights de la cola de incidentes en Pipeline, con un resumen del diagnóstico proyectado desde Recommendation (outbox transaccional y `PUT` interno idempotente). | Enmienda la unión en el navegador de la decisión D03; Recommendation sigue siendo dueña del diagnóstico y sus revisiones, y la proyección es solo de lectura. |
| [ADR-028](ADR-028-people-from-github-collaborators.md#decision) | Los candidatos a recibir grants salen de los colaboradores del repositorio en GitHub; los grants siguen siendo explícitos y un pipeline conserva siempre un `CONFIGURE`. | Enmienda ADR-020 (cómo se encuentra a quien recibe un grant y recuperación del último `CONFIGURE`); no deriva VIEW del acceso GitHub ni crea usuarios o equipos. |
| [ADR-029](ADR-029-login-consent-record.md#decision) | El inicio de sesión exige y registra en el servidor la versión de la Política de privacidad y los Términos aceptados; revocación manual y conservación mientras la persona use Pipesor más un año. | Enmienda ADR-022 y el contrato de identidad §5 (Ley 29733, D.S. 016-2024-JUS, arts. 4 y 9). |

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

Las referencias de esta tabla remiten a los ADRs enlazados arriba, sección `Decision`, salvo ADR-001, cuyo pendiente del dashboard también figura en `Consequences`. Para ADR-019 a ADR-028 la relación procede de la cabecera `Amends` cuando existe (ADR-024 a ADR-028) o de la sección indicada en la fila; ADR-022 y ADR-023 no declaran `Amends` en su cabecera. Las sustituciones son parciales: no se marca ningún ADR completo como totalmente sustituido.

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
| ADR-019 | ADR-003, ADR-006, ADR-008, ADR-016 y DD-006 | Sustitución parcial del enrutamiento APIM/perímetro y de la representación Blob de workload; complementa ADR-004/007/015 con la fundación de infraestructura (`Evolution and limits`). |
| ADR-020 | ADR-005; ADR-006, ADR-016 y ADR-019 | Amplía ADR-005 con tokens de usuario y un conector en Ingestion; amplía de forma limitada la exposición de ADR-006/016/019 (`Alcance y evolución`). |
| ADR-021 | ADR-007 | Fija para RAG `text-embedding-3-small`/1536 y su acceso al proveedor; NLP conserva sus decisiones (`Decision`). |
| ADR-022 | ADR-003, ADR-019, ADR-020 y ADR-021 | Sustituye solo la exigencia de que las APIs HTTP de Pipesor validen tokens emitidos por Entra, en el MVP académico sin app registrations; los cuatro siguen `Accepted` y Entra se conserva para recursos Azure (`Consequences`). |
| ADR-023 | Implementación de ADR-020 (`authority.json`) | Traslada la admisión y el alcance de captura a tablas de Ingestion sincronizadas por Pipeline; no declara enmienda de otro ADR (`Decision`). |
| ADR-024 | ADR-023 | Enmienda: la admisión deja de ser solo acto del operador; conserva las garantías de ADR-020 (cabecera `Amends`). |
| ADR-025 | ADR-020 y ADR-024 | Sustituye la viñeta de instalaciones/cuentas admitidas de ADR-020 y completa la admisión autoservicio de ADR-024; las comprobaciones por repositorio se conservan (cabecera `Amends`, `Decision`). |
| ADR-026 | ADR-004 | Enmienda la restricción «familia GPT-4» solo para dev y la evaluación OE3-I2; Azure OpenAI por API y la ausencia de hosting propio se conservan (cabecera `Amends`, `Consequences`). |
| ADR-027 | Decisión D03 del [MVP HTTP API v1](../contracts/mvp-http-api-v1.md) | Enmienda la unión en el navegador de *Needs validation*; conserva el ownership de ADR-018 y la autorización de ADR-020 (cabecera `Amends`). |
| ADR-028 | ADR-020 | Enmienda cómo se encuentra a quien recibe un grant y garantiza un `CONFIGURE` por pipeline; la recuperación ante pérdida de administración sigue pendiente (cabecera `Amends`, `Decision`). |

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

El texto de ADR-020 cambió después de su aceptación, según el historial de Git: el 22/11/2026 se añadió la sección «Amendment 2026-11-22: VIEW verification budget» (reutilización de una verificación `VIEW` correcta durante 30 s como máximo; los comandos siempre verifican en vivo) y se tachó la viñeta de instalaciones/cuentas admitidas con remisión a ADR-025 y ADR-024. Otras menciones a instalaciones admitidas (tabla de capacidades y fila de IaC) se conservan sin tachar y se leen junto con ADR-024 y ADR-025. ADR-022, ADR-025 y ADR-028 enmiendan después la identidad humana, el inicio de sesión y la selección de destinatarios de grants.
