# Generated migration for Sprint 1 - Trazabilidad Lead → Venta

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discador', '0009_basellamada_base_manual_basellamada_base_procedencia'),
        ('ventas', '0015_remove_old_seguimientobo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basellamada',
            name='resultado_gestion',
            field=models.CharField(blank=True, choices=[('', 'Sin gestión'), ('GESTIONADO', 'Gestionado'), ('VENTA_CONVERTIDA', 'Venta Convertida')], max_length=100, verbose_name='Resultado de Gestión'),
        ),
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