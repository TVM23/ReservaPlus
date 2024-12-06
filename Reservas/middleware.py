from django.conf import settings

class DynamicDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Actualiza settings.DOMAIN dinámicamente según el dominio actual
        settings.DOMAIN = request.build_absolute_uri('/')  # E.g., http://127.0.0.1:8000/
        response = self.get_response(request)
        return response