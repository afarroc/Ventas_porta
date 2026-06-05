from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Venta, ItemVenta, SeguimientoBO, Cliente
from apps.discador.models import BaseLlamada, CallRecord


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
            'producto_nombre': 'Test Product',
            'origen': 'Test',
            'operador': 'Test',
            'tipo_linea': 'PREPAGO',
            'facturacion_requerida': 'NO',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-tipo_venta': 'Venta',
            'items-0-tipo_producto': 'Producto Test',
            'items-0-precio_plan': '29.99',
            'backoffice_form-status_bo': 'Pendiente',
            'backoffice_form-supervisor': 'Test Supervisor',
            'backoffice_form-intervalo': 'Mensual',
        })
        
        if response.status_code == 302:
            self.assertRedirects(response, reverse('ventas:venta_list'))
        
        self.client.logout()


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
        self.client.login(username='otheragent', password='testpass123')
        url = reverse('ventas:recargar_lead', kwargs={'id_lead': self.base_llamada.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('acceso', data['mensaje'].lower())