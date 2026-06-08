from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q, F

from .models import SeguimientoBO, HistorialEstado
from apps.ventas.models import Venta
from apps.discador.models import BaseLlamada
from .forms import SeguimientoBOForm


class DashboardBOView(LoginRequiredMixin, ListView):
    template_name = 'postventa/dashboard_bo.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente', 'base_llamada')
            .prefetch_related(
                'bo_seguimiento', 'despacho_estado', 'courier_estado'
            )
            .order_by('-creado')[:10]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bo_qs = SeguimientoBO.objects.all()

        context['total_ventas'] = Venta.objects.count()
        context['total_bo'] = bo_qs.count()
        context['pendientes_bo'] = bo_qs.filter(status_bo='PDTE_BO').count()
        context['en_bo'] = bo_qs.filter(status_bo='EN_BO').count()
        context['validados'] = bo_qs.filter(status_bo='VALIDADO').count()
        context['en_despacho'] = bo_qs.filter(status_bo='EN_DESPACHO').count()
        context['despachados'] = bo_qs.filter(status_bo='DESPACHADO').count()

        return context


class DashboardConversionView(LoginRequiredMixin, ListView):
    template_name = 'postventa/dashboard_conversion.html'
    context_object_name = 'stats_por_base'

    def get_queryset(self):
        # Estadísticas de conversión por base de procedencia
        return BaseLlamada.objects.values('base_procedencia').annotate(
            total=Count('id'),
            con_venta=Count('venta', distinct=True)
        ).order_by('-total')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas generales
        total_leads = BaseLlamada.objects.count()
        total_ventas = Venta.objects.count()

        context['total_leads'] = total_leads
        context['total_ventas'] = total_ventas

        # Calcular total de leads con venta
        leads_con_venta = BaseLlamada.objects.filter(venta__isnull=False).count()
        context['leads_con_venta'] = leads_con_venta
        context['tasa_conversion'] = round((leads_con_venta / total_leads * 100), 2) if total_leads > 0 else 0

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
                'bo_seguimiento', 'despacho_estado', 'courier_estado'
            )
            .order_by('-creado')
        )


class SeguimientoBOCreateView(LoginRequiredMixin, CreateView):
    model = SeguimientoBO
    form_class = SeguimientoBOForm
    template_name = 'postventa/backoffice_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        # Validar: no permitir crear si ya existe (redirigir a update)
        if hasattr(self.venta, 'bo_seguimiento'):
            messages.info(request, "El seguimiento BO ya existe. Se mostrará para edición.")
            return redirect('postventa:backoffice_update', pk=self.venta.bo_seguimiento.pk)
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


class SeguimientoBOUpdateView(LoginRequiredMixin, UpdateView):
    model = SeguimientoBO
    form_class = SeguimientoBOForm
    template_name = 'postventa/backoffice_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(SeguimientoBO, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.object.venta.pk
        context['is_update'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Seguimiento BO actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.object.venta.pk})