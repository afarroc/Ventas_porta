from django.contrib import admin
from .models import SeguimientoBO


@admin.register(SeguimientoBO)
class SeguimientoBOAdmin(admin.ModelAdmin):
    list_display = ['venta', 'status_bo', 'fecha_bo', 'supervisor']
    list_filter = ['status_bo', 'fecha_bo']
    search_fields = ['venta__cliente_nombres', 'supervisor']