from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from .models import ProveedorCourier, EstadoCourier
from apps.ventas.models import Venta
from .forms import ProveedorCourierForm, EstadoCourierForm
from apps.postventa.services import registrar_cambio_estado


class ProveedorCourierListView(LoginRequiredMixin, ListView):
    model = ProveedorCourier
    template_name = 'courier/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 50


class ProveedorCourierCreateView(LoginRequiredMixin, CreateView):
    model = ProveedorCourier
    form_class = ProveedorCourierForm
    template_name = 'courier/proveedor_form.html'
    success_url = reverse_lazy('courier:proveedor_list')
    success_message = "Proveedor courier creado correctamente."


class EstadoCourierCreateView(LoginRequiredMixin, CreateView):
    model = EstadoCourier
    form_class = EstadoCourierForm
    template_name = 'courier/courier_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        # Validación: requerir SeguimientoBO existente y en estado DESPACHADO
        if not hasattr(self.venta, 'bo_seguimiento'):
            messages.error(request, "Debe existir SeguimientoBO para crear EstadoCourier.")
            return redirect('ventas:venta_detail', pk=self.venta.pk)
        bo_status = self.venta.bo_seguimiento.status_bo
        if bo_status != 'DESPACHADO':
            messages.error(
                request,
                f"SeguimientoBO debe estar en DESPACHADO para crear EstadoCourier (actual: {bo_status})"
            )
            return redirect('ventas:venta_detail', pk=self.venta.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.venta.pk
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_cambio_estado(
            venta=form.instance.venta,
            area='COURIER',
            estado_anterior='',
            estado_nuevo=form.instance.sts_courier,
            usuario=self.request.user,
        )
        messages.success(self.request, "Estado de courier registrado correctamente.")
        return response

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.venta.pk})


class EstadoCourierUpdateView(LoginRequiredMixin, UpdateView):
    model = EstadoCourier
    form_class = EstadoCourierForm
    template_name = 'courier/courier_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.object.venta.pk
        context['is_update'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Estado de courier actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.object.venta.pk})