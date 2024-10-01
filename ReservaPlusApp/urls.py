from django.urls import path
from .views import agregar_habitacion

urlpatterns = [
    path('', agregar_habitacion, name='agregar_habitacion'),
    # Asegúrate de agregar otras rutas, como la de la lista de habitaciones
]