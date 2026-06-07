from django.urls import path
from . import views

app_name = 'courier'

urlpatterns = [
    path('proveedores/', views.ProveedorCourierListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', views.ProveedorCourierCreateView.as_view(), name='proveedor_create'),
    path('venta/<int:venta_id>/', views.EstadoCourierCreateView.as_view(), name='courier_create'),
    path('venta/<int:pk>/editar/', views.EstadoCourierUpdateView.as_view(), name='courier_update'),
]