from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'postventa_proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


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
        'ventas.Venta', on_delete=models.CASCADE, related_name='seguimiento_bo'
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
        'ventas.Venta', on_delete=models.CASCADE, related_name='estado_despacho'
    )
    etapa = models.CharField(
        max_length=30, choices=ETAPA_CHOICES, default='EN_BASE', blank=True
    )
    fecha_etapa = models.DateField(null=True, blank=True)
    proveedor = models.ForeignKey(
        'Proveedor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despachos',
    )
    tracking = models.CharField(max_length=100, blank=True, verbose_name="N° Seguimiento / Tracking")
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'postventa_estadodespacho'
        verbose_name = 'Estado Despacho'
        verbose_name_plural = 'Estados Despacho'
        ordering = ['-creado']

    def __str__(self):
        return f"Despacho - Venta {self.venta_id}: {self.get_etapa_display()}"


class EstadoCourier(models.Model):
    STS_COURIER_CHOICES = [
        ('PDTE_BO', 'Pdte. BO'),
        ('EN_RUTA', 'En Ruta'),
        ('ENTREGADO', 'Entregado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    venta = models.OneToOneField(
        'ventas.Venta', on_delete=models.CASCADE, related_name='estado_courier'
    )
    sts_courier = models.CharField(
        max_length=30, choices=STS_COURIER_CHOICES, default='PDTE_BO', blank=True
    )
    fch_courier = models.DateField(null=True, blank=True, verbose_name="Fecha Courier")
    proveedor = models.ForeignKey(
        'Proveedor', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='couriers',
    )
    tracking = models.CharField(max_length=100, blank=True, verbose_name="N° Seguimiento / Tracking")
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'postventa_estadocourier'
        verbose_name = 'Estado Courier'
        verbose_name_plural = 'Estados Courier'
        ordering = ['-creado']

    def __str__(self):
        return f"Courier - Venta {self.venta_id}: {self.get_sts_courier_display()}"
