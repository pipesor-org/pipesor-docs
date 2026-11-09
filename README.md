# Pipesor — documentación arquitectónica

Pipesor es un prototipo de diagnóstico asistido de fallos CI/CD identificados por GitHub Actions. Su diseño contempla capturar y proteger evidencia, correlacionar contexto, recuperar conocimiento mediante RAG y producir una causa probable con recomendaciones y revisión humana.

Este repositorio mantiene la arquitectura como código: modelos, decisiones, validadores y documentación derivada. Sirve como referencia para agentes que trabajen en repositorios independientes de backend e infraestructura como código (IaC), conforme a [ADR-018](docs/architecture/decisions/ADR-018-application-architecture-ddd-cqrs.md). Los modelos y diagramas describen diseño; no acreditan servicios implementados ni recursos desplegados.

El repositorio se mantiene en `pipesor-org/pipesor-docs`. Los nombres e IDs históricos se conservan para mantener la trazabilidad.

## Estado entre repositorios — 06/11/2026

La [reconciliación actual](docs/architecture/cross-repository-reconciliation.md)
registra revisiones exactas de IaC, frontend y los siete servicios. IaC ya contiene
fundaciones opcionales de ACA/red/monitoring, Service Bus, PostgreSQL, Foundry y
SWA Free, además de state y presupuesto; no contiene aplicaciones backend ni
acredita recursos desplegados. Los servicios siguen en readiness y el frontend
usa fixtures, sin integración backend ni auth implementada. La landing accesible
es `pipesor-landing` (no `pipesor-landing-page`); contiene código/configuración
Workers, pero su despliegue no está verificado.

[ADR-019](docs/architecture/decisions/ADR-019-align-mvp-with-iac.md) alinea ahora el modelo canónico con las decisiones MVP de IaC: ingress nativo de ACA sin gateway dedicado, exclusión de Blob de workload, fundación Microsoft Foundry y preparación Terraform dev-only temporal. Los diagramas derivan de ese modelo; no acreditan despliegue. Se conservan Entra ID, las siete fronteras backend, PostgreSQL/pgvector y la retención de 365 días. Exposición/auth, contratos, modelos AI y garantías de recuperación/retención siguen pendientes. Los antecedentes APIM/Blob se leen con la evolución de ADR-019.

## Lectura y estructura

Leer primero [AGENTS.md](AGENTS.md), que define las reglas de trabajo. Consultar después las fuentes de la materia afectada y los ADRs aplicables. [Overview.md](Overview.md) ofrece una síntesis histórica con su propia fecha y revisión de referencia; sus resultados de validación no certifican el checkout actual.

| Ruta | Responsabilidad |
|---|---|
| `model/` | Arquitectura, dominio persistente, diseño de clases, decisiones explicativas y modelos de presentación. |
| `docs/architecture/decisions/` | ADRs y evolución de decisiones arquitectónicas. |
| `docs/architecture/cross-repository-reconciliation.md` | Corte actual de evidencia integrada, decisiones externas, drift y dependencias entre repositorios. |
| `docs/sources/` | Copias íntegras de fuentes y registro de procedencia, integridad y aprobación verificable. |
| `docs/research/` | Derivación funcional y propuestas, sujetas a los límites arquitectónicos aprobados. |
| `tools/` | Validadores, generadores y comprobaciones del entorno documental. |
| `tests/` | Pruebas de modelos, validadores y generación; no prueban la ejecución del producto. |
| `out/` | Diagramas, guías y diccionario generados y versionados. |
| `build/` | Salidas generadas temporales, ignoradas por Git. |
| `Makefile`, `requirements.txt` | Interfaz de ejecución y dependencias Python de las herramientas documentales. |

## Fuentes de verdad y autoridad

La autoridad se aplica **por materia**, conforme a ADR-018 y a la gobernanza del modelo; no hay una precedencia lineal que permita reemplazar unas fuentes por otras indiscriminadamente.

| Materia | Fuente y límite |
|---|---|
| Alcance | Project Charter referenciado en `architecture.yml`. |
| Arquitectura | [model/architecture.yml](model/architecture.yml), sus invariantes y los ADRs `Accepted` aplicables, teniendo en cuenta sustituciones posteriores. |
| Tecnología | `tech_drift_resolutions.md` y los ADRs tecnológicos aplicables, según la gobernanza existente. |
| Dominio persistente | [model/domain.yml](model/domain.yml), explicado por [model/domain_decisions.md](model/domain_decisions.md), dentro de los límites de ADR-018. |
| Diseño de clases propuesto | [model/design.yml](model/design.yml), explicado por [model/design_decisions.md](model/design_decisions.md). Su autoridad describe la propuesta, no su aprobación ni implementación. |
| Presentación | [logical_presentation.yml](model/logical_presentation.yml), [physical_presentation.yml](model/physical_presentation.yml) y [c4_container_presentation.yml](model/c4_container_presentation.yml): composición visual y proyecciones de hechos arquitectónicos existentes. No autorizan nuevos elementos, tecnologías ni relaciones. |
| Derivación funcional | [Arquitectura de información](docs/research/arquitectura-informacion.md), contrastada con las decisiones posteriores y las fuentes anteriores. Sus ejemplos de API no son contratos implementados. |

`model/db.dbml` es **generado desde `model/domain.yml`**, al igual que SQL, ER y diccionario. No se edita manualmente ni constituye una fuente independiente. Tampoco lo son `out/`, `build/`, README u Overview.

El Charter v1.3 y el drift están disponibles en raíz y como copias íntegras en [docs/sources/](docs/sources/README.md), cuyo registro distingue autoridad declarada de aprobación verificable. Los originales de raíz se conservan para las referencias existentes. TI y los Excel citados siguen ausentes; `A-011` conserva una referencia de ausencia parcialmente desactualizada, registrada externamente sin modificar el modelo. Consultar la [reconciliación de las 50 resoluciones](docs/architecture/reconciliation.md) y el [índice de decisiones y evolución](docs/architecture/decisions/index.md). Estos índices son descriptivos y no resuelven TMD ni CF-001. No atribuir a las fuentes ausentes contenido adicional ni reconstruirlo por inferencia.

## Estados y preguntas abiertas

- **Decisiones aprobadas:** los ADRs `Accepted` documentan decisiones, con el alcance y las sustituciones que indiquen. `confirmed` en un modelo expresa confirmación documental, no despliegue. El modelo arquitectónico global sigue en estado `draft`.
- **Diseños propuestos:** las clases de `design.yml` están marcadas `proposed`. Generar sus figuras no aprueba ni implementa esas clases.
- **Supuestos e inferencias:** conservar las marcas `assumption`, `inferred` e `ia_only`; no promoverlas a requisitos aprobados.
- **Preguntas abiertas:** revisar `open_questions` en arquitectura, dominio y diseño. Una lista vacía en arquitectura no cierra las preguntas de los otros modelos ni los detalles expresamente sin especificar.
- **Artefactos derivados:** representan las fuentes y sus estados; no crean decisiones ni demuestran comportamiento operativo.

Los ADRs históricos se leen junto con sus sustituciones: ADR-009/010/011/012 retiran capacidades previamente descritas, y ADR-015/016/017 refinan fronteras y responsabilidades. Conservar el historial no convierte cada afirmación histórica en una instrucción vigente.

## Contribución y validación

1. Delimitar la tarea y leer AGENTS.md, las fuentes afectadas y los ADRs aplicables. Para consumo desde backend o IaC, identificar la revisión consultada y los IDs de elementos, relaciones e invariantes relevantes.
2. Distinguir corrección documental de cambio arquitectónico. Cambiar arquitectura, tecnología, estados o resolver preguntas requiere instrucción explícita; una tarea de implementación no autoriza completar vacíos por cuenta propia.
3. Modificar únicamente los archivos autorizados. Los cambios de modelo son primero en su fuente; los derivados se actualizan mediante el generador correspondiente. Preservar IDs, referencias e historial salvo autorización expresa.
4. Validar según el tipo de cambio y reportar resultados, limitaciones y pendientes. Ante contradicciones o información ausente, detener la parte afectada y reportarla sin inventar una decisión.

**Auditorías y tareas de solo lectura:** no requieren generadores, `make all` ni modificaciones de archivos. Ejecutar solo comprobaciones compatibles con las restricciones de la tarea. Los cambios exclusivamente documentales requieren revisar coherencia, enlaces y diff; no requieren regenerar artefactos.

Para cambios que afecten modelos o generación, usar el [Makefile](Makefile) como interfaz canónica, con las dependencias existentes disponibles:

```sh
make validate
make validate_design
```

`make validate` comprueba arquitectura y dominio; `make validate_design` comprueba además el diseño. Cuando corresponda y esté dentro del alcance, ejecutar el generador afectado, `make all` y las pruebas relevantes. `make all` genera archivos y no ejecuta la suite unittest. El Makefile utiliza `.venv/bin/python`; las herramientas externas dependen del target y se comprueban en `tools/check_env.sh`. No instalar dependencias ni ampliar el alcance para ocultar un fallo.

Para comprobar cambios con las dependencias ya instaladas:

```sh
make test
PATH="$PWD/tools/node_modules/.bin:$PATH" make all
PATH="$PWD/tools/node_modules/.bin:$PATH" make test-postgres
```

`make test` cubre reglas y contratos de generación. `make test-postgres` aplica DDL generado en PostgreSQL/pgvector aislado, sin puertos host ni credenciales de aplicación; requiere Docker y la imagen fijada por la herramienta. No aprueba runner, permisos ni integración productiva del conector.

Si el entorno impide usar Make, reportar la limitación. Los validadores equivalentes pueden ejecutarse directamente con Python y PyYAML ya disponibles, sin generación:

```sh
python3 -B tools/validate.py model/architecture.yml model/domain.yml
python3 -B tools/validate_design.py model/design.yml model/architecture.yml model/domain.yml
```

El [registro agregado de decisiones pendientes](docs/architecture/pending-decisions.md) centraliza preguntas abiertas, discrepancias y evidencias faltantes, conservando los estados de sus fuentes. La recuperación de fuentes ausentes, el cierre de esos asuntos, los contratos entre repositorios y el fortalecimiento de la reproducibilidad permanecen como trabajo posterior.

## Convenciones de desarrollo backend

Consultar las [convenciones comunes](docs/development/backend-conventions.md) y las [convenciones Java/Spring](docs/development/java-spring-conventions.md), acordadas para la primera iteración y revisables. No sustituyen los modelos fuente ni aprueban contratos pendientes.

## Conexión GitHub y alta de workflows

[ADR-020](docs/architecture/decisions/ADR-020-github-user-access-and-workflow-onboarding.md) registra la decisión aprobada el 06/11/2026: Entra vinculado explícitamente con GitHub, tokens de usuario para selección/acceso humano e installation tokens para monitoreo continuo. Dashboard, Ingestion y Pipeline tienen cambios directos; Log/Event y Recommendation tienen dependencias de autorización para sus APIs humanas. No se añade microservicio ni acceso GitHub a Python/correlación. La política funcional queda aprobada; DD-020 concreta después almacenamiento técnico y modo de custodia localmente, conservando los detalles operativos pendientes. El código local y los diagramas no prueban integración ni despliegue.

El 07/11/2026 el usuario aprobó explícitamente `github-connector-draft-0.2`: «Propuesta aprobada». [DD-020 y la definición física](model/domain_decisions.md#DD-020) adoptan localmente cuatro tablas de metadata del schema `ingestion`, ownership de Ingestion, y principios OBO, Key Vault Secrets y validez limitada a petición. [model/domain.yml](model/domain.yml) es la SSOT; DBML/SQL/ER/diccionario se regeneran desde ella. El [contrato semántico de Ingestion](https://github.com/pipesor-org/pipesor-ingestion-normalization-service/blob/main/docs/deployment-contract.md#connector-contract-proposal-for-decision) conserva binding/API. Aceptado localmente no significa integrado en main, recurso provisionado o integración segura desplegada. [PD-027/034/035](docs/architecture/pending-decisions.md) conservan configuración de identidad, protocolos y responsabilidades operativas pendientes sin reabrir las decisiones aprobadas; no se reescribe el snapshot histórico.

El 08/11/2026 el usuario indicó «Vamos a por ello» tras el plan de captura/publicación durable: [DD-021](model/domain_decisions.md#DD-021) adopta localmente cuatro tablas adicionales de Ingestion en `domain.yml` 1.3.0 (25 en total), ledger de recepción/aliases/observaciones/salidas, bytes protegidos inmutables y plan cerrado antes del primer envío. La generación y PostgreSQL aislado validan restricciones locales; supplier de scope, corte de revocación, presupuestos, horizontes y purga de metadata siguen pendientes antes de activar captura. No amplía permisos, DD-020 ni ownership de Pipeline/Log-Event.
