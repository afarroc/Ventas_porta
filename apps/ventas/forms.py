from decimal import Decimal

from django import forms
from .models import Venta, ItemVenta, Cliente, PLANES_CHIP, MODELOS_CHIP_LIST
from .catalogo_utils import PLAN_PRECIO_MAP, obtener_oferta_catalogo_para_venta, precio_plan_legacy
from apps.discador.models import BaseLlamada
from .ubigeo_peru import DEPTO_CHOICES, PROV_CHOICES, DISTRITOS_CHOICES


def _precio_entero(valor):
    if valor is None:
        return None
    return int(Decimal(str(valor)))


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_documento', 'documento', 'nombres', 'paterno', 'materno', 'telefono_1', 'telefono_2']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI para buscar', 'autocomplete': 'username'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'materno': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
            'telefono_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'documento': 'Documento',
            'nombres': 'Nombres',
            'paterno': 'Paterno',
            'materno': 'Materno',
            'telefono_1': 'Teléfono 01',
            'telefono_2': 'Teléfono 02',
        }


class VentaForm(forms.ModelForm):
    registrar_nuevo_cliente = forms.BooleanField(
        required=False,
        label="Registrar nuevo cliente",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    base_telefono = forms.CharField(required=False, label="Teléfono Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_nombres = forms.CharField(required=False, label="Nombres Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_paterno = forms.CharField(required=False, label="Paterno Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_materno = forms.CharField(required=False, label="Materno Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_correo = forms.EmailField(required=False, label="Correo Base", widget=forms.EmailInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_documento = forms.CharField(required=False, label="Documento Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_observaciones = forms.CharField(required=False, label="Observaciones Base", widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control vp-readonly', 'readonly': True}))

    cliente_tipo_documento = forms.ChoiceField(
        choices=Cliente.TIPO_DOCUMENTO_CHOICES,
        initial='DNI',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Documento'
    )
    cliente_documento = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI para buscar'}),
        label='Documento'
    )
    cliente_nombres = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombres'
    )
    cliente_paterno = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Paterno'
    )
    cliente_materno = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Materno'
    )
    cliente_telefono_1 = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
        label='Teléfono 01'
    )
    cliente_telefono_2 = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'}),
        label='Teléfono 02'
    )

    departamento = forms.ChoiceField(
        choices=DEPTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Departamento'
    )
    provincia = forms.ChoiceField(
        choices=[('', 'Seleccione provincia')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Provincia'
    )
    distrito = forms.ChoiceField(
        choices=[('', 'Seleccione distrito')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Distrito'
    )

    class Meta:
        model = Venta
        exclude = ['creado', 'actualizado', 'agente', 'cliente', 'base_llamada']
        widgets = {
            'recibo_electronico': forms.Select(attrs={'class': 'form-select'}),
            'abdcp': forms.Select(attrs={'class': 'form-select'}),
            'clausulas': forms.Select(attrs={'class': 'form-select'}),
            'tipo_linea': forms.Select(attrs={'class': 'form-select'}),
            'facturacion_requerida': forms.Select(attrs={'class': 'form-select'}),
            'zona_referencia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: Frente al parque, al lado de la bodega Don José'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'horario_visita': forms.Select(attrs={'class': 'form-select'}),
            'producto_nombre': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'origen': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'operador': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'modelo_producto': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'plan_producto': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'precio_venta': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'precio_plan': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'tipo_via': forms.Select(attrs={'class': 'form-select'}),
            'centro_poblado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: AA.HH. Las Brisas'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lead_readonly_fields = {
            'base_telefono', 'base_nombres', 'base_paterno', 'base_materno',
            'base_correo', 'base_documento', 'base_observaciones',
        }
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-select'
            elif isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.DateInput, forms.TimeInput)):
                if field_name not in lead_readonly_fields:
                    widget.attrs.setdefault('class', '')
                    widget.attrs['class'] += ' form-control'
            elif isinstance(widget, forms.Textarea):
                if field_name not in lead_readonly_fields:
                    widget.attrs.setdefault('class', '')
                    widget.attrs['class'] += ' form-control'
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-check-input'

        model_field = self.fields.get('modelo_producto')
        if isinstance(model_field, forms.ChoiceField):
            choices = list(model_field.choices)
            if ('0', '') not in choices:
                model_field.choices = [('0', '')] + [choice for choice in choices if choice[0] != '']

        precio_venta_field = self.fields.get('precio_venta')
        if isinstance(precio_venta_field, forms.ChoiceField):
            precio_venta_choices = list(precio_venta_field.choices)
            current = {str(choice[0]) for choice in precio_venta_choices}
            for precio in sorted(set(str(valor) for valor in PLAN_PRECIO_MAP.values())):
                if precio not in current:
                    try:
                        choice_value = int(precio)
                    except (TypeError, ValueError):
                        choice_value = precio
                    precio_venta_choices.append((choice_value, str(precio)))
                    current.add(str(choice_value))
            precio_venta_field.choices = precio_venta_choices

        precio_plan_field = self.fields.get('precio_plan')
        if isinstance(precio_plan_field, forms.ChoiceField):
            precio_plan_choices = list(precio_plan_field.choices)
            current = {str(choice[0]) for choice in precio_plan_choices}
            for precio in sorted(set(str(valor) for valor in PLAN_PRECIO_MAP.values())):
                if precio not in current:
                    try:
                        choice_value = int(precio)
                    except (TypeError, ValueError):
                        choice_value = precio
                    precio_plan_choices.append((choice_value, str(precio)))
                    current.add(str(choice_value))
            precio_plan_field.choices = precio_plan_choices

        for model_field_name in ('precio_venta', 'precio_plan'):
            model_field = Venta._meta.get_field(model_field_name)
            if not getattr(model_field, 'choices', None):
                continue
            current = {str(choice[0]) for choice in list(model_field.choices)}
            for precio in sorted(set(str(valor) for valor in PLAN_PRECIO_MAP.values())):
                if precio not in current:
                    try:
                        choice_value = int(precio)
                    except (TypeError, ValueError):
                        choice_value = precio
                    if hasattr(model_field.choices, 'append'):
                        model_field.choices.append((choice_value, str(precio)))
                    else:
                        new_choices = list(model_field.choices)
                        new_choices.append((choice_value, str(precio)))
                        model_field.choices = new_choices
                    current.add(str(choice_value))

        if self.instance and self.instance.pk:
            self.fields['registrar_nuevo_cliente'].disabled = True
            # Populate provincia choices based on departamento
            if self.instance.departamento:
                self.fields['provincia'].choices = PROV_CHOICES.get(self.instance.departamento, [('', 'Seleccione provincia')])
            # Populate distrito choices based on departamento + provincia
            if self.instance.departamento and self.instance.provincia:
                key = f"{self.instance.departamento}_{self.instance.provincia}"
                self.fields['distrito'].choices = DISTRITOS_CHOICES.get(key, [('', 'Seleccione distrito')])

        # Set default value for tipo_linea if not set
        if not self.initial.get('tipo_linea') and not (self.instance and self.instance.tipo_linea):
            self.fields['tipo_linea'].initial = 'POSTPAGO'

        # If there is a base_llamada, populate the read-only fields (for both new and existing instances)
        if self.instance and self.instance.base_llamada:
            base = self.instance.base_llamada
            self.fields['base_telefono'].initial = base.telefono
            self.fields['base_nombres'].initial = base.nombres
            self.fields['base_paterno'].initial = base.paterno
            self.fields['base_materno'].initial = base.materno
            self.fields['base_correo'].initial = base.correo
            self.fields['base_documento'].initial = base.documento
            self.fields['base_observaciones'].initial = base.observaciones

    def clean_modelo_producto(self):
        modelo = (self.cleaned_data.get('modelo_producto') or '').strip()
        if modelo == '0':
            return ''
        return modelo

    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('cliente_documento')
        nombres = cleaned_data.get('cliente_nombres')
        paterno = cleaned_data.get('cliente_paterno')
        registrar_nuevo = cleaned_data.get('registrar_nuevo_cliente', False)
        recibo = cleaned_data.get('recibo_electronico')
        correo_recibo = cleaned_data.get('correo_electronico_recibo')

        if not documento:
            raise forms.ValidationError("Debe ingresar el documento del cliente.")

        for tel_field in ('cliente_telefono_1', 'cliente_telefono_2', 'telefono_portar'):
            valor = cleaned_data.get(tel_field)
            if valor:
                cleaned_data[tel_field] = ''.join(c for c in str(valor) if c.isdigit())

        base_llamada = getattr(self.instance, 'base_llamada', None)
        if base_llamada and base_llamada.resultado_gestion == 'VENTA_CONVERTIDA':
            raise forms.ValidationError("Este lead ya fue convertido en venta. No se puede registrar una nueva venta.")

        producto = cleaned_data.get('producto_nombre')
        origen = cleaned_data.get('origen')
        operador = cleaned_data.get('operador')
        telefono_portar = cleaned_data.get('telefono_portar')
        modelo = cleaned_data.get('modelo_producto')
        plan = cleaned_data.get('plan_producto')
        tipo_linea = cleaned_data.get('tipo_linea')

        modelo = (modelo or '').strip()
        if modelo == '0':
            modelo = ''
            cleaned_data['modelo_producto'] = ''

        if producto == 'CHIP':
            if modelo:
                self.add_error('modelo_producto', forms.ValidationError("Los productos tipo CHIP no tienen modelo de equipo. El campo modelo debe estar vacío."))

            if not plan:
                self.add_error('plan_producto', forms.ValidationError("Para CHIP, debe seleccionar un plan ENTEL CHIP."))
            else:
                oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
                if oferta:
                    cleaned_data['precio_venta'] = _precio_entero(oferta.precio_equipo)
                    cleaned_data['precio_plan'] = _precio_entero(oferta.precio_plan_mensual)
                elif plan in PLANES_CHIP:
                    precio_plan = precio_plan_legacy(plan)
                    cleaned_data['precio_venta'] = 1
                    cleaned_data['precio_plan'] = precio_plan or 0
                else:
                    self.add_error('plan_producto', forms.ValidationError(f"Para CHIP, el plan debe ser uno de: {', '.join(PLANES_CHIP)}"))

        if producto == 'PACK':
            if not modelo:
                self.add_error('modelo_producto', forms.ValidationError("Para PACK, debe seleccionar un modelo de equipo válido."))
            elif modelo in MODELOS_CHIP_LIST:
                self.add_error('modelo_producto', forms.ValidationError(f"El modelo '{modelo}' es un chip. Para PACK, seleccione un modelo de equipo válido."))

            if not plan:
                self.add_error('plan_producto', forms.ValidationError("Para PACK, debe seleccionar un plan."))
            else:
                oferta = obtener_oferta_catalogo_para_venta(producto, modelo, plan, tipo_linea, origen)
                if oferta:
                    cleaned_data['precio_venta'] = _precio_entero(oferta.precio_equipo)
                    cleaned_data['precio_plan'] = _precio_entero(oferta.precio_plan_mensual)
                elif tipo_linea == 'PREPAGO':
                    precio = Venta.PRECIOS_PREPAGO.get(modelo)
                    if precio is None:
                        self.add_error('precio_venta', forms.ValidationError(f"No hay precio definido para el modelo {modelo} en modo Prepago. Consulte con el área comercial."))
                    cleaned_data['precio_venta'] = precio
                    cleaned_data['precio_plan'] = precio_plan_legacy(plan) or 0
                elif tipo_linea == 'POSTPAGO':
                    precio_plan = precio_plan_legacy(plan)
                    if precio_plan is None:
                        self.add_error('plan_producto', forms.ValidationError(f"No hay precio definido para el plan {plan}."))
                        cleaned_data['precio_plan'] = 0
                    precio = Venta.PRECIOS_POSTPAGO.get((modelo, plan))
                    if precio is None:
                        self.add_error('precio_venta', forms.ValidationError(f"No hay precio definido para la combinación modelo={modelo}, plan={plan} en modo Postpago."))
                    cleaned_data['precio_venta'] = precio
                    cleaned_data['precio_plan'] = precio_plan or 0
                else:
                    self.add_error('tipo_linea', forms.ValidationError(f"Tipo de línea inválido: {tipo_linea}"))

        if origen == 'PORTABILIDAD':
            valid_operadores = ['CLARO', 'MOVISTAR', 'VIETTEL', 'VIRGIN']
            if not operador or operador not in valid_operadores:
                raise forms.ValidationError("Seleccione un operador válido (Claro, Movistar, Viettel, Virgin) para portabilidad.")
            if not telefono_portar:
                raise forms.ValidationError("El número a portar es obligatorio para portabilidad.")
            if len(telefono_portar) < 7 or len(telefono_portar) > 15:
                raise forms.ValidationError("El número a portar debe tener entre 7 y 15 dígitos.")
            from apps.ventas.models import Venta as VentaModel
            venta_existente = VentaModel.objects.filter(
                origen='PORTABILIDAD',
                telefono_portar__iexact=telefono_portar
            ).exclude(pk=self.instance.pk if self.instance.pk else None).first()
            if venta_existente:
                raise forms.ValidationError(f"El número {telefono_portar} ya está registrado en la venta #{venta_existente.id}.")

        cliente_existe = Cliente.objects.filter(documento=documento, activo=True).exists()
        if not cliente_existe:
            raise forms.ValidationError(
                "El cliente no está registrado. Valide los datos y haga clic en 'Registrar Cliente' para crear uno nuevo."
            )

        if recibo == 'SI_DESEA':
            if not correo_recibo:
                raise forms.ValidationError("Debe ingresar el correo electrónico si selecciona 'Si desea'.")

        multiples_lineas = cleaned_data.get('multiples_lineas', False)
        tipo_renta2 = cleaned_data.get('tipo_renta2', '')
        if multiples_lineas and not tipo_renta2:
            raise forms.ValidationError("Si la venta es multilínea, debe completar el Tipo Renta 2.")

        if documento:
            base_qs = BaseLlamada.objects.filter(documento=documento)
            if base_qs.exists():
                base = base_qs.first()
                if not self.instance.base_llamada:
                    self.instance.base_llamada = base
                    self.fields['base_telefono'].initial = base.telefono
                    self.fields['base_nombres'].initial = base.nombres
                    self.fields['base_paterno'].initial = base.paterno
                    self.fields['base_materno'].initial = base.materno
                    self.fields['base_correo'].initial = base.correo
                    self.fields['base_documento'].initial = base.documento
                    self.fields['base_observaciones'].initial = base.observaciones
            else:
                if not self.instance.base_llamada:
                    self.instance.base_llamada = None
        return cleaned_data


class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ['tipo_venta', 'tipo_producto', 'precio_plan']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-select'
            elif isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.DateInput, forms.TimeInput)):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-control'
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-control'


def validate_items_formset(items_formset):
    has_item = False
    for form in items_formset:
        if form.cleaned_data.get('tipo_venta') or form.cleaned_data.get('tipo_producto'):
            has_item = True
            break
    return has_item