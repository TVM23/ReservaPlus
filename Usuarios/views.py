# Create your views here.
# Users/views.py
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
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
        next_url = request.GET.get('next')

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirigir a 'next_url' si está presente, de lo contrario a 'home'
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')  # Cambia 'home' por el nombre de tu vista de inicio
        else:
            messages.error(request, 'Credenciales inválidas.')
            return render(request, 'login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'logout.html')

@login_required
def user_profile(request):
    # El usuario que está autenticado puede acceder aquí
    user = request.user
    return render(request, 'user_profile.html', {'user': user})


@login_required
def usuario_list(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})


@login_required
def toggle_usuario_status(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    # Cambiar el estado de is_active
    usuario.is_active = not usuario.is_active
    usuario.save()

    # Redirigir de nuevo a la lista de usuarios
    return redirect('usuario_list')

