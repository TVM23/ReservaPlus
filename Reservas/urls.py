from HotelApp.urls import path
from .views import formulario_reserva, lista_reservas, detalle_reserva, buscar_habitaciones, \
    reservas_usuario, crear_resena, cancelar_reserva, checkout_session, success, cancel, stripe_webhook, \
    ValidarFechasReservaApiView, FormularioReservaApiView, CheckoutSessionAPIView, stripe_webhookAPI, SuccessAPIView, \
    CancelAPIView, ReservasUsuarioApiView, CrearResenaApiView, CancelarReservaApiView

urlpatterns = [
    path('buscar_habitacion/', buscar_habitaciones, name='buscar_habitacion'),
    # Aqui van unas en la app de Hotel app listahabitacion2 y detalle habitacion
    path('formulario_reserva/<int:habitacion_id>/<int:numero_de_habitacion>/', formulario_reserva,
         name='formulario_reserva'),
    path('reservas/', lista_reservas, name='lista_reservas'),
    path('reserva/<int:reserva_id>/', detalle_reserva, name='detalle_reserva'),

    path('mis-reservas/', reservas_usuario, name='reservas_usuario'),
    path('crear_resena/<int:usuario_id>/<int:reserva_id>/<int:habitacion_id>/', crear_resena,
         name='crear_resena'),
    path('reservas/cancelar/<int:reserva_id>/', cancelar_reserva, name='cancelar_reserva'),

    path('checkout_session/', checkout_session, name='checkout_session'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),

    # Apis
    path('api/validar-fechas/', ValidarFechasReservaApiView.as_view(), name='validar-fechas-reserva-api'),
    path('api/formulario-reserva/<int:habitacion_id>/<int:numero_de_habitacion>/', FormularioReservaApiView.as_view(),
         name='formulario_reserva_api'),
    path('api/checkout-session/', CheckoutSessionAPIView.as_view(), name='checkout_session_api'),
    path('api/webhook/', stripe_webhookAPI, name='stripe_webhook'),
    path('api/success/', SuccessAPIView.as_view(), name='payment_success'),
    path('api/cancel/', CancelAPIView.as_view(), name='payment_cancel'),
    path('api/reservas_usuario/', ReservasUsuarioApiView.as_view(), name='reservas_usuario_api'),
    path('api/crear_resena/<int:usuario_id>/<int:reserva_id>/<int:habitacion_id>/', CrearResenaApiView.as_view(),
         name='crear_resena_api'),
    path('api/reservas/cancelar/<int:reserva_id>/', CancelarReservaApiView.as_view(), name='cancelar-reserva-api'),

]
