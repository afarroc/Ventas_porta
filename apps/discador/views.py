from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, OuterRef, Subquery
from django.http import JsonResponse, Http404
from .models import BaseLlamada, CallRecord, TIPO_VALIDO
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
                pass
            elif profile.rol == UserProfile.ROL_SUPERVISOR:
                supervised_user_ids = UserProfile.objects.filter(supervisor__user=self.request.user).values_list('user_id', flat=True)
                supervised_user_ids = list(supervised_user_ids) + [self.request.user.id]
                queryset = queryset.filter(llamadas__agente__in=supervised_user_ids).distinct()
            else:
                queryset = queryset.filter(llamadas__agente=self.request.user).distinct()
        except UserProfile.DoesNotExist:
            queryset = queryset.none()

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
                context['current_lead'] = BaseLlamada.objects.get(id_lead=lead_id)
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
        if 'cambiar_estado' in request.POST:
            nuevo_estado = request.POST.get('estado')
            profile = request.user.profile
            profile.disponibilidad = nuevo_estado
            profile.save()
            messages.success(request, f"Disponibilidad cambiada a {dict(profile.DISPONIBILIDAD_CHOICES).get(nuevo_estado, nuevo_estado)}")
            return redirect('discador:agent_dashboard')

        if 'obtener_lead' in request.POST:
            profile = request.user.profile
            if profile.disponibilidad != UserProfile.DISPONIBLE:
                messages.error(request, "Debe estar disponible para obtener un lead.")
                return redirect('discador:agent_dashboard')

            current_lead_id = request.session.get('current_lead_id')
            ongoing_call = CallRecord.objects.filter(agente=request.user, fin=None).exists()
            if current_lead_id or ongoing_call:
                messages.error(request, "Debe finalizar el lead actual antes de obtener uno nuevo.")
            else:
                lead = BaseLlamada.objects.exclude(llamadas__agente=request.user).order_by('?').first()
                if lead:
                    request.session['current_lead_id'] = str(lead.id_lead)
                    messages.success(request, f"Lead asignado: {lead.telefono}")
                else:
                    messages.warning(request, "No hay leads disponibles que usted no haya gestionado.")
            return redirect('discador:agent_dashboard')

        if 'iniciar_llamada' in request.POST:
            lead_id = request.session.get('current_lead_id')
            if lead_id:
                try:
                    lead = BaseLlamada.objects.get(id_lead=lead_id)
                    ongoing_call_exists = CallRecord.objects.filter(
                        agente=request.user,
                        base_llamada=lead,
                        fin=None
                    ).exists()

                    if ongoing_call_exists:
                        messages.error(request, "Ya tienes una llamada en curso para este lead. Por favor, finalízala primero.")
                    else:
                        pending_for_same_lead = CallRecord.objects.filter(
                            agente=request.user,
                            base_llamada=lead,
                            fin__isnull=False,
                            acw_end__isnull=True
                        ).exists()
                        if pending_for_same_lead:
                            messages.error(request, "Debe tipificar la llamada anterior antes de iniciar una nueva con el mismo lead.")
                        else:
                            CallRecord.objects.create(
                                agente=request.user,
                                base_llamada=lead,
                                inicio=timezone.now()
                            )
                            profile = request.user.profile
                            profile.disponibilidad = UserProfile.EN_LLAMADA
                            profile.save()
                            messages.success(request, "Llamada iniciada.")
                except BaseLlamada.DoesNotExist:
                    messages.error(request, "Lead no encontrado.")
                    request.session.pop('current_lead_id', None)
            else:
                messages.error(request, "No hay lead asignado.")
            return redirect('discador:agent_dashboard')

        if 'finalizar_llamada' in request.POST:
            lead_id = request.session.get('current_lead_id')
            ongoing_call = None
            if lead_id:
                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada__id_lead=lead_id,
                    fin=None
                ).order_by('-inicio').first()
            else:
                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    fin=None
                ).order_by('-inicio').first()

            if ongoing_call:
                ongoing_call.fin = timezone.now()
                ongoing_call.acw_start = ongoing_call.fin
                ongoing_call.save()
                profile = request.user.profile
                profile.disponibilidad = UserProfile.LISTO_NO
                profile.save()
                request.session['current_lead_id'] = str(ongoing_call.base_llamada.id_lead)
                messages.success(request, "Llamada finalizada. Ahora puede tipificar el registro.")
            else:
                messages.error(request, "No hay llamada en curso para finalizar.")
            return redirect('discador:agent_dashboard')

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
                    profile = request.user.profile
                    profile.disponibilidad = UserProfile.DISPONIBLE
                    profile.save()
                    messages.success(request, "Tipificación guardada correctamente. Puede iniciar otra llamada con este lead.")
                except CallRecord.DoesNotExist:
                    messages.error(request, "No se encontró la llamada pendiente de tipificación.")
            else:
                messages.error(request, "ID de llamada pendiente no proporcionado.")
            return redirect('discador:agent_dashboard')

        if 'hold_llamada' in request.POST:
            messages.info(request, "Llamada en espera (funcionalidad no implementada).")
            return redirect('discador:agent_dashboard')

        if 'transferir_llamada' in request.POST:
            messages.info(request, "Llamada transferida (funcionalidad no implementada).")
            return redirect('discador:agent_dashboard')

        if 'liberar_lead' in request.POST:
            lead_id = request.session.get('current_lead_id')
            if lead_id:
                lead = BaseLlamada.objects.get(id_lead=lead_id)

                ongoing_call = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada__id_lead=lead_id,
                    fin=None
                ).order_by('-inicio').first()

                any_completed_calls = CallRecord.objects.filter(
                    agente=request.user,
                    base_llamada__id_lead=lead_id,
                    fin__isnull=False
                ).exists()

                if ongoing_call:
                    if not any_completed_calls:
                        ongoing_call.fin = timezone.now()
                        ongoing_call.acw_start = ongoing_call.fin
                        ongoing_call.resultado = 'LIBERADO_SIN_USO'
                        ongoing_call.liberado_sin_uso = True
                        ongoing_call.save()
                        messages.warning(request, "Llamada liberada sin uso. Registro guardado para auditoría.")
                    else:
                        ongoing_call.fin = timezone.now()
                        ongoing_call.acw_start = ongoing_call.fin
                        if not ongoing_call.resultado:
                            ongoing_call.resultado = 'NO_CONTESTADA'
                        ongoing_call.save()
                        messages.info(request, "Llamada finalizada. Lead liberado.")
                else:
                    pending_exists = CallRecord.objects.filter(
                        agente=request.user,
                        base_llamada__id_lead=lead_id,
                        fin__isnull=False,
                        acw_end__isnull=True
                    ).exists()
                    if pending_exists:
                        messages.error(request, "Complete la tipificación antes de liberar el lead.")
                    elif any_completed_calls:
                        messages.info(request, "Lead liberado. Puede obtener un nuevo lead.")
                    else:
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
            profile = request.user.profile
            profile.disponibilidad = UserProfile.DISPONIBLE
            profile.save()
            return redirect('discador:agent_dashboard')

        return super().post(request, *args, **kwargs)


def check_incoming_call(request):
    if not request.user.is_authenticated:
        return JsonResponse({'has_incoming': False})

    try:
        profile = request.user.profile
        if profile.disponibilidad != UserProfile.DISPONIBLE:
            return JsonResponse({'has_incoming': False})
    except:
        return JsonResponse({'has_incoming': False})

    incoming = CallRecord.objects.filter(
        agente=request.user,
        fin=None
    ).first()

    if incoming:
        return JsonResponse({
            'has_incoming': True,
            'call': {
                'telefono': incoming.base_llamada.telefono,
                'id': str(incoming.base_llamada.id_lead)
            }
        })

    return JsonResponse({'has_incoming': False})


class ResultadoDiscadoListView(LoginRequiredMixin, ListView):
    """Vista de resultados del discado - accesible por agente/supervisor."""
    model = BaseLlamada
    template_name = 'discador/resultado_discado_list.html'
    context_object_name = 'leads'
    paginate_by = 50

    def get_queryset(self):
        queryset = BaseLlamada.objects.all().prefetch_related(
            'llamadas',
            'venta_set'
        )
        
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            if profile.rol == UserProfile.ROL_ADMIN:
                pass
            elif profile.rol == UserProfile.ROL_SUPERVISOR:
                supervised_ids = list(
                    UserProfile.objects.filter(supervisor__user=self.request.user)
                    .values_list('user_id', flat=True)
                ) + [self.request.user.id]
                queryset = queryset.filter(
                    llamadas__agente__in=supervised_ids
                ).distinct()
            else:
                queryset = queryset.filter(
                    llamadas__agente=self.request.user
                ).distinct()

        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_desde:
            queryset = queryset.filter(fecha_gestion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_gestion__lte=fecha_hasta)

        tipo_valido = self.request.GET.get('tipo_valido')
        if tipo_valido:
            queryset = queryset.filter(tipo_valido=tipo_valido)

        resultado = self.request.GET.get('resultado')
        if resultado:
            queryset = queryset.filter(resultado_gestion=resultado)

        return queryset.order_by('-fecha_gestion', '-hora_gestion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Resultados del Discado'
        context['TIPO_VALIDO_CHOICES'] = TIPO_VALIDO
        return context


class ResultadoDiscadoDetailView(LoginRequiredMixin, DetailView):
    """Detalle de resultados de un lead específico."""
    model = BaseLlamada
    template_name = 'discador/resultado_discado_detail.html'
    context_object_name = 'base'

    def get_object(self, queryset=None):
        from uuid import UUID
        try:
            uuid_val = UUID(str(self.kwargs['id_lead']))
        except (ValueError, TypeError):
            raise Http404("Lead no encontrado")

        try:
            return BaseLlamada.objects.prefetch_related(
                'llamadas',
                'venta_set'
            ).get(id_lead=uuid_val)
        except BaseLlamada.DoesNotExist:
            raise Http404("Lead no encontrado")