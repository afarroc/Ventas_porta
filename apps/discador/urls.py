from django.urls import path
from .views import BaseLlamadaListView, BaseLlamadaDetailView, AgentDashboardView, check_incoming_call, ResultadoDiscadoListView, ResultadoDiscadoDetailView

app_name = 'discador'

urlpatterns = [
    path('', AgentDashboardView.as_view(), name='agent_dashboard'),
    path('bases/', BaseLlamadaListView.as_view(), name='base_list'),
    path('base/<int:pk>/', BaseLlamadaDetailView.as_view(), name='base_detail'),
    path('check-incoming/', check_incoming_call, name='check_incoming'),
    # Resultados del discado
    path('resultados/', ResultadoDiscadoListView.as_view(), name='resultado_list'),
    path('resultados/<uuid:id_lead>/', ResultadoDiscadoDetailView.as_view(), name='resultado_detail'),
]
