from django import forms
from .models import SeguimientoBO, EstadoDespacho, EstadoCourier, Proveedor


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SeguimientoBOForm(forms.ModelForm):
    class Meta:
        model = SeguimientoBO
        fields = ['status_bo', 'fecha_bo', 'supervisor', 'observaciones']
        widgets = {
            'status_bo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_bo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supervisor': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EstadoDespachoForm(forms.ModelForm):
    class Meta:
        model = EstadoDespacho
        fields = ['etapa', 'fecha_etapa', 'proveedor', 'tracking', 'observaciones']
        widgets = {
            'etapa': forms.Select(attrs={'class': 'form-select'}),
            'fecha_etapa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'tracking': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EstadoCourierForm(forms.ModelForm):
    class Meta:
        model = EstadoCourier
        fields = ['sts_courier', 'fch_courier', 'proveedor', 'tracking', 'observaciones']
        widgets = {
            'sts_courier': forms.Select(attrs={'class': 'form-select'}),
            'fch_courier': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'tracking': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
