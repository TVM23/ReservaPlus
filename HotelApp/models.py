from django.db import models

# Create your models here.
class Habitacion(models.Model):
    nombre = models.CharField(max_length=100)  # varchar con longitud máxima de 100 caracteres
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Campo decimal para el precio
    cupo = models.IntegerField()  # Entero para el cupo de personas
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class DetalleHabitacion(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=255)
    ventanas = models.IntegerField()
    camas = models.CharField(max_length=100)
    numero_de_camas = models.IntegerField()
    aire_acondicionado = models.BooleanField(default=False)
    jacuzzi = models.BooleanField(default=False)
    Numero_de_habitacion = models.IntegerField(unique=True)
    habitaciones_disponibles = models.IntegerField(default=1)

    def __str__(self):
        return f"Detalle de {self.habitacion.nombre}"

class Servicios(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)
    disponibilidad=models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.nombre