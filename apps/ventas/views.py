from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.forms import inlineformset_factory
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Venta, ItemVenta, SeguimientoBO, Cliente
from apps.discador.models import BaseLlamada
from .forms import VentaForm, ItemVentaForm, SeguimientoBOForm

ItemVentaFormSet = inlineformset_factory(
    Venta, ItemVenta, form=ItemVentaForm, extra=2, max_num=2, can_delete=False
)


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
    backoffice_form = SeguimientoBOForm()
    
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
        'backoffice_form': backoffice_form,
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
    }, request=request)
    
    return JsonResponse({'ok': True, 'mensaje': '', 'html': html})


@login_required
def venta_api_create(request, id_lead):
    """API endpoint for creating venta - POST only, returns JSON."""
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
    
    form = VentaForm(request.POST)
    
    if form.is_valid():
        venta = form.save(commit=False)
        venta.base_llamada = base
        venta.agente_nombre = request.user.get_full_name() or request.user.username or request.user.email or 'Usuario'
        
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
        
        # Process backoffice
        status_bo = request.POST.get('status_bo', '')
        if status_bo:
            SeguimientoBO.objects.create(
                venta=venta,
                status_bo=status_bo,
                fecha_bo=request.POST.get('fecha_bo') or None,
                sts_courier=request.POST.get('sts_courier', ''),
                fch_courier=request.POST.get('fch_courier') or None,
                supervisor=request.POST.get('supervisor_bo', ''),
                intervalo=request.POST.get('intervalo', '')
            )
        
        messages.success(request, "Venta registrada correctamente.")
        return JsonResponse({'ok': True, 'mensaje': 'Venta registrada correctamente.', 'venta_id': venta.id})
    
    errors = {k: str(v[0]) for k, v in form.errors.items()}
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
                if current_lead_id and base_llamada.id == current_lead_id:
                    return True
            # Allow access if lead hasn't been managed by any other agent
            # This allows initial sale registration before call starts
            other_agent_calls = CallRecord.objects.filter(
                base_llamada=base_llamada
            ).exclude(agente=user).exists()
            return not other_agent_calls
    
    return False


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
            context['backoffice_form'] = SeguimientoBOForm(self.request.POST)
        else:
            context['items_formset'] = ItemVentaFormSet()
            context['backoffice_form'] = SeguimientoBOForm()
        return context

    def form_valid(self, form):
        user = self.request.user
        full_name = (user.get_full_name() or user.username or user.email or 'Usuario').strip()
        if not full_name:
            full_name = user.get_username() or str(user.pk)
        profile = getattr(user, 'profile', None)
        if profile:
            form.instance.agente_nombre = full_name

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

        context = self.get_context_data()
        items_formset = context['items_formset']
        backoffice_form = context['backoffice_form']

        if not (items_formset.is_valid() and backoffice_form.is_valid()):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        items_formset.instance = self.object
        items_formset.save()

        backoffice = backoffice_form.save(commit=False)
        backoffice.venta = self.object
        backoffice.save()

        messages.success(self.request, "Venta registrada correctamente.")
        return redirect(self.success_url)
