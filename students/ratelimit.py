"""Limitation de débit légère (anti-DoS applicatif) pour les vues publiques
sans authentification, où rien d'autre ne protège contre le spam de requêtes
(inscription, connexion). Utilise le cache Django (LocMemCache par défaut,
suffisant pour une instance unique comme sur Render) — pas de dépendance
externe.

Volontairement simple (fenêtre fixe par IP) : ça ne remplace pas une
protection réseau (Cloudflare, déjà en place devant Render), mais ça évite
qu'un script trivial puisse spammer /register/ ou /login/ sans effort.
"""
from functools import wraps

from django.core.cache import cache
from django.shortcuts import render


def get_client_ip(request):
    """Best-effort : IP réelle derrière un proxy (Render/Cloudflare) si présente."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


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
                return render(request, 'errors/rate_limited.html', status=429)
            cache.set(cache_key, attempts + 1, window_seconds)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
