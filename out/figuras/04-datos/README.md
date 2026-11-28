# Modelo de datos por esquema

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Modelo de datos del esquema ops (Pipeline)

- **Archivo:** [`datos-operacion.png`](datos-operacion.png)
- **Orientación:** vertical · **ancho de inserción:** 14,7 cm (alto 12,9 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria · Diseño de la solución: modelo de datos (a confirmar por el equipo)
- **Título APA:** *Modelo de datos del esquema ops (Pipeline)*

**Nota APA.** Elaboración propia a partir del modelo de datos y de las migraciones del servicio Pipeline. Todas las tablas están implementadas. Las flechas son claves foráneas; «ref.» marca referencias lógicas sin clave foránea. Se muestran hasta cinco columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de datos y de las migraciones del servicio Pipeline. Todas las tablas están implementadas. Las flechas son claves foráneas; «ref.» marca referencias lógicas sin clave foránea. Se muestran hasta cinco columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N presenta las tablas del servicio Pipeline. Conviene observar que cada incidente se vincula con sus ejecuciones mediante incident_runs y que incident_diagnoses es una proyección de lectura del diagnóstico.

**Texto alternativo.** Esquema ops con repositorios, pipelines, ejecuciones, etapas, incidentes, recibos, permisos y diagnósticos de incidentes.

**Simplificaciones respecto de la vista completa:**

- Se muestran sin tipos la clave primaria, las claves foráneas y hasta cinco columnas por tabla.

## Modelo de datos de los esquemas evidence y audit

- **Archivo:** [`datos-evidencia-auditoria.png`](datos-evidencia-auditoria.png)
- **Orientación:** vertical · **ancho de inserción:** 12,6 cm (alto 14,5 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria · Diseño de la solución: modelo de datos (a confirmar por el equipo)
- **Título APA:** *Modelo de datos de los esquemas evidence y audit*

**Nota APA.** Elaboración propia a partir del modelo de datos y de las migraciones de Log/Event, Correlation y Pipeline. Todas las tablas están implementadas. Las flechas son claves foráneas; «ref.» marca referencias lógicas. Se muestran hasta seis columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de datos y de las migraciones de Log/Event, Correlation y Pipeline. Todas las tablas están implementadas. Las flechas son claves foráneas; «ref.» marca referencias lógicas. Se muestran hasta seis columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N reúne la evidencia registrada por Log/Event, los grupos y contextos de correlación y la auditoría transversal. El lector puede notar que el contexto correlacionado solo referencia la evidencia por identificador, sin claves foráneas entre servicios.

**Texto alternativo.** Esquemas evidence y audit: ítems de evidencia, grupos, contextos y recibos de correlación, y eventos de auditoría.

**Simplificaciones respecto de la vista completa:**

- Se muestran sin tipos la clave primaria, las claves foráneas y hasta seis columnas por tabla.

## Modelo de datos del esquema diagnosis

- **Archivo:** [`datos-diagnostico.png`](datos-diagnostico.png)
- **Orientación:** vertical · **ancho de inserción:** 14,9 cm (alto 13,5 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: modelo de datos (a confirmar por el equipo)
- **Título APA:** *Modelo de datos del esquema diagnosis*

**Nota APA.** Elaboración propia a partir del modelo de datos y de las migraciones del servicio de diagnóstico. Borde continuo: implementada; ámbar discontinuo: parcial; rojo punteado: propuesta; columnas en rojo: sin implementar. Se muestran hasta cinco columnas por tabla. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de datos y de las migraciones del servicio de diagnóstico. Borde continuo: implementada; ámbar discontinuo: parcial; rojo punteado: propuesta; columnas en rojo: sin implementar. Se muestran hasta cinco columnas por tabla. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra el esquema del servicio de diagnóstico y lo que aún no se ha implementado. Destaca que tres tablas del diseño no existen y que varias columnas de diagnoses se guardan dentro de la instantánea output.

**Texto alternativo.** Esquema diagnosis con recibos, diagnósticos, revisiones, trabajos y outbox; tres tablas y seis columnas solo propuestas.

**Simplificaciones respecto de la vista completa:**

- Se muestran sin tipos la clave primaria, las claves foráneas y hasta cinco columnas por tabla.

## Modelo de datos del esquema knowledge (RAG)

- **Archivo:** [`datos-conocimiento.png`](datos-conocimiento.png)
- **Orientación:** vertical · **ancho de inserción:** 10,5 cm (alto 5,5 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria · Diseño de la solución: modelo de datos (a confirmar por el equipo)
- **Título APA:** *Modelo de datos del esquema knowledge (RAG)*

**Nota APA.** Elaboración propia a partir del modelo de datos y de las migraciones del servicio RAG. Ambas tablas están implementadas. La flecha es una clave foránea. Se muestran hasta ocho columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de datos y de las migraciones del servicio RAG. Ambas tablas están implementadas. La flecha es una clave foránea. Se muestran hasta ocho columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N presenta el almacén de conocimiento del RAG. Cada documento autorizado se divide en fragmentos con su embedding, y el ámbito del documento limita qué conocimiento puede recuperar cada consulta.

**Texto alternativo.** Esquema knowledge: documentos de conocimiento y sus fragmentos con embedding vectorial.

**Simplificaciones respecto de la vista completa:**

- Se muestran sin tipos la clave primaria, las claves foráneas y hasta ocho columnas por tabla.

## Modelo de datos del esquema ingestion

- **Archivo:** [`datos-ingesta.png`](datos-ingesta.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 15,8 cm) · texto mínimo 9,3 pt
- **Destino:** Memoria · Implementación: servicio de ingesta (a confirmar por el equipo)
- **Título APA:** *Modelo de datos del esquema ingestion*

**Nota APA.** Elaboración propia a partir del modelo de datos y de las migraciones del servicio de ingesta. Todas las tablas están implementadas. Las flechas son claves foráneas. Por espacio se muestran hasta tres columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de datos y de las migraciones del servicio de ingesta. Todas las tablas están implementadas. Las flechas son claves foráneas. Por espacio se muestran hasta tres columnas por tabla; el resto está en el diccionario de datos del repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N agrupa las tablas del servicio de ingesta en dos áreas: el vínculo con GitHub y el inicio de sesión, y la captura de eventos con su publicación. El lector puede seguir cómo un recibo de captura produce una observación y sus salidas publicadas.

**Texto alternativo.** Esquema ingestion: conexiones de GitHub, inicio de sesión, consentimientos, admisiones, recibos, observaciones y salidas.

**Simplificaciones respecto de la vista completa:**

- Por espacio, se muestran sin tipos la clave primaria, las claves foráneas y hasta tres columnas por tabla.
