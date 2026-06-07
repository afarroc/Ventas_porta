# Dev Reference - Sistema de Gestión de Ventas (Actualizado 2026-06-07)

## Arquitectura por Areas

El sistema se organiza por areas de negocio independientes sobre la misma entidad `Venta`:

```
Lead (BaseLlamada) ────────── discador / WFM
       │
       Venta (Operaciones) ──── entrada de venta
       │
       ├── postventa ──── SeguimientoBO (validación, administrativo)
       │
       ├── despacho ──── EstadoDespacho (preparación, tránsito, entrega)
       │
       └── courier ──── EstadoCourier (proveedor, tracking, entrega)
```

**Tabla de responsabilidades por area:**

| Area | Modelo | App | Función |
|------|--------|-----|---------|
| WFM / Discador | BaseLlamada, CallRecord | apps.discador | Gestion de leads, llamadas, bases |
| Operaciones | Venta, ItemVenta, Cliente | apps.ventas | Registro de venta y cliente |
| Postventa (BO) | SeguimientoBO | apps.postventa | Validacion, seguimiento administrativo |
| Despacho | EstadoDespacho, Proveedor | apps.despacho | Preparacion, transito, entrega fisica |
| Courier | EstadoCourier, ProveedorCourier | apps.courier | Estado del proveedor de entrega |

---

## URLs Actualizadas

```
/despacho/proveedores/         → Lista proveedores despacho
/despacho/proveedores/nuevo/   → Crear proveedor despacho
/despacho/venta/<id>/          → EstadoDespacho formulario

/courier/proveedores/          → Lista proveedores courier  
/courier/proveedores/nuevo/    → Crear proveedor courier
/courier/venta/<id>/           → EstadoCourier formulario

/postventa/                    → Dashboard BO
/postventa/backoffice/         → Listado consolidado BO
/postventa/backoffice/venta/<id>/ → SeguimientoBO formulario
```

---

## Modelos - App Separdas

### apps.postventa.models
```python
class SeguimientoBO(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='bo_seguimiento')
    status_bo = CharField(choices=STATUS_BO_CHOICES, default='PDTE_BO')
    fecha_bo = DateField(null=True, blank=True)
    supervisor = CharField(max_length=150, blank=True)
```

### apps.despacho.models
```python
class Proveedor(models.Model):
    nombre = CharField(max_length=100, unique=True)
    activo = BooleanField(default=True)

class EstadoDespacho(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='despacho_estado')
    etapa = CharField(choices=ETAPA_CHOICES)
    proveedor = ForeignKey(Proveedor, null=True, blank=True)
    tracking = CharField(max_length=100, blank=True)
```

### apps.courier.models
```python
class ProveedorCourier(models.Model):
    nombre = CharField(max_length=100, unique=True)

class EstadoCourier(models.Model):
    venta = OneToOneField('ventas.Venta', related_name='courier_estado')
    sts_courier = CharField(choices=STS_COURIER_CHOICES)
```

---

## Query Pattern Actualizado

```python
# Obtener venta con informacion del lead y postventa
venta = Venta.objects.select_related('base_llamada', 'cliente').prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado', 'items'
).get(id=venta_id)

# Acceso a datos
venta.bo_seguimiento.status_bo
venta.despacho_estado.etapa
venta.despacho_estado.proveedor.nombre
venta.courier_estado.sts_courier
```