from celery import shared_task
from django.utils.timezone import now, timedelta
from firebase_admin import messaging
from .models import Reserva

@shared_task
def enviar_notificaciones_reservas():
    tiempo_actual = now()
    limite = tiempo_actual + timedelta(hours=1)
    reservas = Reserva.objects.filter(fecha_fin__range=(tiempo_actual, limite))

    for reserva in reservas:
        mensaje = messaging.Message(
            notification=messaging.Notification(
                title="¡Atención!",
                body=f"Tu reserva termina pronto: {reserva.fecha_final_reserva.strftime('%d-%m-%Y %H:%M')}",
            ),
            token=reserva.firebase_token,
        )
        messaging.send(mensaje)