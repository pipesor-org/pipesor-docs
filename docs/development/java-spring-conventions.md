# Convenciones Java y Spring

Acuerdo inicial del 2026-11-06, refinado por indicación del usuario tras la revisión de Clean Architecture de Pipeline Service en la misma fecha. El acuerdo y su refinamiento están integrados en main; revisiones consultadas: `d44b45b` y `18dacfb`, respectivamente. Aplicar junto con las [convenciones backend](backend-conventions.md). Alcance: ingestion_normalization_service, pipeline_service, log_event_service, evidence_correlation_engine y recommendation_service. Maven, Java/Spring Boot según ADR-018 y la base de desarrollo del servicio. Las versiones exactas están fijadas en el `pom.xml` de cada servicio (al 24/11/2026, Java 25 y Spring Boot 4.1.2).

## Estructura por funcionalidad

```text
src/main/java/<paquete-base>/<servicio>/
  <funcionalidad>/
    domain/
      model/
        aggregates/
        entities/
        valueobjects/
      services/
    application/
      commands/
      queries/
      services/
      commandhandlers/
      queryhandlers/
      ports/
    interfaces/
      rest/
        resources/
        transform/
      messaging/
        transform/
    infrastructure/
      persistence/
        jpa/
  shared/
    domain/model/
    infrastructure/persistence/jpa/
  configuration/
src/main/resources/
  application.yml
  db/migration/
src/test/java/<paquete-base>/<servicio>/
src/test/resources/
```

Crear únicamente los paquetes necesarios. Las pruebas reflejan la funcionalidad. Un solo proyecto Maven por servicio, con wrapper; no añadir módulos o bibliotecas compartidas antes de tener reutilización comprobada.

## Contratos, handlers y transformers

Command y Query son records internos inmutables en application/commands y application/queries. Las interfaces que describen casos de uso viven en application/services y las implementaciones en application/commandhandlers y queryhandlers. Reservar domain/services para operaciones propias del negocio, no coordinación de casos de uso. Dominio y aplicación permanecen libres de Spring, JPA, tipos Azure y recursos HTTP. Registrar handlers mediante configuración externa con dependencias por constructor. Esta revisión sustituye expresamente la ubicación inicial de estos contratos en domain. No crear interfaces para toda clase ni un dispatcher genérico.

Los puertos de I/O requeridos por aplicación viven en application/ports y sus implementaciones en infrastructure. El dominio no depende de aplicación. El caso de uso determina la atomicidad necesaria, y la composición técnica implementa su transacción sin anotar el handler con Spring. En una consulta simple la transacción puede envolver el adaptador y su transformación. Un comando con varias escrituras requiere una transacción alrededor de todo el caso de uso mediante infraestructura; no dividirla entre adaptadores. Las queries devuelven proyecciones específicas cuando corresponda; no exponer entidades JPA.

Transformaciones: recurso REST o mensaje → Command/Query; resultado de dominio o proyección → recurso de respuesta; entidad JPA ↔ dominio en infraestructura. Los transformers de interfaces viven junto al adaptador correspondiente, los de persistencia junto a JPA. Usar métodos explícitos inicialmente; invocar constructores/fábricas del dominio para preservar invariantes.

## Agregados y objetos de valor

Entity expresa identidad estable. Aggregate delimita invariantes que deben mantenerse consistentes y sus modificaciones pasan por una raíz, que también es Entity. Una tabla o una FK no determina un agregado. Documentar invariantes, raíz y atomicidad antes del primer comando; no crear una base AggregateRoot vacía para simular el diseño.

Un Value Object aporta significado, igualdad por valor, validación o prevención de confusiones concretas. UUID e Instant ya son tipos de valor útiles. Introducir RepositoryId, PipelineId o un identificador externo propio cuando las reglas o los casos de uso justifiquen esa distinción; no envolver todos los campos. La lectura CQRS puede usar proyecciones sin reconstruir agregados.

## Persistencia y clases base

Spring Data JPA con Hibernate es la opción acordada para servicios Java con tablas propias. Distinguir el puerto de lectura de aplicación, su adaptador JPA y la interfaz técnica de Spring Data (por ejemplo SpringDataGitHubRepository). Un repositorio de agregados para comandos debe expresar el contrato en términos de dominio; no confundirlo con esa interfaz técnica. Mantener modelos JPA en infraestructura y dominio libre de anotaciones ORM. Usar proyecciones o SQL explícito cuando una consulta lo justifique. Sin navegación JPA entre contextos; asociaciones dentro del contexto solo cuando el caso de uso las requiera.

Usar la estrategia estándar soportada por la versión de Spring Boot/Hibernate elegida para nombres físicos snake_case en minúsculas, sin normalizador propio. Declarar explícitamente @Table(name = "pipeline_executions", schema = "ops") y nombres de columnas cuando corresponda al modelo. No inferir pluralización desde nombres de clases; JPA y Flyway deben coincidir con model/domain.yml.

- shared/domain/model: base mínima de Entity con identidad java.util.UUID. Una base AggregateRoot solo se añade si aporta comportamiento común. No heredar clases JPA desde dominio.
- shared/infrastructure/persistence/jpa: bases con @MappedSuperclass para identidad UUID y campos temporales que el modelo de cada tabla admita. Separar base de creación y base mutable con updatedAt cuando se necesite; evitar imponer campos por herencia.
- configuration: activación de auditoría técnica Spring Data JPA cuando se introduzca. Instant para fechas Java; persistencia timestamptz. La estrategia debe preservar createdAt y actualizar updatedAt en escrituras reales. Las escrituras SQL que omitan callbacks JPA deben mantener los mismos invariantes explícitamente y tener verificación.

No crear las bases antes de su primer uso. No añadir atributos o listeners a tablas que no los contemplan. updated_at requiere primero la evolución del modelo descrita en las convenciones backend. Asignar UUID en el owner antes de persistir y verificar el comportamiento de inserción de JPA con IDs asignados; no delegar en secuencias enteras.

## Migraciones

Flyway es la herramienta acordada para servicios Java con tablas propias. Migraciones SQL versionadas en src/main/resources/db/migration, con nombres V1__descripcion.sql, V2__descripcion.sql. Mantener las aplicadas inmutables; cambios nuevos en nuevas versiones. No usar Hibernate para crear/actualizar el esquema ni mezclar schema.sql como mecanismo paralelo; usar ddl-auto=validate.

Derivar las migraciones del modelo fuente vigente y sus decisiones, preservando constraints e invariantes documentados. Probar aplicación de migraciones y restricciones sobre PostgreSQL aislado. El SQL generado por la documentación es un derivado, no la autoridad ni un historial Flyway.

La selección de Flyway no decide ejecución automática en producción. Para el MVP, el [manifiesto de runtime](runtime-manifest.md) fija Flyway al arrancar y la tabla de historial de Log/Event y Correlation; credenciales, conectividad, secuenciación, compatibilidad y recuperación de otros entornos siguen en PD-035; no crear roles, grants o recursos desde una migración funcional por inferencia. Servicios sin tablas propias no incorporan Flyway por obligación.

## OpenAPI

Usar springdoc-openapi compatible con Spring Boot. Mantener anotaciones y recursos en interfaces/rest, sin contaminar dominio. Generar OpenAPI desde la implementación y comprobar que coincide con los intercambios acordados; no mantener una segunda especificación manual divergente. Swagger UI sirve para explorar la API, su habilitación y acceso por entorno se definirán en el contrato runtime. No publicar documentación sin revisar su acceso.

## Referencias de herramientas

- [Spring Boot: acceso a datos y naming](https://docs.spring.io/spring-boot/how-to/data-access.html).
- [Spring Boot: inicialización y migraciones](https://docs.spring.io/spring-boot/how-to/data-initialization.html).
- [Springdoc OpenAPI](https://springdoc.org/).

Las APIs y versiones concretas se verifican al introducir o actualizar dependencias; este acuerdo no certifica la compatibilidad de la combinación fijada en cada servicio.
