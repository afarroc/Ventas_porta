from django.urls import path
from .views import BaseLlamadaListView

app_name = 'discador'

urlpatterns = [
    path('bases/', BaseLlamadaListView.as_view(), name='base_list'),
]
