from django import forms
from django.core.exceptions import ValidationError
from .models import Venta, ItemVenta, Cliente
from apps.discador.models import BaseLlamada
from .ubigeo_peru import DEPTO_CHOICES, PROV_CHOICES, DISTRITOS_CHOICES


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
            'telefono_1': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_2': forms.TextInput(attrs={'class': 'form-control'}),
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
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Teléfono 01'
    )
    cliente_telefono_2 = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
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

    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('cliente_documento')
        nombres = cleaned_data.get('cliente_nombres')
        paterno = cleaned_data.get('cliente_paterno')
        registrar_nuevo = cleaned_data.get('registrar_nuevo_cliente', False)
        recibo = cleaned_data.get('recibo_electronico')
        correo_recibo = cleaned_data.get('correo_electronico_recibo')

        # Producto y Venta validations
        producto = cleaned_data.get('producto_nombre')
        origen = cleaned_data.get('origen')
        operador = cleaned_data.get('operador')
        telefono_portar = cleaned_data.get('telefono_portar')
        modelo = cleaned_data.get('modelo_producto')

        if not documento:
            raise forms.ValidationError("Debe ingresar el documento del cliente.")

        # Regla 10.1: No permitir crear venta si el lead ya está convertido
        base_llamada = getattr(self.instance, 'base_llamada', None)
        if base_llamada and base_llamada.resultado_gestion == 'VENTA_CONVERTIDA':
            raise forms.ValidationError("Este lead ya fue convertido en venta. No se puede registrar una nueva venta.")

        # Regla 1: Producto CHIP no tiene modelo ni precio variable
        if producto == 'CHIP':
            if modelo:
                raise forms.ValidationError("Los productos tipo CHIP no tienen modelo de equipo.")
            cleaned_data['precio_venta'] = 1

        # Regla 2: Origen PORTABILIDAD requiere operador y telefono_portar
        if origen == 'PORTABILIDAD':
            valid_operadores = ['CLARO', 'MOVISTAR', 'VIETTEL', 'VIRGIN']
            if not operador or operador not in valid_operadores:
                raise forms.ValidationError("Seleccione un operador válido (Claro, Movistar, Viettel, Virgin) para portabilidad.")
            if not telefono_portar:
                raise forms.ValidationError("El número a portar es obligatorio para portabilidad.")
            # Regla 10.2: Validar formato básico de teléfono portado (solo dígitos, 7-15 caracteres)
            if telefono_portar and not telefono_portar.isdigit():
                raise forms.ValidationError("El número a portar debe contener solo dígitos.")
            if telefono_portar and (len(telefono_portar) < 7 or len(telefono_portar) > 15):
                raise forms.ValidationError("El número a portar debe tener entre 7 y 15 dígitos.")
            # Validar que el teléfono portado no esté ya asociado a otra venta de portabilidad
            from apps.ventas.models import Venta as VentaModel
            telefono_limpio = telefono_portar.strip()
            venta_existente = VentaModel.objects.filter(
                origen='PORTABILIDAD',
                telefono_portar__iexact=telefono_limpio
            ).exclude(pk=self.instance.pk if self.instance.pk else None).first()
            if venta_existente:
                raise forms.ValidationError(f"El número {telefono_limpio} ya está registrado en la venta #{venta_existente.id}.")

        if registrar_nuevo:
            if not nombres or not paterno:
                raise forms.ValidationError("Para registrar un cliente nuevo debe completar al menos nombres y apellido paterno.")
            # Check if a cliente with the same documento already exists (active)
            if Cliente.objects.filter(documento=documento, activo=True).exists():
                raise forms.ValidationError("Ya existe un cliente activo con ese documento. Por favor, desmarque la opción de registrar nuevo cliente y use los datos existentes.")
        else:
            if not Cliente.objects.filter(documento=documento, activo=True).exists():
                raise forms.ValidationError("El cliente no está registrado. Complete los datos para registrar uno nuevo o vuelva a buscar.")

        # If recibo_electronico is SI_DESEA, correo is required
        if recibo == 'SI_DESEA':
            if not correo_recibo:
                raise forms.ValidationError("Debe ingresar el correo electrónico si selecciona 'Si desea'.")

        # Regla 10.3: Si multilínea, requerir tipo_renta2
        multiples_lineas = cleaned_data.get('multiples_lineas', False)
        tipo_renta2 = cleaned_data.get('tipo_renta2', '')
        if multiples_lineas and not tipo_renta2:
            raise forms.ValidationError("Si la venta es multilínea, debe completar el Tipo Renta 2.")

        # Try to find BaseLlamada by documento
        if documento:
            base_qs = BaseLlamada.objects.filter(documento=documento)
            if base_qs.exists():
                base = base_qs.first()
                # Only set base_llamada if not already set (to allow locking via URL)
                if not self.instance.base_llamada:
                    self.instance.base_llamada = base
                    # Also populate read-only fields for immediate display (if not already set via __init__)
                    self.fields['base_telefono'].initial = base.telefono
                    self.fields['base_nombres'].initial = base.nombres
                    self.fields['base_paterno'].initial = base.paterno
                    self.fields['base_materno'].initial = base.materno
                    self.fields['base_correo'].initial = base.correo
                    self.fields['base_documento'].initial = base.documento
                    self.fields['base_observaciones'].initial = base.observaciones
            else:
                # No base found; clear instance.base_llamada only if not already set (locked)
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