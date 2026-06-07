from django.db import models


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