# Cierre del MVP — coordinación 22–25/11/2026

Plan de trabajo en paralelo entre dos sesiones de agente (Claude Code y Codex) para
cubrir los entregables del Charter (OE3-I2, OE4-I2) con despliegue en Azure dev o, como
contingencia, demostración local con el mismo código.

Contratos de referencia (fuente única; cualquier cambio se acuerda antes de implementarlo):

- [ADR-022 — identidad sin app registrations](../architecture/decisions/ADR-022-platform-identity-without-entra-app-registrations.md)
- [Contrato de identidad de plataforma v1](../architecture/contracts/platform-identity-v1.md)
- [Evidencia protegida 2.2](../architecture/contracts/protected-evidence-v2.2.md)
- [API HTTP del MVP v1](../architecture/contracts/mvp-http-api-v1.md)
- [Manifiesto de runtime](runtime-manifest.md)

## Reparto por repositorio

Un repositorio tiene un único dueño durante el cierre. Nadie modifica un repositorio
ajeno; los cambios necesarios en el otro lado se piden mediante issue.

| Dueño | Repositorios | Alcance |
|---|---|---|
| Claude Code | `pipesor-ingestion-normalization-service`, `pipesor-pipeline-service`, `pipesor-log-event-service`, `pipesor-evidence-correlation-engine`, `pipesor-recommendation-service`, `pipesor-workspace`; en `pipesor-docs`, los contratos y ADR | Seguridad de plataforma en Java, composición runtime de cada servicio, consumidores de Service Bus, disparo y persistencia del diagnóstico, rutas `/api/v1`, salud, migraciones, Dockerfiles, localizador 2.2 en Java, stack local `docker compose` y generación de claves |
| Codex (compañero) | `pipesor-frontend`, `pipesor-nlp-log-processor`, `pipesor-rag-retrieval`, nuevo `pipesor-scenarios`; en `pipesor-docs`, el protocolo de evaluación (archivo propio en `docs/research/`) | Dashboard real con login, NLP y RAG según los contratos, repositorio de escenarios, corpus RAG y protocolo de evaluación |
| Jhon | `pipesor-iac` | IaC y despliegue en Azure dev (con apoyo de Claude Code para redactar cambios; toda aplicación requiere su autorización) |
| Codex (Jhon), CI/CD | En Correlation, Log/Event y Recommendation solo `.github/**`, `tools/check_image.py` y su test, herramientas de commit (`package.json`, `bun.lock`, `lefthook.yml`, `commitlint.config.js`) y la sección CI/CD del README | Workflows `ci`/`release`/`deploy` alineados con Pipeline e Ingestion; despliegue desactivado; sin cambios de ajustes, secretos ni environments |

## Reglas

1. Rama corta por repositorio desde `main` y un PR por repositorio, con commits
   convencionales en inglés y las verificaciones del repositorio (`AGENTS.md`).
2. Revisión cruzada de todo PR que toque una interfaz consumida por el otro dueño.
3. Ningún secreto, token, URL de sesión ni PEM en Git. Cada persona usa su propio
   Device Flow y su `~/.config/pipesor-local/`. En Azure, todo secreto vive en Key Vault.
4. Nada de fixtures, rutas `/local-demo` ni spools en `src/main`. Simulaciones solo en
   tests automatizados.
5. Seguimiento con un issue por bloque, asignado a su dueño y enlazado desde su PR.
6. Si un contrato resulta insuficiente, se detiene la parte afectada y se propone el
   cambio en `pipesor-docs` antes de implementarlo.

## Puntos de sincronización

| Cuándo | Resultado esperado |
|---|---|
| 22/11 noche | Contratos fusionados en `pipesor-docs`; stack local (`docker compose`, claves) disponible en `pipesor-workspace` |
| 23/11 tarde | Integración local extremo a extremo: login, selección de run, análisis, diagnóstico GPT-4o visible y revisión humana |
| 24/11 | Despliegue en Azure dev (o decisión de contingencia comunicada a coordinación) |
| 25/11 | Escenarios ejecutados, artifact publicado, evidencias saneadas y demostración |

## Estado verificado — 22/11/2026

Recorrido real ejecutado en local con el stack compartido y los cinco servicios Java
(ramas `feat/platform-runtime` / `feat/runtime-composition`, PRs abiertos):

| Tramo | Resultado observado |
|---|---|
| Login | GitHub OAuth (App `pipesor-dev`) → sesión Pipesor con los claims de §3 del contrato de identidad |
| Discovery | Repositorios, workflows y runs fallidos reales consultados con el token de usuario custodiado por Ingestion |
| Registro | `POST /api/v1/pipelines` del workflow `412504984`: Pipeline verificó admin/admitido/legible vía Ingestion (workload + sujeto); grant `CONFIGURE` y evento de auditoría |
| Captura | Run auténtico `43055757606` → recibo `PUBLISHED`, snapshot y evidencia 2.2 `CONFIRMED` en el emulador de Service Bus |
| Pipeline | Ejecución fallida, incidente `OPEN` (`INFRASTRUCTURE`) con vínculo `ORIGIN`; visible en `GET /api/v1/incidents?state=OPEN` |
| Log/Event | Evidencia registrada tras `Evidence.Check` contra Pipeline, con los mismos IDs, run, attempt y localizador |
| Correlation y Recommendation | Con un sustituto de prueba de NLP (firma como `nlp` con la clave local), la evidencia auténtica fue aceptada tras las comprobaciones reales contra Pipeline y Log/Event; contexto persistido, recibo de Recommendation y trabajo de diagnóstico creado; el reenvío devolvió `duplicate` |
| Pendiente | NLP real, RAG (el worker reintenta con `rag_unavailable`), GPT-4o, dashboard y despliegue |

La demostración paso a paso, con la evidencia que se debe registrar en cada tramo, está en la
[guía de demostración del MVP](mvp-demo-guide.md).

### Reproducir en otra máquina

1. Clonar los repos con `pipesor-workspace` y hacer checkout de las ramas de los PRs (o `main`
   cuando estén fusionados). Requisitos: Docker, Java 25, Python 3.14, `az login` con acceso al
   recurso Foundry `ai-pipesor-dev-04f339b7` (para GPT-4o y embeddings).
2. `python3 tools/local_stack.py init && python3 tools/local_stack.py up` en `pipesor-workspace`.
3. Credenciales privadas, nunca en Git ni en chats: la clave PEM de la GitHub App en la ruta de
   `~/.config/pipesor-local/ingestion-capture.properties`, el *client secret* de la App en
   `~/.config/pipesor-local/github-client-secret` (0600) y `authority.json` con la instalación
   admitida. Se comparten por un canal seguro (gestor de contraseñas). El login exige ser
   administrador del repositorio registrado.
4. `./mvnw -B -ntp -DskipTests package` en cada servicio Java y
   `python3 tools/local_stack.py services-start`.
5. Login en `http://127.0.0.1:8081/api/v1/auth/github/start?return_to=/operations`; el dashboard
   recibe `/auth/complete?handoff=…` (o `?error=<code>` si falla) y lo canjea en
   `POST /api/v1/auth/session`, cuya respuesta incluye también `returnTo`.
6. Registrar el workflow, pedir el análisis de un run fallido y observar los logs en
   `~/.local/state/pipesor-local/`.

El emulador conserva los mensajes como máximo una hora: para probar NLP más tarde se analiza
otro run fallido (por ejemplo `43054769400`) en lugar de esperar los mensajes ya publicados.

### Puntos de integración para NLP, RAG y frontend

- **NLP → Correlation:** `POST http://127.0.0.1:8085/internal/v1/processed-evidence` (Azure:
  `https://correlation.internal.<env-domain>/…`) con token de workload `nlp`
  (`aud urn:pipesor:api:correlation`, rol `Nlp.ProcessedEvidence.Send`), `Idempotency-Key` =
  `message_id`, `X-Correlation-ID`. Correlation acepta `contract_version` 2.0, 2.1 y 2.2; con 2.1
  o 2.2 el `source_locator` debe cumplir la gramática 2.2 y se reenvía sin cambios. Correlation
  descubre la clave de NLP en `http://127.0.0.1:8084/.well-known/jwks.json`, por lo que NLP debe
  publicar su JWKS aunque no tenga otra API. Respuestas: 200 `accepted|duplicate`; 503 = reintentar
  (abandonar el mensaje); 400/409/413/422 = definitivo.
- **Recommendation → RAG:** `POST http://127.0.0.1:8087/internal/v1/retrieval/query` con token de
  workload `recommendation` (`aud urn:pipesor:api:rag`, rol `Rag.Query`); RAG valida contra
  `http://127.0.0.1:8086/.well-known/jwks.json`. El cuerpo y la respuesta no cambian respecto a
  ADR-021/contrato RAG v0.1.
- **Frontend:** API según `mvp-http-api-v1.md`. Las rutas de discovery existentes de Ingestion
  paginan con `limit` (obligatorio) y `cursor`; la lista de runs fallidos usa
  `pageSize`/`pageToken`. CORS permite solo `PIPESOR_DASHBOARD_ORIGIN`
  (`http://127.0.0.1:5173` en local).
- **IaC:** variables y roles del manifiesto; Ingestion además necesita las variables
  `PIPESOR_GITHUB_*` (ver README de Ingestion) y la callback de Azure registrada en la App.

## Brief para la sesión de Codex

> Copiar este bloque como primer mensaje de la sesión de Codex.

```text
Trabajas en Pipesor (prototipo AIOps de tesis, multirepo en pipesor-org). Otra sesión
(Claude Code) trabaja en paralelo. Antes de tocar código lee, en pipesor-docs (main):
ADR-022, docs/architecture/contracts/platform-identity-v1.md, protected-evidence-v2.2.md,
mvp-http-api-v1.md, docs/development/runtime-manifest.md y
docs/development/mvp-close-coordination.md, más el AGENTS.md de cada repositorio.

Tus repositorios (solo estos): pipesor-frontend, pipesor-nlp-log-processor,
pipesor-rag-retrieval y el nuevo pipesor-scenarios. La IaC (pipesor-iac) NO es tuya. No modifiques los servicios Java,
pipesor-workspace ni los contratos; pide cambios mediante issue.

Plazo: 25/11/2026. Puntos de sincronización en mvp-close-coordination.md.

Entregables:
2. pipesor-frontend: login según §5 del contrato de identidad (start, /auth/complete,
   intercambio del handoff, token solo en memoria); config.json en runtime con las
   URLs de las APIs; un cliente único en shared/api con timeouts, X-Correlation-ID y
   problem+json; lecturas reales para la cola de Operations (GET /api/v1/incidents),
   pipelines, Incident Workspace, diagnóstico por incidente, revisiones y el flujo
   "Analizar ejecución" (repositorios → workflows → runs fallidos → análisis →
   progreso → diagnóstico). Eliminar el pegado de tokens y las rutas DEV de piloto o
   demo del bundle de producción. Diferenciar visualmente evidencia observada,
   hipótesis inferida y fuentes RAG. Schemas Zod alineados con el contrato
   (localizador 2.2). Configuración de Static Web Apps.
3. pipesor-nlp-log-processor: sustituir el spool local por el emulador de Service Bus
   (modo cadena de conexión en local, identidad administrada en Azure); emitir tokens
   de workload según el contrato (firma con Key Vault o con PEM local); HTTP mínimo
   con /health/live, /health/ready y /.well-known/jwks.json; endpoint de Correlation
   configurable con la regla de transporte del contrato; aceptar evidencia 2.0, 2.1 y
   2.2.
4. pipesor-rag-retrieval: validar tokens de workload de plataforma (caller
   recommendation, rol Rag.Query) manteniendo el modo Entra por configuración; prohibir
   backends simulados fuera de tests; consulta pgvector con LIMIT top_k y distancia
   desde SQL; statement timeout; importación de corpus autorizado con procedencia.
5. pipesor-scenarios: repositorio con al menos 10 workflows que fallan de forma
   controlada y distinta (build Maven, test JUnit, dependencia npm, lint, Docker build,
   red/DNS, permisos/secret ausente, timeout, set-up de runner, quality gate), cada uno
   con su causa de referencia documentada fuera del corpus RAG; workflow
   pipesor-report (workflow_run + OIDC) que espera el diagnóstico y lo publica como
   artifact. Protocolo de evaluación en pipesor-docs/docs/research/ (archivo propio):
   escenarios, causa de referencia, medición de tiempo y acierto, rúbrica.

Reglas: rama y PR por repositorio, commits convencionales en inglés, verificaciones de
cada AGENTS.md, ningún secreto en Git, nada de código exclusivo de local en rutas de
producción. Si un contrato no alcanza, detente y propón el cambio.
```
