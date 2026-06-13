from django.db import migrations, models
import uuid


def ensure_unique_id_lead(apps, schema_editor):
    seen = set()
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT `id`, `id_lead` FROM `discador_base`')
        rows = list(cursor.fetchall())

    with schema_editor.connection.cursor() as cursor:
        for lead_id, existing_id_lead in rows:
            val = existing_id_lead
            if val in seen or val is None or val == '':
                val = uuid.uuid4().hex
                while val in seen:
                    val = uuid.uuid4().hex
                cursor.execute('UPDATE `discador_base` SET `id_lead` = %s WHERE `id` = %s', [val, lead_id])
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
                    sql='ALTER TABLE `discador_base` ADD COLUMN `id_lead` char(32) NULL',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunPython(ensure_unique_id_lead, migrations.RunPython.noop),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` MODIFY `telefono` varchar(15) NOT NULL',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` MODIFY `id_lead` char(32) NOT NULL',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` ADD UNIQUE `uq_discador_base_telefono` (`telefono`)',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE `discador_base` ADD UNIQUE `uq_discador_base_id_lead` (`id_lead`)',
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
