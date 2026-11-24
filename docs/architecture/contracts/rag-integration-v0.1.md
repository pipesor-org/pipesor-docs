# Contrato de integración RAG–Recommendation–IaC v0.1

Estado: **aprobado por el usuario el 16/11/2026 para desarrollo y preparación**.
Evidencia: tras presentar la propuesta v0.1, el usuario indicó «OK, aprobado.
Documenta esto, sube el PR y dime cuales son las preguntas abiertas que tienes
para proceder sin temor».

La aprobación fija las decisiones de este contrato; no acredita disponibilidad,
implementación, integración, asignaciones de permisos ni recursos desplegados.
Las entradas pendientes deben validarse antes de activar el entorno. No autoriza
por sí sola aprovisionamiento, migraciones de entorno o uso de datos reales.

## Alcance y fuentes

Contrato común para `rag_retrieval`, `recommendation_service` e IaC, limitado a
DEV. Conserva PostgreSQL/pgvector, ownership de `knowledge`, autorización por
recurso y procedencia; no incorpora servicios, bases de datos o APIs públicas.

Fuentes consultadas: `pipesor-docs@95c485878d8ca1f3ccf9ba81ef10b027c3c180e8`,
[ADR-007](../decisions/ADR-007-log-processing-and-embeddings.md),
[ADR-018](../decisions/ADR-018-application-architecture-ddd-cqrs.md),
[ADR-019](../decisions/ADR-019-align-mvp-with-iac.md),
[pendientes PD-005/006/023/034/035](../pending-decisions.md), y los checkouts locales de
[RAG](https://github.com/pipesor-org/pipesor-rag-retrieval/blob/main/docs/deployment-contract.md),
[Recommendation](https://github.com/pipesor-org/pipesor-recommendation-service/blob/main/README.md)
e [IaC](https://github.com/pipesor-org/pipesor-iac/blob/main/docs/mvp-resource-baseline.md).
Los enlaces a main evolucionan y no prueban integración de esta decisión.

Este contrato complementa las decisiones previas de embeddings: la selección
concreta deja de estar abierta para RAG. La adopción en modelos canónicos,
validadores, artefactos generados y contratos de cada repositorio queda como
trabajo explícito posterior; este PR documental no altera el grafo ni DDL.
Los `null` históricos de modelo/dimensión no anulan esta aprobación ni acreditan
su adopción. No se extiende automáticamente el cambio al procesamiento NLP.

## Embeddings y persistencia

| Campo | Decisión aprobada |
|---|---|
| Proveedor | Azure OpenAI bajo la fundación Microsoft Foundry existente |
| Modelo | `text-embedding-3-small` |
| Dimensión | **1536**, explícita e idéntica en consultas y documentos |
| Nombre de deployment DEV | `pipesor-dev-embeddings`, a crear y comprobar |
| API de aplicación | Azure OpenAI **v1** |
| SDK Python | Selección estable y pin exacto por el responsable de RAG, previa verificación con Python 3.14 |
| Región y tipo de deployment | Pendientes de disponibilidad, cuota y aceptación de geografía de procesamiento |
| Endpoint | URL real de embeddings suministrada por IaC; no deducirla del endpoint genérico del proyecto |

Divergencia conocida (auditoría 2026-11-24): RAG sólo arranca con el endpoint
`https://ai-pipesor-dev-04f339b7.services.ai.azure.com` y el deployment
`pipesor-dev-embeddings`, fijados en su código; IaC deriva el endpoint del nombre de la
cuenta Foundry y admite otros entornos — pendiente de decisión del responsable.

La API ARM `2025-06-01` que usa Terraform administra recursos; no es la versión
de la API de embeddings. El cliente envía el nombre de deployment como `model`.
Debe utilizar el mismo modelo, dimensión y versión compatible al importar y
consultar, y registrar la versión efectiva del modelo junto con la identidad del
corpus/importación. La forma física de esa metadata se acuerda antes de migrar.

Validar longitud y compatibilidad antes de persistir o comparar. Los vectores
simulados actuales no se mezclan con embeddings reales: antes de habilitar Azure
se requiere inventario de datos existentes y plan revisado de reimportación o
re-embedding. No borrar ni convertir silenciosamente datos. La adopción de
`vector(1536)` y del índice exige migración y verificación propias del servicio.
Este contrato no selecciona todavía algoritmo ni parámetros del índice.

Estado de implementación (auditoría 2026-11-24, informativo; no cierra las preguntas
abiertas 1-3): `pipesor-rag-retrieval` fija `openai==3.51.0` y `azure-identity==1.27.0`
con Python 3.14, llama a `<endpoint>/openai/v1/` con los reintentos del SDK
desactivados y migra a `vector(1536)` con un índice HNSW `vector_cosine_ops`
(`hnsw_ef_search` configurable, 100 por defecto), compatible con ADR-021.

Se aprueba como intención operativa que RAG invoque embeddings directamente
para consultas y que el importador los genere para documentos. Esta relación
requiere adopción model-first antes de activación; no se presume ya dibujada.
El LLM de diagnóstico sigue siendo responsabilidad de Recommendation y su
variante concreta continúa pendiente en PD-026.

## Identidades y autorización

### Embeddings

RAG utiliza la identidad administrada **system-assigned de su Container App**.
No confundirla con las identidades de la cuenta/proyecto Foundry. Proveer
`Cognitive Services OpenAI User` con alcance en la cuenta correspondiente para
el principal que invoque embeddings. El importador necesita su propio principal
y concesión si se ejecuta separado; su identidad concreta queda pendiente.
No usar claves de API ni permisos administrativos como sustituto.

### Recommendation → RAG

Desde [ADR-022](../decisions/ADR-022-platform-identity-without-entra-app-registrations.md),
en el entorno académico sin registros de aplicación, Recommendation presenta un token
de workload del [contrato de identidad de plataforma v1](platform-identity-v1.md):
`iss` `urn:pipesor:workload:recommendation`, `aud` `urn:pipesor:api:rag`, rol único
`Rag.Query` y vida de 300 s como máximo. RAG lo valida en el modo `platform`, que es el
predeterminado. Las reglas Entra de este apartado siguen siendo la configuración por
defecto donde existan registros de aplicación (modo `entra`).

- Mantener `POST /internal/v1/retrieval/query`, contrato `1.0`, y Recommendation
  como único consumidor de negocio previsto. Mantener RAG con ingress interno.
- Usar tokens de acceso Entra de aplicación del tenant del proyecto, con una
  audiencia exclusiva de RAG y rol de aplicación **`Rag.Query`** asignado a la
  identidad de Recommendation.
- Validar firma con claves del emisor configurado, algoritmo permitido, issuer,
  audiencia, vigencia, rol y principal consumidor autorizado. Tenant, issuer,
  audiencia exacta, registros de aplicación y IDs de principales son entradas
  obligatorias del entorno; no se aceptan comodines o valores de ejemplo.
- Recommendation entrega un scope previamente verificado. RAG aplica de nuevo
  los filtros del contrato: tenant, `github_installation_id`,
  `github_repository_id`, pipeline cuando corresponda y revisión de autorización.
  Un token válido no concede acceso a todo el corpus.
- El encabezado simulado sólo sirve en pruebas automatizadas (modo `test`); los
  arranques `local` y `azure` lo rechazan y exigen el modo `platform` o `entra`.

### PostgreSQL

Autenticación Entra y conectividad privada con TLS verificado. Separar principales
para consulta, importación y migración; no distribuir credenciales DDL al runtime.

| Actor | Permisos requeridos, sujetos al binding SQL concreto |
|---|---|
| Runtime RAG | Conexión a la base, `USAGE` de `knowledge` y `SELECT` en sus tablas de documentos/chunks |
| Importador administrativo | Conexión, `USAGE`, lectura y escrituras estrictamente necesarias para importar/versionar en las tablas propias |
| Migrador | DDL autorizado para las migraciones de `knowledge`; creación de `vector` por administración de la base |

RAG mantiene las migraciones funcionales. IaC/administración proporciona red,
base, principales Entra y acceso acordado. Deben fijarse el runner, grants SQL,
privilegios sobre secuencias si aplican, ownership y privilegios futuros, renovación
de tokens y el mecanismo de recuperación antes de ejecutar en un entorno.
Permitir `vector` en IaC no instala la extensión ni ejecuta SQL.

Divergencia conocida (auditoría 2026-11-24): en `pipesor-iac` (`modules/workloads`) el
runtime de RAG y el job `job-rag-migrations` usan la misma identidad `rag`, a la que el
job de base de datos concede `CONNECT, CREATE` en la base y `USAGE, CREATE` en `public`;
no existe principal de importación — pendiente de decisión del responsable.

## Límites operativos y degradación

- Presupuesto total de **15 segundos por consulta RAG**, incluyendo dependencias,
  esperas y reintentos; no es un timeout adicional por cada intento.
- Hasta **2 reintentos** adicionales, sólo para fallos transitorios, con backoff y
  jitter dentro del presupuesto restante. Respetar `Retry-After`; si no cabe,
  devolver fallo recuperable. No reintentar errores de autenticación, permisos,
  contrato o incompatibilidad de vectores.
- Una sola capa controla los reintentos; desactivar reintentos implícitos duplicados
  del SDK. Los timeouts de conexión/pool deben caber en el presupuesto total.
- La cuota RPM/TPM, concurrencia y disponibilidad se registran al validar la
  suscripción; no se inventan a partir de los valores anteriores. El importador
  requiere su propio presupuesto de ejecución antes de usar Azure.
- Consulta válida sin coincidencias: éxito `no_match`. Dependencia no disponible,
  timeout o cuota agotada: `503` recuperable, sin convertir el fallo en lista vacía
  ni fabricar conocimiento. Mantener errores seguros y telemetría sin contenido.
- Recommendation debe acordar su timeout exterior y decidir si puede continuar
  sin RAG, dejando constancia de la falta de contexto. Esa política sigue abierta.

Divergencia conocida (auditoría 2026-11-24): Recommendation aplica 15 s en total,
5 s por intento y 2 reintentos, y no continúa sin RAG: el job de diagnóstico se
reintenta hasta 8 veces, también tras `401`, `403` o `422` de RAG; el presupuesto de
embeddings de RAG (15 s) supera el intento de 5 s — pendiente de decisión del
responsable. La pregunta abierta 5 sigue abierta.

## Corpus autorizado

Integración inicial con material sintético identificado como tal. El corpus real
requiere inventario, procedencia, versión/hash, evidencia de saneamiento, alcance
autorizado y responsable identificado que acredite el uso. Separar evaluación y
soluciones de referencia del corpus y sus fixtures. La aprobación de este contrato
no autoriza automáticamente ningún documento real.

Conservar el importador administrativo idempotente aprobado bajo PD-006, sin API
pública de carga ni aprendizaje automático. PD-023 sigue abierto hasta acreditar
el corpus efectivo y su separación de evaluación.

## Entrega entre responsables

| Responsable funcional | Entrega antes de activación |
|---|---|
| RAG | Adaptadores Entra/embeddings, SDK fijado, validación vectorial, configuración documentada, migraciones y pruebas sintéticas |
| Recommendation | Consumo del contrato v1, scope verificado, token para RAG y política explícita de degradación/timeout |
| IaC/administración | Región/tipo/versión/cuota verificados, deployment/endpoint, identidades, registros/rol Entra, red y binding PostgreSQL |
| Responsable de corpus | Inventario y evidencias de procedencia, autorización, saneamiento y separación de evaluación |

Estos roles funcionales no asignan personas ni conceden permisos. Se deben nombrar
responsables efectivos. Las entradas de entorno son configuración obligatoria,
no valores que el servicio deba adivinar. Cada repositorio adopta el contrato en
su propio PR; no se declara desplegable el código actual por esta aprobación.

## Preguntas abiertas para activar

1. ¿Qué región y tipo de deployment están disponibles con cuota en la suscripción,
   qué geografía procesará los datos y quién la acepta? ¿Qué versión efectiva del
   modelo y cuota RPM/TPM se verifican?
2. ¿Quién implementa y entrega endpoint/deployment, registros Entra y asignaciones?
   ¿Cuáles son tenant, issuer, audiencia, IDs de aplicación/principales y el binding
   de `Rag.Query` para Recommendation?
3. ¿Qué versión exacta del SDK pasa la prueba con Python 3.14 y Entra? ¿Quién realiza
   la prueba autorizada contra el deployment real?
4. ¿Qué principal ejecuta importación y cuál migraciones? ¿Desde qué runner/red,
   con qué grants SQL, renovación de tokens y procedimiento de recuperación?
5. ¿Recommendation puede continuar sin RAG? ¿Qué timeout exterior y estado visible
   corresponden cuando se agota el presupuesto de 15 segundos?
6. ¿Qué documentos reales están autorizados y quién firma su procedencia/uso?
   ¿Dónde queda el inventario y la evidencia de separación de evaluación?
7. ¿Existen datos/vectores persistidos que debamos preservar? ¿Qué plan de migración,
   reimportación y reversión se aprueba antes de adoptar embeddings reales?

Se puede continuar desarrollo y pruebas sintéticas con estas preguntas abiertas.
La activación requiere sus respuestas, adopción en modelos/servicios y evidencia
positiva de integración, además de la autorización de la acción de Azure concreta.

## Referencias técnicas

- [Microsoft: embeddings, API v1 y autenticación Entra](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings).
- [Microsoft: dimensiones admitidas de embeddings](https://learn.microsoft.com/en-us/azure/search/cognitive-search-skill-azure-openai-embedding).

Las referencias respaldan compatibilidad general, no cuota, disponibilidad ni
permisos efectivos de nuestra suscripción.
