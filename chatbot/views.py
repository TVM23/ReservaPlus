from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from django.conf import settings
from chatbot.utils import get_relevant_items, format_items_for_ai

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')
        user_name = request.user.first_name or request.user.username if request.user.is_authenticated else "Usuario"

        relevant_services, relevant_rooms = get_relevant_items(user_input)
        items_info = format_items_for_ai(relevant_services, relevant_rooms)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Eres un asistente AI del hotel. Responde a {user_name} de forma breve y clara. "
                                                  f"Usa máximo 2 frases cortas. Recomienda servicios o habitaciones de esta lista si es relevante: {items_info}. "
                                                  f"Prioriza opciones mejor calificadas. Si no hay coincidencias, da información general concisa. "
                                                  f"Sé amigable y directo en español."},
                    {"role": "user", "content": user_input}
                ]
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"Error: {str(e)}"

        return JsonResponse({'reply': response_text})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def get_user_name(request):
    user_name = request.user.first_name or request.user.username if request.user.is_authenticated else "Usuario"
    return JsonResponse({'name': user_name})
