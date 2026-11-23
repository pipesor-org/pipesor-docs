# Informe de validación del diagnóstico asistido (OE3-I2)

| Campo | Valor |
|---|---|
| Fecha | 23/11/2026 |
| Indicador | OE3-I2 del Project Charter v1.3 |
| Protocolo | [Protocolo de evaluación](protocolo-evaluacion-oe3.md), versión 0.5 (commit `f2b7b0f`) |
| Datos y código | [pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios): corrida oficial `results/2026-11-23-oe3-test/` |
| Fuera de alcance | OE4-I1 e I2 (comparación con el diagnóstico manual, TMD y 20 escenarios comparativos), previstos para el siguiente periodo |

## 1. Resumen

El Charter define OE3-I2 así: el prototipo «procesa al menos 1000 registros de logs y supera las pruebas
funcionales de ingesta, recuperación de conocimiento, diagnóstico, generación y publicación del reporte,
consulta del dashboard y registro de revisión humana. La comprobación inicial comprenderá 10 escenarios de
fallo, con una meta de acierto del 80 % en la identificación de la causa probable».

| Criterio | Resultado | Estado |
|---|---|---|
| ≥ 1000 registros de log procesados | **5279** líneas de los jobs fallidos diagnosticados | Cumplido |
| 10 escenarios de fallo por la cadena funcional | 28/28 ejecuciones según diseño; 26/26 diagnósticos generados y publicados como artifact; los 2 controles sin fallo no abrieron incidente | Cumplido para ingesta, recuperación, diagnóstico y reporte |
| Consulta del dashboard y registro de revisión humana | No se ejercitaron en la corrida automatizada | **Pendiente de evidencia** |
| Acierto ≥ 80 % en la causa probable | **15/20 = 75 %** en los casos `test` positivos, IC de Wilson 95 % [0,53; 0,89], **evaluado automáticamente** | **No alcanzado** |

**Conclusión.** La cadena completa funciona de punta a punta sobre escenarios controlados, con volumen
suficiente, recuperación precisa y recomendaciones seguras. El acierto evaluado automáticamente queda
**un caso por debajo de la meta**: con 16/20 se cumpliría el 80 %. El intervalo de confianza incluye la meta,
así que con 20 casos el resultado no permite afirmar ni descartar que el sistema la alcance. Tres de los
cinco casos no acertados tienen defectos de escenario identificados (§5). El indicador no se declara cumplido.

## 2. Método

Se resume aquí; el detalle completo está en el protocolo v0.5.

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
  - El corpus RAG (22 documentos, 33 fragmentos) se genera solo a partir del inventario, con procedencia y
    autorización registradas.
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
- **Configuración congelada** (§15 del protocolo):
  - gpt-6-luna 2026-09-22 con el prompt `diagnostic-hypothesis-v2`;
  - la recuperación descrita arriba;
  - el corpus importado con el alcance `scope-r1`;
  - captura por webhook;
  - los digests de las 7 imágenes desplegadas, registrados en el manifiesto.
- **Ejecución oficial.** Las 28 ejecuciones de `test` se lanzaron una sola vez. Cada diagnóstico se recogió
  del artifact `pipesor-report`, obtenido por OIDC.
- **Evaluación.** La rúbrica 0/1/2 de causa probable, y la de recomendación, la aplicó un **juez LLM**:
  - gpt-6.2-sol, distinto del modelo que diagnostica, con salida JSON estricta;
  - 3 juicios por ítem, con mediana de las puntuaciones;
  - para ver lo mismo que vería una persona, recibe la evidencia enviada, el diagnóstico, la causa de
    referencia, la evidencia clave y la corrección esperada.

  Este semestre no se recogieron puntuaciones humanas: es una desviación registrada en el §8.3 del protocolo.

## 3. Resultados

### 3.1 Acierto en la causa probable (`test`, evaluado automáticamente)

| Escenario | Patrón | Reproducción | b | c |
|---|---|---|---|---|
| ESC-01 | C01 compilación | real | 1 | 0 |
| ESC-02 | C02 ruta | real | 2 | 2 |
| ESC-03 | C08 IIS | simulada | 1 | 2 |
| ESC-05 | C11 plazo de sondeo | real | 2 | 2 |
| ESC-06 | C06 sondeo sin respuesta | real | 2 | 2 |
| ESC-07 | C03 RBAC | simulada | 2 | 2 |
| ESC-08 | C04 operación desplazada | simulada | 1 | 1 |
| ESC-09 | C09 permisos | real | 2 | 2 |
| ESC-10 | C07 HTTP 500 | real | 2 | 2 |
| ESC-11 | C05 extensión de VM | simulada | 2 | 2 |

- **Acierto estricto:** 15/20 = 75 %, IC de Wilson 95 % [0,53; 0,89].
- **Escenarios con ambas variantes en 2:** 7/10.
- **Por tipo de reproducción:** real 10/12; simulada 5/8.
- **Estabilidad del juez:** la puntuación de causa coincidió en los 3 juicios en 25 de 26 ítems. El único
  inestable es ESC-01-c (0, 2, 0).

### 3.2 Controles

- **Fuera del inventario (6 casos):** 3/6 con puntuación 2 y **ninguna atribución falsa** a un patrón del
  inventario. Estos diagnósticos tampoco citaron documentos del corpus.
- **Sin fallo (2 casos):** ninguno abrió incidente.

### 3.3 Recuperación y citas

- **Recuperación con la evidencia exacta enviada por Pipesor** (documentación técnica):
  - hit@1 0,80, hit@3 **1,00** y MRR@10 0,90, iguales a lo estimado en `dev`.
  - Las puntuaciones que registró el servicio (líneas `rag_retrieval`) coinciden con las de la emulación del
    arnés en 24 de 26 diagnósticos. En los otros dos (NC-03-b y NC-03-c, controles fuera del inventario)
    difieren en 0,003 como máximo.
- **Precisión de citas:** 0,947 en los 19 diagnósticos que citan el corpus.

### 3.4 Recomendación, volumen y latencia

- **Rúbrica de recomendación** (0–2): pertinencia 1,62, respaldo en evidencia 2,00 y seguridad 2,00.
- **Volumen:** 5279 líneas de log en los jobs fallidos diagnosticados; de ellas, 599 llegaron al diagnóstico
  como evidencia, por el extracto de hasta 40 líneas.
- **Latencia** desde el fin de la ejecución hasta el diagnóstico disponible: mediana 34 s (23–47 s). Es un dato
  descriptivo, no TMD.

## 4. Desviaciones respecto del protocolo

| Desviación | Motivo | Efecto |
|---|---|---|
| La rúbrica la aplica un juez LLM, sin puntuaciones humanas (v0.5 §8.3) | No se contemplan validaciones humanas este semestre | El acierto es una medición automática; no hay κ humano. Las hojas ciegas quedan disponibles para confirmarlo |
| Sin aprobación previa de los asesores (v0.5 §13) | Misma razón | El protocolo se fijó (v0.5) antes de la corrida oficial |
| Modelo elegido sin la rúbrica (v0.4, ADR-026) | Decisión del responsable del proyecto | La selección se apoya en el filtro eliminatorio y el indicador automático |
| Umbral de similitud no adoptado (§6.1) | Separación de 0,0007 con 3 casos | Sin umbral; se registran las puntuaciones |
| ESC-04 no implementado (v0.5 §14) | La ingestión no prepara evidencia para `startup_failure` | C10 queda fuera de la medición |

## 5. Defectos de escenario y hallazgos

- **ESC-01-b y ESC-01-c.** La causa de referencia exige información que el error del compilador no muestra: la
  constante `TaxRate` y el origen de `Guard`. Los diagnósticos identifican el identificador no declarado, que
  es el elemento visible.
  - En ESC-01-c el juez fue inestable (0, 2, 0).
  - Ajustar la causa de referencia a lo que la evidencia permite identificar es parte de la siguiente versión
    de los escenarios. Según el protocolo, el caso no se excluye.
- **ESC-08-c.** El fixture imprime horas de inicio fijas de la noche anterior, lo que debilita la atribución de
  concurrencia.
- **ESC-03-b y ESC-08-b** son aciertos parciales legítimos: el diagnóstico identifica el patrón, pero no el
  elemento determinante, o lo menciona solo como alternativa secundaria.
- **Análisis de sensibilidad** (no reemplaza la cifra principal): sin los 3 casos positivos con defecto, el
  acierto es 15/17 = 88 %.
- **Hallazgos de la plataforma durante la validación:**
  - La protección de la ingestión enmascara tokens con IP o `@` (por ejemplo `paquete@versión` de npm) y
    rechaza extractos con comillas escapadas. Se adaptaron los fixtures afectados; el efecto en npm se
    registra como limitación (NC-01-c).
  - Nombres de job repetidos en un workflow impedían capturar la evidencia. Se corrigió en la ingestión
    (pipesor-ingestion-normalization-service #38).
  - Los primeros diagnósticos reales recién se obtuvieron tras esa corrección.

## 6. Amenazas a la validez

- **Interna.**
  - El equipo construyó los escenarios, las causas de referencia y el corpus a partir del mismo inventario.
    Mitigaciones: variantes `test` no usadas para ajustar, controles fuera del inventario, prueba de fugas y
    configuración congelada antes de la corrida.
  - El juez LLM puede tener sesgos propios: es un modelo de otro tramo de la misma familia y no hay contraste
    humano.
- **De constructo.**
  - Los escenarios son sintéticos y 4 de los 10 positivos usan respuestas simuladas.
  - El diagnóstico ve un extracto de hasta 40 líneas.
  - La rúbrica depende de cómo se redactó la causa de referencia: ESC-01 muestra que una referencia más
    exigente que la evidencia reduce el acierto.
- **Externa.** El inventario proviene de tres repositorios elegidos de forma intencional y de despliegues sobre
  VM/IIS. Los resultados no se generalizan a otras organizaciones.
- **De conclusión.** Con N = 20, un caso equivale a 5 puntos y el intervalo de confianza es amplio; las
  diferencias pequeñas no son concluyentes.
- **De plataforma.** El modelo se usa en su versión fijada y las imágenes quedan registradas por digest. Un
  cambio de cualquiera de ellos invalida la comparación directa con esta corrida.

## 7. Trazabilidad al Charter

| Charter | Evidencia |
|---|---|
| OE3-I2: ≥ 1000 registros de log | `results/2026-11-23-oe3-test/summary.md`, `metrics.json` (`log_lines`) |
| OE3-I2: pruebas funcionales de ingesta, recuperación, diagnóstico y reporte | `cases.jsonl` (resultado, diagnóstico, reporte), artifacts `pipesor-report-*`, líneas `rag_retrieval` del servicio |
| OE3-I2: consulta del dashboard y registro de revisión humana | Pendiente: requiere una sesión en el dashboard sobre un incidente de esta corrida |
| OE3-I2: 10 escenarios, acierto del 80 % | §3.1; `ratings-2026-11-23-oe3-test/metrics.json` |
| «Enfoques del trabajo»: protocolo previo, causa de referencia, reglas de medición, casos sin diagnóstico registrados | Protocolo v0.5; `eval/cases`; ningún caso quedó sin diagnóstico |
| «Recursos de Datos y Evidencias»: procedencia, autorización y separación de la evaluación | `corpus/authorization.json`; `inventory/`; protocolo §5; prueba de fugas del arnés |
| CTRL-006 / INV-010 | Corpus generado solo desde `inventory/`; `eval/qrels.json` marcado como material de evaluación |
| PD-022 / PD-023 / PD-024 | Este informe, el protocolo y los manifiestos aportan la evidencia pendiente. Las aprobaciones humanas siguen fuera de este semestre |

## 8. Próximos pasos

1. Ejercitar la consulta del dashboard y registrar una revisión humana sobre un incidente de esta corrida, para
   completar la evidencia funcional de OE3-I2.
2. Corregir los escenarios ESC-01 (causa de referencia) y ESC-08 (horas del fixture) en una nueva versión.
   Medir de nuevo con una corrida y una versión del protocolo nuevas, sin reescribir esta corrida.
3. Si es posible, una confirmación humana de las puntuaciones del juez con las hojas ciegas disponibles, en
   especial ESC-01-c.
4. Para OE4: un protocolo propio con el personal del entorno de validación, 20 escenarios comparativos y TMD.
