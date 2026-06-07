# Dev Reference - Sistema de Gestión de Ventas

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

| Area | Modelo | Función |
|------|--------|---------|
| WFM / Discador | BaseLlamada, CallRecord | Gestion de leads, llamadas, bases |
| Operaciones | Venta, ItemVenta, Cliente | Registro de venta y cliente |
| Postventa (BO) | SeguimientoBO | Validacion, seguimiento administrativo |
| Despacho | EstadoDespacho, Proveedor | Preparacion, transito, entrega fisica |
| Courier | EstadoCourier, Proveedor | Estado del proveedor de entrega |

---

## Flujo de Trabajo del Agente

### Asignacion de Leads
1. Agente en `/discador/` obtiene lead aleatorio
2. Lead se guarda en `session['current_lead_id']`
3. Agente puede iniciar llamada (`iniciar_llamada`)

### Registro de Venta
1. Desde dashboard: Click en "Registrar Venta" → abre modal
2. Desde URL directa: `/ventas/nueva/<uuid:id_lead>/`

## API Endpoints

### AJAX Endpoints

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/ventas/buscar-cliente/` | GET | Busca cliente por tipo_documento + documento |
| `/ventas/validar-cliente/` | GET | Valida existencia de cliente |
| `/ventas/recargar-lead/<uuid:id_lead>/` | GET | Recarga datos del lead |
| `/ventas/modal/<uuid:id_lead>/` | GET | Retorna HTML del formulario modal |
| `/api/ventas/crear/<uuid:id_lead>/` | POST | Crea venta vía API |
| `/ventas/backoffice/` | GET | Listado consolidado postventa |

### Seguridad

- `id_lead` (UUID): identificador público, dificil de adivinar
- Verificacion de acceso: solo usuarios autorizados pueden ver/gestionar leads
- Roles: ADMIN (acceso total), SUPERVISOR (su equipo), AGENTE (solo sus leads)

## Modelos Clave

### Cliente
```python
# Campo eliminado: numero
# Campo agregado: tipo_documento (DNI/RUC/CE/PASAPORTE)
```

### Venta
```python
# Campos agregados: tipo_renta2, multiples_lineas
# base_llamada = ForeignKey(BaseLlamada, null=True, blank=True)  # FK opcional al lead
# tipo_renta = calculado automaticamente segun origen, producto_nombre, precio_venta
# tipo_renta2 = misma logica, para multilinea
```

### BaseLlamada
```python
id_lead = UUIDField(unique=True)
telefono = CharField(unique=True)
base_procedencia = CharField(max_length=20, choices=[('POT','POT'),('RSG_01','RSG_01')])
base_manual = BooleanField(default=False)
```

### Postventa (app separada)
```python
# apps/postventa/models.py

class SeguimientoBO(models.Model):
    venta = OneToOneField('ventas.Venta', on_delete=CASCADE, related_name='seguimiento_bo')
    status_bo = CharField(max_length=30, choices=STATUS_BO_CHOICES, default='PDTE_BO')
    fecha_bo = DateField(null=True, blank=True)
    supervisor = CharField(max_length=150, blank=True)

class EstadoDespacho(models.Model):
    venta = OneToOneField('ventas.Venta', on_delete=CASCADE, related_name='estado_despacho')
    etapa = CharField(max_length=30, choices=ETAPA_CHOICES, default='EN_BASE')
    fecha_etapa = DateField(null=True, blank=True)
    proveedor = ForeignKey(Proveedor, null=True, blank=True)
    tracking = CharField(max_length=100, blank=True)

class EstadoCourier(models.Model):
    venta = OneToOneField('ventas.Venta', on_delete=CASCADE, related_name='estado_courier')
    sts_courier = CharField(max_length=30, choices=STS_COURIER_CHOICES, default='PDTE_BO')
    fch_courier = DateField(null=True, blank=True)
    proveedor = ForeignKey(Proveedor, null=True, blank=True)
    tracking = CharField(max_length=100, blank=True)

class Proveedor(models.Model):
    nombre = CharField(max_length=100, unique=True)
    activo = BooleanField(default=True)
```

## Templates

- `venta_form.html`: Formulario completo (standalone)
- `venta_form_modal.html`: Formulario simplificado para modal
- `agent_dashboard.html`: Panel con modal integrado
- `backoffice_list.html`: Listado consolidado postventa

## JavaScript Functions (agent_dashboard)

```javascript
openVentaModal(id_lead)  // Abre modal de venta
closeVentaModal()        // Cierra modal
confirmReleaseLead()     // Libera lead actual
```

---

## Query Pattern para Datos Unificados

```python
# Obtener venta con informacion del lead y postventa
venta = Venta.objects.select_related('base_llamada', 'cliente').prefetch_related(
    'seguimiento_bo', 'estado_despacho', 'estado_courier', 'items'
).get(id=venta_id)

lead_data = {
    'base_procedencia': venta.base_llamada.base_procedencia,
    'base_manual': venta.base_llamada.base_manual,
    'telefono': venta.base_llamada.telefono,
    'tipo_valido': venta.base_llamada.tipo_valido,
    'resultado_gestion': venta.base_llamada.resultado_gestion,
}
```
