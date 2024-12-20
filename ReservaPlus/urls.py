"""
URL configuration for ReservaPlus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import ReservaPlus
from HotelApp.views import redirect_to_home
from chatbot import views
from chatbot.views import chatbot_response

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('HotelApp/', include('HotelApp.urls')),
                  path('Usuarios/', include('Usuarios.urls')),
                  path('Reservas/', include('Reservas.urls')),
                  path('get-response/', views.chatbot_response, name='chatbot_response'),
                  path('get_user_name/', views.get_user_name, name='get_user_name'),
                  path('', redirect_to_home),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
