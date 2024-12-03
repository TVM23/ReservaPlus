# serializers.py
from rest_framework import serializers
from .models import Reserva, HabitacionesReservas, ServiciosReservas,Reseña

class FechaReservaSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField(required=True)
    fecha_final = serializers.DateField(required=True)



class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ['id', 'fecha_inicio_reserva', 'fecha_final_reserva', 'estado', 'Numero_de_habitacion', 'costo']

class HabitacionesReservasSerializer(serializers.ModelSerializer):
    imagen_slug = serializers.CharField(source="habitacion.slug", read_only=True)
    class Meta:
        model = HabitacionesReservas
        fields = ['id', 'habitacion', 'personas', 'imagen_slug']

class ServiciosReservasSerializer(serializers.ModelSerializer):
    nombre_servicio = serializers.CharField(source='servicio.nombre', read_only=True)
    class Meta:
        model = ServiciosReservas
        fields = ['id', 'servicio', 'nombre_servicio']


class ReseñaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = ['id', 'usuario', 'reserva', 'habitacion_reservada', 'comentarios', 'reseña']