# Registro de Cambios (Changelog)

## 2026-06-20

- **feat(validation):** Integrar validación de Producto y Venta con catálogo comercial opcional. `apps/ventas/catalogo_utils.py` consulta `apps.catalogo` solo si la app está registrada y luego usa fallback legacy.
- **feat(validation):** Actualizar `/api/ventas/precio-venta/` y `/api/ventas/validar-producto/` para retornar `precio`, `precio_plan`, `tipo_renta`, `catalogo` y `oferta_id` cuando aplica.
- **fix(catalogo):** Evitar error `RuntimeError` cuando `apps.catalogo` no está en `INSTALLED_APPS`.
- **fix(home):** Eliminar referencia rota a `{% url 'catalogo:index' %}` en `templates/home.html` para evitar `NoReverseMatch`.
- **fix(lead):** Cambiar `BaseLlamada.id_lead` de `UUIDField` a `HexUUIDField` para compatibilidad MySQL `char(32)`.
- **feat(migration):** Agregar y aplicar `apps/discador/migrations/0011_alter_basellamada_id_lead.py`.
- **fix(discador):** Corregir `prefetch_related('venta_set')` a `prefetch_related('ventas_asociadas')`.
- **fix(retail):** Agregar precios legacy `IPHONE_4S + ENTEL_75_CONTROL = 75` e `IPHONE_6_PLUS + ENTEL_75_CONTROL = 75`.
- **fix(form):** Corregir error Django 5.x `BlankChoiceIterator` en `apps/ventas/forms.py`: usar `list()` antes de manipular choices y manejar el caso donde el campo no tiene método `append`.
- **fix(csrf):** Corregir obtención de CSRF token en `agent_dashboard.html`: agregada función `getCsrfToken()` que obtiene el token del formulario de disponibilidad.
- **fix(modal-js):** Corregir obtención de CSRF token en submit del modal: ahora usa el token del propio formulario (`e.target.querySelector('[name=csrfmiddlewaretoken]')`).
- **fix(button):** Agregar IDs `btnGuardarVenta` y `btnGuardarVentaFull` a botones de guardar venta para habilitarlos vía JavaScript cuando cliente y producto están validados.
- **docs:** Actualizar `README.md`, `docs/documentacion.md` y `docs/HISTORIAL.md` con el estado actual de validaciones, catálogo opcional, UUID en hex y documentación ordenada.

## 2026-06-18
- **feat(validation):** Implementar validación de sección Producto y Venta en formulario de ventas. Se agregó endpoint `/api/ventas/validar-producto/`, botón `btnValidarProducto`, campo `producto_validado`, mensajes de validación, bloqueo de Guardar para formulario completo y modal, y tests de API.
- **fix(js):** Definir `resetProductoValidacion()` y `actualizarSubmitVenta()` para evitar rotura al cambiar producto y coordinar validación de Cliente + Producto.
- **fix(modal):** El modal de venta ahora bloquea guardado si Producto no fue validado.
- **docs:** Actualizar `docs/documentacion.md`, `docs/HISTORIAL.md`, `README.md` y `.kilo/plans/validacion-producto-venta.md` con el flujo de validación de Producto.

## 2026-06-11

- **feat(validation):** Implementar validación de sección cliente en formulario de ventas. El botón "Registrar Cliente" aparece cuando el cliente no existe, crea el cliente vía API y habilita el botón "Guardar Venta".
- **feat(forms):** Simplificar validación en `VentaForm.clean()`; ahora solo verifica que el cliente exista en BD porque el cliente debe haber sido registrado previamente vía el botón dedicado.
- **feat(api):** Agregar endpoint `/ventas/registrar-cliente/<uuid:id_lead>/` para crear clientes sin crear venta.
- **feat(js):** Actualizar `static/js/venta-form.js` con funciones `marcarSeccionValida()`, `registrarCliente()` y `keypress` handler para prevenir submit al presionar Enter.
- **fix(ui):** Prevenir submit al presionar Enter en campo documento; el evento `keypress` llama a `buscarCliente()`.
- **fix(ui):** Corregir error `@import` en CSS moviendo la regla de Google Fonts antes de las declaraciones de estilo en `static/css/form-data.css`. El `@import` debe aparecer al inicio del archivo, después de comentarios.
- **feat(ui):** Agregar `favicon.ico` convertido desde icono de formulario en `static/img/`. El archivo `icons8-form-96.png` se convirtió a `favicon.ico` y se enlazó en `templates/base.html` con `<link rel="icon">` y `<link rel="shortcut icon">`.
- **config:** Agregar `192.168.18.7` a `ALLOWED_HOSTS` en `.env` para permitir acceso desde esa IP en desarrollo.

## 2026-06-10

- **fix(ui):** Mostrar botón "Recargar Lead" en la sección *Cliente* del formulario de ventas (`templates/ventas/_venta_form_fields.html`). El botón estaba oculto con `style="display: none;"` luego de una refactorización.
- **fix(ui):** Convertir campos de la sección *Lead* del formulario de ventas a etiquetas en vez de inputs readonly, y añadir campo **Observaciones** (`templates/ventas/_venta_form_fields.html`). Actualizado `static/js/venta-form.js` para usar `setText()` y `textContent` en las funciones `recargarLead()` y botón "Teléfono a Portar".

## 2026-06-08

- **feat(postventa):** Separar apps `postventa`, `despacho` y `courier`.
- **feat(postventa):** Implementar modelos `SeguimientoBO`, `EstadoDespacho`, `EstadoCourier`, `Proveedor`, `ProveedorCourier` e `HistorialEstado`.
- **feat(postventa):** Implementar señales para registrar cambios en `HistorialEstado`.
- **feat(dashboard):** Implementar dashboard de conversión por base de procedencia.
- **feat(api):** Implementar API de trazabilidad `/api/venta/<int:pk>/trazabilidad/`.

## 2026-06-07

- **feat(trazabilidad):** Implementar trazabilidad Lead → Venta.
- **feat(models):** Agregar FK bidireccional entre `BaseLlamada` y `Venta`.
- **feat(postventa):** Implementar flujo BO, despacho y courier sobre la misma entidad `Venta`.

## 2026-06-06

- **feat(retail):** Refactor de reglas de negocio retail.
- **feat(models):** Actualizar `Venta` con producto, origen, operador, teléfono a portar, modelo, plan, precios y tipo de renta.
- **feat(api):** Agregar endpoint `/api/ventas/precio-venta/`.

## 2026-06-05

- **feat(ventas):** Registro de ventas con cliente, items, ubigeo, recibo electrónico y datos de portabilidad.
- **feat(ventas):** Implementar flujo de creación de ventas desde discador.
