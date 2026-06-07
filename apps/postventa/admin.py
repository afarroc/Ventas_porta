from django.contrib import admin
from .models import Proveedor, SeguimientoBO, EstadoDespacho, EstadoCourier


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'creado']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(SeguimientoBO)
class SeguimientoBOAdmin(admin.ModelAdmin):
    list_display = ['venta', 'status_bo', 'fecha_bo', 'supervisor']
    list_filter = ['status_bo', 'fecha_bo']
    search_fields = ['venta__cliente_nombres', 'supervisor']


@admin.register(EstadoDespacho)
class EstadoDespachoAdmin(admin.ModelAdmin):
    list_display = ['venta', 'etapa', 'fecha_etapa', 'proveedor', 'tracking']
    list_filter = ['etapa', 'fecha_etapa']
    search_fields = ['venta__cliente_nombres', 'tracking']


@admin.register(EstadoCourier)
class EstadoCourierAdmin(admin.ModelAdmin):
    list_display = ['venta', 'sts_courier', 'fch_courier', 'proveedor', 'tracking']
    list_filter = ['sts_courier', 'fch_courier']
    search_fields = ['venta__cliente_nombres', 'tracking']
