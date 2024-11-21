# Create your views here.
# Users/views.py
from django.core.exceptions import PermissionDenied
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .forms import UserUpdateForm, CustomPasswordChangeForm, CustomUserCreationFormRegister
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserCreateSerializer,LoginSerializer,UserProfileUpdateSerializer,PasswordChangeSerializer
from django.contrib.auth.models import User

class RegistroView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
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
        if request.user.is_authenticated:
            return redirect('home')
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
    if not request.user.is_superuser:
        return redirect('acceso_denegado')
    usuarios = User.objects.all()  # Obtener todos los usuarios
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})


@login_required
def toggle_usuario_status(request, user_id):
    if not request.user.is_superuser:
        return redirect('acceso_denegado')

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

@login_required
def Registro(request):
    if not request.user.is_superuser:
        return redirect('acceso_denegado')
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

            messages.success(request, 'Registro exitoso.')
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


def access_denied(request):
    return render(request, 'acceso_denegado.html')





#APIs
"""
class UserCreateApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        # Crear el usuario con el serializador
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Autenticación e inicio de sesión con sesiones
        username = request.data.get('username')
        password = request.data.get('password1')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)  # Inicia la sesión con el usuario autenticado

        # Devolver una respuesta con éxito y los detalles del usuario
        return Response({
            "message": "Registro exitoso. Bienvenido",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
"""

class UserCreateApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]  # Permitir el acceso a usuarios no autenticados

    def create(self, request, *args, **kwargs):
        # Crear el usuario con el serializador
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Crear el token para el usuario registrado
        token, created = Token.objects.get_or_create(user=user)

        # Devolver la respuesta con el token y los detalles del usuario
        return Response({
            "message": "Registro exitoso. Bienvenido",
            "user": {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "token": token.key  # Enviar el token en la respuesta
        }, status=status.HTTP_201_CREATED)



"""
class LoginApiView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        # Validar los datos de entrada
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Obtener los datos validados
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si la autenticación es exitosa, iniciar sesión
            login(request, user)
            return Response({
                "message": "Inicio de sesión exitoso. Bienvenido",
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            # Si la autenticación falla, enviar un mensaje de error
            return Response({
                "error": "Credenciales inválidas"
            }, status=status.HTTP_400_BAD_REQUEST)
"""

class LoginApiView(APIView):
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        # Validar los datos de entrada
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Obtener los datos validados
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Obtener o crear el token para el usuario
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Inicio de sesión exitoso. Bienvenido",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "token": token.key  # Devolver el token en la respuesta
            }, status=status.HTTP_200_OK)
        else:
            # Si la autenticación falla, enviar un mensaje de error
            return Response({
                "error": "Credenciales inválidas"
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(APIView):
    def post(self, request):
        # Cierra la sesión del usuario
        logout(request)
        return Response({"message": "Sesión cerrada exitosamente."}, status=status.HTTP_200_OK)




class UserProfileUpdateApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Obtiene el usuario autenticado
        return self.request.user

    def put(self, request):
        user = self.get_object()
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Perfil actualizado correctamente",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Cambiar la contraseña del usuario autenticado
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()

            return Response({"message": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





