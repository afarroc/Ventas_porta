from django.contrib import admin
from .models import SeguimientoBO, HistorialEstado


@admin.register(SeguimientoBO)
class SeguimientoBOAdmin(admin.ModelAdmin):
    list_display = ['venta', 'status_bo', 'fecha_bo', 'supervisor']
    list_filter = ['status_bo', 'fecha_bo']
    search_fields = ['venta__cliente_nombres', 'supervisor']


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ['venta', 'area', 'estado_anterior', 'estado_nuevo', 'fecha_cambio']
    list_filter = ['area', 'estado_nuevo', 'fecha_cambio']
    search_fields = ['venta__id', 'venta__cliente_nombres']
    readonly_fields = ['fecha_cambio']