# HANDOFF — 2026-06-10 · Refactor Modelo Venta: Eliminación Campos Transitorios

> Sesión: Eliminación de campos redundantes y creación de formulario cliente inline

---

## 1. Cambios Realizados

### Modelo Venta (`apps/ventas/models.py`)

**Campos eliminados (transitorios/redundantes):**
| Campo Eliminado | Razón |
|-----------------|-------|
| `agente_nombre` | Reemplazado por FK `agente` a User |
| `cliente_nombres`, `cliente_paterno`, `cliente_materno` | Ya existe FK `cliente` |
| `cliente_tipo_documento`, `cliente_documento` | Ya existe FK `cliente` |
| `cliente_telefono_1`, `cliente_telefono_2` | Ya existe FK `cliente` |
| `base3`, `q_ventas` | Campos no utilizados |

**Campos agregados/modificados:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `agente` | ForeignKey(User) | Agente que registra la venta (reemplaza `agente_nombre`) |
| `tipo_renta` | CharField(choices=TIPO_RENTA_CHOICES) | R.BAJA/R.MEDIA/R.ALTA - agregado choices |

### Formulario (`apps/ventas/forms.py`)

**Nuevos:**
- `ClienteForm` - Formulario modelo para crear/editar clientes inline

**VentaForm actualizado:**
- Campos cliente como form fields (no model fields) para crear cliente inline
- Excluye `agente` y `cliente` del Meta (se asignan en vistas)
- Lógica de `registrar_nuevo_cliente` validada en `clean()`

### Vistas (`apps/ventas/views.py`)

**Actualizado:**
| Vista | Cambio |
|-------|--------|
| `VentaCreateView` | Asigna `agente = request.user`, crea cliente si no existe |
| `venta_api_create` | Usa `agente = request.user` FK |
| `venta_trazabilidad_api` | Usa `venta.cliente` para datos de cliente |

### Admin (`apps/ventas/admin.py`)

**Actualizado:**
- `list_display`: `agente` en lugar de `agente_nombre`
- `search_fields`: Busca por `agente__username`, `agente__first_name`
- `fieldsets`: Solo muestra `cliente` (no campos duplicados)
- `ItemVentaAdmin`: Busca por `venta__cliente__nombres`

### Template (`templates/ventas/venta_detail.html`)

**Actualizado:**
- Cliente: muestra datos de `venta.cliente` con fallback a campos legacy
- Documento: muestra de `venta.cliente.documento` con fallback
- Agregado campo Agente usando FK `venta.agente`

### Migración (`apps/ventas/migrations/0019_remove_transitory_fields.py`)

Elimina de la base de datos:
- `base3`
- `q_ventas`

---

## 2. Flujo de Registro de Venta

```
1. Usuario abre formulario de venta (desde lead o independiente)
2. Campo documento cliente: busca en BD
   - Si existe → precarga datos cliente
   - Si no existe → marcar "Registrar nuevo cliente" para habilitar campos
3. Validaciones:
   - Documento obligatorio
   - Si registrar_nuevo → nombres y paterno obligatorios
   - Si no registrar → cliente debe existir en BD
4. Al guardar:
   - Se crea cliente (si aplica) o se usa existente
   - Se asigna FK `agente = request.user`
   - Se crea venta con FK `cliente`
```

---

## 3. Próximos Pasos

1. Aplicar migración: `python manage.py migrate`
2. Verificar en admin: Venta con FK agente/cliente
3. Ejecutar tests: `python manage.py test apps.ventas`
4. Validar flujo en navegador: registro de venta con cliente nuevo

---

## 4. Referencias

- Campo `agente` ya existe en BD con nombre `agente_id`
- Cliente con FK `cliente_id` ya existe en tabla `ventas_venta`
- Tests y migración de discador con error `id_lead` (revisar `apps/discador/migrations/0006_changes.py`)