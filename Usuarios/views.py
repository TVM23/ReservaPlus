from django.shortcuts import render

# Create your views here.
# Users/views.py
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout

class RegistroView(View):
    def get(self, request):
        return render(request, 'registro.html')

    def post(self, request):
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        # Crear el usuario con firstname y lastname
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = firstname
            user.last_name = lastname
            user.is_active = True  # Asegúrate de que el usuario esté activo
            user.save()
            messages.success(request, 'Registro exitoso. Puedes iniciar sesión ahora.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error en el registro: {e}')
            return render(request, 'registro.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Cambia esto a la vista que desees después de login
        else:
            messages.error(request, 'Credenciales inválidas.')
            return render(request, 'login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'logout.html')

