from django.urls import path
from .views import agregar_habitacion, lista_habitaciones, editar_habitacion, eliminar_habitacion

urlpatterns = [
    path('agregar/', agregar_habitacion, name='agregar_habitacion'),
    path('habitaciones/', lista_habitaciones, name='lista_habitaciones'),
    path('habitaciones/editar/<int:id>/', editar_habitacion, name='editar_habitacion'),
    path('habitaciones/eliminar/<int:id>/', eliminar_habitacion, name='eliminar_habitacion'),
    # Asegúrate de agregar otras rutas, como la de la lista de habitaciones
]