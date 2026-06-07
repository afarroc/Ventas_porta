from django import forms
from .models import SeguimientoBO


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