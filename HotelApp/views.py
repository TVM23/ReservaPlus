import os
import uuid
from datetime import datetime

from django.conf import settings
from django.db.models.functions import ExtractMonth
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from Reservas.models import Reserva, Pago, Reseña
from django.utils.dateparse import parse_date
from .forms import HabitacionForm
from django.db.models import Q
from .models import Habitacion, DetalleHabitacion, Servicios
from rest_framework.response import Response
from .serializers import ServiciosSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from collections import defaultdict
from django.db.models import Count

# Configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

@login_required()
def dashboard_view(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    # Obtener filtros desde la URL (query parameters)
    fecha_inicio = request.GET.get('fecha_inicio', None)
    fecha_final = request.GET.get('fecha_final', None)

    # Filtrar reservas y pagos por rango de fechas
    reservas = Reserva.objects.all()
    pagos = Pago.objects.all()

    if fecha_inicio and fecha_final:
        fecha_inicio = parse_date(fecha_inicio)
        fecha_final = parse_date(fecha_final)
        reservas = reservas.filter(fecha_inicio_reserva__gte=fecha_inicio, fecha_final_reserva__lte=fecha_final)
        pagos = pagos.filter(fecha_pago__date__gte=fecha_inicio, fecha_pago__date__lte=fecha_final)

    # Datos generales
    total_habitaciones = Habitacion.objects.count()
    total_reservas = reservas.count()
    total_reseñas = Reseña.objects.count()
    total_servicios = Servicios.objects.count()
    reservas_completadas = reservas.filter(estado="completado").count()
    ingresos_totales = pagos.filter(estado="completado").aggregate(Sum('monto'))['monto__sum'] or 0.0
    promedio_calificaciones = Reseña.objects.aggregate(Avg('reseña'))['reseña__avg'] or 0.0

    # Habitaciones con más reservas
    habitaciones_populares = Habitacion.objects.annotate(
        total_reservas=Count('habitacionesreservas')
    ).order_by('-total_reservas')[:5]

    # Servicios más utilizados
    servicios_populares = Servicios.objects.annotate(
        total_usos=Count('serviciosreservas')
    ).order_by('-total_usos')[:5]

    # Obtener ingresos totales por mes
    ingresos_por_mes = (
        pagos.filter(estado="completado")
        .annotate(mes=ExtractMonth("fecha_pago"))
        .values("mes")
        .annotate(total=Sum("monto"))
        .order_by('mes')
    )

    # Crear lista de ingresos mensuales (asegurando que todos los meses estén representados)
    ingresos_totales_mes = defaultdict(float)
    for item in ingresos_por_mes:
        ingresos_totales_mes[item['mes']] = float(item['total'])  # Convertir Decimal a float

        # Crear una lista ordenada de ingresos por mes
    ingresos_por_mes_list = [ingresos_totales_mes.get(mes, 0) for mes in range(1, 13)]

        # Datos de reservas por estado (por ejemplo: 'pendiente', 'completado', 'cancelado')
    reservas_por_estado = reservas.values('estado').annotate(total=Count('estado'))

    # Obtener reservas por mes
    reservas_por_mes = (
        reservas
        .annotate(mes=ExtractMonth("fecha_inicio_reserva"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by('mes')
    )
    # Crear lista de reservas mensuales
    reservas_totales_mes = defaultdict(int)
    for item in reservas_por_mes:
        reservas_totales_mes[item['mes']] = item['total']

    reservas_por_mes_list = [reservas_totales_mes.get(mes, 0) for mes in range(1, 13)]

    context = {
        "total_habitaciones": total_habitaciones,
        "total_reservas": total_reservas,
        "total_reseñas": total_reseñas,
        "total_servicios": total_servicios,
        "reservas_completadas": reservas_completadas,
        "ingresos_totales": ingresos_totales,
        "promedio_calificaciones": round(promedio_calificaciones, 2),
        "habitaciones_populares": habitaciones_populares,
        "servicios_populares": servicios_populares,
        "fecha_inicio": fecha_inicio,
        "fecha_final": fecha_final,
        "ingresos_por_mes": ingresos_por_mes_list,  # Ingresos por mes
        "reservas_por_estado": reservas_por_estado,  # Reservas por estado
        "reservas_por_mes_list": reservas_por_mes_list,
    }

    return render(request, 'dashboard.html', context)


@login_required
def agregar_habitacion(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        cupo = request.POST.get('cupo')
        imagen = request.FILES.get('imagen')
        slug = None
        public_id_img = None

        if imagen:
            # Generar un nombre único para la imagen
            extension = os.path.splitext(imagen.name)[1]  # Obtener la extensión (por ejemplo, .jpg o .png)
            nombre_imagen = nombre.replace(" ", "_").lower()
            nuevo_nombre = f"{nombre_imagen}_{uuid.uuid4()}{extension}"  # Crear un nuevo nombre único
            imagen.name = nuevo_nombre  # Asignar el nuevo nombre al archivo
            upload_result = cloudinary.uploader.upload(
                imagen,
                asset_folder="reservaplus/" + "habitaciones/",
                public_id=imagen.name.split('.')[0],
                resource_type="image"
            )
            slug = upload_result["secure_url"]
            public_id_img = upload_result["public_id"]

        # Crear la nueva habitación
        nueva_habitacion = Habitacion(nombre=nombre, precio=precio, cupo=cupo, imagen=imagen, slug=slug, public_id_img=public_id_img)
        nueva_habitacion.save()

        # Redirigir a la vista de lista de habitaciones
        return redirect('lista_habitaciones')  # Asegúrate que esta URL esté definida en urls.py

    return render(request, 'agregar_habitacion.html')


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

    habitacion = get_object_or_404(Habitacion, id=id)

    if request.method == 'POST':
        habitacion.nombre = request.POST.get('nombre')
        habitacion.precio = request.POST.get('precio')
        habitacion.cupo = request.POST.get('cupo')

        if request.FILES.get('imagen'):
            nueva_imagen = request.FILES.get('imagen')
            extension = os.path.splitext(nueva_imagen.name)[1]
            nombre_imagen = habitacion.nombre.replace(" ", "_").lower()
            nuevo_nombre = f"{nombre_imagen}_{uuid.uuid4()}{extension}"  # Crear un nuevo nombre único
            nueva_imagen.name = nuevo_nombre
            if habitacion.public_id_img:  # Solo si existe un public_id
                try:
                    cloudinary.uploader.destroy(habitacion.public_id_img) # Se elimina imagen del cloudinary
                except Exception as e:
                    print(f"Error al eliminar la imagen antigua: {e}")
            upload_result = cloudinary.uploader.upload(
                nueva_imagen,
                asset_folder="reservaplus/" + "habitaciones/",
                public_id=nueva_imagen.name.split('.')[0],
                resource_type="image"
            )
            habitacion.slug = upload_result["secure_url"]
            habitacion.public_id_img = upload_result["public_id"]

            # Eliminar la imagen anterior si existe
            if habitacion.imagen:
                if os.path.isfile(habitacion.imagen.path):
                    os.remove(habitacion.imagen.path)

            # Asignar la nueva imagen
            habitacion.imagen = nueva_imagen

        habitacion.save()
        return redirect('lista_habitaciones')

    return render(request, 'editar_habitacion.html', {'habitacion': habitacion})


@login_required()
def eliminar_habitacion(request, id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('acceso_denegado')

    habitacion = Habitacion.objects.get(id=id)
    if request.method == 'POST':
        if habitacion.public_id_img:  # Solo si existe un public_id
            try:
                cloudinary.uploader.destroy(habitacion.public_id_img)  # Se elimina imagen del cloudinary
            except Exception as e:
                print(f"Error al eliminar la imagen: {e}")

        if habitacion.imagen:  # Verificar si la habitación tiene una imagen
            if os.path.isfile(habitacion.imagen.path):  # Verificar si el archivo existe
                os.remove(habitacion.imagen.path)  # Eliminar el archivo físico
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
        slug = None
        public_id_img = None

        if imagen:
            # Generar un nombre único para la imagen
            extension = os.path.splitext(imagen.name)[1]  # Obtener la extensión (por ejemplo, .jpg o .png)
            nombre_imagen = nombre.replace(" ", "_").lower()
            nuevo_nombre = f"{nombre_imagen}_{uuid.uuid4()}{extension}"  # Crear un nuevo nombre único
            imagen.name = nuevo_nombre  # Asignar el nuevo nombre al archivo
            upload_result = cloudinary.uploader.upload(
                imagen,
                asset_folder="reservaplus/" + "servicios/",
                public_id=imagen.name.split('.')[0],
                resource_type="image"
            )
            slug = upload_result["secure_url"]
            public_id_img = upload_result["public_id"]

        servicio = Servicios(nombre=nombre, descripcion=descripcion, imagen=imagen, disponibilidad=disponibilidad,
                             precio=precio, slug=slug, public_id_img=public_id_img)
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
            nueva_imagen = request.FILES['imagen']
            extension = os.path.splitext(nueva_imagen.name)[1]  # Obtener la extensión de la imagen
            nombre_imagen = servicio.nombre.replace(" ", "_").lower()
            nuevo_nombre = f"{nombre_imagen}_{uuid.uuid4()}{extension}"  # Crear un nuevo nombre único
            nueva_imagen.name = nuevo_nombre
            if servicio.public_id_img:  # Solo si existe un public_id
                try:
                    cloudinary.uploader.destroy(servicio.public_id_img) # Se elimina imagen del cloudinary
                except Exception as e:
                    print(f"Error al eliminar la imagen antigua: {e}")
            upload_result = cloudinary.uploader.upload(
                nueva_imagen,
                asset_folder="reservaplus/" + "servicios/",
                public_id=nueva_imagen.name.split('.')[0],
                resource_type="image"
            )
            servicio.slug = upload_result["secure_url"]
            servicio.public_id_img = upload_result["public_id"]
            # Eliminar la imagen anterior si existe
            if servicio.imagen:
                if os.path.isfile(servicio.imagen.path):  # Verificar que el archivo exista
                    os.remove(servicio.imagen.path)  # Eliminar el archivo físico anterior

            # Asignar la nueva imagen al servicio
            servicio.imagen = nueva_imagen

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
        if servicio.public_id_img:  # Solo si existe un public_id
            try:
                cloudinary.uploader.destroy(servicio.public_id_img)  # Se elimina imagen del cloudinary
            except Exception as e:
                print(f"Error al eliminar la imagen antigua: {e}")
        if servicio.imagen:  # Verificar si el servicio tiene una imagen
            if os.path.isfile(servicio.imagen.path):  # Verificar si el archivo existe
                os.remove(servicio.imagen.path)  # Eliminar el archivo físico
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

@login_required
def lista_habitaciones2(request, fecha_inicio, fecha_final):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('acceso_denegado')
    # Busca las reservas que caen dentro del rango de fechas
    reservas = Reserva.objects.filter(
        Q(fecha_inicio_reserva__lt=fecha_final) & Q(fecha_final_reserva__gt=fecha_inicio) & ~Q(estado="cancelada")
    )

    # Obtiene los números de habitación ocupados
    numeros_ocupados = reservas.values_list('Numero_de_habitacion', flat=True)


    # Filtra los detalles de habitaciones que no están ocupadas
    detalles_disponibles = DetalleHabitacion.objects.exclude(Numero_de_habitacion__in=numeros_ocupados)

    # Crea un diccionario para almacenar el primer detalle disponible por cada tipo de habitación
    habitaciones_con_detalle = {}

    for detalle in detalles_disponibles:
        habitacion_id = detalle.habitacion.id

        # Solo añade el primer detalle disponible para cada tipo de habitación
        if habitacion_id not in habitaciones_con_detalle:
            habitaciones_con_detalle[habitacion_id] = detalle

    # Convierte el diccionario a una lista para el contexto
    habitaciones_con_detalle = [(detalle.habitacion, detalle) for detalle in habitaciones_con_detalle.values()]


    return render(request, 'lista_habitaciones2.html', {
        'habitaciones_con_detalle': habitaciones_con_detalle,
        'fecha_inicio': fecha_inicio,
        'fecha_final': fecha_final
    })

@login_required()
def detalle_habitacion(request, habitacion_id):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('acceso_denegado')
    # Obtener la habitación por su ID
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)

    # Obtener las fechas desde los parámetros GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_final = request.GET.get('fecha_final')

    # Filtrar reservas para las fechas proporcionadas
    reservas = Reserva.objects.filter(
        Q(fecha_inicio_reserva__lt=fecha_final) & Q(fecha_final_reserva__gt=fecha_inicio) & ~Q(estado="cancelada")
    )

    # Obtener los números de habitación ocupados
    numeros_ocupados = reservas.values_list('Numero_de_habitacion', flat=True)

    # Filtrar los detalles de la habitación que están disponibles
    detalle = DetalleHabitacion.objects.filter(
        habitacion=habitacion,
    ).exclude(
        Numero_de_habitacion__in=numeros_ocupados  # Excluyendo los números de habitación ocupados
    ).filter(
        disponibilidad='disponible'  # Asegurándote de que esté disponible
    ).first()

    if detalle:
        numero_de_habitacion = detalle.Numero_de_habitacion
    else:
        numero_de_habitacion = None

    return render(request, 'detalle_habitacion.html', {
        'habitacion': habitacion,
        'detalle': detalle,
        'numero_de_habitacion': numero_de_habitacion,
        'fecha_inicio': fecha_inicio,
        'fecha_final': fecha_final,
    })




#APIS

class ServiciosListApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #permission_classes = [AllowAny]
    def get(self, request):
        # Obtener todos los servicios
        servicios = Servicios.objects.all()
        # Serializar los datos
        serializer = ServiciosSerializer(servicios, many=True)
        # Retornar la respuesta en JSON
        return Response(serializer.data, status=status.HTTP_200_OK)


#Parte de la reservas

class ListaHabitacionesDisponiblesApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_final = request.query_params.get('fecha_final')

        if not fecha_inicio or not fecha_final:
            return Response(
                {"error": "Faltan los parámetros de fecha_inicio y/o fecha_final."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            fecha_final = datetime.fromisoformat(fecha_final)
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use el formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtra las reservas que caen dentro del rango de fechas
        reservas = Reserva.objects.filter(
            Q(fecha_inicio_reserva__lt=fecha_final) &
            Q(fecha_final_reserva__gt=fecha_inicio) &
            ~Q(estado="cancelada")
        )

        # Obtiene los números de habitación ocupados
        numeros_ocupados = reservas.values_list('Numero_de_habitacion', flat=True)

        # Filtra los detalles de habitaciones que no están ocupadas
        detalles_disponibles = DetalleHabitacion.objects.exclude(Numero_de_habitacion__in=numeros_ocupados)

        # Crea un diccionario para almacenar solo el primer detalle disponible por cada tipo de habitación
        habitaciones_con_detalle = {}
        for detalle in detalles_disponibles:
            habitacion_id = detalle.habitacion.id
            if habitacion_id not in habitaciones_con_detalle:
                habitaciones_con_detalle[habitacion_id] = detalle

        # Convierte el diccionario a una lista de detalles de habitaciones disponibles
        habitaciones_disponibles = [
            {
                "id": detalle.habitacion.id,
                "nombre": detalle.habitacion.nombre,
                "precio": detalle.habitacion.precio,
                "cupo": detalle.habitacion.cupo,
                "ubicacion": detalle.ubicacion,
                "ventanas": detalle.ventanas,
                "camas": detalle.camas,
                "numero_de_camas": detalle.numero_de_camas,
                "aire_acondicionado": detalle.aire_acondicionado,
                "jacuzzi": detalle.jacuzzi,
                "Numero_de_habitacion": detalle.Numero_de_habitacion,
                "disponibilidad": detalle.disponibilidad,
                "slug": detalle.habitacion.slug
            }
            for detalle in habitaciones_con_detalle.values()
        ]

        # Retorna la respuesta con habitaciones y fechas
        return Response(
            {
                "habitaciones_disponibles": habitaciones_disponibles,
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_final": fecha_final.isoformat()
            },
            status=status.HTTP_200_OK
        )


class DetalleHabitacionApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, habitacion_id):
        # Obtener la habitación por su ID
        habitacion = get_object_or_404(Habitacion, id=habitacion_id)

        # Obtener las fechas desde los parámetros GET
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_final = request.query_params.get('fecha_final')

        if not fecha_inicio or not fecha_final:
            return Response(
                {"error": "Faltan los parámetros de fecha_inicio y/o fecha_final."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            fecha_final = datetime.fromisoformat(fecha_final)
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use el formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtrar reservas para las fechas proporcionadas
        reservas = Reserva.objects.filter(
            Q(fecha_inicio_reserva__lt=fecha_final) &
            Q(fecha_final_reserva__gt=fecha_inicio) &
            ~Q(estado="cancelada")
        )

        # Obtener los números de habitación ocupados
        numeros_ocupados = reservas.values_list('Numero_de_habitacion', flat=True)

        # Filtrar los detalles de la habitación que están disponibles
        detalle = DetalleHabitacion.objects.filter(
            habitacion=habitacion,
            disponibilidad='disponible'  # Verificar que esté disponible
        ).exclude(
            Numero_de_habitacion__in=numeros_ocupados  # Excluir los números ocupados
        ).first()

        if detalle:
            response_data = {
                "habitacion": {
                    "id": habitacion.id,
                    "nombre": habitacion.nombre,
                    "precio": habitacion.precio,
                    "cupo": habitacion.cupo,
                },
                "detalle": {
                    "Numero_de_habitacion": detalle.Numero_de_habitacion,
                    "ubicacion": detalle.ubicacion,
                    "ventanas": detalle.ventanas,
                    "camas": detalle.camas,
                    "numero_de_camas": detalle.numero_de_camas,
                    "aire_acondicionado": detalle.aire_acondicionado,
                    "jacuzzi": detalle.jacuzzi,
                    "disponibilidad": detalle.disponibilidad,
                },
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_final": fecha_final.isoformat()
            }
        else:
            response_data = {
                "mensaje": "No hay detalles disponibles para esta habitación en las fechas solicitadas.",
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_final": fecha_final.isoformat()
            }

        return Response(response_data, status=status.HTTP_200_OK)