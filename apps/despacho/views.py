from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Proveedor, EstadoDespacho
from apps.ventas.models import Venta
from .forms import ProveedorForm, EstadoDespachoForm


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
        messages.success(self.request, "Estado de despacho actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ventas:venta_detail', kwargs={'pk': self.object.venta.pk})