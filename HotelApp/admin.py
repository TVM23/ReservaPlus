from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Habitacion, DetalleHabitacion  # Asegúrate de importar tus modelos

admin.site.register(Habitacion)
admin.site.register(DetalleHabitacion)