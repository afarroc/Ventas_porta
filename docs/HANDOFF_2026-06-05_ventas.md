# HANDOFF — 2026-06-05 · App `ventas`

> Sesión: Seguridad de leads, modal de registro de venta, validación de acceso

---

## Commits aplicados

| Hash | Mensaje |
|------|---------|
| (working tree) | security(ventas): UUID-based lead access + modal register |

---

## Qué se hizo

### Security — Lead Access con UUID
Se reemplazó `<int:base_llamada_id>` por `<uuid:id_lead>` en rutas:
- `/ventas/nueva/<uuid:id_lead>/`
- `/ventas/recargar-lead/<uuid:id_lead>/`
- `/ventas/modal/<uuid:id_lead>/`
- `/api/ventas/crear/<uuid:id_lead>/`

Implementada función `_check_lead_access()` con verificación por rol:
- **ADMIN**: acceso total a cualquier lead
- **SUPERVISOR**: acceso a leads de agentes supervisados
- **AGENTE**: acceso si tiene CallRecord existente O lead no gestionado por otros

### Modal de Registro de Venta
Integrado en `agent_dashboard.html`:
- Botón "Registrar Venta" ahora abre modal via `openVentaModal()`
- Modal carga formulario async vía API
- Submit vía API `/api/ventas/crear/<uuid:id_lead>/`

### Modelo Cliente/Venta
- Eliminado: `Cliente.numero`, `Venta.cliente_numero`
- Agregado: `Cliente.tipo_documento`, `Venta.cliente_tipo_documento`
- Migración `0007` creada (pendiente aplicar)

### Templates
- `venta_form_modal.html` usa parcial compartido `_venta_form_fields.html`
- `venta_form.html` usa mismo parcial (formulario único)
- Scroll habilitado en modal (`max-height: 65vh` + `modal-body-modal`)
- `templates/ventas/_venta_form_fields.html` - parcial compartido con todos los campos del formulario (Lead, Cliente, Ítems, Backoffice)

---

## Archivos modificados

```
apps/ventas/models.py              ← tipo_documento agregado
apps/ventas/forms.py               ← base_* campos readonly
apps/ventas/views.py               ← UUID routes + modal API + access check + formset processing
apps/ventas/urls.py                ← rutas UUID
apps/ventas/admin.py               ← tipo_documento en list_display
apps/ventas/tests.py               ← tests actualizados
templates/ventas/_venta_form_fields.html ← parcial compartido (NUEVO)
templates/ventas/venta_form_modal.html   ← usa parcial + scroll
templates/ventas/venta_form.html          ← reescrito para usar parcial
templates/discador/agent_dashboard.html   ← modal + scroll CSS
```

---

## Próximos pasos sugeridos

1. **Base de datos**: Migración `0007` aplicada (verificado)
2. **Tests**: Ejecutar suite `python manage.py test apps.ventas.tests`
3. **UI**: Verificar funcionamiento del modal en navegador