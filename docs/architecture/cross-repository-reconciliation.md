# Reconciliación entre repositorios — 06/11/2026

Corte de evidencia: 06/11/2026 (America/Lima). Informe documental, no ADR ni
aprobación de arquitectura/despliegue. Distingue lo declarado en decisiones, código
integrado, propuestas y recursos realmente observados. Las fuentes vecinas se
consultaron en copias temporales de sus ramas por defecto; no se modificaron.

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

Ese contenido no está disponible en el checkout sincronizado. Los hashes y las
menciones externas no recuperan sus bytes ni prueban aprobación. PD-033–036 se
usan en los servicios para eventos, APIs, entrega backend–IaC y acceso de workflows;
este informe registra esas referencias externas sin reconstruir las entradas ni
atribuirlas al registro de 32 PD integrado. La autoridad Jhon Galvez/Ramiro Guzman
es reportada por esos documentos; no se verificó CODEOWNERS ni la regla de una o
ambas aprobaciones. Recuperar una revisión revisada y publicable sigue pendiente.

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
| RAG / Python–FastAPI | Diagnóstico → recuperación pgvector; posee `knowledge` | Corpus, embeddings/dimensión, acceso y actualización; Foundry no los resuelve. |

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
| XR-003 — AI | [Foundry][baseline] registra aceptación de cuenta/proyecto Entra-only, en vez del candidato de cuenta OpenAI independiente; modelo mantiene API externa Azure OpenAI y propiedades NLP/RAG sin acceso explícito. | Precisar compatibilidad endpoint/SDK, deployment/modelo/geografía, embeddings y grants. Foundry no selecciona modelos ni autoriza Search/agentes/nuevos servicios. |
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
