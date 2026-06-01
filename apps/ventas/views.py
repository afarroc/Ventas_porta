from django.views.generic import ListView, DetailView, TemplateView
from .models import Venta, ItemVenta


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
