from django.urls import path
from .views import RegistroView, LoginView, logout_view

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]