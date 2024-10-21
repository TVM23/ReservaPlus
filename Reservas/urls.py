from HotelApp.urls import path
from .views import formulario_reserva, lista_reservas, detalle_reserva

urlpatterns = [
    path('reservar/<int:habitacion_id>/<int:numero_de_habitacion>/', formulario_reserva, name='formulario_reserva'),
    path('reservas/', lista_reservas, name='lista_reservas'),
    path('reserva/<int:reserva_id>/', detalle_reserva, name='detalle_reserva'),
]