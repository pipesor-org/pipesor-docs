# Despliegue y estrategia de ramas

Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a 300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.

## Despliegue del entorno dev en Azure

- **Archivo:** [`despliegue-dev.png`](despliegue-dev.png)
- **Orientación:** vertical · **ancho de inserción:** 15,9 cm (alto 14,4 cm) · texto mínimo 10,0 pt
- **Destino:** Memoria y Capstone · Implementación: despliegue (a confirmar por el equipo)
- **Título APA:** *Despliegue del entorno dev en Azure*

**Nota APA.** Elaboración propia a partir de la infraestructura como código y de una observación de solo lectura del 27/11/2026, con PostgreSQL detenido. Todos los elementos dibujados están implementados. Las aplicaciones se agrupan por tipo de ingress. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir de la infraestructura como código y de una observación de solo lectura del 27/11/2026, con PostgreSQL detenido. Todos los elementos dibujados están implementados. Las aplicaciones se agrupan por tipo de ingress. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N muestra cómo se despliega el prototipo en el entorno dev. Conviene observar que solo cuatro aplicaciones exponen ingress externo y que las imágenes se descargan desde GHCR por digest.

**Texto alternativo.** Despliegue dev: Container Apps agrupadas por ingress, jobs, PostgreSQL, Service Bus, Key Vault, Foundry y GHCR.

**Simplificaciones respecto de la vista completa:**

- Los dos Key Vault y los tres jobs se agrupan en un nodo cada uno; las nueve identidades administradas se omiten.
- Las ocho aplicaciones se agrupan en dos nodos según su ingress: externo (dashboard, ingestion, pipeline, recommendation) e interno.
- Todos los recursos de Azure están en el grupo rg-pipesor-dev (westus3); su marco se omite.
- La GitHub App (OAuth con PKCE y webhook) se muestra en las figuras de contexto, contenedores e inicio de sesión.
- Se omiten la red virtual, las subredes, Log Analytics (logs de plataforma) y Application Insights, que está desactivado.

## Estrategia de ramas, entrega de imágenes y entornos

- **Archivo:** [`despliegue-entornos-ramas.png`](despliegue-entornos-ramas.png)
- **Orientación:** vertical · **ancho de inserción:** 15,3 cm (alto 19,0 cm) · texto mínimo 9,6 pt
- **Destino:** Memoria y Capstone · Implementación: integración y entrega continua (a confirmar por el equipo)
- **Título APA:** *Estrategia de ramas, entrega de imágenes y entornos*

**Nota APA.** Elaboración propia a partir de los workflows de CI, de la infraestructura como código y de las reglas de los repositorios. Borde continuo: implementado; rojo punteado: propuesto o sin definir. qa, preprod y prod solo tienen fundaciones. El detalle completo está en el repositorio pipesor-docs (Anexo C).

*Texto para la nota en Word:* *Nota.* Elaboración propia a partir de los workflows de CI, de la infraestructura como código y de las reglas de los repositorios. Borde continuo: implementado; rojo punteado: propuesto o sin definir. qa, preprod y prod solo tienen fundaciones. El detalle completo está en el repositorio pipesor-docs (Anexo C).

**Párrafo de llamada.** La Figura N resume cómo un cambio llega al entorno dev con una estrategia basada en main. El lector puede distinguir los pasos definidos de la promoción a qa, preprod y prod, que sigue propuesta, y de los puntos todavía sin definir.

**Texto alternativo.** Flujo de entrega: rama, PR, squash a main, CI, GHCR, PR de imágenes, plan y apply a dev; qa, preprod y prod propuestos.

**Simplificaciones respecto de la vista completa:**

- Los seis puntos sin definir se agrupan en un nodo.
- El squash a main y el apply se fusionan con el paso anterior.
- La promoción entre entornos reutiliza el mismo digest de imagen; la etiqueta lo abrevia como «digest».
- El rollback, que restaura la entrada anterior de images.json, se explica en el texto.
