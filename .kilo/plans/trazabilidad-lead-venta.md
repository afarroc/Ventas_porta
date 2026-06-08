# Plan de Acción: Trazabilidad Lead → Venta y Reglas de Negocio Retail

## Objetivo
Completar la trazabilidad completa del ciclo de vida de un lead (BaseLlamada) hasta su conversión en venta, con seguimiento postventa (BO/Despacho/Courier), auditoría de cambios de estado, y actualización de reglas de negocio retail.

---

## Estado Actual del Proyecto

### Arquitectura Implementada
```
Lead (BaseLlamada) ────────── apps.discador (WFM/Discador)
        │
        ▼
    Venta (Operaciones) ──── apps.ventas
        │
        ├── Postventa/BO ──── apps.postventa (SeguimientoBO + HistorialEstado + services)
        ├── Despacho ──────── apps.despacho (EstadoDespacho + Proveedor)
        └── Courier ───────── apps.courier (EstadoCourier + ProveedorCourier)
```

### Sprints Completados (2026-06-05 a 2026-06-08) ✅

| Sprint | Estado | Entregable |
|--------|--------|------------|
| Sprint 0 - Bug Fix Tests | ✅ | Indentación corregida en `apps/ventas/tests.py` |
| Sprint 1 - FK Bidireccional | ✅ | `BaseLlamada.venta` FK, actualización automática en `Venta.save()` |
| Sprint 2 - HistorialEstado | ✅ | Modelo `HistorialEstado` creado, migration aplicada |
| Sprint 3 - Validaciones Flujo | ✅ | Validaciones en BO, Despacho, Courier |
| Sprint 4 - Dashboard Conversión | ✅ | Template, vista y URL creadas |
| Sprint 5 - API Trazabilidad | ✅ | Endpoint `/api/venta/<int:pk>/trazabilidad/` implementado |
| Sprint 6 - Separación Apps | ✅ | Apps `despacho` y `courier` separadas de `postventa` |
| Sprint 7 - Templates Postventa | ✅ | Templates despacho/courier/proveedor creados |
| Sprint 8 - Bugs Críticos | ✅ | UpdateView, API trazabilidad, operadores, tipo_renta, validación courier |
| Sprint 9 - Historial Persistent | ✅ | Servicio `registrar_cambio_estado()` integrado en BO/Despacho/Courier |
| Sprint 10 - Validaciones Negocio | ✅ | Lead convertido, teléfono portado, multilínea |
| Sprint 11 - Tests Iniciales | ✅ | Suites creadas para postventa, despacho, courier |
| Sprint 12 - Refactor | ✅ | Transacciones atómicas en ventas |

---

## Sprints Pendientes

### Sprint 13: Unificación de Tipos y Limpieza Docs - 0.5 día

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 13.1 | Unificar `precio_plan`: cambiar `ItemVenta.precio_plan` a `IntegerField` para coincidir con `Venta.precio_plan` | `apps/ventas/models.py:278` | Media |
| 13.2 | Limpiar secciones duplicadas en `docs/documentacion.md` (Sección 14 repetida) | `docs/documentacion.md` | Baja |
| 13.3 | Actualizar tabla de historial en plan con sprints 8-12 completados | `.kilo/plans/trazabilidad-lead-venta.md` | Baja |

---

## Reglas de Negocio Retail - Estado Actual

### Ventas (Apps Ventas)

| Regla | Estado | Notas |
|-------|--------|-------|
| Tipo Renta por combinación Origen/Producto/Precio | ✅ | Rangos completos según documentación (Sprint 8.4) |
| CHIP sin modelo, precio = 1 fijo | ✅ | `apps/ventas/forms.py:121-124` |
| Portabilidad: operador + teléfono obligatorios | ✅ | Valida CLARO/MOVISTAR/VIETTEL/VIRGIN |
| Plan → Precio Plan autocompletado | ✅ | Template JS |
| Modelo → Precio Venta filtrado | ✅ | `modeloPreciosMap` en JS |
| Tipo línea default POSTPAGO | ✅ | `apps/ventas/forms.py:87-88` |
| Recibo SI_DESEA → correo obligatorio | ✅ | `apps/ventas/forms.py:145-147` |
| Cliente DNI/RUC/CE/Pasaporte | ✅ | Choices en modelo |
| Multilínea: `tipo_renta2` | ✅ | Validación agregada (Sprint 10.3) |
| Lead convertido no reutilizable | ✅ | Validación en form (Sprint 10.1) |
| Teléfono portado único y formato | ✅ | Validación en form (Sprint 10.2) |

### Postventa (Apps Postventa/Despacho/Courier)

| Regla | Estado | Notas |
|-------|--------|-------|
| Flujo BO: EN_BASE → PDTE_BO → EN_BO → VALIDADO → EN_DESPACHO → DESPACHADO | ✅ | Implementado en modelo y vistas |
| EstadoDespacho solo si BO en VALIDADO/EN_DESPACHO | ✅ | `apps/despacho/views.py:38-44` |
| EstadoCourier solo si BO en DESPACHADO | ✅ | `apps/courier/views.py:39-44` (Sprint 8.5) |
| Historial de cambios persistente | ✅ | Servicio integrado (Sprint 9) |
| Tracking único por venta | ❌ | No validado |

### Discador (Apps Discador)

| Regla | Estado | Notas |
|-------|--------|-------|
| VENTA_CONVERTIDA bloquea re-gestión | ⚠️ | Falta validación en vistas de discador |
| UUID para acceso seguro a leads | ✅ | `_check_lead_access()` implementado |
| Un lead, una venta | ✅ | Validado en form (Sprint 10.1) |

---

## Historico de Sprints

| Sprint | Fecha | Estado | Descripción |
|--------|-------|--------|-------------|
| Sprint 0 | 2026-06-07 | ✅ | Bug fix tests - indentación |
| Sprint 1 | 2026-06-07 | ✅ | FK bidireccional Lead-Venta |
| Sprint 2 | 2026-06-07 | ✅ | Modelo HistorialEstado |
| Sprint 3 | 2026-06-07 | ✅ | Validaciones de flujo BO/Despacho/Courier |
| Sprint 4 | 2026-06-07 | ✅ | Dashboard de Conversión |
| Sprint 5 | 2026-06-07 | ✅ | API Trazabilidad unificada |
| Sprint 6 | 2026-06-07 | ✅ | Separación apps Despacho/Courier |
| Sprint 7 | 2026-06-07 | ✅ | Templates postventa |
| Sprint 8 | 2026-06-08 | ✅ | Corrección de bugs críticos |
| Sprint 9 | 2026-06-08 | ✅ | Persistencia de HistorialEstado |
| Sprint 10 | 2026-06-08 | ✅ | Validaciones adicionales de negocio |
| Sprint 11 | 2026-06-08 | ✅ | Tests iniciales postventa/despacho/courier |
| Sprint 12 | 2026-06-08 | ✅ | Refactor: transacciones atómicas |
| Sprint 13 | Pendiente | ⏳ | Unificación tipos y limpieza documentación |

---

## Comandos de Verificación

```bash
# Tests actuales
python manage.py test apps.ventas.tests apps.discador.tests apps.postventa.tests apps.despacho.tests apps.courier.tests --verbosity=2

# Verificar migraciones
python manage.py showmigrations

# Verificar sintaxis
python3 -m py_compile apps/postventa/*.py apps/despacho/*.py apps/courier/*.py apps/ventas/*.py

# Runserver
python manage.py runserver
```

---

## Entregables Finales

| Entregable | Estado |
|-----------|--------|
| Trazabilidad Lead → Venta | ✅ |
| Historial de cambios postventa | ✅ |
| Validaciones de flujo | ✅ |
| Dashboard de conversión | ✅ |
| API trazabilidad unificada | ✅ |
| Reglas de negocio retail actualizadas | ✅ |
| Tests unitarios iniciales | ✅ |
| Transacciones atómicas | ✅ |
