from django.urls import path
from .views import HomeView, VentaListView, VentaDetailView, VentaCreateView, buscar_cliente_ajax, validar_cliente_ajax

app_name = 'ventas'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('ventas/', VentaListView.as_view(), name='venta_list'),
    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
    path('ventas/nueva/<int:base_llamada_id>/', VentaCreateView.as_view(), name='venta_create_with_base'),
    path('ventas/nueva/', VentaCreateView.as_view(), name='venta_create'),
    path('ventas/buscar-cliente/', buscar_cliente_ajax, name='buscar_cliente'),
    path('ventas/validar-cliente/', validar_cliente_ajax, name='validar_cliente'),
]
