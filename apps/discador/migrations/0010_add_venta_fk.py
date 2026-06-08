# Generated migration for Sprint 1 - Trazabilidad Lead → Venta

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discador', '0009_basellamada_base_manual_basellamada_base_procedencia'),
        ('ventas', '0015_remove_old_seguimientobo'),
    ]

    operations = [
        migrations.AddField(
            model_name='basellamada',
            name='venta',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='lead_venta',
                to='ventas.venta',
                help_text='Venta asociada generada desde este lead (trazabilidad)',
                verbose_name='Venta Generada'
            ),
        ),
    ]