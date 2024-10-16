from django.shortcuts import render, redirect, get_object_or_404
from HotelApp.models import *
from django.utils import timezone
from .models import Reserva,HabitacionesReservas,ServiciosReservas
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.
@login_required
def formulario_reserva(request, habitacion_id, numero_de_habitacion):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    servicios = Servicios.objects.filter(disponibilidad=True)  # Obtener solo los servicios disponibles

    if request.method == 'POST':
        fecha_inicio_str = request.POST['fecha_inicio']
        fecha_final_str = request.POST['fecha_final']
        numero_personas = request.POST['numero_personas']
        servicios_seleccionados = request.POST.getlist('servicios')  # Obtener la lista de servicios seleccionados

        fecha_inicio = timezone.datetime.fromisoformat(fecha_inicio_str)
        fecha_final = timezone.datetime.fromisoformat(fecha_final_str)

        # Cálculo del costo total
        costo_servicios = sum(Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
        costo_total = calcular_costo(habitacion.precio, fecha_inicio, fecha_final) + costo_servicios  # Asume que ya tienes esta función definida

        # Crear la reserva
        reserva = Reserva.objects.create(
            fecha_inicio_reserva=fecha_inicio,
            fecha_final_reserva=fecha_final,
            usuario=request.user,  # ID del usuario logueado
            estado='pendiente',  # Cambiar según sea necesario
            Numero_de_habitacion=numero_de_habitacion,
            costo=costo_total
        )

        HabitacionesReservas.objects.create(
            reserva=reserva,
            habitacion=habitacion,
            personas=numero_personas  # Este es el número de personas que ingresó el usuario
        )

        # Crear las relaciones con los servicios seleccionados
        for servicio_id in servicios_seleccionados:
            ServiciosReservas.objects.create(
                reserva=reserva,
                servicio_id=servicio_id
            )

        return redirect('lista_habitaciones2')  # Redirige a donde necesites

    return render(request, 'formulario_reserva.html', {
        'habitacion': habitacion,
        'numero_de_habitacion': numero_de_habitacion,  # Pasar el número de habitación
        'servicios': servicios  # Pasar los servicios al template
    })


def calcular_costo(precio_por_noche, fecha_inicio, fecha_final):
    # Calcular la diferencia en días entre las fechas
    dias_estancia = (fecha_final - fecha_inicio).days
    # Asegúrate de que no haya una estancia negativa
    if dias_estancia < 0:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha final.")
    # Calcular el costo total
    costo_total = precio_por_noche * dias_estancia
    return costo_total