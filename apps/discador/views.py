from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, OuterRef, Subquery
from .models import BaseLlamada, CallRecord
from apps.users.models import UserProfile


class BaseLlamadaListView(ListView):
    model = BaseLlamada
    template_name = 'discador/base_llamada_list.html'
    context_object_name = 'bases'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        try:
            profile = self.request.user.profile
            if profile.rol == UserProfile.ROL_ADMIN:
                # Admin sees all leads
                pass
            elif profile.rol == UserProfile.ROL_SUPERVISOR:
                # Supervisor sees leads managed by themselves and their direct subordinates
                supervised_user_ids = UserProfile.objects.filter(supervisor__user=self.request.user).values_list('user_id', flat=True)
                supervised_user_ids = list(supervised_user_ids) + [self.request.user.id]
                queryset = queryset.filter(llamadas__agente__in=supervised_user_ids).distinct()
            else:
                # Regular agent: only leads they have managed
                queryset = queryset.filter(llamadas__agente=self.request.user).distinct()
        except UserProfile.DoesNotExist:
            # If no profile, treat as agent with no leads
            queryset = queryset.none()

# Annotate with the last call agent and disposition for each base
        latest_call = CallRecord.objects.filter(
            base_llamada=OuterRef('pk')
        ).order_by('-inicio')

        queryset = queryset.annotate(
            last_call_agent=Subquery(latest_call.values('agente__username')[:1]),
            last_call_disposition=Subquery(latest_call.values('disposition')[:1])
        ).distinct()

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(telefono__icontains=query) |
                Q(nombres__icontains=query) |
                Q(paterno__icontains=query) |
                Q(materno__icontains=query) |
                Q(documento__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Bases de Llamada'
        context['total_records'] = self.get_queryset().count()
        context['search_query'] = self.request.GET.get('q', '')
        return context


class BaseLlamadaDetailView(DetailView):
    model = BaseLlamada
    template_name = 'discador/base_llamada_detail.html'
    context_object_name = 'base'

    def get_queryset(self):
        queryset = BaseLlamada.objects.all()
        if not self.request.user.is_authenticated:
            return queryset.none()
        try:
            profile = self.request.user.profile
            if profile.rol == UserProfile.ROL_ADMIN:
                pass
            elif profile.rol == UserProfile.ROL_SUPERVISOR:
                supervised_user_ids = UserProfile.objects.filter(supervisor__user=self.request.user).values_list('user_id', flat=True)
                supervised_user_ids = list(supervised_user_ids) + [self.request.user.id]
                queryset = queryset.filter(id__in=CallRecord.objects.filter(agente__in=supervised_user_ids).values_list('base_llamada_id', flat=True))
            else:
                queryset = queryset.filter(id__in=CallRecord.objects.filter(agente=self.request.user).values_list('base_llamada_id', flat=True))
        except UserProfile.DoesNotExist:
            queryset = queryset.none()
        return queryset


class AgentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'discador/agent_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context['profile'] = profile
        
        lead_id = self.request.session.get('current_lead_id')
        if lead_id:
            try:
                context['current_lead'] = BaseLlamada.objects.get(id=lead_id)
            except BaseLlamada.DoesNotExist:
                context['current_lead'] = None
                self.request.session.pop('current_lead_id', None)
        else:
            context['current_lead'] = None
        
        ongoing_call = CallRecord.objects.filter(agente=user, fin=None).order_by('-inicio').first()
        context['ongoing_call'] = ongoing_call
        context['pending_disposition'] = CallRecord.objects.filter(
            agente=user, fin__isnull=False, acw_end__isnull=True
        ).order_by('-inicio').first()
        
        # Determine active lead for display
        if ongoing_call:
            context['active_lead'] = ongoing_call.base_llamada
        elif context['current_lead']:
            context['active_lead'] = context['current_lead']
        elif context['pending_disposition']:
            context['active_lead'] = context['pending_disposition'].base_llamada
        else:
            context['active_lead'] = None
        
        return context

    def post(self, request, *args, **kwargs):
        # Handle status change
        if 'cambiar_estado' in request.POST:
            nuevo_estado = request.POST.get('estado')
            profile = request.user.profile
            profile.estado = nuevo_estado
            profile.save()
            messages.success(request, f"Estado cambiado a {dict(UserProfile.ESTADO_CHOICES).get(nuevo_estado, nuevo_estado)}")
            return redirect('discador:agent_dashboard')

        # Handle getting a lead
        if 'obtener_lead' in request.POST:
            # Only if available
            profile = request.user.profile
            if profile.estado == UserProfile.ESTADO_DISPONIBLE:
                # Check if there is already a lead in session or an ongoing/stuck call
                current_lead_id = request.session.get('current_lead_id')
                ongoing_call = CallRecord.objects.filter(agente=request.user, fin=None).exists()
                if current_lead_id or ongoing_call:
                    messages.error(request, "Debe finalizar el lead actual antes de obtener uno nuevo.")
                else:
                    # Get a random BaseLlamada that the agent has NOT managed yet
                    lead = BaseLlamada.objects.exclude(llamadas__agente=request.user).order_by('?').first()
                    if lead:
                        request.session['current_lead_id'] = lead.id
                        messages.success(request, f"Lead asignado: {lead.telefono}")
                    else:
                        messages.warning(request, "No hay leads disponibles que usted no haya gestionado.")
            else:
                messages.error(request, "Solo puedes obtener un lead si estás disponible.")
            return redirect('discador:agent_dashboard')

        # Handle call start
        if 'iniciar_llamada' in request.POST:
            lead_id = request.session.get('current_lead_id')
            if lead_id:
                try:
                    lead = BaseLlamada.objects.get(id=lead_id)
                    # VALIDATION: Check if there's already an ongoing call for this agent and lead
                    ongoing_call_exists = CallRecord.objects.filter(
                        agente=request.user,
                        base_llamada=lead,
                        fin=None
                    ).exists()
                    
                    if ongoing_call_exists:
                        messages.error(request, "Ya tienes una llamada en curso para este lead. Por favor, finalízala primero.")
                    else:
                        # Check if there's a pending disposition for this lead
                        pending_for_same_lead = CallRecord.objects.filter(
                            agente=request.user,
                            base_llamada=lead,
                            fin__isnull=False,
                            acw_end__isnull=True
                        ).exists()
                        if pending_for_same_lead:
                            messages.error(request, "Debe tipificar la llamada anterior antes de iniciar una nueva con el mismo lead.")
                        else:
                            # Create a CallRecord
                            CallRecord.objects.create(
                                agente=request.user,
                                base_llamada=lead,
                                inicio=timezone.now()
                            )
                            messages.success(request, "Llamada iniciada.")
                except BaseLlamada.DoesNotExist:
                    messages.error(request, "Lead no encontrado.")
                    request.session.pop('current_lead_id', None)
            else:
                messages.error(request, "No hay lead asignado.")
            return redirect('discador:agent_dashboard')

        # Handle call finish (sets fin and acw_start)
        if 'finalizar_llamada' in request.POST:
            lead_id = request.session.get('current_lead_id')
            ongoing_call = None
            if lead_id:
                # Find the ongoing call for this agent and lead (most recent without fin)
                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada_id=lead_id,
                    fin=None
                ).order_by('-inicio').first()
            else:
                # Buscar llamada pegada (en curso sin lead en sesión)
                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    fin=None
                ).order_by('-inicio').first()
            
            if ongoing_call:
                ongoing_call.fin = timezone.now()
                ongoing_call.acw_start = ongoing_call.fin  # ACW starts right after the call
                ongoing_call.save()  # This will update the BaseLlamada via the save method
                # Restore lead_id to session for disposition step
                request.session['current_lead_id'] = ongoing_call.base_llamada.id
                messages.success(request, "Llamada finalizada. Ahora puede tipificar el registro.")
            else:
                messages.error(request, "No hay llamada en curso para finalizar.")
            return redirect('discador:agent_dashboard')

        # Handle disposition submission
        if 'submit_disposition' in request.POST:
            pending_disposition_id = request.POST.get('pending_disposition_id')
            if pending_disposition_id:
                try:
                    disposition_call = CallRecord.objects.get(
                        id=pending_disposition_id,
                        agente=request.user,
                        fin__isnull=False,
                        acw_end__isnull=True
                    )
                    disposition_call.acw_end = timezone.now()
                    disposition_call.disposition = request.POST.get('disposition')
                    disposition_call.observaciones = request.POST.get('observaciones', '')
                    disposition_call.save()
                    # Keep lead_id in session to allow another interaction
                    # Lead remains in session until user clicks "Obtener Lead" or releases manually
                    messages.success(request, "Tipificación guardada correctamente. Puede iniciar otra llamada con este lead.")
                except CallRecord.DoesNotExist:
                    messages.error(request, "No se encontró la llamada pendiente de tipificación.")
            else:
                messages.error(request, "ID de llamada pendiente no proporcionado.")
            return redirect('discador:agent_dashboard')

        # For now, hold and transfer just show a message
        if 'hold_llamada' in request.POST:
            messages.info(request, "Llamada en espera (funcionalidad no implementada).")
            return redirect('discador:agent_dashboard')

        if 'transferir_llamada' in request.POST:
            messages.info(request, "Llamada transferida (funcionalidad no implementada).")
            return redirect('discador:agent_dashboard')

# Handle lead release
        if 'liberar_lead' in request.POST:
            lead_id = request.session.get('current_lead_id')
            if lead_id:
                lead = BaseLlamada.objects.get(id=lead_id)
                
                # Get ongoing call for this lead
                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada_id=lead_id,
                    fin=None
                ).order_by('-inicio').first()
                
                # Check if there are ANY completed calls with this lead (fin is set)
                # Una llamada con fin registrado significa que ocurrió, sin importar acw_end
                any_completed_calls = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada_id=lead_id,
                    fin__isnull=False
                ).exists()
                
                if ongoing_call:
                    if not any_completed_calls:
                        # This is the ONLY call (ongoing) and has not been completed before
                        # Mark as liberado sin uso
                        ongoing_call.fin = timezone.now()
                        ongoing_call.acw_start = ongoing_call.fin
                        ongoing_call.resultado = 'LIBERADO_SIN_USO'
                        ongoing_call.liberado_sin_uso = True
                        ongoing_call.save()
                        messages.warning(request, "Llamada liberada sin uso. Registro guardado para auditoría.")
                    else:
                        # Has completed calls before - just finish this call
                        ongoing_call.fin = timezone.now()
                        ongoing_call.acw_start = ongoing_call.fin
                        ongoing_call.save()
                        messages.info(request, "Llamada finalizada. Lead liberado.")
                else:
                    pending_exists = CallRecord.objects.filter(
                        agente=request.user,
                        base_llamada_id=lead_id,
                        fin__isnull=False,
                        acw_end__isnull=True
                    ).exists()
                    if pending_exists:
                        messages.error(request, "Complete la tipificación antes de liberar el lead.")
                    elif any_completed_calls:
                        messages.info(request, "Lead liberado. Puede obtener un nuevo lead.")
                    else:
                        # Lead obtained but never called at all
                        now = timezone.now()
                        CallRecord.objects.create(
                            agente=request.user,
                            base_llamada=lead,
                            inicio=now,
                            fin=now,
                            acw_start=now,
                            acw_end=now,
                            resultado='LIBERADO_SIN_USO',
                            disposition='LIBERADO_SIN_USO',
                            liberado_sin_uso=True,
                            observaciones='Lead liberado sin iniciar llamada'
                        )
                        messages.warning(request, "Lead liberado sin uso. Registro guardado para auditoría.")
            
            request.session.pop('current_lead_id', None)
            return redirect('discador:agent_dashboard')

        return super().post(request, *args, **kwargs)