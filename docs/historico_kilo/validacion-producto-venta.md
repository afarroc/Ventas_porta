# Plan de Acción: Botón de Validación de Producto en Formulario de Ventas

## Objetivo

Agregar en la sección **Producto y Venta** del formulario de ventas un botón de validación equivalente al existente en la sección **Cliente**, manteniendo la validación backend como fuente definitiva y usando el frontend solo para UX y bloqueo del botón Guardar.

## Estado actual

Actualizado: 2026-06-18

- Backend: endpoint `validar_producto_venta_api()` implementado y registrado en `/api/ventas/validar-producto/`.
- Template: sección Producto incluye `btnValidarProducto`, `productoMensaje` y `id_producto_validado`.
- Frontend: `static/js/venta-form.js` implementa `validarProducto()`, `resetProductoValidacion()` y `actualizarSubmitVenta()`.
- Modal: `templates/discador/agent_dashboard.html` bloquea guardar si Producto no está validado.
- Tests: se agregaron casos en `apps/ventas/tests.py` para validación de Producto.
- Documentación: se actualizaron `docs/documentacion.md`, `docs/HISTORIAL.md`, `README.md` y este plan.
- Pendiente operativo: ejecutar `python manage.py check` y `python manage.py test apps.ventas.tests --verbosity=2` antes de aplicar migraciones o desplegar.

---

## Contexto revisado

### Documentación relevante

- `docs/documentacion.md`
  - Sección **Producto y Venta**.
  - Regla canónica de precio para `CHIP` y `PACK`.
  - Regla canónica de `tipo_renta`.
  - Endpoint actual `/api/ventas/precio-venta/`.
  - Validaciones implementadas en Sprint 19.3.
- `docs/HISTORIAL.md`
  - 2026-06-11: validación de sección Cliente implementada.
- `docs/HANDOFF_2026-06-05_ventas.md`
  - Dependencias de Producto y Venta.
  - Botón Teléfono a Portar.
  - Selectores de producto, modelo, plan y precio.
- `docs/HANDOFF_2026-06-10_modelo_venta_refactor.md`
  - Formulario cliente inline y validación de cliente.
- `docs/DEV_REFERENCE.md`
  - Validación backend como fuente definitiva.
  - Frontend solo sincroniza.

### Código actual

- Sección Cliente:
  - `templates/ventas/_venta_form_fields.html:67`
  - `templates/ventas/_venta_form_fields.html:78`
  - `templates/ventas/_venta_form_fields.html:96`
  - `static/js/venta-form.js:529`
  - `static/js/venta-form.js:596`
  - `static/js/venta-form.js:886`
- Sección Producto:
  - `templates/ventas/_venta_form_fields.html:214`
  - `templates/ventas/_venta_form_fields.html:221`
  - `static/js/venta-form.js:451`
  - `static/js/venta-form.js:502`
- Backend:
  - `apps/ventas/views.py:121`
  - `apps/ventas/urls.py:21`
  - `apps/ventas/tests.py:239`

### Brecha cerrada

La sección Cliente conserva:

- `btnValidarCliente`
- `btnRegistrarCliente`
- `clienteMensaje`
- `id_cliente_validado`
- bloqueo del submit hasta validar o registrar cliente

La sección Producto ahora tiene:

- botón dedicado de validación
- mensaje de validación
- campo oculto `producto_validado`
- bloqueo explícito del submit por validación de producto
- endpoint backend registrado
- tests de API

---

## Alcance

### Incluir

- Botón **Validar Producto** en la sección Producto y Venta.
- Endpoint backend para validar producto completo.
- Campo oculto `producto_validado`.
- Mensaje visual `productoMensaje`.
- Integración con el bloqueo actual del botón Guardar.
- Tests para endpoint y comportamiento de validación.
- Documentación actualizada.

### No incluir

- Nuevos modelos.
- Migraciones.
- Cambios de estructura de base de datos.
- Cambios en reglas comerciales de precio.
- Persistencia del estado de validación.

---

## Sprints asignados

## Sprint 0 — Preparación y contrato de validación

**Objetivo:** dejar definido el contrato técnico antes de implementar.

### Tareas

1. Definir contrato JSON del endpoint:

   Respuesta válida:

   ```json
   {
     "ok": true,
     "precio": 49,
     "precio_plan": 49,
     "tipo_renta": "R.BAJA",
     "mensaje": "Producto validado correctamente."
   }
   ```

   Respuesta inválida:

   ```json
   {
     "ok": false,
     "campo": "precio_venta",
     "mensaje": "No hay precio definido para la combinación seleccionada."
   }
   ```

2. Definir estado frontend:

   ```text
   id_producto_validado = 'true' | 'false'
   productoMensaje = mensaje visible
   btnValidarProducto = valida contra backend
   Guardar Venta = habilitado solo si Cliente y Producto están validados
   ```

3. Confirmar que no se bloquearán los selects de producto después de validar.
   - Motivo: permitir correcciones sin recargar.
   - Al cambiar cualquier dato de producto, se resetea `producto_validado` a `false`.

4. Confirmar que el backend sigue siendo la validación definitiva.
   - El endpoint solo apoya al frontend.
   - `VentaForm.clean()` sigue siendo obligatorio en el guardado.

### Criterio de aceptación

- Contrato claro para frontend y backend.
- No requiere migración.
- No cambia reglas comerciales existentes.

---

## Sprint 1 — Backend: endpoint de validación de producto

**Objetivo:** crear endpoint backend que valide la sección Producto y Venta completa y retorne valores calculados.

### Archivos

- `apps/ventas/views.py`
- `apps/ventas/urls.py`
- `apps/ventas/tests.py`

### Tareas

1. Crear vista `validar_producto_venta_api()` en `apps/ventas/views.py`.

2. Decorar la vista con:

   ```python
   @login_required
   @require_GET
   ```

3. Reutilizar reglas existentes desde `apps/ventas/models.py`:

   - `Venta.obtener_precio_venta()`
   - `Venta.calcular_tipo_renta()`
   - `PLANES_CHIP`
   - `MODELOS_CHIP_LIST`
   - `PRECIOS_PREPAGO`
   - `PRECIOS_POSTPAGO`

4. Validar datos recibidos:

   - `producto`
   - `origen`
   - `operador`
   - `telefono_portar`
   - `modelo`
   - `plan`
   - `tipo_linea`

5. Para `origen = PORTABILIDAD`:

   - exigir operador válido
   - exigir teléfono a portar
   - exigir solo dígitos
   - exigir longitud entre 7 y 15 dígitos

6. Para `producto = CHIP`:

   - rechazar modelo no vacío
   - exigir plan
   - exigir plan en `PLANES_CHIP`
   - retornar `precio = 1`
   - calcular `precio_plan` desde el plan seleccionado
   - calcular `tipo_renta` usando `precio_plan`

7. Para `producto = PACK`:

   - exigir modelo
   - rechazar modelos chip
   - exigir plan
   - exigir tipo de línea
   - calcular precio según:
     - `PREPAGO`: precio fijo por modelo
     - `POSTPAGO`: matriz modelo + plan
   - calcular `tipo_renta` usando `precio_venta`

8. Retornar errores con campo afectado:

   ```json
   {
     "ok": false,
     "campo": "modelo_producto",
     "mensaje": "Para PACK, debe seleccionar un modelo de equipo válido."
   }
   ```

9. Registrar URL en `apps/ventas/urls.py`:

   ```python
   path('api/ventas/validar-producto/', validar_producto_venta_api, name='validar_producto'),
   ```

### Tests

Agregar tests en `apps/ventas/tests.py`:

- `CHIP` válido retorna `ok=true`, `precio=1`, `precio_plan`, `tipo_renta`.
- `CHIP` con modelo retorna `ok=false`.
- `CHIP` sin plan retorna `ok=false`.
- `PACK + POSTPAGO` válido retorna precio de matriz.
- `PACK + POSTPAGO` sin precio retorna `ok=false`.
- `PACK + PREPAGO` válido retorna precio fijo.
- Portabilidad sin operador retorna `ok=false`.
- Teléfono portar inválido retorna `ok=false`.

### Criterio de aceptación

- Endpoint existe.
- Endpoint no guarda datos.
- Endpoint retorna JSON consistente.
- Tests de endpoint pasan.

---

## Sprint 2 — Template: botón y estado visual de Producto

**Objetivo:** agregar UI de validación en la sección Producto y Venta.

### Archivos

- `templates/ventas/_venta_form_fields.html`

### Tareas

1. Agregar campo oculto en la sección Producto y Venta:

   ```html
   <input type="hidden" name="producto_validado" id="id_producto_validado" value="false">
   ```

2. Agregar botón:

   ```html
   <button type="button" class="btn btn-sm btn-outline-success mt-4" id="btnValidarProducto">
       <i class="bi bi-check-circle"></i> Validar Producto
   </button>
   ```

3. Agregar contenedor de mensaje:

   ```html
   <div id="productoMensaje" class="mt-2"></div>
   ```

4. Mantener estilo visual similar a Cliente:
   - botón pequeño
   - icono Bootstrap
   - mensaje debajo del botón
   - alert success/warning/danger según resultado

### Criterio de aceptación

- El botón aparece en formulario completo.
- El botón aparece en modal, porque usa el mismo parcial.
- No requiere cambios en `venta_form.html` ni `venta_form_modal.html`.

---

## Sprint 3 — Frontend: validación JS y bloqueo del submit

**Objetivo:** conectar botón, endpoint, mensaje y estado global del submit.

### Archivos

- `static/js/venta-form.js`
- `templates/ventas/_venta_form_fields.html`

### Tareas

1. Dentro de `initVentaFormFields()`, obtener referencias:

   ```js
   const productoMensaje = document.getElementById('productoMensaje');
   const btnValidarProducto = document.getElementById('btnValidarProducto');
   const productoValidado = document.getElementById('id_producto_validado');
   ```

2. Crear función global compartida:

   ```js
   window.actualizarSubmitVenta = function() {
       const clienteValidado = document.getElementById('id_cliente_validado');
       const productoValidado = document.getElementById('id_producto_validado');

       const clienteOk = !clienteValidado || clienteValidado.value === 'true';
       const productoOk = !productoValidado || productoValidado.value === 'true';

       const submitBtn = document.querySelector('#ventaModalForm button[type="submit"]') ||
                         document.querySelector('#ventaForm button[type="submit"]');

       if (submitBtn) {
           submitBtn.disabled = !(clienteOk && productoOk);

           if (clienteOk && productoOk) {
               submitBtn.classList.add('btn-success');
               submitBtn.classList.remove('btn-primary');
           } else {
               submitBtn.classList.remove('btn-success');
               submitBtn.classList.add('btn-primary');
           }
       }
   };
   ```

3. Modificar `marcarSeccionValida()` dentro de `initClienteSearch()` para llamar:

   ```js
   window.actualizarSubmitVenta();
   ```

4. Crear helpers en `initVentaFormFields()`:

   ```js
   function mostrarProductoMensaje(texto, tipo) { ... }
   function marcarProductoValido(valida) { ... }
   function resetProductoValidacion() { ... }
   ```

5. Crear `validarProducto()` en `initVentaFormFields()`:

   - leer valores visibles u ocultos
   - llamar endpoint `/api/ventas/validar-producto/`
   - si `ok=true`:
     - asignar `precio_venta`
     - asignar `precio_plan`
     - asignar `tipo_renta`
     - sincronizar hidden fields
     - marcar `producto_validado=true`
     - mostrar mensaje success
   - si `ok=false`:
     - marcar `producto_validado=false`
     - mostrar mensaje danger/warning
     - si el response trae `campo`, marcar campo con `is-invalid` opcionalmente

6. Agregar listener:

   ```js
   if (btnValidarProducto) {
       btnValidarProducto.addEventListener('click', validarProducto);
   }
   ```

7. Resetear validación al cambiar datos de producto:

   - `producto_nombre`
   - `origen`
   - `operador`
   - `telefono_portar`
   - `modelo_producto`
   - `plan_producto`
   - `tipo_linea`

8. Ajustar submit manual de formulario completo en:

   ```js
   document.addEventListener('DOMContentLoaded', function() { ... });
   ```

   Debe validar ambos estados:

   ```js
   const clienteOk = !clienteValidado || clienteValidado.value === 'true';
   const productoOk = !productoValidado || productoValidado.value === 'true';

   if (!clienteOk || !productoOk) {
       e.preventDefault();
   }
   ```

### Criterio de aceptación

- Al validar Producto correctamente, `id_producto_validado` queda en `true`.
- Al validar Cliente correctamente, `id_cliente_validado` queda en `true`.
- El botón Guardar solo se habilita si ambos estados son `true`.
- Si el usuario cambia Producto después de validar, `producto_validado` vuelve a `false`.
- El modal respeta el mismo comportamiento que el formulario completo.
- No se rompe la validación actual de Cliente.

---

## Sprint 4 — Pruebas y validación técnica

**Objetivo:** ejecutar pruebas y verificar flujo manual.

### Comandos

```bash
python manage.py check
python manage.py test apps.ventas.tests --verbosity=2
```

### Validación manual

Probar formulario completo y modal:

1. `CHIP` válido:
   - producto `CHIP`
   - plan `ENTEL_CHIP_*`
   - origen `LINEA_NUEVA`
   - validar producto
   - guardar debe estar habilitado si Cliente está validado

2. `CHIP` inválido:
   - producto `CHIP`
   - modelo seleccionado
   - validar producto
   - debe mostrar error
   - guardar debe estar bloqueado

3. `PACK + POSTPAGO` válido:
   - modelo válido
   - plan válido
   - tipo línea `POSTPAGO`
   - validar producto
   - precio y tipo renta deben sincronizarse

4. `PACK + POSTPAGO` inválido:
   - combinación sin precio
   - validar producto
   - debe mostrar error

5. `PACK + PREPAGO` válido:
   - modelo válido
   - tipo línea `PREPAGO`
   - validar producto
   - precio fijo debe aplicarse

6. Portabilidad:
   - origen `PORTABILIDAD`
   - sin operador
   - validar producto
   - debe mostrar error
   - con operador y teléfono inválido
   - validar producto
   - debe mostrar error

### Criterio de aceptación

- `python manage.py check` pasa.
- `python manage.py test apps.ventas.tests --verbosity=2` pasa.
- Validación manual cubre formulario completo y modal.

---

## Sprint 5 — Documentación

**Objetivo:** actualizar documentación para reflejar la nueva validación de producto.

### Archivos

- `docs/documentacion.md`
- `.kilo/plans/validacion-producto-venta.md`

### Tareas

1. En `docs/documentacion.md`, sección Producto y Venta:
   - agregar botón **Validar Producto**.
   - documentar flujo:
     - usuario completa producto
     - hace clic en Validar Producto
     - frontend llama backend
     - backend retorna precio, precio plan y tipo renta
     - frontend marca sección validada
     - Guardar Venta se habilita solo si Cliente y Producto están validados

2. En sección API Endpoints:
   - agregar:

   ```text
   /api/ventas/validar-producto/  → Valida datos de Producto y Venta y retorna precio/tipo_renta calculados
   ```

3. En validaciones implementadas:
   - agregar validación frontend de Producto y Venta.
   - mantener nota: backend sigue siendo validación definitiva.

4. Actualizar este plan con estado final después de implementación.

### Criterio de aceptación

- Documentación principal menciona el nuevo botón.
- Documentación API incluye nuevo endpoint.
- No hay contradicción con reglas canónicas existentes.

---

## Dependencias entre sprints

```text
Sprint 0 → Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5
```

- Sprint 2 puede iniciar en paralelo con Sprint 1 si el contrato JSON queda definido en Sprint 0.
- Sprint 3 depende de Sprint 1 y Sprint 2.
- Sprint 4 depende de Sprint 3.
- Sprint 5 puede ejecutarse en paralelo con Sprint 4, pero debe cerrar después de confirmar comportamiento final.

---

## Riesgos y decisiones

1. **No bloquear selects después de validar Producto**
   - A diferencia de Cliente, los campos de producto deben poder editarse.
   - La validación se resetea al cambiar cualquier dato relevante.

2. **No duplicar reglas comerciales**
   - El endpoint debe usar `Venta.obtener_precio_venta()` y `Venta.calcular_tipo_renta()`.
   - El frontend no debe reimplementar matrices de precio.

3. **No cambiar validación de guardado**
   - `VentaForm.clean()` sigue siendo obligatorio.
   - El botón solo mejora UX y previene intentos obvios.

4. **Compatibilidad modal**
   - El parcial compartido debe funcionar tanto en `venta_form.html` como en `venta_form_modal.html`.

5. **No requiere migración**
   - `producto_validado` es solo campo oculto de formulario, no campo de modelo.

---

## Criterios de aceptación generales

- Existe botón **Validar Producto** en Producto y Venta.
- El botón valida contra backend.
- El botón muestra mensaje de éxito o error.
- El botón sincroniza `precio_venta`, `precio_plan` y `tipo_renta` cuando la validación es exitosa.
- El botón marca `producto_validado=true` solo si la validación backend es exitosa.
- El botón Guardar permanece bloqueado si Producto no está validado.
- El botón Guardar permanece bloqueado si Cliente no está validado.
- Cambiar datos de Producto invalida la validación previa.
- El formulario completo y el modal se comportan igual.
- No se agregan migraciones.
- Tests de ventas pasan.
- Documentación queda actualizada.
