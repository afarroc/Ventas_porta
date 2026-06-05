from django.contrib import admin
from .models import Cliente, Venta, ItemVenta, SeguimientoBO


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['documento', 'tipo_documento', 'nombres', 'paterno', 'materno', 'telefono_1', 'activo', 'creado']
    list_filter = ['activo', 'tipo_documento']
    search_fields = ['documento', 'nombres', 'paterno', 'materno', 'telefono_1', 'telefono_2']
    readonly_fields = ['creado', 'actualizado']
    fieldsets = (
        ('Documento', {
            'fields': ('tipo_documento', 'documento')
        }),
        ('Datos Personales', {
            'fields': ('nombres', 'paterno', 'materno')
        }),
        ('Contacto', {
            'fields': ('telefono_1', 'telefono_2')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )


class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 1
    fields = ('tipo_venta', 'tipo_producto', 'precio_plan')


class SeguimientoBOInline(admin.StackedInline):
    model = SeguimientoBO
    extra = 0
    fields = ('status_bo', 'fecha_bo', 'sts_courier', 'fch_courier', 'supervisor', 'intervalo')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'agente_nombre', 'cliente', 'tipo_linea', 'fecha_venta', 'precio_venta'
    ]
    list_filter = ['tipo_linea', 'fecha_venta', 'facturacion_requerida']
    search_fields = ['agente_nombre', 'cliente__nombres', 'cliente__documento']
    readonly_fields = ['creado', 'actualizado']
    inlines = [ItemVentaInline, SeguimientoBOInline]

    fieldsets = (
        ('Agente', {
            'fields': ('agente_nombre',)
        }),
        ('Cliente', {
            'fields': ('cliente', 'cliente_nombres', 'cliente_paterno', 'cliente_materno',
                      'cliente_tipo_documento', 'cliente_documento', 'cliente_telefono_1', 'cliente_telefono_2')
        }),
        ('Recibo Electrónico', {
            'fields': ('recibo_electronico', 'correo_electronico_recibo', 'horario_visita', 'clausulas', 'abdcp')
        }),
        ('Producto y Venta', {
            'fields': ('producto_nombre', 'origen', 'operador', 'telefono_portar',
                      'modelo_producto', 'plan_producto', 'tipo_linea', 'precio_venta', 'precio_plan', 'tipo_pago')
        }),
        ('Dirección de Despacho', {
            'fields': ('tipo_via', 'nombre_via', 'numero_via', 'manzana', 'interior', 'lote', 'piso',
                      'zona_tipo', 'zona_nombre', 'zona_referencia', 'departamento', 'provincia', 'distrito')
        }),
        ('Facturación', {
            'fields': ('facturacion_requerida',)
        }),
        ('Gestión del Discador', {
            'fields': ('contact_callable', 'es_callable', 'fecha_gestion', 'hora_gestion', 
                      'resultado_gestion', 'tipo_contacto', 'tipo_valido', 'status_java', 'supervisor_nombre')
        }),
        ('Backoffice/Resumen', {
            'fields': ('base', 'tipo_renta', 'tipo_renta2', 'base3', 'q_ventas', 'fecha_venta', 'hora_venta')
        }),
        ('Auditoría', {
            'fields': ('observaciones', 'creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'venta', 'tipo_venta', 'tipo_producto', 'precio_plan']
    list_filter = ['tipo_venta', 'tipo_producto']
    search_fields = ['venta__cliente_nombres', 'tipo_producto']


@admin.register(SeguimientoBO)
class SeguimientoBOAdmin(admin.ModelAdmin):
    list_display = ['venta', 'status_bo', 'fecha_bo', 'sts_courier', 'supervisor']
    list_filter = ['status_bo', 'fecha_bo']
    search_fields = ['venta__cliente_nombres', 'supervisor']
