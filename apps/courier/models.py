from django.db import models


class ProveedorCourier(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'courier_proveedor'
        verbose_name = 'Proveedor Courier'
        verbose_name_plural = 'Proveedores Courier'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EstadoCourier(models.Model):
    STS_COURIER_CHOICES = [
        ('PDTE_BO', 'Pdte. BO'),
        ('EN_RUTA', 'En Ruta'),
        ('ENTREGADO', 'Entregado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    venta = models.OneToOneField(
        'ventas.Venta', on_delete=models.CASCADE, related_name='courier_estado'
    )
    sts_courier = models.CharField(
        max_length=30, choices=STS_COURIER_CHOICES, default='PDTE_BO', blank=True
    )
    fch_courier = models.DateField(null=True, blank=True, verbose_name="Fecha Courier")
    proveedor = models.ForeignKey(
        ProveedorCourier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='couriers'
    )
    tracking = models.CharField(max_length=100, blank=True, verbose_name="N° Seguimiento / Tracking")
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courier_estado'
        verbose_name = 'Estado Courier'
        verbose_name_plural = 'Estados Courier'
        ordering = ['-creado']

    def __str__(self):
        return f"Courier - Venta {self.venta_id}: {self.get_sts_courier_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ventas:venta_detail', kwargs={'pk': self.venta_id})