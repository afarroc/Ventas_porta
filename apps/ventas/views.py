import logging

from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.views.generic.edit import CreateView
from django.forms import inlineformset_factory
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db import transaction
from .models import Venta, ItemVenta, Cliente, PLANES_CHIP, MODELOS_CHIP_LIST
from .catalogo_utils import obtener_oferta_catalogo_para_venta, precio_plan_legacy
from apps.discador.models import BaseLlamada, CallRecord
from apps.users.models import UserProfile
from .forms import VentaForm, ItemVentaForm, ClienteForm
from .ubigeo_peru import DEPTO_CHOICES, PROV_CHOICES, DISTRITOS_CHOICES
from uuid import UUID

ItemVentaFormSet = inlineformset_factory(
    Venta, ItemVenta, form=ItemVentaForm, extra=2, max_num=2, can_delete=False,
)


@require_GET
def get_provincias(request):
    """AJAX endpoint to get provincias by departamento."""
    depto = request.GET.get('departamento', '').strip()
    # Normalizar: si viene nombre en lugar de código, buscar por nombre en DEPTO_CHOICES
    if depto and depto not in PROV_CHOICES:
        for code, nombre in DEPTO_CHOICES:
            if nombre.upper() == depto.upper():
                depto = code
                break
    provincias = PROV_CHOICES.get(depto, [('', 'Seleccione provincia')])
    return JsonResponse({'provincias': provincias})


@require_GET
def get_distritos(request):
    """AJAX endpoint to get distritos by departamento and provincia."""
    depto = request.GET.get('departamento', '').strip()
    provincia = request.GET.get('provincia', '').strip()
    key = f"{depto}_{provincia}"
    distritos = DISTRITOS_CHOICES.get(key, [('', 'Seleccione distrito')])
    return JsonResponse({'distritos': distritos})


@login_required
@require_GET
def obtener_precio_venta_api(request):
    """
    API endpoint para obtener precio.
    Fase 2: consulta primero el catálogo comercial y luego mantiene fallback legacy.
    """
    producto = request.GET.get('producto')
    modelo = request.GET.get('modelo')
    plan = request.GET.get('plan')
    tipo_linea = request.GET.get('tipo_linea')
    origen = request.GET.get('origen')

    if tipo_linea not in ['POSTPAGO', 'PREPAGO']:
        return JsonResponse({'ok': False, 'mensaje': f'Tipo de línea inválido: {tipo_linea}. Debe ser POSTPAGO o PREPAGO.'})

    modelo = (modelo or '').strip()
    if modelo == '0':
        modelo = ''

    if not producto:
        return JsonResponse({'ok': False, 'mensaje': 'Falta el producto'})

    from .models import Venta

    if producto == 'CHIP':
        oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
        if oferta:
            return JsonResponse({'ok': True, 'precio': str(oferta.precio_equipo), 'precio_plan': str(oferta.precio_plan_mensual), 'catalogo': True, 'oferta_id': oferta.id})
        return JsonResponse({'ok': True, 'precio': 1, 'catalogo': False})

    if producto == 'PACK':
        if not modelo:
            return JsonResponse({'ok': False, 'mensaje': 'Falta el modelo'})

        oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
        if oferta:
            return JsonResponse({'ok': True, 'precio': str(oferta.precio_equipo), 'precio_plan': str(oferta.precio_plan_mensual), 'catalogo': True, 'oferta_id': oferta.id})

        if tipo_linea == 'PREPAGO':
            precio = Venta.PRECIOS_PREPAGO.get(modelo)
            if precio is None:
                return JsonResponse({'ok': False, 'mensaje': f'No hay precio prepago definido para {modelo}'})
            return JsonResponse({'ok': True, 'precio': precio, 'catalogo': False})

        if not plan:
            return JsonResponse({'ok': False, 'mensaje': 'Falta el plan'})

        precio = Venta.PRECIOS_POSTPAGO.get((modelo, plan))
        if precio is None:
            return JsonResponse({'ok': False, 'mensaje': f'No hay precio postpago para {modelo} + {plan}'})
        return JsonResponse({'ok': True, 'precio': precio, 'catalogo': False})

    return JsonResponse({'ok': False, 'mensaje': 'Producto inválido'})


@login_required
@require_GET
def validar_producto_venta_api(request):
    """
    API endpoint para validar la sección Producto y Venta completa.
    Retorna precio, precio_plan y tipo_renta calculados si es válido.
    """
    def error(campo, mensaje):
        return JsonResponse({'ok': False, 'campo': campo, 'mensaje': mensaje})

    producto = (request.GET.get('producto') or '').strip()
    origen = (request.GET.get('origen') or '').strip()
    operador = (request.GET.get('operador') or '').strip()
    telefono_portar = ''.join(filter(str.isdigit, (request.GET.get('telefono_portar') or '').strip()))
    modelo = (request.GET.get('modelo') or '').strip()
    if modelo == '0':
        modelo = ''
    plan = (request.GET.get('plan') or '').strip()
    tipo_linea = (request.GET.get('tipo_linea') or '').strip()

    valid_origenes = [valor for valor, _ in Venta.ORIGEN_CHOICES]
    valid_operadores = [valor for valor, _ in Venta.OPERADOR_CHOICES]
    valid_tipos_linea = [valor for valor, _ in Venta.TIPO_LINEA_CHOICES]

    if origen not in valid_origenes:
        return error('origen', 'Seleccione un origen válido.')

    if tipo_linea not in valid_tipos_linea:
        return error('tipo_linea', 'Seleccione tipo de línea (Prepago/Postpago).')

    if origen == 'PORTABILIDAD':
        if operador not in valid_operadores:
            return error('operador', 'Para portabilidad, debe seleccionar un operador válido.')
        if not telefono_portar:
            return error('telefono_portar', 'El teléfono a portar es obligatorio.')
        if len(telefono_portar) < 7 or len(telefono_portar) > 15:
            return error('telefono_portar', 'El teléfono a portar debe tener entre 7 y 15 dígitos.')

    if producto == 'CHIP':
        if modelo:
            return error('modelo_producto', 'Para CHIP no debe seleccionar modelo.')
        if not plan:
            return error('plan_producto', 'Para CHIP debe seleccionar un plan.')

        oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
        if oferta:
            precio = oferta.precio_equipo
            precio_plan = oferta.precio_plan_mensual
        else:
            if plan not in PLANES_CHIP:
                return error('plan_producto', 'Para CHIP, el plan debe ser uno de: ' + ', '.join(PLANES_CHIP))
            precio_plan = precio_plan_legacy(plan)
            if precio_plan is None:
                return error('plan_producto', f'No hay precio definido para el plan {plan}.')
            precio = 1

        try:
            tipo_renta = Venta.calcular_tipo_renta(origen, producto, precio, precio_plan)
        except ValueError as e:
            return error('tipo_renta', str(e))

        return JsonResponse({'ok': True, 'precio': str(precio), 'precio_plan': str(precio_plan), 'tipo_renta': tipo_renta, 'catalogo': bool(oferta), 'oferta_id': oferta.id if oferta else None, 'mensaje': 'Producto CHIP validado correctamente.'})

    if producto == 'PACK':
        if not modelo:
            return error('modelo_producto', 'Para PACK debe seleccionar un modelo de equipo.')
        if modelo in MODELOS_CHIP_LIST:
            return error('modelo_producto', 'El modelo seleccionado es para CHIP, no para PACK.')
        if not plan:
            return error('plan_producto', 'Para PACK debe seleccionar un plan.')

        oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
        if oferta:
            precio = oferta.precio_equipo
            precio_plan = oferta.precio_plan_mensual
        elif tipo_linea == 'PREPAGO':
            precio = Venta.PRECIOS_PREPAGO.get(modelo)
            if precio is None:
                return error('modelo_producto', f'No hay precio prepago definido para {modelo}.')
            precio_plan = precio_plan_legacy(plan) or 0
        elif tipo_linea == 'POSTPAGO':
            precio_plan = precio_plan_legacy(plan)
            if precio_plan is None:
                return error('plan_producto', f'No hay precio definido para el plan {plan}.')
            precio = Venta.PRECIOS_POSTPAGO.get((modelo, plan))
            if precio is None:
                return error('modelo_producto', f'No hay precio postpago para {modelo} + {plan}.')
        else:
            return error('tipo_linea', f'Tipo de línea inválido: {tipo_linea}')

        try:
            tipo_renta = Venta.calcular_tipo_renta(origen, producto, precio, precio_plan)
        except ValueError as e:
            return error('tipo_renta', str(e))

        return JsonResponse({'ok': True, 'precio': str(precio), 'precio_plan': str(precio_plan), 'tipo_renta': tipo_renta, 'catalogo': bool(oferta), 'oferta_id': oferta.id if oferta else None, 'mensaje': 'Producto PACK validado correctamente desde catálogo.' if oferta else 'Producto PACK validado correctamente.'})

    return error('producto_nombre', 'Producto inválido.')


class HomeView(TemplateView):
    template_name = 'home.html'


class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 50


class VentaDetailView(DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'


class BackofficeListView(ListView):
    model = Venta
    template_name = 'ventas/backoffice_list.html'
    context_object_name = 'ventas'
    paginate_by = 50

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente', 'base_llamada')
            .prefetch_related(
                'bo_seguimiento', 'despacho_estado', 'courier_estado'
            )
            .order_by('-creado')
        )


@login_required
@require_GET
def buscar_cliente_ajax(request):
    tipo_documento = request.GET.get('tipo_documento', '').strip()
    documento = request.GET.get('documento', '').strip()
    if not tipo_documento or not documento:
        return JsonResponse({'encontrado': False, 'mensaje': 'Ingrese tipo de documento y número.'})

    try:
        cliente = Cliente.objects.get(tipo_documento=tipo_documento, documento=documento, activo=True)
        return JsonResponse({
            'encontrado': True,
            'cliente': {
                'tipo_documento': cliente.tipo_documento,
                'documento': cliente.documento,
                'nombres': cliente.nombres or '',
                'paterno': cliente.paterno or '',
                'materno': cliente.materno or '',
                'telefono_1': cliente.telefono_1 or '',
                'telefono_2': cliente.telefono_2 or '',
            }
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'encontrado': False, 'mensaje': 'Cliente no encontrado.'})


@login_required
def registrar_cliente_ajax(request, id_lead):
    """API endpoint for registering a new cliente without creating venta."""
    from uuid import UUID
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'mensaje': 'Método no permitido.'})
    
    try:
        UUID(str(id_lead))
    except ValueError:
        return JsonResponse({'ok': False, 'mensaje': 'ID de lead inválido.'})
    
    try:
        base = BaseLlamada.objects.get(id_lead=id_lead)
    except BaseLlamada.DoesNotExist:
        return JsonResponse({'ok': False, 'mensaje': 'Lead no encontrado.'})
    
    if not _check_lead_access(request.user, base, request.session):
        return JsonResponse({'ok': False, 'mensaje': 'No tiene acceso a este lead.'})
    
    tipo_documento = request.POST.get('cliente_tipo_documento', 'DNI').strip()
    documento = request.POST.get('cliente_documento', '').strip()
    nombres = request.POST.get('cliente_nombres', '').strip()
    paterno = request.POST.get('cliente_paterno', '').strip()
    materno = request.POST.get('cliente_materno', '').strip()
    telefono_1 = request.POST.get('cliente_telefono_1', '').strip()
    telefono_2 = request.POST.get('cliente_telefono_2', '').strip()
    
    if not documento:
        return JsonResponse({'ok': False, 'mensaje': 'El documento es obligatorio.'})
    if not nombres:
        return JsonResponse({'ok': False, 'mensaje': 'Los nombres son obligatorios.'})
    if not paterno:
        return JsonResponse({'ok': False, 'mensaje': 'El apellido paterno es obligatorio.'})
    
    cliente_existe = Cliente.objects.filter(documento=documento, activo=True).first()
    if cliente_existe:
        return JsonResponse({
            'ok': True,
            'mensaje': 'Cliente ya existe en la base de datos.',
            'cliente_id': cliente_existe.id
        })
    
    cliente = Cliente.objects.create(
        tipo_documento=tipo_documento,
        documento=documento,
        nombres=nombres,
        paterno=paterno,
        materno=materno,
        telefono_1=telefono_1,
        telefono_2=telefono_2,
        activo=True,
    )
    
    return JsonResponse({
        'ok': True,
        'mensaje': 'Cliente registrado correctamente.',
        'cliente_id': cliente.id
    })


@login_required
@require_GET
def validar_cliente_ajax(request):
    documento = request.GET.get('documento', '').strip()
    if not documento:
        return JsonResponse({'existe': False})

    cliente = Cliente.objects.filter(documento=documento, activo=True).first()
    if cliente:
        return JsonResponse({
            'existe': True,
            'cliente': {
                'tipo_documento': cliente.tipo_documento,
                'documento': cliente.documento,
                'nombres': cliente.nombres or '',
                'paterno': cliente.paterno or '',
                'materno': cliente.materno or '',
                'telefono_1': cliente.telefono_1 or '',
                'telefono_2': cliente.telefono_2 or '',
            }
        })
    return JsonResponse({'existe': False})


@login_required
@require_GET
def recargar_lead_ajax(request, id_lead):
    from apps.users.models import UserProfile
    from uuid import UUID
    
    try:
        UUID(str(id_lead))
    except ValueError:
        return JsonResponse({'ok': False, 'mensaje': 'ID de lead inválido.'})
    
    try:
        base = BaseLlamada.objects.get(id_lead=id_lead)
    except BaseLlamada.DoesNotExist:
        return JsonResponse({'ok': False, 'mensaje': 'Lead no encontrado.'})
    
    if not _check_lead_access(request.user, base, request.session):
        return JsonResponse({'ok': False, 'mensaje': 'No tiene acceso a este lead.'})
    
    return JsonResponse({
        'ok': True,
        'lead': {
            'tipo_documento': 'DNI',
            'telefono': base.telefono or '',
            'nombres': base.nombres or '',
            'paterno': base.paterno or '',
            'materno': base.materno or '',
            'correo': base.correo or '',
            'documento': base.documento or '',
            'observaciones': base.observaciones or '',
        }
    })


@login_required
def venta_modal_partial(request, id_lead):
    """Returns the sale form as HTML for modal display in agent dashboard."""
    from uuid import UUID
    from django.template.loader import render_to_string
    
    try:
        UUID(str(id_lead))
    except ValueError:
        return JsonResponse({'ok': False, 'mensaje': 'ID de lead inválido.', 'html': ''})
    
    try:
        base = BaseLlamada.objects.get(id_lead=id_lead)
    except BaseLlamada.DoesNotExist:
        return JsonResponse({'ok': False, 'mensaje': 'Lead no encontrado.', 'html': ''})
    
    if not _check_lead_access(request.user, base, request.session):
        return JsonResponse({'ok': False, 'mensaje': 'No tiene acceso a este lead.', 'html': ''})
    
    user = request.user
    full_name = user.get_full_name() or user.username or user.email or 'Usuario'
    
    cliente = Cliente.objects.filter(documento=base.documento, activo=True).first()
    
    form = VentaForm(initial={
        'cliente_tipo_documento': cliente.tipo_documento if cliente else 'DNI',
        'cliente_documento': (cliente.documento if cliente else base.documento) or '',
        'cliente_nombres': (cliente.nombres if cliente else base.nombres) or '',
        'cliente_paterno': (cliente.paterno if cliente else base.paterno) or '',
        'cliente_materno': (cliente.materno if cliente else base.materno) or '',
        'cliente_telefono_1': (cliente.telefono_1 if cliente else base.telefono) or '',
        'cliente_telefono_2': cliente.telefono_2 if cliente else '',
        'registrar_nuevo_cliente': not bool(cliente),
    })
    
    items_formset = ItemVentaFormSet()
    
    profile = getattr(user, 'profile', None)
    supervisor_name = '-'
    if profile and getattr(profile, 'supervisor', None):
        sup = profile.supervisor
        supervisor_name = sup.user.get_full_name() or sup.user.username or str(sup.pk)
        if sup.codigo_agente:
            supervisor_name = f"{supervisor_name} ({sup.codigo_agente})"
    
    html = render_to_string('ventas/venta_form_modal.html', {
        'form': form,
        'items_formset': items_formset,
        'base_llamada_id': str(base.id_lead),
        'base_llamada_telefono': base.telefono or '',
        'base_llamada_nombres': base.nombres or '',
        'base_llamada_paterno': base.paterno or '',
        'base_llamada_materno': base.materno or '',
        'base_llamada_documento': base.documento or '',
        'base_llamada_correo': base.correo or '',
        'base_llamada_observaciones': base.observaciones or '',
        'agente_nombre_auto': full_name,
        'supervisor_nombre_auto': supervisor_name,
        'departamentos': DEPTO_CHOICES,
    }, request=request)
    
    return JsonResponse({'ok': True, 'mensaje': '', 'html': html})


@login_required
def venta_api_create(request, id_lead):
    """API endpoint for creating venta - POST only, returns JSON."""
    from uuid import UUID
    from django.db import transaction
    from django.conf import settings
    
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'mensaje': 'Método no permitido.'})
    
    try:
        UUID(str(id_lead))
    except ValueError:
        return JsonResponse({'ok': False, 'mensaje': 'ID de lead inválido.'})
    
    try:
        base = BaseLlamada.objects.get(id_lead=id_lead)
    except BaseLlamada.DoesNotExist:
        return JsonResponse({'ok': False, 'mensaje': 'Lead no encontrado.'})
    
    if not _check_lead_access(request.user, base, request.session):
        return JsonResponse({'ok': False, 'mensaje': 'No tiene acceso a este lead.'})
    
    form = VentaForm(request.POST)
    
    if form.is_valid():
        try:
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.base_llamada = base
                venta.agente = request.user
                
                cliente_documento = form.cleaned_data.get('cliente_documento')
                cliente_tipo_documento = form.cleaned_data.get('cliente_tipo_documento', 'DNI')
                
                if cliente_documento:
                    cliente = Cliente.objects.filter(documento=cliente_documento, activo=True).first()
                    if cliente:
                        venta.cliente = cliente
                    else:
                        cliente = Cliente.objects.create(
                            tipo_documento=cliente_tipo_documento,
                            documento=cliente_documento,
                            nombres=form.cleaned_data.get('cliente_nombres', ''),
                            paterno=form.cleaned_data.get('cliente_paterno', ''),
                            materno=form.cleaned_data.get('cliente_materno', ''),
                            telefono_1=form.cleaned_data.get('cliente_telefono_1', ''),
                            telefono_2=form.cleaned_data.get('cliente_telefono_2', ''),
                            activo=True,
                        )
                        venta.cliente = cliente
                
                venta.save()
                
                # Process items formset
                items_total = int(request.POST.get('items-TOTAL_FORMS', 0))
                for i in range(items_total):
                    tipo_venta = request.POST.get(f'items-{i}-tipo_venta', '')
                    tipo_producto = request.POST.get(f'items-{i}-tipo_producto', '')
                    precio_plan = request.POST.get(f'items-{i}-precio_plan', '')
                    if tipo_venta or tipo_producto:
                        ItemVenta.objects.create(
                            venta=venta,
                            tipo_venta=tipo_venta,
                            tipo_producto=tipo_producto,
                            precio_plan=precio_plan if precio_plan else None
                        )
            
            messages.success(request, "Venta registrada correctamente.")
            return JsonResponse({'ok': True, 'mensaje': 'Venta registrada correctamente.', 'venta_id': venta.id})
        except Exception as e:
            logger.exception("Error creating venta API")
            if request.user.is_staff or request.user.is_superuser:
                return JsonResponse({'ok': False, 'mensaje': f'Error: {str(e)}'})
            return JsonResponse({'ok': False, 'mensaje': 'Error interno al guardar la venta.'})
            return JsonResponse({'ok': False, 'mensaje': 'Error interno al guardar la venta.'})
    
    errors = {k: str(v[0]) for k, v in form.errors.items()}
    logger.warning(f"VentaForm errors: {errors}")
    return JsonResponse({'ok': False, 'mensaje': 'Error en el formulario.', 'errores': errors})


def _check_lead_access(user, base_llamada, session=None):
    """Check if user has access to the lead via assigned CallRecord or session.
    
    Para AGENTE: Permite acceso si:
    - Tiene un CallRecord existente para este lead, O
    - El lead está en su sesión actual, O
    - El lead no ha sido gestionado por ningún otro agente (registro inicial)
    """
    from apps.users.models import UserProfile
    
    if not user.is_authenticated:
        return False
    
    profile = getattr(user, 'profile', None)
    if profile:
        if profile.rol == UserProfile.ROL_ADMIN:
            return True
        elif profile.rol == UserProfile.ROL_SUPERVISOR:
            supervised_ids = UserProfile.objects.filter(supervisor__user=user).values_list('user_id', flat=True)
            supervised_ids = list(supervised_ids) + [user.id]
            return CallRecord.objects.filter(
                base_llamada=base_llamada, agente__in=supervised_ids
            ).exists()
        else:  # AGENTE
            has_record = CallRecord.objects.filter(
                base_llamada=base_llamada, agente=user
            ).exists()
            if has_record:
                return True
            if session:
                current_lead_id = session.get('current_lead_id')
                if current_lead_id and base_llamada.id_lead == current_lead_id:
                    return True
            # Allow access if lead hasn't been managed by any other agent
            # This allows initial sale registration before call starts
            other_agent_calls = CallRecord.objects.filter(
                base_llamada=base_llamada
            ).exclude(agente=user).exists()
            return not other_agent_calls
    
    return False


@login_required
@require_GET
def venta_trazabilidad_api(request, pk):
    """API endpoint que retorna la trazabilidad completa de una venta."""
    from apps.postventa.models import HistorialEstado, SeguimientoBO
    from apps.despacho.models import EstadoDespacho
    from apps.courier.models import EstadoCourier
    
    venta = get_object_or_404(Venta, pk=pk)
    
    data = {
        'venta': {
            'id': venta.id,
            'cliente': f"{venta.cliente.nombres} {venta.cliente.paterno}" if venta.cliente else None,
            'origen': venta.origen,
            'producto': venta.producto_nombre,
            'precio_venta': str(venta.precio_venta) if venta.precio_venta else None,
            'tipo_renta': venta.tipo_renta,
            'creado': venta.creado.isoformat() if venta.creado else None,
        },
        'lead': None,
        'backoffice': None,
        'despacho': None,
        'courier': None,
        'historial': [],
    }
    
    if venta.base_llamada:
        base = venta.base_llamada
        data['lead'] = {
            'id_lead': str(base.id_lead),
            'telefono': base.telefono,
            'nombres': base.nombres,
            'paterno': base.paterno,
            'documento': base.documento,
            'base_procedencia': base.base_procedencia,
            'resultado_gestion': base.resultado_gestion,
            'fecha_gestion': base.fecha_gestion.isoformat() if base.fecha_gestion else None,
        }
    
    bo = getattr(venta, 'bo_seguimiento', None)
    if bo:
        data['backoffice'] = {
            'status': bo.status_bo,
            'supervisor': bo.supervisor,
            'fecha_bo': bo.fecha_bo.isoformat() if bo.fecha_bo else None,
            'observaciones': bo.observaciones,
        }
    
    despacho = getattr(venta, 'despacho_estado', None)
    if despacho:
        data['despacho'] = {
            'status': despacho.etapa,
            'fecha_despacho': despacho.fecha_etapa.isoformat() if despacho.fecha_etapa else None,
            'observaciones': despacho.observaciones,
        }
    
    courier = getattr(venta, 'courier_estado', None)
    if courier:
        data['courier'] = {
            'status': courier.sts_courier,
            'fecha_courier': courier.fch_courier.isoformat() if courier.fch_courier else None,
            'observaciones': courier.observaciones,
        }
    
    historial = HistorialEstado.objects.filter(venta=venta).order_by('-fecha_cambio')
    for h in historial:
        data['historial'].append({
            'area': h.area,
            'estado_anterior': h.estado_anterior,
            'estado_nuevo': h.estado_nuevo,
            'fecha': h.fecha_cambio.isoformat() if h.fecha_cambio else None,
            'usuario': h.usuario.username if h.usuario else None,
            'observaciones': h.observaciones,
        })
    
    return JsonResponse(data)


class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.base_llamada = None
        self.request = request
        id_lead = kwargs.get('id_lead')
        if id_lead:
            try:
                from uuid import UUID
                UUID(str(id_lead))
                self.base_llamada = BaseLlamada.objects.get(id_lead=id_lead)
            except (ValueError, BaseLlamada.DoesNotExist):
                pass

    def dispatch(self, request, *args, **kwargs):
        if self.base_llamada and not _check_lead_access(request.user, self.base_llamada, request.session):
            messages.error(request, "No tiene acceso a este lead.")
            return redirect('ventas:venta_list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.base_llamada:
            kwargs['instance'] = Venta(base_llamada=self.base_llamada)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.base_llamada:
            cliente = Cliente.objects.filter(documento=self.base_llamada.documento, activo=True).first()
            if cliente:
                initial['cliente_tipo_documento'] = cliente.tipo_documento
                initial['cliente_documento'] = cliente.documento
                initial['cliente_nombres'] = cliente.nombres
                initial['cliente_paterno'] = cliente.paterno
                initial['cliente_materno'] = cliente.materno
                initial['cliente_telefono_1'] = cliente.telefono_1
                initial['cliente_telefono_2'] = cliente.telefono_2
            else:
                initial['cliente_documento'] = self.base_llamada.documento
                initial['cliente_nombres'] = self.base_llamada.nombres
                initial['cliente_paterno'] = self.base_llamada.paterno
                initial['cliente_materno'] = self.base_llamada.materno
                initial['cliente_telefono_1'] = self.base_llamada.telefono
                initial['cliente_telefono_2'] = ''
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if profile:
            full_name = user.get_full_name() or user.username
            initial['agente_nombre'] = full_name
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        full_name = (user.get_full_name() or user.username or user.email or 'Usuario').strip()
        if not full_name:
            full_name = user.get_username() or str(user.pk)
        context['agente_nombre_auto'] = full_name
        context['departamentos'] = DEPTO_CHOICES

        profile = getattr(user, 'profile', None)
        supervisor_name = '-'
        if profile and getattr(profile, 'supervisor', None):
            sup = profile.supervisor
            supervisor_name = sup.user.get_full_name() or sup.user.username or str(sup.pk)
            if sup.codigo_agente:
                supervisor_name = f"{supervisor_name} ({sup.codigo_agente})"
        context['supervisor_nombre_auto'] = supervisor_name

        if self.base_llamada:
            context['base_llamada_id'] = str(self.base_llamada.id_lead)
            context['base_llamada_telefono'] = self.base_llamada.telefono
            context['base_llamada_nombres'] = self.base_llamada.nombres
            context['base_llamada_paterno'] = self.base_llamada.paterno
            context['base_llamada_materno'] = self.base_llamada.materno
            context['base_llamada_correo'] = self.base_llamada.correo
            context['base_llamada_documento'] = self.base_llamada.documento
            context['base_llamada_observaciones'] = self.base_llamada.observaciones
        else:
            context['base_llamada_id'] = None

        if self.request.POST:
            context['items_formset'] = ItemVentaFormSet(self.request.POST)
        else:
            context['items_formset'] = ItemVentaFormSet()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            user = self.request.user
            form.instance.agente = user

            cliente_documento = form.cleaned_data.get('cliente_documento')
            cliente_tipo_documento = form.cleaned_data.get('cliente_tipo_documento', 'DNI')
            registrar_nuevo = form.cleaned_data.get('registrar_nuevo_cliente', False)

            if cliente_documento:
                existe = Cliente.objects.filter(documento=cliente_documento, activo=True).first()
                if existe and registrar_nuevo:
                    form.instance.cliente = existe
                elif existe:
                    form.instance.cliente = existe
                else:
                    cliente = Cliente.objects.create(
                        tipo_documento=cliente_tipo_documento,
                        documento=cliente_documento,
                        nombres=form.cleaned_data.get('cliente_nombres', ''),
                        paterno=form.cleaned_data.get('cliente_paterno', ''),
                        materno=form.cleaned_data.get('cliente_materno', ''),
                        telefono_1=form.cleaned_data.get('cliente_telefono_1', ''),
                        telefono_2=form.cleaned_data.get('cliente_telefono_2', ''),
                        activo=True,
                    )
                    form.instance.cliente = cliente

            self.object = form.save()
        messages.success(self.request, "Venta registrada correctamente.")
        return redirect(self.success_url)


# ========================
# Vistas separadas para Backoffice
# ========================

class ItemVentaCreateView(LoginRequiredMixin, CreateView):
    model = ItemVenta
    form_class = ItemVentaForm
    template_name = 'ventas/item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.kwargs['venta_id']
        return context

    def form_valid(self, form):
        form.instance.venta_id = self.kwargs['venta_id']
        return super().form_valid()

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.kwargs['venta_id']})
