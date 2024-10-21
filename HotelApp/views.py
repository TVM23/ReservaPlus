from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import HabitacionForm
from .models import Habitacion,DetalleHabitacion,Servicios

@login_required
def agregar_habitacion(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
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

"""

@login_required
def agregar_habitacion(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_habitaciones')  # Redirige a una lista o página de éxito
    else:
        form = HabitacionForm()

    return render(request, 'agregar_habitacion.html', {'form': form})

"""

@login_required
def lista_habitaciones(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    habitaciones = Habitacion.objects.all()
    return render(request, 'lista_habitaciones.html', {'habitaciones': habitaciones})

@login_required()
def editar_habitacion(request, id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

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

@login_required()
def eliminar_habitacion(request, id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

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

@login_required
def agregar_detalle_habitacion(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    if request.method == 'POST':
        habitacion_id = request.POST['habitacion']
        ubicacion = request.POST['ubicacion']
        ventanas = request.POST.get('ventanas', 0)  # Asegurarse de que el valor sea un entero
        camas = request.POST['camas']
        numero_de_camas = request.POST['numero_de_camas']
        aire_acondicionado = 'aire_acondicionado' in request.POST  # Verifica si está presente en el POST
        jacuzzi = 'jacuzzi' in request.POST  # Verifica si está presente en el POST
        numero_de_habitacion = request.POST['Numero_de_habitacion']

        habitacion = get_object_or_404(Habitacion, id=habitacion_id)

        # Crear el detalle de la habitación
        detalle = DetalleHabitacion.objects.create(
            habitacion=habitacion,
            ubicacion=ubicacion,
            ventanas=ventanas,
            camas=camas,
            numero_de_camas=numero_de_camas,
            aire_acondicionado=aire_acondicionado,
            jacuzzi=jacuzzi,
            Numero_de_habitacion=numero_de_habitacion
        )
        detalle.save()

        return redirect('lista_detalles_habitacion')  # Redirigir a la lista de detalles de habitaciones

    habitaciones = Habitacion.objects.all()
    return render(request, 'agregar_detalle_habitacion.html', {'habitaciones': habitaciones})

@login_required
def lista_detalles_habitacion(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    detalles = DetalleHabitacion.objects.all()
    return render(request, 'lista_detalles_habitacion.html', {'detalles': detalles})


@login_required
def editar_detalle_habitacion(request, id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    detalle = get_object_or_404(DetalleHabitacion, id=id)
    if request.method == "POST":
        habitacion_id = request.POST.get('habitacion')
        detalle.habitacion = Habitacion.objects.get(id=habitacion_id)
        detalle.ubicacion = request.POST.get('ubicacion')
        detalle.ventanas = request.POST.get('ventanas', 0)  # Asegurarse de que el valor sea un entero
        detalle.camas = request.POST.get('camas')
        detalle.numero_de_camas = request.POST.get('numero_de_camas')
        detalle.Numero_de_habitacion = request.POST.get('Numero_de_habitacion')
        detalle.aire_acondicionado = 'aire_acondicionado' in request.POST
        detalle.jacuzzi = 'jacuzzi' in request.POST
        detalle.save()

        return redirect('lista_detalles_habitacion')

    habitaciones = Habitacion.objects.all()
    return render(request, 'editar_detalle_habitacion.html', {
        'detalle': detalle,
        'habitaciones': habitaciones
    })

@login_required()
def eliminar_detalle_habitacion(request, id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    detalle = get_object_or_404(DetalleHabitacion, id=id)
    detalle.delete()
    return redirect('lista_detalles_habitacion')

""""""

@login_required()
def crear_servicio_view(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        imagen = request.FILES.get('imagen')
        disponibilidad = request.POST.get('disponibilidad') == 'on'  # Convertir a boolean
        precio = request.POST['precio']

        servicio = Servicios(nombre=nombre, descripcion=descripcion, imagen=imagen, disponibilidad=disponibilidad, precio=precio)
        servicio.save()
        messages.success(request, 'Servicio creado exitosamente.')
        return redirect('listar_servicios')

    return render(request, 'crear_servicio.html')


# Listar servicios
@login_required
def listar_servicios_view(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    servicios = Servicios.objects.all()
    return render(request, 'listar_servicios.html', {'servicios': servicios})


# Actualizar servicio
@login_required
def actualizar_servicio_view(request, pk):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    servicio = get_object_or_404(Servicios, pk=pk)
    if request.method == 'POST':
        servicio.nombre = request.POST['nombre']
        servicio.descripcion = request.POST['descripcion']
        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']
        servicio.disponibilidad = request.POST.get('disponibilidad') == 'on'
        servicio.precio = request.POST['precio']
        servicio.save()
        messages.success(request, 'Servicio actualizado exitosamente.')
        return redirect('listar_servicios')

    return render(request, 'actualizar_servicio.html', {'servicio': servicio})


# Eliminar servicio
@login_required
def eliminar_servicio_view(request, pk):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    servicio = get_object_or_404(Servicios, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado exitosamente.')
        return redirect('listar_servicios')
    return render(request, 'eliminar_servicio.html', {'servicio': servicio})


def servicios_cartas(request):
    servicios = Servicios.objects.all()
    return render(request, 'servicios_cartas.html', {'servicios': servicios})


"""
def lista_habitaciones2(request):
    # Obtener todas las habitaciones con su primer detalle
    habitaciones = Habitacion.objects.prefetch_related('detallehabitacion_set')

    # Preparar un diccionario para mostrar solo un detalle por habitación
    habitaciones_con_detalle = []
    for habitacion in habitaciones:
        primer_detalle = habitacion.detallehabitacion_set.first()
        habitaciones_con_detalle.append((habitacion, primer_detalle))

    return render(request, 'lista_habitaciones2.html', {'habitaciones_con_detalle': habitaciones_con_detalle})
    
"""

def lista_habitaciones2(request):
    habitaciones = Habitacion.objects.all()

    habitaciones_con_detalle = []
    for habitacion in habitaciones:
        primer_detalle = habitacion.detallehabitacion_set.filter(disponibilidad='disponible').first()
        if primer_detalle:
            habitaciones_con_detalle.append((habitacion, primer_detalle))

    return render(request, 'lista_habitaciones2.html', {'habitaciones_con_detalle': habitaciones_con_detalle})



def detalle_habitacion(request, habitacion_id):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)

    # Obtener el primer detalle de la habitación que esté disponible
    detalle = DetalleHabitacion.objects.filter(habitacion=habitacion, disponibilidad='disponible').first()

    # Verifica si hay detalle disponible y obtiene el numero_de_habitacion
    if detalle:
        numero_de_habitacion = detalle.Numero_de_habitacion
    else:
        numero_de_habitacion = None  # Manejo en caso de que no haya detalles disponibles

    return render(request, 'detalle_habitacion.html', {
        'habitacion': habitacion,
        'detalle': detalle,
        'numero_de_habitacion': numero_de_habitacion,  # Incluye el número de habitación
    })
