from django.db import models


class Venta(models.Model):
    # --- Agente (temporalmente texto) ---
    agente_nombre = models.CharField(max_length=150, verbose_name="Agente (Vendedor)")

    # --- Cliente transitorio (se migrará a entidad propia) ---
    cliente_nombres = models.CharField(max_length=100, blank=True)
    cliente_paterno = models.CharField(max_length=50, blank=True)
    cliente_materno = models.CharField(max_length=50, blank=True)
    cliente_documento = models.CharField(max_length=20, blank=True)
    cliente_numero = models.CharField(max_length=50, blank=True)
    cliente_telefono_1 = models.CharField(max_length=20, blank=True)
    cliente_telefono_2 = models.CharField(max_length=20, blank=True)

    # --- Venta y producto (resumen o datos heredados) ---
    RECIBO_CHOICES = [('SI', 'Sí'), ('NO', 'No'), ('SI_DESEA', 'Si desea'), ('NO_DESEA', 'No desea')]
    recibo_electronico = models.CharField(max_length=10, choices=RECIBO_CHOICES, blank=True)
    correo_electronico_recibo = models.EmailField(max_length=150, blank=True)
    horario_visita = models.CharField(max_length=100, blank=True)

    ABDCP_CHOICES = [('SI', 'Sí'), ('NO', 'No')]
    abdcp = models.CharField(max_length=2, choices=ABDCP_CHOICES, blank=True)
    clausulas = models.CharField(max_length=10, choices=RECIBO_CHOICES, blank=True)

    producto_nombre = models.CharField(max_length=150, blank=True)
    origen = models.CharField(max_length=100, blank=True)
    operador = models.CharField(max_length=50, blank=True)
    telefono_portar = models.CharField(max_length=20, blank=True)
    modelo_producto = models.CharField(max_length=100, blank=True)
    plan_producto = models.CharField(max_length=100, blank=True)
    TIPO_LINEA = [('PREPAGO', 'Prepago'), ('POSTPAGO', 'Postpago'), ('LINEA_NUEVA', 'Línea nueva'), ('PORTABILIDAD', 'Portabilidad')]
    tipo_linea = models.CharField(max_length=20, choices=TIPO_LINEA, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_plan = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tipo_pago = models.CharField(max_length=50, blank=True)

    # --- Dirección de despacho ---
    tipo_via = models.CharField(max_length=20, blank=True)
    nombre_via = models.CharField(max_length=150, blank=True)
    numero_via = models.CharField(max_length=20, blank=True)
    manzana = models.CharField(max_length=10, blank=True)
    interior = models.CharField(max_length=10, blank=True)
    lote = models.CharField(max_length=10, blank=True)
    piso = models.CharField(max_length=10, blank=True)
    zona_tipo = models.CharField(max_length=50, blank=True)
    zona_nombre = models.CharField(max_length=150, blank=True)
    zona_referencia = models.TextField(blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    distrito = models.CharField(max_length=100, blank=True)

    FACTURACION_CHOICES = [('SI', 'Sí'), ('NO', 'No')]
    facturacion_requerida = models.CharField(max_length=2, choices=FACTURACION_CHOICES, blank=True)

    # --- Nuevos campos de backoffice/resumen ---
    base = models.CharField(max_length=50, blank=True, verbose_name="Base")
    tipo_renta = models.CharField(max_length=20, blank=True)
    tipo_renta2 = models.CharField(max_length=20, blank=True)
    base3 = models.CharField(max_length=50, blank=True)
    q_ventas = models.PositiveSmallIntegerField(null=True, blank=True)
    fecha_venta = models.DateField(null=True, blank=True)
    hora_venta = models.TimeField(null=True, blank=True)

    # --- Campos de gestión (heredados de BaseLlamada) ---
    CONTACT_CALLABLE = [('0', 'No'), ('1', 'Sí')]
    contact_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True)
    es_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True)
    fecha_gestion = models.DateField(null=True, blank=True)
    hora_gestion = models.TimeField(null=True, blank=True)
    resultado_gestion = models.CharField(max_length=100, blank=True)
    tipo_contacto = models.CharField(max_length=50, blank=True)
    TIPO_VALIDO = [('Válido', 'Válido'), ('Inválido', 'Inválido'), ('', 'No definido')]
    tipo_valido = models.CharField(max_length=10, choices=TIPO_VALIDO, blank=True)
    status_java = models.CharField(max_length=50, blank=True)
    supervisor_nombre = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ventas_venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-creado']

    def __str__(self):
        return f"Venta {self.id} - {self.cliente_nombres} {self.cliente_paterno}"


class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    tipo_venta = models.CharField(max_length=50, blank=True)
    tipo_producto = models.CharField(max_length=50, blank=True)
    precio_plan = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'ventas_item'
        verbose_name = 'Ítem de Venta'
        verbose_name_plural = 'Ítems de Venta'

    def __str__(self):
        return f"Item {self.id} - {self.tipo_producto}"


class SeguimientoBO(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='backoffice')
    status_bo = models.CharField(max_length=50, blank=True)
    fecha_bo = models.DateField(null=True, blank=True)
    sts_courier = models.CharField(max_length=50, blank=True)
    fch_courier = models.DateField(null=True, blank=True)
    supervisor = models.CharField(max_length=150, blank=True)
    intervalo = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'ventas_backoffice'
        verbose_name = 'Seguimiento Backoffice'
        verbose_name_plural = 'Seguimientos Backoffice'

    def __str__(self):
        return f"Seguimiento BO - Venta {self.venta_id}"
