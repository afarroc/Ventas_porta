from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ventas.models import MODELOS_CHIP_LIST, PLANES_CHIP, Venta
from apps.catalogo.models import ChipCompatibilidad, Oferta, Producto, ProveedorCatalogo


PLAN_PRECIO_MAP = {
    'ENTEL_CHIP_29_CONTROL': 29,
    'ENTEL_CHIP_39_CONTROL': 39,
    'ENTEL_CHIP_45_CONTROL': 45,
    'ENTEL_CHIP_59_CONTROL': 59,
    'ENTEL_CHIP_74_CONTROL': 74,
    'ENTEL_CHIP_89_CONTROL': 89,
    'ENTEL_CHIP_109_CONTROL': 109,
    'ENTEL_CHIP_145_CONTROL': 145,
    'ENTEL_CONTROL_49_CONTROL': 49,
    'ENTEL_CONTROL_75_CONTROL': 75,
    'ENTEL_CONTROL_99_CONTROL': 99,
    'ENTEL_CONTROL_149_CONTROL': 149,
    'ENTEL_CONTROL_199_CONTROL': 199,
    'ENTEL_75_CONTROL': 75,
    'ENTEL_LIBRE_149_LIBRE': 149,
    'ENTEL_LIBRE_99_LIBRE': 99,
}


class Command(BaseCommand):
    help = 'Carga una semilla inicial de catálogo desde las constantes actuales de ventas.'

    def add_arguments(self, parser):
        parser.add_argument('--crear-compatibilidad-general', action='store_true', help='Crea compatibilidad entre todos los chips y equipos. Úsalo solo como dato temporal de respaldo. (DEPRECATED - use specific compatibility data)')

    @transaction.atomic
    def handle(self, *args, **options):
        modelo_producto_choices = Venta.MODELO_PRODUCTO_CHOICES
        modelos_chip_list = MODELOS_CHIP_LIST
        planes_chip = PLANES_CHIP
        precios_prepago = Venta.PRECIOS_PREPAGO
        precios_postpago = Venta.PRECIOS_POSTPAGO
        plan_nombre_map = {codigo: nombre for codigo, nombre in Venta.PLAN_PRODUCTO_CHOICES}
        self.plan_nombre_map = plan_nombre_map

        proveedor, _ = ProveedorCatalogo.objects.update_or_create(codigo='ENTEL', defaults={'nombre': 'ENTEL', 'activo': True})

        productos = {}
        for sku, nombre in modelo_producto_choices:
            tipo = 'CHIP' if sku in modelos_chip_list else 'EQUIPO'
            producto, _ = Producto.objects.update_or_create(sku=sku, defaults={'tipo': tipo, 'proveedor_principal': proveedor, 'marca': self._extraer_marca(nombre), 'nombre': nombre, 'descripcion': f'Seed desde Venta.MODELO_PRODUCTO_CHOICES ({tipo}).', 'activo': True})
            productos[sku] = producto

        self._crear_ofertas_prepago(productos, proveedor, precios_prepago)
        self._crear_ofertas_postpago(productos, proveedor, precios_postpago)
        creadas = self._crear_ofertas_plan_choices_revision(productos, proveedor)
        self._crear_ofertas_chip(productos, proveedor, planes_chip)

        if options.get('crear_compatibilidad_general'):
            self._crear_compatibilidad_general(productos)

        self.stdout.write(self.style.SUCCESS(f'Catálogo seed listo. Productos: {Producto.objects.count()} | Ofertas: {Oferta.objects.count()} | Compatibilidades: {ChipCompatibilidad.objects.count()} | Ofertas revisión creadas: {creadas}'))

    def _extraer_marca(self, nombre):
        nombre = (nombre or '').strip()
        marcas = ['APPLE', 'HUAWEI', 'LG', 'MOTOROLA', 'SAMSUNG', 'ZTE', 'SUPER CHIP', 'SUPERCHIP']
        for marca in marcas:
            if nombre.upper().startswith(marca):
                return marca
        return ''

    def _crear_ofertas_prepago(self, productos, proveedor, precios_prepago):
        for sku, precio in precios_prepago.items():
            producto = productos.get(sku)
            if not producto or producto.tipo != 'EQUIPO':
                continue
            for origen in ('PORTABILIDAD', 'LINEA_NUEVA'):
                Oferta.objects.update_or_create(producto=producto, proveedor=proveedor, plan_codigo='PREPAGO', tipo_linea='PREPAGO', origen=origen, meses_contrato=0, defaults={'plan_nombre': 'Prepago', 'precio_plan_mensual': Decimal('0.00'), 'precio_equipo': Decimal(str(precio)), 'prioridad': 100, 'activo': True, 'fuente': 'seed:ventas.PRECIOS_PREPAGO', 'confianza': 'REVISION', 'requiere_revision': True, 'observacion_comercial': 'Oferta seed generada automáticamente. Validar con comercial.'})

    def _crear_ofertas_postpago(self, productos, proveedor, precios_postpago):
        for (sku, plan_codigo), precio in precios_postpago.items():
            producto = productos.get(sku)
            if not producto or producto.tipo != 'EQUIPO':
                continue
            Oferta.objects.update_or_create(producto=producto, proveedor=proveedor, plan_codigo=plan_codigo, tipo_linea='POSTPAGO', origen='PORTABILIDAD', meses_contrato=18, defaults={'plan_nombre': self.plan_nombre_map.get(plan_codigo, plan_codigo), 'precio_plan_mensual': Decimal(str(PLAN_PRECIO_MAP.get(plan_codigo, 0))), 'precio_equipo': Decimal(str(precio)), 'prioridad': 100, 'activo': True, 'fuente': 'seed:ventas.PRECIOS_POSTPAGO',         'confianza': 'REVISION',  # Temporalmente revisado
        'requiere_revision': True,
        'observacion_comercial': 'Oferta generada temporalmente. Validar con comercial.' if precio == 1 else ''})

    def _crear_ofertas_plan_choices_revision(self, productos, proveedor):
        equipos = [p for p in productos.values() if p.tipo == 'EQUIPO']
        existentes = set(Oferta.objects.filter(tipo_linea='POSTPAGO', meses_contrato=18).values_list('producto_id', 'plan_codigo', 'origen'))
        ofertas = []
        for plan_codigo, plan_nombre in Venta.PLAN_PRODUCTO_CHOICES:
            precio_plan = Decimal(str(PLAN_PRECIO_MAP.get(plan_codigo, 0)))
            for producto in equipos:
                for origen in ('PORTABILIDAD', 'LINEA_NUEVA'):
                    key = (producto.id, plan_codigo, origen)
                    if key in existentes:
                        continue
                    ofertas.append(Oferta(producto=producto, proveedor=proveedor, plan_codigo=plan_codigo, plan_nombre=plan_nombre, precio_plan_mensual=precio_plan, precio_equipo=precio_plan, tipo_linea='POSTPAGO', origen=origen, meses_contrato=18, prioridad=500, activo=True, fuente='seed:ventas.PLAN_PRODUCTO_CHOICES_sin_precio', confianza='REVISION', requiere_revision=True, observacion_comercial='Oferta generada porque el plan existe pero no tenía precio postpago explícito. Validar con comercial.'))
                    existentes.add(key)
        if not ofertas:
            return 0
        Oferta.objects.bulk_create(ofertas, batch_size=500, ignore_conflicts=True)
        return len(ofertas)

    def _crear_ofertas_chip(self, productos, proveedor, planes_chip):
        for sku, producto in productos.items():
            if producto.tipo != 'CHIP':
                continue
            for plan_codigo in planes_chip:
                for origen in ('PORTABILIDAD', 'LINEA_NUEVA'):
                    Oferta.objects.update_or_create(producto=producto, proveedor=proveedor, plan_codigo=plan_codigo, tipo_linea='POSTPAGO', origen=origen, meses_contrato=18, defaults={'plan_nombre': self.plan_nombre_map.get(plan_codigo, plan_codigo), 'precio_plan_mensual': Decimal(str(PLAN_PRECIO_MAP.get(plan_codigo, 0))), 'precio_equipo': Decimal('1.00'), 'prioridad': 100, 'activo': True, 'fuente': 'seed:ventas.PLANES_CHIP', 'confianza': 'REVISION', 'requiere_revision': False})

    def _crear_compatibilidad_general(self, productos):
        equipos = [p for p in productos.values() if p.tipo == 'EQUIPO']
        chips = [p for p in productos.values() if p.tipo == 'CHIP']
        creadas = 0
        for equipo in equipos:
            for chip in chips:
                _, creada = ChipCompatibilidad.objects.get_or_create(equipo=equipo, chip=chip, defaults={'activo': True, 'observacion': 'Compatibilidad temporal creada por seed general.'})
                if creada:
                    creadas += 1
        self.stdout.write(f'Compatibilidades creadas: {creadas}')
