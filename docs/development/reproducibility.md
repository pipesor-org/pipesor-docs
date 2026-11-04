# Validación y reproducibilidad de DaC

Estas herramientas desarrollan la documentación; no son decisiones sobre el stack
runtime de los microservicios. No requieren configuración WSL2. Usar el checkout
existente y leer `AGENTS.md`. No cambiar modelos para obtener una ejecución verde.

## Dependencias

Perfil ejecutado el 04/11/2026:

| Herramienta | Versión probada / instalación |
|---|---|
| Python | 3.12.14; `python3 -m venv .venv`; `.venv/bin/pip install -r requirements.txt` |
| Paquetes Python | Versiones exactas en `requirements.txt`, incluidos PyYAML 6.0.3 y diagrams 0.25.1 |
| Node / npm | 24.22.1 / 11.9.0; `npm ci --prefix tools` usa `tools/package-lock.json` |
| @dbml/cli | 11.0.1, solo herramientas de desarrollo |
| D2 | 0.7.1, distribución oficial `d2-v0.7.1-linux-amd64.tar.gz` de terrastruct/d2 en GitHub |
| Graphviz | `dot` y `neato` 2.42.4 |
| Java | OpenJDK 21.0.12.1 |
| PlantUML | JAR versionado `tools/plantuml.jar`, versión 1.2026.8 |
| PostgreSQL / pgvector | Solo integración opcional: 16.15 / 0.8.7, imagen Docker fijada por digest en `tools/test_postgres.py` |

Checksum SHA-256 del JAR: `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462`.
Checksum observado del archivo oficial D2 descargado mediante TLS:
`eb172adf59f38d1e5a70ab177591356754ffaf9bebb84e0ca8b767dfb421dad7`.
No se sustituye verificación TLS ni se afirma una firma independiente de D2.
`dbml-renderer` y `pandoc` no participan en `make all`; pueden comprobarse con
`CHECK_OPTIONAL_TOOLS=1 make check-env`, si se instalan por separado.
Las versiones D2 0.9.0 / DBML 10.2.0 mencionadas en el documento histórico de
modelado no fueron las usadas en esta ejecución. No se modifica aquel registro.

## Ejecución

Exponer D2, Node y Graphviz en PATH. Para DBML instalado por el lockfile:

```sh
export PATH="$PWD/tools/node_modules/.bin:$PATH"
make check-env
make validate
make test
make all
make verify-artifacts
# Opcional: Docker local disponible y permiso de acceso al daemon.
make test-postgres
```

Si Fontconfig no dispone de caché escribible, seleccionar una ubicación local
mediante `XDG_CACHE_HOME`. No se necesita cambiar la configuración personal del
host. El entorno cloud verificado utiliza `/workspace/.cache`.
`D2` y `DBML2SQL` aceptan rutas ejecutables explícitas a través del resolvedor
compartido; no aceptan comandos con argumentos. Los fallos de resolución o
conversión son errores. Los checks temporales se eliminan incluso al fallar.

`make all` **regenera** archivos en `out/`, `build/` y `model/db.dbml` según el
flujo vigente. No editar esos archivos manualmente. Revisar el diff antes de
commitear. `make verify-artifacts` no los repara: crea dos copias desechables del
checkout de trabajo, genera desde directorios de salida vacíos y compara bytes,
inventario y vigencia. Incluye cambios aún no commiteados; no demuestra una
instalación desde cero ni equivalencia entre plataformas/versiones de fuentes.
No normaliza IDs ni elimina diferencias de los SVG para hacer pasar el check.

`make test-postgres` genera SQL y crea su propio contenedor, sin puertos publicados,
con red deshabilitada y datos sintéticos. Nunca acepta una URL de base existente.
Aplica `schema.sql` y `extras.sql`, exige errores SQLSTATE concretos y elimina el
contenedor mediante cleanup. Docker/imagen ausente es un fallo explícito, no un
resultado aprobado. `POSTGRES_TEST_IMAGE` permite probar otra versión de manera
explícita; los resultados de esa versión deben registrarse por separado.

## Cobertura de etapa 4

Las ocho áreas de corrección se enumeran aquí como localizadores de implementación,
no como nuevos IDs de decisiones arquitectónicas:

| Área / hallazgo | Corrección y evidencia |
|---|---|
| 1. Falsos éxitos de dependencias | `check_env.sh`: exit no cero, diagnóstico, cleanup, sin pipelines que oculten al productor; smoke de render y SQL real. |
| 2. GitHub read-only y publicación | `architecture_policy.py`: credenciales declaradas, relaciones read-only, artifact publicado por workflow según ADR-005/016; mutaciones negativas. |
| 3. Ingesta y privacidad | Guardas INV-001/002/010, controles previos a IA, rutas alternativas que eluden ingesta, contrato LLM y corpus/provenance RAG; regresiones. |
| 4. Checks y unicidad | `domain_constraints.py`: preserva expresiones y conjuntos de columnas aprobados, nombres válidos, NOT NULL necesario; prueba cada eliminación/debilitamiento. |
| 5. Referencias y preguntas abiertas | Guarda todas las referencias físicas/lógicas vigentes, duplicados y DQ; pruebas de eliminación conjunta de atributo/relación. No fija dimensión ni escala de confianza. |
| 6. DBML/SQL | Exportador rechaza salida vacía/parcial y omisiones de checks/índices; pruebas reales PostgreSQL/pgvector sobre DDL generado. |
| 7. Vigencia/reproducibilidad | `verify_artifacts.py`, doble generación aislada, comparación exacta; regeneración automática de 13 SVG desactualizados. |
| 8. Dependencias y ejecución repetible | Este perfil, manifest/lock npm, targets Make de tests y comprobación; dependencias opcionales separadas. |

Los contratos de validación codifican restricciones **actuales**, no decisiones
inmutables: una evolución autorizada debe cambiar modelo, guardas y pruebas en el
mismo trabajo. Los tests no deciden autorizaciones. Las pruebas del grafo no
demuestran saneamiento de payloads reales, permisos efectivos GitHub ni elegibilidad
semántica del corpus. Las referencias lógicas quedan sin FK física: los owners
siguen siendo responsables de su existencia en aplicación. No hay servicios de
producto en este repositorio para probar esos controles runtime.

No se resuelven CF-001, TMD, aprobación de fuentes, RBAC, modelo/dimensión de
embeddings, contratos operacionales ni preguntas de `pending-decisions.md`.
La discrepancia de colapso implícito C4 descrita en Overview requiere una decisión
de presentación/gobernanza separada; no se altera aquí la topología aprobada.
La integración SQL prueba transacciones secuenciales, no carga ni concurrencia
exhaustiva. Continúan ocho advertencias C4 de metadatos/estilos ya documentadas;
no se inventan tecnologías/descripciones. No hubo fallback de iconos. No se realizó
una inspección visual manual exhaustiva de todos los SVG.
