from HotelApp.urls import path
from .views import formulario_reserva


urlpatterns = [
    path('reservar/<int:habitacion_id>/<int:numero_de_habitacion>/', formulario_reserva, name='formulario_reserva'),
]