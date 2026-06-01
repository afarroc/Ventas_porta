from django.urls import path
from .views import HomeView, VentaListView, VentaDetailView

app_name = 'ventas'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('ventas/', VentaListView.as_view(), name='venta_list'),
    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
]
