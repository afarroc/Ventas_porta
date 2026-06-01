from django.test import TestCase
from .models import Venta, ItemVenta, SeguimientoBO


class VentaModelTest(TestCase):
    def setUp(self):
        self.venta = Venta.objects.create(
            agente_nombre='Juan Gómez',
            cliente_nombres='Pedro',
            cliente_paterno='López',
            cliente_documento='12345678'
        )

    def test_venta_creation(self):
        self.assertEqual(self.venta.agente_nombre, 'Juan Gómez')
        self.assertTrue(str(self.venta))

    def test_item_venta_creation(self):
        item = ItemVenta.objects.create(
            venta=self.venta,
            tipo_producto='Línea móvil',
            precio_plan=29.99
        )
        self.assertEqual(item.venta, self.venta)
        self.assertEqual(self.venta.items.count(), 1)

    def test_seguimiento_bo_creation(self):
        seguimiento = SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='Pendiente',
            supervisor='Carlos Ruiz'
        )
        self.assertEqual(seguimiento.venta, self.venta)
