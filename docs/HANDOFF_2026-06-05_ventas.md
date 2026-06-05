# HANDOFF — 2026-06-05 · App `ventas`

> Sesión: Seguridad de leads, modal de registro de venta, validación de acceso

---

## Commits aplicados

| Hash | Mensaje |
|------|---------|
| (working tree) | security(ventas): UUID-based lead access + modal register + runtime fixes |

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
- Script JS de búsqueda/validación cliente incluido en parcial compartido

### Modelo Cliente/Venta
- Eliminado: `Cliente.numero`, `Venta.cliente_numero`
- Agregado: `Cliente.tipo_documento`, `Venta.cliente_tipo_documento`
- Migración `0007` aplicada

### Templates
- `venta_form_modal.html` usa parcial compartido `_venta_form_fields.html`
- `venta_form.html` usa mismo parcial (formulario único)
- Scroll habilitado en modal (`max-height: 70vh` + `modal-body-modal`)
- `templates/ventas/_venta_form_fields.html` - parcial compartido con todos los campos del formulario + script JS

---

## Correcciones de runtime aplicadas

1. **Import faltante**: Agregado `CallRecord` en `apps/ventas/views.py`
2. **UUID inconsistencia**: `discador/views.py` ahora guarda `id_lead` (UUID) en sesión en lugar de `id` (entero)
3. **Filtros UUID**: Actualizados queries con `base_llamada__id_lead` donde corresponde
4. **Tests**: Agregado `UserProfile` a setUp, corregidos nombres de campos

---

## Archivos modificados

```
apps/ventas/views.py               ← CallRecord import, UUID fix, supervisor field name
apps/ventas/forms.py               ← base_* campos readonly
apps/ventas/tests.py               ← UserProfile en tests, campos backoffice corregidos
apps/discador/views.py             ← id_lead en sesión, filtros UUID
templates/ventas/_venta_form_fields.html ← script JS agregado
templates/ventas/venta_form.html   ← script movido a parcial
templates/ventas/venta_form_modal.html   ← usa parcial + scroll
templates/discador/agent_dashboard.html   ← modal + scroll CSS
```

---

## Próximos pasos

1. **Tests**: Ejecutar `python manage.py test apps.ventas.tests` (BD requerida)
2. **UI**: Verificar funcionamiento del modal en navegador