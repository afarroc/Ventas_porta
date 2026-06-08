# Queries Referenciadas - Separación Apps Despacho/Courier

## Arquitectura Actual (2026-06-07)

```
Venta (Operaciones)
    │
    ├── Postventa/Backoffice → apps.postventa.models.SeguimientoBO
    ├── Despacho → apps.despacho.models.EstadoDespacho
    └── Courier → apps.courier.models.EstadoCourier
```

## Queries para Acceso a Datos

```python
# Venta con datos del lead y postventa (con nuevos related_name)
venta = Venta.objects.select_related('base_llamada', 'cliente').prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado'
).get(id=venta_id)

# Items de venta
venta.items.all()  # Relación 1:N

# Seguimiento backoffice (postventa)
venta.bo_seguimiento  # Relación 1:1 - OneToOne

# Estado despacho
venta.despacho_estado  # Relación 1:1 - OneToOne

# Estado courier
venta.courier_estado  # Relación 1:1 - OneToOne
```

## Acceso a Proveedores

```python
# Proveedor de despacho
venta.despacho_estado.proveedor.nombre  # Nombre del proveedor

# Proveedor courier  
venta.courier_estado.proveedor.nombre  # Nombre del proveedor
```

## Queries por Área

### Backoffice
```python
from apps.postventa.models import SeguimientoBO
bo = SeguimientoBO.objects.filter(status_bo='PDTE_BO')
```

### Despacho
```python
from apps.despacho.models import EstadoDespacho, Proveedor
despachos = EstadoDespacho.objects.select_related('proveedor').filter(etapa='EN_PREPARACION')
proveedores = Proveedor.objects.filter(activo=True)
```

### Courier
```python
from apps.courier.models import EstadoCourier, ProveedorCourier
couriers = EstadoCourier.objects.select_related('proveedor').filter(sts_courier='EN_RUTA')
proveedores_courier = ProveedorCourier.objects.filter(activo=True)
```

---

## Queries de Trazabilidad Lead → Venta (Próximamente)

### Lead con Venta Asociada
```python
# Una vez implementado BaseLlamada.venta
base = BaseLlamada.objects.select_related('venta').prefetch_related(
    'venta__bo_seguimiento',
    'venta__despacho_estado',
    'venta__courier_estado'
).get(id_lead=uuid_val)

if base.venta:
    print(f"Venta ID: {base.venta.id}")
    print(f"Estado BO: {base.venta.bo_seguimiento.status_bo}")
```

### Estadísticas de Conversión
```python
from django.db.models import Count, Q

# Tasa de conversión por base de procedencia
stats = BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta', distinct=True),
    sin_venta=Count('id', filter=Q(venta__isnull=True))
).order_by('-total')

# Ventas con estado completo del flujo
from apps.ventas.models import Venta
ventas_flujo = Venta.objects.filter(
    bo_seguimiento__status_bo='DESPACHADO'
).select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'despacho_estado', 'courier_estado'
)
```

---

## API Endpoints - Trazabilidad

### Endpoint: `/api/venta/{id}/trazabilidad/` (IMPLEMENTADO)

```python
# Retorna JSON con toda la trazabilidad
{
    "venta": {
        "id": 123,
        "cliente": "...",
        "origen": "...",
        "producto": "...",
        "precio_venta": "...",
        "tipo_renta": "...",
        "creado": "..."
    },
    "lead": {
        "id_lead": "...",
        "telefono": "...",
        "nombres": "...",
        "documento": "...",
        "base_procedencia": "...",
        "resultado_gestion": "..."
    },
    "backoffice": {
        "status": "...",
        "supervisor": "...",
        "fecha_bo": "..."
    },
    "despacho": {...},
    "courier": {...},
    "historial": [...]
}
```

**Método:** GET autenticado  
**Permisos:** `@login_required`

```python
# Retorna JSON con toda la trazabilidad
{
    "venta": {
        "id": 123,
        "agente_nombre": "...",
        "cliente": {...}
    },
    "lead": {
        "id_lead": "...",
        "telefono": "...",
        "base_procedencia": "..."
    },
    "postventa": {
        "bo": {"status_bo": "...", "fecha_bo": "..."},
        "despacho": {"etapa": "...", "tracking": "..."},
        "courier": {"sts_courier": "...", "tracking": "..."}
    },
    "historial": [
        {"area": "BO", "estado_anterior": "EN_BO", "estado_nuevo": "VALIDADO", "fecha": "..."},
        ...
    ]
}
```