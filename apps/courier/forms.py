from django import forms
from .models import ProveedorCourier, EstadoCourier


class ProveedorCourierForm(forms.ModelForm):
    class Meta:
        model = ProveedorCourier
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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