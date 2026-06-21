from django.urls import path

from .views import CatalogoView

app_name = 'catalogo'

urlpatterns = [
    path('', CatalogoView.as_view(), name='index'),
]
