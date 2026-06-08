# HANDOFF — 2026-06-07 · Plan Trazabilidad Lead → Venta

> Sesión: Documentación y planificación del desarrollo de trazabilidad completa

---

## 1. Resumen Ejecutivo

Se ha completado el análisis del proyecto y se ha documentado el plan para completar la trazabilidad del ciclo de vida de un lead (BaseLlamada) hasta su conversión en venta.

---

## 2. Archivos Actualizados

| Archivo | Cambios |
|---------|---------|
| `docs/documentacion.md` | Agregadas secciones 15-19: Trazabilidad, Historial, Validaciones, Dashboard, Reglas de Negocio |
| `docs/queries_referenciadas.md` | Agregadas queries de trazabilidad y estadísticas de conversión |
| `.kilo/plans/trazabilidad-lead-venta.md` | Plan de acción con 5 sprints + bug fix |

---

## 3. Sprints Definidos

| Sprint | Duración | Enfoque |
|--------|----------|---------|
| Sprint 0 | 0.5 día | Bug Fix: Indentación tests |
| Sprint 1 | 0.5 día | FK Venta en BaseLlamada |
| Sprint 2 | 1 día | Historial de estados |
| Sprint 3 | 1 día | Validaciones de flujo |
| Sprint 4 | 0.5 día | Dashboard conversión |
| Sprint 5 | 0.5 día | API trazabilidad |

---

## 4. Arquitectura Objetivo

```
Lead (BaseLlamada)
    │
    ├── Venta (operaciones) → base_llamada_id
    │       │
    │       ├── SeguimientoBO (postventa) → bo_seguimiento
    │       ├── EstadoDespacho (despacho) → despacho_estado
    │       └── EstadoCourier (courier) → courier_estado
    │
    └── Venta (FK inverso - Sprint 1) → lead_origen
```

---

## 5. Queries Clave Actualizadas

```python
# Venta con toda la trazabilidad
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado'
).get(id=venta_id)

# Estadísticas de conversión (Sprint 1)
from django.db.models import Count
stats = BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta')
)
```

---

## 6. Validaciones de Negocio Retail - PENDIENTE

**Requiere confirmación con área comercial:**

1. Modelos de Producto: 48 opciones en `MODELO_PRODUCTO_CHOICES` - ¿Coinciden con catálogo ENTEL 2026?
2. Planes de Producto: 17 opciones - ¿Portafolio vigente?
3. Precio Venta mínimo: 1 (CHIP) - ¿Precio correcto?
4. Precio Venta PACK: 9-699 - ¿Rangos vigentes?
5. Operadores portabilidad: CLARO/MOVISTAR/VIETTEL/VIRGIN - ¿Lista completa?

---

## 7. Próximos Pasos

1. **Confirmar reglas de negocio con área comercial**
2. **Crear branch `feature/trazabilidad-lead-venta`**
3. **Corregir bug de indentación en tests.py (bloqueante)**
4. **Iniciar con Sprint 1: FK Venta en BaseLlamada**

---

## 8. Commands de Inicio

```bash
# Crear branch
git checkout -b feature/trazabilidad-lead-venta

# Verificar estado
python manage.py showmigrations

# Tests (corregir bug primero)
python manage.py test apps.ventas.tests apps.discador.tests --verbosity=2
```

---

## 9. Referencias

- Plan completo: `.kilo/plans/trazabilidad-lead-venta.md`
- Documentación: `docs/documentacion.md` (secciones 15-19)
- Queries: `docs/queries_referenciadas.md`