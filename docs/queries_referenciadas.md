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
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
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
venta.despacho_estado.proveedor  # Nombre del proveedor

# Proveedor courier  
venta.courier_estado.proveedor  # Nombre del proveedor
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