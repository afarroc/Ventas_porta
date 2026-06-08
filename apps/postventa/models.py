from django.db import models
from django.contrib.auth.models import User


class HistorialEstado(models.Model):
    AREA_CHOICES = [
        ('BO', 'Backoffice'),
        ('DESPACHO', 'Despacho'),
        ('COURIER', 'Courier'),
    ]

    venta = models.ForeignKey('ventas.Venta', on_delete=models.CASCADE, related_name='historial_estados')
    area = models.CharField(max_length=10, choices=AREA_CHOICES, verbose_name="Área")
    estado_anterior = models.CharField(max_length=50, blank=True, verbose_name="Estado Anterior")
    estado_nuevo = models.CharField(max_length=50, verbose_name="Estado Nuevo")
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_cambios',
        verbose_name="Usuario"
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Cambio")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        db_table = 'postventa_historial'
        verbose_name = 'Historial Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-fecha_cambio']

    def __str__(self):
        return f"{self.get_area_display()}: {self.estado_anterior} → {self.estado_nuevo}"


class SeguimientoBO(models.Model):
    STATUS_BO_CHOICES = [
        ('EN_BASE', 'En Base'),
        ('PDTE_BO', 'Pdte. BO'),
        ('EN_BO', 'En BO'),
        ('VALIDADO', 'Validado'),
        ('EN_DESPACHO', 'En Despacho'),
        ('DESPACHADO', 'Despachado'),
    ]

    venta = models.OneToOneField(
        'ventas.Venta', on_delete=models.CASCADE, related_name='bo_seguimiento'
    )
    status_bo = models.CharField(
        max_length=30, choices=STATUS_BO_CHOICES, default='PDTE_BO', blank=True
    )
    fecha_bo = models.DateField(null=True, blank=True, verbose_name="Fecha BO")
    supervisor = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'postventa_seguimientobo'
        verbose_name = 'Seguimiento BO'
        verbose_name_plural = 'Seguimientos BO'
        ordering = ['-creado']

    def __str__(self):
        return f"BO - Venta {self.venta_id}: {self.get_status_bo_display()}"