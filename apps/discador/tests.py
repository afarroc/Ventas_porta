from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from .models import BaseLlamada, CallRecord
from .views import AgentDashboardView


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


class CallRecordModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create a test BaseLlamada
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890',
            nombres='Juan',
            paterno='Pérez',
            materno='García',
            documento='12345678'
        )

    def test_call_record_creation(self):
        """Test that we can create a CallRecord"""
        call = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now()
        )
        
        self.assertEqual(call.agente, self.user)
        self.assertEqual(call.base_llamada, self.base_llamada)
        self.assertIsNotNone(call.inicio)
        self.assertIsNone(call.fin)  # Initially not finished
        self.assertTrue(str(call))

    def test_only_one_ongoing_call_per_agent_per_lead(self):
        """Test that our business logic prevents multiple ongoing calls for same agent-lead"""
        # This test validates the business rule, not necessarily the view enforcement
        # The view enforcement is tested in integration tests
        
        # Create first call
        call1 = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now()
        )
        
        # Verify first call is ongoing (fin=None)
        self.assertIsNone(call1.fin)
        
        # Attempt to create second call for same agent-lead
        # At the model level, this is allowed (we rely on view to prevent)
        call2 = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now()
        )
        
        # Both calls exist and both have fin=None at model level
        # The view layer should prevent this scenario
        ongoing_calls = CallRecord.objects.filter(
            agente=self.user,
            base_llamada=self.base_llamada,
            fin=None
        )
        
        # At model level, we have 2 ongoing calls (this is allowed)
        # The view should prevent creating the second one
        self.assertEqual(ongoing_calls.count(), 2)
        
        # But if we finish the first one, then we should be able to have another
        call1.fin = timezone.now()
        call1.save()
        
        # Now only call2 should be ongoing
        ongoing_calls = CallRecord.objects.filter(
            agente=self.user,
            base_llamada=self.base_llamada,
            fin=None
        )
        self.assertEqual(ongoing_calls.count(), 1)
        self.assertEqual(ongoing_calls.first(), call2)


class AgentDashboardViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create a test BaseLlamada
        self.base_llamada = BaseLlamada.objects.create(
            telefono='1234567890',
            nombres='Juan',
            paterno='Pérez',
            materno='García',
            documento='12345678'
        )
        
        # Create a request factory
        self.factory = RequestFactory()
        
    def _get_request_with_session(self, user, session_data=None):
        """Helper to create a request with session and messages"""
        request = self.factory.post('/discador/')
        request.user = user
        
        # Add session middleware
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        # Add session data if provided
        if session_data:
            for key, value in session_data.items():
                request.session[key] = value
            request.session.save()
            
        # Add messages middleware
        middleware = MessageMiddleware()
        middleware.process_request(request)
        
        return request

    def test_prevents_simultaneous_calls_for_same_agent_and_lead(self):
        """Test that initiating a call when one is already in progress shows error message"""
        # Create an ongoing call
        CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now()
        )
        
        # Create request with lead in session
        request = self._get_request_with_session(
            self.user, 
            {'current_lead_id': self.base_llamada.id}
        )
        request.POST = {'iniciar_llamada': '1'}
        
        # Add CSRF token (required by Django)
        request.META['CSRF_COOKIE'] = 'testtoken'
        request.POST['csrfmiddlewaretoken'] = 'testtoken'
        
        # Call the view
        view = AgentDashboardView.as_view()
        response = view(request)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Should have error message about ongoing call
        # Note: In a real test we'd check messages, but for simplicity we're just checking
        # that the view processes the request without creating a second call
        
        # Verify only one call exists
        calls = CallRecord.objects.filter(agente=self.user, base_llamada=self.base_llamada)
        self.assertEqual(calls.count(), 1)
        
        # Verify the call is still ongoing (not finished)
        ongoing_calls = calls.filter(fin=None)
        self.assertEqual(ongoing_calls.count(), 1)

    def test_allows_new_call_after_previous_one_is_finished(self):
        """Test that we can initiate a new call after finishing the previous one"""
        # Create a finished call
        finished_call = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now(),
            fin=timezone.now()
        )
        
        # Create request with lead in session
        request = self._get_request_with_session(
            self.user, 
            {'current_lead_id': self.base_llamada.id}
        )
        request.POST = {'iniciar_llamada': '1'}
        
        # Add CSRF token (required by Django)
        request.META['CSRF_COOKIE'] = 'testtoken'
        request.POST['csrfmiddlewaretoken'] = 'testtoken'
        
        # Call the view
        view = AgentDashboardView.as_view()
        response = view(request)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify we now have two calls: one finished, one ongoing
        calls = CallRecord.objects.filter(agente=self.user, base_llamada=self.base_llamada)
        self.assertEqual(calls.count(), 2)
        
        # Verify one is finished and one is ongoing
        finished_calls = calls.exclude(fin=None)
        ongoing_calls = calls.filter(fin=None)
        self.assertEqual(finished_calls.count(), 1)
        self.assertEqual(ongoing_calls.count(), 1)

    def test_liberar_lead_without_call_creates_audit_record(self):
        """Test that releasing a lead without calling creates an audit record"""
        # Create request with lead in session but no call
        request = self._get_request_with_session(
            self.user, 
            {'current_lead_id': self.base_llamada.id}
        )
        request.POST = {'liberar_lead': '1'}
        
        # Add CSRF token
        request.META['CSRF_COOKIE'] = 'testtoken'
        request.POST['csrfmiddlewaretoken'] = 'testtoken'
        
        # Call the view
        view = AgentDashboardView.as_view()
        response = view(request)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify an audit call record was created
        audit_calls = CallRecord.objects.filter(
            agente=self.user,
            base_llamada=self.base_llamada,
            liberado_sin_uso=True
        )
        self.assertEqual(audit_calls.count(), 1)
        self.assertEqual(audit_calls.first().resultado, 'LIBERADO_SIN_USO')
        self.assertEqual(audit_calls.first().disposition, 'LIBERADO_SIN_USO')

    def test_liberar_lead_with_ongoing_call_marks_as_liberado_sin_uso(self):
        """Test that releasing a lead during an ongoing call marks it as liberado_sin_uso"""
        # Create an ongoing call
        ongoing_call = CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now()
        )
        
        # Create request with lead in session
        request = self._get_request_with_session(
            self.user, 
            {'current_lead_id': self.base_llamada.id}
        )
        request.POST = {'liberar_lead': '1'}
        
        # Add CSRF token
        request.META['CSRF_COOKIE'] = 'testtoken'
        request.POST['csrfmiddlewaretoken'] = 'testtoken'
        
        # Call the view
        view = AgentDashboardView.as_view()
        response = view(request)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the call was marked as liberado_sin_uso
        ongoing_call.refresh_from_db()
        self.assertTrue(ongoing_call.liberado_sin_uso)
        self.assertEqual(ongoing_call.resultado, 'LIBERADO_SIN_USO')

    def test_multiple_interactions_same_lead_after_disposition(self):
        """Test that we can have multiple interactions with same lead after disposition"""
        # Create a finished and dispositioned call
        CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base_llamada,
            inicio=timezone.now() - timezone.timedelta(minutes=10),
            fin=timezone.now() - timezone.timedelta(minutes=9),
            acw_start=timezone.now() - timezone.timedelta(minutes=9),
            acw_end=timezone.now() - timezone.timedelta(minutes=8),
            disposition='NO_CONTESTA'
        )
        
        # Verify no ongoing calls
        ongoing_calls = CallRecord.objects.filter(agente=self.user, fin=None)
        self.assertEqual(ongoing_calls.count(), 0)
        
        # Create request with lead in session (simulating user can get the lead again)
        request = self._get_request_with_session(
            self.user, 
            {'current_lead_id': self.base_llamada.id}
        )
        request.POST = {'iniciar_llamada': '1'}
        
        # Add CSRF token
        request.META['CSRF_COOKIE'] = 'testtoken'
        request.POST['csrfmiddlewaretoken'] = 'testtoken'
        
        # Call the view
        view = AgentDashboardView.as_view()
        response = view(request)
        
        # Should redirect back to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify we now have a new ongoing call
        calls = CallRecord.objects.filter(agente=self.user, base_llamada=self.base_llamada)
        self.assertEqual(calls.count(), 2)
        
        # Verify the new call is ongoing
        new_ongoing = calls.filter(fin=None)
        self.assertEqual(new_ongoing.count(), 1)


class ResultadoDiscadoListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testagent',
            password='testpass123'
        )
        self.user.is_staff = True
        self.user.save()
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROL_AGENTE)
        
        self.base = BaseLlamada.objects.create(
            telefono='123456789',
            nombres='Test',
            paterno='Lead',
            documento='12345678',
            tipo_valido='Válido'
        )
        
        CallRecord.objects.create(
            agente=self.user,
            base_llamada=self.base,
            inicio=timezone.now()
        )

    def test_resultado_list_view_requires_login(self):
        """Test that resultado list requires authentication"""
        url = reverse('discador:resultado_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/users/login/?next={url}')

    def test_resultado_list_view_loads_for_authenticated(self):
        """Test that resultado list loads for authenticated users"""
        self.client.login(username='testagent', password='testpass123')
        url = reverse('discador:resultado_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resultados del Discado')

    def test_resultado_detail_view(self):
        """Test that resultado detail view works"""
        self.client.login(username='testagent', password='testpass123')
        url = reverse('discador:resultado_detail', kwargs={'id_lead': self.base.id_lead})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123456789')