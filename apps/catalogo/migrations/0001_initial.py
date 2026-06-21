# Generated manually for feature/catalogo-productos-retail.

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ProveedorCatalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código comercial: ENTEL, CLARO, VIRGIN, MOVISTAR.', max_length=30, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=120, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Proveedor de catálogo', 'verbose_name_plural': 'Proveedores de catálogo', 'db_table': 'catalogo_proveedor', 'ordering': ['codigo']},
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=80, unique=True, verbose_name='SKU')),
                ('tipo', models.CharField(choices=[('EQUIPO', 'Equipo'), ('CHIP', 'Chip')], max_length=20, verbose_name='Tipo')),
                ('marca', models.CharField(blank=True, max_length=120, verbose_name='Marca')),
                ('nombre', models.CharField(max_length=180, verbose_name='Nombre descriptivo')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('stock_actual', models.PositiveIntegerField(default=0, verbose_name='Stock actual')),
                ('stock_minimo', models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')),
                ('requiere_stock', models.BooleanField(default=False, help_text='Desactivado por defecto porque esta fase es catálogo comercial, no inventario.', verbose_name='Requiere control de stock')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('proveedor_principal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productos_principales', to='catalogo.proveedorcatalogo', verbose_name='Proveedor principal')),
            ],
            options={'verbose_name': 'Producto de catálogo', 'verbose_name_plural': 'Productos de catálogo', 'db_table': 'catalogo_producto', 'ordering': ['tipo', 'marca', 'nombre']},
        ),
        migrations.CreateModel(
            name='Oferta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_codigo', models.CharField(max_length=80, verbose_name='Código de plan')),
                ('plan_nombre', models.CharField(blank=True, max_length=180, verbose_name='Nombre de plan')),
                ('precio_plan_mensual', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precio mensual del plan')),
                ('precio_equipo', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precio del equipo')),
                ('tipo_linea', models.CharField(choices=[('PREPAGO', 'Prepago'), ('POSTPAGO', 'Postpago')], max_length=20, verbose_name='Tipo de línea')),
                ('origen', models.CharField(choices=[('PORTABILIDAD', 'Portabilidad'), ('LINEA_NUEVA', 'Línea nueva')], max_length=20, verbose_name='Origen')),
                ('meses_contrato', models.PositiveIntegerField(default=18, verbose_name='Meses de contrato')),
                ('prioridad', models.PositiveIntegerField(default=100, verbose_name='Prioridad')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('vigencia_desde', models.DateField(blank=True, null=True, verbose_name='Vigencia desde')),
                ('vigencia_hasta', models.DateField(blank=True, null=True, verbose_name='Vigencia hasta')),
                ('fuente', models.CharField(default='manual', max_length=60, verbose_name='Fuente')),
                ('confianza', models.CharField(choices=[('ALTA', 'Alta'), ('MEDIA', 'Media'), ('BAJA', 'Baja'), ('REVISION', 'Requiere revisión')], default='ALTA', max_length=20, verbose_name='Confianza')),
                ('requiere_revision', models.BooleanField(default=False, verbose_name='Requiere revisión')),
                ('observacion_comercial', models.TextField(blank=True, verbose_name='Observación comercial')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ofertas', to='catalogo.producto', verbose_name='Producto')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ofertas', to='catalogo.proveedorcatalogo', verbose_name='Proveedor')),
            ],
            options={'verbose_name': 'Oferta comercial', 'verbose_name_plural': 'Ofertas comerciales', 'db_table': 'catalogo_oferta', 'ordering': ['prioridad', 'plan_codigo', 'producto']},
        ),
        migrations.CreateModel(
            name='ChipCompatibilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('observacion', models.TextField(blank=True, verbose_name='Observación')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('equipo', models.ForeignKey(limit_choices_to={'tipo': 'EQUIPO'}, on_delete=django.db.models.deletion.CASCADE, related_name='compatibilidad_equipo', to='catalogo.producto', verbose_name='Equipo')),
                ('chip', models.ForeignKey(limit_choices_to={'tipo': 'CHIP'}, on_delete=django.db.models.deletion.CASCADE, related_name='compatibilidad_chip', to='catalogo.producto', verbose_name='Chip')),
            ],
            options={'verbose_name': 'Compatibilidad chip-equipo', 'verbose_name_plural': 'Compatibilidades chip-equipo', 'db_table': 'catalogo_chip_compatibilidad', 'ordering': ['equipo__nombre', 'chip__nombre']},
        ),
        migrations.AddConstraint(model_name='oferta', constraint=models.UniqueConstraint(fields=('producto', 'proveedor', 'plan_codigo', 'tipo_linea', 'origen', 'meses_contrato'), name='uq_catalogo_oferta_completa')),
        migrations.AddConstraint(model_name='chipcompatibilidad', constraint=models.UniqueConstraint(fields=('equipo', 'chip'), name='uq_catalogo_chip_compatibilidad')),
    ]
