# Convenciones comunes de desarrollo backend

Acuerdo inicial autorizado por el usuario el 2026-11-06, revisable en futuras iteraciones. Alcance: los siete servicios backend de ADR-018. Este registro documenta decisiones de desarrollo; no aprueba contratos de integración ni despliegues. Mientras estos cambios no estén integrados, son un acuerdo local de esta sesión, no una revisión publicada en main.

## Autoridad y consumo

Aplicar las fronteras e invariantes de [arquitectura](../../model/architecture.yml), [ADR-018](../architecture/decisions/ADR-018-application-architecture-ddd-cqrs.md), sus sustituciones y el [modelo persistente](../../model/domain.yml). Estas convenciones no agregan relaciones, tablas ni permisos. Conservar los estados proposed, inferred y las preguntas abiertas de las fuentes.

Cada AGENTS.md de servicio debe remitir a este documento; su presencia en otro repositorio no garantiza descubrimiento automático. Consultar el checkout accesible de pipesor-docs o los enlaces a main, identificando revisión y cambios locales por separado. No suponer que un documento local ya está publicado. Registrar excepciones justificadas en la arquitectura del servicio; los cambios de fronteras requieren su decisión arquitectónica correspondiente.

Los servicios Java aplican además [convenciones Java/Spring](java-spring-conventions.md). Los servicios Python conservan FastAPI y su organización propia: no se les impone JPA ni una jerarquía Java. Un servicio sin tablas propias no recibe persistencia ni migraciones por esta convención.

## Arquitectura y contratos

- Organizar por funcionalidad y separar dominio, aplicación, interfaces e infraestructura. Crear carpetas cuando tengan contenido; un paquete no constituye un nuevo microservicio ni un agregado.
- Mantener el dominio independiente de HTTP, broker, ORM y framework. Usar DDD táctico cuando existan invariantes reales; no equiparar tabla y agregado.
- Separar comandos y consultas mediante CQRS lógico sobre la persistencia existente. Usar handlers explícitos y dependencias por constructor; no introducir un bus interno o repositorios genéricos sin necesidad.
- Mantener adaptadores pequeños. Los transformers traducen representaciones; las reglas e invariantes corresponden al dominio. Las consultas pueden devolver proyecciones sin reconstruir agregados.
- Usar APIs y eventos declarados, sin escrituras ajenas, navegación ORM entre contextos ni FK cross-schema. Validar identidad, autorización y datos en las fronteras.

## Asincronía

Un handler no exige ejecución asíncrona. Mantener las relaciones síncronas documentadas. REST responde al terminar el caso de uso por defecto; comandos diferidos requieren contrato de aceptación, seguimiento, errores y durabilidad. No añadir endpoints de comandos donde solo estén declaradas consultas.

La entrada Service Bus es asíncrona. Antes de integrar, acordar identidad del mensaje, duplicación, concurrencia, eventos tardíos/fuera de orden, reintentos y settlement; coordinar confirmación y commit sin asumir exactly-once. Un futuro o un hilo separado no proporciona entrega durable. Estas reglas no cierran PD-031/033/034.

## Identidad y tiempos

- Identificadores internos GUID/UUID, asignados por el servicio propietario; sin IDs enteros autoincrementales. PostgreSQL usa uuid; REST representa estos IDs como string con format uuid. No confundir identidad con autorización.
- Conservar IDs externos de GitHub y correlation_id como texto conforme al modelo. No convertirlos a UUID. La variante/algoritmo UUID se fijará al implementar y no queda elegida aquí.
- Tiempos absolutos en UTC; PostgreSQL usa timestamptz. created_at es fecha técnica de inserción, inmutable, asignada por el owner. No sustituye timestamps de negocio.
- updated_at corresponde a la última modificación persistida de registros mutables; se inicializa con created_at. No añadirlo a registros append-only ni usarlo como control de concurrencia.
- El modelo actual todavía no incluye updated_at. Antes de mapearlo o migrarlo, registrar las tablas aplicables en model/domain.yml y explicar el cambio en model/domain_decisions.md, actualizando derivados mediante generadores y checks pertinentes. Esta convención no agrega columnas implícitas.
- No añadir created_by, updated_by, soft delete o version por herencia sin requisito y definición del modelo. Los metadatos temporales no sustituyen audit.audit_events ni sus contratos pendientes.

## Documentación y verificación

Documentar intercambios REST con OpenAPI: entradas, respuestas, errores, validación, seguridad y ejemplos sintéticos. Acordar contratos antes de integrar consumidores; una especificación generada no aprueba PD-034 ni autoriza exposición pública.

Trabajar en incrementos pequeños: definir comportamiento y criterios de aceptación; revisar callers, contratos, tablas, configuración y pruebas afectados; implementar el flujo necesario; verificar fallos materiales y actualizar documentación en la misma entrega. Incluir pruebas de reglas, contratos y persistencia según el riesgo. Usar PostgreSQL aislado para comprobar SQL y transacciones; no considerar mocks como evidencia de integración real.

Mantener comandos verificados en el README de cada servicio. Fijar dependencias compatibles al introducir el build. Entregar por cambios revisables conforme a la política de contribución; sin despliegues o recursos cloud implícitos.

La [guía CI/CD](cicd.md) concentra las prácticas acordadas, el pipeline
compartido de [pipesor-ci](https://github.com/pipesor-org/pipesor-ci) y el estado
de cada repositorio. Los servicios publican candidatos inmutables y no despliegan;
no sustituye los comandos de cada README ni aprueba contratos de despliegue.

## Adopción de esta iteración

Alcance documental: convenciones comunes y Java/Spring, referencias desde los siete servicios y concreción de Pipeline Service. Criterios: enlaces resolubles en los checkouts, coherencia con ownership y decisiones pendientes, diff sin errores de whitespace. No incluye código, migraciones, cambios del modelo persistente ni generación de diagramas. La validación realizada se reporta en la entrega; no equivale a pruebas de aplicación.
