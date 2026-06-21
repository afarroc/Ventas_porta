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
        ├── postventa ──── apps.postventa (SeguimientoBO + HistorialEstado + services/signals)
        ├── despacho ──── apps.despacho (EstadoDespacho + Proveedor)
        └── courier ────── apps.courier (EstadoCourier + ProveedorCourier)
```

### Sprints Completados (2026-06-05 a 2026-06-08) ✅

| Sprint | Fecha | Entregable |
|--------|-------|------------|
| Sprint 0 - Bug Fix Tests | 2026-06-05 | Indentación corregida en `apps/ventas/tests.py` |
| Sprint 1 - FK Bidireccional | 2026-06-05 | `BaseLlamada.venta` FK + `Venta.save()` hook |
| Sprint 2 - HistorialEstado | 2026-06-06 | Modelo `HistorialEstado` + migration |
| Sprint 3 - Validaciones Flujo | 2026-06-06 | Validaciones BO, Despacho, Courier |
| Sprint 4 - Dashboard Conversión | 2026-06-06 | Vista + template + URL |
| Sprint 5 - API Trazabilidad | 2026-06-06 | Endpoint `/api/venta/<int:pk>/trazabilidad/` |
| Sprint 6 - Separación Apps | 2026-06-06 | Apps `despacho` y `courier` independientes |
| Sprint 7 - Templates Postventa | 2026-06-06 | Templates despacho/courier/proveedor |
| Sprint 8 - Bugs Críticos | 2026-06-08 | UpdateView, API trazabilidad, operadores, tipo_renta, validación courier |
| Sprint 9 - Historial Persistent | 2026-06-08 | Servicio + signals de HistorialEstado |
| Sprint 10 - Validaciones Negocio | 2026-06-08 | Multilínea, lead convertido, teléfono portar |
| Sprint 11 - Tests Iniciales | 2026-06-08 | Suites postventa, despacho, courier |
| Sprint 12 - Refactor | 2026-06-08 | Transacciones atómicas, unificar precio_plan |
| Sprint 13 - Trazabilidad Avanzada | 2026-06-08 | `get_absolute_url()` en modelos, tracking único, bloqueo VENTA_CONVERTIDA |

---

## Entregables Principales — Estado Detallado

### Trazabilidad Lead → Venta
| Característica | Estado | Ubicación |
|----------------|--------|-----------|
| FK `Venta.base_llamada` | ✅ | `apps/ventas/models.py:192-199` |
| FK `BaseLlamada.venta` | ✅ | `apps/discador/models.py:58-66` (related_name='lead_venta') |
| Auto-actualización al crear venta | ✅ | `apps/ventas/models.py:251-279` |
| API trazabilidad JSON | ✅ | `apps/ventas/views.py:342-416` |
| Dashboard de conversión | ✅ | `apps/postventa/views.py` |
| Bloqueo VENTA_CONVERTIDA en discador | ✅ | `apps/discador/views.py:143-148` |

### Historial de Cambios Postventa
| Característica | Estado | Ubicación |
|----------------|--------|-----------|
| Modelo `HistorialEstado` | ✅ | `apps/postventa/models.py:5-34` |
| Servicio `registrar_cambio_estado()` | ✅ | `apps/postventa/services.py` |
| Signals post_save BO/Despacho/Courier | ✅ | `apps/postventa/signals.py` |
| Integración en views (BO, Despacho, Courier) | ✅ | `form_valid()` de cada view |

### Reglas de Negocio Retail
| Regla | Estado | Ubicación |
|-------|--------|-----------|
| Tipo renta: rangos completos Origen/Producto/Precio | ✅ | `apps/ventas/models.py:211-249` |
| CHIP: sin modelo, precio fijo S/. 1 | ✅ | `apps/ventas/forms.py` |
| Portabilidad: operador + teléfono obligatorios | ✅ | Validación en form |
| Plan → precio_plan autocompletado | ✅ | Template JS |
| Modelo → filtra precio_venta | ✅ | `modeloPreciosMap` en JS |
| Multilínea: requiere tipo_renta2 | ✅ | Validación (Sprint 10.3) |
| Teléfono portado: formato único | ✅ | Validación (Sprint 10.2) |
| Tracking único entre despacho/courier | ✅ | `apps/despacho/views.py`, `apps/courier/views.py` |

### Flujo Postventa
| Validación | Estado | Ubicación |
|------------|--------|-----------|
| EstadoDespacho: BO en VALIDADO o EN_DESPACHO | ✅ | `apps/despacho/views.py` |
| EstadoCourier: BO en DESPACHADO | ✅ | `apps/courier/views.py` |
| `get_absolute_url()` en todos los modelos | ✅ | Cada `models.py` |

---

## Comandos de Verificación

```bash
# Tests
python manage.py test apps.ventas.tests apps.discador.tests apps.postventa.tests apps.despacho.tests apps.courier.tests --verbosity=2

# Migraciones
python manage.py showmigrations

# Sintaxis
python3 -m py_compile apps/postventa/*.py apps/despacho/*.py apps/courier/*.py apps/ventas/*.py

# Servidor
python manage.py runserver
```

---

## Entregables Finales

| Entregable | Estado |
|-----------|--------|
| Trazabilidad Lead → Venta | ✅ |
| Historial de cambios postventa | ✅ |
| Validaciones de flujo BO/Despacho/Courier | ✅ |
| Dashboard de conversión | ✅ |
| API trazabilidad unificada | ✅ |
| Reglas de negocio retail actualizadas | ✅ |
| Tests unitarios iniciales | ✅ |
| Transacciones atómicas | ✅ |
| Tracking único despacho/courier | ✅ |
| Bloqueo VENTA_CONVERTIDA en discador | ✅ |
