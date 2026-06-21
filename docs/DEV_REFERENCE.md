# Dev Reference - Sistema de Gestión de Ventas (Actualizado 2026-06-20)

## Estado actual 2026-06-20

- `BaseLlamada.id_lead` usa `HexUUIDField`; en MySQL se almacena como hex `char(32)`.
- `apps.catalogo` está registrada en `INSTALLED_APPS`.
- La integración comercial usa `apps/ventas/catalogo_utils.py`, consulta catálogo primero y mantiene fallback legacy cuando no hay oferta.
- `Venta.base_llamada` apunta a `BaseLlamada`; `BaseLlamada.venta` apunta a `Venta`.
- El related_name de `Venta` hacia `BaseLlamada` es `ventas_asociadas`.

## Índice

1. Arquitectura por Áreas
2. URLs Actualizadas
3. Modelos - Apps Separadas
4. Query Pattern Actualizado
5. Servicios y Signals
6. Validaciones Implementadas

El sistema se organiza por áreas de negocio independientes sobre la misma entidad `Venta`:

```
Lead (BaseLlamada) ────────── discador / WFM
        │
        ▼
    Venta (Operaciones) ──── entrada de venta
        │
        ├── postventa ──── SeguimientoBO (validación, administrativo)
        │
        ├── despacho ──── EstadoDespacho (preparación, tránsito, entrega)
        │
        └── courier ──── EstadoCourier (proveedor, tracking, entrega)
```

**Tabla de responsabilidades por área:**

| Área | Modelo | App | Función |
|------|--------|-----|---------|
| WFM / Discador | BaseLlamada, CallRecord | apps.discador | Gestión de leads, llamadas, bases |
| Operaciones | Venta, ItemVenta, Cliente | apps.ventas | Registro de venta y cliente |
| Postventa (BO) | SeguimientoBO, HistorialEstado | apps.postventa | Validación, seguimiento administrativo |
| Despacho | EstadoDespacho, Proveedor | apps.despacho | Preparación, tránsito, entrega física |
| Courier | EstadoCourier, ProveedorCourier | apps.courier | Estado del proveedor de entrega |

---

## URLs Actualizadas

```
/despacho/proveedores/         → Lista proveedores despacho
/despacho/proveedores/nuevo/   → Crear proveedor despacho
/despacho/venta/<int:venta_id>/ → EstadoDespachoCreateView
/despacho/venta/<int:pk>/editar/ → EstadoDespachoUpdateView

/courier/proveedores/          → Lista proveedores courier
/courier/proveedores/nuevo/    → Crear proveedor courier
/courier/venta/<int:venta_id>/ → EstadoCourierCreateView
/courier/venta/<int:pk>/editar/ → EstadoCourierUpdateView

/postventa/                    → Dashboard BO
/postventa/backoffice/         → Listado consolidado BO
/postventa/backoffice/venta/<int:venta_id>/ → SeguimientoBOCreateView
/postventa/backoffice/<int:pk>/editar/ → SeguimientoBOUpdateView
/postventa/dashboard/conversion/ → DashboardConversionView
```

---

## Modelos - Apps Separadas

### apps.postventa.models
```python
class HistorialEstado(models.Model):
    venta = ForeignKey('ventas.Venta', related_name='historial_estados')
    area = CharField(choices=AREA_CHOICES)  # BO, DESPACHO, COURIER
    estado_anterior = CharField(max_length=50, blank=True)
    estado_nuevo = CharField(max_length=50)
    usuario = ForeignKey(User, null=True, blank=True, related_name='historial_cambios')
    fecha_cambio = DateTimeField(auto_now_add=True)
    observaciones = TextField(blank=True)

class SeguimientoBO(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='bo_seguimiento')
    status_bo = CharField(choices=STATUS_BO_CHOICES, default='PDTE_BO')
    fecha_bo = DateField(null=True, blank=True)
    supervisor = CharField(max_length=150, blank=True)
    observaciones = TextField(blank=True)
    creado = DateTimeField(auto_now_add=True)
    actualizado = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('ventas:venta_detail', kwargs={'pk': self.venta_id})
```

### apps.despacho.models
```python
class Proveedor(models.Model):
    nombre = CharField(max_length=100, unique=True)
    activo = BooleanField(default=True)
    creado = DateTimeField(auto_now_add=True)

class EstadoDespacho(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='despacho_estado')
    etapa = CharField(choices=ETAPA_CHOICES, default='EN_BASE')
    fecha_etapa = DateField(null=True, blank=True)
    proveedor = ForeignKey(Proveedor, null=True, blank=True, related_name='despachos')
    tracking = CharField(max_length=100, blank=True)
    observaciones = TextField(blank=True)
    creado = DateTimeField(auto_now_add=True)
    actualizado = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('ventas:venta_detail', kwargs={'pk': self.venta_id})
```

### apps.courier.models
```python
class ProveedorCourier(models.Model):
    nombre = CharField(max_length=100, unique=True)
    activo = BooleanField(default=True)
    creado = DateTimeField(auto_now_add=True)

class EstadoCourier(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='courier_estado')
    sts_courier = CharField(choices=STS_COURIER_CHOICES, default='PDTE_BO')
    fch_courier = DateField(null=True, blank=True)
    proveedor = ForeignKey(ProveedorCourier, null=True, blank=True, related_name='couriers')
    tracking = CharField(max_length=100, blank=True)
    observaciones = TextField(blank=True)
    creado = DateTimeField(auto_now_add=True)
    actualizado = DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('ventas:venta_detail', kwargs={'pk': self.venta_id})
```

---

## Query Pattern Actualizado

```python
# Obtener venta con información del lead y postventa
venta = Venta.objects.select_related('base_llamada', 'cliente').prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado', 'items', 'historial_estados'
).get(id=venta_id)

# Acceso a datos
venta.bo_seguimiento.status_bo
venta.despacho_estado.etapa
venta.despacho_estado.proveedor.nombre
venta.courier_estado.sts_courier

# Historial de estados
venta.historial_estados.all().order_by('-fecha_cambio')

# Estadísticas de conversión
from django.db.models import Count, Q
stats = BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta', distinct=True),
    sin_venta=Count('id', filter=Q(venta__isnull=True))
).order_by('-total')
```

---

## Servicios y Signals

### apps.postventa.services.py
```python
from apps.postventa.services import registrar_cambio_estado

registrar_cambio_estado(
    venta=venta,
    area='BO',               # BO, DESPACHO, COURIER
    estado_anterior='',
    estado_nuevo='EN_BO',
    usuario=request.user,
    observaciones='Notas'
)
```

### apps.postventa.signals.py
Los signals registran automáticamente cambios en `HistorialEstado`:
- `post_save` en `SeguimientoBO` → área BO
- `post_save` en `EstadoDespacho` → área DESPACHO
- `post_save` en `EstadoCourier` → área COURIER

---

## Validaciones Implementadas (Sprint 13)

1. **Tracking único** (`apps/despacho/views.py`, `apps/courier/views.py`): No duplicar tracking entre despacho y courier de la misma venta.
2. **EstadoDespacho**: Requiere `SeguimientoBO` con `status_bo` en `VALIDADO` o `EN_DESPACHO`.
3. **EstadoCourier**: Requiere `SeguimientoBO` con `status_bo == 'DESPACHADO'`.
4. **VENTA_CONVERTIDA** (`apps/discador/views.py`): Leads con `resultado_gestion == 'VENTA_CONVERTIDA'` no pueden asignarse a agentes.
