from django.contrib import admin
from .models import Proveedor, EstadoDespacho


@admin.register(Proveedor)
class ProveedorDespachoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'creado']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(EstadoDespacho)
class EstadoDespachoAdmin(admin.ModelAdmin):
    list_display = ['venta', 'etapa', 'fecha_etapa', 'proveedor', 'tracking']
    list_filter = ['etapa', 'fecha_etapa']
    search_fields = ['venta__cliente__nombres', 'tracking']