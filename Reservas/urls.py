from HotelApp.urls import path
from .views import formulario_reserva, lista_reservas, detalle_reserva, buscar_habitaciones, \
    reservas_usuario

urlpatterns = [
    path('formulario_reserva/<int:habitacion_id>/<int:numero_de_habitacion>/', formulario_reserva,name='formulario_reserva'),
    path('reservas/', lista_reservas, name='lista_reservas'),
    path('reserva/<int:reserva_id>/', detalle_reserva, name='detalle_reserva'),
    path('buscar_habitacion/', buscar_habitaciones, name='buscar_habitacion'),
    path('mis-reservas/', reservas_usuario, name='reservas_usuario'),
]
