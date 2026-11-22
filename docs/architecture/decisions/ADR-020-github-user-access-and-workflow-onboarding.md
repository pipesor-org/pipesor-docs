Title: GitHub user access and monitored workflow onboarding
Status: Accepted
Date: 2026-11-06

## Context

El usuario aprobó expresamente en la sesión de Pipeline Service la propuesta de investigación sobre conexión GitHub, alta y autorización: «Aprobado, necesito que hagas la actualizacion de los documentos, hay que ser bastante cuidadosos al definir que servicios afecta esta decision». Esta confirmación autoriza registrar la decisión y su impacto; no acredita revisión de ambos CODEOWNERS, publicación, implementación, contratos ejecutables ni despliegue.

ADR-005 selecciona GitHub App read-only con installation tokens. Esos tokens representan a la instalación y no prueban el acceso individual del usuario del dashboard. Entra autentica al usuario corporativo, pero no vincula por sí mismo su cuenta GitHub. El alta manual basada en una declaración y el catálogo local preaprovisionado no satisfacen la selección de workflows con acceso verificado.

## Decision

### Identidad y credenciales

- Conservar Entra como identidad de AIOps y la GitHub App read-only. Añadir user access tokens para las acciones en nombre de una persona; conservar installation tokens para captura y monitoreo de máquina. No usar el token de instalación como sustituto cuando falla la autorización del usuario.
- Vincular explícitamente tenantId/objectId de Entra con githubUserId estable. Una cuenta GitHub por identidad AIOps en el MVP; correo, login, nombres y datos del navegador no prueban esa vinculación. El proceso de cambio/desvinculación debe invalidar el contexto anterior y auditarse; no transferir grants entre identidades.
- Flujo de autorización de servidor con state impredecible, de un solo uso, ligado al usuario/intento y con expiración, más PKCE S256. Resolver identidad y canjear el código en backend. No entregar tokens GitHub al frontend, Pipeline ni otros servicios consumidores; no registrar tokens/códigos en logs, URLs de retorno o auditoría.
- Usar tokens de usuario con expiración y renovación; coordinar renovaciones concurrentes y solicitar reconexión al perder autorización. Custodia, cifrado, claves, rotación y borrado requieren contrato antes de persistir credenciales. Esta decisión no selecciona Key Vault ni otro recurso.
- Admitir solo instalaciones/cuentas GitHub expresamente autorizadas para el tenant. Verificar también acceso de usuario y acceso de la App al repositorio. Acceso público a un repositorio o administración de un repositorio personal no autoriza su importación corporativa.
- Respetar la instalación/aprobación y SSO de la organización GitHub. AIOps puede dirigir al flujo nativo de GitHub, pero no instalar Apps, cambiar permisos ni crear webhooks por repositorio mediante su API.

### Responsabilidades e impacto por servicio

| Servicio/capacidad | Impacto autorizado y límite |
|---|---|
| web_dashboard | Impacto directo: conectar/desconectar GitHub, mostrar instalaciones/repositorios/workflows accesibles, seleccionar y enviar IDs, mostrar reconexión, aprobación pendiente y errores. Continúa React/TypeScript SPA; no custodia tokens GitHub ni decide autorización. |
| ingestion_normalization_service | Impacto directo: alojar un componente técnico interno de conexión GitHub; gestionar vinculación, credenciales, selección verificada, hechos de acceso y eventos de instalación/revocación. Conserva captura, saneamiento y normalización; no registra objetos ops ni decide capacidades de Pipeline. No es un nuevo microservicio de identidad. |
| pipeline_service | Impacto directo: verificar acceso mediante API interna del conector, decidir permisos, registrar/reutilizar Repository y registrar Pipeline, grants iniciales y auditoría. Conserva ownership exclusivo de ops, ejecuciones e incidentes. No recibe tokens GitHub, no consulta GitHub directamente ni escribe almacenamiento del conector. |
| log_event_service | Impacto de seguridad sobre sus APIs humanas: impedir que logs/evidencia vinculados a un repositorio eludan la restricción vigente de acceso. Se requiere contrato para resolver el contexto de autorización; no se añade aquí una relación directa al conector ni acceso a ops. Captura/persistencia de evidencia conserva ownership. |
| recommendation_service | Impacto de seguridad sobre consultas humanas de diagnósticos/recomendaciones y revisión humana vinculadas al repositorio. Requiere contrato de autorización equivalente, no una relación nueva implícita ni copia de grants. Conserva orquestación, diagnóstico y Human Review. El acceso del workflow de PD-036 es otro actor/contrato. |
| evidence_correlation_engine | Sin cambio funcional ni credenciales GitHub. Mantiene correlación de evidencia saneada y referencias lógicas; no resuelve identidad humana ni consume tokens de usuario. |
| nlp_log_processor y rag_retrieval | Sin cambio funcional ni acceso GitHub. El procesamiento de máquina y el corpus autorizado mantienen sus contratos y controles; no heredan grants ni se detienen por la desconexión de una persona. |
| IaC / operadores de integración | Impacto de entrega: configurar App, instalaciones admitidas, callbacks, identidades de servicio, red y custodia acordadas. Esta aprobación documental no autoriza crear recursos, permisos, secretos o desplegar. Entra sigue siendo un proveedor gestionado, no un servicio nuevo. |

El almacenamiento técnico de vinculaciones y credenciales tiene owner lógico ingestion_normalization_service; el schema, tablas, permisos, migraciones y mecanismo seguro quedan pendientes. No se reutiliza ops, evidence ni audit para guardar tokens; no hay tablas users/roles/teams ni nuevo almacén físico aprobados por esta decisión. audit conserva únicamente metadata funcional sanitizada conforme a ADR-011.

### Relaciones aprobadas y contratos pendientes

Se añaden a architecture.yml únicamente:

- rel_dashboard_ingestion_github_connection: dashboard → Ingestion, REST/HTTPS por ingress nativo, limitado a conexión y descubrimiento para el usuario autenticado. Incluye inicio del flujo y recepción controlada del callback de GitHub, con su intercambio externo descrito por la relación siguiente. No expone configuración interna de ingesta.
- rel_ingestion_github_connection: Ingestion → GitHub, OAuth/HTTPS y REST/HTTPS read-only para autorización de usuario, identidad, instalaciones y metadata. Complementa la lectura existente de GitHub Actions y los webhooks de entrada existentes.
- rel_pipeline_ingestion_github_access: Pipeline → Ingestion, REST/HTTPS interno para obtener hechos verificados de acceso y metadata, sin tokens GitHub ni autorización basada en un actor arbitrario enviado por el frontend.

El callback no autentica al usuario mediante el code o installation_id recibido: debe recuperar y verificar el intento vinculado a la identidad Entra. La API interna debe autenticar al servicio llamador y propagar un sujeto verificable, ligado a tenant/repositorio/operación. Rutas, esquemas, audiences, scopes, mecanismo concreto de propagación, errores y versionado siguen pendientes de contrato PD-034/035. No reenviar un token Entra a una API con audience incompatible.

No se añaden llamadas desde Log/Event, Recommendation, correlación o Python al conector por inferencia. Su resolución de autorización se acuerda antes de integrar sus rutas humanas. El conector ofrece hechos; cada owner autoriza sus recursos. La ausencia de ese contrato bloquea la exposición integrada afectada, no el trabajo local independiente.

### Política MVP de capacidades y alta

| Operación | Condiciones acumulativas |
|---|---|
| Explorar repositorios/workflows | Identidad Entra válida y scope de API, vínculo GitHub vigente, instalación admitida y acceso efectivo de lectura mediante token de usuario. |
| Registrar pipeline | Condiciones de exploración más administración efectiva del repositorio verificada en backend. No se deduce permiso de alta de CONFIGURE sobre otro pipeline. |
| Consultar pipeline y datos operacionales | VIEW efectivo en AIOps más acceso GitHub de lectura vigente y contexto de instalación autorizado. |
| Operar incidentes | OPERATE en AIOps más acceso GitHub de lectura vigente. No exige escritura de código ni autoriza cambios en GitHub. |
| Modificar settings o administrar grants | CONFIGURE en AIOps más administración efectiva GitHub vigente. CONFIGURE incluye VIEW, no OPERATE. |

GitHub limita recursos; AIOps puede restringirlos adicionalmente. No copiar el RBAC GitHub ni crear users/roles internos. Usar permisos efectivos del proveedor, no comparar exclusivamente nombres de roles personalizados ni fiarse de flags del navegador. Un administrador GitHub no obtiene grants AIOps automáticamente. Quien recibe un grant debe ser una identidad Entra vinculada y elegible; CONFIGURE no se concede sin administración GitHub verificada. La elegibilidad también se comprueba al usarlo, por lo que un grant almacenado no permite eludir una revocación.

No se requiere un scope global adicional de registro como solución principal: se conserva el scope de API y se aplica la política anterior. Los identificadores/scopes de despliegue aún requieren configuración autorizada.

Al registrar, el backend verifica selección y permisos actuales y obtiene metadata del proveedor; el frontend solo aporta IDs seleccionados y configuración AIOps. Pipeline crea o reutiliza Repository por githubRepositoryId único; no exige una fila preaprovisionada. Pipeline equivale al workflow monitorizado; no hay entidad workflows separada. Se conserva unicidad repository_id/github_workflow_id, con protección concurrente. La identidad del pipeline debe ser compatible con el contrato de IDs acordado con consumidores; la regla UUIDv5 aprobada localmente en Pipeline no se convierte aquí en una regla de IDs para todo el sistema.

Crear repositorio cuando corresponda, pipeline, grant inicial CONFIGURE al creador y auditoría como una única transacción local. Comprobar GitHub antes de abrir esa transacción; no mantener locks SQL durante llamadas remotas ni afirmar atomicidad distribuida. Un duplicado devuelve conflicto sin cambiar settings ni otorgar grants. Nuevos administradores requieren recuperación explícita autorizada y auditada si no conservan grants; su procedimiento sigue pendiente. No existe administrador implícito.

### Revocación, disponibilidad y monitoreo

- Comprobar acceso en cada petición protegida del primer incremento; reutilizar resultados solo dentro de esa petición, sin caché positiva entre peticiones inicialmente. No afirmar revocación instantánea: existe una ventana entre comprobación y uso, y no hay transacción con GitHub.
- En listas aplicar conjuntamente acceso a repositorios y grants AIOps antes de paginar. No filtrar páginas ya calculadas ni exponer nombres, recuentos o datos de repositorios denegados.
- Procesar los eventos aplicables de autorización revocada, instalación suspendida/eliminada y repositorios retirados con firma verificada, idempotencia y recuperación de entregas. Los webhooks complementan, no sustituyen, la comprobación de acceso; no asumir entrega garantizada ni cobertura completa de cambios de permisos por usuario.
- Expiración/revocación del vínculo de una persona bloquea su acceso, incluidos los datos históricos servidos por AIOps. No detiene por sí misma el monitoreo de máquina mientras la instalación siga autorizada. Retirar/suspender la instalación impide nuevas capturas y bloquea el acceso humano dependiente de ella; no usar un token de usuario para sortearlo. No borrar automáticamente datos ni alterar retención.
- Mantener el estado de conexión separado de ACTIVE/PAUSED. La pérdida de conexión no modifica silenciosamente la decisión humana de supervisión. No filtrar por defaultBranch ni prometer backfill al registrar/reactivar. Eventos ya capturados/en tránsito necesitan un contrato explícito de corte y aceptación antes de integrar revocación con consumidores; no purgar ni descartar el broker por inferencia.
- Ante timeout, rate limit o fallo de proveedor/conector, rechazar la operación dependiente por indisponibilidad; no degradar a permiso almacenado vencido ni devolver una lista vacía engañosa. Diferenciar necesidad de reconexión, denegación e indisponibilidad sin revelar existencia de recursos ajenos. El detalle HTTP pertenece al contrato.

### Alcance y evolución

Esta decisión amplía ADR-005 y la exposición limitada de ADR-006/016/019; conserva Entra, native ingress sin gateway dedicado, siete backends y ownership de ADR-018. Cierra la política funcional MVP de PD-007/008; no cierra su implementación, representación física definitiva, recuperación ni contratos externos. La representación pipeline_access_grants conserva ia_only/inferred hasta una decisión física explícita. DQ-005/006 se acotan a esos detalles restantes, no reabren la política aprobada.

No aprueba todavía operaciones nuevas de policy/ownership, rutas de historial o lectura de grants ni pipeline owners: las propuestas anteriores de ese prompt no fueron objeto de esta aprobación de investigación. Tampoco aprueba topología/eventos nuevos, imágenes, recursos o despliegue.

## Verification and adoption

Actualizar el modelo y derivados mediante sus generadores; las vistas existentes conservan su membresía y no representan exhaustivamente el onboarding. Antes de activar: contratos versionados, custodia, firma/replay del callback, aislamiento entre tenants/instalaciones, pérdida de permisos y SSO, renovación concurrente, duplicados/rollback, filtrado antes de paginar, denegación por proveedor no disponible y ausencia de bypass por APIs de evidencia/diagnóstico. Las pruebas locales no acreditan instalación GitHub o integración Entra reales.

## Research sources

Consultadas el 2026-11-06; son evidencia técnica, no autoridad sobre la política de AIOps:

- [GitHub App best practices](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app): tokens por actor, mínimo privilegio y comprobaciones de acceso.
- [User access tokens y PKCE](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app).
- [Instalaciones y repositorios accesibles al usuario](https://docs.github.com/en/rest/apps/installations#list-repositories-accessible-to-the-user-access-token).
- [Workflows y Actions read](https://docs.github.com/en/rest/actions/workflows#list-repository-workflows).
- [Permisos efectivos de colaboradores](https://docs.github.com/en/rest/collaborators/collaborators#get-repository-permissions-for-a-user).
- [Renovación](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/refreshing-user-access-tokens), [SSO](https://docs.github.com/en/enterprise-cloud%40latest/authentication/authenticating-with-single-sign-on/authorizing-an-app-for-single-sign-on), [restricciones de instalación](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/limiting-oauth-app-and-github-app-access-requests-and-installations).
- [Webhooks](https://docs.github.com/en/webhooks/webhook-events-and-payloads), [entregas fallidas sin reenvío automático](https://docs.github.com/en/webhooks/using-webhooks/handling-failed-webhook-deliveries).

## Consequences and reversibility

Las operaciones humanas dependen de disponibilidad/rate limits GitHub y del conector. Sin caché positiva entre peticiones se prioriza comprobar acceso reciente; futuras optimizaciones requieren un presupuesto explícito de obsolescencia y revocación. Es un cambio de seguridad respecto de los grants locales existentes y debe implementarse también en las superficies humanas afectadas antes de afirmar acceso integrado seguro. Revertirlo o permitir acceso histórico independiente requiere otra decisión; no basta conservar un grant ni reutilizar credenciales de máquina.

## Amendment 2026-11-22: VIEW verification budget (MVP)

Accepted by the project owner after measuring the local stack: each human read re-verified access with 4–5 GitHub API calls (~1.7 s), and dashboard lists repeat it per row (~120 calls per page), enough to exhaust the user's GitHub rate limit during a demo.

- **Staleness budget:** Pipeline may reuse a successful `VIEW` verification for at most 30 s (`pipeline.ingestion.view-access-cache-ttl`, maximum 60 s, `0` disables), keyed by actor, subject, repository set and operation. A revocation in GitHub therefore affects reads within 30 s.
- **No budget for commands:** `OPERATE`, `CONFIGURE`, grants, registration and workflow verification always verify live, so a revoked user cannot change state from cached facts.
- **Never cached:** failures, unavailable verifications and unlinked connections.

Implementation: pipesor-pipeline-service `CachingGitHubConnector`.
