from django.contrib import admin
from .models import BaseLlamada, CallRecord


@admin.register(BaseLlamada)
class BaseLlamadaAdmin(admin.ModelAdmin):
    list_display = [
        'id_lead', 'telefono', 'nombres', 'paterno', 'es_callable',
        'fecha_gestion', 'resultado_gestion', 'tipo_valido'
    ]
    list_filter = ['es_callable', 'tipo_valido', 'fecha_gestion']
    search_fields = ['telefono', 'nombres', 'documento', 'id_lead']
    readonly_fields = ['id_lead', 'creado', 'actualizado']
    
    fieldsets = (
        ('Datos de Contacto', {
            'fields': ('telefono', 'nombres', 'paterno', 'materno', 'correo', 'documento')
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


@admin.register(CallRecord)
class CallRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'agente', 'base_llamada', 'inicio', 'fin', 'resultado', 'disposition', 'duracion'
    ]
    list_filter = ['resultado', 'disposition', 'inicio', 'fin']
    search_fields = ['agente__username', 'agente__first_name', 'agente__last_name', 'base_llamada__telefono', 'base_llamada__documento']
    readonly_fields = ['inicio', 'fin', 'duracion', 'acw_start', 'acw_end']
    
    fieldsets = (
        ('Información de la Llamada', {
            'fields': ('agente', 'base_llamada', 'inicio', 'fin', 'duracion', 'resultado')
        }),
        ('ACW (After Call Work)', {
            'fields': ('acw_start', 'acw_end', 'disposition', 'observaciones')
        }),
    )
