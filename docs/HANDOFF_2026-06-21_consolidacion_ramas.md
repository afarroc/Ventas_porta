# HANDOFF — 2026-06-21 · Consolidación de Ramas y Estado del Proyecto

> Sesión: Consolidación de ramas feature/catalogo-productos-retail y little-garnet en master. Historia lineal unificada.

---

## 1. Resumen Ejecutivo

Se realizó la consolidación de ramas del repositorio Ventas_Porta. Las ramas `feature/catalogo-productos-retail` y `little-garnet` fueron integradas en `master` mediante rebase, resultando en una historia lineal de commits. Todos los cambios de ambas ramas se preservaron sin pérdida de sincronización.

**Cambio estructural realizado:**
- Rebase de `feature/catalogo-productos-retail` sobre `master` (commits reescritos: `c12093a` a `66542e4`)
- Fast-forward de `master` al tip de la feature
- Eliminación de ramas `feature/catalogo-productos-retail`, `little-garnet` y worktree asociado
- Remoto actualizado: `cb9aa6d..66542e4 master -> master`

---

## 2. Estado de Sprints (Real)

### ✅ Completados (0-8)

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
| Sprint 8 - Validación Producto/Venta | Catálogo opcional + reglas legacy | `apps/catalogo/`, `apps/ventas/catalogo_utils.py`, `apps/ventas/forms.py`, `apps/ventas/views.py`, `static/js/venta-form.js` |

---

## 3. Arquitectura del Proyecto

### Apps Django

| App | Descripción | Estado |
|-----|-------------|--------|
| `apps.discador` | BaseLlamada, CallRecord, dashboard agente | Activa |
| `apps.ventas` | Venta, ItemVenta, Cliente, validaciones, catálogo | Activa |
| `apps.users` | UserProfile, roles, disponibilidad | Activa |
| `apps.postventa` | SeguimientoBO, HistorialEstado, dashboard BO | Activa |
| `apps.despacho` | EstadoDespacho, tracking físico | Activa |
| `apps.courier` | EstadoCourier, ProveedorCourier | Activa |
| `apps.catalogo` | Catálogo comercial (opcional, no registrada en `INSTALLED_APPS`) | Opcional |

### Estructura de carpetas

```
├── apps/
│   ├── catalogo/           # App opcional (no registrada)
│   │   ├── models.py       # Oferta, Plan, ModeloProducto
│   │   ├── views.py        # API catálogo
│   │   └── urls_api.py     # /api/catalogo/
│   ├── discador/
│   │   ├── models.py       # BaseLlamada (HexUUIDField id_lead), CallRecord
│   │   └── views.py        # Dashboard agente, listado resultados
│   ├── ventas/
│   │   ├── models.py       # Venta, ItemVenta, Cliente, PRECIOS_*
│   │   ├── forms.py        # VentaForm (validación secciones Cliente/Producto)
│   │   ├── views.py        # CRUD + API precio-venta + validar-producto
│   │   ├── catalogo_utils.py # Fallback catálogo → legacy
│   │   └── ubigeo_peru.py  # JSON local ubigeo Perú
│   ├── postventa/
│   │   ├── models.py       # SeguimientoBO, HistorialEstado
│   │   └── views.py        # BO, dashboard, trazabilidad
│   ├── despacho/
│   │   └── views.py        # EstadoDespacho CRUD
│   ├── courier/
│   │   └── views.py        # EstadoCourier CRUD
│   └── users/
│       └── models.py       # UserProfile
├── config/
│   ├── settings.py         # INSTALLED_APPS (catalogo NO registrada)
│   └── urls.py             # Router principal
├── static/
│   ├── js/venta-form.js    # Validaciones frontend
│   └── data/ubigeo-peru.json
├── templates/
│   ├── ventas/
│   │   ├── venta_form.html
│   │   ├── venta_form_modal.html
│   │   └── _venta_form_fields.html
│   └── postventa/, despacho/, courier/
└── docs/
    ├── documentacion.md    # Documentación principal
    ├── HISTORIAL.md        # Changelog
    └── HANDOFF_*.md        # Handoffs por fecha
```

---

## 4. Características Principales

### 4.1 Validación de Venta por Secciones

El formulario de ventas valida en etapas bloqueando el botón **Guardar Venta** hasta completar:

1. **Cliente**: Buscar/validar cliente existente o registrar nuevo vía API
2. **Producto y Venta**: Validar producto (CHIP/PACK), modelo, plan, precios
3. **Guardar Venta**: Se habilita solo cuando Cliente y Producto están validados

### 4.2 Catálogo Comercial Opcional

- `apps.catalogo` existe pero **no está registrada** en `INSTALLED_APPS`
- `apps/ventas/catalogo_utils.py` consulta el catálogo solo si la app está instalada
- Fallback automático a reglas legacy (`PRECIOS_PREPAGO`, `PRECIOS_POSTPAGO`, `precio_plan_legacy`)
- Endpoints retornan `catalogo: true/false` y `oferta_id` cuando aplica

### 4.3 Reglas de Precio Canónicas

| Producto | tipo_linea | Regla |
|----------|------------|-------|
| `CHIP` | cualquiera | `precio_venta = 1`, `modelo_producto` vacío |
| `PACK` | `POSTPAGO` | matriz `modelo_producto + plan_producto` |
| `PACK` | `PREPAGO` | precio fijo por `modelo_producto` |

### 4.4 Trazabilidad Lead → Venta → Postventa

- `BaseLlamada.id_lead` usa `HexUUIDField` (`char(32)`) para compatibilidad MySQL
- FK bidireccional: `BaseLlamada.venta` y `Venta.base_llamada`
- Flujo: `SeguimientoBO` → `EstadoDespacho` → `EstadoCourier`
- `HistorialEstado` registra cambios automáticamente (en progreso)

---

## 5. Migraciones Relevantes

| Migración | App | Descripción |
|-----------|-----|-------------|
| `0011_alter_basellamada_id_lead` | discador | Cambio UUIDField → HexUUIDField |
| `0018_remove_transitory_fields` | ventas | Remover campos transitorios |
| `0019_add_venta_agente` | ventas | Agregar FK agente a Venta |
| `0001_initial` | catalogo | Modelos Oferta, Plan, ModeloProducto |

---

## 6. Comandos Útiles

```bash
# Activar entorno
source venv/bin/activate

# Verificar proyecto
python manage.py check

# Migraciones (solo verificar, no aplicar en producción sin respaldo)
python manage.py makemigrations --check --dry-run

# Aplicar migraciones
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

# Tests
python manage.py test apps.ventas
python manage.py test apps.discador
```

---

## 7. Acceso Rápido a URLs

| URL | Vista |
|-----|-------|
| `/` | Home |
| `/admin/` | Panel admin Django |
| `/users/login/` | Login |
| `/users/dashboard/` | Dashboard usuario |
| `/discador/` | Dashboard agente |
| `/discador/resultados/` | Listado resultados discador |
| `/ventas/` | Listado ventas |
| `/ventas/<uuid>/modal/` | Modal venta vía API |
| `/postventa/` | Dashboard BO |
| `/postventa/despacho/` | Estados de despacho |
| `/postventa/courier/` | Estados de courier |
| `/api/ventas/precio-venta/` | API precio |
| `/api/ventas/validar-producto/` | API validación Producto/Venta |
| `/api/venta/<int:pk>/trazabilidad/` | API trazabilidad |

---

## 8. Configuración y Variables

Archivo `.env` requerido en la raíz:

```env
SECRET_KEY=<django-secret-key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.18.7
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=ventas_porta
DATABASE_USER=root
DATABASE_PASSWORD=<password>
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

---

## 9. Próximos Pasos Sugeridos

1. **Registrar `apps.catalogo`** en `INSTALLED_APPS` cuando el catálogo esté listo para producción
2. **Completar tests estables** para `apps.discador` (actualmente bloqueado por inestabilidad de test database MySQL)
3. **Confirmar portafolio ENTEL 2026** con área comercial
4. **Completar matrices** `PRECIOS_POSTPAGO` y `PRECIOS_PREPAGO` con todos los casos vigentes
5. **Persistencia de HistorialEstado** — integrar `registrar_cambio_estado()` en views de BO, Despacho y Courier

---

## 10. Notas Técnicas

- **Rama única**: Solo existe `master` en local y remoto
- **Historia lineal**: 12 commits desde `06e3932` (Sprint 13) hasta `66542e4` (test API catálogo)
- **Sin conflictos pendientes**: Todos los conflictos de merge del rebase fueron resueltos
- **Working tree limpio**: No hay cambios sin commit
- **Origen actualizado**: `origin/master` apunta a `66542e4`

---

*Generado: 2026-06-21 16:16 (UTC-5)*
