from django.urls import path
from .views import RegistroView, LoginView, logout_view, user_profile, usuario_list, toggle_usuario_status, Registro, \
    UserProfileUpdateView, UserPasswordChangeView, access_denied, UserCreateApiView,  \
    LoginApiView, LogoutApiView, UserProfileUpdateApiView, PasswordChangeApiView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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

    # Apis

    path('api/registrar/', UserCreateApiView.as_view(), name='api_registrar_usuario'),
    path('api/login/', LoginApiView.as_view(), name='login-api'),
    path('api/logout/', LogoutApiView.as_view(), name='logout-api'),
    path('api/update-profile/', UserProfileUpdateApiView.as_view(), name='update-profile-api'),
    path('api/change-password/', PasswordChangeApiView.as_view(), name='change-password-api'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
