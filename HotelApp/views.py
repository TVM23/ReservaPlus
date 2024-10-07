from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Habitacion,DetalleHabitacion,Servicios


def agregar_habitacion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        cupo = request.POST.get('cupo')
        imagen= request.FILES.get('imagen')

        # Crear la nueva habitación
        nueva_habitacion = Habitacion(nombre=nombre, precio=precio, cupo=cupo,imagen=imagen)
        nueva_habitacion.save()

        # Redirigir a la vista de lista de habitaciones
        return redirect('lista_habitaciones')  # Asegúrate que esta URL esté definida en urls.py

    return render(request, 'agregar_habitacion.html')


def lista_habitaciones(request):
    habitaciones = Habitacion.objects.all()
    return render(request, 'lista_habitaciones.html', {'habitaciones': habitaciones})


def editar_habitacion(request, id):
    habitacion = Habitacion.objects.get(id=id)

    if request.method == 'POST':
        habitacion.nombre = request.POST.get('nombre')
        habitacion.precio = request.POST.get('precio')
        habitacion.cupo = request.POST.get('cupo')
        if request.FILES.get('imagen'):
            habitacion.imagen = request.FILES.get('imagen')
        habitacion.save()
        return redirect('lista_habitaciones')

    return render(request, 'editar_habitacion.html', {'habitacion': habitacion})

def eliminar_habitacion(request, id):
    habitacion = Habitacion.objects.get(id=id)

    if request.method == 'POST':
        habitacion.delete()
        return redirect('lista_habitaciones')

    return render(request, 'eliminar_habitacion.html', {'habitacion': habitacion})


# Redirigir desde la raíz a Home
def redirect_to_home(request):
    return redirect('home')  # Asegúrate de que 'home' sea el nombre de la URL de tu home

# Vista para renderizar Home
def home(request):
    return render(request, 'home.html')  # Renderiza tu template home.html

""""""

def agregar_detalle_habitacion(request):
    if request.method == "POST":
        habitacion_id = request.POST.get('habitacion')
        habitacion = Habitacion.objects.get(id=habitacion_id)
        ubicacion = request.POST.get('ubicacion')
        ventanas = request.POST.get('ventanas')
        camas = request.POST.get('camas')
        numero_de_camas = request.POST.get('numero_de_camas')
        aire_acondicionado = 'aire_acondicionado' in request.POST
        jacuzzi = 'jacuzzi' in request.POST

        DetalleHabitacion.objects.create(
            habitacion=habitacion,
            ubicacion=ubicacion,
            ventanas=ventanas,
            camas=camas,
            numero_de_camas=numero_de_camas,
            aire_acondicionado=aire_acondicionado,
            jacuzzi=jacuzzi
        )

        return redirect('lista_detalles_habitacion')

    habitaciones = Habitacion.objects.all()
    return render(request, 'agregar_detalle_habitacion.html', {'habitaciones': habitaciones})


def lista_detalles_habitacion(request):
    detalles = DetalleHabitacion.objects.all()
    return render(request, 'lista_detalles_habitacion.html', {'detalles': detalles})


def editar_detalle_habitacion(request, id):
    detalle = get_object_or_404(DetalleHabitacion, id=id)

    if request.method == "POST":
        habitacion_id = request.POST.get('habitacion')
        detalle.habitacion = Habitacion.objects.get(id=habitacion_id)
        detalle.ubicacion = request.POST.get('ubicacion')
        detalle.ventanas = request.POST.get('ventanas')
        detalle.camas = request.POST.get('camas')
        detalle.numero_de_camas = request.POST.get('numero_de_camas')
        detalle.aire_acondicionado = 'aire_acondicionado' in request.POST
        detalle.jacuzzi = 'jacuzzi' in request.POST
        detalle.save()

        return redirect('lista_detalles_habitacion')

    habitaciones = Habitacion.objects.all()
    return render(request, 'editar_detalle_habitacion.html', {'detalle': detalle, 'habitaciones': habitaciones})

def eliminar_detalle_habitacion(request, id):
    detalle = get_object_or_404(DetalleHabitacion, id=id)
    detalle.delete()
    return redirect('lista_detalles_habitacion')

""""""

def crear_servicio_view(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        imagen = request.FILES.get('imagen')
        disponibilidad = request.POST.get('disponibilidad') == 'on'  # Convertir a boolean

        servicio = Servicios(nombre=nombre, descripcion=descripcion, imagen=imagen, disponibilidad=disponibilidad)
        servicio.save()
        messages.success(request, 'Servicio creado exitosamente.')
        return redirect('listar_servicios')

    return render(request, 'crear_servicio.html')


# Listar servicios
def listar_servicios_view(request):
    servicios = Servicios.objects.all()
    return render(request, 'listar_servicios.html', {'servicios': servicios})


# Actualizar servicio
def actualizar_servicio_view(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk)

    if request.method == 'POST':
        servicio.nombre = request.POST['nombre']
        servicio.descripcion = request.POST['descripcion']
        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']
        servicio.disponibilidad = request.POST.get('disponibilidad') == 'on'
        servicio.save()
        messages.success(request, 'Servicio actualizado exitosamente.')
        return redirect('listar_servicios')

    return render(request, 'actualizar_servicio.html', {'servicio': servicio})


# Eliminar servicio
def eliminar_servicio_view(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado exitosamente.')
        return redirect('listar_servicios')
    return render(request, 'eliminar_servicio.html', {'servicio': servicio})