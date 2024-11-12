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
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .Serializers import FechaReservaSerializer, ReservaSerializer, HabitacionesReservasSerializer, \
    ServiciosReservasSerializer, ReseñaSerializer
from django.utils.decorators import method_decorator

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
        # habitaciones_disponibles = Habitacion.objects.exclude(id__in=numeros_ocupados)

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
        'fecha_final': fecha_final,  # Pasar la fecha final
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
            costo_servicios = sum(
                Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
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
        servicios_seleccionados = session['metadata'].get('servicios_seleccionados', '')
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
            Numero_de_habitacion=numero_de_habitacion,
            costo=costo_total
        )

        # Registrar la habitación en la reserva
        HabitacionesReservas.objects.create(
            reserva=reserva,
            habitacion=habitacion,
            personas=numero_personas
        )

        # Si servicios_seleccionados es una cadena, dividimos; de lo contrario, asumimos que es una lista
        if isinstance(servicios_seleccionados, str):
            servicios_seleccionados = [s for s in servicios_seleccionados.split(',') if s]

        if servicios_seleccionados:  # Solo entramos al bucle si la lista no está vacía
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


# APIS


class ValidarFechasReservaApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FechaReservaSerializer(data=request.data)

        if serializer.is_valid():
            fecha_inicio = serializer.validated_data['fecha_inicio']
            fecha_final = serializer.validated_data['fecha_final']

            return Response(
                {"mensaje": "Fechas recibidas correctamente.", "fecha_inicio": fecha_inicio,
                 "fecha_final": fecha_final},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class FormularioReservaApiView(APIView):
    def post(self, request, habitacion_id, numero_de_habitacion):
        habitacion = get_object_or_404(Habitacion, id=habitacion_id)
        servicios = Servicios.objects.filter(disponibilidad=True)

        # Obtener fechas y datos del formulario desde la solicitud
        fecha_inicio_str = request.data.get('fecha_inicio')
        fecha_final_str = request.data.get('fecha_final')
        numero_personas = request.data.get('numero_personas')
        servicios_seleccionados = request.data.get('servicios', [])

        if not fecha_inicio_str or not fecha_final_str:
            return Response({"error": "Las fechas de inicio y final son requeridas."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_final = datetime.fromisoformat(fecha_final_str)
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use el formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Calcular el costo total de los servicios seleccionados
        try:
            costo_servicios = sum(
                Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
        except Servicios.DoesNotExist:
            return Response({"error": "Uno o más servicios seleccionados no existen."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Calcular el costo total de la reserva
        try:
            costo_total = calcular_costo(habitacion.precio, fecha_inicio, fecha_final) + costo_servicios
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la reserva
        reserva = Reserva.objects.create(
            fecha_inicio_reserva=fecha_inicio,
            fecha_final_reserva=fecha_final,
            usuario=request.user,  # ID del usuario logueado
            estado='pendiente',  # Cambiar según sea necesario
            Numero_de_habitacion=numero_de_habitacion,
            costo=costo_total
        )

        # Crear el registro en HabitacionesReservas
        HabitacionesReservas.objects.create(
            reserva=reserva,
            habitacion=habitacion,
            personas=numero_personas
        )

        # Crear las relaciones con los servicios seleccionados
        for servicio_id in servicios_seleccionados:
            ServiciosReservas.objects.create(
                reserva=reserva,
                servicio_id=servicio_id
            )

        return Response({
            "mensaje": "Reserva creada exitosamente.",
            "reserva_id": reserva.id,
            "costo_total": costo_total,
            "numero_de_habitacion": numero_de_habitacion,
            "fecha_inicio": fecha_inicio_str,
            "fecha_final": fecha_final_str
        }, status=status.HTTP_201_CREATED)

    def get(self, request, habitacion_id, numero_de_habitacion):
        """
        Devuelve los datos de la habitación y servicios disponibles para el formulario de reserva.
        """
        habitacion = get_object_or_404(Habitacion, id=habitacion_id)
        servicios = Servicios.objects.filter(disponibilidad=True).values('id', 'nombre', 'precio')

        return Response({
            "habitacion": {
                "id": habitacion.id,
                "nombre": habitacion.nombre,
                "precio": habitacion.precio,
                "cupo": habitacion.cupo
            },
            "numero_de_habitacion": numero_de_habitacion,
            "servicios": list(servicios)
        }, status=status.HTTP_200_OK)


class CheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Obtener datos de la solicitud
            habitacion_id = request.data.get('habitacion_id')
            fecha_inicio_str = request.data.get('fecha_inicio')
            fecha_final_str = request.data.get('fecha_final')
            numero_personas = request.data.get('numero_personas')
            servicios_seleccionados = request.data.get('servicios', [])
            numero_de_habitacion = request.data.get('numero_de_habitacion')

            # Convertir fechas
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
            fecha_final = datetime.fromisoformat(fecha_final_str)

            # Obtener detalles de la habitación y calcular el costo total
            habitacion = get_object_or_404(Habitacion, id=habitacion_id)
            costo_servicios = sum(
                Servicios.objects.get(id=servicio_id).precio for servicio_id in servicios_seleccionados)
            costo_total = calcular_costo(habitacion.precio, fecha_inicio, fecha_final) + costo_servicios

            # Crear la sesión de checkout de Stripe
            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'mxn',
                        'unit_amount': int(costo_total * 100),
                        'product_data': {
                            'name': habitacion.nombre,
                            'description': f'Numero personas: {numero_personas}',
                            'images': [habitacion.imagen.url],
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                billing_address_collection='required',
                success_url=settings.DOMAIN + '/api/reservas/success',
                cancel_url=settings.DOMAIN + '/api/reservas/cancel',
                customer_email=request.user.email,
                metadata={
                    'habitacion_id': habitacion_id,
                    'fecha_inicio': fecha_inicio_str,
                    'fecha_final': fecha_final_str,
                    'numero_personas': numero_personas,
                    'servicios_seleccionados': ','.join(map(str, servicios_seleccionados)),
                    'user_id': request.user.id,
                    'costo_total': costo_total,
                    'numero_de_habitacion': numero_de_habitacion,
                }
            )

            return Response({'url': checkout_session.url})

        except Exception as error:
            return Response({'error': str(error)}, status=400)


@csrf_exempt
@require_POST
def stripe_webhookAPI(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        habitacion_id = session['metadata']['habitacion_id']
        fecha_inicio_str = session['metadata']['fecha_inicio']
        fecha_final_str = session['metadata']['fecha_final']
        numero_personas = int(session['metadata']['numero_personas'])
        servicios_seleccionados = session['metadata']['servicios_seleccionados'].split(',')
        user_id = session['metadata']['user_id']
        costo_total = float(session['metadata']['costo_total'])
        numero_de_habitacion = int(session['metadata']['numero_de_habitacion'])

        # Convertir fechas
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
        fecha_final = datetime.fromisoformat(fecha_final_str)

        # Crear reserva y registrar detalles en la base de datos
        usuario = User.objects.get(id=user_id)
        habitacion = Habitacion.objects.get(id=habitacion_id)

        reserva = Reserva.objects.create(
            fecha_inicio_reserva=fecha_inicio,
            fecha_final_reserva=fecha_final,
            usuario=usuario,
            estado='pendiente',
            Numero_de_habitacion=numero_de_habitacion,
            costo=costo_total
        )

        HabitacionesReservas.objects.create(
            reserva=reserva,
            habitacion=habitacion,
            personas=numero_personas
        )

        if isinstance(servicios_seleccionados, str):
            servicios_seleccionados = [s for s in servicios_seleccionados.split(',') if s]

        if servicios_seleccionados:  # Solo entramos al bucle si la lista no está vacía
            for servicio_id in servicios_seleccionados:
                servicio = Servicios.objects.get(id=servicio_id)
                ServiciosReservas.objects.create(
                    reserva=reserva,
                    servicio=servicio
                )

        Pago.objects.create(
            reserva=reserva,
            usuario=usuario,
            monto=costo_total,
            estado='completado',
            transaccion_id=session['payment_intent']
        )

    return JsonResponse({'status': 'success'}, status=200)


class SuccessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'Pago completado con éxito'})


class CancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'El pago fue cancelado'})


class ReservasUsuarioApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar que el usuario no sea superuser o staff
        if request.user.is_superuser or request.user.is_staff:
            return Response({'detail': 'Acceso denegado'}, status=status.HTTP_403_FORBIDDEN)

        usuario = request.user
        # Filtrar reservas del usuario en estado "pendiente" o "en curso"
        reservas = Reserva.objects.filter(usuario=usuario, estado__in=['pendiente', 'en curso'])

        # Estructurar la respuesta
        reservas_info = []
        for reserva in reservas:
            # Obtener habitaciones y servicios asociados a cada reserva
            habitaciones_reserva = HabitacionesReservas.objects.filter(reserva=reserva)
            servicios_reserva = ServiciosReservas.objects.filter(reserva=reserva)

            # Serializar la información de reserva, habitaciones y servicios
            reserva_data = {
                'reserva': ReservaSerializer(reserva).data,
                'habitaciones': HabitacionesReservasSerializer(habitaciones_reserva, many=True).data,
                'servicios': ServiciosReservasSerializer(servicios_reserva, many=True).data,
                'usuario_id': usuario.id,
            }
            reservas_info.append(reserva_data)

        return Response({'reservas_info': reservas_info}, status=status.HTTP_200_OK)


class CrearResenaApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, usuario_id, reserva_id, habitacion_id):
        # Validar que el usuario no sea superuser o staff
        if request.user.is_superuser or request.user.is_staff:
            return Response({'detail': 'Acceso denegado'}, status=status.HTTP_403_FORBIDDEN)

        # Obtener el usuario, la reserva y la habitación reservada
        usuario = get_object_or_404(User, id=usuario_id)
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario)
        habitacion_reservada = get_object_or_404(HabitacionesReservas, reserva=reserva, habitacion__id=habitacion_id)

        # Validar los datos del formulario en el request
        comentarios = request.data.get('comentarios')
        reseña = request.data.get('reseña')

        if not comentarios or not reseña:
            return Response({'detail': 'Los campos comentarios y reseña son obligatorios.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear la nueva reseña
        nueva_resena = Reseña(
            usuario=usuario,
            reserva=reserva,
            habitacion_reservada=habitacion_reservada,
            comentarios=comentarios,
            reseña=reseña,
        )
        nueva_resena.save()

        # Serializar y devolver la respuesta
        resena_data = ReseñaSerializer(nueva_resena).data
        return Response(resena_data, status=status.HTTP_201_CREATED)
