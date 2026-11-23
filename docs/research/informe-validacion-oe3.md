# Informe de validación del diagnóstico asistido (OE3-I2)

| Campo | Valor |
|---|---|
| Fecha | 23/11/2026 |
| Indicador | OE3-I2 del Project Charter v1.3 |
| Protocolo | [Protocolo de evaluación](protocolo-evaluacion-oe3.md): versión 0.5 (commit `f2b7b0f`) para la primera corrida oficial y versión 0.6 (commit `d5251e4`) para la segunda |
| Datos y código | [pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios): corrida oficial `results/2026-11-23-oe3-test-r2/`; primera corrida `results/2026-11-23-oe3-test/` |
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

| Criterio (protocolo §11) | Primera corrida | **Segunda corrida (oficial)** | Estado |
|---|---|---|---|
| ≥ 1000 registros de log procesados | 5279 líneas | **5280** líneas de los jobs fallidos diagnosticados | Cumplido |
| Pruebas funcionales: ingesta, recuperación, diagnóstico, reporte publicado | 28/28 ejecuciones según diseño; 26/26 diagnósticos | **28/28; 26/26**; los 2 controles sin fallo no abrieron incidente | Cumplido |
| Pruebas funcionales: incidente visible en el dashboard y revisión registrada (§7.7) | No ejercitadas | No ejercitadas | **Pendiente de evidencia** |
| Acierto estricto ≥ 80 % en la causa probable | 15/20 = 75 %, IC de Wilson 95 % [0,53; 0,89] | **18/20 = 90 %, IC de Wilson 95 % [0,70; 0,97]** | **Alcanzado**, evaluado automáticamente |

**Conclusión.**
- La cadena funciona de punta a punta sobre escenarios controlados, con volumen suficiente, recuperación
  precisa y recomendaciones seguras.
- El acierto evaluado automáticamente supera la meta del 80 %. El límite inferior del intervalo (0,70) queda
  por debajo de la meta: con 20 casos, el resultado debe leerse junto con sus límites (§11).
- Toda la diferencia entre las dos corridas proviene de los tres casos corregidos. Los otros 17 positivos
  obtuvieron exactamente la misma puntuación en ambas.
- Faltan dos etapas funcionales para declarar cumplido el indicador según el §11: el incidente visible en el
  dashboard y la revisión registrada (§8).

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
- **Evaluación.** La rúbrica 0/1/2 de causa probable, y la de recomendación, la aplicó un **juez LLM**:
  - gpt-6.2-sol, distinto del modelo que diagnostica, con salida JSON estricta;
  - 3 juicios por ítem, con mediana de las puntuaciones;
  - para ver lo mismo que vería una persona, recibe la evidencia enviada, el diagnóstico, la causa de
    referencia, la evidencia clave y la corrección esperada.

  Este semestre no se recogieron puntuaciones humanas: es una desviación registrada en el §8.3 del protocolo.

## 3. Resultados

### 3.1 Acierto en la causa probable (`test`, evaluado automáticamente)

| Escenario | Patrón | Reproducción | 1.ª corrida b | 1.ª corrida c | **2.ª corrida b** | **2.ª corrida c** |
|---|---|---|---|---|---|---|
| ESC-01 | C01 compilación | real | 1 | 0 | **2** | **2** |
| ESC-02 | C02 ruta | real | 2 | 2 | 2 | 2 |
| ESC-03 | C08 IIS | simulada | 1 | 2 | 1 | 2 |
| ESC-05 | C11 plazo de sondeo | real | 2 | 2 | 2 | 2 |
| ESC-06 | C06 sondeo sin respuesta | real | 2 | 2 | 2 | 2 |
| ESC-07 | C03 RBAC | simulada | 2 | 2 | 2 | 2 |
| ESC-08 | C04 operación desplazada | simulada | 1 | 1 | 1 | **2** |
| ESC-09 | C09 permisos | real | 2 | 2 | 2 | 2 |
| ESC-10 | C07 HTTP 500 | real | 2 | 2 | 2 | 2 |
| ESC-11 | C05 extensión de VM | simulada | 2 | 2 | 2 | 2 |

Segunda corrida (oficial):
- **Acierto estricto:** 18/20 = 90 %, IC de Wilson 95 % [0,70; 0,97].
- **Escenarios con ambas variantes en 2:** 8/10.
- **Por tipo de reproducción:** real 12/12; simulada 6/8.
- **Casos por debajo de 2:** ESC-03-b y ESC-08-b, aciertos parciales con puntuación 1 en las dos corridas.
  El diagnóstico identifica el patrón, pero no el elemento determinante (la aplicación padre `/portal` y la
  actualización de `WindowsPatchExtension`), o lo menciona solo como alternativa secundaria.
- **Estabilidad del juez:** la puntuación de causa coincidió en los 3 juicios en 26 de 26 ítems; en la primera
  corrida, en 25 de 26.
- **Estabilidad entre corridas:** los 17 positivos que no cambiaron obtuvieron la misma puntuación en ambas
  corridas. La primera corrida dio 15/20, IC [0,53; 0,89].

### 3.2 Controles

- **Fuera del inventario (6 casos):** 3/6 con puntuación 2 en las dos corridas y **ninguna atribución falsa** a
  un patrón del inventario. Estos diagnósticos tampoco citaron documentos del corpus. NC-02-c pasó de 1 a 0
  porque la respuesta del modelo varió entre corridas.
- **Sin fallo (2 casos):** ninguno abrió incidente en ninguna de las dos corridas.

### 3.3 Recuperación y citas (segunda corrida)

- **Recuperación con la evidencia exacta enviada por Pipesor** (documentación técnica): hit@1 0,75, hit@3
  **1,00** y MRR@10 0,875. En la primera corrida: 0,80, 1,00 y 0,90.
- **Coincidencia con el servicio:** las puntuaciones que registró el servicio (líneas `rag_retrieval`)
  coinciden con las de la emulación del arnés en 23 de 26 diagnósticos. En los otros 3 difieren en 0,0023
  como máximo; en la primera corrida coincidieron 24 de 26.
- **Precisión de citas:** 0,971 en los 17 diagnósticos que citan el corpus. En la primera corrida, 0,947 en 19.

### 3.4 Recomendación, volumen y latencia (segunda corrida)

- **Rúbrica de recomendación** (0–2): pertinencia 1,69, respaldo en evidencia 1,96 y seguridad 2,00.
- **Volumen:** 5280 líneas de log en los jobs fallidos diagnosticados; de ellas, 599 llegaron al diagnóstico
  como evidencia, por el extracto de hasta 40 líneas.
- **Latencia** desde el fin de la ejecución hasta el diagnóstico disponible: mediana 33 s (21–47 s). Es un dato
  descriptivo, no TMD.

## 4. Desviaciones respecto del protocolo

| Desviación | Motivo | Efecto |
|---|---|---|
| La rúbrica la aplica un juez LLM, sin puntuaciones humanas (v0.5 §8.3) | No se contemplan validaciones humanas este semestre | El acierto es una medición automática; no hay κ humano. Las hojas ciegas quedan disponibles para confirmarlo |
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
  - **Efecto:** los tres pasaron a 2 en la segunda corrida y ninguno quedó marcado como defecto.
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
  - **El mismo juez LLM** marca los defectos y puntúa los casos. Puede tener sesgos propios: es un modelo de
    otro tramo de la misma familia y no hay contraste humano.
- **De constructo.**
  - Los escenarios son sintéticos y 4 de los 10 positivos usan respuestas simuladas.
  - El diagnóstico ve un extracto de hasta 40 líneas.
  - La rúbrica depende de cómo se redacta la causa de referencia, como mostró ESC-01 en la primera corrida.
- **Externa.** El inventario proviene de tres repositorios elegidos de forma intencional y de despliegues sobre
  VM/IIS. Los resultados no se generalizan a otras organizaciones.
- **De conclusión.**
  - Con N = 20, un caso equivale a 5 puntos y el intervalo es amplio: [0,70; 0,97] en la corrida oficial.
  - El resultado supera la meta, pero no permite afirmar con 95 % de confianza que el acierto real sea
    ≥ 80 %.
- **De plataforma.** El modelo se usa en su versión fijada y las imágenes quedan registradas por digest. Un
  cambio de cualquiera de ellos invalida la comparación directa con estas corridas.

## 7. Trazabilidad al Charter

| Charter | Evidencia |
|---|---|
| OE3-I2: ≥ 1000 registros de log | `results/2026-11-23-oe3-test-r2/summary.md`, `metrics.json` (`log_lines`) |
| OE3-I2: pruebas funcionales de ingesta, recuperación, diagnóstico y reporte | `cases.jsonl` (resultado, diagnóstico, reporte), artifacts `pipesor-report-*`, líneas `rag_retrieval` del servicio |
| OE3-I2: consulta del dashboard y registro de revisión humana | Pendiente: incidente visible en el dashboard en al menos un caso por escenario y revisión registrada (protocolo §7.7) |
| OE3-I2: 10 escenarios, acierto del 80 % | §3.1; `ratings-2026-11-23-oe3-test-r2/metrics.json`; primera corrida en `ratings-2026-11-23-oe3-test/` |
| «Enfoques del trabajo»: protocolo previo, causa de referencia, reglas de medición, casos sin diagnóstico registrados | Protocolo v0.5 y v0.6; `eval/cases` (revisiones r1 y r2); ningún caso quedó sin diagnóstico |
| «Recursos de Datos y Evidencias»: procedencia, autorización y separación de la evaluación | `corpus/authorization.json`; `inventory/`; protocolo §5; prueba de fugas del arnés |
| CTRL-006 / INV-010 | Corpus generado solo desde `inventory/`; `eval/qrels.json` marcado como material de evaluación |
| PD-022 / PD-023 / PD-024 | Este informe, el protocolo y los manifiestos aportan la evidencia de método y resultados |

## 8. Próximos pasos

1. **Completar las pruebas funcionales de §7.7**, condición necesaria para declarar cumplido OE3-I2:
   - verificar en el dashboard el incidente de al menos un caso por escenario de la corrida oficial;
   - registrar en el dashboard una revisión con la decisión de consenso.
2. **Revisión humana de los 20 diagnósticos positivos** (protocolo v0.7, §8.3 y §8.4), en curso.
   - Cada integrante revisa una variante de cada escenario.
   - La revisión aporta la cifra principal de acierto, el acuerdo con el juez LLM, el análisis cualitativo
     y la evidencia del dashboard del punto 1.
3. **OE4:** un protocolo propio con el personal del entorno de validación, 20 escenarios comparativos y TMD.
   En ese protocolo también se corregirían los controles con defecto (NC-02 y NC-03-b).
