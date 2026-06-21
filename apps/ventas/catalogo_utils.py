from django.apps import apps
from django.db.models import Q
from django.utils import timezone


PLAN_PRECIO_MAP = {
    'ENTEL_CHIP_29_CONTROL': 29,
    'ENTEL_CHIP_39_CONTROL': 39,
    'ENTEL_CHIP_45_CONTROL': 45,
    'ENTEL_CHIP_59_CONTROL': 59,
    'ENTEL_CHIP_74_CONTROL': 74,
    'ENTEL_CHIP_89_CONTROL': 89,
    'ENTEL_CHIP_109_CONTROL': 109,
    'ENTEL_CHIP_145_CONTROL': 145,
    'ENTEL_CONTROL_49_CONTROL': 49,
    'ENTEL_CONTROL_75_CONTROL': 75,
    'ENTEL_CONTROL_99_CONTROL': 99,
    'ENTEL_CONTROL_149_CONTROL': 149,
    'ENTEL_CONTROL_199_CONTROL': 199,
    'ENTEL_75_CONTROL': 75,
    'ENTEL_LIBRE_149_LIBRE': 149,
    'ENTEL_LIBRE_99_LIBRE': 99,
    'PREPAGO': 0,
}


def obtener_oferta_catalogo_para_venta(producto_nombre, modelo, plan, tipo_linea, origen=None):
    if producto_nombre not in {'CHIP', 'PACK'}:
        return None

    if not apps.is_installed('apps.catalogo'):
        return None

    from apps.catalogo.models import Oferta

    today = timezone.localdate()
    qs = (
        Oferta.objects
        .select_related('producto', 'proveedor')
        .filter(activo=True, proveedor__activo=True, producto__activo=True)
        .filter(
            Q(vigencia_desde__isnull=True) | Q(vigencia_desde__lte=today),
            Q(vigencia_hasta__isnull=True) | Q(vigencia_hasta__gte=today),
        )
    )

    if producto_nombre == 'CHIP':
        qs = qs.filter(producto__tipo='CHIP')
    else:
        qs = qs.filter(producto__tipo='EQUIPO', producto__sku=(modelo or '').strip().upper())

    if plan:
        qs = qs.filter(plan_codigo=plan.strip().upper())
    if tipo_linea:
        qs = qs.filter(tipo_linea=tipo_linea.strip().upper())
    if origen:
        qs = qs.filter(origen=origen.strip().upper())

    return qs.order_by('prioridad', 'id').first()


def precio_plan_legacy(plan):
    return PLAN_PRECIO_MAP.get((plan or '').strip().upper())
