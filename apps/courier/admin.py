from django.contrib import admin
from .models import ProveedorCourier, EstadoCourier


@admin.register(ProveedorCourier)
class ProveedorCourierAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'creado']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(EstadoCourier)
class EstadoCourierAdmin(admin.ModelAdmin):
    list_display = ['venta', 'sts_courier', 'fch_courier', 'proveedor', 'tracking']
    list_filter = ['sts_courier', 'fch_courier']
    search_fields = ['venta__cliente_nombres', 'tracking']