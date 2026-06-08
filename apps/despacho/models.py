from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'despacho_proveedor'
        verbose_name = 'Proveedor Despacho'
        verbose_name_plural = 'Proveedores Despacho'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EstadoDespacho(models.Model):
    ETAPA_CHOICES = [
        ('EN_BASE', 'En Base'),
        ('PDTE_DESPACHO', 'Pdte. Despacho'),
        ('EN_PREPARACION', 'En Preparación'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('ENTREGADO', 'Entregado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    venta = models.OneToOneField(
        'ventas.Venta', on_delete=models.CASCADE, related_name='despacho_estado'
    )
    etapa = models.CharField(
        max_length=30, choices=ETAPA_CHOICES, default='EN_BASE', blank=True
    )
    fecha_etapa = models.DateField(null=True, blank=True, verbose_name="Fecha Etapa")
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despachos'
    )
    tracking = models.CharField(max_length=100, blank=True, verbose_name="N° Seguimiento / Tracking")
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'despacho_estado'
        verbose_name = 'Estado Despacho'
        verbose_name_plural = 'Estados Despacho'
        ordering = ['-creado']

    def __str__(self):
        return f"Despacho - Venta {self.venta_id}: {self.get_etapa_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ventas:venta_detail', kwargs={'pk': self.venta_id})