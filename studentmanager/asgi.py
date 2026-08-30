"""
Configuration ASGI pour studentmanager.

Sert les requêtes HTTP classiques via Django et les connexions WebSocket
(messagerie en temps réel) via Channels.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentmanager.settings')

# Doit être initialisé avant d'importer quoi que ce soit qui touche aux modèles
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

import students.routing  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(students.routing.websocket_urlpatterns)
    ),
})
