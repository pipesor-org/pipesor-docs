# Clases de dominio por bounded context

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Agregado Incident del contexto de operación (Pipeline)

- **Archivo:** [`clases-operacion.png`](clases-operacion.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 17,1 cm) · texto mínimo 9,4 pt
- **Destino:** Memoria · Diseño de la solución: modelo de dominio (a confirmar por el equipo)
- **Título APA:** *Agregado Incident del contexto de operación (Pipeline)*

**Nota APA.** Elaboración propia a partir del código del servicio Pipeline. Todas las clases están implementadas. Se muestran solo el agregado, sus entidades y value objects clave, con atributos y reglas seleccionados. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del código del servicio Pipeline. Todas las clases están implementadas. Se muestran solo el agregado, sus entidades y value objects clave, con atributos y reglas seleccionados. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N presenta el agregado Incident, que concentra las reglas del ciclo de vida de un incidente. El lector puede observar que el origen es siempre una ejecución fallida y que las transiciones de estado se validan dentro del agregado.

**Texto alternativo.** Clases del agregado Incident: detalles, ciclo de vida, ejecución de origen, verificación, estado, severidad y repositorio.

**Simplificaciones respecto de la vista completa:**

- Se omiten puertos, adaptadores y filas JPA (IncidentStore, JpaIncidentStore e IncidentJpaEntity).
- Se muestran hasta seis atributos por clase y solo los métodos que expresan reglas de negocio.

## Agregados GitHubConnection y CaptureReceipt del contexto de ingesta

- **Archivo:** [`clases-ingesta.png`](clases-ingesta.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 16,5 cm) · texto mínimo 9,0 pt
- **Destino:** Memoria · Diseño de la solución: modelo de dominio (a confirmar por el equipo)
- **Título APA:** *Agregados GitHubConnection y CaptureReceipt del contexto de ingesta*

**Nota APA.** Elaboración propia a partir del código del servicio de ingesta. Todas las clases están implementadas. Se muestran los dos agregados con sus entidades y value objects clave; se omiten operaciones de credenciales, enumeraciones y persistencia. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del código del servicio de ingesta. Todas las clases están implementadas. Se muestran los dos agregados con sus entidades y value objects clave; se omiten operaciones de credenciales, enumeraciones y persistencia. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N reúne los dos agregados del servicio de ingesta. GitHubConnection gobierna el vínculo del usuario con GitHub por generaciones de credenciales, y CaptureReceipt garantiza que cada evento capturado deje un recibo durable con su ámbito.

**Texto alternativo.** Clases de ingesta: GitHubConnection con raíz, generaciones e intentos; CaptureReceipt con ámbito y observación del workflow.

**Simplificaciones respecto de la vista completa:**

- Se omiten las operaciones de credenciales (ConnectionRecords.Operation), los value objects de identidad y secreto y las demás enumeraciones.
- WorkflowObservation se muestra sin sus records anidados (contexto, ejecución, etapas, fallo y evidencia).
- Se omiten puertos, adaptadores y filas JPA.

## Agregado CorrelationGroup del contexto de correlación

- **Archivo:** [`clases-correlacion.png`](clases-correlacion.png)
- **Orientación:** vertical · **ancho de inserción:** 14,0 cm (alto 10,5 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria · Diseño de la solución: modelo de dominio (a confirmar por el equipo)
- **Título APA:** *Agregado CorrelationGroup del contexto de correlación*

**Nota APA.** Elaboración propia a partir del código del servicio de correlación. Todas las clases están implementadas. Se muestran el agregado, su contexto y los value objects de cada contribución; se omiten el almacén durable y la entidad de persistencia. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del código del servicio de correlación. Todas las clases están implementadas. Se muestran el agregado, su contexto y los value objects de cada contribución; se omiten el almacén durable y la entidad de persistencia. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra cómo se agrupa la evidencia de una ejecución fallida en un CorrelationGroup. Cada contribución aporta una señal y un ámbito, y la revisión del grupo crece con cada evidencia incluida.

**Texto alternativo.** Clases de correlación: CorrelationGroup con su contexto y contribuciones con señal de evidencia y ámbito.

**Simplificaciones respecto de la vista completa:**

- Se omiten DurableCorrelationStore, CorrelatedContextEntity y SourceLocator.

## Agregados propuestos del diagnóstico frente a los registros implementados

- **Archivo:** [`clases-diagnostico.png`](clases-diagnostico.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 14,9 cm) · texto mínimo 9,6 pt
- **Destino:** Memoria y Capstone · Diseño de la solución: modelo de dominio (a confirmar por el equipo)
- **Título APA:** *Agregados propuestos del diagnóstico frente a los registros implementados*

**Nota APA.** Elaboración propia a partir del diseño de clases propuesto y del código del servicio de diagnóstico. Borde continuo: implementado; ámbar discontinuo: parcial; rojo punteado: propuesto. La línea discontinua con triángulo indica qué registro realiza cada agregado propuesto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir del diseño de clases propuesto y del código del servicio de diagnóstico. Borde continuo: implementado; ámbar discontinuo: parcial; rojo punteado: propuesto. La línea discontinua con triángulo indica qué registro realiza cada agregado propuesto. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N contrasta los agregados Diagnosis y HumanReview del diseño con los registros que implementa el código. El lector debe observar que el diagnóstico se guarda como una instantánea JSON y que la recomendación y la causa probable no existen como clases propias.

**Texto alternativo.** Clases propuestas Diagnosis, Recommendation, ProbableCause y HumanReview frente a los registros implementados.

**Simplificaciones respecto de la vista completa:**

- Se omiten los records de recibos, trabajos de diagnóstico y outbox, y los controladores y servicios de aplicación.
- Se muestran hasta seis atributos por clase.
