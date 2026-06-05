from django.db import models


class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [('DNI', 'DNI'), ('RUC', 'RUC'), ('CE', 'Carnet de Extranjería'), ('PASAPORTE', 'Pasaporte')]
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='DNI', verbose_name="Tipo de Documento")
    documento = models.CharField(max_length=20, unique=True, verbose_name="Documento")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    paterno = models.CharField(max_length=50, blank=True, verbose_name="Paterno")
    materno = models.CharField(max_length=50, blank=True, verbose_name="Materno")
    telefono_1 = models.CharField(max_length=20, blank=True, verbose_name="Teléfono 01")
    telefono_2 = models.CharField(max_length=20, blank=True, verbose_name="Teléfono 02")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ventas_cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.nombres} {self.paterno} {self.materno} ({self.documento})"


class Venta(models.Model):
    agente_nombre = models.CharField(max_length=150, verbose_name="Agente (Vendedor)")

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas', verbose_name="Cliente")
    cliente_nombres = models.CharField(max_length=100, blank=True, verbose_name="Nombres")
    cliente_paterno = models.CharField(max_length=50, blank=True, verbose_name="Paterno")
    cliente_materno = models.CharField(max_length=50, blank=True, verbose_name="Materno")
    cliente_tipo_documento = models.CharField(max_length=20, choices=Cliente.TIPO_DOCUMENTO_CHOICES, default='DNI', verbose_name="Tipo de Documento")
    cliente_documento = models.CharField(max_length=20, blank=True, verbose_name="Documento")
    cliente_telefono_1 = models.CharField(max_length=20, blank=True, verbose_name="Teléfono 01")
    cliente_telefono_2 = models.CharField(max_length=20, blank=True, verbose_name="Teléfono 02")

    RECIBO_ELECTRONICO_CHOICES = [('SI_DESEA', 'Si desea'), ('NO_DESEA', 'No desea')]
    recibo_electronico = models.CharField(max_length=10, choices=RECIBO_ELECTRONICO_CHOICES, blank=True, verbose_name="Recibo Electrónico")
    correo_electronico_recibo = models.EmailField(max_length=150, blank=True, verbose_name="Correo Electrónico (Recibo)")
    HORARIO_VISITA_CHOICES = [
        ('LUNES_8_12', 'Lunes a Viernes 8am – 12pm'),
        ('LUNES_13_17', 'Lunes a Viernes 1pm – 5pm'),
        ('LUNES_17_20', 'Lunes a Viernes 5pm – 8pm (express)'),
        ('SABADO_8_13', 'Sábado 8am – 1pm'),
    ]
    horario_visita = models.CharField(max_length=20, choices=HORARIO_VISITA_CHOICES, blank=True, verbose_name="Horario de Visita")

    ABDCP_CHOICES = [('SI', 'Sí'), ('NO', 'No')]
    abdcp = models.CharField(max_length=2, choices=ABDCP_CHOICES, blank=True, verbose_name="ABDCP")
    clausulas = models.CharField(max_length=10, choices=RECIBO_ELECTRONICO_CHOICES, blank=True, verbose_name="Cláusulas")

    producto_nombre = models.CharField(max_length=150, blank=True, verbose_name="Producto")
    origen = models.CharField(max_length=100, blank=True, verbose_name="Origen")
    operador = models.CharField(max_length=50, blank=True, verbose_name="Operador")
    telefono_portar = models.CharField(max_length=20, blank=True, verbose_name="Teléfono a Portar")
    modelo_producto = models.CharField(max_length=100, blank=True, verbose_name="Modelo Producto")
    plan_producto = models.CharField(max_length=100, blank=True, verbose_name="Plan Producto")
    TIPO_LINEA = [('PREPAGO', 'Prepago'), ('POSTPAGO', 'Postpago'), ('LINEA_NUEVA', 'Línea nueva'), ('PORTABILIDAD', 'Portabilidad')]
    tipo_linea = models.CharField(max_length=20, choices=TIPO_LINEA, blank=True, verbose_name="Tipo de Línea")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio de Venta")
    precio_plan = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Precio del Plan")
    tipo_pago = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Pago")

    tipo_via = models.CharField(max_length=20, blank=True, verbose_name="Tipo de Vía")
    nombre_via = models.CharField(max_length=150, blank=True, verbose_name="Nombre de Vía")
    numero_via = models.CharField(max_length=20, blank=True, verbose_name="Número de Vía")
    manzana = models.CharField(max_length=10, blank=True, verbose_name="Manzana")
    interior = models.CharField(max_length=10, blank=True, verbose_name="Interior")
    lote = models.CharField(max_length=10, blank=True, verbose_name="Lote")
    piso = models.CharField(max_length=10, blank=True, verbose_name="Piso")
    zona_tipo = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Zona")
    zona_nombre = models.CharField(max_length=150, blank=True, verbose_name="Nombre de Zona")
    zona_referencia = models.TextField(blank=True, verbose_name="Referencia de Zona")
    departamento = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    distrito = models.CharField(max_length=100, blank=True, verbose_name="Distrito")

    FACTURACION_CHOICES = [('SI', 'Sí'), ('NO', 'No')]
    facturacion_requerida = models.CharField(max_length=2, choices=FACTURACION_CHOICES, blank=True, verbose_name="¿Requiere Factura?")

    base = models.CharField(max_length=50, blank=True, verbose_name="Base")
    tipo_renta = models.CharField(max_length=20, blank=True, verbose_name="Tipo Renta")
    tipo_renta2 = models.CharField(max_length=20, blank=True, verbose_name="Tipo Renta 2")
    base3 = models.CharField(max_length=50, blank=True, verbose_name="Base3")
    q_ventas = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Cantidad de Ventas")
    fecha_venta = models.DateField(null=True, blank=True, verbose_name="Fecha de Venta")
    hora_venta = models.TimeField(null=True, blank=True, verbose_name="Hora de Venta")

    CONTACT_CALLABLE = [('0', 'No'), ('1', 'Sí')]
    contact_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True, verbose_name="Contacto Llamable (disc.)")
    es_callable = models.CharField(max_length=1, choices=CONTACT_CALLABLE, blank=True, verbose_name="Es Callable (disc.)")
    fecha_gestion = models.DateField(null=True, blank=True, verbose_name="Fecha Gestión (disc.)")
    hora_gestion = models.TimeField(null=True, blank=True, verbose_name="Hora Gestión (disc.)")
    resultado_gestion = models.CharField(max_length=100, blank=True, verbose_name="Resultado Gestión (disc.)")
    tipo_contacto = models.CharField(max_length=50, blank=True, verbose_name="Tipo Contacto (disc.)")
    TIPO_VALIDO = [('Válido', 'Válido'), ('Inválido', 'Inválido'), ('', 'No definido')]
    tipo_valido = models.CharField(max_length=10, choices=TIPO_VALIDO, blank=True, verbose_name="Tipo Válido (disc.)")
    status_java = models.CharField(max_length=50, blank=True, verbose_name="Status JAVA (disc.)")
    supervisor_nombre = models.CharField(max_length=150, blank=True, verbose_name="Supervisor (disc.)")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    base_llamada = models.ForeignKey('discador.BaseLlamada', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Base Llamada")

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
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items', verbose_name="Venta")
    tipo_venta = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Venta")
    tipo_producto = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Producto")
    precio_plan = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Precio del Plan")

    class Meta:
        db_table = 'ventas_item'
        verbose_name = 'Ítem de Venta'
        verbose_name_plural = 'Ítems de Venta'

    def __str__(self):
        return f"Item {self.id} - {self.tipo_producto}"


class SeguimientoBO(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='backoffice', verbose_name="Venta")
    status_bo = models.CharField(max_length=50, blank=True, verbose_name="Status BO")
    fecha_bo = models.DateField(null=True, blank=True, verbose_name="Fecha BO")
    sts_courier = models.CharField(max_length=50, blank=True, verbose_name="Sts Courier")
    fch_courier = models.DateField(null=True, blank=True, verbose_name="Fecha Courier")
    supervisor = models.CharField(max_length=150, blank=True, verbose_name="Supervisor")
    intervalo = models.CharField(max_length=20, blank=True, verbose_name="Intervalo")

    class Meta:
        db_table = 'ventas_backoffice'
        verbose_name = 'Seguimiento Backoffice'
        verbose_name_plural = 'Seguimientos Backoffice'

    def __str__(self):
        return f"Seguimiento BO - Venta {self.venta_id}"
