# Componentes (C4, nivel 3)

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Componentes del servicio de diagnóstico y recomendación

- **Archivo:** [`componentes-diagnostico.png`](componentes-diagnostico.png)
- **Orientación:** vertical · **ancho de inserción:** 15,8 cm (alto 16,9 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: servicio de diagnóstico (a confirmar por el equipo)
- **Título APA:** *Componentes del servicio de diagnóstico y recomendación*

**Nota APA.** Elaboración propia a partir del modelo de arquitectura (ADR-017) y del código del servicio. Línea continua: implementado; ámbar discontinua: parcial, es decir, implementado en parte o de otra forma. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de arquitectura (ADR-017) y del código del servicio. Línea continua: implementado; ámbar discontinua: parcial, es decir, implementado en parte o de otra forma. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N descompone el servicio de diagnóstico en sus cuatro componentes de diseño. Lo relevante es que la orquestación se ejecuta de forma asíncrona y que el compositor de salida no existe como pieza separada, por lo que esas relaciones aparecen como parciales.

**Texto alternativo.** Componentes del diagnóstico: API, orquestador, compositor de salida y revisión humana, con RAG, Azure OpenAI y PostgreSQL.

**Simplificaciones respecto de la vista completa:**

- Se muestran los cuatro componentes del diseño; el intake de recibos, la cola de diagnóstico y el outbox del código se explican en la figura de secuencia de diagnóstico.

## Componentes del servicio de ingesta y normalización

- **Archivo:** [`componentes-ingesta.png`](componentes-ingesta.png)
- **Orientación:** vertical · **ancho de inserción:** 15,5 cm (alto 19,0 cm) · texto mínimo 9,5 pt
- **Destino:** Memoria · Implementación: servicio de ingesta (a confirmar por el equipo)
- **Título APA:** *Componentes del servicio de ingesta y normalización*

**Nota APA.** Elaboración propia a partir del código del servicio de ingesta; los componentes se infirieron del código y el responsable autorizó modelarlos. Todos están implementados. Se omiten la persistencia y el uso de Key Vault. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del código del servicio de ingesta; los componentes se infirieron del código y el responsable autorizó modelarlos. Todos están implementados. Se omiten la persistencia y el uso de Key Vault. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra los siete componentes del servicio de ingesta. La captura sigue un recorrido de webhook, recibo durable, preparación, normalización y publicación, mientras que el inicio de sesión y el conector de GitHub forman una vía independiente.

**Texto alternativo.** Componentes de ingesta: webhook, captura, preparación, normalización, publicación, inicio de sesión y conector de GitHub.

**Simplificaciones respecto de la vista completa:**

- Se omiten PostgreSQL y Key Vault: la persistencia del registro de captura, de los inicios de sesión y del conector, y la firma y custodia de credenciales.
- Se omite el análisis bajo demanda que pide el dashboard.
- Se omiten las llamadas de Pipeline a la autoridad de captura y al conector.
