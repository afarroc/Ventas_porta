from django.urls import path
from . import views

app_name = 'postventa'

urlpatterns = [
    path('', views.DashboardBOView.as_view(), name='dashboard_bo'),
    path('backoffice/', views.BackofficeListView.as_view(), name='backoffice_list'),
    path('backoffice/venta/<int:venta_id>/', views.SeguimientoBOCreateView.as_view(), name='backoffice_create'),
]