# Dev Reference - Sistema de Gestión de Ventas

## Flujo de Trabajo del Agente

### Asignación de Leads
1. Agente en `/discador/` obtiene lead aleatorio
2. Lead se guarda en `session['current_lead_id']`
3. Agente puede iniciar llamada (`iniciar_llamada`)

### Registro de Venta
1. Desde dashboard: Click en "Registrar Venta" → abre modal
2. Desde URL directa: `/ventas/nueva/<uuid:id_lead>/`

## API Endpoints

### AJAX Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/ventas/buscar-cliente/` | GET | Busca cliente por tipo_documento + documento |
| `/ventas/validar-cliente/` | GET | Valida existencia de cliente |
| `/ventas/recargar-lead/<uuid:id_lead>/` | GET | Recarga datos del lead |
| `/ventas/modal/<uuid:id_lead>/` | GET | Retorna HTML del formulario modal |
| `/api/ventas/crear/<uuid:id_lead>/` | POST | Crea venta vía API |

### Seguridad

- `id_lead` (UUID): identificador público, difícil de adivinar
- Verificación de acceso: solo usuarios autorizados pueden ver/gestionar leads
- Roles: ADMIN (acceso total), SUPERVISOR (su equipo), AGENTE (solo sus leads)

## Modelos Clave

### Cliente
```python
# Campo eliminado: numero
# Campo agregado: tipo_documento (DNI/RUC/CE/PASAPORTE)
```

### Venta
```python
# Campo eliminado: cliente_numero
# Campo agregado: cliente_tipo_documento
base_llamada = ForeignKey(BaseLlamada, null=True, blank=True)  # FK opcional al lead
```

### BaseLlamada
```python
id_lead = UUIDField(unique=True)  # Identificador público
telefono = CharField(unique=True)   # Teléfono único
```

## Templates

- `venta_form.html`: Formulario completo (standalone)
- `venta_form_modal.html`: Formulario simplificado para modal
- `agent_dashboard.html`: Panel con modal integrado

## JavaScript Functions (agent_dashboard)

```javascript
openVentaModal(id_lead)  // Abre modal de venta
closeVentaModal()        // Cierra modal
confirmReleaseLead()     // Libera lead actual
```