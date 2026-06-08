from django.urls import path
from .views import HomeView, VentaListView, VentaDetailView, VentaCreateView, BackofficeListView, buscar_cliente_ajax, validar_cliente_ajax, recargar_lead_ajax, venta_modal_partial, venta_api_create, get_provincias, get_distritos, ItemVentaCreateView, venta_trazabilidad_api

app_name = 'ventas'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('ventas/', VentaListView.as_view(), name='venta_list'),
    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
    path('ventas/nueva/<uuid:id_lead>/', VentaCreateView.as_view(), name='venta_create_with_base'),
    path('ventas/nueva/', VentaCreateView.as_view(), name='venta_create'),
    path('ventas/buscar-cliente/', buscar_cliente_ajax, name='buscar_cliente'),
    path('ventas/validar-cliente/', validar_cliente_ajax, name='validar_cliente'),
    path('ventas/recargar-lead/<uuid:id_lead>/', recargar_lead_ajax, name='recargar_lead'),
    path('ventas/modal/<uuid:id_lead>/', venta_modal_partial, name='venta_modal'),
    path('api/ventas/crear/<uuid:id_lead>/', venta_api_create, name='venta_api_create'),
    path('api/ubigeo/provincias/', get_provincias, name='get_provincias'),
    path('api/ubigeo/distritos/', get_distritos, name='get_distritos'),
    # Ítems
    path('ventas/<int:venta_id>/item/nuevo/', ItemVentaCreateView.as_view(), name='item_create'),
    path('ventas/backoffice/', BackofficeListView.as_view(), name='backoffice_list'),
    path('api/venta/<int:pk>/trazabilidad/', venta_trazabilidad_api, name='venta_trazabilidad'),
]
