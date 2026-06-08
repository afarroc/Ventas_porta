# HANDOFF — 2026-06-08 · Estado Actual y Sprints Pendientes

> Sesión: Revisión completa del proyecto, actualización de planes y preparación de sprints de corrección

---

## 1. Resumen Ejecutivo

Se realizó una revisión exhaustiva del proyecto Ventas_Porta. Los sprints 0-7 de trazabilidad están **completados**, pero se identificaron **5 bugs críticos** y **5 sprints pendientes** (8-12) para completar la trazabilidad y las reglas de negocio retail.

---

## 2. Estado de Sprints (Real)

### ✅ Completados (0-7)

| Sprint | Entregable | Archivos touched |
|--------|-----------|------------------|
| Sprint 0 - Bug Fix Tests | Indentación corregida | `apps/ventas/tests.py` |
| Sprint 1 - FK Bidireccional | `BaseLlamada.venta` + `Venta.save()` hook | `apps/discador/models.py`, `apps/ventas/models.py` |
| Sprint 2 - HistorialEstado | Modelo + migration | `apps/postventa/models.py`, migrations |
| Sprint 3 - Validaciones Flujo | BO, Despacho, Courier | `apps/postventa/views.py`, `apps/despacho/views.py`, `apps/courier/views.py` |
| Sprint 4 - Dashboard Conversión | Vista + template + URL | `apps/postventa/views.py`, `templates/postventa/dashboard_conversion.html` |
| Sprint 5 - API Trazabilidad | Endpoint `/api/venta/<int:pk>/trazabilidad/` | `apps/ventas/views.py`, `apps/ventas/urls.py` |
| Sprint 6 - Separación Apps | Apps `despacho` y `courier` independientes | `apps/despacho/`, `apps/courier/`, `apps/postventa/`, `config/settings.py` |
| Sprint 7 - Templates Postventa | Templates creados | `templates/despacho/`, `templates/courier/` |

---

## 3. Bugs Críticos Identificados

### 3.1 Bug 1: `SeguimientoBOUpdateView` hereda de `CreateView`
- **Ubicación**: `apps/postventa/views.py:117`
- **Problema**: Hereda de `CreateView` en lugar de `UpdateView`
- **Impacto**: No actualiza registros existentes, crea duplicados o falla
- **Fix**: Cambiar herencia a `UpdateView`

### 3.2 Bug 2: Nombres de campo incorrectos en API Trazabilidad
- **Ubicación**: `apps/ventas/views.py:388-400`
- **Problema**: Usa `despacho.status_despacho` y `courier.status_courier` (campos no existen)
- **Impacto**: API retorna `None` o error en despacho/courier
- **Fix**: Cambiar a `despacho.etapa` y `courier.sts_courier`

### 3.3 Bug 3: `LINEA_NUEVA` en `OPERADOR_CHOICES`
- **Ubicación**: `apps/ventas/models.py:59-62`
- **Problema**: `LINEA_NUEVA` es un origen, no un operador de portabilidad
- **Impacto**: Validación permite operador inválido en portabilidad
- **Fix**: Remover `LINEA_NUEVA` de `OPERADOR_CHOICES`

### 3.4 Bug 4: `calcular_tipo_renta()` desactualizado
- **Ubicación**: `apps/ventas/models.py:208-249`
- **Problema**: Faltan rangos intermedios de la tabla de documentación (Sección 19.1)
- **Impacto**: Cálculo de tipo renta devuelve vacío para precios válidos
- **Fix**: Actualizar reglas según documentación oficial

### 3.5 Bug 5: Validación Estado Courier incompleta
- **Ubicación**: `apps/courier/views.py:32-38`
- **Problema**: Solo valida que exista SeguimientoBO, no que esté en `DESPACHADO`
- **Impacto**: Flujo postventa puede saltearse etapas
- **Fix**: Agregar validación `bo_status == 'DESPACHADO'`

---

## 4. Sprints Pendientes (8-12)

### Sprint 8: Corrección de Bugs Críticos — 0.5 día
- Bug 1: `SeguimientoBOUpdateView` → `UpdateView`
- Bug 2: Corregir campos en API trazabilidad
- Bug 3: Remover `LINEA_NUEVA` de operadores
- Bug 4: Actualizar `calcular_tipo_renta()`
- Bug 5: Validación EstadoCourier requiere DESPACHADO

### Sprint 9: Persistencia de HistorialEstado — 1 día
- **Objetivo**: Registrar automáticamente cambios en `HistorialEstado`
- **Archivos**:
  - `apps/postventa/services.py` (nuevo) - helper `registrar_cambio_estado()`
  - `apps/postventa/views.py` - integrar en `form_valid()` de BO
  - `apps/despacho/views.py` - integrar en create/update despacho
  - `apps/courier/views.py` - integrar en create/update courier
  - `templates/ventas/venta_detail.html` - mostrar historial

### Sprint 10: Validaciones Adicionales de Negocio — 1 día
| # | Validación | Descripción |
|---|-----------|-------------|
| 10.1 | Lead con venta | No crear venta si `resultado_gestion == 'VENTA_CONVERTIDA'` |
| 10.2 | Número portado | Formato válido + no-duplicado en `telefono_portar` |
| 10.3 | Multilínea | Si `multiples_lineas=True`, requerir `tipo_renta2` |
| 10.4 | Tracking único | No duplicar tracking entre despacho/courier |
| 10.5 | Actualización completa lead | Actualizar `es_callable`, `tipo_valido`, `status_java` en `Venta.save()` |

### Sprint 11: Tests Faltantes — 1 día
| App | Archivo | Tests a agregar |
|-----|---------|----------------|
| postventa | `apps/postventa/tests.py` | Modelo HistorialEstado, vistas BO, servicios |
| despacho | `apps/despacho/tests.py` | Modelos, vistas, validaciones flujo |
| courier | `apps/courier/tests.py` | Modelos, vistas, validaciones flujo |
| users | `apps/users/tests.py` | Login, perfiles, roles |
| ventas | `apps/ventas/tests.py` | API trazabilidad, validaciones negocio |

### Sprint 12: Refactor y Mejoras — 0.5 día
- Transacciones atómicas en vistas multi-objecto
- Unificar tipos de `precio_plan` (IntegerField vs DecimalField)
- Limpiar documentación duplicada

---

## 5. Reglas de Negocio Retail — Estado Detallado

### Ventas
| Regla | Código | Documentación | Gap |
|-------|--------|---------------|-----|
| Tipo Renta PORTABILIDAD/PACK 29-49 = R.BAJA | ❌ Falta 29-48 | ✅ | **Desactualizado** |
| Tipo Renta PORTABILIDAD/CHIP 39-59 = R.BAJA | ⚠️ Parcial (solo 25,39,49,59) | ✅ | **Desactualizado** |
| Tipo Renta LINEA_NUEVA/PACK 49-75 = R.BAJA/MEDIA | ❌ Solo 49,75 | ✅ | **Desactualizado** |
| CHIP precio = 1 | ✅ | ✅ | - |
| Portabilidad: operador obligatorio | ✅ | ✅ | - |
| Portabilidad: teléfono_portar obligatorio | ✅ | ✅ | - |
| Plan → Precio autocompletado | ✅ | ✅ | - |
| Modelo → Precio filtrado | ✅ | ✅ | - |

### Postventa
| Regla | Estado | Nota |
|-------|--------|------|
| Flujo BO válido | ✅ | EN_BASE → PDTE_BO → EN_BO → VALIDADO → EN_DESPACHO → DESPACHADO |
| Despacho solo si BO válido | ✅ | VALIDADO o EN_DESPACHO |
| Courier solo si BO existe | ⚠️ | Falta validación estado DESPACHADO |

### Discador
| Regla | Estado | Nota |
|-------|--------|------|
| VENTA_CONVERTIDA bloquea re-gestión | ⚠️ | Falta validación en vistas |

---

## 6. Archivos a Modificar (Resumen)

### Sprint 8
```
apps/postventa/views.py          # UpdateView
apps/ventas/views.py             # campos trazabilidad
apps/ventas/models.py            # operadores + tipo_renta
apps/courier/views.py            # validación estado
```

### Sprint 9
```
apps/postventa/services.py       # NUEVO
apps/postventa/views.py          # integrar historial
apps/despacho/views.py           # integrar historial
apps/courier/views.py            # integrar historial
templates/ventas/venta_detail.html # mostrar historial
```

### Sprint 10
```
apps/ventas/forms.py             # validaciones negocio
apps/discador/views.py           # validación VENTA_CONVERTIDA
apps/ventas/models.py            # actualización completa lead
```

### Sprint 11
```
apps/postventa/tests.py          # NUEVO
apps/despacho/tests.py           # NUEVO
apps/courier/tests.py            # NUEVO
apps/users/tests.py              # NUEVO
apps/ventas/tests.py             # EXTENDER
```

### Sprint 12
```
apps/ventas/views.py             # transacciones
apps/ventas/models.py            # tipo precio_plan
docs/documentacion.md            # limpiar duplicados
```

---

## 7. Checklist de Próximos Pasos

- [ ] **Sprint 8**: Corregir 5 bugs críticos
- [ ] **Sprint 9**: Implementar persistencia de HistorialEstado
- [ ] **Sprint 10**: Agregar validaciones de negocio faltantes
- [ ] **Sprint 11**: Crear suite de tests completa
- [ ] **Sprint 12**: Refactor final
- [ ] **Validar** reglas de tipo_renta con área comercial
- [ ] **Validar** catálogo ENTEL 2026 (modelos y planes)

---

## 8. Referencias

- Plan actualizado: `.kilo/plans/trazabilidad-lead-venta.md`
- Documentación: `docs/documentacion.md`
- Queries: `docs/queries_referenciadas.md`
- Últimos commits:
  - `f08926f` refactor(postventa): separar apps despacho y courier
  - `a7edf24` feat(ui): navbar con dropdown Postventa
  - `9db3d79` fix(navbar): agregar bootstrap CSS

---

## 9. Entregable Sprint 8 (Detalle Técnico)

### 9.1 Fix `SeguimientoBOUpdateView`
```python
# ANTES (incorrecto)
class SeguimientoBOUpdateView(LoginRequiredMixin, CreateView):

# DESPUÉS (correcto)
class SeguimientoBOUpdateView(LoginRequiredMixin, UpdateView):
```

### 9.2 Fix API Trazabilidad
```python
# ANTES
data['despacho']['status'] = despacho.status_despacho  # NO EXISTE
data['courier']['status'] = courier.status_courier      # NO EXISTE

# DESPUÉS
data['despacho']['status'] = despacho.etapa
data['courier']['status'] = courier.sts_courier
```

### 9.3 Fix Operadores
```python
# ANTES
OPERADOR_CHOICES = [
    ('CLARO', 'CLARO'),
    ('LINEA_NUEVA', 'Linea NUEVA'),  # INCORRECTO
    ('MOVISTAR', 'MOVISTAR'),
    ('VIETTEL', 'VIETTEL'),
    ('VIRGIN', 'VIRGIN'),
]

# DESPUÉS
OPERADOR_CHOICES = [
    ('CLARO', 'CLARO'),
    ('MOVISTAR', 'MOVISTAR'),
    ('VIETTEL', 'VIETTEL'),
    ('VIRGIN', 'VIRGIN'),
]
```

### 9.4 Fix Validación Courier
```python
# AGREGAR en EstadoCourierCreateView.dispatch()
bo_status = self.venta.bo_seguimiento.status_bo
if bo_status != 'DESPACHADO':
    messages.error(request, f"Debe estar DESPACHADO para crear EstadoCourier (actual: {bo_status})")
    return redirect('ventas:venta_detail', pk=self.venta.pk)
```
