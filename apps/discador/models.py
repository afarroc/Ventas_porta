from django.db import models


class BaseLlamada(models.Model):
    # Datos de contacto originales
    telefono = models.CharField(max_length=20, verbose_name="Teléfono Base")
    nombres = models.CharField(max_length=100, blank=True, verbose_name="Nombres Base")
    paterno = models.CharField(max_length=50, blank=True, verbose_name="Paterno Base")
    materno = models.CharField(max_length=50, blank=True, verbose_name="Materno Base")
    correo = models.EmailField(max_length=150, blank=True, verbose_name="Correo Base")
    documento = models.CharField(max_length=20, blank=True, verbose_name="Documento Base")
    numero_base = models.CharField(max_length=50, blank=True, verbose_name="Número Base")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Base")

    # Resultados de la gestión del discador
    CONTACT_CALLABLE = [('0', 'No'), ('1', 'Sí')]
    contact_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True)
    ultimo_intento = models.CharField(max_length=50, blank=True)
    ultimo_resultado_crm = models.CharField(max_length=100, blank=True)
    es_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True)
    fecha_gestion = models.DateField(null=True, blank=True)
    hora_gestion = models.TimeField(null=True, blank=True)
    resultado_gestion = models.CharField(max_length=100, blank=True)
    tipo_contacto = models.CharField(max_length=50, blank=True)
    TIPO_VALIDO = [('Válido', 'Válido'), ('Inválido', 'Inválido'), ('', 'No definido')]
    tipo_valido = models.CharField(max_length=10, choices=TIPO_VALIDO, blank=True)
    status_java = models.CharField(max_length=50, blank=True)
    supervisor_nombre = models.CharField(max_length=150, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discador_base'
        verbose_name = 'Base de Llamada'
        verbose_name_plural = 'Bases de Llamadas'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.telefono} - {self.nombres}"
