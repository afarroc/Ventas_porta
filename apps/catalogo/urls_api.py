from django.urls import path

from .views import catalogo_productos_api, ofertas_por_producto_api, chips_compatibles_api, validar_oferta_api

app_name = 'catalogo_api'

urlpatterns = [
    path('productos/', catalogo_productos_api, name='catalogo_productos'),
    path('productos/<str:sku>/ofertas/', ofertas_por_producto_api, name='catalogo_ofertas_producto'),
    path('equipos/<str:sku>/chips/', chips_compatibles_api, name='catalogo_chips_equipo'),
    path('ofertas/validar/', validar_oferta_api, name='catalogo_validar_oferta'),
]
