# HANDOFF — 2026-06-06 · Refactorización Arquitectura Postventa

> Sesión: Separación de Backoffice/Despacho/Courier en apps independientes + vista consolidada postventa + dashboard BO

---

## 1. Mapeo de Ubicaciones - Arquitectura por Areas

| Sección | Antigua Ubicación | Nueva Ubicación |
|---------|------------------|----------------|
| **SeguimientoBO** | `apps/ventas/models.py` | `apps/postventa/models.py` |
| **EstadoDespacho** | No existía | `apps/postventa/models.py` |
| **EstadoCourier** | No existía | `apps/postventa/models.py` |
| **Proveedor** | No existía | `apps/postventa/models.py` |
| **Gestión del Discador** | Formulario principal (`/ventas/nueva/`) | `/discador/resultados/` (lista), `/discador/resultados/<id>/` (detalle) |
| **Ítems de la Venta** | Formulario principal (`/ventas/nueva/`) | `/ventas/<id>/item/nuevo/` (vista CreateView) |
| **Vista consolidada postventa** | No existía | `/ventas/backoffice/` (BackofficeListView) |
| **Dashboard BO** | No existía | `/postventa/` (DashboardBOView) |
| **Formulario BO por venta** | No existía | `/postventa/backoffice/venta/<id>/` (SeguimientoBOCreateView) |

---

## 2. Arquitectura por Areas

```
Lead (BaseLlamada) ────────── discador / WFM
        │
        ▼
    Venta (Operaciones) ──── entrada de venta
        │
        ├── postventa ──── SeguimientoBO (validación, administrativo)
        │
        ├── despacho ──── EstadoDespacho (preparación, tránsito, entrega)
        │
        └── courier ──── EstadoCourier (proveedor, tracking, entrega)
```

**Nuevos modelos en `apps/postventa`:**

| Modelo | Tabla | Descripción |
|--------|-------|-------------|
| `SeguimientoBO` | `postventa_seguimientobo` | Estado BO: EN_BASE/PDTE_BO/EN_BO/VALIDADO/EN_DESPACHO/DESPACHADO |
| `EstadoDespacho` | `postventa_estadodespacho` | Etapa: EN_BASE/PDTE_DESPACHO/EN_PREPARACION/EN_TRANSITO/ENTREGADO/RECHAZADO |
| `EstadoCourier` | `postventa_estadocourier` | Estado courier: PDTE_BO/EN_RUTA/ENTREGADO/RECHAZADO |
| `Proveedor` | `postventa_proveedor` | Entidad independiente para proveedores de despacho/courier |

---

## 3. Sprints Planificados

| Sprint | Duración | Tareas | Archivos |
|--------|----------|--------|----------|
| Sprint 1 | 0.5 día | Backup BD, verificación, branch | Git |
| Sprint 2 | 1 día | Migraciones: BaseLlamada + Venta | `apps/discador/migrations/`, `apps/ventas/migrations/` |
| Sprint 3 | 1 día | App postventa (modelos + migración) | `apps/postventa/` |
| Sprint 4 | 0.5 día | Config + Admin panel | `settings.py`, `apps/postventa/admin.py` |
| Sprint 5 | 0.5 día | Vista BackofficeListView + template | `apps/ventas/views.py`, `templates/ventas/backoffice_list.html` |
| Sprint 6 | 0.5 día | URLs + Home dashboard | `apps/ventas/urls.py`, `templates/home.html` |
| Sprint 7 | 0.5 día | Dashboard BO + formulario | `apps/postventa/views.py`, `templates/postventa/` |
| Sprint 8 | 0.5 día | Testing y docs | tests.py, docs/ |

---

## 4. Status Actual

| Sprint | Status | Comentarios |
|--------|--------|-------------|
| Sprint 1-6 (anterior) | Completado | Backup BD pendiente ejecución manual |
| Sprint 7 | Completado | Dashboard BO + formulario propio creado |
| Sprint 8 | **Completado** | Templates faltantes creados, URLs agregadas, código duplicado eliminado |

---

## 9. Próximos Pasos

✅ **COMPLETADO - Sprint 8:**

1. ✅ Templates faltantes creados:
   - `templates/postventa/despacho_form.html` - Formulario EstadoDespacho
   - `templates/postventa/courier_form.html` - Formulario EstadoCourier
   - `templates/postventa/proveedor_list.html` - Listado Proveedores
   - `templates/postventa/proveedor_form.html` - Formulario Proveedor

2. ✅ URLs agregadas en `apps/postventa/urls.py`:
   - `/postventa/despacho/venta/<int:venta_id>/` - Formulario Despacho
   - `/postventa/courier/venta/<int:venta_id>/` - Formulario Courier
   - `/postventa/proveedores/` - Listado Proveedores
   - `/postventa/proveedores/nuevo/` - Crear Proveedor

3. ✅ Botones de acción en detalle de venta actualizados:
   - BO, Despacho, Courier con enlaces a rutas de postventa
   - Muestra información de seguimiento_bo, estado_despacho, estado_courier

4. ✅ Modelo duplicado eliminado:
   - `SeguimientoBO` removido de `apps/ventas/models.py` (ahora solo existe en postventa)

5. ✅ Imports corregidos:
   - `apps/ventas/views.py` usa `SeguimientoBO` y `SeguimientoBOForm` desde `apps.postventa`
