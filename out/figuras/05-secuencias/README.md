# Secuencias

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Captura de un fallo de GitHub Actions hasta la entrega del contexto

- **Archivo:** [`secuencia-captura-fallo.png`](secuencia-captura-fallo.png)
- **Orientación:** vertical · **ancho de inserción:** 15,4 cm (alto 19,0 cm) · texto mínimo 9,4 pt
- **Destino:** Memoria y Capstone · Implementación: flujo de diagnóstico de un fallo (a confirmar por el equipo)
- **Título APA:** *Captura de un fallo de GitHub Actions hasta la entrega del contexto*

**Nota APA.** Elaboración propia a partir del modelo de secuencias y del código. Todo está implementado; flechas discontinuas: respuestas; de punta abierta: mensajes asíncronos. Service Bus y NLP se indican en el mensaje; Log/Event, los reintentos y la idempotencia se omiten. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de secuencias y del código. Todo está implementado; flechas discontinuas: respuestas; de punta abierta: mensajes asíncronos. Service Bus y NLP se indican en el mensaje; Log/Event, los reintentos y la idempotencia se omiten. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N recorre la captura de un fallo desde el webhook firmado hasta la entrega del contexto correlacionado. Conviene observar que GitHub recibe la respuesta en cuanto existe un recibo durable y que el resto del proceso continúa de forma asíncrona.

**Texto alternativo.** Secuencia de captura: webhook, recibo, lectura de logs, Service Bus, NLP, correlación y entrega al diagnóstico.

**Simplificaciones respecto de la vista completa:**

- Log/Event, que registra la evidencia en paralelo, no se dibuja.
- Service Bus y NLP no tienen línea de vida: los mensajes asíncronos indican por dónde pasan.
- Si la ejecución aún no está registrada, Correlation responde 503 y NLP reintenta; se explica en el texto.
- Los reintentos por lease, la deduplicación por digest y los mensajes a dead-letter se explican en el texto.

## Diagnóstico asistido con recuperación RAG e inferencia en Azure OpenAI

- **Archivo:** [`secuencia-diagnostico.png`](secuencia-diagnostico.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 19,0 cm) · texto mínimo 9,8 pt
- **Destino:** Memoria y Capstone · Implementación: flujo de diagnóstico de un fallo (a confirmar por el equipo)
- **Título APA:** *Diagnóstico asistido con recuperación RAG e inferencia en Azure OpenAI*

**Nota APA.** Elaboración propia a partir del modelo de secuencias y del código de los servicios. Flechas negras: implementado; ámbar: parcial, es decir, implementado de otra forma que el diseño; discontinuas: respuestas. Los reintentos con espera exponencial se explican en el texto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de secuencias y del código de los servicios. Flechas negras: implementado; ámbar: parcial, es decir, implementado de otra forma que el diseño; discontinuas: respuestas. Los reintentos con espera exponencial se explican en el texto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra cómo el servicio de diagnóstico procesa un contexto encolado. Lo importante es que la consulta al RAG y la inferencia ocurren en un worker asíncrono, y que el resumen llega a Pipeline mediante un outbox y no en la misma llamada.

**Texto alternativo.** Secuencia de diagnóstico: trabajo encolado, consulta RAG, inferencia, persistencia y resumen enviado a Pipeline.

**Simplificaciones respecto de la vista completa:**

- El worker y el outbox se representan dentro del servicio de diagnóstico.
- La validación de las citas de evidencia antes de guardar se explica en el texto.
- Los reintentos (hasta ocho, con espera exponencial) y el estado FAILED se explican en el texto y no se dibujan.

## Revisión humana del diagnóstico desde el dashboard

- **Archivo:** [`secuencia-revision-humana.png`](secuencia-revision-humana.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 17,6 cm) · texto mínimo 9,6 pt
- **Destino:** Memoria y Capstone · Implementación: flujo de diagnóstico de un fallo (a confirmar por el equipo)
- **Título APA:** *Revisión humana del diagnóstico desde el dashboard*

**Nota APA.** Elaboración propia a partir del modelo de secuencias y del código de los servicios. Todo está implementado; las flechas discontinuas son respuestas. Se omiten la reproyección del resumen en Pipeline y la consulta del informe desde GitHub Actions. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de secuencias y del código de los servicios. Todo está implementado; las flechas discontinuas son respuestas. Se omiten la reproyección del resumen en Pipeline y la consulta del informe desde GitHub Actions. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra cómo una persona revisa el diagnóstico desde el dashboard. Conviene observar que cada lectura comprueba los permisos en Pipeline y que una revisión concurrente se rechaza con un conflicto en lugar de sobrescribirse.

**Texto alternativo.** Secuencia de revisión humana: dashboard, permisos en Pipeline y registro de la revisión con control de conflictos.

**Simplificaciones respecto de la vista completa:**

- La consulta del informe desde GitHub Actions con token OIDC, su sondeo y la subida del artifact se explican en el texto.
- La reproyección del resumen en Pipeline tras la revisión se explica en el texto.

## Inicio de sesión con GitHub mediante OAuth y PKCE

- **Archivo:** [`secuencia-inicio-sesion.png`](secuencia-inicio-sesion.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 18,2 cm) · texto mínimo 9,7 pt
- **Destino:** Memoria y Capstone · Implementación: seguridad e identidad (a confirmar por el equipo)
- **Título APA:** *Inicio de sesión con GitHub mediante OAuth y PKCE*

**Nota APA.** Elaboración propia a partir del modelo de secuencias y del código de ingesta y del dashboard. Flechas negras: implementado; discontinuas: respuestas o redirecciones. Se omiten la custodia del verifier, el registro del intento y el cierre de sesión. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del modelo de secuencias y del código de ingesta y del dashboard. Flechas negras: implementado; discontinuas: respuestas o redirecciones. Se omiten la custodia del verifier, el registro del intento y el cierre de sesión. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N describe el inicio de sesión con GitHub. El lector debe observar que el consentimiento se exige antes de redirigir a GitHub, que el código se canjea con el verifier PKCE y que el dashboard recibe un token de sesión firmado con una clave de Key Vault.

**Texto alternativo.** Secuencia de inicio de sesión: consentimiento, autorización en GitHub con PKCE, canje del código y token de sesión firmado.

**Simplificaciones respecto de la vista completa:**

- Se omiten la custodia del verifier en Key Vault, los registros de intento en PostgreSQL y el cierre de sesión.
- Las redirecciones del navegador se dibujan como mensajes entre el dashboard, la ingesta y GitHub.
- El uso posterior del token contra Pipeline y Diagnóstico, validado con JWKS, se explica en el texto.
- La casilla de consentimiento del dashboard se representa por el parámetro consent_version.
