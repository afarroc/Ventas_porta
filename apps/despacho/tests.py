from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.test import RequestFactory

from apps.ventas.models import Venta, Cliente
from apps.postventa.models import SeguimientoBO
from apps.despacho.models import Proveedor, EstadoDespacho
from apps.users.models import UserProfile


class ProveedorModelTest(TestCase):
    def test_proveedor_creation(self):
        proveedor = Proveedor.objects.create(nombre='Chaz Perú', activo=True)
        self.assertEqual(str(proveedor), 'Chaz Perú')
        self.assertTrue(proveedor.activo)

    def test_proveedor_nombre_unique(self):
        Proveedor.objects.create(nombre='Chaz Perú', activo=True)
        with self.assertRaises(Exception):
            Proveedor.objects.create(nombre='Chaz Perú', activo=True)


class EstadoDespachoModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Pedro',
            paterno='López',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Agente Test',
            cliente=self.cliente,
            cliente_nombres='Pedro',
            cliente_paterno='López',
            cliente_documento='12345678',
        )
        self.proveedor = Proveedor.objects.create(nombre='Chaz Perú')

    def test_estado_despacho_creation(self):
        estado = EstadoDespacho.objects.create(
            venta=self.venta,
            etapa='EN_PREPARACION',
            proveedor=self.proveedor,
            tracking='TRACK123',
            observaciones='En preparación',
        )
        self.assertEqual(estado.venta, self.venta)
        self.assertEqual(estado.etapa, 'EN_PREPARACION')
        self.assertEqual(str(estado), f'Despacho - Venta {self.venta.id}: En Preparación')

    def test_default_etapa(self):
        estado = EstadoDespacho.objects.create(venta=self.venta)
        self.assertEqual(estado.etapa, 'EN_BASE')


class DespachoViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)

        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='22222222',
            nombres='Test',
            paterno='Cliente',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Test Agent',
            cliente=self.cliente,
            cliente_nombres='Test',
            cliente_paterno='Cliente',
            cliente_documento='22222222',
        )

    def test_proveedor_list_requires_login(self):
        url = reverse('despacho:proveedor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/users/login/?next={url}')

    def test_proveedor_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('despacho:proveedor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_despacho_create_requires_bo(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('despacho:despacho_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Debe existir SeguimientoBO', str(messages_list[0]))

    def test_despacho_create_with_bo(self):
        self.client.login(username='testuser', password='testpass123')
        SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='VALIDADO',
            supervisor='Super Test',
        )
        url = reverse('despacho:despacho_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Etapa')
