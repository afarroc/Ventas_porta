# Generated migration to remove transitory fields: base3, q_ventas
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0017_alter_itemventa_precio_plan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venta',
            name='agente_nombre',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_nombres',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_paterno',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_materno',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_documento',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_telefono_1',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_telefono_2',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cliente_tipo_documento',
        ),
        migrations.AlterField(
            model_name='venta',
            name='tipo_renta',
            field=models.CharField(blank=True, choices=[('R.BAJA', 'R.BAJA'), ('R.MEDIA', 'R.MEDIA'), ('R.ALTA', 'R.ALTA')], max_length=20, verbose_name='Tipo Renta'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='tipo_renta2',
            field=models.CharField(blank=True, choices=[('R.BAJA', 'R.BAJA'), ('R.MEDIA', 'R.MEDIA'), ('R.ALTA', 'R.ALTA')], max_length=20, verbose_name='Tipo Renta Multilínea', help_text='Calculado igual que tipo_renta, pero para la segunda línea o línea adicional'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='operador',
            field=models.CharField(blank=True, choices=[('CLARO', 'CLARO'), ('MOVISTAR', 'MOVISTAR'), ('VIETTEL', 'VIETTEL'), ('VIRGIN', 'VIRGIN')], max_length=20, verbose_name='Operador'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='precio_plan',
            field=models.IntegerField(blank=True, choices=[(29, '29'), (39, '39'), (45, '45'), (49, '49'), (59, '59'), (74, '74'), (75, '75'), (89, '89'), (99, '99'), (109, '109'), (145, '145'), (149, '149'), (199, '199')], null=True, verbose_name='Precio del Plan'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='precio_venta',
            field=models.IntegerField(blank=True, choices=[(1, '1'), (4, '4'), (9, '9'), (13, '13'), (29, '29'), (39, '39'), (49, '49'), (59, '59'), (79, '79'), (89, '89'), (99, '99'), (109, '109'), (119, '119'), (129, '129'), (149, '149'), (189, '189'), (199, '199'), (229, '229'), (249, '249'), (299, '299'), (349, '349'), (399, '399'), (429, '429'), (499, '499'), (599, '599'), (699, '699')], null=True, verbose_name='Precio de Venta'),
        ),
        migrations.RemoveField(
            model_name='venta',
            name='base3',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='q_ventas',
        ),
    ]
