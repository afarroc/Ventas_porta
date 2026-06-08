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
        ├── Postventa/BO ──── apps.postventa (SeguimientoBO + HistorialEstado)
        ├── Despacho ──────── apps.despacho (EstadoDespacho + Proveedor)
        └── Courier ───────── apps.courier (EstadoCourier + ProveedorCourier)
```

### Sprints Completados (2026-06-05 a 2026-06-08)

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

---

## Sprints Pendientes

### Sprint 8: Corrección de Bugs Críticos - 0.5 día

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 8.1 | Corregir `SeguimientoBOUpdateView` hereda de `UpdateView` (actualmente `CreateView`) | `apps/postventa/views.py:117` | Alta |
| 8.2 | Corregir nombres de campo en API trazabilidad: `status_despacho` → `etapa`, `status_courier` → `sts_courier` | `apps/ventas/views.py:388-400` | Alta |
| 8.3 | Corregir `LINEA_NUEVA` en `OPERADOR_CHOICES` (es origen, no operador) | `apps/ventas/models.py:59-62` | Alta |
| 8.4 | Actualizar `calcular_tipo_renta()` con rangos completos de documentación | `apps/ventas/models.py:208-249` | Alta |
| 8.5 | Agregar validación en `EstadoCourierCreateView`: requerir SeguimientoBO en `DESPACHADO` | `apps/courier/views.py:32-38` | Alta |

### Sprint 9: Persistencia de HistorialEstado - 1 día

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 9.1 | Crear helper/service para registrar cambios en `HistorialEstado` | `apps/postventa/services.py` (nuevo) | Alta |
| 9.2 | Integrar en `SeguimientoBOUpdateView.form_valid()` | `apps/postventa/views.py` | Alta |
| 9.3 | Integrar en `EstadoDespachoCreateView/UpdateView` | `apps/despacho/views.py` | Alta |
| 9.4 | Integrar en `EstadoCourierCreateView/UpdateView` | `apps/courier/views.py` | Alta |
| 9.5 | Incluir historial en template `venta_detail.html` | `templates/ventas/venta_detail.html` | Media |

### Sprint 10: Validaciones Adicionales de Negocio - 1 día

| # | Tarea | Descripción | Prioridad |
|---|-------|-------------|-----------|
| 10.1 | Validación lead con venta | No permitir crear venta si `BaseLlamada.resultado_gestion == 'VENTA_CONVERTIDA'` | Alta |
| 10.2 | Validación número portado | Validar formato y no-duplicado de `telefono_portar` en portabilidad | Alta |
| 10.3 | Validación multilínea | Si `multiples_lineas=True`, requerir `tipo_renta2` | Media |
| 10.4 | Validación tracking | Tracking único por venta (despacho + courier no duplicados) | Media |
| 10.5 | Actualización completa del lead | En `Venta.save()`, actualizar: `es_callable`, `tipo_valido`, `status_java` desde CallRecord | Media |

### Sprint 11: Tests Faltantes - 1 día

| # | Test | Archivo | Prioridad |
|---|------|---------|-----------|
| 11.1 | Tests para `apps.postventa` | `apps/postventa/tests.py` (nuevo) | Alta |
| 11.2 | Tests para `apps.despacho` | `apps/despacho/tests.py` (nuevo) | Alta |
| 11.3 | Tests para `apps.courier` | `apps/courier/tests.py` (nuevo) | Alta |
| 11.4 | Tests para `apps.users` | `apps/users/tests.py` | Media |
| 11.5 | Tests API trazabilidad | Extender `apps/ventas/tests.py` | Media |
| 11.6 | Tests flujo completo | Integración lead → venta → BO → despacho → courier | Alta |

### Sprint 12: Refactor y Mejoras - 0.5 día

| # | Tarea | Archivo | Prioridad |
|---|-------|---------|-----------|
| 12.1 | Transacciones atómicas | Usar `transaction.atomic()` en vistas que crean múltiples objetos | Alta |
| 12.2 | Inconsistencia `precio_plan` | Unificar tipo: `ItemVenta.precio_plan` debería ser `IntegerField` o `Venta.precio_plan` `DecimalField` | Media |
| 12.3 | Limpiar documentación | Remover secciones duplicadas en `docs/documentacion.md` | Baja |

---

## Reglas de Negocio Retail - Estado Actual

### Ventas (Apps Ventas)

| Regla | Estado | Notas |
|-------|--------|-------|
| Tipo Renta por combinación Origen/Producto/Precio | ⚠️ Parcial | Código desactualizado, faltan rangos intermedios (ver Sprint 8.4) |
| CHIP sin modelo, precio = 1 fijo | ✅ | `apps/ventas/forms.py:121-124` |
| Portabilidad: operador + teléfono obligatorios | ✅ | Valida CLARO/MOVISTAR/VIETTEL/VIRGIN |
| Plan → Precio Plan autocompletado | ✅ | Template JS |
| Modelo → Precio Venta filtrado | ✅ | `modeloPreciosMap` en JS |
| Tipo línea default POSTPAGO | ✅ | `apps/ventas/forms.py:87-88` |
| Recibo SI_DESEA → correo obligatorio | ✅ | `apps/ventas/forms.py:145-147` |
| Cliente DNI/RUC/CE/Pasaporte | ✅ | Choices en modelo |
| Multilínea: `tipo_renta2` | ✅ | Campo existe pero sin validación |

### Postventa (Apps Postventa/Despacho/Courier)

| Regla | Estado | Notas |
|-------|--------|-------|
| Flujo BO: EN_BASE → PDTE_BO → EN_BO → VALIDADO → EN_DESPACHO → DESPACHADO | ✅ | Implementado en modelo y vistas |
| EstadoDespacho solo si BO en VALIDADO/EN_DESPACHO | ✅ | `apps/despacho/views.py:38-44` |
| EstadoCourier solo si BO existe | ⚠️ Parcial | Falta validación de estado DESPACHADO (Sprint 8.5) |
| Tracking único por venta | ❌ | No validado |

### Discador (Apps Discador)

| Regla | Estado | Notas |
|-------|--------|-------|
| Lead con VENTA_CONVERTIDA no vuelve a gestionarse | ⚠️ Parcial | Falta validación en vistas de discador |
| UUID para acceso seguro a leads | ✅ | `_check_lead_access()` implementado |
| Un lead, una venta | ⚠️ Parcial | Falta validación al crear venta |

---

## Entregables por Sprint

| Sprint | Entregable | Criteria de Aceptación |
|--------|------------|------------------------|
| Sprint 8 | Bugs corregidos | Tests pasan, vistas funcionan correctamente |
| Sprint 9 | Historial persistente | Cada cambio de estado BO/Despacho/Courier queda registrado |
| Sprint 10 | Validaciones completas | Flujos respetados, no se pueden saltar etapas |
| Sprint 11 | Cobertura de tests | >80% cobertura en apps postventa/despacho/courier |
| Sprint 12 | Código limpio | Sin deudas técnicas críticas, transacciones atómicas |

---

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Migración de datos con apps separadas | Scripts SQL documentados en HANDOFF apps separación |
| Performance en queries complejas | `select_related`/`prefetch_related` optimizado |
| Conflictos de estados entre áreas | Transacciones atómicas + validaciones en vistas |
| Reglas de negocio desactualizadas | Sincronizar con área comercial antes de Sprint 10 |

---

## Archivos a Modificar por Sprint

| Sprint | Archivos principales |
|--------|---------------------|
| Sprint 8 | `apps/postventa/views.py`, `apps/ventas/views.py`, `apps/ventas/models.py`, `apps/courier/views.py` |
| Sprint 9 | `apps/postventa/services.py` (nuevo), `apps/postventa/views.py`, `apps/despacho/views.py`, `apps/courier/views.py` |
| Sprint 10 | `apps/ventas/forms.py`, `apps/discador/views.py`, `apps/ventas/models.py` |
| Sprint 11 | `apps/postventa/tests.py`, `apps/despacho/tests.py`, `apps/courier/tests.py`, `apps/users/tests.py` |
| Sprint 12 | Múltiples archivos (refactor) |

---

## Git Workflow

```bash
git checkout -b feature/trazabilidad-lead-venta

# Sprint 8: Bugs
git commit -m "fix: corregir bugs críticos en vistas postventa"

# Sprint 9: Historial
git commit -m "feat: implementar persistencia de HistorialEstado"

# Sprint 10: Validaciones
git commit -m "feat: agregar validaciones de flujo postventa"

# Sprint 11: Tests
git commit -m "test: agregar suite de tests postventa/despacho/courier"

# Sprint 12: Refactor
git commit -m "refactor: transacciones atómicas y limpieza código"

git push origin feature/trazabilidad-lead-venta
```

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
| Sprint 8 | Pendiente | ⏳ | Corrección de bugs críticos |
| Sprint 9 | Pendiente | ⏳ | Persistencia de HistorialEstado en vistas |
| Sprint 10 | Pendiente | ⏳ | Validaciones adicionales de negocio |
| Sprint 11 | Pendiente | ⏳ | Tests faltantes |
| Sprint 12 | Pendiente | ⏳ | Refactor y mejoras |

---

## Comandos de Verificación

```bash
# Tests actuales
python manage.py test apps.ventas.tests apps.discador.tests --verbosity=2

# Verificar migraciones
python manage.py showmigrations

# Verificar sintaxis
python3 -m py_compile apps/postventa/*.py apps/despacho/*.py apps/courier/*.py
```
