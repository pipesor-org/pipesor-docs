# Registro de fuentes documentales

Registro incorporado en la etapa 2 de refinamiento, con fecha 31/10/2026. Documenta las fuentes suministradas localmente por el usuario y su estado verificable; no constituye una aprobación arquitectónica. Referencia Git inspeccionada: `c1e7e5f4ac2775d0eeb929328d24eb98b2a13265`, junto con los archivos locales suministrados y los cambios documentales de la etapa 1.

## Ubicación e integridad

Las copias de este directorio preservan todos los bytes de los originales de raíz. Son snapshots de las mismas fuentes, no autoridades independientes. Los originales se mantienen para no romper las rutas de `model/architecture.yml`; no se han modificado esas referencias. Los archivos auxiliares `:Zone.Identifier` no se incorporan al archivo documental y no acreditan aprobación.

El drift conserva cinco líneas con espacios finales originales (líneas 5–9, saltos de línea Markdown). La comprobación de whitespace sobre esa copia nueva los señala; no se normalizan porque se exige integridad byte a byte.

| Fuente | Original conservado | Copia archivada | Tamaño |
|---|---|---|---|
| Project Charter | [Original](<../../P202620027 - Project Charter v.1.3.docx>) | [Project Charter v1.3](<P202620027 - Project Charter v.1.3.docx>) | 184069 bytes |
| Registro de drift | [Original](../../tech_drift_resolutions.md) | [tech_drift_resolutions.md](tech_drift_resolutions.md) | 28690 bytes |

SHA-256, idéntico para cada par original/copia:

```text
P202620027 - Project Charter v.1.3.docx
f2e4f3d3f86abb648941b8c83c98fe92e05d244ae9b5257fb365c11dbd249abf

tech_drift_resolutions.md
bab4d39da8b9e9b24d6499f1f6383de79a4534e40b5554d745459a7c8a8070c4
```

Los hashes identifican el contenido recibido y permiten detectar alteraciones; no prueban autoría, aprobación ni autenticidad frente a una fuente externa. No se ha verificado una cadena de custodia anterior a la entrega local. Si se recibe otra versión, deberá identificarse como tal, sin reinterpretar este snapshot como si contuviera las decisiones nuevas.

## Project Charter v1.3

- **Versión y fecha documentales:** portada «Versión 1.3» e historial de revisiones, fila 1.3, de 23/09/2026.
- **Autoría declarada:** Jhon Alexander Galvez Chambi y Ramiro Alexander Guzmán Chávez en el historial; portada preparada por Jhon Alexander Galvez Chambi.
- **Procedencia disponible:** archivo proporcionado en la raíz del checkout. No se dispone de acta de entrega o repositorio de origen que permita ampliar esa procedencia.
- **Autoridad declarada:** objetivos, alcance y restricciones; indicadores de éxito, organización y validación del proyecto. El drift, su cabecera y §50, le atribuyen precedencia sobre el registro. La gobernanza vigente distingue autoridad por materia, conforme a ADR-018; esta anotación no impone una jerarquía nueva.
- **Aprobación verificable:** sección «Aprobación», tabla Nombre/Cargo/Firma/Fecha, con filas vacías. No se encontraron partes de firma digital en el DOCX. La aprobación formal no es verificable con esta copia; no se afirma que no haya ocurrido fuera del checkout.
- **Metadatos técnicos:** creador `Jhon Galvez`; última modificación por `u202323270 (Galvez Chambi, Jhon Alexander)`; creación 09/09/2026 y modificación 24/09/2026 en `docProps/core.xml`. La revisión interna OOXML `8` no es una versión documental adicional ni una aprobación. La fecha técnica de modificación no sustituye el 23/09/2026 declarado en el historial.

Para citar el DOCX, usar su hash, sección y, cuando exista, identificador OE; añadir el inicio del párrafo si hace falta desambiguar. La paginación puede variar al renderizar. Ejemplo: «Enfoques del trabajo», párrafo «Antes de las pruebas comparativas…». El texto se inspeccionó mediante `word/document.xml` sin reguardar ni convertir el original.

## Registro de drift

- **Contenido:** 50 resoluciones consecutivas, §1 a §50, más diagramas y resúmenes finales.
- **Versión, fecha y autoría:** no declaradas formalmente en el archivo. Se identifica este snapshot por su hash; no se le asigna una versión ni una fecha de redacción inferidas.
- **Procedencia disponible:** archivo proporcionado en la raíz del checkout; historia previa no acreditada.
- **Autoridad declarada:** registrar desviaciones frente a documentos iniciales. La cabecera y §50 reconocen precedencia del Charter y de decisiones posteriores confirmadas por el equipo; no invalidan automáticamente esas decisiones.
- **Aprobación verificable:** sin aprobador, firma, fecha ni acta identificable. «Definitivo», «confirmado» y «cerradas» son declaraciones del documento, no evidencia independiente de aceptación.
- **Límite de uso:** conserva detector y asuntos abiertos luego tratados por ADRs. No debe aplicarse aislado como fotografía vigente; consultar la [reconciliación](../architecture/reconciliation.md).

## Decisiones y evidencia pendiente

Los 18 ADRs declaran `Accepted` y fecha 03/10/2026. Su estado registrado se conserva; no se ha acreditado por separado el acto de aprobación individual. El [índice de decisiones](../architecture/decisions/index.md) documenta evolución explícita sin modificar ADRs históricos.

La [reconciliación y sus pendientes](../architecture/reconciliation.md#referencias-desactualizadas-y-evidencia-pendiente) registra TMD, CF-001, A-011, política de retención, prompts aprobados citados, fuentes ausentes y aprobaciones no verificadas. Incorporar estas copias no resuelve esas cuestiones ni cambia tecnologías, topologías o alcance.
