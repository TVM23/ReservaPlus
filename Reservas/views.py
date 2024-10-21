from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from HotelApp.models import *
from django.utils import timezone
from .models import Reserva,HabitacionesReservas,ServiciosReservas
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView

from datetime import datetime

# Create your views here.



def verificar_disponibilidad(habitacion, fecha_inicio, fecha_final):
    # Buscar todas las reservas para la habitación en el rango de fechas
    reservas = Reserva.objects.filter(
        habitacionesreservas__habitacion=habitacion,
        fecha_final_reserva__gte=fecha_inicio,  # Fecha de finalización después o igual a la fecha de inicio solicitada
        fecha_inicio_reserva__lte=fecha_final   # Fecha de inicio antes o igual a la fecha de finalización solicitada
    )
    return not reservas.exists()  # Si no hay reservas en ese rango, la habitación está disponible


@login_required
def formulario_reserva(request, habitacion_id, numero_de_habitacion):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    servicios = Servicios.objects.filter(disponibilidad=True)

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
    dias_estancia = (fecha_final - fecha_inicio).days
    if dias_estancia < 0:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha final.")
    costo_total = precio_por_noche * dias_estancia
    return costo_total

@login_required
def lista_reservas(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    reservas = Reserva.objects.all()
    return render(request, 'lista_reservas.html', {'reservas': reservas})


@login_required
def detalle_reserva(request, reserva_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    # Obtener la reserva específica
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Obtener las habitaciones y servicios relacionados a la reserva
    habitaciones_reservadas = HabitacionesReservas.objects.filter(reserva=reserva)
    servicios_reservados = ServiciosReservas.objects.filter(reserva=reserva)
    detalle_habitacion = get_object_or_404(DetalleHabitacion, Numero_de_habitacion=reserva.Numero_de_habitacion)

    if request.method == 'POST':
        # Obtener el nuevo estado de la reserva desde el formulario
        nuevo_estado = request.POST.get('estado')

        # Actualizar el estado de la reserva
        reserva.estado = nuevo_estado
        reserva.save()

        # Cambiar la disponibilidad de la habitación basada en el estado de la reserva
        if nuevo_estado == 'en curso':
            detalle_habitacion.disponibilidad = 'ocupada'
        else:
            detalle_habitacion.disponibilidad = 'disponible'

        detalle_habitacion.save()

        # Redirigir de nuevo a la misma página para reflejar los cambios
        return redirect('lista_reservas')

    # Pasar los datos al contexto para la plantilla
    context = {
        'reserva': reserva,
        'habitaciones_reservadas': habitaciones_reservadas,
        'servicios_reservados': servicios_reservados,
        'detalle_habitacion': detalle_habitacion,
    }

    return render(request, 'detalle_reserva.html', context)