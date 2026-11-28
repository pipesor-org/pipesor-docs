# Diagramas de despliegue

Generado desde `model/deployment_presentation.yml` con `tools/generators/deployment.py`. Hechos de `model/architecture.yml`; evidencia `repo:ruta:línea` en las revisiones fijadas en `model/implementation_status.yml`. No editar a mano.

Autorización: 2026-11-27, decisiones 1 y 7. Modelo de presentación con generador, validador y pruebas; citas a architecture.yml o a evidencia repo:ruta:línea con estado; lo implementado no modelado se marca sin añadirlo al modelo; ramas: solo lo definido y el resto TBD, sin proponer una estrategia.

Las figuras no añaden arquitectura ni aprueban un despliegue. Lo que existe en IaC o en código y no está en el modelo figura como «implementación no modelada» y no se añade a `architecture.yml`.

## Observación del 27/11

Observación del entorno `dev` el 2026-11-27T22:07Z: az containerapp list, az containerapp revision show, az containerapp job list, az postgres flexible-server show y az servicebus topic subscription list (solo lectura). En la guía se cita como «observación 27/11».

- `container_apps`: 8 Container Apps Healthy (ingestion, pipeline, log-event, nlp, correlation, recommendation, rag, dashboard), una réplica, con los digests de environments/dev/images.json.
- `jobs`: job-database-setup, job-ingestion-authority-import y job-rag-migrations (Manual).
- `postgresql`: pg-pipesor-dev-04f339b7, PostgreSQL 17, Standard_D2s_v3, detenido en el momento de la observación.
- `service_bus`: topic workflow-evidence con las suscripciones pipeline, log-event y nlp.

Evidencia de la observación: `iac:environments/dev/images.json:1-62`.

Solo esos recursos se observaron. Los demás (red, Container Apps Environment, Key Vault, Foundry, Log Analytics, identidades, GHCR) constan en IaC y van como implementados: no se volvieron a comprobar. La configuración privada de dev (tfvars) no se leyó; se cita el ejemplo versionado `environments/dev/terraform.tfvars.example`.

## Leyenda

| Trazo de nodos, grupos y aristas | Estado | Significado |
|---|---|---|
| continuo grueso | desplegado (observado el 27/11) | Desplegado: observado en Azure el 27/11/2026 (observación de solo lectura). |
| discontinuo | implementado, no observado o inactivo | Implementado en IaC o código, pero no observado el 27/11 o no activo. |
| punteado | propuesto | Propuesto: declarado en documentos o en roots de Terraform sin workloads. |
| punteado gris | TBD: no definido | No definido (TBD): ni implementado ni decidido; lleva el motivo. |

| Color de relleno | Categoría |
|---|---|
| #EFF6FF con borde #2563EB | Azul: Pipesor (servicios, jobs, entornos) |
| #F1F5F9 con borde #64748B | Gris: actores y servicios externos |
| #ECFDF5 con borde #059669 | Verde: persistencia y secretos |
| #FFFFFF con borde #475569 | Blanco: plataforma o paso de entrega no modelado |
| #E5E7EB con borde #6B7280 | Gris oscuro: TBD |
| #FFFBEB con borde #B45309 | Nota ámbar: divergencia entre el modelo y lo observado |

La categoría de un elemento del modelo sale de su `kind` (actor y sistema externo: gris; datastore: verde; contenedor: azul). Los marcos gris claro son agrupaciones de lectura, no recursos.

## Límites de la evidencia

- La obligatoriedad de los checks conventions, build y assurance, el merge solo por squash y las cero aprobaciones mínimas son rulesets de GitHub, fuera de Git; solo se cita el CI que los produce y la guía de CI/CD.
- La ausencia de CODEOWNERS no se puede citar con una línea: es una ausencia comprobada en la auditoría del 27/11.
- Quién fusiona el PR de images.json y desde dónde se ejecuta el apply constan en notas de traspaso fuera de Git; la figura solo dice «apply manual del operador» con autorización explícita, como el runbook.
- Los tfvars privados de dev (workloads, webhook, deployments reales de Foundry, lectores de Key Vault) no se leyeron; se cita el ejemplo versionado. Que el webhook esté activo no se observó el 27/11.
- La observación del 27/11 no incluyó la red, el Container Apps Environment, Key Vault, Foundry, Log Analytics, las identidades ni GHCR: van como implementados.

## Revisiones de la evidencia

| Clave | Repositorio | Revisión |
|---|---|---|
| `ci` | `pipesor-ci` | `43c70cd` |
| `demo` | `pipesor-demo` | `2ed10e1` |
| `frontend` | `pipesor-frontend` | `2806ae1` |
| `iac` | `pipesor-iac` | `318af56` |
| `ingestion` | `services/pipesor-ingestion-normalization-service` | `a41188a` |
| `recommendation` | `services/pipesor-recommendation-service` | `c3ce559` |

## Despliegue del entorno dev en Azure (`deploy_dev_runtime`)

Vista: [SVG](deploy_dev_runtime.svg)

Recursos del root environments/dev de pipesor-iac y sus dependencias externas. Las 8 Container Apps, los 3 jobs, PostgreSQL y el topic de Service Bus se observaron el 27/11; el resto consta en IaC y no se observó. Las llamadas REST entre servicios por el ingress interno no se dibujan (ver las vistas C4).

En la vista, cada flecha lleva su número y su etiqueta; esta guía trae la tabla de aristas y la leyenda de estados y colores. La figura para documentos está en `out/figuras/06-despliegue/`.

21 nodos: 15 elementos distintos del modelo, 5 implementaciones no modeladas y 0 puntos TBD.

### Nodos

| Nodo | Elemento del modelo o «implementación no modelada» | Estado | Evidencia |
|---|---|---|---|
| Navegador (ejecuta la SPA) | `technical_users`; ejecuta `web_dashboard` | implementado, no observado o inactivo | `frontend:src/shared/config/env.ts:1-11`<br>`iac:modules/workloads/main.tf:284-290`<br>doc. `docs/architecture/decisions/ADR-030-dashboard-on-azure-container-apps.md:32-38` |
| GitHub App (OAuth + PKCE S256) | `github` | implementado, no observado o inactivo | `ingestion:src/main/java/org/pipesor/ingestion/auth/interfaces/rest/AuthController.java:84-86`<br>`ingestion:src/main/java/org/pipesor/ingestion/auth/infrastructure/github/GitHubAuthorizeUrls.java:10-25`<br>`iac:modules/workloads/main.tf:98-109` |
| GitHub Actions (eventos workflow_run; informe con OIDC) | `github_actions` | implementado, no observado o inactivo | `demo:.github/workflows/pipesor-report.yml:7-21`<br>`ingestion:src/main/java/org/pipesor/ingestion/configuration/GitHubWebhookConfiguration.java:23-27` |
| GHCR (paquetes privados; imágenes por digest) | «implementación no modelada» | implementado, no observado o inactivo | `iac:environments/dev/images.json:1-62`<br>`ci:.github/workflows/publish-container.yml:53-91` |
| ingestion (0,5 vCPU · 1 GiB) | `ingestion_normalization_service` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:5-11` |
| pipeline (0,5 vCPU · 1 GiB) | `pipeline_service` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:12-18` |
| recommendation (0,5 vCPU · 1 GiB) | `recommendation_service` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:40-46` |
| dashboard (nginx · 0,25 vCPU · 0,5 GiB) | `web_dashboard` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:247-300`<br>`iac:environments/dev/images.json:54-60`<br>doc. `docs/architecture/decisions/ADR-030-dashboard-on-azure-container-apps.md:29-31` |
| log-event (0,5 vCPU · 1 GiB) | `log_event_service` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:19-25` |
| nlp (0,25 vCPU · 0,5 GiB) | `nlp_log_processor` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:26-32` |
| correlation (0,5 vCPU · 1 GiB) | `evidence_correlation_engine` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:33-39` |
| rag (0,25 vCPU · 0,5 GiB) | `rag_retrieval` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:modules/workloads/main.tf:196-245`<br>`iac:environments/dev/images.json:47-53` |
| 3 jobs manuales (setup de BD · autoridad · migraciones RAG; job-database-setup; job-ingestion-authority-import; job-rag-migrations) | «implementación no modelada» | desplegado (observado el 27/11) | observación 27/11 (`jobs`)<br>`iac:modules/workloads/main.tf:302-312`<br>`iac:modules/workloads/main.tf:334-367`<br>`iac:modules/workloads/main.tf:369-400`<br>`iac:modules/workloads/main.tf:402-431` |
| PostgreSQL Flexible Server (PostgreSQL 17; Standard_D2s_v3; extensión vector; solo autenticación Entra; sin alta disponibilidad; backup de 7 días) | `postgresql_operational_store`; misma instancia: `pgvector_knowledge_store` | desplegado (observado el 27/11); detenido el 27/11 | observación 27/11 (`postgresql`)<br>`iac:modules/postgresql/main.tf:27-50`<br>`iac:modules/postgresql/main.tf:64-70`<br>`iac:environments/dev/terraform.tfvars.example:28-32`<br>`iac:modules/workloads/main.tf:322` |
| Service Bus Standard (topic workflow-evidence; 3 suscripciones con filtro SQL) | `azure_service_bus` | desplegado (observado el 27/11) | observación 27/11 (`service_bus`)<br>`iac:modules/service-bus/main.tf:1-61`<br>`iac:environments/dev/terraform.tfvars.example:13-27` |
| Key Vault de material (claves RSA de firma; secretos de la App y del registro) | `azure_key_vault` | implementado, no observado o inactivo | `iac:modules/key-vault/main.tf:1-41`<br>`iac:modules/workloads/main.tf:156-169`<br>`iac:environments/dev/terraform.tfvars.example:55-62`<br>`iac:docs/dev-runtime-deployment.md:57-65` |
| Key Vault de custodia (tokens de usuario y verifier PKCE) | `azure_key_vault` | implementado, no observado o inactivo | `iac:modules/key-vault/main.tf:1-2`<br>`iac:modules/key-vault/main.tf:56-85`<br>`iac:environments/dev/terraform.tfvars.example:61`<br>`ingestion:src/main/java/org/pipesor/ingestion/auth/application/commandhandlers/GitHubLoginHandler.java:89-95` |
| Foundry (AIServices S0) (chat: pipesor-dev-diagnostics-luna; gpt-6-luna 2026-09-22; embeddings: pipesor-dev-embeddings; proyecto pipesor-dev; embeddings: text-embedding-3-small) | `pretrained_llm_diagnostic_service`; hecho `deployment.llm.model_deployment` | implementado, no observado o inactivo | `iac:modules/foundry/main.tf:1-60`<br>`iac:environments/dev/terraform.tfvars.example:41-52`<br>`iac:modules/workloads/main.tf:116-130` |
| 9 identidades administradas (asignadas por el usuario; 7 servicios · db-admin · dashboard) | «implementación no modelada»; hecho `deployment.identity_and_api_perimeter.azure_resource_identity` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:29`<br>`iac:modules/workloads/main.tf:146-154` |
| Log Analytics (PerGB2018 · 30 días · 0,1 GB/día) | «implementación no modelada» | implementado, no observado o inactivo | `iac:modules/container-platform/main.tf:28-41`<br>`iac:environments/dev/terraform.tfvars.example:10-11` |
| Application Insights (desactivado en dev) | «implementación no modelada»; hecho `deployment.observability_platform.application_telemetry` | implementado, no observado o inactivo | `iac:modules/application-insights/main.tf:7-28`<br>`iac:environments/dev/main.tf:39-48`<br>`iac:environments/dev/terraform.tfvars.example:40` |

### Grupos

| Grupo | Tipo | Estado | Evidencia |
|---|---|---|---|
| Azure for Students (tenant UPC) · rg-pipesor-dev · westus3 | recurso; hecho `deployment.mvp_preparation.active_environment` | implementado, no observado o inactivo | `iac:docs/adr-004-mvp-state-and-deployment.md:43-46`<br>`iac:environments/dev/terraform.tfvars.example:3-4`<br>`iac:environments/dev/main.tf:1-6`<br>`iac:modules/resource-group/main.tf:1-16`<br>`iac:docs/dev-provisioning.md:23` |
| Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24 | recurso; hecho `deployment.containerization.orchestrator` | implementado, no observado o inactivo | `iac:modules/container-platform/main.tf:7-27`<br>`iac:environments/dev/terraform.tfvars.example:8`<br>`iac:modules/container-platform/main.tf:42-61`<br>`iac:environments/dev/main.tf:8-15`<br>`iac:environments/dev/terraform.tfvars.example:9` |
| Ingress interno: https://<app>.internal.<dominio> | agrupación de lectura: Agrupa las apps con ingress interno; no es un recurso. | — | `iac:modules/workloads/main.tf:3-4`<br>`iac:modules/workloads/main.tf:28` |
| Ingress externo: https://<app>.<dominio> | agrupación de lectura: Agrupa las apps con ingress externo; no es un recurso. | — | `iac:modules/workloads/main.tf:4`<br>`iac:modules/workloads/main.tf:28`<br>`iac:modules/workloads/main.tf:212-218`<br>`iac:modules/workloads/main.tf:263-269` |
| Subred 10.50.2.0/28 · DNS privado | recurso | implementado, no observado o inactivo | `iac:modules/postgresql/main.tf:1-26`<br>`iac:environments/dev/terraform.tfvars.example:31` |

### Aristas

| Nº | Arista | Relación del modelo | Estado | Evidencia |
|---|---|---|---|---|
| 01 | Navegador → dashboard: SPA (HTTPS). El navegador descarga la SPA del dashboard por su ingress externo. | `rel_technical_users_dashboard` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:263-269` |
| 02 | Navegador → [Ingress externo: https://<app>.<dominio>]: REST + token de sesión. La SPA llama desde el navegador, con CORS y el token de sesión, a las APIs de ingestion, pipeline y recommendation; no a log-event. | `rel_dashboard_ingestion_github_connection`, `rel_dashboard_pipeline_service`, `rel_dashboard_recommendation_service` | implementado, no observado o inactivo | `frontend:src/shared/config/env.ts:4-11`<br>`iac:modules/workloads/main.tf:284-290` |
| 03 | GitHub Actions → ingestion: webhook workflow_run. La GitHub App entrega eventos workflow_run firmados a /webhooks/v1/github/workflow-runs; se activa solo si se fija webhook_secret_version en los tfvars privados. | `rel_github_actions_ingestion_event` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:110-115`<br>`ingestion:src/main/java/org/pipesor/ingestion/configuration/GitHubWebhookConfiguration.java:23-27` |
| 04 | ingestion → GitHub Actions: runs, jobs y logs. Ingestion lee runs, jobs y logs con el token de instalación de la GitHub App. | `rel_ingestion_github_actions_read` | implementado, no observado o inactivo | `ingestion:src/main/java/org/pipesor/ingestion/capture/infrastructure/github/GitHubMachineTransport.java:86-125` |
| 05 | ingestion → GitHub App: OAuth + PKCE. Ingestion redirige a GitHub e intercambia el código con el verifier PKCE. | `rel_ingestion_github_connection` | implementado, no observado o inactivo | `ingestion:src/main/java/org/pipesor/ingestion/auth/application/commandhandlers/GitHubLoginHandler.java:89-95`<br>`iac:modules/workloads/main.tf:102` |
| 06 | GitHub Actions → recommendation: informe (OIDC). El workflow de informe del repositorio monitorizado pide el diagnóstico a Recommendation con un token OIDC de GitHub Actions (audiencia urn:pipesor:api:recommendation). | `rel_github_actions_diagnostic` | implementado, no observado o inactivo | `demo:.github/workflows/pipesor-report.yml:20-48`<br>`recommendation:src/main/java/com/pipesor/recommendation/shared/security/GitHubActionsJwtDecoder.java:25-44`<br>`recommendation:src/main/java/com/pipesor/recommendation/diagnosis/interfaces/rest/GitHubActionsReportController.java:20-29` |
| 07 | ingestion → Service Bus Standard: publica. Ingestion publica en workflow-evidence con el rol Data Sender sobre el topic. | `rel_ingestion_service_bus` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:56`<br>`iac:modules/workloads/main.tf:93-96` |
| 08 | Service Bus Standard → pipeline: suscripción pipeline. Suscripción pipeline, filtro eventType = 'execution.snapshot'; rol Data Receiver. | `rel_service_bus_pipeline_service` | desplegado (observado el 27/11) | observación 27/11 (`service_bus`)<br>`iac:environments/dev/terraform.tfvars.example:22`<br>`iac:modules/workloads/main.tf:49` |
| 09 | Service Bus Standard → log-event: suscripción log-event. Suscripción log-event, filtro eventType = 'protected_workflow_evidence'. | `rel_service_bus_log_event_service` | desplegado (observado el 27/11) | observación 27/11 (`service_bus`)<br>`iac:environments/dev/terraform.tfvars.example:23`<br>`iac:modules/workloads/main.tf:49` |
| 10 | Service Bus Standard → nlp: suscripción nlp. Suscripción nlp, filtro eventType = 'protected_workflow_evidence'. | `rel_service_bus_nlp` | desplegado (observado el 27/11) | observación 27/11 (`service_bus`)<br>`iac:environments/dev/terraform.tfvars.example:24`<br>`iac:modules/workloads/main.tf:49` |
| 11 | [Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24] → PostgreSQL Flexible Server: SQL + token Entra. Seis servicios (todos menos nlp) y los jobs de base de datos se conectan con el token Entra de su identidad administrada; el job de setup crea los principals, la base pipesor y la extensión vector. | `rel_ingestion_postgresql_connector_metadata`, `rel_pipeline_service_postgresql`, `rel_log_event_service_postgresql`, `rel_correlation_postgresql`, `rel_recommendation_service_postgresql`, `rel_rag_pgvector` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:7`<br>`iac:modules/workloads/main.tf:61-65`<br>`iac:modules/workloads/main.tf:120-123`<br>`iac:modules/workloads/main.tf:313-331` |
| 12 | [Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24] → Key Vault de material: firma y secretos. Cada servicio firma sus tokens con su clave no exportable (Crypto User); las apps y los jobs leen el token del registro por referencia de Key Vault; Ingestion lee el material de la App. | `rel_ingestion_key_vault`, `rel_pipeline_key_vault`, `rel_log_event_key_vault`, `rel_nlp_key_vault`, `rel_correlation_key_vault`, `rel_recommendation_key_vault` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:46-53`<br>`iac:modules/workloads/main.tf:219-224` |
| 13 | ingestion → Key Vault de custodia: custodia. Ingestion guarda tokens de usuario y verifiers PKCE con el rol Secrets Officer. | `rel_ingestion_key_vault` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:57`<br>`iac:modules/workloads/main.tf:108` |
| 14 | recommendation → Foundry (AIServices S0): inferencia. Recommendation llama al deployment de chat con el rol Cognitive Services OpenAI User. | `rel_recommendation_llm` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:50`<br>`iac:modules/workloads/main.tf:116-119` |
| 15 | rag → Foundry (AIServices S0): embeddings. RAG genera embeddings con el deployment pipesor-dev-embeddings. | `rel_rag_embeddings` | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:50`<br>`iac:modules/workloads/main.tf:126-129` |
| 16 | [Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24] → Log Analytics: logs de plataforma. Diagnostic settings del environment: solo ContainerAppSystemLogs y ContainerAppConsoleLogs; sin métricas. | «implementación no modelada» | implementado, no observado o inactivo | `iac:modules/container-platform/main.tf:52`<br>`iac:modules/container-platform/main.tf:62-85` |
| 17 | Application Insights → Log Analytics: workspace (inactivo). El módulo de Application Insights usa el workspace, pero dev lo deja desactivado. | «implementación no modelada» | implementado, no observado o inactivo | `iac:modules/application-insights/main.tf:18`<br>`iac:environments/dev/main.tf:39-48` |
| 18 | GHCR → [Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24]: imágenes por digest. Las apps y los jobs descargan la imagen fijada por digest en images.json con el token del registro guardado en Key Vault; la observación del 27/11 encontró esos digests. | «implementación no modelada» | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:environments/dev/main.tf:75-81`<br>`iac:modules/workloads/main.tf:137`<br>`iac:modules/workloads/main.tf:219-229` |
| 19 | 9 identidades administradas → [Container Apps Environment (Consumption) VNet 10.50.0.0/16 · subred delegada 10.50.1.0/24]: una por app y job. Cada Container App y cada job usa su identidad asignada por el usuario. | «implementación no modelada» | implementado, no observado o inactivo | `iac:modules/workloads/main.tf:203-206`<br>`iac:modules/workloads/main.tf:340-343` |

### Implementado y no dibujado

| Elemento | Estado | Motivo | Evidencia |
|---|---|---|---|
| Módulo de Static Web Apps | implementado, no observado o inactivo | En dev vale static_web_app = null; el dashboard es una Container App (ADR-030). | `iac:environments/dev/main.tf:58-64`<br>`iac:environments/dev/terraform.tfvars.example:53-54` |
| Llamadas REST entre servicios por el ingress interno y descarga de JWKS | implementado, no observado o inactivo | Se dibujan en las vistas C4; aquí solo se muestra el tipo de ingress de cada app. | `iac:modules/workloads/main.tf:13-25`<br>`iac:modules/workloads/main.tf:79-88` |
| Otros deployments de Foundry (gpt-4o de referencia y variantes -terra y -sol) | implementado, no observado o inactivo | No los usa ningún workload; el valor real está en los tfvars privados, que no se leen. | `iac:environments/dev/terraform.tfvars.example:49`<br>`iac:docs/dev-runtime-deployment.md:14` |
| Estado de Terraform (rg-pipesor-state-dev) | implementado, no observado o inactivo | Lo crea el bootstrap, fuera del root dev; no es un recurso del runtime. | `iac:docs/dev-provisioning.md:22-23` |

## Entornos y entrega de imágenes (`deploy_environments_delivery`)

Vista: [SVG](deploy_environments_delivery.svg)

Flujo trunk-based definido en los repositorios hasta el entorno dev, y roots de Terraform de qa, preprod y prod, que solo tienen fundaciones. Lo que ningún documento ni código define se marca TBD con su motivo, sin proponer una estrategia.

En la vista, cada flecha lleva su número y su etiqueta; esta guía trae la tabla de aristas y la leyenda de estados y colores. La figura para documentos está en `out/figuras/06-despliegue/`. Los puntos TBD no tienen aristas: van en el recuadro «No definido (TBD)» bajo el dibujo.

19 nodos: 0 elementos distintos del modelo, 13 implementaciones no modeladas y 6 puntos TBD.

### Nodos

| Nodo | Elemento del modelo o «implementación no modelada» | Estado | Evidencia |
|---|---|---|---|
| rama feature/ o fix/ desde main | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/adr-001-branching-and-promotion.md:36-38`<br>`ingestion:.github/workflows/ci.yml:3-6`<br>doc. `docs/development/cicd.md:12-14` |
| PR a main (checks: conventions · build · assurance) | «implementación no modelada» | implementado, no observado o inactivo | `ingestion:.github/workflows/ci.yml:16-25`<br>`ci:.github/workflows/service-ci.yml:56-82`<br>`ci:.github/workflows/conventions.yml:111-133`<br>doc. `docs/development/cicd.md:28-31` |
| squash merge a main | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/adr-001-branching-and-promotion.md:42-43`<br>`ci:.github/workflows/conventions.yml:135-137`<br>doc. `docs/development/cicd.md:28-34` |
| CI en main (build · Trivy · publish; candidate.json (90 días)) | «implementación no modelada» | implementado, no observado o inactivo | `ingestion:.github/workflows/ci.yml:7-8`<br>`ci:.github/workflows/service-ci.yml:84-92`<br>`ci:.github/workflows/container-build.yml:107-109`<br>`ci:.github/workflows/image-assurance.yml:23`<br>`ci:.github/workflows/image-assurance.yml:63-81`<br>`ci:.github/workflows/publish-container.yml:93-131` |
| GHCR (paquete privado · imagen por digest) | «implementación no modelada» | implementado, no observado o inactivo | `ci:.github/workflows/publish-container.yml:50-91`<br>`iac:environments/dev/images.json:6-7` |
| tools/images.js set dev (candidato de un push a main con éxito) | «implementación no modelada» | implementado, no observado o inactivo | `iac:tools/images.js:66-79`<br>`iac:tools/images.js:155-163` |
| PR a dev/images.json (CI valida el archivo · merge) | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/dev-runtime-deployment.md:157-160`<br>`iac:environments/dev/main.tf:75-81`<br>`iac:tests/images.test.js:22-29` |
| plan nuevo desde main (el CI de IaC no planifica) | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/adr-001-branching-and-promotion.md:85-90`<br>`iac:docs/dev-runtime-deployment.md:159-160`<br>`iac:.github/workflows/ci.yml:67-71` |
| apply manual del operador (plan revisado · autorización explícita) | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/dev-runtime-deployment.md:7`<br>`iac:docs/dev-runtime-deployment.md:159-161`<br>`iac:docs/adr-001-branching-and-promotion.md:103` |
| dev (8 Container Apps Healthy; digests de images.json) | «implementación no modelada»; hecho `deployment.mvp_preparation.active_environment` | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:environments/dev/main.tf:75-117`<br>`iac:environments/dev/images.json:1-62` |
| qa (solo fundaciones · sin workloads) | «implementación no modelada»; hecho `deployment.mvp_preparation.preserved_environment_roots` | propuesto | `iac:environments/qa/main.tf:1-73`<br>`iac:environments/qa/terraform.tfvars.example:1-6`<br>`iac:README.md:25` |
| preprod (solo fundaciones · sin workloads) | «implementación no modelada»; hecho `deployment.mvp_preparation.preserved_environment_roots` | propuesto | `iac:environments/preprod/main.tf:1-73`<br>`iac:environments/preprod/terraform.tfvars.example:1-6`<br>`iac:README.md:25` |
| prod (solo fundaciones · sin workloads) | «implementación no modelada»; hecho `deployment.mvp_preparation.preserved_environment_roots` | propuesto | `iac:environments/prod/main.tf:1-73`<br>`iac:environments/prod/terraform.tfvars.example:1-6`<br>`iac:README.md:25` |
| gates entre entornos | — (no definido) | TBD: Los Environments con revisores de qa, preprod y prod están por configurar; no hay gate definido. | `iac:docs/adr-001-branching-and-promotion.md:31-32`<br>doc. `docs/development/cicd.md:180`<br>doc. `docs/development/cicd.md:249-251` |
| releases y tags SemVer | — (no definido) | TBD: release.yml está deshabilitado en el código (if: false) y stable exige una validación preprod que no existe. | `ingestion:.github/workflows/release.yml:44-45`<br>`ci:README.md:80-81`<br>doc. `docs/development/cicd.md:107-110` |
| despliegue automático a dev | — (no definido) | TBD: La plantilla terraform-dev.yml.example es un andamiaje inactivo (if: ${{ false }}) con un runner propuesto. | `iac:.github/workflow-templates/terraform-dev.yml.example:1-3`<br>`iac:.github/workflow-templates/terraform-dev.yml.example:45-48`<br>doc. `docs/development/cicd.md:152-154` |
| aprobaciones de PR y CODEOWNERS | — (no definido) | TBD: Los rulesets no exigen aprobaciones mínimas y ningún repositorio tiene CODEOWNERS. | doc. `docs/development/cicd.md:28-30` |
| orden de despliegue entre repositorios | — (no definido) | TBD: PD-035 no especifica el contrato de entrega backend–IaC (artefactos, migraciones, promoción). | doc. `docs/architecture/pending-decisions.md:226` |
| registro de despliegue (IaC ADR 001) | — (no definido) | TBD: ADR 001 pide SHA, digest del plan, aprobadores y timestamps; en Git solo queda el historial de images.json. | `iac:docs/adr-001-branching-and-promotion.md:105-110`<br>`iac:docs/dev-runtime-deployment.md:157-159` |

### Grupos

| Grupo | Tipo | Estado | Evidencia |
|---|---|---|---|
| Repositorio de cada servicio (GitHub) | agrupación de lectura: Pasos que ejecuta cada repositorio de servicio o del frontend. | — | — |
| pipesor-iac | agrupación de lectura: Pasos del repositorio de IaC, dueño de las imágenes desplegadas. | — | — |
| Entornos (un root de Terraform cada uno) | agrupación de lectura: Roots de environments/; solo dev tiene workloads. | — | — |

### Aristas

| Nº | Arista | Relación del modelo | Estado | Evidencia |
|---|---|---|---|---|
| 01 | rama feature/ o fix/ desde main → PR a main: PR. Cada cambio entra por un PR a main que dispara el CI del repositorio. | «implementación no modelada» | implementado, no observado o inactivo | `ingestion:.github/workflows/ci.yml:3-6` |
| 02 | PR a main → squash merge a main: checks en verde. conventions, build y assurance del CI compartido; su obligatoriedad está en los rulesets de GitHub. | «implementación no modelada» | implementado, no observado o inactivo | `ci:.github/workflows/service-ci.yml:56-82` |
| 03 | squash merge a main → CI en main: push a main. El push a main vuelve a verificar el commit integrado y habilita la publicación. | «implementación no modelada» | implementado, no observado o inactivo | `ingestion:.github/workflows/ci.yml:7-8`<br>`ci:.github/workflows/service-ci.yml:84-86` |
| 04 | CI en main → GHCR: push sin reconstruir. Publica el archivo ya verificado y comprueba que el paquete sea privado. | «implementación no modelada» | implementado, no observado o inactivo | `ci:.github/workflows/publish-container.yml:50-91` |
| 05 | CI en main → tools/images.js set dev: candidate.json. images.js descarga el candidate.json del run y verifica que sea un push a main de ci.yml con éxito. | «implementación no modelada» | implementado, no observado o inactivo | `ci:.github/workflows/publish-container.yml:125-131`<br>`iac:tools/images.js:112-131` |
| 06 | tools/images.js set dev → PR a dev/images.json: cambia la entrada. set reescribe la entrada del workload e indica abrir un PR. | «implementación no modelada» | implementado, no observado o inactivo | `iac:tools/images.js:155-163` |
| 07 | PR a dev/images.json → plan nuevo desde main: tras el merge. Después del merge se genera un plan nuevo desde main. | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/dev-runtime-deployment.md:157-160` |
| 08 | plan nuevo desde main → apply manual del operador: revisión humana. Se revisa el plan guardado y se autoriza ese apply concreto. | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/adr-001-branching-and-promotion.md:85-93` |
| 09 | apply manual del operador → dev: apply. Se aplica solo el plan revisado sobre el root dev. | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/dev-runtime-deployment.md:159-161` |
| 10 | GHCR → dev: imagen por digest. Las Container Apps de dev ejecutan los digests de images.json (observación del 27/11). | «implementación no modelada» | desplegado (observado el 27/11) | observación 27/11 (`container_apps`)<br>`iac:environments/dev/main.tf:75-81` |
| 11 | dev → PR a dev/images.json: rollback: restaura la entrada anterior. Un PR que restaura la entrada anterior de images.json y un plan nuevo revisado; no hay downgrade SQL implícito. No consta en Git una ejecución de rollback. | «implementación no modelada» | implementado, no observado o inactivo | `iac:docs/dev-runtime-deployment.md:161-162`<br>doc. `docs/development/cicd.md:145-147` |
| 12 | dev → qa: mismo digest. Promoción declarada: el mismo digest en el root siguiente (images.js promote). Hoy fallaría: qa no tiene images.json y readDocument lo exige. | «implementación no modelada» | propuesto | `iac:docs/adr-001-branching-and-promotion.md:57-64`<br>`iac:tools/images.js:90-96`<br>`iac:tools/images.js:164-170` |
| 13 | qa → preprod: mismo digest. Promoción declarada de qa a preprod tras verificar en qa y la aprobación independiente de QA. | «implementación no modelada» | propuesto | `iac:docs/adr-001-branching-and-promotion.md:63` |
| 14 | preprod → prod: mismo digest. Promoción declarada de preprod a prod tras verificar en preprod y la aprobación de producción. | «implementación no modelada» | propuesto | `iac:docs/adr-001-branching-and-promotion.md:64` |

### Divergencia

Nota junto a «dev»: architecture.yml: deployment_authorized: false (ADR-019) frente a: dev desplegado (observado 27/11).
Hecho del modelo: `deployment.mvp_preparation.deployment_authorized` = `false`; observación 27/11 (`container_apps`). Fuente: `docs/architecture/decisions/ADR-019-align-mvp-with-iac.md:79-84`. La figura muestra la divergencia; no cambia architecture.yml ni acredita una autorización.

### Implementado y no dibujado

| Elemento | Estado | Motivo | Evidencia |
|---|---|---|---|
| Retención semanal de GHCR | implementado, no observado o inactivo | Protege el digest actual y 3 anteriores de cada images.json; funciona en dry-run hasta REGISTRY_RETENTION_DELETE=true. | `ci:README.md:83-90`<br>`ci:README.md:126-129` |
| CI de pipesor-iac | implementado, no observado o inactivo | Valida formato, roots, módulos e images.json sin credenciales ni backend; no hace plan real. | `iac:.github/workflows/ci.yml:39-97` |
