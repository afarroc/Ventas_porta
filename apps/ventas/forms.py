from django import forms
from django.core.exceptions import ValidationError
from .models import Venta, ItemVenta, SeguimientoBO, Cliente
from apps.discador.models import BaseLlamada
from .ubigeo_peru import DEPTO_CHOICES, PROV_CHOICES, DISTRITOS_CHOICES


class VentaForm(forms.ModelForm):
    registrar_nuevo_cliente = forms.BooleanField(
        required=False,
        label="Cliente no encontrado: registrar nuevo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    # Lead fields shown as read-only visually via CSS; must stay enabled for JS updates
    base_telefono = forms.CharField(required=False, label="Teléfono Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_nombres = forms.CharField(required=False, label="Nombres Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_paterno = forms.CharField(required=False, label="Paterno Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_materno = forms.CharField(required=False, label="Materno Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_correo = forms.EmailField(required=False, label="Correo Base", widget=forms.EmailInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_documento = forms.CharField(required=False, label="Documento Base", widget=forms.TextInput(attrs={'class': 'form-control vp-readonly', 'readonly': True}))
    base_observaciones = forms.CharField(required=False, label="Observaciones Base", widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control vp-readonly', 'readonly': True}))

    class Meta:
        model = Venta
        exclude = ['creado', 'actualizado', 'agente_nombre', 'cliente', 'base_llamada']
        widgets = {
            'recibo_electronico': forms.Select(attrs={'class': 'form-select'}),
            'abdcp': forms.Select(attrs={'class': 'form-select'}),
            'clausulas': forms.Select(attrs={'class': 'form-select'}),
            'tipo_linea': forms.Select(attrs={'class': 'form-select'}),
            'facturacion_requerida': forms.Select(attrs={'class': 'form-select'}),
            'contact_callable': forms.Select(attrs={'class': 'form-select'}),
            'es_callable': forms.Select(attrs={'class': 'form-select'}),
            'tipo_valido': forms.Select(attrs={'class': 'form-select'}),
            'zona_referencia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: Frente al parque, al lado de la bodega Don José'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'fecha_venta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_gestion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_venta': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_gestion': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'cliente_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI para buscar', 'autocomplete': 'username'}),
            'horario_visita': forms.Select(attrs={'class': 'form-select'}),
            'producto_nombre': forms.Select(attrs={'class': 'form-select'}),
            'origen': forms.Select(attrs={'class': 'form-select'}),
            'operador': forms.Select(attrs={'class': 'form-select'}),
            'modelo_producto': forms.Select(attrs={'class': 'form-select'}),
            'plan_producto': forms.Select(attrs={'class': 'form-select'}),
            'precio_venta': forms.Select(attrs={'class': 'form-select'}),
            'precio_plan': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select'}),
            'tipo_via': forms.Select(attrs={'class': 'form-select'}),
            'centro_poblado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: AA.HH. Las Brisas'}),
            'departamento': forms.Select(attrs={'class': 'form-control departamento-select'}),
            'provincia': forms.Select(attrs={'class': 'form-control provincia-select'}),
            'distrito': forms.Select(attrs={'class': 'form-control distrito-select'}),
            }
        labels = {
            'cliente_nombres': 'Nombres',
            'cliente_paterno': 'Paterno',
            'cliente_materno': 'Materno',
            'cliente_documento': 'Documento',
            'cliente_tipo_documento': 'Tipo de Documento',
            'cliente_telefono_1': 'Teléfono 01',
            'cliente_telefono_2': 'Teléfono 02',
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

        # If there is a base_llamada, populate the read-only fields (for both new and existing instances)
        if self.instance.base_llamada:
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

        if not documento:
            raise forms.ValidationError("Debe ingresar el documento del cliente.")

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
                # Optionally clear initial values (they'll be empty anyway)
                # Note: we do not clear read-only fields here because they should remain as set via __init__ if locked.
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


class SeguimientoBOForm(forms.ModelForm):
    class Meta:
        model = SeguimientoBO
        fields = ['status_bo', 'fecha_bo', 'sts_courier', 'fch_courier', 'supervisor', 'intervalo']
        widgets = {
            'fecha_bo': forms.DateInput(attrs={'type': 'date'}),
            'fch_courier': forms.DateInput(attrs={'type': 'date'}),
        }

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