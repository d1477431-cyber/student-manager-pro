"""Limitation de débit légère (anti-DoS applicatif). Utilise le cache Django
(LocMemCache par défaut, suffisant pour une instance unique comme sur Render)
— pas de dépendance externe.

Volontairement simple (fenêtre fixe par IP) : ça ne remplace pas une
protection réseau (Cloudflare, déjà en place devant Render), mais ça évite
qu'un script trivial puisse spammer le site sans effort.

La réponse 429 est un HttpResponse minimal, sans template ni accès à la
session/l'auth : le but est justement de répondre le plus vite et le moins
cher possible pendant un afflux de requêtes.
"""
import os
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse

RATE_LIMIT_BODY = (
    "<!doctype html><html lang='fr'><meta charset='utf-8'>"
    "<title>Trop de requêtes</title>"
    "<body style='font-family:sans-serif;text-align:center;padding:60px 20px;'>"
    "<h1>⏳ Trop de requêtes</h1>"
    "<p>Merci de patienter quelques instants avant de réessayer.</p>"
    "</body></html>"
)


def get_client_ip(request):
    """Best-effort : IP réelle derrière un proxy (Render/Cloudflare) si présente."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _rate_limited_response():
    return HttpResponse(RATE_LIMIT_BODY, status=429, content_type='text/html; charset=utf-8')


def rate_limit(key_prefix, max_attempts, window_seconds):
    """Limite `max_attempts` requêtes par IP sur une fenêtre de `window_seconds`.

    Fenêtre fixe (pas glissante) : simple et suffisant pour ce cas d'usage,
    au prix d'un effet de bord mineur en bordure de fenêtre.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            cache_key = f'ratelimit:{key_prefix}:{ip}'
            attempts = cache.get(cache_key, 0)
            if attempts >= max_attempts:
                return _rate_limited_response()
            cache.set(cache_key, attempts + 1, window_seconds)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class GlobalRateLimitMiddleware:
    """Limite globale par IP sur l'ensemble du site (toutes les requêtes HTTP).

    Placée tôt dans MIDDLEWARE, juste après WhiteNoiseMiddleware : WhiteNoise
    répond aux requêtes de fichiers statiques (CSS/JS/images) avant d'arriver
    ici, donc seules les vraies requêtes applicatives (pages, API,
    formulaires) comptent dans le quota. Vient en complément de rate_limit()
    (plus strict, ciblé sur login/inscription) : celle-ci protège tout le
    reste, moins finement.
    """
    MAX_REQUESTS = 100
    WINDOW_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Desactive pendant la suite de tests : sinon le compteur global
        # cumule les requetes de TOUS les tests dans le meme processus pytest,
        # et finirait par renvoyer 429 a des tests sans rapport une fois le
        # total de la suite au-dela de MAX_REQUESTS. Le rate limit cible
        # (login/inscription, via rate_limit()) reste actif et teste
        # normalement — seule cette protection globale, plus grossiere, est
        # court-circuitee ici.
        if os.environ.get('PYTEST_CURRENT_TEST'):
            return self.get_response(request)
        ip = get_client_ip(request)
        cache_key = f'ratelimit:global:{ip}'
        count = cache.get(cache_key, 0)
        if count >= self.MAX_REQUESTS:
            return _rate_limited_response()
        try:
            cache.incr(cache_key)
        except ValueError:
            # Pas encore de clé (première requête de cette IP dans la fenêtre)
            cache.set(cache_key, 1, self.WINDOW_SECONDS)
        return self.get_response(request)
