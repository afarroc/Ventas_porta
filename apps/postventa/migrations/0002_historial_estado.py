# Generated migration for Sprint 2 - Historial de Estados

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('postventa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(choices=[('BO', 'Backoffice'), ('DESPACHO', 'Despacho'), ('COURIER', 'Courier')], max_length=10, verbose_name='Área')),
                ('estado_anterior', models.CharField(blank=True, max_length=50, verbose_name='Estado Anterior')),
                ('estado_nuevo', models.CharField(max_length=50, verbose_name='Estado Nuevo')),
                ('fecha_cambio', models.DateTimeField(auto_now_add=True, verbose_name='Fecha Cambio')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='historial_cambios', to='auth.user', verbose_name='Usuario')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_estados', to='ventas.venta')),
            ],
            options={
                'db_table': 'postventa_historial',
                'verbose_name': 'Historial Estado',
                'verbose_name_plural': 'Historial de Estados',
                'ordering': ['-fecha_cambio'],
            },
        ),
    ]