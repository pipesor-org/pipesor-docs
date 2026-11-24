# Informe de validación del diagnóstico asistido (OE3-I2)

| Campo | Valor |
|---|---|
| Fecha | 23/11/2026 (corridas) y 24/11/2026 (revisión humana) |
| Indicador | OE3-I2 del Project Charter v1.3 |
| Protocolo | [Protocolo de evaluación](protocolo-evaluacion-oe3.md): versión 0.5 (commit `f2b7b0f`) para la primera corrida oficial, versión 0.6 (commit `d5251e4`) para la segunda y versión 0.7 (commit `784a864`) para la revisión humana |
| Datos y código | [pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios): corrida oficial `results/2026-11-23-oe3-test-r2/`; primera corrida `results/2026-11-23-oe3-test/`; revisión humana `results/review-2026-11-23-oe3-test-r2/` |
| Fuera de alcance | OE4-I1 e I2 (comparación con el diagnóstico manual, TMD y 20 escenarios comparativos), previstos para el siguiente periodo |

## 1. Resumen

El Charter define OE3-I2 así: el prototipo «procesa al menos 1000 registros de logs y supera las pruebas
funcionales de ingesta, recuperación de conocimiento, diagnóstico, generación y publicación del reporte,
consulta del dashboard y registro de revisión humana. La comprobación inicial comprenderá 10 escenarios de
fallo, con una meta de acierto del 80 % en la identificación de la causa probable».

Hubo dos corridas oficiales sobre los 28 casos `test`, con la misma configuración congelada:
- **La primera** detectó tres casos positivos con defectos de escenario.
- **La segunda** se hizo tras corregirlos con la regla del protocolo v0.6. Es la oficial para el indicador y
  la última de este semestre.

Después, los dos integrantes del equipo revisaron los 20 diagnósticos positivos de la corrida oficial
(protocolo v0.7). Su puntuación es la cifra principal; el juez LLM queda como verificación auxiliar.

| Criterio (protocolo §11) | Primera corrida | **Segunda corrida (oficial)** | Estado |
|---|---|---|---|
| ≥ 1000 registros de log procesados | 5279 líneas | **5280** líneas de los jobs fallidos diagnosticados | Cumplido |
| Pruebas funcionales: ingesta, recuperación, diagnóstico, reporte publicado | 28/28 ejecuciones según diseño; 26/26 diagnósticos | **28/28; 26/26**; los 2 controles sin fallo no abrieron incidente | Cumplido |
| Pruebas funcionales: incidente visible en el dashboard y revisión registrada (§7.7) | No ejercitadas | **20/20 incidentes visibles y coherentes con el diagnóstico; 20/20 revisiones registradas** | Cumplido |
| Acierto estricto ≥ 80 % en la causa probable | 15/20 = 75 %, IC de Wilson 95 % [0,53; 0,89] (juez LLM) | **17/20 = 85 %, IC de Wilson 95 % [0,64; 0,95] (revisión humana)**; juez LLM: 18/20 | **Cumplido** |

**Conclusión.**
- **OE3-I2 se cumple** según el §11 del protocolo: volumen suficiente, pruebas funcionales de punta a punta
  (incluidos el dashboard y la revisión registrada) y acierto estricto sobre la meta en los 10 escenarios.
- La revisión humana da 17/20 = 85 %. El límite inferior del intervalo (0,64) queda por debajo de la meta:
  con 20 casos, el resultado debe leerse junto con sus límites (§11).
- El juez LLM coincide con la puntuación humana en 18 de 20 casos. En los otros dos, la revisión humana es
  más estricta; solo uno (ESC-01-c) cambia el acierto y explica la diferencia entre 17/20 y 18/20.
- Toda la diferencia entre las dos corridas proviene de los tres casos corregidos. Los otros 17 positivos
  obtuvieron exactamente la misma puntuación del juez en ambas.
- La causa es correcta en 17 casos, pero solo 4 recomendaciones son aplicables tal cual. Las demás van en la
  dirección correcta y se quedan en verificar o dejan una decisión abierta (§3.3).

## 2. Método

Se resume aquí; el detalle completo está en el protocolo.

- **Escenarios.** Derivan de la taxonomía C01–C11 del inventario R01–R03:
  - 10 escenarios positivos: 6 con reproducción real y 4 con respuestas simuladas de Azure CLI;
  - 3 controles con fallos reales fuera del inventario;
  - 1 control sin fallo.

  Cada uno tiene tres variantes. La `a` forma el conjunto `dev`, usado solo para ajustar. Las `b` y `c` forman
  el conjunto `test`, con 20 casos positivos. ESC-04 (C10, `startup_failure`) no se implementó, porque el
  perfil de ingestión no prepara evidencia para ese resultado; se reporta como límite de cobertura.
- **Causa de referencia.** Se define por construcción del fixture y se registra antes de ejecutar
  (`eval/cases`). No se toma del RCA retrospectivo del inventario.
- **Separación entre conocimiento y evaluación.**
  - El corpus RAG (22 documentos, 33 fragmentos) se genera solo a partir del inventario maestro, validado
    durante OE1 con el asesor especializado y con el entorno de validación. Cada documento registra su
    procedencia.
  - Los casos, las causas de referencia y los juicios de relevancia no se importan.
  - Una prueba automática impide que texto específico de los casos llegue al corpus.
- **Selección de la configuración, solo en `dev`** (protocolo §6):
  - **Recuperación (§6.1).** Sobre los extractos emulados se comparó la consulta actual con tres variantes.
    Se eligió quitar las marcas de tiempo de GitHub, conservar solo la documentación técnica y usar
    `topK` = 3. Resultado en `dev`: MRR@10 0,90 frente a 0,87, y hit@3 1,00 frente a 0,90.
  - **Umbral de similitud.** No se adoptó: la separación encontrada era de 0,0007 con 3 casos, lo que quedó
    registrado como desviación. La recomendación registra las puntuaciones para calibrarlo más adelante.
  - **Modelo (§6.2).** Se repitió con entradas fijas la petición exacta del adaptador a cuatro modelos, 3 veces
    con y sin corpus: 312 llamadas.
    - Los cuatro superaron el filtro eliminatorio.
    - Indicador de términos clave con corpus: gpt-6-luna 10/10, gpt-6.2-sol 9/10, gpt-6.1-terra 8/10 y gpt-4o
      4/10.
    - Se eligió **gpt-6-luna**, el más barato que no está claramente por debajo del mejor: USD 0,0004 por
      diagnóstico ([ADR-026](../architecture/decisions/ADR-026-diagnosis-model-gpt-6-luna.md)). Se decidió sin
      la rúbrica humana, lo que quedó registrado como desviación.
  - **El corpus mejora el diagnóstico.** Sin conocimiento (C0), luna obtuvo 8/10 y terra 6/10. Con el corpus
    (C1), 10/10 y 8/10.
- **Configuración congelada** (§15 del protocolo), idéntica en las dos corridas:
  - gpt-6-luna 2026-09-22 con el prompt `diagnostic-hypothesis-v2`;
  - la recuperación descrita arriba;
  - el corpus importado con el alcance `scope-r1`;
  - captura por webhook;
  - los digests de las 7 imágenes desplegadas, registrados en los manifiestos y verificados antes de la
    segunda corrida.
- **Ejecución oficial.** En cada corrida, las 28 ejecuciones de `test` se lanzaron una sola vez. Cada
  diagnóstico se recogió del artifact `pipesor-report`, obtenido por OIDC.
- **Corrección de escenarios entre corridas** (protocolo v0.6 §4 y §10):
  - **Qué se corrigió:** solo los casos positivos que el consenso del evaluador marcó como defecto de
    escenario, es decir, cuya evidencia no permitía identificar la causa de referencia. No se seleccionó por
    puntuación.
  - **Cómo:** se modificó el fixture para que la evidencia mostrara el elemento determinante, como lo mostraría
    un registro real. La referencia solo se reescribió para nombrar ese mismo elemento.
  - **Qué no se consideró defecto:** lo que oculta Pipesor (NC-01-c).
  - **Segunda corrida:** se repitieron los 28 casos `test`, no solo los corregidos. Se declaró de antemano
    como la última del semestre, para reportarla sea cual fuera su resultado.
- **Revisión humana (cifra principal, protocolo v0.7 §8.3).**
  - Los dos integrantes del equipo revisaron los 20 diagnósticos positivos de la corrida oficial, 10 cada
    uno. Las variantes `b` y `c` de cada escenario se asignaron a revisores distintos por sorteo con semilla
    fija, así que cada revisor vio los 10 escenarios una vez.
  - Cada revisor recibió sus casos con alias y en orden aleatorio, con la evidencia tal como se envió, el
    diagnóstico, la causa de referencia, la evidencia clave y la corrección esperada.
  - Por caso puntuó la rúbrica de causa (0/1/2) y la de recomendación, asignó una categoría cualitativa
    (§8.4), indicó si la recomendación es accionable y justificó su puntuación.
  - Después abrió el incidente en el dashboard, comprobó que coincidiera con su hoja y registró la revisión:
    Confirmar si la causa obtuvo 2; si no, Rechazar con la causa de referencia como causa real.
  - `harness.review` verificó que cada registro estuviera completo y fuera coherente entre puntuación,
    categoría y decisión.
- **Juez LLM (verificación auxiliar).**
  - gpt-6.2-sol, distinto del modelo que diagnostica, con salida JSON estricta;
  - 3 juicios por ítem, con mediana de las puntuaciones;
  - recibe las mismas entradas que los revisores.

  En v0.5 y v0.6 fue el único evaluador. Los 6 controles fuera del inventario conservan su puntuación.

## 3. Resultados

### 3.1 Acierto en la causa probable (`test`)

| Escenario | Patrón | Reproducción | 1.ª corrida, juez (b / c) | 2.ª corrida, juez (b / c) | **2.ª corrida, revisión humana (b / c)** |
|---|---|---|---|---|---|
| ESC-01 | C01 compilación | real | 1 / 0 | 2 / 2 | 2 / **1** |
| ESC-02 | C02 ruta | real | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-03 | C08 IIS | simulada | 1 / 2 | 1 / 2 | 1 / 2 |
| ESC-05 | C11 plazo de sondeo | real | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-06 | C06 sondeo sin respuesta | real | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-07 | C03 RBAC | simulada | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-08 | C04 operación desplazada | simulada | 1 / 1 | 1 / 2 | **0** / 2 |
| ESC-09 | C09 permisos | real | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-10 | C07 HTTP 500 | real | 2 / 2 | 2 / 2 | 2 / 2 |
| ESC-11 | C05 extensión de VM | simulada | 2 / 2 | 2 / 2 | 2 / 2 |

En negrita, las puntuaciones humanas que difieren del juez.

Revisión humana de la corrida oficial (cifra principal):
- **Acierto estricto:** 17/20 = 85 %, IC de Wilson 95 % [0,64; 0,95].
- **Por revisor:** A 9/10 y B 8/10.
- **Por tipo de reproducción:** real 11/12; simulada 6/8.
- **Escenarios con ambas variantes en 2:** 7/10.
- **Distribución:** 17 casos con 2, 2 con 1 y 1 con 0.
- **Casos por debajo de 2:** ESC-01-c (1), ESC-03-b (1) y ESC-08-b (0); se analizan en §3.3.

Juez LLM:
- **Segunda corrida:** 18/20 = 90 %, IC de Wilson 95 % [0,70; 0,97]. Escenarios con ambas variantes en 2:
  8/10; real 12/12 y simulada 6/8. Por debajo de 2: ESC-03-b y ESC-08-b, con 1 en las dos corridas.
- **Estabilidad del juez:** la puntuación de causa coincidió en los 3 juicios en 26 de 26 ítems; en la primera
  corrida, en 25 de 26.
- **Estabilidad entre corridas:** los 17 positivos que no cambiaron obtuvieron la misma puntuación en ambas
  corridas. La primera corrida dio 15/20, IC [0,53; 0,89].

### 3.2 Acuerdo entre la revisión humana y el juez LLM

- **Misma puntuación de causa:** 18/20 = 90 %, IC de Wilson 95 % [0,70; 0,97]; κ de Cohen 0,56 en la escala
  0/1/2.
- **Mismo resultado de acierto (2 frente a menos de 2):** 19/20 = 95 %, IC [0,76; 0,99]; κ 0,77.
- **Por revisor:** A coincide con el juez en la puntuación en 9/10 casos y en el acierto en 10/10; B, en 9/10
  y en 9/10.
- **Discrepancias.** En las dos, la revisión humana es más estricta que el juez:

| Caso | Revisión humana | Juez | Motivo |
|---|---|---|---|
| ESC-01-c | 1, categoría C (revisor B) | 2 | **Revisor:** la frase principal solo reformula el CS0234, y la causa de referencia (el código de `Orders.Api.Validation` no está incluido ni referenciado) aparece solo entre tres alternativas sin elegir. **Juez:** identifica el elemento, porque `HealthEndpoint.cs` hace referencia a `Orders.Api.Validation`, que no está disponible al compilar, aunque admite que no distingue si falta el código o la referencia. |
| ESC-08-b | 0, categoría D (revisor A) | 1 | **Revisor:** la hipótesis principal dice con otras palabras el mensaje de `OperationPreempted`; la extensión `WindowsPatchExtension` aparece solo en las limitaciones y la recomendación. **Juez:** identifica el patrón (una operación más reciente desplazó el comando), pero no la actualización de la extensión como causa principal. |

Solo ESC-01-c cambia el acierto: ESC-08-b no acierta según ninguna de las dos series.

### 3.3 Análisis cualitativo (protocolo §8.4)

| Categoría | Descripción | Total | Real (12) | Simulada (8) |
|---|---|---|---|---|
| A | Acierto completo: identifica el elemento determinante | 17 | 11 | 6 |
| B | Identifica el patrón o el síntoma, pero no el elemento determinante | 1 | 0 | 1 |
| C | Menciona la causa de referencia solo como alternativa secundaria | 1 | 1 | 0 |
| D | Reformula el error sin proponer una causa | 1 | 0 | 1 |
| E | Propone una causa distinta o contradictoria | 0 | 0 | 0 |

Recomendación accionable: sí en 4 casos, parcial en 10 y no en 6.

**Casos ilustrativos**, según las justificaciones de los revisores:
- **A, con recomendación aplicable (ESC-10-c).** El diagnóstico culpa a la coma final ilegal de un objeto JSON
  en la configuración de producción, que impide el arranque y provoca el HTTP 500. La recomendación da el
  archivo, la ubicación exacta (línea 3, columna 66) y el cambio.
- **B (ESC-03-b).** Atribuye la falla a una incompatibilidad con el sitio padre y cita `/portal/api`, `/` y
  `/admin` solo como datos. Acierta en el patrón (jerarquía de IIS), pero no culpa a la ausencia de la
  aplicación padre `/portal`.
- **C (ESC-01-c).** La frase principal reformula el CS0234; la causa de referencia aparece entre tres
  alternativas sin elegir.
- **D (ESC-08-b).** La hipótesis principal repite el mensaje de `OperationPreempted`. La extensión
  `WindowsPatchExtension`, en estado `Updating`, aparece solo en las limitaciones y la recomendación.

**Síntesis de las justificaciones:**
1. **Cuando falla, el diagnóstico tiene el dato, pero no lo culpa.** En los tres casos por debajo de 2 el
   elemento determinante está en la evidencia, y el diagnóstico lo cita o lo menciona como dato, alternativa
   o limitación. Ocurre cuando la causa exige relacionar dos hechos del log (la jerarquía de IIS; la extensión
   en actualización y el desplazamiento) o elegir entre explicaciones compatibles con el mismo error. Dos de
   los tres casos son escenarios simulados.
2. **La causa acierta más que la recomendación.** Con 17 causas correctas, solo 4 recomendaciones son
   aplicables tal cual (ESC-02-c, ESC-08-b, ESC-08-c y ESC-10-c).
   - **Parciales (10):** van al elemento correcto, pero dejan dos opciones sin elegir (ESC-02-b, ESC-03-b,
     ESC-09-b), no dan el valor (por ejemplo, el puerto 18092 en ESC-06-c, el plazo del sondeo en ESC-05-b o
     los parámetros desatendidos del instalador en ESC-11-b) o cubren solo una rama de la condición
     (ESC-06-b, ESC-09-c).
   - **No accionables (6):** se quedan en comprobar o verificar, sin acción correctiva (ESC-01-c, ESC-03-c,
     ESC-05-c, ESC-07-b, ESC-07-c y ESC-11-c). Son también los seis casos con pertinencia 1.
3. **Respaldo y seguridad.** Todo lo que afirman los diagnósticos está en el log: respaldo 2 en los 20 casos.
   Ninguna recomendación es riesgosa sin advertencia. Las 3 con seguridad 1 (ESC-08-b, ESC-08-c y ESC-09-c)
   proponen reintentar un despliegue o repetir una limpieza, con una verificación previa.
4. **Defectos de escenario.** Ningún revisor marcó defectos en los 20 casos.

Este análisis describe el comportamiento del diagnóstico. La percepción y la utilidad para los usuarios
corresponden a OE4.

### 3.4 Prueba funcional del dashboard (protocolo §7.7)

- **Incidente visible:** 20/20 casos positivos, de los 10 escenarios.
- **Secciones coherentes:** en los 20 casos, la evidencia, la hipótesis, la recomendación, las citas y el
  modelo del dashboard coinciden con la hoja del revisor.
- **Revisión registrada:** 20/20, visibles en el historial de revisiones de cada incidente.
  - En 19 casos la decisión registrada corresponde a la puntuación: 17 Confirmar y 2 Rechazar con la causa
    real.
  - En ESC-03-b se registró Confirmar por error al pulsar. Vale la puntuación del registro del revisor
    (1, categoría B). Como exige §8.3, la revisión no se editó; la diferencia consta en `dashboard_notes`.
  - `metrics.json` cuenta la decisión según el registro del revisor (17 y 3).
- **Evidencia:** una captura por caso (`screenshots/`), sin usuario, avatar ni correo, y las columnas
  `dashboard_*` de `review-A.csv` y `review-B.csv`.

### 3.5 Controles

- **Fuera del inventario (6 casos):** 3/6 con puntuación 2 en las dos corridas y **ninguna atribución falsa** a
  un patrón del inventario. Estos diagnósticos tampoco citaron documentos del corpus. NC-02-c pasó de 1 a 0
  porque la respuesta del modelo varió entre corridas.
- **Sin fallo (2 casos):** ninguno abrió incidente en ninguna de las dos corridas.

### 3.6 Recuperación y citas (segunda corrida)

- **Recuperación con la evidencia exacta enviada por Pipesor** (documentación técnica): hit@1 0,75, hit@3
  **1,00** y MRR@10 0,875. En la primera corrida: 0,80, 1,00 y 0,90.
- **Coincidencia con el servicio:** las puntuaciones que registró el servicio (líneas `rag_retrieval`)
  coinciden con las de la emulación del arnés en 23 de 26 diagnósticos. En los otros 3 difieren en 0,0023
  como máximo; en la primera corrida coincidieron 24 de 26.
- **Precisión de citas:** 0,971 en los 17 diagnósticos que citan el corpus. En la primera corrida, 0,947 en 19.

### 3.7 Recomendación, volumen y latencia (segunda corrida)

- **Rúbrica de recomendación** (0–2) en los 20 positivos:
  - revisión humana: pertinencia 1,70, respaldo en evidencia 2,00 y seguridad 1,85;
  - juez LLM: 1,75, 2,00 y 2,00 (1,69, 1,96 y 2,00 con los 26 diagnósticos).
- **Volumen:** 5280 líneas de log en los jobs fallidos diagnosticados; de ellas, 599 llegaron al diagnóstico
  como evidencia, por el extracto de hasta 40 líneas.
- **Latencia** desde el fin de la ejecución hasta el diagnóstico disponible: mediana 33 s (21–47 s). Es un dato
  descriptivo, no TMD.

## 4. Desviaciones respecto del protocolo

| Desviación | Motivo | Efecto |
|---|---|---|
| La rúbrica de las corridas la aplicó un juez LLM, sin puntuaciones humanas (v0.5 §8.3) | Al fijar v0.5 no se contemplaban validaciones humanas este semestre | Desde v0.7, la revisión humana de los 20 positivos es la cifra principal y el juez es verificación auxiliar. Los 6 controles fuera del inventario conservan la puntuación del juez |
| Corrección de escenarios y segunda corrida después de ver resultados de `test` (v0.6 §4, §10) | Tres casos positivos con defectos de escenario en la primera corrida | Se reportan ambas corridas; la segunda es la oficial y la última del semestre (§6) |
| Modelo elegido sin la rúbrica (v0.4, ADR-026) | Decisión del responsable del proyecto | La selección se apoya en el filtro eliminatorio y el indicador automático |
| Umbral de similitud no adoptado (§6.1) | Separación de 0,0007 con 3 casos | Sin umbral; se registran las puntuaciones |
| ESC-04 no implementado (v0.5 §14) | La ingestión no prepara evidencia para `startup_failure` | C10 queda fuera de la medición |

## 5. Defectos de escenario y hallazgos

- **Defectos corregidos** (revisión r2, pipesor-validation-scenarios#14). En la primera corrida, el consenso
  del juez marcó tres positivos cuya evidencia no permitía identificar la causa de referencia:
  - **ESC-01-b.** Solo se veía `taxRate` no declarado; la referencia exige saber que existe `TaxRate`. Ahora
    `TaxRate` es un campo privado sin usar y el build también imprime CS0414, que lo nombra.
  - **ESC-01-c.** Solo se veía `Guard` no resuelto, sin poder distinguir si faltaba la clase o había un problema
    de ámbito. Ahora el archivo importa `Orders.Api.Validation` y el build informa que ese espacio de nombres
    no existe (CS0234). La referencia nombra ese espacio de nombres.
  - **ESC-08 (las tres variantes).** Las horas de inicio de los run commands eran fijas de la noche anterior.
    Ahora son relativas a la ejecución.
    - ESC-08-c: la referencia dejó de exigir que el otro job fuera «del mismo pipeline», un dato que no era
      visible en el log.
  - **Efecto:** según el juez, los tres pasaron a 2 en la segunda corrida y ninguno quedó marcado como
    defecto. En la revisión humana, ESC-01-b y ESC-08-c obtuvieron 2 y ESC-01-c obtuvo 1 (categoría C,
    §3.2); ningún revisor marcó defectos.
- **Defectos no corregidos** (controles fuera del inventario, que no entran en la métrica principal):
  - NC-02-b/c: la salida de unittest no muestra la implementación.
  - NC-03-b: el log no lista el contenido del contexto de Docker.
- **Límite de la plataforma, no defecto de escenario:**
  - **NC-01-c.** La protección de la ingestión enmascara `left-pad@1.4.0`.
  - **En general,** la protección enmascara tokens con IP o `@` (por ejemplo `paquete@versión` de npm) y
    rechaza extractos con comillas escapadas. Se adaptaron los fixtures afectados.
- **Hallazgo de la plataforma durante la validación:** nombres de job repetidos en un workflow impedían
  capturar la evidencia. Se corrigió en la ingestión (pipesor-ingestion-normalization-service #38); los
  primeros diagnósticos reales recién se obtuvieron tras esa corrección.

## 6. Amenazas a la validez

- **Interna.**
  - El equipo construyó los escenarios, las causas de referencia y el corpus a partir del mismo inventario.
    Mitigaciones: variantes `test` no usadas para ajustar, controles fuera del inventario, prueba de fugas y
    configuración congelada antes de cada corrida.
  - **Corrección posterior a los resultados.** Los escenarios se corrigieron después de ver la primera corrida
    de `test`, lo que puede favorecer el resultado. Mitigaciones:
    - la regla de selección es la marca de defecto del evaluador, no la puntuación: ESC-03-b y ESC-08-b, con 1,
      no se tocaron;
    - la corrección exige mostrar en la evidencia el mismo elemento que pide la referencia, no rebajar la
      referencia;
    - se repitieron los 28 casos;
    - la segunda corrida se declaró de antemano como la última;
    - se reportan ambas corridas.

    Aun así, la reformulación de ESC-01-c (el espacio de nombres en lugar de la clase `Guard`) cambia lo que
    el caso exige y debe leerse como tal.
  - **El juez LLM marcó los defectos** que motivaron la corrección. Puede tener sesgos propios: es un modelo de
    otro tramo de la misma familia. La revisión humana de la corrida oficial no marcó defectos y coincide con
    el juez en 18 de 20 puntuaciones.
  - **Los revisores son autores** del sistema, de los escenarios y de las causas de referencia. Mitigaciones:
    rúbrica, categorías y causas de referencia fijadas antes de la revisión; alias y orden aleatorio;
    coherencia verificada por `harness.review`; contraste con el juez LLM; y registros completos (hojas,
    puntuaciones, justificaciones y capturas) para que los asesores los verifiquen.
  - **Un único revisor por caso.** No se mide el acuerdo entre humanos. La verificación de la medición es el
    acuerdo con el juez, reportado también por revisor (§3.2).
  - **Cegamiento parcial.** Uno de los integrantes conoció las puntuaciones del juez antes de la revisión. En
    los dos casos en que la revisión humana difiere del juez, es más estricta que él.
- **De constructo.**
  - Los escenarios son sintéticos y 4 de los 10 positivos usan respuestas simuladas.
  - El diagnóstico ve un extracto de hasta 40 líneas.
  - La rúbrica depende de cómo se redacta la causa de referencia, como mostró ESC-01 en la primera corrida.
- **Externa.** El inventario proviene de tres repositorios elegidos de forma intencional y de despliegues sobre
  VM/IIS. Los resultados no se generalizan a otras organizaciones.
- **De conclusión.**
  - Con N = 20, un caso equivale a 5 puntos y el intervalo es amplio: [0,64; 0,95] en la revisión humana de la
    corrida oficial.
  - El resultado supera la meta, pero no permite afirmar con 95 % de confianza que el acierto real sea
    ≥ 80 %.
- **De plataforma.** El modelo se usa en su versión fijada y las imágenes quedan registradas por digest. Un
  cambio de cualquiera de ellos invalida la comparación directa con estas corridas.

## 7. Trazabilidad al Charter

| Charter | Evidencia |
|---|---|
| OE3-I2: ≥ 1000 registros de log | `results/2026-11-23-oe3-test-r2/summary.md`, `metrics.json` (`log_lines`) |
| OE3-I2: pruebas funcionales de ingesta, recuperación, diagnóstico y reporte | `cases.jsonl` (resultado, diagnóstico, reporte), artifacts `pipesor-report-*`, líneas `rag_retrieval` del servicio |
| OE3-I2: consulta del dashboard y registro de revisión humana | §3.4; `results/review-2026-11-23-oe3-test-r2/`: capturas por caso (`screenshots/`), columnas `dashboard_*` y `review_decision` de `review-A.csv` y `review-B.csv`, y `metrics.json` (`dashboard`) |
| OE3-I2: 10 escenarios, acierto del 80 % | §3.1–§3.3; `review-2026-11-23-oe3-test-r2/metrics.json` y `qualitative.json` (revisión humana, cifra principal); `ratings-2026-11-23-oe3-test-r2/metrics.json` (juez LLM); primera corrida en `ratings-2026-11-23-oe3-test/` |
| «Enfoques del trabajo»: protocolo previo, causa de referencia, reglas de medición, casos sin diagnóstico registrados | Protocolo v0.5, v0.6 y v0.7; `eval/cases` (revisiones r1 y r2); ningún caso quedó sin diagnóstico |
| «Recursos de Datos y Evidencias»: procedencia, autorización y separación de la evaluación | `corpus/authorization.json`; `inventory/`; protocolo §5; prueba de fugas del arnés |
| CTRL-006 / INV-010 | Corpus generado solo desde `inventory/`; `eval/qrels.json` marcado como material de evaluación |
| PD-022 / PD-023 / PD-024 | Este informe, el protocolo y los manifiestos aportan la evidencia de método y resultados |

## 8. Próximos pasos

1. **OE4:** un protocolo propio con el personal del entorno de validación, 20 escenarios comparativos y TMD.
   En ese protocolo también se corregirían los controles con defecto (NC-02 y NC-03-b).
