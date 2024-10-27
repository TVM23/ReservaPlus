from HotelApp.urls import path
from .views import formulario_reserva, lista_reservas, detalle_reserva, buscar_habitaciones, \
    reservas_usuario,crear_resena

urlpatterns = [
    path('formulario_reserva/<int:habitacion_id>/<int:numero_de_habitacion>/', formulario_reserva,
         name='formulario_reserva'),
    path('reservas/', lista_reservas, name='lista_reservas'),
    path('reserva/<int:reserva_id>/', detalle_reserva, name='detalle_reserva'),
    path('buscar_habitacion/', buscar_habitaciones, name='buscar_habitacion'),
    path('mis-reservas/', reservas_usuario, name='reservas_usuario'),
    path('crear_resena/<int:usuario_id>/<int:reserva_id>/<int:habitacion_id>/', crear_resena,
         name='crear_resena'),
]
