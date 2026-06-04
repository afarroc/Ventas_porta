# apps/users/views.py
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context['agente_nombre'] = user.get_full_name() or user.username
        context['codigo_agente'] = profile.codigo_agente
        context['rol'] = profile.get_rol_display()
        context['supervisor'] = profile.supervisor.user.get_full_name() if profile.supervisor else 'Sin supervisor'
        context['zona'] = profile.zona
        return context


def logout_view(request):
    logout(request)
    return redirect('users:login')