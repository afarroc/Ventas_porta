import uuid

from django.db import models
from django.contrib.auth.models import User

CONTACT_CALLABLE = [('0', 'No'), ('1', 'Sí')]
TIPO_VALIDO = [('Válido', 'Válido'), ('Inválido', 'Inválido'), ('', 'No definido')]


class BaseLlamada(models.Model):
    id = models.AutoField(primary_key=True)
    id_lead = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID Lead")
    telefono = models.CharField(max_length=15, unique=True, verbose_name="Teléfono")
    nombres = models.CharField(max_length=100, blank=True, verbose_name="Nombres Base")
    paterno = models.CharField(max_length=50, blank=True, verbose_name="Paterno Base")
    materno = models.CharField(max_length=50, blank=True, verbose_name="Materno Base")
    correo = models.EmailField(max_length=150, blank=True, verbose_name="Correo Base")
    documento = models.CharField(max_length=20, blank=True, verbose_name="Documento Base", help_text="DNI, RUT o identificación")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Base")
    contact_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True, verbose_name="Contacto Llamable")
    ultimo_intento = models.CharField(max_length=50, blank=True, verbose_name="Último Intento (CRM)")
    ultimo_resultado_crm = models.CharField(max_length=100, blank=True, verbose_name="Último Resultado (CRM)")
    es_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True, verbose_name="Es Callable")
    fecha_gestion = models.DateField(null=True, blank=True, verbose_name="Fecha de Gestión")
    hora_gestion = models.TimeField(null=True, blank=True, verbose_name="Hora de Gestión")
    resultado_gestion = models.CharField(max_length=100, blank=True, verbose_name="Resultado de Gestión")
    tipo_contacto = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Contacto")
    tipo_valido = models.CharField(max_length=10, choices=TIPO_VALIDO, blank=True, verbose_name="Tipo Válido")
    status_java = models.CharField(max_length=50, blank=True, verbose_name="Status JAVA")
    supervisor_nombre = models.CharField(max_length=150, blank=True, verbose_name="Supervisor")
    BASE_PROCEDENCIA_CHOICES = [
        ('POT', 'POT'),
        ('RSG_01', 'RSG_01'),
    ]
    base_procedencia = models.CharField(
        max_length=20,
        choices=BASE_PROCEDENCIA_CHOICES,
        blank=True,
        default='',
        verbose_name="Base de Procedencia",
        db_index=True,
    )
    base_manual = models.BooleanField(
        default=False,
        verbose_name="Lead Manual",
        help_text="Marcar si el número NO existe en una base y es lead cargado manualmente",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discador_base'
        verbose_name = 'Base de Llamada'
        verbose_name_plural = 'Bases de Llamadas'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.telefono} - {self.nombres}"


class CallRecord(models.Model):
    RESULTADO_CHOICES = [
        ('CONTESTADA', 'Contestada'),
        ('NO_CONTESTADA', 'No contestada'),
        ('OCUPADA', 'Ocupada'),
        ('DESCONECTADA', 'Desconectada'),
        ('NO_VOZ', 'No voz'),
        ('FAX', 'Fax'),
        ('OTRO', 'Otro'),
        ('LIBERADO_SIN_USO', 'Liberado sin uso'),
    ]

    DISPOSITION_CHOICES = [
        ('VENTA', 'Venta'),
        ('NO_CONTESTA', 'No contesta'),
        ('CUELGA', 'Cuelga'),
        ('FAX', 'Fax'),
        ('NO_DESEA', 'No desea'),
        ('OTRO', 'Otro'),
        ('LIBERADO_SIN_USO', 'Liberado sin uso'),
    ]

    agente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='llamadas')
    base_llamada = models.ForeignKey(BaseLlamada, on_delete=models.CASCADE, related_name='llamadas')
    inicio = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)
    duracion = models.DurationField(null=True, blank=True)
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, blank=True, default='')
    observaciones = models.TextField(blank=True)
    acw_start = models.DateTimeField(null=True, blank=True, verbose_name="Inicio de ACW")
    acw_end = models.DateTimeField(null=True, blank=True, verbose_name="Fin de ACW")
    disposition = models.CharField(max_length=20, choices=DISPOSITION_CHOICES, blank=True, verbose_name="Tipificación")
    liberado_sin_uso = models.BooleanField(default=False, verbose_name="Liberado sin uso")

    def save(self, *args, **kwargs):
        # Compute duration for the call (if we have both inicio and fin)
        if self.inicio and self.fin:
            self.duracion = self.fin - self.inicio
        # If we have both acw_start and acw_end, we could compute acw_duration, but we don't store it as a field.
        # We'll compute it as a property if needed.
        super().save(*args, **kwargs)
        # If the call has a finish time, update the BaseLlamada's last attempt and result
        if self.fin:
            base = self.base_llamada
            # Format the start time as a string for the BaseLlamada field
            base.ultimo_intento = self.inicio.strftime("%Y-%m-%d %H:%M:%S")
            # Get the display name for the result
            base.ultimo_resultado_crm = dict(self.RESULTADO_CHOICES).get(self.resultado, self.resultado)
            # Update only these two fields to avoid triggering other signals/saves unnecessarily
            base.save(update_fields=['ultimo_intento', 'ultimo_resultado_crm'])

    def __str__(self):
        return f"Llamada {self.id} - {self.agente} - {self.base_llamada}"

    @property
    def acw_duration(self):
        if self.acw_start and self.acw_end:
            return self.acw_end - self.acw_start
        return None

    class Meta:
        verbose_name = "Registro de Llamada"
        verbose_name_plural = "Registros de Llamadas"
        ordering = ['-inicio']
