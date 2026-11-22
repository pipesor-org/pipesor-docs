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
| Codex | `pipesor-iac`, `pipesor-frontend`, `pipesor-nlp-log-processor`, `pipesor-rag-retrieval`, nuevo `pipesor-scenarios`; en `pipesor-docs`, el protocolo de evaluación (archivo propio en `docs/research/`) | IaC y despliegue, dashboard real con login, NLP y RAG según los contratos, repositorio de escenarios, corpus RAG y protocolo de evaluación |

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

## Brief para la sesión de Codex

> Copiar este bloque como primer mensaje de la sesión de Codex.

```text
Trabajas en Pipesor (prototipo AIOps de tesis, multirepo en pipesor-org). Otra sesión
(Claude Code) trabaja en paralelo. Antes de tocar código lee, en pipesor-docs (main):
ADR-022, docs/architecture/contracts/platform-identity-v1.md, protected-evidence-v2.2.md,
mvp-http-api-v1.md, docs/development/runtime-manifest.md y
docs/development/mvp-close-coordination.md, más el AGENTS.md de cada repositorio.

Tus repositorios (solo estos): pipesor-iac, pipesor-frontend, pipesor-nlp-log-processor,
pipesor-rag-retrieval y el nuevo pipesor-scenarios. No modifiques los servicios Java,
pipesor-workspace ni los contratos; pide cambios mediante issue.

Plazo: 25/11/2026. Puntos de sincronización en mvp-close-coordination.md.

Entregables:
1. pipesor-iac (dev, westus3, suscripción existente; el tenant no permite app
   registrations): Key Vault de aplicación y vault de custodia OAuth; claves RSA de
   firma por workload y pipesor-session-signing; secretos de la GitHub App como
   referencias; identidades y asignaciones de rol del manifiesto; topic
   workflow-evidence y sus tres suscripciones con filtros; siete Container Apps con
   ingress, puertos, probes y variables del manifiesto; principales Entra de PostgreSQL
   por servicio y extensión vector; Static Web Apps; Application Insights; workflow de
   despliegue. Toda aplicación real (apply) requiere la autorización explícita de Jhon.
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
