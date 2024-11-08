import json
import stripe
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from HotelApp.models import *
from django.utils import timezone
from .models import Reserva, HabitacionesReservas, ServiciosReservas, Reseña, Pago
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime

DOMAIN = settings.DOMAIN
stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here
@login_required
def buscar_habitaciones(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_final = request.POST.get('fecha_final')

        # Busca las reservas que caen dentro del rango de fechas
        reservas = Reserva.objects.filter(
            (models.Q(fecha_inicio_reserva__lt=fecha_final) & models.Q(fecha_final_reserva__gt=fecha_inicio))
        )

        # Obtiene los números de habitación ocupados
        numeros_ocupados = reservas.values_list('Numero_de_habitacion', flat=True)

        # Filtra las habitaciones que no están ocupadas
        habitaciones_disponibles = Habitacion.objects.exclude(id__in=numeros_ocupados)

        # Redirigir a la vista lista_habitaciones2 pasando las fechas
        return redirect('lista_habitaciones2',
                        fecha_inicio=fecha_inicio,
                        fecha_final=fecha_final)

    return render(request, 'buscar_habitaciones.html')


def verificar_disponibilidad(habitacion, fecha_inicio, fecha_final):
    # Buscar todas las reservas para la habitación en el rango de fechas
    reservas = Reserva.objects.filter(
        habitacionesreservas__habitacion=habitacion,
        fecha_final_reserva__gte=fecha_inicio,  # Fecha de finalización después o igual a la fecha de inicio solicitada
        fecha_inicio_reserva__lte=fecha_final  # Fecha de inicio antes o igual a la fecha de finalización solicitada
    )
    return not reservas.exists()  # Si no hay reservas en ese rango, la habitación está disponible

@login_required
def formulario_reserva(request, habitacion_id, numero_de_habitacion):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    servicios = Servicios.objects.filter(disponibilidad=True)

    # Obtener fechas de la solicitud GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_final = request.GET.get('fecha_final')

    if request.method == 'POST':
        fecha_inicio_str = request.POST['fecha_inicio']
        fecha_final_str = request.POST['fecha_final']
        numero_personas = request.POST['numero_personas']
        servicios_seleccionados = request.POST.getlist('servicios')

        fecha_inicio = timezone.datetime.fromisoformat(fecha_inicio_str)
        fecha_final = timezone.datetime.fromisoformat(fecha_final_str)

        # Cálculo del costo total
        costo_servicios = sum(Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
        costo_total = calcular_costo(habitacion.precio, fecha_inicio, fecha_final) + costo_servicios

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

        return redirect('lista_habitaciones2', fecha_inicio=fecha_inicio_str, fecha_final=fecha_final_str)

    return render(request, 'formulario_reserva.html', {
        'habitacion': habitacion,
        'numero_de_habitacion': numero_de_habitacion,  # Pasar el número de habitación
        'servicios': servicios,  # Pasar los servicios al template
        'fecha_inicio': fecha_inicio,  # Pasar la fecha de inicio
        'fecha_final': fecha_final,      # Pasar la fecha final
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


@login_required
def reservas_usuario(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('acceso_denegado')
    else:
        usuario = request.user
        # Filtrar reservas del usuario que estén en estado "pendiente" o "en curso"
        reservas = Reserva.objects.filter(usuario=usuario, estado__in=['pendiente', 'en curso'])

        # Agregar información de las habitaciones y servicios de cada reserva
        reservas_info = []
        for reserva in reservas:
            habitaciones_reserva = HabitacionesReservas.objects.filter(reserva=reserva)
            servicios_reserva = ServiciosReservas.objects.filter(reserva=reserva)
            reservas_info.append({
                'reserva': reserva,
                'habitaciones': habitaciones_reserva,
                'servicios': servicios_reserva,
                'usuario_id': usuario.id,
            })

        context = {
            'reservas_info': reservas_info
        }
        return render(request, 'reservas_usuario.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verifica que el usuario sea el dueño de la reserva
    if request.user == reserva.usuario:
        # Cambia el estado de la reserva
        reserva.estado = "cancelada"
        reserva.save()

        # Obtén el pago asociado a la reserva
        pago = reserva.pagos.filter(estado="completado").first()

        # Procesa el reembolso si el pago está completado
        if pago:
            try:
                reembolso = stripe.Refund.create(
                    payment_intent=pago.transaccion_id  # Usa el ID de transacción de Stripe
                )

                # Actualiza el estado del pago a "reembolsado"
                pago.estado = "reembolsado"
                pago.save()

                messages.success(request, "La reserva ha sido cancelada y el reembolso se ha procesado exitosamente.")
            except stripe.error.StripeError as e:
                messages.error(request, f"Error al procesar el reembolso: {e}")
        else:
            messages.info(request, "La reserva fue cancelada, pero no se encontró un pago completado para reembolsar.")
    else:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")

    return redirect('reservas_usuario')

@login_required
def crear_resena(request, usuario_id, reserva_id, habitacion_id):
    usuario = get_object_or_404(User, id=usuario_id)
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario)
    habitacion_reservada = get_object_or_404(HabitacionesReservas, reserva=reserva, habitacion__id=habitacion_id)

    if request.user.is_superuser or request.user.is_staff:
        return redirect('acceso_denegado')

    if request.method == "POST":
        comentarios = request.POST.get('comentarios')
        reseña = request.POST.get('reseña')

        nueva_resena = Reseña(
            usuario=usuario,
            reserva=reserva,
            habitacion_reservada=habitacion_reservada,
            comentarios=comentarios,
            reseña=reseña,
        )
        nueva_resena.save()

        return redirect('reservas_usuario')  # Redirige a la lista de reservas

    return render(request, 'crear_resena.html', {
        'usuario': usuario,
        'reserva': reserva,
        'habitacion_reservada': habitacion_reservada,
    })

@login_required
def checkout_session(request):
    if request.method == 'POST':
        try:
            habitacion_id = request.POST.get('habitacion_id')
            fecha_inicio_str = request.POST.get('fecha_inicio')
            fecha_final_str = request.POST.get('fecha_final')
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_final = datetime.fromisoformat(fecha_final_str)
            numero_personas = request.POST.get('numero_personas')
            servicios_seleccionados = request.POST.getlist('servicios')
            habitacion = get_object_or_404(Habitacion, id=habitacion_id)
            costo_servicios = sum(Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
            costo_total = calcular_costo(habitacion.precio, fecha_inicio, fecha_final) + costo_servicios
            user_email = request.user.email
            numero_de_habitacion = request.POST.get('numero_de_habitacion')

            # Crear sesión de checkout de Stripe
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'mxn',
                            'unit_amount': int(costo_total * 100),
                            'product_data': {
                                'name': habitacion.nombre,
                                'description': f'Numero personas: {numero_personas}',
                                'images': [habitacion.imagen],
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                billing_address_collection='required',
                success_url=DOMAIN + '/Reservas' + '/success',
                cancel_url=DOMAIN + '/Reservas' + '/cancel',
                customer_email=user_email,
                metadata={
                    'habitacion_id': habitacion_id,
                    'fecha_inicio': fecha_inicio_str,
                    'fecha_final': fecha_final_str,
                    'numero_personas': numero_personas,
                    'servicios_seleccionados': ','.join(servicios_seleccionados),
                    'user_id': request.user.id,
                    'costo_total': costo_total,
                    'numero_de_habitacion': numero_de_habitacion,
                }
            )
            return redirect(checkout_session.url)
        except Exception as error:
            print(error)
            return redirect('home')

@login_required
def success(request):
    return render(request, 'success.html')
@login_required
def cancel(request):
    return render(request, 'cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        # Si hay un error, responde con 400
        return HttpResponse(status=400)

    # Manejar el evento checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Obtener datos de la sesión
        habitacion_id = session['metadata']['habitacion_id']
        fecha_inicio_str = session['metadata']['fecha_inicio']
        fecha_final_str = session['metadata']['fecha_final']
        numero_personas = int(session['metadata']['numero_personas'])
        servicios_seleccionados = session['metadata']['servicios_seleccionados'].split(',')
        user_id = session['metadata']['user_id']
        costo_total = session['metadata']['costo_total']
        numero_de_habitacion = session['metadata']['numero_de_habitacion']

        # Convertir fechas
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
        fecha_final = datetime.fromisoformat(fecha_final_str)

        # Obtener los modelos necesarios
        habitacion = Habitacion.objects.get(id=habitacion_id)
        usuario = User.objects.get(id=user_id)

        # Crear la reserva
        reserva = Reserva.objects.create(
            fecha_inicio_reserva=fecha_inicio,
            fecha_final_reserva=fecha_final,
            usuario=usuario,
            estado='pendiente',
            Numero_de_habitacion= numero_de_habitacion,
            costo = costo_total
        )

        # Registrar la habitación en la reserva
        HabitacionesReservas.objects.create(
            reserva=reserva,
            habitacion=habitacion,
            personas=numero_personas
        )

        # Registrar los servicios seleccionados en la reserva
        for servicio_id in servicios_seleccionados:
            servicio = Servicios.objects.get(id=servicio_id)
            ServiciosReservas.objects.create(
                reserva=reserva,
                servicio=servicio
            )

        # Crear el pago en el sistema
        Pago.objects.create(
            reserva=reserva,
            usuario=usuario,
            monto=costo_total,  # Convertir de centavos a la moneda original
            estado='completado',
            transaccion_id=session['payment_intent']
        )

    return JsonResponse({'status': 'success'}, status=200)




#APIS



