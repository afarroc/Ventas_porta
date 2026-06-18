# Registro de Cambios (Changelog)
## 2026-06-18
- **feat(validation):** Implementar validación de sección Producto y Venta en formulario de ventas. Se agregó endpoint `/api/ventas/validar-producto/`, botón `btnValidarProducto`, campo `producto_validado`, mensajes de validación, bloqueo de Guardar para formulario completo y modal, y tests de API.
- **fix(js):** Definir `resetProductoValidacion()` y `actualizarSubmitVenta()` para evitar rotura al cambiar producto y coordinar validación de Cliente + Producto.
- **fix(modal):** El modal de venta ahora bloquea guardado si Producto no fue validado.
- **docs:** Actualizar `docs/documentacion.md`, `docs/HISTORIAL.md`, `README.md` y `.kilo/plans/validacion-producto-venta.md` con el flujo de validación de Producto.

## 2026-06-11
- **feat(validation):** Implementar validación de sección cliente en formulario de ventas. El botón "Registrar Cliente" aparece cuando el cliente no existe, crea el cliente vía API y habilita el botón "Guardar Venta".
- **feat(forms):** Simplificar validación en VentaForm.clean() - ahora solo verifica que el cliente exista en BD (el cliente debe haber sido registrado previamente vía el botón dedicado).
- **feat(api):** Agregar endpoint `/ventas/registrar-cliente/<uuid:id_lead>/` para crear clientes sin crear venta.
- **feat(js):** Actualizar venta-form.js con functiones `marcarSeccionValida()`, `registrarCliente()` y `keypress` handler para prevenir submit al presionar Enter.
- **fix(ui):** Prevenir submit al presionar Enter en campo documento (keypress event llama a buscarCliente).
- **fix(ui):** Corregir error `@import` en CSS moviendo la regla de Google Fonts antes de las declaraciones de estilo en `static/css/form-data.css`. El `@import` debe aparecer al inicio del archivo (después de comentarios).
- **feat(ui):** Agregar favicon.ico convertido desde icono de formulario en `static/img/`. El archivo `icons8-form-96.png` (96x96) se convirtió a `favicon.ico` y se enlazó en `templates/base.html` con `<link rel="icon">` y `<link rel="shortcut icon">`.
- **config:** Agregar `192.168.18.7` a `ALLOWED_HOSTS` en `.env` para permitir acceso desde esa IP en desarrollo.

## 2026-06-10
- **fix(ui):** Mostrar botón "Recargar Lead" en la sección *Cliente* del formulario de ventas (`templates/ventas/_venta_form_fields.html`). El botón estaba oculto con `style="display: none;"` luego de una refactorización.
- **fix(ui):** Convertir campos de la sección *Lead* del formulario de ventas a etiquetas (labels) en vez de inputs readonly, y añadir campo **Observaciones** (`templates/ventas/_venta_form_fields.html`). Actualizado `static/js/venta-form.js` para usar `setText()` y `textContent` en las funciones `recargarLead()` y botón "Teléfono a Portar".
