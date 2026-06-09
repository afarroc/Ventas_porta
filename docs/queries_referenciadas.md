# Queries Referenciadas - Separación Apps Despacho/Courier

## Arquitectura Actual (2026-06-08)

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

## Queries de Trazabilidad Lead → Venta (Implementado)

### Lead con Venta Asociada
```python
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

### Endpoint: `/api/venta/<int:pk>/trazabilidad/` (IMPLEMENTADO)

**Método:** GET autenticado  
**Permisos:** `@login_required`

```python
# Ejemplo de llamada
import requests
response = requests.get('/api/venta/123/trazabilidad/', cookies=request.session)
data = response.json()

# Respuesta JSON:
{
    "venta": {
        "id": 123,
        "cliente": "Juan Perez",
        "origen": "PORTABILIDAD",
        "producto": "PACK",
        "precio_venta": "49",
        "tipo_renta": "R.BAJA",
        "creado": "2026-06-01T10:00:00"
    },
    "lead": {
        "id_lead": "uuid-here",
        "telefono": "999888777",
        "nombres": "Juan",
        "paterno": "Perez",
        "documento": "12345678",
        "base_procedencia": "POT",
        "resultado_gestion": "VENTA_CONVERTIDA",
        "fecha_gestion": "2026-06-01"
    },
    "backoffice": {
        "status": "DESPACHADO",
        "supervisor": "Carlos Ruiz",
        "fecha_bo": "2026-06-02",
        "observaciones": "Validado"
    },
    "despacho": {
        "status": "EN_TRANSITO",
        "fecha_despacho": "2026-06-03",
        "observaciones": "En camino"
    },
    "courier": {
        "status": "EN_RUTA",
        "fecha_courier": "2026-06-04",
        "observaciones": "Entrega programada"
    },
    "historial": [
        {
            "area": "BO",
            "estado_anterior": "",
            "estado_nuevo": "PDTE_BO",
            "fecha": "2026-06-01T10:00:00",
            "usuario": "agente1",
            "observaciones": ""
        },
        {
            "area": "BO",
            "estado_anterior": "PDTE_BO",
            "estado_nuevo": "VALIDADO",
            "fecha": "2026-06-02T08:00:00",
            "usuario": "supervisor1",
            "observaciones": "Validado"
        }
    ]
}
```

#### Validación de tracking único por venta
```python
from apps.despacho.models import EstadoDespacho
from apps.courier.models import EstadoCourier

def validar_tracking_unico(venta_id, tracking):
    exists_despacho = EstadoDespacho.objects.filter(
        venta_id=venta_id,
        tracking__iexact=tracking
    ).exists()
    exists_courier = EstadoCourier.objects.filter(
        venta_id=venta_id,
        tracking__iexact=tracking
    ).exists()
    return not (exists_despacho or exists_courier)
```