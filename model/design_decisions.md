# Decisiones propuestas del diseño de clases

SSOT exclusivo: `model/design.yml`, versión 1.2.0. Las clases de CD-1..CD-3
son `proposed`: este repositorio DaC no contiene el microservicio Java/Spring
Boot. Desde DC-007, CD-4..CD-11 añaden clases `implemented` transcritas del
código de cada servicio, que no son propuestas. Estas decisiones concretan
clases dentro de las fronteras ya aprobadas; no modifican ADR-018 ni resuelven
preguntas del dominio.

## DC-001 — Controllers separados para commands y queries

`DiagnosisCommandController` y `DiagnosisQueryController` delegan a contratos
de aplicación distintos. Human Review usa la misma separación con sus dos
controllers. Los controllers pertenecen a `diagnostic_api_component`, incluso
cuando se muestran como entrada al zoom de Human Review. No contienen reglas
de dominio; sus firmas abrevian los datos REST, sin introducir rutas nuevas.
Los commands devuelven UUID; las queries solo leen y componen resultados.

## DC-002 — Puertos de aplicación para RAG y LLM

`KnowledgeRetrievalPort` y `DiagnosticLlmGateway` son interfaces de salida.
El orquestador depende de ellas; los adaptadores HTTP las implementan en
infraestructura. El gateway acepta únicamente `SanitizedDiagnosticContext`,
con las tres partes del contrato LLM vigente. La traducción RAG ocurre dentro
de su adaptador y conserva provenance; ninguna respuesta externa alcanza el
dominio con tipos de proveedor.

## DC-003 — ACL de respuesta Azure OpenAI

`LlmResponseTranslator`, en `infrastructure.acl`, convierte la respuesta Azure
en `Diagnosis` y sus recomendaciones internas. El gateway devuelve este
resultado interno, todavía sin persistir. `DiagnosticOutputComposer` asocia
contexto, evidencia y fuentes; el repositorio inserta el snapshot y sus vínculos.
Los tipos de SDK/HTTP/JSON de proveedor quedan dentro de infraestructura.

## DC-004 — DiagnosticView como proyección de aplicación

`DiagnosticView` expresa el read model de `diagnostic_output`, con sus campos
canónicos. Usa el estereotipo permitido `ValueObject` y `role: read_model`;
no es un Aggregate ni una entidad persistida. Las queries usan exclusivamente
métodos de lectura de los repositorios existentes. La proyección se compone
en aplicación, sin SQL views ni nuevas tablas. `DiagnosticApiMapper` se omite
porque no añade semántica al zoom; la adaptación simple queda en el controller.

## DC-005 — AuditTrailPort transversal con metadata mínima

`AuditTrailPort` aísla el mecanismo técnico de registro de revisión humana.
`PostgresAuditTrailAdapter` escribe en `audit.audit_events`, mediante la
excepción transversal ya documentada por ADR-011/DD-016. Su operación recibe
solo IDs, actor, decisión, tiempo y correlación; excluye comentario, causa,
evidencia y contenido sensible. No constituye un nuevo Bounded Context.

## DC-006 — Repositorios de dominio sin dependencia JPA

`DiagnosisRepository` y `HumanReviewRepository` son interfaces en
`domain.services`. Sus adaptadores viven en `infrastructure.persistence.jpa`.
`ProbableCause` envuelve exclusivamente el texto existente. Las asociaciones
del Aggregate se representan por relaciones de composición, sin añadir
atributos persistidos a las columnas de `domain.yml`. Los IDs entre contextos
no se convierten en asociaciones ORM. HumanReview valida la decisión sin
reescribir el snapshot diagnóstico original.

Las assumptions DA-001 a DA-006 están en el SSOT. DQ-002 se referencia sin
resolverla; DCQ-001/DCQ-002 dejan abiertas la política concreta de riesgo y
la forma final del contrato REST de recepción. DCQ-003 conserva abierta la
rehidratación del contexto operacional al consultar el read model; no elige
almacenamiento ni una comunicación nueva. Las restantes preguntas de
`domain.yml` siguen intactas. Ninguna de estas decisiones necesita una nueva
decisión arquitectónica para generar las figuras propuestas.

Alineación ADR-019: las referencias de ingress de los controllers propuestos apuntan ahora a la proyección de dashboard → Diagnostic API por ACA, sin salto APIM. Las clases continúan propuestas y DCQ-001–003/DQ-002 abiertas; no se fijan rutas ni DTO.

## DC-007 — Diagramas por bounded context y estado de implementación

Autorización: el responsable aprobó el 27/11/2026 (decisión 4) «autorizar
diagramas de agregados por bounded context, con estado por clase y referencias
al código; en los CD-1..3, marcar las 14 clases que no existen». Petición
original: UML de clases con las raíces de agregado y sus entidades y value
objects principales de cada bounded context, marcando lo propuesto frente a lo
implementado. La evidencia sale de las revisiones fijadas en
`model/implementation_status.yml` (corte 27/11/2026) con referencias
`repo:ruta:línea`.

Alcance:

- Las 38 clases de CD-1..CD-3 siguen `status: proposed`, con su contenido y
  sus reglas. Cada una gana `implementation` (estado de `evidence.STATUSES`,
  evidencia o, si falta, `reason`, y nota): 7 `implemented`, 5 `partial`,
  11 `divergent`, 14 `not_implemented` y 1 `external`. Criterio: `implemented`
  si un tipo del código cumple la misma responsabilidad con un contrato
  equivalente (el nombre puede variar y la nota lo dice); `partial` si cubre
  solo parte de atributos, métodos o relaciones; `divergent` si la
  responsabilidad existe con otra forma (clases fusionadas, cola asíncrona,
  JDBC, un record de aplicación en lugar de un agregado); `not_implemented` si
  no hay tipo, y `reason` indica a dónde fue la responsabilidad (la evidencia
  opcional solo localiza ese sustituto); `external` para Azure OpenAI, fuera del
  código de los servicios.
- CD-4..CD-11 (uno por contenedor; dos en Ingestion) muestran 90 clases
  `status: implemented` y 85 relaciones del código: raíces, entidades, value
  objects, enums y, cuando aclaran la persistencia, puertos, adaptadores y
  filas JPA/SQLAlchemy. Son una selección de lo principal, no un inventario
  del servicio; las notas de CD-4..CD-6 nombran las tablas y tipos que no se
  dibujan. CD-9 enfrenta los records de Recommendation a
  los agregados propuestos (`Diagnosis`, `HumanReview`, `Recommendation`, sin
  miembros) con la relación `realizes`, que exige que la evidencia de la
  propuesta cite ese código.
- Persistencia: `persisted_as` sigue exigiendo coincidencia exacta con
  `model/domain.yml` y solo se usa cuando la clase coincide columna a columna
  (filas JPA/SQLAlchemy y `GitHubRepository`). Las demás clases de datos
  declaran `storage` (`mapped`, `json_column`, `flattened` o `not_persisted`)
  con tablas del mismo contenedor.
- `design_rules.containers` sustituye al contenedor único: lenguaje y
  framework iguales a `backend` en `model/architecture.yml`, repositorio de
  evidencia, paquete base, almacén y ruta de navegación. recommendation_service
  conserva las reglas de CD-1..CD-3 (CQRS lógico, PostgreSQL común, sin event
  sourcing, GitHub de solo lectura).
- La capa de una clase de código se deriva de su paquete; si el paquete no
  nombra capa (`diagnosis.review`, `receipt`, módulos planos de RAG) es
  `unlayered`. Es un hecho del código y no responde la pregunta 24.
- Impresión A4: cada figura declara `print_parts`, partes coherentes que juntas
  conservan todos los miembros y relaciones. El generador elige dirección,
  agrupación y página para que ningún texto quede por debajo de 8 pt.

Límites: no cambia `model/architecture.yml` ni `model/domain.yml`; las clases
`proposed` siguen siendo propuesta y un estado `implemented` no aprueba el
diseño ni prueba comportamiento en ejecución. Quedan abiertas DQ-002,
DCQ-001..DCQ-003 y la pregunta 24 de la reconciliación (paquetes, JPA frente a
JDBC): `divergent` registra que el código usa JDBC o fusiona clases, sin decidir
qué forma es la correcta, y las rutas citadas en las notas describen el código
sin cerrar DCQ-002.
