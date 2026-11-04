# tech_drift_resolutions.md

> **Propósito:** registrar las desviaciones tecnológicas y arquitectónicas entre los documentos iniciales de investigación y las decisiones vigentes del proyecto, para evitar que pipelines de Diagrams-as-Code (DaC), agentes o documentación derivada reconstruyan una arquitectura obsoleta.
>
> **Jerarquía de precedencia:**  
> 1. **Project Charter v1.3**  
> 2. **Decisiones arquitectónicas confirmadas posteriormente por el equipo del proyecto**  
> 3. **Este archivo `tech_drift_resolutions.md`**  
> 4. Trabajo de investigación, benchmarking y documentos históricos  
> 5. Diagramas históricos
>
> **Regla crítica:** cuando un documento histórico contradiga este registro, debe considerarse desactualizado para fines de arquitectura TO-BE.
>
> **Drift controlado pendiente:** la tecnología concreta del **motor AIOps de detección de anomalías** sigue abierta. **LogBERT es la candidata principal, pero NO es una decisión definitiva** hasta completar la revisión del trabajo de investigación y benchmarking frente a alternativas más recientes.

---

## 1. Repositorio y plataforma CI/CD principal

- **Capa o Componente:** Repositorio de código y ejecución CI/CD.
- **Stack Antiguo (Obsoleto):** Azure DevOps como plataforma principal; Jenkins y GitHub Actions aparecían como alternativas.
- **Stack Actualizado (Definitivo):** **GitHub + GitHub Actions** como plataforma principal del MVP y del entorno de validación.
- **Justificación del Cambio:** Los repositorios del área fueron migrados a GitHub y el Project Charter v1.3 formaliza la integración del prototipo con GitHub Actions.

## 2. Integración con la plataforma CI/CD

- **Capa o Componente:** Integración con workflows CI/CD.
- **Stack Antiguo (Obsoleto):** Conectores genéricos orientados a Azure DevOps/Jenkins y recuperación directa de logs.
- **Stack Actualizado (Definitivo):** **Integración con GitHub Actions mediante APIs, webhooks/conectores y recuperación de artefactos y metadatos autorizados**.
- **Justificación del Cambio:** Permite desacoplar el prototipo de la lógica del workflow y operar como una capa AIOps externa.

## 3. Modelo de acceso a GitHub

- **Capa o Componente:** Seguridad de integración.
- **Stack Antiguo (Obsoleto):** Acceso genérico a repositorios y pipelines sin política de privilegios formalizada.
- **Stack Actualizado (Definitivo):** **Read-only por defecto, mínimo privilegio, autorización explícita y auditoría de accesos**.
- **Justificación del Cambio:** El prototipo necesita consumir evidencia para diagnosticar; no requiere modificar repositorios, secretos, workflows o despliegues.

## 4. Posicionamiento arquitectónico del prototipo

- **Capa o Componente:** Rol del prototipo en el ecosistema DevOps.
- **Stack Antiguo (Obsoleto):** Plataforma AIOps descrita en algunos artefactos como solución con observabilidad y automatización propias.
- **Stack Actualizado (Definitivo):** **Capa AIOps integracional y no invasiva** sobre las herramientas CI/CD, observabilidad y DevSecOps existentes.
- **Justificación del Cambio:** El alcance formal excluye reemplazar repositorios, plataformas CI/CD u observabilidad existentes.

## 5. Scanners DevSecOps

- **Capa o Componente:** Fuentes externas de evidencia.
- **Stack Antiguo (Obsoleto):** Herramientas DevSecOps omitidas o tratadas únicamente de forma genérica.
- **Stack Actualizado (Definitivo):** **Checkmarx, Mend y Wiz como fuentes opcionales de evidencia en entornos lower**.
- **Justificación del Cambio:** Son scanners utilizados en los pipelines del entorno objetivo y pueden aportar hallazgos de quality gates, dependencias, seguridad o configuración sin convertirse en dependencias del core.

## 6. Entorno de uso de scanners

- **Capa o Componente:** Alcance de integración DevSecOps.
- **Stack Antiguo (Obsoleto):** Integración potencial sin distinción de ambiente.
- **Stack Actualizado (Definitivo):** **Uso orientado a entornos lower/no productivos durante el MVP y la validación**.
- **Justificación del Cambio:** Coincide con el alcance del proyecto, que excluye el despliegue obligatorio sobre pipelines críticos de producción.

## 7. Captura e ingesta

- **Capa o Componente:** Servicio de ingesta.
- **Stack Antiguo (Obsoleto):** Adaptadores genéricos para múltiples plataformas CI/CD.
- **Stack Actualizado (Definitivo):** **Servicio de ingesta desacoplado especializado inicialmente en GitHub Actions**, manteniendo contratos estándar para futuras fuentes.
- **Justificación del Cambio:** Reduce complejidad del MVP sin perder extensibilidad.

## 8. Privacy Gateway

- **Capa o Componente:** Protección previa de datos.
- **Stack Antiguo (Obsoleto):** `Privacy Gateway` representado como componente/microservicio independiente.
- **Stack Actualizado (Definitivo):** **No existe un componente denominado Privacy Gateway.** Masking, anonimización, minimización, filtrado de secretos y validación forman parte de la etapa de ingesta/normalización y de los controles transversales.
- **Justificación del Cambio:** `Privacy Gateway` fue una agrupación conceptual de responsabilidades, no una decisión arquitectónica real.

## 9. Protección de información sensible

- **Capa o Componente:** Privacy by Design.
- **Stack Antiguo (Obsoleto):** Enmascaramiento tratado principalmente como control transversal o posterior.
- **Stack Actualizado (Definitivo):** **Anonimización/enmascaramiento, minimización, filtrado de secretos y trazabilidad antes del procesamiento por componentes AIOps/LLM**.
- **Justificación del Cambio:** Evita exponer información corporativa sensible a componentes analíticos o servicios externos.

## 10. Política de retención

- **Capa o Componente:** Conservación de datos y evidencias.
- **Stack Antiguo (Obsoleto):** Retención máxima fija de 90 días.
- **Stack Actualizado (Definitivo):** **Retención definida por la política institucional, el entorno de validación y las obligaciones aplicables**.
- **Justificación del Cambio:** Un periodo fijo no debe codificarse como propiedad arquitectónica sin respaldo normativo o corporativo formal.

## 11. Infraestructura cloud

- **Capa o Componente:** Plataforma física de despliegue.
- **Stack Antiguo (Obsoleto):** AWS/EKS como referencia principal o infraestructura cloud agnóstica sin selección definitiva.
- **Stack Actualizado (Definitivo):** **Microsoft Azure**.
- **Justificación del Cambio:** Se busca reducir fricción de integración y compliance con el ecosistema tecnológico corporativo objetivo, manteniendo la arquitectura lógica desacoplada.

## 12. Estrategia cloud

- **Capa o Componente:** Portabilidad arquitectónica.
- **Stack Antiguo (Obsoleto):** Posible dependencia conceptual de servicios AWS.
- **Stack Actualizado (Definitivo):** **Arquitectura lógica basada en capacidades; arquitectura física del MVP desplegada en Azure**.
- **Justificación del Cambio:** Permite documentar una implementación concreta sin convertir cada servicio Azure en una dependencia conceptual irreversible.

## 13. Contenedorización

- **Capa o Componente:** Despliegue de servicios.
- **Stack Antiguo (Obsoleto):** Kubernetes/EKS como destino obligatorio.
- **Stack Actualizado (Definitivo):** **Servicios contenedorizados en entorno Azure controlado; el orquestador concreto no se fija en este registro**.
- **Justificación del Cambio:** El Charter exige contenedores y entorno cloud controlado, pero no obliga a Kubernetes.

## 14. Broker de eventos

- **Capa o Componente:** Mensajería asíncrona.
- **Stack Antiguo (Obsoleto):** Kafka, RabbitMQ o Azure Service Bus como alternativas abiertas.
- **Stack Actualizado (Definitivo):** **Azure Service Bus**.
- **Justificación del Cambio:** Se alinea con Azure y evita administrar un broker propio durante el prototipo.

## 15. Patrón de mensajería

- **Capa o Componente:** Comunicación entre servicios.
- **Stack Antiguo (Obsoleto):** Integraciones punto a punto o broker no especificado.
- **Stack Actualizado (Definitivo):** **Mensajería persistente y asíncrona mediante Azure Service Bus** entre ingesta y procesamiento.
- **Justificación del Cambio:** Reduce acoplamiento y absorbe variaciones en el volumen de logs/eventos.

## 16. Procesamiento inicial de logs

- **Capa o Componente:** Parsing y normalización.
- **Stack Antiguo (Obsoleto):** Drain/Drain3 como parser obligatorio.
- **Stack Actualizado (Definitivo):** **Capacidad de parsing, limpieza y normalización de logs; Drain/Drain3 permanece como opción de implementación**.
- **Justificación del Cambio:** El diseño debe depender de la función de estructuración y no de un algoritmo específico.

## 17. Procesamiento NLP

- **Capa o Componente:** Representación semántica de logs.
- **Stack Antiguo (Obsoleto):** `all-MiniLM` / Sentence Transformers fijados como tecnología obligatoria.
- **Stack Actualizado (Definitivo):** **Embeddings/representación semántica como capacidad del pipeline NLP; modelo concreto reemplazable**.
- **Justificación del Cambio:** Permite adoptar una alternativa más adecuada sin rediseñar el core.

## 18. Motor AIOps de detección

- **Capa o Componente:** Detección y priorización de anomalías.
- **Stack Antiguo (Obsoleto):** LogBERT presentado como motor definitivo.
- **Stack Actualizado (Definitivo):** **Motor AIOps basado en un modelo existente/preentrenado; tecnología concreta PENDIENTE DE SELECCIÓN. LogBERT es la candidata principal, pero NO definitiva.**
- **Justificación del Cambio:** LogBERT debe contrastarse con alternativas más recientes del estado del arte y los benchmarkings antes de formalizar la selección.

## 19. Estado del drift del motor

- **Capa o Componente:** Gobierno de decisión del motor de anomalías.
- **Stack Antiguo (Obsoleto):** Selección implícita de LogBERT.
- **Stack Actualizado (Definitivo):** **`OPEN_DECISION`: mantener en diagramas el nombre lógico “Motor AIOps de detección de anomalías”; opcionalmente anotar “candidato actual: LogBERT”**.
- **Justificación del Cambio:** Evita que el pipeline DaC transforme una candidata técnica en una decisión formal aún no aprobada.

## 20. Responsabilidad del detector

- **Capa o Componente:** Separación entre detección y diagnóstico.
- **Stack Antiguo (Obsoleto):** Detector interpretado como componente capaz de producir directamente la causa raíz.
- **Stack Actualizado (Definitivo):** **El motor AIOps detecta, puntúa y prioriza señales anómalas; no confirma la causa del fallo**.
- **Justificación del Cambio:** La explicación diagnóstica pertenece al flujo de correlación + RAG + LLM + validación humana.

## 21. Correlación de evidencia

- **Capa o Componente:** Motor de correlación.
- **Stack Antiguo (Obsoleto):** Correlación principalmente temporal de logs/eventos.
- **Stack Actualizado (Definitivo):** **Correlación por workflow/run/job, etapa, servicio, timestamp, eventos, métricas disponibles e identificadores de trazabilidad**.
- **Justificación del Cambio:** Permite reconstruir el contexto del incidente de forma reproducible.

## 22. Identificador de trazabilidad técnica

- **Capa o Componente:** Correlación end-to-end.
- **Stack Antiguo (Obsoleto):** Identificadores no estandarizados entre componentes.
- **Stack Actualizado (Definitivo):** **`correlationId` como identificador técnico transversal**.
- **Justificación del Cambio:** El Charter lo incluye desde la fase de ingesta y permite seguir una misma evidencia entre servicios.

## 23. Identificador de incidente

- **Capa o Componente:** Modelo de dominio del diagnóstico.
- **Stack Antiguo (Obsoleto):** Uso informal de `IncidentId` como nombre técnico obligatorio.
- **Stack Actualizado (Definitivo):** **ID de incidente compartido por reporte, dashboard y evidencias; el nombre físico del campo puede definirse en implementación**.
- **Justificación del Cambio:** El Charter exige el identificador de incidente, pero no prescribe el nombre técnico `IncidentId`.

## 24. Persistencia estructurada

- **Capa o Componente:** Base de datos operacional.
- **Stack Antiguo (Obsoleto):** Repositorio genérico o tecnología no cerrada.
- **Stack Actualizado (Definitivo):** **PostgreSQL**.
- **Justificación del Cambio:** Centraliza incidentes, diagnósticos, revisiones, trazabilidad y metadatos usando una tecnología consolidada.

## 25. Recuperación vectorial

- **Capa o Componente:** Base de conocimiento RAG.
- **Stack Antiguo (Obsoleto):** Vector store genérico.
- **Stack Actualizado (Definitivo):** **PostgreSQL + pgvector**.
- **Justificación del Cambio:** Permite búsqueda semántica de conocimiento operacional sobre el mismo ecosistema de persistencia.

## 26. Separación de almacenamiento

- **Capa o Componente:** Persistencia de evidencias.
- **Stack Antiguo (Obsoleto):** Base relacional/vectorial utilizada implícitamente para todos los tipos de datos.
- **Stack Actualizado (Definitivo):** **PostgreSQL + pgvector para datos estructurados/conocimiento; almacenamiento de objetos separado para evidencias y artefactos pesados**.
- **Justificación del Cambio:** El Charter distingue persistencia estructurada y de objetos; evita forzar archivos/logs extensos dentro de la base relacional.

## 27. Base de conocimiento RAG

- **Capa o Componente:** Knowledge Retrieval.
- **Stack Antiguo (Obsoleto):** Recuperación limitada principalmente a incidentes históricos.
- **Stack Actualizado (Definitivo):** **Incidentes previamente revisados, documentación técnica y procedimientos de atención autorizados**.
- **Justificación del Cambio:** Aporta contexto verificable y permite conservar procedencia de las fuentes utilizadas en cada diagnóstico.

## 28. Separación de conocimiento y evaluación

- **Capa o Componente:** Validación experimental.
- **Stack Antiguo (Obsoleto):** Base de conocimiento y casos de evaluación sin frontera explícita.
- **Stack Actualizado (Definitivo):** **Dataset/casos de evaluación y sus soluciones de referencia separados del contenido usado por RAG**.
- **Justificación del Cambio:** Evita data leakage y contaminación de la evaluación con respuestas conocidas.

## 29. Modelo de lenguaje

- **Capa o Componente:** Generación diagnóstica.
- **Stack Antiguo (Obsoleto):** LLM descrito en algunos diseños como agente capaz de analizar directamente todo el log.
- **Stack Actualizado (Definitivo):** **LLM preentrenado integrado como servicio/API o contenedor, alimentado mediante RAG y contexto previamente procesado**.
- **Justificación del Cambio:** El proyecto integra modelos existentes y no desarrolla ni modifica pesos.

## 30. Entrada del LLM

- **Capa o Componente:** Contexto de inferencia.
- **Stack Antiguo (Obsoleto):** Logs crudos enviados directamente al LLM.
- **Stack Actualizado (Definitivo):** **Evidencia saneada y priorizada + contexto correlacionado + conocimiento recuperado mediante RAG**.
- **Justificación del Cambio:** Reduce exposición de datos, ruido, costo y riesgo de generar respuestas no sustentadas.

## 31. Resultado automático

- **Capa o Componente:** Salida del diagnóstico.
- **Stack Antiguo (Obsoleto):** “Causa raíz” generada automáticamente.
- **Stack Actualizado (Definitivo):** **Hipótesis de causa probable + evidencias + fuentes consultadas + recomendación + limitaciones/nivel de confianza cuando corresponda**.
- **Justificación del Cambio:** La salida de IA es apoyo diagnóstico y requiere evaluación; no constituye una causa raíz confirmada.

## 32. Causa raíz

- **Capa o Componente:** Terminología de diagnóstico.
- **Stack Antiguo (Obsoleto):** Uso intercambiable de causa raíz y causa probable.
- **Stack Actualizado (Definitivo):** **“Causa probable” para la hipótesis automática; “causa raíz” solo para una causa confirmada mediante evidencia y revisión técnica**.
- **Justificación del Cambio:** Evita atribuir certeza indebida a la inferencia automatizada.

## 33. Human-in-the-Loop

- **Capa o Componente:** Validación humana.
- **Stack Antiguo (Obsoleto):** Revisión humana limitada principalmente a recomendaciones críticas.
- **Stack Actualizado (Definitivo):** **Registro explícito de revisión humana para validar, corregir o rechazar diagnósticos/recomendaciones según el escenario**.
- **Justificación del Cambio:** Mejora gobernanza, trazabilidad y calidad de la evidencia de evaluación.

## 34. Actores de validación

- **Capa o Componente:** Usuarios del prototipo.
- **Stack Antiguo (Obsoleto):** Desarrolladores o DevOps tratados como único actor principal según el documento.
- **Stack Actualizado (Definitivo):** **Desarrolladores, DevOps/SRE, QA, líderes técnicos y Seguridad de la Información según el tipo de incidente y control**.
- **Justificación del Cambio:** El Charter reconoce múltiples perfiles beneficiarios y validadores del proceso.

## 35. Remediación automática

- **Capa o Componente:** Acciones posteriores al diagnóstico.
- **Stack Antiguo (Obsoleto):** Auto-remediación, rollback o cambios correctivos automáticos como parte potencial del MVP.
- **Stack Actualizado (Definitivo):** **Fuera del alcance del MVP ejecutar rollback productivo, cambios de infraestructura, cambios sensibles o despliegues correctivos de forma autónoma**.
- **Justificación del Cambio:** El Charter excluye expresamente la automatización crítica sin aprobación humana.

## 36. Observabilidad

- **Capa o Componente:** Fuentes de telemetría.
- **Stack Antiguo (Obsoleto):** Loki y Prometheus como componentes obligatorios.
- **Stack Actualizado (Definitivo):** **Plataformas de observabilidad como fuentes compatibles; producto específico no fijado por este registro**.
- **Justificación del Cambio:** El prototipo consume evidencia de observabilidad y no busca reemplazar la plataforma existente.

## 37. Dashboard

- **Capa o Componente:** Interfaz de consulta.
- **Stack Antiguo (Obsoleto):** Dashboard + Teams/Slack/comentarios en PR como canales principales equivalentes.
- **Stack Actualizado (Definitivo):** **Dashboard web como interfaz formal del prototipo**.
- **Justificación del Cambio:** El Charter lo define como entregable para consultar incidentes, diagnósticos, evidencias, recomendaciones, métricas y revisión humana.

## 38. Reporte de diagnóstico

- **Capa o Componente:** Evidencia exportable.
- **Stack Antiguo (Obsoleto):** Reporte genérico o diagnóstico visible únicamente en dashboard.
- **Stack Actualizado (Definitivo):** **Reporte descargable publicado como artifact de GitHub Actions y vinculado al workflow correspondiente**.
- **Justificación del Cambio:** El Charter lo establece expresamente como salida del prototipo y mejora trazabilidad del caso.

## 39. Canales corporativos de notificación

- **Capa o Componente:** Notificaciones.
- **Stack Antiguo (Obsoleto):** Microsoft Teams, Slack o correo integrados directamente al flujo principal.
- **Stack Actualizado (Definitivo):** **Integraciones opcionales y desacopladas; no forman parte del core obligatorio del MVP**.
- **Justificación del Cambio:** Requieren permisos corporativos independientes y no deben condicionar el diagnóstico.

## 40. Entrenamiento de modelos

- **Capa o Componente:** Ciclo de vida de IA.
- **Stack Antiguo (Obsoleto):** Posible entrenamiento/reentrenamiento propio del detector.
- **Stack Actualizado (Definitivo):** **No se entrenan modelos desde cero, no se ajustan hiperparámetros como aporte de investigación y no se modifican pesos**.
- **Justificación del Cambio:** El Project Charter lo excluye de manera explícita y el alcance es integracional.

## 41. Mantenimiento ante cambio operacional

- **Capa o Componente:** Mantenimiento de componentes AIOps.
- **Stack Antiguo (Obsoleto):** Reentrenamiento automático del detector como respuesta estándar al concept drift.
- **Stack Actualizado (Definitivo):** **Monitoreo de degradación, versionado y actualización/sustitución controlada del componente analítico**.
- **Justificación del Cambio:** Mantiene adaptabilidad sin transformar la tesis en investigación de entrenamiento de modelos.

## 42. KPI temporal

- **Capa o Componente:** Métrica principal de eficiencia diagnóstica.
- **Stack Antiguo (Obsoleto):** MTTR utilizado como indicador principal del prototipo.
- **Stack Actualizado (Definitivo):** **TMD — Tiempo Medio de Diagnóstico**.
- **Justificación del Cambio:** El prototipo mide hasta completar el diagnóstico; no controla necesariamente la reparación ni la recuperación del servicio.

## 43. Meta del TMD

- **Capa o Componente:** Criterio de aceptación.
- **Stack Antiguo (Obsoleto):** Metas inconsistentes del 30 % y 40 %, o reducción de MTTR.
- **Stack Actualizado (Definitivo):** **Reducción mínima del TMD del 30 % respecto al procedimiento manual**.
- **Justificación del Cambio:** Es la meta formal registrada en el Project Charter v1.3.

## 44. Calidad diagnóstica

- **Capa o Componente:** KPI de acierto.
- **Stack Antiguo (Obsoleto):** F1-score, Top-3 y otras métricas utilizadas indistintamente como criterio global.
- **Stack Actualizado (Definitivo):** **Acierto mínimo del 80 % en la identificación de la causa probable** como meta end-to-end.
- **Justificación del Cambio:** Evalúa directamente la utilidad del diagnóstico generado frente a la causa de referencia.

## 45. F1-score

- **Capa o Componente:** Métrica técnica del detector.
- **Stack Antiguo (Obsoleto):** F1 ≥ 0.85 como KPI contractual de éxito del prototipo.
- **Stack Actualizado (Definitivo):** **F1 puede emplearse como métrica auxiliar del motor de detección seleccionado, pero no sustituye el KPI de acierto diagnóstico**.
- **Justificación del Cambio:** Detectar anomalías correctamente no equivale a identificar correctamente la causa probable.

## 46. Evidencia antes de inferencia

- **Capa o Componente:** Principio de flujo diagnóstico.
- **Stack Antiguo (Obsoleto):** IA aplicada directamente sobre logs para producir una respuesta.
- **Stack Actualizado (Definitivo):** **Captura → protección/normalización → correlación/análisis → recuperación de conocimiento → inferencia LLM → revisión humana**.
- **Justificación del Cambio:** Mantiene el diagnóstico vinculado con evidencia verificable y reduce respuestas genéricas o no sustentadas.

## 47. Contrato canónico del core

- **Capa o Componente:** Flujo end-to-end del prototipo.
- **Stack Antiguo (Obsoleto):** `Logs → LogBERT → LLM/RCA`.
- **Stack Actualizado (Definitivo):** **`GitHub Actions → captura read-only → ingesta + protección de datos → Azure Service Bus → procesamiento NLP → Motor AIOps de detección (OPEN_DECISION) → correlación → PostgreSQL/pgvector + RAG → LLM preentrenado → hipótesis de causa probable + evidencia/recomendación → revisión humana → dashboard + artifact de GitHub Actions`**.
- **Justificación del Cambio:** Consolida las responsabilidades y decisiones vigentes sin convertir LogBERT en una selección definitiva.

## 48. Stack físico confirmado

- **Capa o Componente:** Baseline tecnológico para diagramas físicos.
- **Stack Antiguo (Obsoleto):** AWS/EKS, broker abierto, almacenamiento/vector store abiertos.
- **Stack Actualizado (Definitivo):** **GitHub Actions + Microsoft Azure + Azure Service Bus + PostgreSQL + pgvector + servicios de IA preentrenados/integrados**.
- **Justificación del Cambio:** Son las decisiones actualmente confirmadas para minimizar fricción operativa y de compliance en el prototipo.

## 49. Componentes que NO deben fijarse todavía en DaC

- **Capa o Componente:** Gobierno de arquitectura.
- **Stack Antiguo (Obsoleto):** Diagramas que presentan todas las tecnologías exploradas como seleccionadas.
- **Stack Actualizado (Definitivo):** **No fijar aún el detector de anomalías concreto, parser concreto, modelo de embeddings, orquestador de contenedores ni plataforma concreta de observabilidad salvo que exista una decisión posterior aprobada**.
- **Justificación del Cambio:** Estas decisiones permanecen abiertas o son intercambiables y no deben convertirse accidentalmente en arquitectura contractual.

## 50. Source of Truth de Diagramas-as-Code

- **Capa o Componente:** Gobierno documental.
- **Stack Antiguo (Obsoleto):** Diagramas históricos y documentos iniciales tratados implícitamente como arquitectura vigente.
- **Stack Actualizado (Definitivo):** **Project Charter v1.3 → decisiones arquitectónicas posteriores confirmadas → `tech_drift_resolutions.md` → documentos históricos**.
- **Justificación del Cambio:** Impide que un agente reconstruya tecnologías descartadas o convierta alternativas históricas en decisiones TO-BE.

---

## Baseline canónico para nuevos diagramas

```text
GitHub / GitHub Actions
        │
        │ read-only + mínimo privilegio
        ▼
Captura / Ingesta
        │
        ├── Validación
        ├── Normalización
        ├── Masking / anonimización
        ├── Filtrado de secretos
        ├── Minimización
        └── correlationId
        │
        ▼
Azure Service Bus
        │
        ▼
Procesamiento NLP de logs
        │
        ▼
Motor AIOps de detección de anomalías
[OPEN_DECISION — candidato actual: LogBERT]
        │
        ▼
Correlación de evidencias
        │
        ├──────────────► PostgreSQL
        │                ├── Incidentes
        │                ├── Diagnósticos
        │                ├── Revisiones
        │                └── Auditoría / metadatos
        │
        └──────────────► pgvector
                         └── Recuperación semántica RAG
                                │
                                ▼
                    LLM preentrenado + RAG
                                │
                                ▼
                    Hipótesis de causa probable
                    + evidencia
                    + fuentes
                    + recomendación
                    + limitaciones/confianza
                                │
                                ▼
                      Revisión humana
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             Dashboard web       Reporte descargable
                                  artifact GitHub Actions
```

### Fuentes opcionales de evidencia

```text
GitHub Actions ────────────────┐
Checkmarx (lower) ─────────────┤
Mend (lower) ──────────────────┼──► Ingesta autorizada
Wiz (lower) ───────────────────┤
Observabilidad compatible ─────┘
```

### Controles transversales

```text
Control de acceso
Read-only / mínimo privilegio
Privacidad por diseño
Enmascaramiento y anonimización
Auditoría técnica
Trazabilidad
Segregación de evidencias
Human-in-the-Loop
```

### Validación contractual

```text
TMD: reducción mínima ≥ 30 %
Acierto de causa probable: ≥ 80 %
Recomendaciones: pertinencia + evidencia + seguridad
Trazabilidad: evidencia suficiente para reconstruir el diagnóstico
```

---

## Decisiones abiertas controladas

```yaml
open_decisions:
  anomaly_detection_engine:
    status: OPEN_DECISION
    current_candidate: LogBERT
    rule: >
      No representar LogBERT como tecnología definitiva en diagramas
      arquitectónicos hasta concluir la revisión del estado del arte
      y benchmarking tecnológico.

  log_parser:
    status: IMPLEMENTATION_OPTION
    candidates:
      - Drain
      - Drain3

  embedding_model:
    status: IMPLEMENTATION_OPTION

  container_orchestrator:
    status: OPEN_OR_OPTIONAL

  observability_platform:
    status: ENVIRONMENT_DEPENDENT
```

## Decisiones tecnológicas cerradas

```yaml
decisions:
  source_control: GitHub
  ci_cd: GitHub Actions
  integration_access: read-only
  authorization_principle: least-privilege
  cloud: Microsoft Azure
  event_broker: Azure Service Bus
  structured_persistence: PostgreSQL
  vector_store: pgvector
  llm_strategy: pretrained-model-integrated-as-service
  rag: enabled
  dashboard: web
  workflow_report: GitHub Actions artifact
  autonomous_remediation: out-of-scope
  custom_model_training: out-of-scope

optional_sources:
  - Checkmarx
  - Mend
  - Wiz

rejected_as_components:
  - Privacy Gateway
