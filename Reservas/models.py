from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Reserva(models.Model):
    fecha_inicio_reserva = models.TimeField()
    fecha_final_reserva = models.TimeField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el modelo User
    estado = models.CharField(max_length=50)  # Cambia el tamaño según necesites
    costo = models.FloatField()

    def __str__(self):
        return f"Reserva {self.id} - {self.usuario.username} ({self.fecha_inicio_reserva} a {self.fecha_final_reserva})"


class HabitacionesReservas(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)  # ForeignKey hacia Reserva
    habitacion = models.ForeignKey('HotelApp.Habitacion',
                                   on_delete=models.CASCADE)  # Asegúrate de usar el nombre correcto de la app
    personas = models.IntegerField()  # Cantidad de personas

    def __str__(self):
        return f'Habitación {self.habitacion.nombre} en Reserva {self.reserva.id}'


class ServiciosReservas(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE)  # ForeignKey hacia Reserva
    servicio = models.ForeignKey('HotelApp.Servicios', on_delete=models.CASCADE)  # ForeignKey hacia Servicios

    def __str__(self):
        return f'Servicio {self.servicio.nombre} en Reserva {self.reserva.id}'
