from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discador', '0007_alter_basellamada_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callrecord',
            name='resultado',
            field=models.CharField(blank=True, choices=[('CONTESTADA', 'Contestada'), ('NO_CONTESTADA', 'No contestada'), ('OCUPADA', 'Ocupada'), ('DESCONECTADA', 'Desconectada'), ('NO_VOZ', 'No voz'), ('FAX', 'Fax'), ('OTRO', 'Otro'), ('LIBERADO_SIN_USO', 'Liberado sin uso')], default='', max_length=20),
        ),
    ]