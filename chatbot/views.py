from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message').lower()

        # Respuestas básicas del chatbot
        if "hola" in user_input:
            response_text = "¡Hola! ¿En qué puedo ayudarte?"
        elif "adiós" in user_input or "bye" in user_input:
            response_text = "¡Adiós! Que tengas un buen día."
        elif "cómo estás" in user_input:
            response_text = "Estoy bien, gracias por preguntar. ¿Y tú?"
        else:
            response_text = "Lo siento, no entiendo tu pregunta. ¿Puedes reformularla?"

        return JsonResponse({'reply': response_text})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


