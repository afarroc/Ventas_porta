from django.urls import path
from . import views

app_name = 'despacho'

urlpatterns = [
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('venta/<int:venta_id>/', views.EstadoDespachoCreateView.as_view(), name='despacho_create'),
    path('venta/<int:pk>/editar/', views.EstadoDespachoUpdateView.as_view(), name='despacho_update'),
]