# Generated migration for model updates
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0002_alter_venta_options_venta_contact_callable_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='cliente_nombres',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nombres'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_paterno',
            field=models.CharField(blank=True, max_length=50, verbose_name='Paterno'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_materno',
            field=models.CharField(blank=True, max_length=50, verbose_name='Materno'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_documento',
            field=models.CharField(blank=True, max_length=20, verbose_name='Documento'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_numero',
            field=models.CharField(blank=True, max_length=50, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_telefono_1',
            field=models.CharField(blank=True, max_length=20, verbose_name='Teléfono 01'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='cliente_telefono_2',
            field=models.CharField(blank=True, max_length=20, verbose_name='Teléfono 02'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='recibo_electronico',
            field=models.CharField(blank=True, choices=[('SI', 'Sí'), ('NO', 'No'), ('SI_DESEA', 'Si desea'), ('NO_DESEA', 'No desea')], max_length=10, verbose_name='Recibo Electrónico'),
        ),
    ]