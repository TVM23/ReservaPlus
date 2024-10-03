from django.urls import path
from .views import agregar_habitacion, lista_habitaciones, editar_habitacion, eliminar_habitacion, home, \
    redirect_to_home
from . import views

urlpatterns = [
    path('agregar/', agregar_habitacion, name='agregar_habitacion'),
    path('habitaciones/', lista_habitaciones, name='lista_habitaciones'),
    path('habitaciones/editar/<int:id>/', editar_habitacion, name='editar_habitacion'),
    path('habitaciones/eliminar/<int:id>/', eliminar_habitacion, name='eliminar_habitacion'),
    path('detalles/', views.lista_detalles_habitacion, name='lista_detalles_habitacion'),
    path('detalles/agregar/', views.agregar_detalle_habitacion, name='agregar_detalle_habitacion'),
    path('detalles/editar/<int:id>/', views.editar_detalle_habitacion, name='editar_detalle_habitacion'),
    path('detalles/eliminar/<int:id>/', views.eliminar_detalle_habitacion, name='eliminar_detalle_habitacion'),
    # Asegúrate de agregar otras rutas, como la de la lista de habitaciones

    path('', redirect_to_home, name='redirect_to_home'),  # Redirigir desde la raíz
    path('home/', home, name='home'),  # Vista para el home

]
