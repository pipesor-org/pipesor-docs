# Protocolo de evaluación del diagnóstico asistido (OE3-I2)

| Campo | Valor |
|---|---|
| Versión | 0.3 — **borrador para aprobación** (historial en §13) |
| Fecha | 23/11/2026 |
| Alcance | Indicador OE3-I2 del Project Charter v1.3. OE4 queda fuera de este protocolo. |
| Repositorio de ejecución | [pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios) |
| Evaluación de la rúbrica | Los dos integrantes del equipo del proyecto (§8.3) |
| Revisión y aprobación | Pendiente: asesor especializado y asesor metodológico (§13) |

Este documento fija, **antes de ejecutar las pruebas oficiales**, los escenarios, la causa de referencia,
las reglas de medición, la rúbrica y los criterios de aceptación del diagnóstico de Pipesor. Así lo
exige el Charter («Enfoques del trabajo»: «Antes de las pruebas comparativas se aprobará un protocolo que
establezca los escenarios, la evidencia disponible, la causa de referencia y las reglas de medición»).
El protocolo atiende parcialmente [PD-022, PD-023 y PD-024](../architecture/pending-decisions.md):
define el método y deja la evidencia de su aprobación y de los resultados para los registros indicados
en §12–§13. No resuelve PD-001 (TMD).

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
| ESC-04 | C10 fallo de inicialización del workflow | pendiente (§14) | — |

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

## 5. Separación entre conocimiento y evaluación

Rigen CTRL-006 e INV-010 ([architecture.yml](../../model/architecture.yml)), DD-007 y
[ADR-021](../architecture/decisions/ADR-021-rag-runtime-contract-v0.1.md), además de «Recursos de Datos
y Evidencias» del Charter: «Los casos destinados a la evaluación y sus soluciones de referencia se
mantendrán separados del contenido utilizado para preparar la recuperación».

- El corpus RAG se genera solo a partir del inventario (`inventory/`), con procedencia y referencia de
  autorización por documento.
- Los casos, las causas de referencia, los juicios de relevancia (`qrels`) y los extractos del entorno de
  validación viven en `eval/` y nunca se importan.
- El importador solo verifica la marca `evaluation_material`. La separación efectiva se comprueba en el
  repositorio de ejecución: el generador del corpus no lee `eval/`, y una prueba busca líneas de
  evaluación dentro de los fragmentos del corpus.
- La importación del corpus en un entorno requiere aprobación explícita del responsable del entorno.

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
  - `top_k`: el menor valor que alcanza el máximo hit@k en `dev`;
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
   - incidente visible en el dashboard (verificado en una muestra de al menos un caso por escenario);
   - revisión humana registrada en el dashboard con la decisión de consenso.
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

- Asignan las puntuaciones, de forma independiente, los **dos integrantes del equipo del proyecto**
  (evaluadores A y B). Al equipo le corresponde obtener las métricas y sustentarlas. Los asesores
  revisan este protocolo y califican el logro del indicador a partir del informe y de los registros de
  evaluación, que quedan disponibles para su verificación (§10).
- Cada evaluador recibe, por caso: el extracto de evidencia tal como se envió, el diagnóstico, la causa
  de referencia y la evidencia clave.
- Los casos se presentan en orden aleatorio con identificadores anonimizados. No se revela la
  configuración (C0, C1…).
- Las discrepancias se resuelven en una sesión de consenso que queda registrada. La puntuación final es
  la de consenso.
- La concordancia se reporta con el κ de Cohen sobre las puntuaciones previas al consenso, en escala
  0/1/2 y en forma binaria (2 frente a menos de 2).
- **Juez LLM (recomendado como verificación auxiliar).** Los evaluadores son autores del sistema
  (§12), así que se aplica un juez LLM independiente.
  - Usa un despliegue distinto del modelo que diagnostica y un prompt versionado, con las mismas
    entradas y la misma rúbrica.
  - Se reporta su concordancia con el consenso y cada caso en que discrepe.
  - Nunca sustituye la evaluación humana.
- En OE4, el próximo periodo, la evaluación quedará a cargo del personal del entorno de validación. Eso
  se definirá en un protocolo propio.

## 9. Métricas

| Métrica | Definición | Uso |
|---|---|---|
| **Acierto estricto (principal)** | Casos con puntuación 2 / 20 casos `test` de los 10 escenarios positivos. Los casos sin diagnóstico cuentan como 0. Se reporta con IC de Wilson al 95 %. | Criterio OE3-I2: ≥ 80 % (≥ 16/20). |
| Acierto por escenario | Escenarios con ambas variantes `test` en 2. | Descriptiva. |
| Distribución de la rúbrica | Proporción de casos con 0, 1 y 2, por escenario y por tipo de reproducción. | Descriptiva. |
| Concordancia | κ de Cohen entre evaluadores; κ del juez LLM frente al consenso. | Calidad de la medición. |
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
    - ocultamiento de la configuración y orden aleatorio;
    - dos evaluaciones independientes con κ antes del consenso;
    - concordancia con un juez LLM independiente;
    - registros completos disponibles para que los asesores los verifiquen.
- **De constructo.**
  - Los escenarios son sintéticos y cuatro usan respuestas simuladas.
  - El extracto de 40 líneas puede omitir contexto: se observó con la ayuda que imprime `npm ci`.
  - La rúbrica conserva cierta subjetividad, que se mitiga con dos evaluadores y κ.
- **Externa.**
  - El inventario procede de tres repositorios elegidos de forma intencional, con despliegues sobre
    VM/IIS. Los resultados no se generalizan a otras organizaciones ni plataformas.
- **De conclusión.**
  - N pequeño e IC amplios.
  - Las diferencias de ablación con pocos pares discordantes pueden no ser significativas.
- **De plataforma.**
  - Cambios del modelo desplegado o de las imágenes entre corridas. Mitigación: el manifiesto fija
    versiones y digests, y las corridas comparadas comparten entorno.

## 13. Aprobación y cambios

| Rol | Responsabilidad | Decisión | Fecha |
|---|---|---|---|
| Asesor especializado | Revisa y aprueba el protocolo; califica el logro del indicador | Pendiente | — |
| Asesor metodológico | Revisa y aprueba el protocolo; califica el logro del indicador | Pendiente | — |

- La aprobación cubre este protocolo y las rúbricas de §8, y se registra antes de la primera corrida
  oficial.

| Versión | Fecha | Cambio |
|---|---|---|
| 0.1 | 23/11/2026 | Borrador inicial. |
| 0.2 | 23/11/2026 | Los integrantes del equipo asignan las puntuaciones de la rúbrica. Los asesores revisan el protocolo y califican el logro del indicador. El juez LLM pasa a ser verificación auxiliar recomendada y se añade la amenaza de evaluadores autores. |
| 0.3 | 23/11/2026 | Procedimiento preregistrado de selección en `dev`: primero la recuperación (§6.1) y después el modelo (§6.2). Efecto de la protección de la ingestión sobre la evidencia (§3). La medición de la recuperación queda resuelta: local con el despliegue de embeddings del entorno. |
- Cualquier cambio posterior genera una nueva versión con su motivo. Las corridas indican la versión
  aplicada.

## 14. Decisiones pendientes antes de aprobar

1. **ESC-04 (C10, `startup_failure`).** El perfil de ingestión vigente no prepara evidencia para ese
   resultado, por lo que no habrá diagnóstico. Opciones:
   - (a) incluirlo y contarlo como 0, con lo que el máximo posible baja a 10/11;
   - (b) reportarlo aparte como límite de cobertura de la ingestión, fuera del denominador.

   Hasta decidir, los 10 escenarios positivos de §3 cumplen el mínimo de OE3-I2.
2. **Disparo del análisis.** Opciones:
   - captura automática por webhook en dev, recomendada porque hace interpretable la latencia;
   - solicitud manual desde el dashboard.
3. **Repeticiones** de la configuración final (§7.8): una o tres.
4. **Modelo del tramo sol** para §6.2: gpt-6.1-sol (más maduro) o gpt-6.2-sol (más reciente).

Resuelto en la versión 0.3: la recuperación se mide en local con el despliegue de embeddings del entorno
(`pipesor-dev-embeddings`), autorizado por el responsable del proyecto. No requiere cambios de IaC.
