from django.urls import path
from . import views

app_name = 'postventa'

urlpatterns = [
    path('', views.DashboardBOView.as_view(), name='dashboard_bo'),
    path('backoffice/', views.BackofficeListView.as_view(), name='backoffice_list'),
    path('backoffice/venta/<int:venta_id>/', views.SeguimientoBOCreateView.as_view(), name='backoffice_edit'),
    path('despacho/venta/<int:venta_id>/', views.EstadoDespachoCreateView.as_view(), name='despacho_edit'),
    path('courier/venta/<int:venta_id>/', views.EstadoCourierCreateView.as_view(), name='courier_edit'),
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
]
