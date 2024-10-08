from django.urls import path
from .views import RegistroView, LoginView, logout_view, user_profile

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', user_profile, name='user_profile'),
]