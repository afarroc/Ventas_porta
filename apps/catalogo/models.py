from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class ProveedorCatalogo(models.Model):
    codigo = models.CharField(max_length=30, unique=True, verbose_name='Código', help_text='Código comercial: ENTEL, CLARO, VIRGIN, MOVISTAR.')
    nombre = models.CharField(max_length=120, verbose_name='Nombre')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalogo_proveedor'
        verbose_name = 'Proveedor de catálogo'
        verbose_name_plural = 'Proveedores de catálogo'
        ordering = ['codigo']

    def save(self, *args, **kwargs):
        self.codigo = (self.codigo or '').strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo


class Producto(models.Model):
    TIPO_CHOICES = [('EQUIPO', 'Equipo'), ('CHIP', 'Chip')]

    sku = models.CharField(max_length=80, unique=True, verbose_name='SKU')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    proveedor_principal = models.ForeignKey(ProveedorCatalogo, null=True, blank=True, on_delete=models.SET_NULL, related_name='productos_principales', verbose_name='Proveedor principal')
    marca = models.CharField(max_length=120, blank=True, verbose_name='Marca')
    nombre = models.CharField(max_length=180, verbose_name='Nombre descriptivo')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    stock_actual = models.PositiveIntegerField(default=0, verbose_name='Stock actual')
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')
    requiere_stock = models.BooleanField(default=False, verbose_name='Requiere control de stock', help_text='Desactivado por defecto porque esta fase es catálogo comercial, no inventario.')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalogo_producto'
        verbose_name = 'Producto de catálogo'
        verbose_name_plural = 'Productos de catálogo'
        ordering = ['tipo', 'marca', 'nombre']

    def save(self, *args, **kwargs):
        self.sku = (self.sku or '').strip().upper()
        super().save(*args, **kwargs)

    @property
    def es_chip(self):
        return self.tipo == 'CHIP'

    @property
    def es_equipo(self):
        return self.tipo == 'EQUIPO'

    def __str__(self):
        return f'{self.sku} - {self.nombre}'


class Oferta(models.Model):
    TIPO_LINEA_CHOICES = [('PREPAGO', 'Prepago'), ('POSTPAGO', 'Postpago')]
    ORIGEN_CHOICES = [('PORTABILIDAD', 'Portabilidad'), ('LINEA_NUEVA', 'Línea nueva')]
    CONFIANZA_CHOICES = [('ALTA', 'Alta'), ('MEDIA', 'Media'), ('BAJA', 'Baja'), ('REVISION', 'Requiere revisión')]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ofertas', verbose_name='Producto')
    proveedor = models.ForeignKey(ProveedorCatalogo, on_delete=models.PROTECT, related_name='ofertas', verbose_name='Proveedor')
    plan_codigo = models.CharField(max_length=80, verbose_name='Código de plan')
    plan_nombre = models.CharField(max_length=180, blank=True, verbose_name='Nombre de plan')
    precio_plan_mensual = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Precio mensual del plan')
    precio_equipo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Precio del equipo')
    tipo_linea = models.CharField(max_length=20, choices=TIPO_LINEA_CHOICES, verbose_name='Tipo de línea')
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES, verbose_name='Origen')
    meses_contrato = models.PositiveIntegerField(default=18, verbose_name='Meses de contrato')
    prioridad = models.PositiveIntegerField(default=100, verbose_name='Prioridad')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    vigencia_desde = models.DateField(null=True, blank=True, verbose_name='Vigencia desde')
    vigencia_hasta = models.DateField(null=True, blank=True, verbose_name='Vigencia hasta')
    fuente = models.CharField(max_length=60, default='manual', verbose_name='Fuente')
    confianza = models.CharField(max_length=20, choices=CONFIANZA_CHOICES, default='ALTA', verbose_name='Confianza')
    requiere_revision = models.BooleanField(default=False, verbose_name='Requiere revisión')
    observacion_comercial = models.TextField(blank=True, verbose_name='Observación comercial')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalogo_oferta'
        verbose_name = 'Oferta comercial'
        verbose_name_plural = 'Ofertas comerciales'
        ordering = ['prioridad', 'plan_codigo', 'producto']
        constraints = [models.UniqueConstraint(fields=['producto', 'proveedor', 'plan_codigo', 'tipo_linea', 'origen', 'meses_contrato'], name='uq_catalogo_oferta_completa')]

    def es_vigente(self, fecha=None):
        fecha = fecha or timezone.localdate()
        if self.vigencia_desde and fecha < self.vigencia_desde:
            return False
        if self.vigencia_hasta and fecha > self.vigencia_hasta:
            return False
        return True

    def __str__(self):
        return f'{self.producto.sku} | {self.plan_codigo} | {self.tipo_linea} | {self.origen}'


class ChipCompatibilidad(models.Model):
    equipo = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compatibilidad_equipo', limit_choices_to={'tipo': 'EQUIPO'}, verbose_name='Equipo')
    chip = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compatibilidad_chip', limit_choices_to={'tipo': 'CHIP'}, verbose_name='Chip')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    observacion = models.TextField(blank=True, verbose_name='Observación')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalogo_chip_compatibilidad'
        verbose_name = 'Compatibilidad chip-equipo'
        verbose_name_plural = 'Compatibilidades chip-equipo'
        ordering = ['equipo__nombre', 'chip__nombre']
        constraints = [models.UniqueConstraint(fields=['equipo', 'chip'], name='uq_catalogo_chip_compatibilidad')]

    def __str__(self):
        return f'{self.equipo.sku} ↔ {self.chip.sku}'
