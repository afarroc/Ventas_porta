# apps/users/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROL_AGENTE = 'AGENTE'
    ROL_SUPERVISOR = 'SUPERVISOR'
    ROL_ADMIN = 'ADMIN'
    ROL_CHOICES = [
        (ROL_AGENTE, 'Agente'),
        (ROL_SUPERVISOR, 'Supervisor'),
        (ROL_ADMIN, 'Administrador'),
    ]

    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_INACTIVO = 'INACTIVO'
    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    TURNO_DIURNO = 'DIURNO'
    TURNO_NOCTURNO = 'NOCTURNO'
    TURNO_HIBRIDO = 'HIBRIDO'
    TURNO_CHOICES = [
        (TURNO_DIURNO, 'Diurno'),
        (TURNO_NOCTURNO, 'Nocturno'),
        (TURNO_HIBRIDO, 'Híbrido'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_AGENTE, verbose_name="Rol")
    codigo_agente = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Código de Agente")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': ROL_SUPERVISOR},
        related_name='agentes_supervisados',
        verbose_name="Supervisor Asignado"
    )
    zona = models.CharField(max_length=100, blank=True, verbose_name="Zona de Trabajo")
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, blank=True, verbose_name="Turno")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO, verbose_name="Estado")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_profile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def __str__(self):
        if self.codigo_agente:
            return f"{self.user.get_full_name()} ({self.codigo_agente})"
        return self.user.get_full_name() or self.user.username
