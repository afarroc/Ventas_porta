from django.contrib import admin
from .models import BaseLlamada


@admin.register(BaseLlamada)
class BaseLlamadaAdmin(admin.ModelAdmin):
    list_display = [
        'telefono', 'nombres', 'paterno', 'es_callable',
        'fecha_gestion', 'resultado_gestion', 'tipo_valido'
    ]
    list_filter = ['es_callable', 'tipo_valido', 'fecha_gestion']
    search_fields = ['telefono', 'nombres', 'documento']
    readonly_fields = ['creado', 'actualizado']
    
    fieldsets = (
        ('Datos de Contacto', {
            'fields': ('telefono', 'nombres', 'paterno', 'materno', 'correo', 'documento', 'numero_base')
        }),
        ('Gestión del Discador', {
            'fields': ('contact_callable', 'es_callable', 'ultimo_intento', 'ultimo_resultado_crm',
                      'fecha_gestion', 'hora_gestion', 'resultado_gestion', 'tipo_contacto', 'tipo_valido')
        }),
        ('Supervisión', {
            'fields': ('supervisor_nombre', 'status_java')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
