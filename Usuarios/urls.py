from django.urls import path
from .views import RegistroView, LoginView, logout_view, user_profile, usuario_list, toggle_usuario_status, Registro, \
    UserProfileUpdateView, UserPasswordChangeView, access_denied

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', user_profile, name='user_profile'),
    path('lista-usuarios/', usuario_list, name='usuario_list'),
    path('usuarios/<int:user_id>/toggle/', toggle_usuario_status, name='toggle_usuario_status'),
    path('registros/', Registro, name='Registro_A-E'),
    path('usuarios/editar/', UserProfileUpdateView.as_view(), name='edit_profile'),
    path('ususarios/cambiar-contraseña/', UserPasswordChangeView.as_view(), name='change_password'),
    path('acceso-denegado/', access_denied, name='acceso_denegado'),
]