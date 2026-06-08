import django.dispatch
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import SeguimientoBO, EstadoDespacho, EstadoCourier, HistorialEstado

from apps.despacho.models import EstadoDespacho
from apps.courier.models import EstadoCourier


@receiver(post_save, sender=SeguimientoBO)
def registrar_cambio_bo(sender, instance, created, **kwargs):
    """Registra cambio de estado en SeguimientoBO."""
    if created:
        HistorialEstado.objects.create(
            venta=instance.venta,
            area='BO',
            estado_anterior='',
            estado_nuevo=instance.status_bo,
            usuario=_get_usuario_desde_request(),
        )


@receiver(post_save, sender=EstadoDespacho)
def registrar_cambio_despacho(sender, instance, created, **kwargs):
    """Registra cambio de estado en EstadoDespacho."""
    if created:
        HistorialEstado.objects.create(
            venta=instance.venta,
            area='DESPACHO',
            estado_anterior='',
            estado_nuevo=instance.etapa,
            usuario=_get_usuario_desde_request(),
        )


@receiver(post_save, sender=EstadoCourier)
def registrar_cambio_courier(sender, instance, created, **kwargs):
    """Registra cambio de estado en EstadoCourier."""
    if created:
        HistorialEstado.objects.create(
            venta=instance.venta,
            area='COURIER',
            estado_anterior='',
            estado_nuevo=instance.sts_courier,
            usuario=_get_usuario_desde_request(),
        )


def _get_usuario_desde_request():
    """Helper para obtener usuario desde thread local (requiere middleware)."""
    # Placeholder - se implementará con middleware de request
    return None