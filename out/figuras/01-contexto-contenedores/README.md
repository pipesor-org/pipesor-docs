# Contexto y contenedores (C4, niveles 1 y 2)

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Contexto del prototipo AIOps de diagnóstico de fallos de CI/CD

- **Archivo:** [`c4-contexto.png`](c4-contexto.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 15,7 cm) · texto mínimo 9,8 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: arquitectura del sistema (a confirmar por el equipo)
- **Título APA:** *Contexto del prototipo AIOps de diagnóstico de fallos de CI/CD*

**Nota APA.** Elaboración propia a partir del modelo de arquitectura del prototipo. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. Cada relación agrupa los flujos entre el sistema y un actor externo. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de arquitectura del prototipo. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. Cada relación agrupa los flujos entre el sistema y un actor externo. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N sitúa el prototipo frente a las personas y los sistemas con los que interactúa. Conviene observar que GitHub Actions es a la vez fuente de evidencia y consumidor del informe de diagnóstico, y que la telemetría de observabilidad sigue siendo una propuesta.

**Texto alternativo.** Diagrama de contexto: usuarios técnicos, GitHub, GitHub Actions, Azure OpenAI y observabilidad alrededor del prototipo.

**Simplificaciones respecto de la vista completa:**

- Cada flecha agrupa todas las relaciones del modelo entre el sistema y un elemento externo.
- Los contenedores internos se muestran en la figura de contenedores.

## Contenedores de captura, procesamiento y diagnóstico

- **Archivo:** [`c4-contenedores-procesamiento.png`](c4-contenedores-procesamiento.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 18,6 cm) · texto mínimo 9,2 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: arquitectura del sistema (a confirmar por el equipo)
- **Título APA:** *Contenedores de captura, procesamiento y diagnóstico*

**Nota APA.** Elaboración propia a partir del modelo de arquitectura (vista 2A) y del código de los servicios. Azul: contenedores del prototipo; gris: sistemas externos. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de arquitectura (vista 2A) y del código de los servicios. Azul: contenedores del prototipo; gris: sistemas externos. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra el recorrido de un fallo por los contenedores del prototipo, desde la captura hasta el diagnóstico. Conviene seguir el desacoplamiento mediante Service Bus y notar que la telemetría de observabilidad sigue siendo una propuesta.

**Texto alternativo.** Contenedores de procesamiento: ingesta, Service Bus, Pipeline, Log/Event, NLP, correlación, diagnóstico y RAG.

**Simplificaciones respecto de la vista completa:**

- La persistencia en PostgreSQL, la firma de tokens y los permisos y el resumen hacia Pipeline se muestran en la figura de consumo.
- Se omiten las comprobaciones de referencias entre Correlation, Pipeline, Log/Event e Ingesta.
- La consulta del informe desde GitHub Actions se explica con la secuencia de revisión.
- No se dibuja el marco del sistema: el color distingue los contenedores del prototipo (azul) de los sistemas externos (gris).

## Contenedores de consulta, revisión humana y gobierno

- **Archivo:** [`c4-contenedores-consumo.png`](c4-contenedores-consumo.png)
- **Orientación:** vertical · **ancho de inserción:** 12,6 cm (alto 19,0 cm) · texto mínimo 9,2 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: arquitectura del sistema (a confirmar por el equipo)
- **Título APA:** *Contenedores de consulta, revisión humana y gobierno*

**Nota APA.** Elaboración propia a partir del modelo de arquitectura (vista 2B) y del código de los servicios. Azul: prototipo; gris: externos. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. Persistencia y firma de tokens se agrupan por destino. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de arquitectura (vista 2B) y del código de los servicios. Azul: prototipo; gris: externos. Línea continua: implementado; ámbar discontinua: parcial; roja punteada: propuesto. Persistencia y firma de tokens se agrupan por destino. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra cómo las personas acceden al prototipo y cómo se gobiernan la identidad y los datos. El lector puede observar que el inicio de sesión pasa por la ingesta y que la consulta directa de evidencia desde el dashboard sigue propuesta.

**Texto alternativo.** Contenedores de consumo: usuarios, dashboard, ingesta, Pipeline, Log/Event, diagnóstico, PostgreSQL, Key Vault y GitHub.

**Simplificaciones respecto de la vista completa:**

- Las relaciones de persistencia y de firma con Key Vault se agrupan en una flecha por destino.
- La captura y el procesamiento se muestran en la figura de contenedores de procesamiento.
- No se dibuja el marco del sistema: el color distingue los contenedores del prototipo (azul) de los elementos externos (gris).
