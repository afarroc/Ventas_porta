from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

from .forms import VentaForm
from .models import Venta, Cliente, TIPO_RENTA_TABLE
from .views import VentaCreateView, ItemVentaCreateView
from apps.discador.models import BaseLlamada, CallRecord
from apps.users.models import UserProfile
from apps.postventa.models import SeguimientoBO
from apps.postventa.views import SeguimientoBOCreateView


class VentaBusinessRulesTest(TestCase):
    def test_obtener_precio_venta_chip(self):
        self.assertEqual(Venta.obtener_precio_venta('CHIP', '', 'ENTEL_CHIP_45_CONTROL', 'POSTPAGO'), 1)

    def test_obtener_precio_venta_pack_postpago_matrix(self):
        self.assertEqual(
            Venta.obtener_precio_venta('PACK', 'MOTO_G_PLAY', 'ENTEL_CONTROL_49_CONTROL', 'POSTPAGO'),
            49,
        )

    def test_obtener_precio_venta_pack_prepago_modelo(self):
        self.assertEqual(Venta.obtener_precio_venta('PACK', 'MOTO_G_PLUS', '', 'PREPAGO'), 299)

    def test_tipo_renta_pack_portabilidad_table(self):
        cases = {
            29: 'R.BAJA',
            49: 'R.BAJA',
            74: 'R.MEDIA',
            75: 'R.MEDIA',
            99: 'R.ALTA',
            149: 'R.ALTA',
            199: 'R.ALTA',
            299: 'R.ALTA',
        }
        for valor, esperado in cases.items():
            self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', valor, 0), esperado)

    def test_tipo_renta_chip_portabilidad_table(self):
        cases = {
            25: 'R.BAJA',
            29: 'R.BAJA',
            39: 'R.BAJA',
            45: 'R.BAJA',
            49: 'R.BAJA',
            59: 'R.MEDIA',
            74: 'R.MEDIA',
            75: 'R.MEDIA',
            89: 'R.MEDIA',
            99: 'R.ALTA',
            109: 'R.ALTA',
            145: 'R.ALTA',
            209: 'R.ALTA',
        }
        for valor, esperado in cases.items():
            self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 1, valor), esperado)

    def test_tipo_renta_pack_linea_nueva_table(self):
        cases = {
            49: 'R.BAJA',
            75: 'R.MEDIA',
            89: 'R.MEDIA',
            99: 'R.ALTA',
            149: 'R.ALTA',
            199: 'R.ALTA',
            299: 'R.ALTA',
        }
        for valor, esperado in cases.items():
            self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'PACK', valor, 0), esperado)

    def test_tipo_renta_chip_linea_nueva_table(self):
        cases = {
            25: 'R.BAJA',
            29: 'R.BAJA',
            39: 'R.BAJA',
            45: 'R.BAJA',
            59: 'R.MEDIA',
            74: 'R.MEDIA',
            89: 'R.MEDIA',
            109: 'R.ALTA',
            145: 'R.ALTA',
            209: 'R.ALTA',
        }
        for valor, esperado in cases.items():
            self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 1, valor), esperado)

    def test_tipo_renta_rejects_undefined_value(self):
        with self.assertRaises(ValueError):
            Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 2, 0)

    def test_tipo_renta_covers_all_price_matrix_values(self):
        for (modelo, plan), precio in Venta.PRECIOS_POSTPAGO.items():
            self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', precio, 0), TIPO_RENTA_TABLE[('PORTABILIDAD', 'PACK', precio)])
            self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'PACK', precio, 0), TIPO_RENTA_TABLE[('LINEA_NUEVA', 'PACK', precio)])

        plan_prices = {
            'ENTEL_CHIP_29_CONTROL': 29,
            'ENTEL_CHIP_39_CONTROL': 39,
            'ENTEL_CHIP_45_CONTROL': 45,
            'ENTEL_CHIP_59_CONTROL': 59,
            'ENTEL_CHIP_74_CONTROL': 74,
            'ENTEL_CHIP_89_CONTROL': 89,
            'ENTEL_CHIP_109_CONTROL': 109,
            'ENTEL_CHIP_145_CONTROL': 145,
        }
        for plan, precio in plan_prices.items():
            self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 1, precio), TIPO_RENTA_TABLE[('PORTABILIDAD', 'CHIP', precio)])
            self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 1, precio), TIPO_RENTA_TABLE[('LINEA_NUEVA', 'CHIP', precio)])

        for modelo, precio in Venta.PRECIOS_PREPAGO.items():
            self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', precio, 0), TIPO_RENTA_TABLE[('PORTABILIDAD', 'PACK', precio)])
            self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'PACK', precio, 0), TIPO_RENTA_TABLE[('LINEA_NUEVA', 'PACK', precio)])


class VentaFormBusinessRulesTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Juan',
            paterno='Pérez',
            activo=True,
        )

    def base_data(self, **kwargs):
        data = {
            'cliente_tipo_documento': 'DNI',
            'cliente_documento': '12345678',
            'registrar_nuevo_cliente': False,
            'producto_nombre': 'CHIP',
            'modelo_producto': '',
            'plan_producto': 'ENTEL_CHIP_45_CONTROL',
            'precio_venta': '',
            'precio_plan': '45',
            'tipo_linea': 'POSTPAGO',
            'origen': 'LINEA_NUEVA',
        }
        data.update(kwargs)
        return data

    def test_chip_price_model_and_plan_validation(self):
        form = VentaForm(self.base_data())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['precio_venta'], 1)
        self.assertEqual(form.cleaned_data['modelo_producto'], '')

    def test_chip_normalizes_zero_model_to_empty(self):
        form = VentaForm(self.base_data(modelo_producto='0'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['modelo_producto'], '')
        self.assertEqual(form.cleaned_data['precio_venta'], 1)

    def test_chip_rejects_equipment_model(self):
        form = VentaForm(self.base_data(modelo_producto='MOTO_G_PLAY'))
        self.assertFalse(form.is_valid())
        self.assertIn('modelo_producto', form.errors)

    def test_chip_requires_chip_plan(self):
        form = VentaForm(self.base_data(plan_producto=''))
        self.assertFalse(form.is_valid())
        self.assertIn('plan_producto', form.errors)

        form = VentaForm(self.base_data(plan_producto='ENTEL_CONTROL_49_CONTROL'))
        self.assertFalse(form.is_valid())
        self.assertIn('plan_producto', form.errors)

    def test_pack_requires_equipment_model(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='', plan_producto='ENTEL_CONTROL_49_CONTROL', tipo_linea='POSTPAGO'))
        self.assertFalse(form.is_valid())
        self.assertIn('modelo_producto', form.errors)

    def test_pack_rejects_chip_model(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='SUPER_CHIP_ENTEL_PLUS', plan_producto='ENTEL_CONTROL_49_CONTROL', tipo_linea='POSTPAGO'))
        self.assertFalse(form.is_valid())
        self.assertIn('modelo_producto', form.errors)

    def test_pack_requires_plan(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='MOTO_G_PLAY', plan_producto='', tipo_linea='POSTPAGO'))
        self.assertFalse(form.is_valid())
        self.assertIn('plan_producto', form.errors)

    def test_pack_postpago_uses_model_plan_matrix(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='MOTO_G_PLAY', plan_producto='ENTEL_CONTROL_49_CONTROL', tipo_linea='POSTPAGO'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['precio_venta'], 49)

    def test_pack_prepago_uses_model_price(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='MOTO_G_PLUS', plan_producto='ENTEL_CONTROL_75_CONTROL', tipo_linea='PREPAGO'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['precio_venta'], 299)

    def test_pack_rejects_missing_price(self):
        form = VentaForm(self.base_data(producto_nombre='PACK', modelo_producto='IPHONE_4S', plan_producto='ENTEL_CONTROL_49_CONTROL', tipo_linea='POSTPAGO'))
        self.assertFalse(form.is_valid())
        self.assertIn('precio_venta', form.errors)


class PrecioVentaApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='agente', password='pass')
        self.client = Client()
        self.client.login(username='agente', password='pass')

    def test_api_returns_chip_price(self):
        response = self.client.get(
            reverse('ventas:obtener_precio_venta'),
            {'producto': 'CHIP', 'modelo': '', 'plan': 'ENTEL_CHIP_45_CONTROL', 'tipo_linea': 'POSTPAGO'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'precio': 1})

    def test_api_returns_pack_postpago_price(self):
        response = self.client.get(
            reverse('ventas:obtener_precio_venta'),
            {'producto': 'PACK', 'modelo': 'MOTO_G_PLAY', 'plan': 'ENTEL_CONTROL_49_CONTROL', 'tipo_linea': 'POSTPAGO'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'precio': 49})

    def test_api_returns_pack_prepago_price(self):
        response = self.client.get(
            reverse('ventas:obtener_precio_venta'),
            {'producto': 'PACK', 'modelo': 'MOTO_G_PLUS', 'plan': '', 'tipo_linea': 'PREPAGO'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'precio': 299})

    def test_api_rejects_invalid_tipo_linea(self):
        response = self.client.get(
            reverse('ventas:obtener_precio_venta'),
            {'producto': 'PACK', 'modelo': 'MOTO_G_PLAY', 'plan': 'ENTEL_CONTROL_49_CONTROL', 'tipo_linea': 'INVALIDO'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['ok'])


class VentaCreateViewSmokeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE, codigo_agente='A001')
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890',
            nombres='Juan',
            paterno='Pérez',
            documento='87654321',
        )
        CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio='2024-01-01 10:00:00',
        )
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='87654321',
            nombres='Juan',
            paterno='Pérez',
            activo=True,
        )

    def test_venta_create_view_with_base_llamada_id(self):
        request = self.factory.get(reverse('ventas:venta_create_with_base', kwargs={'id_lead': self.base_llamada.id_lead}))
        request.user = self.user
        request.session = {}
        response = VentaCreateView.as_view()(request, id_lead=str(self.base_llamada.id_lead))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['base_llamada_telefono'], self.base_llamada.telefono)

    def test_venta_create_view_without_base_llamada_id(self):
        request = self.factory.get(reverse('ventas:venta_create'))
        request.user = self.user
        response = VentaCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class PostVentaSmokeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE, codigo_agente='A002')
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Juan',
            paterno='Pérez',
            activo=True,
        )
        self.venta = Venta.objects.create(cliente=self.cliente)

    def test_item_create_view_get(self):
        request = self.factory.get(reverse('ventas:item_create', kwargs={'venta_id': self.venta.id}))
        request.user = self.user
        response = ItemVentaCreateView.as_view()(request, venta_id=self.venta.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tipo de Venta', str(response.context_data['form']))

    def test_backoffice_create_view_get(self):
        request = self.factory.get(reverse('postventa:backoffice_create', kwargs={'venta_id': self.venta.id}))
        request.user = self.user
        response = SeguimientoBOCreateView.as_view()(request, venta_id=self.venta.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Status bo', str(response.context_data['form']))

    def test_seguimiento_bo_creation(self):
        seguimiento = SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='PDTE_BO',
            supervisor='Carlos Ruiz',
        )
        self.assertEqual(seguimiento.venta, self.venta)
