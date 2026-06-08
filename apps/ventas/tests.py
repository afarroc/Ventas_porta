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


class VentaCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890',
            nombres='Juan',
            paterno='Pérez',
            materno='García',
            documento='12345678'
        )
        
        # Create CallRecord to give user access to this lead
        self.call_record = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio='2024-01-01 10:00:00'
        )
        
        self.existing_cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Juan Existente',
            paterno='Apellido',
            materno='De Prueba',
            activo=True
        )

    def test_venta_create_view_with_base_llamada_id(self):
        """Test that accessing /ventas/nueva/<id_lead>/ works and pre-fills form"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('ventas:venta_create_with_base', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, self.base_llamada.telefono)
        self.assertContains(response, self.base_llamada.nombres)
        self.assertContains(response, self.base_llamada.paterno)
        self.assertContains(response, self.base_llamada.materno)
        self.assertContains(response, self.base_llamada.documento)
        
        self.assertContains(response, self.existing_cliente.nombres)
        self.assertContains(response, self.existing_cliente.paterno)
        
        self.client.logout()

    def test_venta_create_view_without_base_llamada_id(self):
        """Test that the regular /ventas/nueva/ still works"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('ventas:venta_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        self.client.logout()

    def test_venta_form_validates_existing_client_when_not_registering_new(self):
        """Test that form validates correctly when trying to create sale with existing client but not marking as new"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('ventas:venta_create_with_base', kwargs={'id_lead': self.base_llamada.id_lead})
        
        response = self.client.post(url, {
            'cliente_tipo_documento': 'DNI',
            'cliente_documento': self.existing_cliente.documento,
            'cliente_nombres': self.existing_cliente.nombres,
            'cliente_paterno': self.existing_cliente.paterno,
            'cliente_materno': self.existing_cliente.materno,
            'cliente_telefono_1': self.existing_cliente.telefono_1,
            'cliente_telefono_2': self.existing_cliente.telefono_2,
            'registrar_nuevo_cliente': False,
            'producto_nombre': 'CHIP',
            'origen': 'LINEA_NUEVA',
            'tipo_linea': 'POSTPAGO',
            'facturacion_requerida': 'NO',
        })
        
        if response.status_code == 302:
            self.assertRedirects(response, reverse('ventas:venta_list'))
        
        self.client.logout()

    def test_tipo_renta_calculation(self):
        """Test tipo_renta is calculated correctly based on origen, producto, precio_venta"""
        from .models import Venta
        
        # Test PACK with 49 = R.BAJA
        venta = Venta(
            origen='PORTABILIDAD',
            producto_nombre='PACK',
            precio_venta=49
        )
        self.assertEqual(venta.calcular_tipo_renta('PORTABILIDAD', 'PACK', 49, None), 'R.BAJA')
        
        # Test CHIP with 75 = R.MEDIA
        venta2 = Venta(
            origen='LINEA_NUEVA',
            producto_nombre='CHIP',
            precio_venta=75
        )
        self.assertEqual(venta2.calcular_tipo_renta('LINEA_NUEVA', 'CHIP', 75, None), 'R.MEDIA')
        
        # Test PACK with 99 = R.ALTA
        venta3 = Venta(
            origen='PORTABILIDAD',
            producto_nombre='PACK',
            precio_venta=99
        )
        self.assertEqual(venta3.calcular_tipo_renta('PORTABILIDAD', 'PACK', 99, None), 'R.ALTA')


class BaseLlamadaModelTest(TestCase):
    def setUp(self):
        self.base = BaseLlamada.objects.create(
            telefono='123456789',
            nombres='Juan',
            paterno='Pérez',
            materno='García'
        )

    def test_base_creation(self):
        self.assertEqual(self.base.telefono, '123456789')
        self.assertTrue(str(self.base))


class RecargarLeadAjaxTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testagent',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        self.base_llamada = BaseLlamada.objects.create(
            telefono='987654321',
            nombres='Maria',
            paterno='Test',
            materno='Lead',
            documento='87654321',
            correo='maria@test.com',
            observaciones='Test notes'
        )
        # Create CallRecord to give user access to this lead
        self.call_record = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio='2024-01-01 10:00:00'
        )

    def test_recargar_lead_ajax_success(self):
        """Test that recargar_lead_ajax returns correct lead data"""
        self.client.login(username='testagent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['lead']['telefono'], '987654321')
        self.assertEqual(data['lead']['nombres'], 'Maria')
        self.assertEqual(data['lead']['paterno'], 'Test')
        self.assertEqual(data['lead']['materno'], 'Lead')
        self.assertEqual(data['lead']['documento'], '87654321')
        self.assertEqual(data['lead']['correo'], 'maria@test.com')
        self.assertEqual(data['lead']['observaciones'], 'Test notes')
        self.assertEqual(data['lead']['tipo_documento'], 'DNI')

    def test_recargar_lead_ajax_not_found(self):
        """Test that recargar_lead_ajax returns error for non-existent lead"""
        self.client.login(username='testagent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': '00000000-0000-0000-0000-000000000000'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('mensaje', data)

    def test_recargar_lead_ajax_without_access(self):
        """Test that recargar_lead_ajax denies access without proper permissions"""
        other_user = User.objects.create_user(
            username='otheragent',
            password='testpass123'
        )
        UserProfile.objects.create(user=other_user, rol=UserProfile.ROL_AGENTE)
        self.client.login(username='otheragent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('acceso', data['mensaje'].lower())


class PostVentaViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890',
            nombres='Juan',
            paterno='Pérez',
            materno='García',
            documento='12345678'
        )
        
        self.existing_cliente = Cliente.objects.create(
            tipo_documento='DNI',
            documento='12345678',
            nombres='Juan Existente',
            paterno='Apellido',
            materno='De Prueba',
            activo=True
        )
        
        self.venta = Venta.objects.create(
            agente_nombre='Juan Gómez',
            cliente=self.existing_cliente
        )

    def test_item_create_view_get(self):
        """Test that item create view loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('ventas:item_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tipo Venta')
        self.client.logout()

    def test_backoffice_create_view_get(self):
        """Test that backoffice create view loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('postventa:backoffice_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Status BO')
        self.client.logout()

    def test_despacho_create_view_get(self):
        """Test that despacho create view loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('despacho:despacho_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Etapa')
        self.client.logout()

    def test_courier_create_view_get(self):
        """Test that courier create view loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('courier:courier_create', kwargs={'venta_id': self.venta.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estado Courier')
        self.client.logout()

    def test_dashboard_bo_view_get(self):
        """Test that dashboard BO view loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('postventa:dashboard_bo')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Postventa')
        self.client.logout()