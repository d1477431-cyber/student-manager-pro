from django.conf import settings


class DynamicCSRFMiddleware:
    """Ajoute dynamiquement l'origine de la requête à CSRF_TRUSTED_ORIGINS"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host:
            origin = f'https://{host}'
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS = list(settings.CSRF_TRUSTED_ORIGINS) + [origin]
        return self.get_response(request)