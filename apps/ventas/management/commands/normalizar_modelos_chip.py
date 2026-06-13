from django.core.management.base import BaseCommand
from apps.ventas.models import Venta


class Command(BaseCommand):
    help = 'Normaliza modelos de ventas CHIP: convierte valores no vacíos a cadena vacía'

    def handle(self, *args, **options):
        self.stdout.write("Normalizando modelos de ventas CHIP...")

        count = Venta.objects.filter(
            producto_nombre='CHIP'
        ).exclude(
            modelo_producto__in=['', '0']
        ).update(modelo_producto='')

        self.stdout.write(
            self.style.SUCCESS(f"✅ Normalizadas {count} ventas CHIP.")
        )
