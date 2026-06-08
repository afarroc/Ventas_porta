from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Venta, ItemVenta, Cliente
from apps.discador.models import BaseLlamada, CallRecord
from apps.users.models import UserProfile
from apps.postventa.models import SeguimientoBO


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
            precio_plan=29
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

    def test_tipo_renta_calculation(self):
        """Test tipo_renta is calculated correctly based on origen, producto, precio_venta"""
        # PACK PORTABILIDAD - R.BAJA (29-49)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 29, None), 'R.BAJA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 49, None), 'R.BAJA')
        # PACK PORTABILIDAD - R.MEDIA (59-75)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 59, None), 'R.MEDIA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 75, None), 'R.MEDIA')
        # PACK PORTABILIDAD - R.ALTA (89+)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 89, None), 'R.ALTA')

        # CHIP PORTABILIDAD - R.BAJA (39-59)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 39, None), 'R.BAJA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 59, None), 'R.BAJA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 38, None), 'R.ALTA')
        # CHIP PORTABILIDAD - R.MEDIA (74-89)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 74, None), 'R.MEDIA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 89, None), 'R.MEDIA')
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 73, None), 'R.ALTA')
        # CHIP PORTABILIDAD - R.ALTA (109+)
        self.assertEqual(Venta.calcular_tipo_renta('PORTABILIDAD', 'CHIP', 109, None), 'R.ALTA')

        # CHIP LINEA_NUEVA - R.BAJA (25-45)
        self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 25, None), 'R.BAJA')
        self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 45, None), 'R.BAJA')
        # CHIP LINEA_NUEVA - R.MEDIA (59+)
        self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 59, None), 'R.MEDIA')
        self.assertEqual(Venta.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 79, None), 'R.MEDIA')


class VentaCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890', nombres='Juan', paterno='Pérez', materno='García', documento='12345678'
        )
        self.call_record = CallRecord.objects.create(
            agente=self.user, base_llamada=self.base_llamada, inicio='2024-01-01 10:00:00'
        )
        self.existing_cliente = Cliente.objects.create(
            tipo_documento='DNI', documento='12345678',
            nombres='Juan Existente', paterno='Apellido', materno='De Prueba', activo=True
        )

    def test_venta_create_view_with_base_llamada_id(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('ventas:venta_create_with_base', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.base_llamada.telefono)
        self.client.logout()

    def test_venta_create_view_without_base_llamada_id(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('ventas:venta_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()


class BaseLlamadaModelTest(TestCase):
    def setUp(self):
        self.base = BaseLlamada.objects.create(
            telefono='123456789', nombres='Juan', paterno='Pérez', materno='García'
        )

    def test_base_creation(self):
        self.assertEqual(self.base.telefono, '123456789')
        self.assertTrue(str(self.base))


class RecargarLeadAjaxTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testagent', password='testpass123')
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        self.base_llamada = BaseLlamada.objects.create(
            telefono='987654321', nombres='Maria', paterno='Test', materno='Lead',
            documento='87654321', correo='maria@test.com', observaciones='Test notes'
        )
        self.call_record = CallRecord.objects.create(
            agente=self.user, base_llamada=self.base_llamada, inicio='2024-01-01 10:00:00'
        )

    def test_recargar_lead_ajax_success(self):
        self.client.login(username='testagent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['lead']['telefono'], '987654321')
        self.client.logout()

    def test_recargar_lead_ajax_not_found(self):
        self.client.login(username='testagent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['ok'])
        self.client.logout()

    def test_recargar_lead_ajax_without_access(self):
        other_user = User.objects.create_user(username='otheragent', password='testpass123')
        UserProfile.objects.create(user=other_user, rol=UserProfile.ROL_AGENTE)
        self.client.login(username='otheragent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('acceso', data['mensaje'].lower())
        self.client.logout()


class PostVentaViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890', nombres='Juan', paterno='Pérez', materno='García', documento='12345678'
        )
        self.existing_cliente = Cliente.objects.create(
            tipo_documento='DNI', documento='12345678',
            nombres='Juan Existente', paterno='Apellido', materno='De Prueba', activo=True
        )
        self.venta = Venta.objects.create(agente_nombre='Juan Gómez', cliente=self.existing_cliente)

    def test_item_create_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('ventas:item_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tipo Venta')
        self.client.logout()

    def test_backoffice_create_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('postventa:backoffice_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Status BO')
        self.client.logout()

    def test_despacho_create_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('despacho:despacho_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_courier_create_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('courier:courier_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_dashboard_bo_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('postventa:dashboard_bo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Postventa')
        self.client.logout()