# Registro de Cambios (Changelog)
## 2026-06-10
- **fix(ui):** Mostrar botón "Recargar Lead" en la sección *Cliente* del formulario de ventas (`templates/ventas/_venta_form_fields.html`). El botón estaba oculto con `style="display: none;"` luego de una refactorización.
La lógica JS `recargarLead()` en `static/js/venta-form.js` y el endpoint en `apps/ventas/views.py` ya existían; solo se restauró la visibilidad para permitir recargar datos del lead cuando los campos cliente fueron borrados o limpiados.
- **fix(ui):** Convertir campos de la sección *Lead* del formulario de ventas a etiquetas (labels) en vez de inputs readonly, y añadir campo **Observaciones** (`templates/ventas/_venta_form_fields.html`). Actualizado `static/js/venta-form.js` para usar `setText()` y `textContent` en las funciones `recargarLead()` y botón "Teléfono a Portar".
