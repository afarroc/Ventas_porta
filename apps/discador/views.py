from django.views.generic import ListView
from .models import BaseLlamada


class BaseLlamadaListView(ListView):
    model = BaseLlamada
    template_name = 'discador/base_llamada_list.html'
    context_object_name = 'bases'
    paginate_by = 50
