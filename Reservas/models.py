from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Reserva(models.Model):
    fecha_inicio_reserva = models.DateTimeField(default=datetime.now)
    fecha_final_reserva = models.DateTimeField(default=datetime.now)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el modelo User
    estado = models.CharField(max_length=50)  # Cambia el tamaño según necesites
    Numero_de_habitacion = models.IntegerField()
    costo = models.FloatField()
    firebase_token = models.CharField(max_length=255, help_text="Token FCM del cliente", default="")

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


class Reseña(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey a la tabla de usuarios de Django
    habitacion_reservada = models.ForeignKey('HabitacionesReservas', on_delete=models.CASCADE)  # ForeignKey a HabitacionesReservas
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE)  # ForeignKey a la tabla Reserva
    comentarios = models.CharField(max_length=255)  # Campo para comentarios de tipo varchar
    reseña = models.IntegerField()  # Campo para la calificación (reseña)

    def __str__(self):
        return f"Reseña de {self.usuario.username} para la Reserva {self.reserva.id}"


class Pago(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="pagos")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('completado', 'Completado'), ('reembolsado', 'Reembolsado')]
    )
    fecha_pago = models.DateTimeField(auto_now_add=True)
    transaccion_id = models.CharField(max_length=100, unique=True)