from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from django.conf import settings

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message')

        try:
            # Call the OpenAI API with the new interface
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            response_text = response.choices[0].message.content
        except Exception as e:
            response_text = f"An error occurred: {str(e)}"

        return JsonResponse({'reply': response_text})

    return JsonResponse({'error': 'Method not allowed'}, status=405)