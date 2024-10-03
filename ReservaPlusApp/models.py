from django.db import models

# Create your models here.
class Habitacion(models.Model):
    nombre = models.CharField(max_length=100)  # varchar con longitud máxima de 100 caracteres
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Campo decimal para el precio
    cupo = models.IntegerField()  # Entero para el cupo de personas
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    def __str__(self):
        return self.nombre