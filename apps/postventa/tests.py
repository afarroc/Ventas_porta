from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.ventas.models import Venta, Cliente
from apps.discador.models import BaseLlamada
from apps.users.models import UserProfile
from .models import SeguimientoBO, HistorialEstado


class SeguimientoBOModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Pedro',
            paterno='López',
            materno='M',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Juan Gómez',
            cliente=self.cliente,
            cliente_nombres='Pedro',
            cliente_paterno='López',
            cliente_documento='12345678',
        )
        self.seguimiento = SeguimientoBO.objects.create(
            venta=self.venta,
            status_bo='PDTE_BO',
            supervisor='Carlos Ruiz',
        )

    def test_seguimiento_creation(self):
        self.assertEqual(self.seguimiento.venta, self.venta)
        self.assertEqual(self.seguimiento.status_bo, 'PDTE_BO')
        self.assertTrue(str(self.seguimiento))

    def test_seguimiento_one_to_one(self):
        # No se puede crear un segundo seguimiento para la misma venta
        with self.assertRaises(Exception):
            SeguimientoBO.objects.create(
                venta=self.venta,
                status_bo='EN_BO',
                supervisor='Otro',
            )


class HistorialEstadoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='87654321',
            nombres='Maria',
            paterno='García',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Agente Test',
            cliente=self.cliente,
            cliente_nombres='Maria',
            cliente_paterno='García',
            cliente_documento='87654321',
        )

    def test_historial_creation(self):
        historial = HistorialEstado.objects.create(
            venta=self.venta,
            area='BO',
            estado_anterior='PDTE_BO',
            estado_nuevo='EN_BO',
            usuario=self.user,
            observaciones='Cambio de estado',
        )
        self.assertEqual(historial.venta, self.venta)
        self.assertEqual(historial.area, 'BO')
        self.assertEqual(historial.estado_anterior, 'PDTE_BO')
        self.assertTrue(str(historial))

    def test_historial_ordering(self):
        h1 = HistorialEstado.objects.create(
            venta=self.venta, area='BO', estado_anterior='', estado_nuevo='PDTE_BO'
        )
        h2 = HistorialEstado.objects.create(
            venta=self.venta, area='BO', estado_anterior='PDTE_BO', estado_nuevo='EN_BO'
        )
        historiales = HistorialEstado.objects.filter(venta=self.venta)
        self.assertEqual(historiales[0], h2)
        self.assertEqual(historiales[1], h1)

    def test_historial_filtrado_por_area(self):
        HistorialEstado.objects.create(
            venta=self.venta, area='BO', estado_anterior='', estado_nuevo='PDTE_BO'
        )
        HistorialEstado.objects.create(
            venta=self.venta, area='DESPACHO', estado_anterior='', estado_nuevo='EN_PREPARACION'
        )
        bo_historial = HistorialEstado.objects.filter(venta=self.venta, area='BO')
        self.assertEqual(bo_historial.count(), 1)
        despacho_historial = HistorialEstado.objects.filter(venta=self.venta, area='DESPACHO')
        self.assertEqual(despacho_historial.count(), 1)


class BackofficeViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)

        self.cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='11111111',
            nombres='Test',
            paterno='Cliente',
            activo=True,
        )
        self.venta = Venta.objects.create(
            agente_nombre='Test Agent',
            cliente=self.cliente,
            cliente_nombres='Test',
            cliente_paterno='Cliente',
            cliente_documento='11111111',
        )

    def test_dashboard_bo_requires_login(self):
        url = reverse('postventa:dashboard_bo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/users/login/?next={url}')

    def test_dashboard_bo_loads(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('postventa:dashboard_bo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Postventa')
