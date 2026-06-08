from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages

from apps.ventas.models import Venta, Cliente
from apps.postventa.models import SeguimientoBO
from apps.courier.models import ProveedorCourier, EstadoCourier
from apps.users.models import UserProfile


class ProveedorCourierModelTest(TestCase):
    def test_proveedor_courier_creation(self):
        proveedor = ProveedorCourier.objects.create(nombre='Olva Courier', activo=True)
        self.assertEqual(str(proveedor), 'Olva Courier')
        self.assertTrue(proveedor.activo)

    def test_proveedor_courier_nombre_unique(self):
        ProveedorCourier.objects.create(nombre='Olva Courier', activo=True)
        with self.assertRaises(Exception):
            ProveedorCourier.objects.create(nombre='Olva Courier', activo=True)


class EstadoCourierModelTest(TestCase):
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
        self.proveedor = ProveedorCourier.objects.create(nombre='Olva Courier')

    def test_estado_courier_creation(self):
        estado = EstadoCourier.objects.create(
            venta=self.venta,
            sts_courier='EN_RUTA',
            proveedor=self.proveedor,
            tracking='COURIER123',
            observaciones='En camino',
        )
        self.assertEqual(estado.venta, self.venta)
        self.assertEqual(estado.sts_courier, 'EN_RUTA')
        self.assertEqual(str(estado), f'Courier - Venta {self.venta.id}: En Ruta')

    def test_default_sts_courier(self):
        estado = EstadoCourier.objects.create(venta=self.venta)
        self.assertEqual(estado.sts_courier, 'PDTE_BO')


class CourierViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)

        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='33333333',
            nombres='Test',
            paterno='Cliente',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Test Agent',
            cliente=self.cliente,
            cliente_nombres='Test',
            cliente_paterno='Cliente',
            cliente_documento='33333333',
        )

    def test_proveedor_courier_list_requires_login(self):
        url = reverse('courier:proveedor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/users/login/?next={url}')

    def test_proveedor_courier_list_loads(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('courier:proveedor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_courier_create_requires_bo(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('courier:courier_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_courier_create_requires_bo_despachado(self):
        self.client.login(username='testuser', password='testpass123')
        SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='VALIDADO',
            supervisor='Super Test',
        )
        url = reverse('courier:courier_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_courier_create_with_bo_despachado(self):
        self.client.login(username='testuser', password='testpass123')
        SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='DESPACHADO',
            supervisor='Super Test',
        )
        url = reverse('courier:courier_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estado Courier')
