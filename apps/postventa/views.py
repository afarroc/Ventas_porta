from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q

from .models import SeguimientoBO, EstadoDespacho, EstadoCourier, Proveedor
from apps.ventas.models import Venta
from .forms import SeguimientoBOForm, EstadoDespachoForm, EstadoCourierForm, ProveedorForm


class DashboardBOView(LoginRequiredMixin, TemplateView):
    template_name = 'postventa/dashboard_bo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = Venta.objects.select_related('cliente', 'base_llamada').prefetch_related(
            'seguimiento_bo', 'estado_despacho', 'estado_courier'
        )

        bo_qs = SeguimientoBO.objects.all()

        context['total_ventas'] = qs.count()
        context['total_bo'] = bo_qs.count()
        context['pendientes_bo'] = bo_qs.filter(status_bo='PDTE_BO').count()
        context['en_bo'] = bo_qs.filter(status_bo='EN_BO').count()
        context['validados'] = bo_qs.filter(status_bo='VALIDADO').count()
        context['en_despacho'] = bo_qs.filter(status_bo='EN_DESPACHO').count()
        context['despachados'] = bo_qs.filter(status_bo='DESPACHADO').count()

        context['ultimas_ventas'] = qs.order_by('-creado')[:10]

        return context


class BackofficeListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/backoffice_list.html'
    context_object_name = 'ventas'
    paginate_by = 50

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente', 'base_llamada')
            .prefetch_related(
                'seguimiento_bo', 'estado_despacho', 'estado_courier'
            )
            .order_by('-creado')
        )


class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'postventa/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 50


class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'postventa/proveedor_form.html'
    success_url = reverse_lazy('postventa:proveedor_list')


class SeguimientoBOCreateView(LoginRequiredMixin, CreateView):
    model = SeguimientoBO
    form_class = SeguimientoBOForm
    template_name = 'postventa/backoffice_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.venta.pk
        return context

    def form_valid(self, form):
        form.instance.venta = self.venta
        messages.success(self.request, "Seguimiento BO registrado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.venta.pk})


class EstadoDespachoCreateView(LoginRequiredMixin, CreateView):
    model = EstadoDespacho
    form_class = EstadoDespachoForm
    template_name = 'postventa/despacho_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.venta.pk
        return context

    def form_valid(self, form):
        form.instance.venta = self.venta
        messages.success(self.request, "Estado de despacho registrado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.venta.pk})


class EstadoCourierCreateView(LoginRequiredMixin, CreateView):
    model = EstadoCourier
    form_class = EstadoCourierForm
    template_name = 'postventa/courier_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.venta.pk
        return context

    def form_valid(self, form):
        form.instance.venta = self.venta
        messages.success(self.request, "Estado de courier registrado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.venta.pk})
