# Queries Referenciadas - Campos Retirados del Formulario

## Acciones Completadas

| Campo | Acción | Ubicación Nueva |
|-------|--------|-----------------|
| `contact_callable`, `es_callable`, etc. | Retirado del formulario | Disponible en BaseLlamada via JOIN |
| `fecha_venta`, `hora_venta` | Reemplazado por `creado` | Campo datetime auto-generado |
| Ítems de Venta | Separado en vista independiente | `/ventas/<id>/item/nuevo/` |
| Seguimiento BO | Separado en vista independiente | `/postventa/backoffice/venta/<id>/` |

## Queries para Acceso a Datos (Post-Eliminación)

```python
# Venta con datos del lead y postventa
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'seguimiento_bo', 'estado_despacho', 'estado_courier'
).get(id=venta_id)

# Items de venta
venta.items.all()  # Relación 1:N

# Seguimiento backoffice (usar seguimiento_bo, no backoffice)
venta.seguimiento_bo  # Relación 1:1 - OneToOne

# Estado despacho
venta.estado_despacho  # Relación 1:1 - OneToOne

# Estado courier
venta.estado_courier  # Relación 1:1 - OneToOne
```