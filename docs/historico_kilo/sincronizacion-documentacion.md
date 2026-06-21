# Plan de Acción: Limpieza y Sincronización de Proyecto Ventas_Porta

## Objetivo
Sincronizar la documentación del proyecto (`.kilo/plans/`, `docs/`) con el estado real actual del código, limpiando información obsoleta y garantizando consistencia entre archivos.

---

## Alcance

### Archivos a actualizar
- `.kilo/plans/trazabilidad-lead-venta.md` — Plan de acción
- `docs/documentacion.md` — Documentación principal
- `docs/queries_referenciadas.md` — Queries ORM
- `docs/DEV_REFERENCE.md` — Referencia rápida desarrollador

### Información obsoleta detectada
- Referencia a `SeguimientoBOUpdateView` heredando de `CreateView` (ya fue corregido en Sprint 8)
- Campos inexistentes en API trazabilidad (`status_despacho`/`status_courier` — corregidos a `etapa`/`sts_courier` en Sprint 8)
- `LINEA_NUEVA` listado como operador válido (removido en Sprint 13)
- `calcular_tipo_renta()` con rangos desactualizados (corregidos en Sprint 13)
- Falta reflejar: `BaseLlamada.id` AutoField, `related_name` en FKs, servicios/signals de historial, get_absolute_url() en modelos, arquitectura real con apps separadas (despacho/courier)

---

## Plan de Trabajo

### Paso 1: Actualizar `.kilo/plans/trazabilidad-lead-venta.md`

**Cambios requeridos:**
1. Corregir fechas de Sprint 0-1: eran 2026-06-07, deberían ser 2026-06-05/06 (alinear con HANDOFF docs)
2. Agregar Sprint 13 completado con sus 5 tareas (get_absolute_url, tracking único, VENTA_CONVERTIDA)
3. Agregar sección "Arquitectura de Archivos" con paths reales de apps separadas (apps/despacho, apps/courier)
4. Actualizar tabla de reglas de negocio con nuevas validaciones (Sprint 13)
5. Limpiar referencias a planes futuros marcados como "(planeado)"

**Archivos touch:** `.kilo/plans/trazabilidad-lead-venta.md`

---

### Paso 2: Sincronizar `docs/documentacion.md` con código actual

**Cambios requeridos:**

#### 2.1 Sección 2.1 — BaseLlamada
- Agregar campo `id` AutoField (existe en código, no documentado)
- Actualizar `contact_callable` y `es_callable`: choices son `0/1` no `Sí/No`
- Actualizar `resultado_gestion`: choices son `''/GESTIONADO/VENTA_CONVERTIDA`
- Agregar FK `venta` con `related_name='lead_venta'`

#### 2.2 Sección 2.3 — Venta
- Corregir numeración: eliminar "2.3" duplicada en Cliente
- Actualizar `multiples_lineas` y `tipo_renta2` — existen dos campos (línea 173 duplicada en doc)
- Agregar nota: `LINEA_NUEVA` removido de operadores en Sprint 13
- Actualizar rango `tipo_renta` LINEA_NUEVA/PACK: separar R.BAJA (49-75) y R.MEDIA (76-98)

#### 2.3 Secciones 15-17 — Renumerar y actualizar
- Sección 15: Cambiar fecha a 2026-06-08, marcar relación bidireccional como **implementada** (no "planificada")
- Sección 16: Mover contenido de "Servicio y Signals" antes de "Historial"
- Sección 17: Actualizar reglas de negocio — incluir tracking único, estado courier requiere DESPACHADO
- Sección 18: Cambiar "Próximamente" → "Implementado" para Dashboard Conversión

#### 2.4 Sección 9 — URLs
- Agregar rutas faltantes: `/ventas/<int:venta_id>/item/nuevo/`, rutas de edición postventa
- Remover rutas obsoletas si existen

**Archivos touch:** `docs/documentacion.md`

---

### Paso 3: Sincronizar `docs/queries_referenciadas.md`

**Cambios requeridos:**
1. Cambiar fecha de arquitectura a 2026-06-08
2. Cambiar "Próximamente" → "Implementado" para trazabilidad Lead→Venta
3. Corregir endpoint URL: `/api/venta/<int:pk>/trazabilidad/` (no `{id}`)
4. Actualizar JSON de ejemplo con campos reales del código (`apps/ventas/views.py:342-416`)
5. Agregar query de validación de tracking único entre despacho/courier

**Archivos touch:** `docs/queries_referenciadas.md`

---

### Paso 4: Sincronizar `docs/DEV_REFERENCE.md`

**Cambios requeridos:**
1. Actualizar fecha a 2026-06-08
2. Agregar `HistorialEstado` en tabla de responsabilidades
3. Agregar `get_absolute_url()` en snippets de modelos
4. Actualizar URLs con rutas de edición (`/despacho/venta/<int:pk>/editar/`, etc.)
5. Agregar sección de Servicios y Signals
6. Agregar sección de Validaciones Sprint 13

**Archivos touch:** `docs/DEV_REFERENCE.md`

---

### Paso 5: Limpiar referencias a .kilo/node_modules en .gitignore

**Cambios requeridos:**
- El `.kilo/.gitignore` actual excluye correctamente `node_modules`, `package.json`, etc.
- Verificar que `.gitignore` raíz también excluya `.kilo/node_modules/`

**Archivos touch:** `.gitignore` (solo si falta entrada)

---

## Checklist de Validación

- [ ] `python manage.py check` ejecuta sin errores
- [ ] Todos los paths de archivos mencionados en docs existen en el proyecto
- [ ] Campos de modelos documentados coinciden con `apps/*/models.py`
- [ ] URLs documentadas coinciden con `apps/*/urls.py`
- [ ] No hay referencias a código eliminado o renombrado
- [ ] Fechas consistentes entre `.kilo/plans/`, `docs/HANDOFF_*` y `docs/documentacion.md`
