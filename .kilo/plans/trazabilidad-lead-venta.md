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

### Sprint 13: Trazabilidad Avanzada y Validaciones - 0.5 día ✅

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 13.1 | Agregar `get_absolute_url()` a SeguimientoBO | `apps/postventa/models.py` | Media |
| 13.2 | Agregar `get_absolute_url()` a EstadoDespacho | `apps/despacho/models.py` | Media |
| 13.3 | Agregar `get_absolute_url()` a EstadoCourier | `apps/courier/models.py` | Media |
| 13.4 | Tracking único despacho/courier por venta | `apps/despacho/views.py`, `apps/courier/views.py` | Alta |
| 13.5 | Bloquear leads VENTA_CONVERTIDA en discador | `apps/discador/views.py` | Alta |

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
| EstadoCourier solo si BO en DESPACHADO | ✅ | `apps/courier/views.py:39-44` |
| Historial de cambios persistente | ✅ | Servicio integrado |
| Tracking único por venta | ✅ | Validación agregada (Sprint 13) |

### Discador (Apps Discador)

| Regla | Estado | Notas |
|-------|--------|-------|
| VENTA_CONVERTIDA bloquea re-gestión | ✅ | Validación agregada (Sprint 13) |
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
| Sprint 13 | 2026-06-08 | ✅ | get_absolute_url, tracking único, bloqueo VENTA_CONVERTIDA |

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
