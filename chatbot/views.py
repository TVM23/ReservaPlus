from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from django.conf import settings
from django.contrib.auth.decorators import login_required
from HotelApp.models import Servicios
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
@login_required
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')
        user_name = request.user.first_name or request.user.username

        # Obtener servicios relevantes basados en el input del usuario
        relevant_services = get_relevant_services(user_input)
        services_info = format_services_for_ai(relevant_services)

        try:
            # Llamar a la API de OpenAI con la nueva interfaz
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # O usa "gpt-4" si tienes acceso
                messages=[
                    {"role": "system", "content": f"Eres un asistente AI del hotel hablando con {user_name}. "
                                                  f"Siempre dirígete a ellos por su nombre en tus respuestas. "
                                                  f"Basándote en la entrada del usuario, recomienda servicios apropiados "
                                                  f"de la siguiente lista: {services_info}. Considera el contexto de la solicitud "
                                                  f"del usuario, ya sea para relajación, diversión, comida, deporte u otras actividades. "
                                                  f"Si la solicitud del usuario no coincide con ningún servicio específico, proporciona "
                                                  f"información general sobre nuestros servicios disponibles. Sé creativo y sugiere cómo "
                                                  f"los servicios pueden satisfacer las necesidades del usuario. Responde en español de "
                                                  f"manera amigable y entusiasta."},
                    {"role": "user", "content": user_input}
                ]
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"Ocurrió un error: {str(e)}"

        return JsonResponse({'reply': response_text})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def get_user_name(request):
    user_name = request.user.first_name or request.user.username
    return JsonResponse({'name': user_name})