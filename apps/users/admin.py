# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile


class UserProfileInlineForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supervisor'].queryset = UserProfile.objects.filter(rol=UserProfile.ROL_SUPERVISOR)
        if self.instance and self.instance.rol == UserProfile.ROL_ADMIN:
            self.fields['supervisor'].required = False
        else:
            self.fields['supervisor'].required = True
        self.fields['rol'].required = True


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileInlineForm
    can_delete = False
    verbose_name_plural = 'Perfil'
    max_num = 1
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'get_codigo_agente', 'get_rol', 'get_supervisor', 'is_active'
    ]

    def get_codigo_agente(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.codigo_agente or '-'
        return '-'
    get_codigo_agente.short_description = 'Código Agente'

    def get_rol(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_rol_display()
        return '-'
    get_rol.short_description = 'Rol'

    def get_supervisor(self, obj):
        if hasattr(obj, 'profile') and obj.profile.supervisor:
            sup = obj.profile.supervisor
            name = sup.user.get_full_name() or sup.user.username
            if sup.codigo_agente:
                return f"{name} ({sup.codigo_agente})"
            return name
        return '-'
    get_supervisor.short_description = 'Supervisor'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileInlineForm
    list_display = [
        'user', 'get_rol', 'codigo_agente', 'telefono',
        'get_supervisor_nombre', 'zona', 'turno', 'activo', 'estado'
    ]
    list_filter = ['activo', 'estado', 'turno', 'zona', 'rol']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 'codigo_agente'
    ]

    def get_rol(self, obj):
        return obj.get_rol_display()
    get_rol.short_description = 'Rol'

    def get_supervisor_nombre(self, obj):
        if obj.supervisor:
            sup = obj.supervisor
            name = sup.user.get_full_name() or sup.user.username
            if sup.codigo_agente:
                return f"{name} ({sup.codigo_agente})"
            return name
        return '-'
    get_supervisor_nombre.short_description = 'Supervisor'
