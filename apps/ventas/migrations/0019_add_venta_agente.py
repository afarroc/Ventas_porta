from django.db import migrations, models
import django.db.models.deletion


def add_agente_column_if_missing(apps, schema_editor):
    table = 'ventas_venta'
    column = 'agente_id'
    db_name = schema_editor.connection.settings_dict['NAME']

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
            """,
            [db_name, table, column],
        )
        exists = cursor.fetchone()[0] > 0

    if not exists:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(f'ALTER TABLE `{table}` ADD COLUMN `{column}` int NULL')


def add_agente_fk_if_missing(apps, schema_editor):
    table = 'ventas_venta'
    column = 'agente_id'
    constraint = 'ventas_venta_agente_id_2b0b31b5_fk_auth_user_id'
    db_name = schema_editor.connection.settings_dict['NAME']

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
              AND CONSTRAINT_NAME = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """,
            [db_name, table, column, constraint],
        )
        exists = cursor.fetchone()[0] > 0

    if not exists:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                f"""
                ALTER TABLE `{table}`
                ADD CONSTRAINT `{constraint}`
                FOREIGN KEY (`{column}`) REFERENCES `auth_user` (`id`)
                """
            )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency('auth.User'),
        ('ventas', '0018_remove_transitory_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_agente_column_if_missing, migrations.RunPython.noop),
                migrations.RunPython(add_agente_fk_if_missing, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='venta',
                    name='agente',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ventas', to='auth.User', verbose_name='Agente'),
                ),
            ],
        ),
    ]
