from django import forms
from .models import Proveedor, EstadoDespacho


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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