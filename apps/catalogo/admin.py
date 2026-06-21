from django.contrib import admin

from .models import ProveedorCatalogo, Producto, Oferta, ChipCompatibilidad


class OfertaInline(admin.TabularInline):
    model = Oferta
    extra = 0
    fields = ('plan_codigo', 'precio_plan_mensual', 'precio_equipo', 'tipo_linea', 'origen', 'activo')


@admin.register(ProveedorCatalogo)
class ProveedorCatalogoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo', 'creado', 'actualizado']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['creado', 'actualizado']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['sku', 'tipo', 'proveedor_principal', 'marca', 'nombre', 'activo', 'stock_actual', 'stock_minimo']
    list_filter = ['tipo', 'activo', 'proveedor_principal', 'requiere_stock']
    search_fields = ['sku', 'marca', 'nombre', 'descripcion']
    readonly_fields = ['creado', 'actualizado']
    inlines = [OfertaInline]

    fieldsets = (
        ('Identificación', {'fields': ('sku', 'tipo', 'proveedor_principal', 'marca', 'nombre', 'descripcion')}),
        ('Disponibilidad comercial', {'fields': ('activo', 'stock_actual', 'stock_minimo', 'requiere_stock')}),
        ('Auditoría', {'fields': ('creado', 'actualizado'), 'classes': ('collapse',)}),
    )


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'proveedor', 'plan_codigo', 'precio_plan_mensual', 'precio_equipo', 'tipo_linea', 'origen', 'meses_contrato', 'activo', 'confianza', 'requiere_revision']
    list_filter = ['tipo_linea', 'origen', 'activo', 'confianza', 'requiere_revision', 'proveedor']
    search_fields = ['producto__sku', 'producto__nombre', 'proveedor__codigo', 'plan_codigo', 'plan_nombre']
    readonly_fields = ['creado', 'actualizado']

    fieldsets = (
        ('Producto y proveedor', {'fields': ('producto', 'proveedor')}),
        ('Plan', {'fields': ('plan_codigo', 'plan_nombre', 'precio_plan_mensual', 'tipo_linea', 'meses_contrato')}),
        ('Condiciones comerciales', {'fields': ('precio_equipo', 'origen', 'prioridad', 'activo', 'vigencia_desde', 'vigencia_hasta')}),
        ('Control de calidad', {'fields': ('fuente', 'confianza', 'requiere_revision', 'observacion_comercial')}),
        ('Auditoría', {'fields': ('creado', 'actualizado'), 'classes': ('collapse',)}),
    )


@admin.register(ChipCompatibilidad)
class ChipCompatibilidadAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'chip', 'activo', 'creado', 'actualizado']
    list_filter = ['activo']
    search_fields = ['equipo__sku', 'equipo__nombre', 'chip__sku', 'chip__nombre']
    readonly_fields = ['creado', 'actualizado']
