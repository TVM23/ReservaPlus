from django.urls import path
from .views import agregar_habitacion, lista_habitaciones, editar_habitacion, eliminar_habitacion, home, \
    redirect_to_home, crear_servicio_view, listar_servicios_view, actualizar_servicio_view, eliminar_servicio_view,lista_habitaciones2,detalle_habitacion
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
    path('servicios/nuevo/', crear_servicio_view, name='crear_servicio'),
    path('servicios/', listar_servicios_view, name='listar_servicios'),
    path('servicios/actualizar/<int:pk>/', actualizar_servicio_view, name='actualizar_servicio'),
    path('servicios/eliminar/<int:pk>/', eliminar_servicio_view, name='eliminar_servicio'),
    path('servicios-cartas/', views.servicios_cartas, name='servicios_cartas'),
    path('lista_habitaciones/', lista_habitaciones2, name='lista_habitaciones2'),
    path('habitaciones/<int:habitacion_id>/', detalle_habitacion, name='detalle_habitacion'),
    # Asegúrate de agregar otras rutas, como la de la lista de habitaciones

    path('', redirect_to_home, name='redirect_to_home'),  # Redirigir desde la raíz
    path('home/', home, name='home'),  # Vista para el home

]
