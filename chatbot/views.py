from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from django.conf import settings
from django.contrib.auth.decorators import login_required
from HotelApp.models import Servicios, Habitacion, DetalleHabitacion
from django.db.models import Q

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_relevant_services(user_input):
    # Definir categorías y palabras clave asociadas
    categories = {
        'relajación': ['cansado', 'dolores', 'relajar', 'estrés', 'descansar', 'spa', 'masaje', 'aguas termales'],
        'diversión': ['divertirse', 'fiesta', 'entretenimiento', 'juego', 'baile', 'música'],
        'comida': ['hambre', 'comer', 'restaurante', 'bar', 'cafetería'],
        'deporte': ['ejercicio', 'gimnasio', 'nadar', 'tenis', 'golf'],
    }

    # Crear una consulta Q vacía
    query = Q()

    # Buscar palabras clave en el input del usuario
    for category, keywords in categories.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            query |= Q(nombre__icontains=category) | Q(descripcion__icontains=category)
            for keyword in keywords:
                query |= Q(nombre__icontains=keyword) | Q(descripcion__icontains=keyword)

    # Si no hay palabras clave específicas, devolver todos los servicios
    services = Servicios.objects.filter(query) if query else Servicios.objects.all()

    return services


def format_services_for_ai(services):
    return ", ".join([f"{service.nombre} (ID: {service.id}): {service.descripcion}" for service in services])


@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')
        if request.user.is_authenticated:
            user_name = request.user.first_name or request.user.username
        else:
            user_name = "Usuario"

        # Obtener servicios y habitaciones relevantes basados en el input del usuario
        relevant_services, relevant_rooms = get_relevant_items(user_input)
        items_info = format_items_for_ai(relevant_services, relevant_rooms)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Eres un asistente AI del hotel hablando con {user_name}. "
                                                  f"Siempre dirígete a ellos por su nombre en tus respuestas. "
                                                  f"Basándote en la entrada del usuario, recomienda servicios y habitaciones apropiados "
                                                  f"de la siguiente lista: {items_info}. Considera el contexto de la solicitud "
                                                  f"del usuario, ya sea para relajación, diversión, comida, deporte, alojamiento u otras actividades. "
                                                  f"Si la solicitud del usuario no coincide con ningún servicio o habitación específica, proporciona "
                                                  f"información general sobre nuestros servicios y tipos de habitaciones disponibles. "
                                                  f"Sé creativo y sugiere cómo los servicios y habitaciones pueden satisfacer las necesidades del usuario. "
                                                  f"Responde en español de manera amigable y entusiasta."},
                    {"role": "user", "content": user_input}
                ]
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"Ocurrió un error: {str(e)}"

        return JsonResponse({'reply': response_text})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def get_user_name(request):
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
    else:
        user_name = "Usuario"
    return JsonResponse({'name': user_name})




def get_relevant_items(user_input):
    # Categorías existentes para servicios
    categories = {
        'relajación': ['cansado', 'dolores', 'relajar', 'estrés', 'descansar', 'spa', 'masaje', 'aguas termales'],
        'diversión': ['divertirse', 'fiesta', 'entretenimiento', 'juego', 'baile', 'música'],
        'comida': ['hambre', 'comer', 'restaurante', 'bar', 'cafetería'],
        'deporte': ['ejercicio', 'gimnasio', 'nadar', 'tenis', 'golf'],
    }

    # Nuevas categorías para habitaciones
    room_categories = {
        'lujo': ['suite', 'deluxe', 'lujosa', 'premium'],
        'familiar': ['familia', 'niños', 'amplia', 'grande'],
        'económica': ['barata', 'económica', 'presupuesto'],
        'vista': ['vista', 'panorámica', 'balcón'],
        'comodidades': ['jacuzzi', 'aire acondicionado', 'ventanas']
    }

    query = Q()
    room_query = Q()

    # Buscar palabras clave para servicios
    for category, keywords in categories.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            query |= Q(nombre__icontains=category) | Q(descripcion__icontains=category)
            for keyword in keywords:
                query |= Q(nombre__icontains=keyword) | Q(descripcion__icontains=keyword)

    # Buscar palabras clave para habitaciones
    for category, keywords in room_categories.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            room_query |= Q(nombre__icontains=category) | Q(detallehabitacion__ubicacion__icontains=category)
            for keyword in keywords:
                room_query |= Q(nombre__icontains=keyword) | Q(detallehabitacion__ubicacion__icontains=keyword)

    # Buscar por número de personas
    for number in range(1, 11):  # Asumimos un máximo de 10 personas
        if str(number) in user_input:
            room_query |= Q(cupo__gte=number)

    services = Servicios.objects.filter(query) if query else Servicios.objects.all()
    rooms = Habitacion.objects.filter(room_query).distinct() if room_query else Habitacion.objects.all()

    return services, rooms


def format_items_for_ai(services, rooms):
    services_info = ", ".join([f"{service.nombre}: {service.descripcion}" for service in services])
    rooms_info = ", ".join([
                               f"{room.nombre} (Capacidad: {room.cupo}, Precio: {room.precio}): {room.detallehabitacion_set.first().ubicacion}"
                               for room in rooms])
    return f"Servicios: {services_info}. Habitaciones: {rooms_info}"