
from rest_framework import serializers
from .models import Servicios

class ServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = ['id', 'nombre', 'descripcion', 'precio', 'disponibilidad']  # Añade los campos que necesites


