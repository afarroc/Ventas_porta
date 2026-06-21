import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from .models import ChipCompatibilidad, Oferta, Producto


VALID_ORIGENES = {valor for valor, _ in Oferta.ORIGEN_CHOICES}
VALID_TIPOS_LINEA = {valor for valor, _ in Oferta.TIPO_LINEA_CHOICES}


class CatalogoView(LoginRequiredMixin, TemplateView):
    template_name = 'catalogo/catalogo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['origenes'] = Oferta.ORIGEN_CHOICES
        context['tipos_linea'] = Oferta.TIPO_LINEA_CHOICES
        return context


def _request_data(request):
    if request.content_type.startswith('application/json'):
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return {}
    return request.POST.dict()


def _vigente_queryset(qs):
    today = timezone.localdate()
    return qs.filter(
        Q(vigencia_desde__isnull=True) | Q(vigencia_desde__lte=today),
        Q(vigencia_hasta__isnull=True) | Q(vigencia_hasta__gte=today),
    )


def _filter_ofertas(qs, origen=None, tipo_linea=None):
    if origen:
        origen = str(origen).strip().upper()
        if origen not in VALID_ORIGENES:
            raise ValidationError(f'Origen inválido: {origen}')
        qs = qs.filter(origen=origen)
    if tipo_linea:
        tipo_linea = str(tipo_linea).strip().upper()
        if tipo_linea not in VALID_TIPOS_LINEA:
            raise ValidationError(f'Tipo de línea inválido: {tipo_linea}')
        qs = qs.filter(tipo_linea=tipo_linea)
    return _vigente_queryset(qs)


def _serialize_proveedor(proveedor):
    return {'codigo': proveedor.codigo, 'nombre': proveedor.nombre}


def _serialize_producto(producto):
    return {
        'sku': producto.sku,
        'tipo': producto.tipo,
        'marca': producto.marca,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'stock_actual': producto.stock_actual,
        'stock_minimo': producto.stock_minimo,
        'requiere_stock': producto.requiere_stock,
        'activo': producto.activo,
    }


def _serialize_oferta(oferta):
    return {
        'id': oferta.id,
        'producto_sku': oferta.producto.sku,
        'producto_tipo': oferta.producto.tipo,
        'producto_nombre': oferta.producto.nombre,
        'proveedor': _serialize_proveedor(oferta.proveedor),
        'plan_codigo': oferta.plan_codigo,
        'plan_nombre': oferta.plan_nombre,
        'precio_plan_mensual': str(oferta.precio_plan_mensual),
        'precio_equipo': str(oferta.precio_equipo),
        'tipo_linea': oferta.tipo_linea,
        'origen': oferta.origen,
        'meses_contrato': oferta.meses_contrato,
        'prioridad': oferta.prioridad,
        'vigencia_desde': str(oferta.vigencia_desde) if oferta.vigencia_desde else None,
        'vigencia_hasta': str(oferta.vigencia_hasta) if oferta.vigencia_hasta else None,
        'confianza': oferta.confianza,
        'requiere_revision': oferta.requiere_revision,
    }


def _base_ofertas_queryset():
    return (
        Oferta.objects
        .select_related('producto', 'proveedor')
        .filter(activo=True, proveedor__activo=True, producto__activo=True)
        .order_by('prioridad', 'plan_codigo')
    )


@login_required
@require_GET
def catalogo_productos_api(request):
    origen = request.GET.get('origen', '').strip().upper() or None
    tipo_linea = request.GET.get('tipo_linea', '').strip().upper() or None
    buscar = request.GET.get('buscar', '').strip()
    incluir_chips = request.GET.get('incluir_chips', 'false').lower() in {'1', 'true', 'si', 'sí'}

    try:
        ofertas_qs = _filter_ofertas(_base_ofertas_queryset(), origen=origen, tipo_linea=tipo_linea)
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'mensaje': str(exc)}, status=400)

    productos_qs = Producto.objects.filter(activo=True).prefetch_related(
        Prefetch('ofertas', queryset=ofertas_qs, to_attr='ofertas_filtradas')
    )
    if not incluir_chips:
        productos_qs = productos_qs.exclude(tipo='CHIP')

    productos_qs = productos_qs.filter(id__in=ofertas_qs.values('producto_id')).distinct()
    productos = [producto for producto in productos_qs.order_by('tipo', 'marca', 'nombre') if getattr(producto, 'ofertas_filtradas', [])]

    if buscar:
        buscar_lower = buscar.lower()
        resultados = []
        for producto in productos:
            ofertas = list(getattr(producto, 'ofertas_filtradas', []))
            producto_match = (
                buscar_lower in producto.sku.lower()
                or buscar_lower in (producto.marca or '').lower()
                or buscar_lower in producto.nombre.lower()
                or buscar_lower in (producto.descripcion or '').lower()
            )
            ofertas_match = [
                oferta for oferta in ofertas
                if buscar_lower in (oferta.plan_codigo or '').lower()
                or buscar_lower in (oferta.plan_nombre or '').lower()
                or buscar_lower in (oferta.proveedor.codigo or '').lower()
                or buscar_lower in (oferta.proveedor.nombre or '').lower()
            ]
            if producto_match or ofertas_match:
                if not producto_match:
                    producto.ofertas_filtradas = ofertas_match
                resultados.append(producto)
        productos = resultados

    return JsonResponse({
        'ok': True,
        'filtros': {'origen': origen, 'tipo_linea': tipo_linea, 'buscar': buscar, 'incluir_chips': incluir_chips},
        'productos': [_serialize_producto(producto) | {'ofertas': [_serialize_oferta(oferta) for oferta in producto.ofertas_filtradas]} for producto in productos],
    })


@login_required
@require_GET
def ofertas_por_producto_api(request, sku):
    origen = request.GET.get('origen', '').strip().upper() or None
    tipo_linea = request.GET.get('tipo_linea', '').strip().upper() or None
    producto = get_object_or_404(Producto, sku=sku.upper(), activo=True)

    try:
        ofertas_qs = _filter_ofertas(_base_ofertas_queryset().filter(producto=producto), origen=origen, tipo_linea=tipo_linea)
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'mensaje': str(exc)}, status=400)

    return JsonResponse({'ok': True, 'producto': _serialize_producto(producto), 'ofertas': [_serialize_oferta(oferta) for oferta in ofertas_qs]})


@login_required
@require_GET
def chips_compatibles_api(request, sku):
    equipo = get_object_or_404(Producto, sku=sku.upper(), tipo='EQUIPO', activo=True)
    compatibilidades = ChipCompatibilidad.objects.select_related('chip').filter(equipo=equipo, activo=True, chip__activo=True).order_by('chip__marca', 'chip__nombre')

    return JsonResponse({
        'ok': True,
        'equipo': _serialize_producto(equipo),
        'chips': [{
            'sku': compat.chip.sku,
            'tipo': compat.chip.tipo,
            'marca': compat.chip.marca,
            'nombre': compat.chip.nombre,
            'descripcion': compat.chip.descripcion,
            'activo': compat.chip.activo,
        } for compat in compatibilidades],
    })


@login_required
@require_POST
def validar_oferta_api(request):
    data = _request_data(request)
    sku = str(data.get('sku') or data.get('producto_sku') or '').strip().upper()
    oferta_id = data.get('oferta_id')
    origen = str(data.get('origen') or '').strip().upper() or None
    tipo_linea = str(data.get('tipo_linea') or '').strip().upper() or None
    chip_sku = str(data.get('chip_sku') or '').strip().upper() or None

    if not sku:
        return JsonResponse({'ok': False, 'mensaje': 'Falta sku del producto.'}, status=400)

    producto = get_object_or_404(Producto, sku=sku, activo=True)

    try:
        ofertas_qs = _filter_ofertas(_base_ofertas_queryset().filter(producto=producto), origen=origen, tipo_linea=tipo_linea)
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'mensaje': str(exc)}, status=400)

    if oferta_id:
        oferta = get_object_or_404(ofertas_qs, id=oferta_id)
    else:
        oferta = ofertas_qs.first()

    if not oferta:
        return JsonResponse({'ok': False, 'mensaje': f'No hay oferta activa para {producto.sku} con los filtros solicitados.'}, status=404)

    compatible = True
    if producto.tipo == 'EQUIPO' and chip_sku:
        chip = get_object_or_404(Producto, sku=chip_sku, tipo='CHIP', activo=True)
        compatible = ChipCompatibilidad.objects.filter(equipo=producto, chip=chip, activo=True).exists()

    return JsonResponse({
        'ok': compatible,
        'producto': _serialize_producto(producto),
        'oferta': _serialize_oferta(oferta),
        'compatibilidad': {'chip_sku': chip_sku or None, 'compatible': compatible} if producto.tipo == 'EQUIPO' else None,
    })
