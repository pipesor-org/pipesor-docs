# Protocolo de evaluación del diagnóstico asistido (OE3-I2)

| Campo | Valor |
|---|---|
| Versión | 0.7 — **vigente para la revisión humana de la corrida oficial de OE3-I2** (historial en §13) |
| Fecha | 23/11/2026 |
| Alcance | Indicador OE3-I2 del Project Charter v1.3. OE4 queda fuera de este protocolo. |
| Repositorio de ejecución | [pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios) |
| Evaluación de la rúbrica | Los dos integrantes del equipo del proyecto (§8.3) |
| Calificación del indicador | Asesor especializado y asesor metodológico, a partir del informe y sus registros (§13) |

Este documento fija, **antes de ejecutar las pruebas oficiales**, los escenarios, la causa de referencia,
las reglas de medición, la rúbrica y los criterios de aceptación del diagnóstico de Pipesor. Cumple para
OE3-I2 la función que el Charter asigna a un protocolo previo a las pruebas («Enfoques del trabajo»: un
protocolo «que establezca los escenarios, la evidencia disponible, la causa de referencia y las reglas de
medición»). El equipo del proyecto fija cada versión antes de las corridas que la aplican.

El protocolo atiende parcialmente [PD-022, PD-023 y PD-024](../architecture/pending-decisions.md): define
el método y los registros de resultados (§10, §13). No resuelve PD-001 (TMD).

## 1. Alcance y objetivo

El Charter define OE3-I2 así: el prototipo «procesa al menos 1000 registros de logs y supera las pruebas
funcionales de ingesta, recuperación de conocimiento, diagnóstico, generación y publicación del reporte,
consulta del dashboard y registro de revisión humana. La comprobación inicial comprenderá 10 escenarios de
fallo, con una meta de acierto del 80 % en la identificación de la causa probable». En el modelo, esto
corresponde a `validation_contract.diagnostic_accuracy` (`target_minimum_percent: 80`,
`probable_cause_identification_accuracy`) de [architecture.yml](../../model/architecture.yml).

Quedan fuera:

- la comparación con el diagnóstico manual y la reducción del TMD (OE4-I1);
- los 20 escenarios comparativos (OE4-I1) y la presentación final (OE4-I2);
- la verificación de requisitos no funcionales, que se documenta aparte.

La latencia del sistema se registra solo como dato descriptivo (§7.6). **No es TMD**, conforme a PD-001.

## 2. Definiciones

| Término | Definición operativa |
|---|---|
| Patrón de fallo | Patrón técnico de la taxonomía C01–C11 del inventario R01–R03 (`inventory/` en el repositorio de ejecución). |
| Escenario | Workflow controlado que reproduce un patrón (o un control) por construcción. |
| Variante | Versión del escenario (`a`, `b`, `c`) que cambia versiones, rutas o mensajes. |
| Caso | Una ejecución de una variante: unidad de evaluación, identificada como `<escenario>-<variante>`. |
| Causa de referencia | Causa definida por la construcción del fixture y registrada antes de ejecutar (§4). |
| Causa probable | La hipótesis principal del diagnóstico (`probableCause`), según el Charter: «hipótesis sobre el origen de un fallo… cuya correspondencia con la causa real debe ser evaluada». |
| Acierto | Caso con puntuación 2 en la rúbrica de causa probable (§8.1). |
| Registro de log | Una línea de log de GitHub Actions de un job fallido ingerido (§7.5). |

## 3. Escenarios

Los escenarios derivan del inventario R01–R03: once patrones técnicos y doce candidatos sintéticos de la
hoja «10 Escenarios». El inventario advierte que esos patrones no son causas raíz confirmadas ni una
muestra estadística, y que ninguna causa retrospectiva constituye *ground truth* independiente (D03). Por
eso la causa de referencia se define por construcción (§4).

| ID | Patrón | Reproducción | Variantes (a / b / c) |
|---|---|---|---|
| ESC-01 | C01 compilación, identificador no declarado | real (`dotnet publish`) | net8.0 / net9.0 / net10.0 y tres identificadores distintos |
| ESC-02 | C02 ruta de despliegue inexistente | real (Linux distingue mayúsculas) | Python / pwsh / bash |
| ESC-03 | C08 sitio padre IIS incorrecto | simulada (salida de run command) | sitio fijo / aplicación padre ausente / nombre con error |
| ESC-05 | C11 plazo de sondeo insuficiente | real (servicio local) | API / UI / jobs con distintos tiempos |
| ESC-06 | C06 sondeo sin respuesta | real (servicio local) | puerto / esquema / puerto con pwsh |
| ESC-07 | C03 autorización Azure insuficiente | simulada (Azure CLI) | storage / role assignment / run command |
| ESC-08 | C04 operación de VM desplazada | simulada (Azure CLI) | despliegue concurrente / extensión de parches / job paralelo |
| ESC-09 | C09 permiso denegado en archivos | real (directorios de solo lectura) | pwsh / unzip / Python |
| ESC-10 | C07 HTTP 500 tras despliegue, rollback | real (servicio local) | archivo renombrado / clave ausente / JSON inválido |
| ESC-11 | C05 timeout de extensión de VM | simulada (Azure CLI) | agente sin respuesta / instalación interactiva / proxy |
| ESC-04 | C10 fallo de inicialización del workflow | no implementado: límite de cobertura (§14) | — |

Controles:

| ID | Tipo | Resultado esperado |
|---|---|---|
| ESC-12 | Ejecución exitosa con advertencias | Ningún incidente. |
| NC-01 | Fallo real fuera del inventario (npm) | Diagnóstico correcto sin atribuirlo a un patrón del inventario. |
| NC-02 | Fallo real fuera del inventario (prueba unitaria) | Ídem. |
| NC-03 | Fallo real fuera del inventario (`docker build`) | Ídem. |

Las respuestas **simuladas** reemplazan Azure por respuestas con el formato de Azure CLI, tal como propone
el inventario («simular respuesta», «no modificar permisos reales de Azure»). Se reportan por separado de
las reproducciones reales (§10).

**Particiones.** La variante `a` de cada escenario forma el conjunto `dev`, que se usa solo para ajustar
(umbral, `top_k`, consulta). Las variantes `b` y `c` forman el conjunto `test`, que solo se usa en
corridas oficiales. Para los 10 escenarios positivos implementados, `test` contiene **20 casos**.

**Evidencia disponible.** El diagnóstico recibe la evidencia que selecciona el perfil
`failed-run-evidence-v1` de la ingestión ([evidencia protegida 2.2](../architecture/contracts/protected-evidence-v2.2.md)):

- un extracto de hasta 40 líneas del primer step fallido del primer job fallido, que termina en la
  última línea de error específica;
- el contexto de conocimiento recuperado por RAG, cuando existe.

Los fixtures imprimen junto al error el contexto que mostraría un pipeline real (listado del paquete,
log del servicio, permisos, estado de la VM). Una prueba automática impide que contengan términos que
revelen el carácter de prueba.

**Protección de la evidencia.** Antes del diagnóstico, la protección de la ingestión
(`verify-protection-v1`) actúa sobre el extracto:

- enmascara por completo los tokens que contienen una dirección IP, un `@` (correos, `paquete@versión`),
  un JWT o un token de GitHub, y los valores de claves sensibles;
- **rechaza** el extracto entero si contiene `\"` o `\u`; en ese caso no hay evidencia ni diagnóstico.

Los fixtures se ajustaron para no perder evidencia por elecciones incidentales: imprimen `localhost` en
lugar de direcciones IP y no imprimen comillas escapadas. Pruebas automáticas mantienen esas reglas. El
enmascaramiento de `paquete@versión` en npm (NC-01) es intrínseco a la herramienta y se registra como
limitación de la plataforma.

## 4. Causa de referencia

- Se define por construcción del fixture y se registra en `eval/cases/<escenario>.json`, con
  `reference_cause`, `key_evidence` y `reference_fix`, **antes** de la corrida oficial. El commit que la
  contiene queda fijado en el manifiesto de la corrida.
- Describe lo que una causa probable correcta debe identificar: el elemento, la ubicación o el parámetro
  determinante. Los detalles accesorios no son obligatorios.
- No se toma de las relaciones retrospectivas del inventario ni de diagnósticos previos de Pipesor.
- Si un evaluador demuestra que la evidencia disponible no permite identificar la causa de referencia,
  el caso se registra como **defecto del escenario**. No se excluye: se reporta, y el escenario se corrige
  para una versión posterior.
- **Regla de corrección (v0.6).**
  - **Qué se corrige.** Solo los casos que el consenso del evaluador marcó como defecto de escenario, no
    los que obtuvieron una puntuación baja.
  - **Cómo se corrige.** Se modifica el fixture para que su evidencia muestre el elemento determinante,
    como lo mostraría un registro real. La causa de referencia solo se reescribe para nombrar **el mismo
    elemento** con lo que muestra la evidencia nueva. No se rebaja lo que exige.
  - **Qué no cuenta como defecto.** Los datos que oculta el procesamiento de Pipesor, como el enmascaramiento
    de la ingestión: se reportan como limitación de la plataforma.
  - **Controles fuera del inventario marcados.** No se corrigen en esta versión: no entran en la métrica
    principal y el defecto no afecta su función, que es detectar atribuciones falsas.
- **Revisión r2 de los escenarios** (pipesor-validation-scenarios#14), sobre la primera corrida oficial:
  - ESC-01-b: el build muestra el campo `TaxRate` sin usar (CS0414).
  - ESC-01-c: el build muestra que falta el espacio de nombres `Orders.Api.Validation` (CS0234).
  - ESC-08: las horas de inicio de los run commands son relativas a la ejecución, no fijas de la noche
    anterior.
  - NC-01-c: no se corrige, porque su dato lo enmascara la ingestión.

## 5. Separación entre conocimiento y evaluación

Rigen CTRL-006 e INV-010 ([architecture.yml](../../model/architecture.yml)), DD-007 y
[ADR-021](../architecture/decisions/ADR-021-rag-runtime-contract-v0.1.md), además de «Recursos de Datos
y Evidencias» del Charter: «Los casos destinados a la evaluación y sus soluciones de referencia se
mantendrán separados del contenido utilizado para preparar la recuperación».

- El corpus RAG se genera solo a partir del inventario maestro (`inventory/`), validado durante OE1 con el
  asesor especializado y con el entorno de validación. No requiere una validación adicional. Cada
  documento registra su procedencia.
- Los casos, las causas de referencia, los juicios de relevancia (`qrels`) y los extractos del entorno de
  validación viven en `eval/` y nunca se importan.
- El importador solo verifica la marca `evaluation_material`. La separación efectiva se comprueba en el
  repositorio de ejecución: el generador del corpus no lee `eval/`, y una prueba busca líneas de
  evaluación dentro de los fragmentos del corpus.
- El responsable del proyecto autorizó la importación del corpus en el entorno dev.

## 6. Configuraciones

| ID | Configuración |
|---|---|
| C0 | Estado desplegado de referencia: corpus vacío; el diagnóstico usa solo el LLM sobre la evidencia. |
| C1 | C0 más el corpus generado del inventario, con el mismo modelo, prompt y parámetros de recuperación. |
| C2… | Cada mejora posterior de recuperación o de consulta (umbral, `top_k`, construcción de la consulta, alcance del corpus) como configuración nueva. |

- Cada configuración se ajusta solo con `dev` y se congela antes de correr `test`.
- **La cifra oficial de OE3-I2 corresponde a la configuración declarada como final antes de su corrida
  en `test`.** Las demás se reportan íntegras como ablación. No se elige a posteriori la mejor
  configuración según `test`.
- El manifiesto de cada corrida fija:
  - los SHA de los repositorios, el hash del código del arnés y los digests de las imágenes desplegadas;
  - el despliegue y la versión del modelo, y `promptVersion`;
  - el hash del corpus, `top_k`, el umbral y la versión de la consulta;
  - la versión de la rúbrica y la de este protocolo.

La configuración final se elige en `dev` en dos etapas y en este orden: primero la recuperación y después
el modelo, porque el modelo se compara con los fragmentos que entrega la recuperación ya congelada. Los
criterios de ambas etapas quedan fijados aquí antes de ejecutarlas.

### 6.1 Selección de la recuperación

- **Medición.** `harness.retrieval` consulta el corpus con el despliegue de embeddings del entorno
  (`pipesor-dev-embeddings`) y ordena por similitud coseno, el mismo orden de pgvector. La consulta es la
  evidencia reportada por Pipesor o, si no hay reporte, una emulación del extracto
  `failed-run-evidence-v1` que pasa por la emulación de la protección (§3). Relevancia según `qrels`.
- **Candidatos:**
  - construcción de la consulta: la actual (el extracto), sin marcas de tiempo, sin los bloques del runner
    y solo líneas de error;
  - tipos de corpus: solo documentación técnica (la configuración actual) o documentación y
    procedimientos;
  - `top_k`: 1 (la configuración actual con una sola evidencia), 3 o 5;
  - umbral mínimo de similitud: ninguno o uno calibrado en `dev`.
- **Regla de decisión:**
  - construcción de la consulta: mayor MRR@10; si hay empate, mayor hit@1 y luego mayor acierto en la
    vista de producción;
  - tipos de corpus: los de mayor MRR@10 con la consulta elegida; si empatan, documentación y
    procedimientos, porque los procedimientos aportan los pasos de atención que usa la recomendación;
  - `top_k`: el menor valor que alcanza el máximo hit@k en `dev` con los tipos elegidos;
  - umbral: solo se adopta si existe un valor que, en `dev`, rechaza todos los casos fuera del inventario y
    conserva todos los relevantes. Si no existe, no hay umbral y se registran las puntuaciones.
- Los cambios elegidos se implementan en los servicios responsables (`pipesor-recommendation-service`,
  `pipesor-rag-retrieval`) y se miden de nuevo en `dev` antes de congelarlos.

### 6.2 Selección del modelo de diagnóstico

- **Candidatos:** un modelo por tramo de costo, más la línea base:
  - el despliegue actual (gpt-4o);
  - gpt-6-luna;
  - gpt-6.1-terra;
  - un modelo del tramo sol (gpt-6.1-sol o gpt-6.2-sol), que se fija antes de ejecutar.

  Su despliegue sigue el procedimiento de IaC con aprobación del responsable del entorno.
- **Entradas fijas (repetición).** Para cada caso `dev` se toman:
  - la evidencia del reporte de Pipesor;
  - los fragmentos que entrega la recuperación congelada (§6.1);
  - el prompt y el esquema de respuesta del adaptador desplegado (`promptVersion` registrada).

  Se envía la misma petición a cada modelo, con los mismos parámetros que usa el adaptador, **3 veces**.
  El modelo es la única variable. Si un modelo exige parámetros distintos, eso es un fallo del filtro
  eliminatorio, salvo que se apruebe un cambio del adaptador y se repita la comparación para todos.
- **Filtro eliminatorio:** el 100 % de las respuestas debe ser válido (esquema, `finish_reason = stop`,
  sin rechazos) y citar solo los identificadores suministrados.
- **Criterio principal:** acierto estricto (§8.1) en los casos positivos de `dev`.
  - Los dos evaluadores puntúan la primera repetición de cada modelo, con los modelos mezclados bajo alias
    (`harness.ratings`).
  - Las otras dos repeticiones se usan para medir estabilidad con un indicador automático: si la causa
    probable menciona los términos clave del caso.
- **Criterios secundarios:**
  - precisión de citas según `qrels`;
  - rúbrica de recomendación;
  - comportamiento en controles fuera del inventario: declarar incertidumbre en lugar de atribuir un patrón
    del inventario.
- **Regla de decisión:**
  - se descartan los modelos que no superan el filtro eliminatorio;
  - se descartan los que aciertan **2 o más casos positivos menos** que el mejor;
  - entre los restantes se elige **el de menor costo por diagnóstico**;
  - si hay empate: latencia p95, luego estabilidad entre repeticiones y luego fecha de retiro del modelo.
- Con 10 casos positivos en `dev`, cada caso vale 10 puntos. Las diferencias menores a la regla anterior no
  se presentan como superioridad de un modelo. La decisión y sus datos se registran en un ADR, y el cambio
  del despliegue de producción requiere aprobación.
- **Resultado y desviación registrada (v0.4).**
  - La comparación del 23/11/2026 (312 llamadas) dio estos resultados:
    - los cuatro candidatos superaron el filtro eliminatorio;
    - con el indicador automático, gpt-6-luna acertó 10/10 positivos, gpt-6.2-sol 9/10, gpt-6.1-terra 8/10 y
      gpt-4o 4/10;
    - el costo por diagnóstico fue de USD 0,0004 para luna frente a 0,0030–0,0061 para los demás.
  - El responsable del proyecto eligió **gpt-6-luna**
    ([ADR-026](../architecture/decisions/ADR-026-diagnosis-model-gpt-6-luna.md)) **sin aplicar todavía el
    criterio principal, la rúbrica humana**.
  - Si una evaluación con la rúbrica, hecha antes de las corridas de `test`, deja a luna 2 o más positivos por
    debajo del mejor, se revisa la decisión.

## 7. Procedimiento de ejecución

1. **Piloto.** Antes de las corridas oficiales se ejecuta al menos un caso `dev` de extremo a extremo:
   ejecución, análisis, diagnóstico y reporte. Los resultados piloto se etiquetan `pilot` y no cuentan.
2. **Disparo.** El arnés lanza cada caso con `workflow_dispatch` (`scenario`, `variant`, `label`) y
   registra el ID y el intento de la ejecución.
3. **Análisis.**
   - Si el entorno tiene habilitada la captura por webhook, el análisis es automático.
   - En caso contrario, se solicita desde el dashboard en cuanto termina la ejecución, y ese método
     queda registrado (§14).
4. **Recolección.**
   - El workflow `Pipesor report` obtiene el reporte por OIDC
     (`/api/v1/github-actions/repositories/{r}/runs/{run}/attempts/{a}/report`) y lo conserva como
     artifact.
   - El arnés guarda el diagnóstico, las citas, las marcas de tiempo y el estado de cada fase.
5. **Conteo de registros de log.**
   - Se suman las líneas de los logs de los jobs fallidos de las corridas oficiales cuyo análisis la
     ingestión aceptó. La fuente es el archivo de logs del intento.
   - Las líneas de los extractos enviados al diagnóstico se reportan aparte.
   - La meta es ≥ 1000 en total. A nivel de caso, basta con que la evidencia permita juzgar el
     diagnóstico.
6. **Latencia (descriptiva).**
   - Se mide desde el fin de la ejecución (`updated_at` del run) hasta la primera respuesta 200 del
     reporte.
   - Solo es interpretable cuando el análisis se dispara automáticamente. No es TMD.
7. **Pruebas funcionales.** Para cada caso oficial se registra si se cumplió cada etapa de OE3-I2:
   - ingesta aceptada;
   - recuperación ejecutada (con o sin coincidencias);
   - diagnóstico disponible;
   - reporte generado y publicado (artifact);
   - incidente visible en el dashboard, verificado en los 20 casos positivos de la corrida oficial (§8.3);
   - revisión humana registrada en el dashboard con la decisión del revisor (§8.3).
8. **Repeticiones.** La cifra oficial usa una ejecución por caso. Si el costo lo permite, la configuración
   final se repite dos veces más sobre `test` y se reporta la estabilidad (proporción de casos con la
   misma puntuación).

## 8. Rúbricas

### 8.1 Causa probable (métrica principal)

| Puntuación | Criterio |
|---|---|
| 2 — Correcta | Identifica el elemento, la ubicación o el parámetro determinante de la causa de referencia. Puede variar la redacción o agregar detalles compatibles. |
| 1 — Parcial | Identifica el patrón, la categoría o el síntoma correcto, pero no el elemento determinante; o lo menciona solo como alternativa secundaria. |
| 0 — Incorrecta o ausente | Causa distinta o contradictoria; mera reformulación del error sin causa; diagnóstico apoyado en evidencia inexistente; o ausencia de diagnóstico (fallo de la plataforma, plazo agotado, abstención). |

Reglas:

- Se puntúa la hipótesis principal.
- Las limitaciones declaradas no restan.
- Si el diagnóstico atribuye un control NC a un patrón del inventario sin sustento, se registra además
  como atribución falsa (§9).

### 8.2 Recomendación (secundaria)

Se puntúa de 0 a 2 en cada una de estas dimensiones, según el Charter: pertinencia frente a
`reference_fix`, respaldo en la evidencia y seguridad. En seguridad, 0 corresponde a una acción
destructiva o riesgosa sin advertencia. Se reporta de forma descriptiva y no forma parte del criterio
de OE3-I2.

### 8.3 Procedimiento de evaluación

- **Al equipo le corresponde obtener y sustentar las métricas.** Los asesores califican el logro del
  indicador a partir del informe y de los registros de evaluación (§10). En OE4, el próximo periodo, la
  evaluación quedará a cargo del personal del entorno de validación, con un protocolo propio.
- **Revisión humana (v0.7).** Los dos integrantes del equipo revisan los **20 diagnósticos positivos** de la
  corrida oficial (`results/2026-11-23-oe3-test-r2/`).
  - **Reparto:** cada integrante revisa la mitad. Las variantes `b` y `c` de cada escenario se asignan a
    integrantes distintos por sorteo con semilla fija (`harness.review prepare`). Así, cada integrante revisa
    los 10 escenarios una vez y cada caso tiene un único revisor.
  - **Materiales:** cada revisor recibe sus casos con alias y en orden aleatorio, con el extracto de evidencia
    tal como se envió, el diagnóstico, la causa de referencia, la evidencia clave y la corrección esperada.
  - **Por caso, el revisor:**
    1. puntúa la rúbrica de §8.1 y §8.2;
    2. asigna la categoría cualitativa de §8.4, coherente con la puntuación, y la justifica en una o dos
       frases;
    3. indica si la recomendación es accionable (sí, parcial o no);
    4. abre el incidente en el dashboard y verifica que sea visible y que sus secciones (evidencia,
       hipótesis, recomendación, citas y modelo) coincidan con la hoja;
    5. registra la revisión en el dashboard: **Confirmar** solo si la causa obtuvo 2; si no, **Rechazar**, con
       la causa de referencia como causa real y la nota «Puntaje N; categoría X».
  - **Reglas del registro:** no se editan revisiones registradas ni se resuelven los incidentes. Las capturas
    no muestran usuario, avatar ni correo.
  - **Cegamiento:** hasta terminar sus casos, el revisor no consulta las puntuaciones ni las justificaciones
    del juez LLM.
  - **Coherencia:** `harness.review consolidate` verifica la coherencia entre puntuación, categoría y
    decisión.
- **Cifra principal (fijada antes de la revisión).**
  - El acierto estricto según la revisión humana de los 20 casos es la cifra principal de OE3-I2.
  - El juez LLM queda como verificación auxiliar. Se reportan el acuerdo humano–juez (proporción con IC de
    Wilson y κ en escala 0/1/2 y binaria) y cada discrepancia con su motivo.
  - Ninguna de las dos series se modifica después de conocer la otra.
  - Los controles fuera del inventario conservan la puntuación del juez.
- **Juez LLM.** Aplica la misma rúbrica, con las mismas entradas, sobre un despliegue distinto del modelo
  que diagnostica:
  - `pipesor-dev-diagnostics-sol` (gpt-6.2-sol), versión `rubric-judge-v1` (`harness.judge`), con salida
    JSON estricta;
  - 3 juicios por ítem: mediana para las puntuaciones y mayoría para los indicadores;
  - en los controles fuera del inventario recibe además los nombres de los patrones del inventario.

  En v0.5 y v0.6 fue el único evaluador. Desde v0.7 es verificación auxiliar de la revisión humana.

### 8.4 Análisis cualitativo

El revisor asigna a cada diagnóstico una categoría, definida antes de la revisión y coherente con la
puntuación de la causa:

| Categoría | Descripción | Puntuación |
|---|---|---|
| A | Acierto completo: identifica el elemento determinante. | 2 |
| B | Identifica el patrón o el síntoma, pero no el elemento determinante. | 1 |
| C | Menciona la causa de referencia solo como alternativa secundaria. | 1 |
| D | Reformula el error sin proponer una causa. | 0 |
| E | Propone una causa distinta o contradictoria. | 0 |

- **Por caso se registra también:** la justificación (una o dos frases) y si la recomendación es accionable.
- **El informe presenta:**
  - las frecuencias por categoría, en total y por tipo de reproducción;
  - los casos ilustrativos;
  - una síntesis temática de las justificaciones (análisis de errores).
- **Alcance:** este análisis describe el comportamiento del diagnóstico. No mide la percepción ni la utilidad
  para usuarios, que corresponden a OE4.

## 9. Métricas

| Métrica | Definición | Uso |
|---|---|---|
| **Acierto estricto (principal)** | Casos con puntuación 2 / 20 casos `test` de los 10 escenarios positivos. Los casos sin diagnóstico cuentan como 0. Se reporta con IC de Wilson al 95 %. | Criterio OE3-I2: ≥ 80 % (≥ 16/20). |
| Acierto por escenario | Escenarios con ambas variantes `test` en 2. | Descriptiva. |
| Distribución de la rúbrica | Proporción de casos con 0, 1 y 2, por escenario y por tipo de reproducción. | Descriptiva. |
| Concordancia | Acuerdo de la revisión humana con el juez LLM: proporción con IC de Wilson y κ de Cohen (0/1/2 y binario). | Calidad de la medición. |
| Categorías cualitativas | Frecuencia de las categorías de §8.4 y de recomendaciones accionables. | Análisis de errores. |
| Prueba funcional del dashboard | Incidentes visibles, secciones coherentes y revisiones registradas, sobre los 20 casos (§7.7). | Criterio OE3-I2. |
| Recuperación | hit@k (k = 1, 3, 5, 10) y MRR@10 frente a `qrels`. Se miden consultando `pipesor-rag-retrieval` directamente con la consulta que construye la recomendación, porque el servicio de recomendaciones no conserva las puntuaciones. | Ablación y mejoras. |
| Precisión de citas | Fragmentos citados relevantes según `qrels` / fragmentos citados. Los diagnósticos sin citas se cuentan aparte. | Respaldo del diagnóstico. |
| Controles | ESC-12: proporción de corridas sin incidente. NC: acierto según §8.1 y tasa de atribución falsa a patrones del inventario. | Especificidad. |
| Ablación | Diferencias entre configuraciones sobre los mismos casos `test`: McNemar exacto para el acierto; bootstrap pareado (semilla fija) para MRR y precisión de citas. | Efecto del corpus y de cada mejora. |
| Registros de log | Total de líneas según §7.5. | Criterio OE3-I2: ≥ 1000. |
| Latencia | Mediana y rango según §7.6. | Descriptiva (no es TMD). |

## 10. Exclusiones, defectos y registro

- **Solo se repiten**, con su motivo registrado, las corridas interrumpidas por causas ajenas a Pipesor
  antes del step que falla por diseño: caída de GitHub o del runner, o cancelación manual.
- Los fallos de la plataforma (análisis atascado, error interno, plazo agotado del reporte) **no se
  excluyen**: el caso cuenta como 0 y se registra la fase en que falló.
- No se eliminan casos después de ver los resultados. Los defectos de escenario (§4) se reportan con el
  caso.
- **Segunda corrida oficial (v0.6).** Tras la corrección de §4 se repiten los 28 casos `test`, no solo los
  corregidos, una vez cada uno y con la configuración de §15.
  - Es la corrida oficial para OE3-I2 y **la última de este semestre**. Su resultado se reporta sea cual sea,
    junto al de la primera corrida.
  - La corrección se decidió después de ver los resultados de `test`. El informe la declara como amenaza a la
    validez (§12).
- Los resultados por reproducción real y simulada se presentan por separado y en conjunto.
- Cada corrida se versiona en `results/<fecha>-<etiqueta>/` del repositorio de ejecución:
  `manifest.json`, registros por caso, evaluaciones por evaluador, consenso, `metrics.json` y resumen.
  Una corrida registrada no se reescribe.

## 11. Criterios de aceptación de OE3-I2

OE3-I2 se considera cumplido en este protocolo cuando, para la configuración final (§6), se cumplen las
tres condiciones:

1. al menos 1000 registros de log procesados (§7.5);
2. los 10 escenarios positivos ejecutados con las pruebas funcionales de §7.7 registradas;
3. acierto estricto ≥ 80 % en los 20 casos `test` (§9).

El informe reporta el IC de Wilson, los casos sin diagnóstico y los defectos encontrados. Con 20 casos,
16/20 tiene un IC aproximado de 0,58–0,92, por lo que el resultado debe leerse junto con sus límites.

## 12. Amenazas a la validez

- **Interna.**
  - El mismo equipo construye los escenarios, las causas de referencia y el corpus, lo que puede
    facilitar la recuperación.
  - Mitigaciones: separación de §5, variantes `test` no vistas durante el ajuste y controles NC.
  - Otro riesgo es el no determinismo del LLM (§7.8).
  - **Los evaluadores son los autores** del sistema, de los escenarios y de las causas de referencia, lo
    que puede sesgar la puntuación. Mitigaciones:
    - rúbrica, reglas de decisión y causas de referencia fijadas antes de ejecutar, con el commit
      registrado en el manifiesto;
    - ocultamiento de la configuración, alias y orden aleatorio;
    - coherencia verificada entre puntuación, categoría y decisión registrada (§8.3);
    - concordancia con un juez LLM independiente;
    - registros completos disponibles para que los asesores los verifiquen.
  - **Un único revisor por caso (v0.7).** No se mide el acuerdo entre humanos. La verificación de la medición
    es el acuerdo con el juez LLM, que se reporta también por revisor.
  - **Cegamiento parcial.** Uno de los integrantes conoció las puntuaciones del juez antes de la revisión.
    Se declara en el informe.
- **De constructo.**
  - Los escenarios son sintéticos y cuatro usan respuestas simuladas.
  - El extracto de 40 líneas puede omitir contexto: se observó con la ayuda que imprime `npm ci`.
  - La rúbrica conserva cierta subjetividad. Se mitiga con reglas de decisión y categorías definidas antes
    de la revisión, y con el contraste con el juez LLM.
- **Externa.**
  - El inventario procede de tres repositorios elegidos de forma intencional, con despliegues sobre
    VM/IIS. Los resultados no se generalizan a otras organizaciones ni plataformas.
- **De conclusión.**
  - N pequeño e IC amplios.
  - Las diferencias de ablación con pocos pares discordantes pueden no ser significativas.
- **De plataforma.**
  - Cambios del modelo desplegado o de las imágenes entre corridas. Mitigación: el manifiesto fija
    versiones y digests, y las corridas comparadas comparten entorno.

## 13. Calificación y cambios

| Rol | Responsabilidad |
|---|---|
| Equipo del proyecto | Fija cada versión del protocolo antes de las corridas o revisiones que la aplican; obtiene y sustenta las métricas |
| Asesor especializado | Califica el logro del indicador a partir del informe y sus registros |
| Asesor metodológico | Califica el logro del indicador a partir del informe y sus registros |

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1 | 23/11/2026 | Borrador inicial. |
| 0.2 | 23/11/2026 | Los integrantes del equipo asignan las puntuaciones de la rúbrica. Los asesores califican el logro del indicador. El juez LLM pasa a ser verificación auxiliar recomendada y se añade la amenaza de evaluadores autores. |
| 0.3 | 23/11/2026 | Procedimiento preregistrado de selección en `dev`: primero la recuperación (§6.1) y después el modelo (§6.2). Efecto de la protección de la ingestión sobre la evidencia (§3). La medición de la recuperación queda resuelta: local con el despliegue de embeddings del entorno. |
| 0.4 | 23/11/2026 | Resultado de §6.2 y desviación registrada: gpt-6-luna se elige con el filtro eliminatorio y el indicador automático, sin la rúbrica humana (ADR-026). El modelo del tramo sol quedó en gpt-6.2-sol. |
| 0.5 | 23/11/2026 | Decisiones de §14 resueltas y configuración final congelada (§15). La rúbrica la aplica el juez LLM, sin puntuaciones humanas (desviación, §8.3). |
| 0.6 | 23/11/2026 | Primera corrida oficial: 15/20. Regla de corrección de defectos de escenario y revisión r2 de los escenarios (§4). Segunda corrida de los 28 casos `test`, oficial y última del semestre (§10). Configuración de §15 sin cambios, verificada en el entorno. |
| 0.7 | 24/11/2026 | Revisión humana de los 20 diagnósticos positivos de la corrida oficial: un integrante por caso, con las variantes de cada escenario repartidas entre ambos (§8.3). Incluye la prueba del dashboard (§7.7) y el análisis cualitativo (§8.4). La cifra principal pasa a ser la humana y el juez LLM queda como verificación auxiliar. Se aclaran los roles (§13) y el origen del corpus en el inventario validado en OE1 (§5). |
- Cualquier cambio posterior genera una nueva versión con su motivo. Las corridas indican la versión
  aplicada.

## 14. Decisiones (resueltas en la versión 0.5)

1. **ESC-04 (C10, `startup_failure`)** no se implementa este semestre. El perfil de ingestión no prepara
   evidencia para ese resultado, así que se reporta como **límite de cobertura** fuera del denominador. Los
   10 escenarios positivos de §3 cumplen el mínimo de OE3-I2.
2. **Disparo del análisis:** captura automática por **webhook**, activa en dev desde el 23/11/2026. La
   latencia (§7.6) mide la cadena sin intervención humana.
3. **Repeticiones:** **una** ejecución oficial por caso. La estabilidad entre repeticiones del modelo se midió
   en `dev`, en la comparación de §6.2.
4. **Medición de la recuperación** (resuelta en v0.3): local, con el despliegue de embeddings del entorno
   (`pipesor-dev-embeddings`), autorizado por el responsable del proyecto.

## 15. Configuración final congelada (v0.5, vigente en v0.6)

| Componente | Valor |
|---|---|
| Modelo de diagnóstico | `pipesor-dev-diagnostics-luna`, gpt-6-luna 2026-09-22 ([ADR-026](../architecture/decisions/ADR-026-diagnosis-model-gpt-6-luna.md)); prompt `diagnostic-hypothesis-v2`; `max_completion_tokens` 1024 |
| Recuperación | Consulta sin marcas de tiempo, solo documentación técnica, `topK` 3, sin umbral (§6.1) |
| Corpus | Inventario R01–R03: 22 documentos y 33 fragmentos; `source_version` `f75113f1f7fc`; contenido `c07ce2e37a72…`; `scope_revision` `scope-r1` |
| Imágenes desplegadas | Recommendation `sha256:fe77a18d…`, RAG `27f301b2…`, Ingestion `a9207a15…`, NLP `71e7e782…`, Correlation `50b6b95b…`, Pipeline `f763b26d…`, Log/Event `ffaf1216…` |
| Evaluador | Juez LLM `rubric-judge-v1` sobre `pipesor-dev-diagnostics-sol` (§8.3) |
| Escenarios | Primera corrida: revisión r1 (`eval/cases` preregistrado). Segunda corrida: revisión r2 (commit `002248f`, §4) |
| Revisión humana (v0.7) | Lote `results/review-2026-11-23-oe3-test-r2/` (`harness.review`, semilla 20261124): 10 casos por integrante |

Los manifiestos de las corridas registran estos valores completos. Cualquier cambio de configuración posterior
abre una nueva versión del protocolo y una corrida nueva.
