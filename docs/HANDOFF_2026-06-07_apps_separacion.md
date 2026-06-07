# HANDOFF — 2026-06-07 · Separación Apps Despacho/Courier

> Sesión: Refactorización arquitectónica - separación de módulos postventa en apps independientes

---

## 1. Arquitectura Final

```
Venta (Operaciones)
    │
    ├── Postventa/Backoffice → apps.postventa (SeguimientoBO)
    │
    ├── Despacho → apps.despacho (EstadoDespacho + Proveedor)
    │
    └── Courier → apps.courier (EstadoCourier + ProveedorCourier)
```

---

## 2. Apps Creadas

### apps/despacho/
- `models.py` - `Proveedor`, `EstadoDespacho` (tabla: `despacho_*`)
- `views.py` - `ProveedorListView`, `ProveedorCreateView`, `EstadoDespachoCreateView`, `EstadoDespachoUpdateView`
- `forms.py` - `ProveedorForm`, `EstadoDespachoForm`
- `admin.py` - Registro en admin
- `urls.py` - Rutas `/despacho/`
- `migrations/0001_initial.py` - Migración inicial

### apps/courier/
- `models.py` - `ProveedorCourier`, `EstadoCourier` (tabla: `courier_*`)
- `views.py` - `ProveedorCourierListView`, `ProveedorCourierCreateView`, `EstadoCourierCreateView`, `EstadoCourierUpdateView`
- `forms.py` - `ProveedorCourierForm`, `EstadoCourierForm`
- `admin.py` - Registro en admin
- `urls.py` - Rutas `/courier/`
- `migrations/0001_initial.py` - Migración inicial

---

## 3. Apps Modificadas

### apps/postventa/
| Archivo | Cambio |
|---------|--------|
| `models.py` | Solo contiene `SeguimientoBO` (cambió `related_name` a `bo_seguimiento`) |
| `forms.py` | Solo contiene `SeguimientoBOForm` |
| `views.py` | `DashboardBOView`, `BackofficeListView`, `SeguimientoBOCreateView` |
| `urls.py` | URLs actualizadas a `backoffice_create` |
| `admin.py` | Solo `SeguimientoBOAdmin` |

### apps/ventas/
| Archivo | Cambio |
|---------|--------|
| `admin.py` | Imports actualizados, inlines para nuevos modelos |
| `views.py` | `prefetch_related` actualizado a nuevos related_name |
| `migrations/0015_remove_old_seguimientobo.py` | Elimina modelo antiguo de ventas |

---

## 4. Cambios en related_name

| Modelo | Antes | Después |
|--------|-------|---------|
| SeguimientoBO | `seguimiento_bo` | `bo_seguimiento` |
| EstadoDespacho | `estado_despacho` | `despacho_estado` |
| EstadoCourier | `estado_courier` | `courier_estado` |

---

## 5. URLs Actualizadas

```
/postventa/                    → Dashboard BO
/postventa/backoffice/         → BackofficeListView  
/postventa/backoffice/venta/<id>/ → SeguimientoBOCreateView

/despacho/proveedores/         → ProveedorListView
/despacho/proveedores/nuevo/   → ProveedorCreateView
/despacho/venta/<id>/          → EstadoDespachoCreateView

/courier/proveedores/          → ProveedorCourierListView
/courier/proveedores/nuevo/    → ProveedorCourierCreateView
/courier/venta/<id>/           → EstadoCourierCreateView
```

---

## 6. Templates

| Template | Ubicación |
|----------|-----------|
| `despacho_form.html` | `templates/despacho/` |
| `proveedor_list.html` (despacho) | `templates/despacho/` |
| `proveedor_form.html` (despacho) | `templates/despacho/` |
| `courier_form.html` | `templates/courier/` |
| `proveedor_list.html` (courier) | `templates/courier/` |
| `proveedor_form.html` (courier) | `templates/courier/` |

---

## 7. Migración de Datos (Requerido)

Para migrar datos existentes de tablas antiguas a nuevas:

```sql
-- Migrar datos de despacho
INSERT INTO despacho_estado SELECT * FROM postventa_estadodespacho;
INSERT INTO despacho_proveedor SELECT * FROM postventa_proveedor;

-- Migrar datos de courier  
INSERT INTO courier_estado SELECT * FROM postventa_estadocourier;
INSERT INTO courier_proveedor SELECT * FROM postventa_proveedor;

-- Migrar SeguimientoBO (desde tabla antigua si existe)
INSERT INTO postventa_seguimientobo 
SELECT id, status_bo, fecha_bo, supervisor, observaciones, creado, actualizado, venta_id
FROM ventas_backoffice;
```

---

## 8. Para Integrar

```bash
# 1. Verificar sintaxis
python3 -m py_compile apps/despacho/*.py apps/courier/*.py apps/postventa/*.py

# 2. Aplicar migraciones
python3 manage.py migrate

# 3. (Opcional) Ejecutar migración de datos si existen datos antiguos

# 4. Verificar en admin
python3 manage.py createsuperuser  # si no existe
```