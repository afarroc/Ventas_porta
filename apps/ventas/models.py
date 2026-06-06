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

    PRODUCTO_CHOICES = [('CHIP', 'CHIP'), ('PACK', 'PACK')]
    producto_nombre = models.CharField(max_length=10, choices=PRODUCTO_CHOICES, blank=True, verbose_name="Producto")
    ORIGEN_CHOICES = [('LINEA_NUEVA', 'Línea Nueva'), ('PORTABILIDAD', 'Portabilidad')]
    origen = models.CharField(max_length=15, choices=ORIGEN_CHOICES, blank=True, verbose_name="Origen")
    OPERADOR_CHOICES = [
        ('CLARO', 'CLARO'), ('LINEA_NUEVA', 'Linea NUEVA'), ('MOVISTAR', 'MOVISTAR'),
        ('VIETTEL', 'VIETTEL'), ('VIRGIN', 'VIRGIN'),
    ]
    operador = models.CharField(max_length=20, choices=OPERADOR_CHOICES, blank=True, verbose_name="Operador")
    telefono_portar = models.CharField(max_length=20, blank=True, verbose_name="Teléfono a Portar")
    MODELO_PRODUCTO_CHOICES = [
        ('IPHONE_4S', 'APPLE IPHONE 4S 8GB-NEGRO-3G'),
        ('IPHONE_6_PLUS', 'APPLE IPHONE 6 PLUS 16GB - PLATEADO-4G'),
        ('HUAWEI_MATE_S', 'HUAWEI MATE S  - NEGRO'),
        ('HUAWEI_MATE_S_NEGRO', 'HUAWEI MATE S - NEGRO'),
        ('HUAWEI_P9_LITE', 'HUAWEI P9 LITE - NEGRO'),
        ('HUAWEI_Y360_II_BLANCO', 'HUAWEI Y360 II-BLANCO-3G'),
        ('HUAWEI_Y360_II_NEGRO', 'HUAWEI Y360 II-NEGRO'),
        ('HUAWEI_Y360_II_NEGRO_DASH', 'HUAWEI Y360 II-NEGRO-'),
        ('HUAWEI_Y360_II_NEGRO_3G', 'HUAWEI Y360 II-NEGRO-3G'),
        ('HUAWEI_Y360_BLANCO', 'HUAWEI Y360-BLANCO-3G'),
        ('HUAWEI_Y360_NEGRO', 'HUAWEI Y360-NEGRO-3G'),
        ('LG_G4_STYLUS_BLANCO', 'LG G4 STYLUS-BLANCO-4G'),
        ('LG_G4_STYLUS_METALICO', 'LG G4 STYLUS-METALICO-4G'),
        ('LG_G5_TITAN', 'LG G5-TITAN-4G'),
        ('LG_X_STYLE_BLANCO', 'LG X STYLE-BLANCO-4G'),
        ('LG_X_STYLE_NEGRO', 'LG X STYLE-NEGRO -4G'),
        ('MOTO_G_PLAY', 'MOTOROLA MOTO G 4TA GENERACION PLAY - NEGRO'),
        ('MOTO_G_PLUS', 'MOTOROLA MOTO G 4TA GENERACION PLUS - NEGRO'),
        ('MOTO_X_PLAY', 'MOTOROLA MOTO X PLAY-NEGRO-4G'),
        ('MOTO_Z_PLAY', 'MOTOROLA MOTO Z PLAY - NEGRO'),
        ('GALAXY_J1', 'SAMSUNG GALAXY J1 2016-NEGRO -4G'),
        ('GALAXY_J7', 'SAMSUNG GALAXY J7-NEGRO-4G'),
        ('SUPER_CHIP_ENTEL_PLUS', 'SUPER CHIP ENTEL PLUS'),
        ('SUPERCHIP_ENTEL', 'SUPERCHIP-ENTEL'),
        ('ZTE_BLADE_A315_BLANCO', 'ZTE BLADE A315-BLANCO-4G'),
        ('ZTE_BLADE_A315_NEGRO', 'ZTE BLADE A315-NEGRO-4G'),
        ('ZTE_BLADE_A610_GRIS', 'ZTE BLADE A610 - Gris'),
        ('ZTE_BLADE_A610_GRIS_DASH', 'ZTE BLADE A610- GRIS-4G'),
        ('ZTE_BLADE_A610_BLANCO', 'ZTE BLADE A610-BLANCO'),
        ('ZTE_BLADE_A610_GRIS_CLEAN', 'ZTE BLADE A610-GRIS'),
        ('ZTE_BLADE_A610_GRIS_4G', 'ZTE BLADE A610-GRIS-4G'),
        ('ZTE_BLADE_A610_NEGRO', 'ZTE BLADE A610-NEGRO'),
        ('ZTE_BLADE_A610_NEGRO_4G', 'ZTE BLADE A610-NEGRO-4G'),
        ('ZTE_BLADE_L5_BLANCO', 'ZTE BLADE L5-BLANCO-3G'),
        ('ZTE_BLADE_L5_GRIS', 'ZTE BLADE L5-GRIS-3G'),
    ]
    modelo_producto = models.CharField(max_length=50, choices=MODELO_PRODUCTO_CHOICES, blank=True, verbose_name="Modelo Producto")
    PLAN_PRODUCTO_CHOICES = [
        ('ENTEL_75_CONTROL', 'ENTEL  75-CONTROL'),
        ('ENTEL_CHIP_109_CONTROL', 'ENTEL CHIP 109-CONTROL'),
        ('ENTEL_CHIP_145_CONTROL', 'ENTEL CHIP 145-CONTROL'),
        ('ENTEL_CHIP_29_CONTROL', 'ENTEL CHIP 29-CONTROL'),
        ('ENTEL_CHIP_39_CONTROL', 'ENTEL CHIP 39-CONTROL'),
        ('ENTEL_CHIP_45_CONTROL', 'ENTEL CHIP 45-CONTROL'),
        ('ENTEL_CHIP_59_CONTROL', 'ENTEL CHIP 59-CONTROL'),
        ('ENTEL_CHIP_74_CONTROL', 'ENTEL CHIP 74-CONTROL'),
        ('ENTEL_CHIP_89_CONTROL', 'ENTEL CHIP 89-CONTROL'),
        ('ENTEL_CONTROL_149_CONTROL', 'ENTEL CONTROL 149-CONTROL'),
        ('ENTEL_CONTROL_199_CONTROL', 'ENTEL CONTROL 199-CONTROL'),
        ('ENTEL_CONTROL_49_CONTROL', 'ENTEL CONTROL 49-CONTROL'),
        ('ENTEL_CONTROL_75_CONTROL', 'ENTEL CONTROL 75-CONTROL'),
        ('ENTEL_CONTROL_99_CONTROL', 'ENTEL CONTROL 99-CONTROL'),
        ('ENTEL_LIBRE_149_LIBRE', 'ENTEL LIBRE 149-LIBRE'),
        ('ENTEL_LIBRE_99_LIBRE', 'ENTEL LIBRE 99-LIBRE'),
    ]
    plan_producto = models.CharField(max_length=50, choices=PLAN_PRODUCTO_CHOICES, blank=True, verbose_name="Plan Producto")
    TIPO_LINEA_CHOICES = [('PREPAGO', 'Prepago'), ('POSTPAGO', 'Postpago')]
    tipo_linea = models.CharField(max_length=20, choices=TIPO_LINEA_CHOICES, blank=True, verbose_name="Tipo de Línea")
    PRECIO_VENTA_CHOICES = [
        (1, '1'), (9, '9'), (29, '29'), (39, '39'), (49, '49'), (59, '59'), (79, '79'), (89, '89'),
        (99, '99'), (109, '109'), (119, '119'), (129, '129'), (149, '149'), (189, '189'), (199, '199'),
        (229, '229'), (349, '349'), (399, '399'), (429, '429'), (499, '499'), (599, '599'), (699, '699'),
    ]
    precio_venta = models.IntegerField(choices=PRECIO_VENTA_CHOICES, null=True, blank=True, verbose_name="Precio de Venta")
    PRECIO_PLAN_CHOICES = [
        (29, '29'), (39, '39'), (45, '45'), (49, '49'), (59, '59'), (74, '74'), (75, '75'),
        (89, '89'), (99, '99'), (109, '109'), (145, '145'), (149, '149'),
    ]
    precio_plan = models.IntegerField(choices=PRECIO_PLAN_CHOICES, null=True, blank=True, verbose_name="Precio del Plan")
    TIPO_PAGO_CHOICES = [('EFECTIVO', 'Efectivo'), ('TARJETA', 'Tarjeta')]
    tipo_pago = models.CharField(max_length=10, choices=TIPO_PAGO_CHOICES, blank=True, verbose_name="Tipo de Pago")

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