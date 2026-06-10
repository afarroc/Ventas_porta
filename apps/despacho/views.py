from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Proveedor, EstadoDespacho
from apps.ventas.models import Venta
from .forms import ProveedorForm, EstadoDespachoForm
from apps.postventa.services import registrar_cambio_estado


class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'despacho/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 50


class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'despacho/proveedor_form.html'
    success_url = reverse_lazy('despacho:proveedor_list')
    success_message = "Proveedor creado correctamente."


class EstadoDespachoCreateView(LoginRequiredMixin, CreateView):
    model = EstadoDespacho
    form_class = EstadoDespachoForm
    template_name = 'despacho/despacho_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        # Validación: requerir SeguimientoBO en estado válido
        if not hasattr(self.venta, 'bo_seguimiento'):
            messages.error(request, "Debe existir SeguimientoBO para crear EstadoDespacho.")
            return redirect('ventas:venta_detail', pk=self.venta.pk)
        bo_status = self.venta.bo_seguimiento.status_bo
        if bo_status not in ['VALIDADO', 'EN_DESPACHO']:
            messages.error(
                request, 
                f"SeguimientoBO debe estar en VALIDADO o EN_DESPACHO (actual: {bo_status})"
            )
            return redirect('ventas:venta_detail', pk=self.venta.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.venta.pk
        return context

    def form_valid(self, form):
        # Asignar la venta antes de guardar
        form.instance.venta = self.venta
        
        # Validar tracking único (no duplicar entre despacho y courier de la misma venta)
        tracking = form.cleaned_data.get('tracking', '')
        if tracking:
            from apps.courier.models import EstadoCourier
            exists_in_courier = EstadoCourier.objects.filter(
                venta=self.venta,
                tracking__iexact=tracking
            ).exists()
            if exists_in_courier:
                form.add_error('tracking', 'Este tracking ya está registrado en el courier de esta venta.')
                return self.form_invalid(form)

        response = super().form_valid(form)
        registrar_cambio_estado(
            venta=form.instance.venta,
            area='DESPACHO',
            estado_anterior='',
            estado_nuevo=form.instance.etapa,
            usuario=self.request.user,
        )
        messages.success(self.request, "Estado de despacho registrado correctamente.")
        return response

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.venta.pk})


class EstadoDespachoUpdateView(LoginRequiredMixin, UpdateView):
    model = EstadoDespacho
    form_class = EstadoDespachoForm
    template_name = 'despacho/despacho_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.object.venta.pk
        context['is_update'] = True
        return context

    def form_valid(self, form):
        estado_anterior = self.object.etapa
        response = super().form_valid(form)
        registrar_cambio_estado(
            venta=form.instance.venta,
            area='DESPACHO',
            estado_anterior=estado_anterior,
            estado_nuevo=form.instance.etapa,
            usuario=self.request.user,
        )
        messages.success(self.request, "Estado de despacho actualizado correctamente.")
        return response

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.object.venta.pk})