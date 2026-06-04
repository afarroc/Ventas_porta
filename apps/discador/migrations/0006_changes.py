from django.db import migrations, models
import uuid


def ensure_unique_id_lead(apps, schema_editor):
    BaseLlamada = apps.get_model('discador', 'BaseLlamada')
    seen = set()
    for base in BaseLlamada.objects.all():
        val = base.id_lead
        if val in seen or val is None:
            val = uuid.uuid4()
            while val in seen:
                val = uuid.uuid4()
            base.id_lead = val
            base.save(update_fields=['id_lead'])
        seen.add(val)


class Migration(migrations.Migration):

    dependencies = [
        ('discador', '0005_add_liberado_sin_uso'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` DROP COLUMN IF EXISTS `numero_base`',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` MODIFY `telefono` varchar(15) NOT NULL',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` ADD CONSTRAINT UNIQUE (`telefono`)',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` ADD CONSTRAINT UNIQUE (`id_lead`)',
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='basellamada',
                    name='numero_base',
                ),
                migrations.AlterField(
                    model_name='basellamada',
                    name='id',
                    field=models.AutoField(primary_key=True, serialize=False, verbose_name='ID'),
                ),
                migrations.AlterField(
                    model_name='basellamada',
                    name='id_lead',
                    field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='ID Lead'),
                ),
                migrations.AlterField(
                    model_name='basellamada',
                    name='telefono',
                    field=models.CharField(max_length=15, unique=True, verbose_name='Teléfono'),
                ),
            ],
        ),
    ]
