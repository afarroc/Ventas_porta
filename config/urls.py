from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('apps.ventas.urls')),
    path('discador/', include('apps.discador.urls')),
    path('users/', include('apps.users.urls')),
    path('postventa/', include('apps.postventa.urls')),
    path('despacho/', include('apps.despacho.urls')),
    path('courier/', include('apps.courier.urls')),
    path('admin/', admin.site.urls),
]
