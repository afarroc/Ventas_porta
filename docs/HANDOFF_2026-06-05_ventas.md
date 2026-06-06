# HANDOFF — 2026-06-05 · App `ventas`

> Sesión: Seguridad de leads, modal de registro de venta, validación de acceso, optimización de formulario de dirección

---

## Commits aplicados

| Hash | Mensaje |
|------|---------|
| 0407ee4 | fix(ventas): UUID lead access consistency and runtime fixes |
| b0c3fa7 | feat(ventas): Update recibo electronico and horario visita choices |
| 1213d58 | feat(ventas): add choices for producto/origen/operador/modelo/plan/precio/tipo_pago fields |

---

## Qué se hizo

### Security — Lead Access con UUID
Se reemplazó `<int:base_llamada_id>` por `<uuid:id_lead>` en rutas:
- `/ventas/nueva/<uuid:id_lead>/`
- `/ventas/recargar-lead/<uuid:id_lead>/`
- `/ventas/modal/<uuid:id_lead>/`
- `/api/ventas/crear/<uuid:id_lead>/`

Implementada función `_check_lead_access()` con verificación por rol:
- **ADMIN**: acceso total a cualquier lead
- **SUPERVISOR**: acceso a leads de agentes supervisados
- **AGENTE**: acceso si tiene CallRecord existente O lead no gestionado por otros

### Modal de Registro de Venta
Integrado en `agent_dashboard.html`:
- Botón "Registrar Venta" ahora abre modal via `openVentaModal()`
- Modal carga formulario async vía API
- Submit vía API `/api/ventas/crear/<uuid:id_lead>/`
- Script JS de búsqueda/validación cliente incluido en parcial compartido

### Modelo Cliente/Venta
- Eliminado: `Cliente.numero`, `Venta.cliente_numero`
- Agregado: `Cliente.tipo_documento`, `Venta.cliente_tipo_documento`
- Migración `0007` aplicada

### Recibo Electrónico y Horario
- `recibo_electronico` y `clausulas`: opciones `SI_DESEA`, `NO_DESEA`
- `horario_visita`: opciones de franjas horarias
  - Lunes a Viernes: 8am–12pm, 1pm–5pm, 5pm–8pm (express)
  - Sábado: 8am–1pm
- `correo_electronico_recibo`: campo Email con validación automática
- `abdcp`: opción SI/NO

### Campos de Producto con Choices (9 campos)
| Campo | Choices |
|-------|---------|
| `producto_nombre` | CHIP, PACK |
| `origen` | Línea Nueva, Portabilidad |
| `operador` | CLARO, Linea NUEVA, MOVISTAR, VIETTEL, VIRGIN |
| `modelo_producto` | 28 opciones (iPhone, Huawei, LG, Motorola, Samsung, ZTE) |
| `plan_producto` | 16 opciones ENTEL (CONTROL/LIBRE) |
| `tipo_linea` | Prepago, Postpago |
| `precio_venta` | 1, 9, 29-699 (valores enteros) |
| `precio_plan` | 29-149 (valores enteros) |
| `tipo_pago` | Efectivo, Tarjeta |

Note: `precio_venta` y `precio_plan` cambiaron de `DecimalField` a `IntegerField` para soportar choices.

### Template - Botón Teléfono Portar
Agregado botón `btnTelefonoPortar` que rellena el campo desde:
1. Teléfono del lead (base_telefono)
2. Teléfono cliente 1
3. Teléfono cliente 2

### Templates
- `venta_form_modal.html` usa parcial compartido `_venta_form_fields.html`
- `venta_form.html` usa mismo parcial (formulario único)
- Scroll habilitado en modal (`max-height: 70vh` + `modal-body-modal`)
- `templates/ventas/_venta_form_fields.html` - parcial compartido con todos los campos del formulario + script JS

### Dirección de Despacho - Optimización (2026-06-05)
- Nuevo campo `centro_poblado` agregado al modelo `Venta`
- `TIPO_VIA_CHOICES` actualizado con 11 opciones peruanas (incluye PUEBLO_JOVEN)
- Combos jerárquicos mejorados: Departamento → Provincia → Distrito con AJAX
- Validación de campo: si `numero_via` está vacío, se requiere `manzana` o `lote`
- Template actualizado con card independiente para dirección

### Producto y Venta - Dependencias por negocio (2026-06-05)
- **Regla 1**: `PRODUCTO = CHIP` → modela deshabilitado, `precio_venta = 1` fijo
- **Regla 2**: `ORIGEN = PORTABILIDAD` → `operador` obligatorio (Claro/Movistar/Viettel/Virgin), `telefono_portar` obligatorio
- **Regla 3**: `plan_producto` → `precio_plan` autocompletado (readonly)
- **Regla 4**: `modelo_producto` → filtra opciones de `precio_venta`
- **Regla 5**: `tipo_linea` → default POSTPAGO
- **Regla 6**: `tipo_renta` → calculado automáticamente según precios

---

## Archivos modificados

```
apps/ventas/models.py              ← Agregado PUEBLO_JOVEN, centro_poblado
apps/ventas/forms.py               ← Widgets mejorados con form-control/form-select
apps/ventas/views.py               ← departamentos agregado al contexto
apps/ventas/migrations/0011_add_centro_poblado.py ← Migración nueva
templates/ventas/_venta_form_fields.html ← Sección dirección reorganizada, JS actualizado
```

---

## Próximos pasos

1. **Tests**: Ejecutar `python manage.py test apps.ventas.tests` (configurar BD de pruebas)
2. **UI**: Verificar dropdowns en navegador y funcionamiento de validaciones
3. **Documentación**: Sincronizar docs/documentacion.md con cambios actuales

---

## Handoff adicional — 2026-06-06 · Template de Producto y Modelo

### Problemas identificados y corregidos

| Problema | Solución |
|----------|----------|
| **19 modelos faltantes** en selector `modelo_producto` | Agregados todos los modelos del `MODELO_PRODUCTO_CHOICES` |
| **3 planes faltantes** en selector `plan_producto` | Agregados `ENTEL_75_CONTROL`, `ENTEL_LIBRE_149_LIBRE`, `ENTEL_LIBRE_99_LIBRE` |
| **Conflicto de IDs** (select visible vs campo oculto) | Renombrados: `_display` suffix para visuales, original para ocultos |
| **Values incorrectos** (labels en lugar de códigos) | Corregidos a códigos (`ZTE_BLADE_L5_GRIS` vs `ZTE BLADE L5-GRIS-3G`) |
| **JavaScript `modeloPreciosMap`** desactualizado | Actualizado con nuevos códigos de modelo |
| **JavaScript `planPrecioMap`** desactualizado | Actualizado con nuevos códigos de plan |
| **Visibilidad del selector de modelo** | Agregada llamada a `updatePorProducto()` al cargar DOM |

### Selectores actualizados

| Campo | ID visual | ID oculto (Django) |
|-------|-----------|-------------------|
| Producto | `id_producto_nombre_display` | `id_producto_nombre` |
| Origen | `id_origen_display` | `id_origen` |
| Operador | `id_operador_display` | `id_operador` |
| Modelo | `id_modelo_producto` | `id_modelo_producto` |
| Plan | `id_plan_producto_display` | `id_plan_producto` |
| Precio Plan | `id_precio_plan_display` | `id_precio_plan` |
| Precio Venta | `id_precio_venta_display` | `id_precio_venta` |
| Tipo Línea | `id_tipo_linea_display` | `id_tipo_linea` |
| Tipo Pago | `id_tipo_pago_display` | `id_tipo_pago` |
| Teléfono Portar | `id_telefono_portar_display` | `id_telefono_portar` |

### Archivos modificados

```
templates/ventas/_venta_form_fields.html ← Corrección IDs y agregado modelos/planes
```

### Funcionalidad verificada

- ✅ Selector de modelo aparece solo cuando `producto = 'PACK'`
- ✅ Precio de plan se puebla automáticamente al seleccionar un plan
- ✅ Precio de venta se filtra según modelo seleccionado
- ✅ Teléfono portar visible solo cuando `origen = 'PORTABILIDAD'`