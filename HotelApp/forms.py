from django import forms
from .models import Habitacion

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['nombre', 'precio', 'cupo', 'imagen']  # Incluye los campos del modelo

        # Personalizar mensajes de error para los campos requeridos
        error_messages = {
            'nombre': {
                'required': 'El nombre de la habitación es obligatorio.',
            },
            'precio': {
                'required': 'El precio es obligatorio.',
                'invalid': 'Introduce un valor numérico válido para el precio.',
            },
            'cupo': {
                'required': 'El cupo es obligatorio.',
                'invalid': 'Introduce un valor numérico válido para el cupo.',
            },
            'imagen': {
                'required': 'Es necesario subir una imagen.',
            }
        }

    # Validación personalizada para el campo 'precio'
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio
    def clean_precio2(self):
        precio = self.cleaned_data.get('precio')
        if precio > 100:
            raise forms.ValidationError('Excediste el máximo de caracteres.')
        return precio

    # Validación personalizada para el campo 'cupo'
    def clean_cupo(self):
        cupo = self.cleaned_data.get('cupo')
        if cupo <= 0:
            raise forms.ValidationError('El cupo debe ser mayor a 0.')
        return cupo
