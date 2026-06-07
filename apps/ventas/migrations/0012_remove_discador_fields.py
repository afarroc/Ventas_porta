# Generated migration to remove duplicated discador fields from Venta model
# These fields exist in BaseLlamada and should be accessed via FK relationship

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('ventas', '0011_add_centro_poblado'),
    ]

    operations = [
        # Gestión del Discador fields - redundant with BaseLlamada
        migrations.RemoveField(
            model_name='venta',
            name='contact_callable',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='es_callable',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='fecha_gestion',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='hora_gestion',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='resultado_gestion',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='tipo_contacto',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='tipo_valido',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='status_java',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='supervisor_nombre',
        ),
        # Reduntante timestamp fields - use Venta.creado/actualizado instead
        migrations.RemoveField(
            model_name='venta',
            name='fecha_venta',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='hora_venta',
        ),
    ]