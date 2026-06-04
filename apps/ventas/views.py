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
    documento = request.GET.get('documento', '').strip()
    if not documento:
        return JsonResponse({'encontrado': False, 'mensaje': 'Ingrese un documento.'})

    try:
        cliente = Cliente.objects.get(documento=documento, activo=True)
        return JsonResponse({
            'encontrado': True,
            'cliente': {
                'documento': cliente.documento,
                'nombres': cliente.nombres or '',
                'paterno': cliente.paterno or '',
                'materno': cliente.materno or '',
                'numero': cliente.numero or '',
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
                'documento': cliente.documento,
                'nombres': cliente.nombres or '',
                'paterno': cliente.paterno or '',
                'materno': cliente.materno or '',
                'numero': cliente.numero or '',
                'telefono_1': cliente.telefono_1 or '',
                'telefono_2': cliente.telefono_2 or '',
            }
        })
    return JsonResponse({'existe': False})


class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta_list')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.base_llamada_id = kwargs.get('base_llamada_id')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'base_llamada_id') and self.base_llamada_id:
            try:
                base_llamada = BaseLlamada.objects.get(pk=self.base_llamada_id)
                # If there's no instance yet (kwargs.get('instance') is None), create one
                if 'instance' not in kwargs or kwargs['instance'] is None:
                    kwargs['instance'] = Venta(base_llamada=base_llamada)
                else:
                    kwargs['instance'].base_llamada = base_llamada
            except BaseLlamada.DoesNotExist:
                pass  # ignore, will proceed without setting base_llamada
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self, 'base_llamada_id') and self.base_llamada_id:
            try:
                base_llamada = BaseLlamada.objects.get(pk=self.base_llamada_id)
                # Try to find an existing Cliente with the same documento
                cliente = Cliente.objects.filter(documento=base_llamada.documento, activo=True).first()
                if cliente:
                    initial['cliente_documento'] = cliente.documento
                    initial['cliente_nombres'] = cliente.nombres
                    initial['cliente_paterno'] = cliente.paterno
                    initial['cliente_materno'] = cliente.materno
                    initial['cliente_numero'] = cliente.numero
                    initial['cliente_telefono_1'] = cliente.telefono_1
                    initial['cliente_telefono_2'] = cliente.telefono_2
                else:
                    # If no existing cliente, use the base_llamada data to pre-fill
                    initial['cliente_documento'] = base_llamada.documento
                    initial['cliente_nombres'] = base_llamada.nombres
                    initial['cliente_paterno'] = base_llamada.paterno
                    initial['cliente_materno'] = base_llamada.materno
                    initial['cliente_numero'] = base_llamada.telefono
                    initial['cliente_telefono_1'] = base_llamada.telefono
                    initial['cliente_telefono_2'] = ''
            except BaseLlamada.DoesNotExist:
                pass
        # Original initial setup for agente_nombre
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
        registrar_nuevo = form.cleaned_data.get('registrar_nuevo_cliente', False)

        if cliente_documento:
            existe = Cliente.objects.filter(documento=cliente_documento, activo=True).first()
            if existe and registrar_nuevo:
                form.instance.cliente = existe
            elif existe:
                form.instance.cliente = existe
            else:
                cliente = Cliente.objects.create(
                    documento=cliente_documento,
                    nombres=form.cleaned_data.get('cliente_nombres', ''),
                    paterno=form.cleaned_data.get('cliente_paterno', ''),
                    materno=form.cleaned_data.get('cliente_materno', ''),
                    numero=form.cleaned_data.get('cliente_numero', ''),
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
