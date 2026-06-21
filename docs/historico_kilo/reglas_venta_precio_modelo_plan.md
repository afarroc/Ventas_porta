# Plan: Implementar reglas canónicas de precio, modelo y plan para ventas

## Objetivo

Implementar la regla canónica definitiva para ventas:

```yaml
CHIP:
  precio_venta: 1
  modelo_producto: solo '' o '0' normalizado a ''
  plan_producto: obligatorio, solo ENTEL_CHIP_*
  tipo_renta: calculado con precio_plan
  tipo_linea: no afecta

PACK:
  modelo_producto: obligatorio, solo modelos equipo
  plan_producto: obligatorio
  tipo_linea:
    POSTPAGO:
      precio_venta: matriz modelo + plan
      tipo_renta: calculado con precio_venta
    PREPAGO:
      precio_venta: fijo por modelo
      tipo_renta: calculado con precio_venta
```

## Alcance

Archivos a modificar en modo implementación:

1. `apps/ventas/models.py`
2. `apps/ventas/forms.py`
3. `apps/ventas/views.py`
4. `apps/ventas/urls.py`
5. `apps/ventas/management/commands/normalizar_modelos_chip.py` nuevo management command
6. `docs/documentacion.md`
7. `apps/ventas/tests.py`

No se agregarán campos nuevos como `modelo_tipo`, `modelo_chip` ni `modelo_equipo`.

## Pasos de implementación

### 1. Actualizar `apps/ventas/models.py`

Agregar constantes al inicio del archivo:

- `PLANES_CHIP`
- `MODELOS_CHIP_LIST`
- `PRECIOS_POSTPAGO`
- `PRECIOS_PREPAGO`

Actualizar choices:

- `PRECIO_VENTA_CHOICES` debe incluir al menos: `1, 4, 9, 13, 29, 39, 49, 59, 79, 89, 99, 109, 119, 129, 149, 189, 199, 229, 249, 299, 349, 399, 429, 499, 599, 699`
- `PRECIO_PLAN_CHOICES` debe incluir `199`

Agregar método estático:

```python
@staticmethod
def obtener_precio_venta(producto, modelo, plan, tipo_linea):
    ...
```

Modificar `calcular_tipo_renta()` para que `CHIP` use `precio_plan` como valor base.

Modificar `save()` para:

- asignar precio como fallback usando `obtener_precio_venta()` cuando `precio_venta` no venga definido
- lanzar `ValueError` si no existe precio definido
- calcular `tipo_renta` con la lógica corregida
- mantener la actualización existente de `BaseLlamada` al crear venta

### 2. Actualizar `apps/ventas/forms.py`

Importar constantes desde `models.py`:

```python
from .models import Venta, ItemVenta, Cliente, PLANES_CHIP, MODELOS_CHIP_LIST
```

En `VentaForm.clean()`:

- normalizar `modelo_producto` con `strip()`
- convertir `'0'` a `''`
- para `CHIP`:
  - forzar `precio_venta = 1`
  - rechazar modelo no vacío
  - exigir plan
  - exigir plan en `PLANES_CHIP`
- para `PACK`:
  - exigir modelo no vacío
  - rechazar modelos chip
  - exigir plan
  - para `PREPAGO`, asignar precio desde `PRECIOS_PREPAGO`
  - para `POSTPAGO`, asignar precio desde `PRECIOS_POSTPAGO[(modelo, plan)]`
  - rechazar tipo de línea inválido

No depender del frontend para validar negocio.

### 3. Agregar endpoint en `apps/ventas/views.py`

Agregar:

```python
@login_required
@require_GET
def obtener_precio_venta_api(request):
    ...
```

Comportamiento:

- validar `tipo_linea in ['POSTPAGO', 'PREPAGO']`
- normalizar `modelo == '0'` a `''`
- `CHIP` retorna `1`
- `PACK + PREPAGO` retorna precio por modelo
- `PACK + POSTPAGO` retorna precio por modelo + plan
- retornar errores JSON cuando falten parámetros o no exista precio

El endpoint es solo apoyo frontend; la validación real sigue en `forms.py`.

### 4. Registrar URL en `apps/ventas/urls.py`

Agregar import de `obtener_precio_venta_api`.

Agregar ruta:

```python
path('api/ventas/precio-venta/', obtener_precio_venta_api, name='obtener_precio_venta')
```

### 5. Crear management command de normalización

Crear:

```text
apps/ventas/management/commands/normalizar_modelos_chip.py
```

Debe:

- heredar de `BaseCommand`
- buscar ventas con `producto_nombre='CHIP'` y `modelo_producto` distinto de `''` y `'0'`
- ejecutar `update(modelo_producto='')`
- imprimir cantidad normalizada

No usar `save()` para evitar efectos secundarios de `Venta.save()`.

No usar `runscript` porque el proyecto no incluye `django-extensions`.

### 6. Actualizar frontend opcionalmente

Modificaciones recomendadas en `static/js/venta-form.js`:

- al cambiar `producto_nombre = CHIP`, filtrar planes a `PLANES_CHIP`
- al cambiar `producto_nombre = PACK`, mostrar todos los planes
- al cambiar `producto_nombre/modelo/plan/tipo_linea`, llamar a `/api/ventas/precio-venta/`
- para `CHIP`, forzar precio `1`
- para `PACK + PREPAGO`, usar precio prepago retornado
- para `PACK + POSTPAGO`, usar precio matriz retornado

El frontend debe ser UX solamente. Si el endpoint falla, limpiar precio y permitir que el backend valide.

### 7. Actualizar documentación

Actualizar `docs/documentacion.md` en la sección de reglas retail:

- `CHIP` no lleva modelo de equipo
- `modelo_producto='0'` se normaliza a vacío
- `CHIP` solo permite planes `ENTEL_CHIP_*`
- `tipo_renta` para `CHIP` usa `precio_plan`
- `PACK + POSTPAGO` usa matriz modelo + plan
- `PACK + PREPAGO` usa precio fijo por modelo
- `tipo_linea` no condiciona modelo ni plan, pero sí precio para `PACK`

Agregar endpoint `/api/ventas/precio-venta/` en la sección de APIs.

### 8. Agregar tests

Agregar tests unitarios para:

- `Venta.calcular_tipo_renta()` con `CHIP` usando `precio_plan`
- `Venta.obtener_precio_venta()` para `CHIP`, `PACK + POSTPAGO`, `PACK + PREPAGO`
- `VentaForm` rechaza `CHIP` con modelo de equipo
- `VentaForm` normaliza `modelo_producto='0'` a `''`
- `VentaForm` exige plan para `CHIP`
- `VentaForm` rechaza plan no chip para `CHIP`
- `VentaForm` exige modelo para `PACK`
- `VentaForm` rechaza modelo chip para `PACK`
- `VentaForm` exige plan para `PACK`
- `VentaForm` asigna precio prepago por modelo
- `VentaForm` asigna precio postpago por modelo + plan
- endpoint retorna precio válido y errores esperados

## Riesgos y decisiones

1. Las matrices `PRECIOS_POSTPAGO` y `PRECIOS_PREPAGO` deben validarse contra tabla comercial real antes de considerar la implementación final.
2. Si la tabla comercial incluye precios no presentes en `PRECIO_VENTA_CHOICES`, se debe actualizar el choice list.
3. Si `PACK + PREPAGO` debe permitir plan opcional, se debe cambiar la validación. La regla canónica actual exige plan obligatorio.
4. No se recomienda permitir excepciones para datos históricos; normalizar datos existentes con el management command.

## Verificación

Ejecutar después de implementar:

```bash
python manage.py check
python manage.py test apps.ventas.tests --verbosity=2
python manage.py normalizar_modelos_chip
```

Si se implementa frontend, validar manualmente:

- formulario completo de venta
- formulario modal de venta
- `CHIP` con plan chip
- `CHIP` con plan no chip
- `PACK + POSTPAGO` con combinación válida
- `PACK + POSTPAGO` con combinación sin precio
- `PACK + PREPAGO` con precio fijo
- normalización de datos históricos

## Criterio de aceptación

- No se pueden crear ventas `CHIP` con modelo de equipo.
- No se pueden crear ventas `CHIP` sin plan o con plan no chip.
- No se pueden crear ventas `PACK` sin modelo, con modelo chip o sin plan.
- `CHIP` siempre guarda `precio_venta=1`.
- `PACK + PREPAGO` usa precio fijo por modelo.
- `PACK + POSTPAGO` usa matriz modelo + plan.
- `tipo_renta` para `CHIP` se calcula con `precio_plan`.
- El endpoint `/api/ventas/precio-venta/` existe y retorna JSON correcto.
- El management command normaliza ventas `CHIP` históricas sin ejecutar `save()`.
