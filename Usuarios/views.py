# Create your views here.
# Users/views.py
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserUpdateForm, CustomPasswordChangeForm, CustomUserCreationFormRegister
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm

class RegistroView(View):
    def get(self, request):
        form = CustomUserCreationFormRegister()
        return render(request, 'registro.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            # Opcional: Autenticar e iniciar sesión después del registro
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)

            messages.success(request, 'Registro con éxito. Bienvenido')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            return render(request, 'registro.html', {'form': form})

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

            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')

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
    user = request.user
    return render(request, 'user_profile.html', {'user': user})


@login_required
def usuario_list(request):
    usuarios = User.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})


@login_required
def toggle_usuario_status(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    usuario.is_active = not usuario.is_active
    usuario.save()

    return redirect('usuario_list')

"""
def Registro(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        is_empleado = request.POST.get('is_empleado', False)  # Checkbox
        is_admin = request.POST.get('is_admin', False)  # Checkbox
        try:
            user = User.objects.create_user(first_name=firstname, last_name=lastname, username=username,
                                            password=password, email=email)

            if is_admin == 'on':
                user.is_staff = True
                user.is_superuser = True
            elif is_empleado == 'on':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()

            messages.success(request, 'Registro exitoso. Puedes iniciar sesión ahora.')
            return redirect('usuario_list')
        except Exception as e:
            messages.error(request, f'Error en el registro: {e}')
            return render(request, 'registro.html')

    return render(request, 'registro2.html')

"""

def Registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            is_empleado = form.cleaned_data.get('is_empleado')
            is_admin = form.cleaned_data.get('is_admin')

            if is_admin:
                user.is_staff = True
                user.is_superuser = True
            elif is_empleado:
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()

            messages.success(request, 'Registro exitoso. Puedes iniciar sesión ahora.')
            return redirect('usuario_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registro2.html', {'form': form})


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'actualiza_datos_perfil.html'
    success_url = reverse_lazy('user_profile')

    # Sobrescribimos este método para asegurarnos de que solo el usuario actual puede editar sus datos
    def get_object(self, queryset=None):
        return self.request.user

class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'cambiar_password.html'
    success_url = reverse_lazy('user_profile')
    success_message = "Tu contraseña ha sido cambiada exitosamente."

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Tu contraseña ha sido actualizada exitosamente.')
        return response
