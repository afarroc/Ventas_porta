from django.contrib.auth.models import User
from .models import HistorialEstado


def registrar_cambio_estado(venta, area, estado_anterior, estado_nuevo, usuario=None, observaciones=''):
    """
    Registra un cambio de estado en el historial de postventa.
    
    Args:
        venta: Instancia de Venta
        area: 'BO', 'DESPACHO' o 'COURIER'
        estado_anterior: Estado previo (puede ser vacío si es creación)
        estado_nuevo: Estado nuevo
        usuario: Instancia de User (opcional)
        observaciones: Texto adicional (opcional)
    """
    HistorialEstado.objects.create(
        venta=venta,
        area=area,
        estado_anterior=estado_anterior or '',
        estado_nuevo=estado_nuevo,
        usuario=usuario,
        observaciones=observaciones,
    )
