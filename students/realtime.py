"""Aide synchrone pour pousser des événements temps réel depuis les vues Django."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .consumers import user_group_name


def notify_user(user_id, data):
    """Envoie `data` (dict JSON-sérialisable) en temps réel à un utilisateur donné.

    Ne fait rien si aucune couche de canal n'est configurée (ex. tests) ou si
    l'utilisateur n'a pas de connexion WebSocket ouverte — silencieux dans les
    deux cas, l'application continue de fonctionner normalement sans temps réel.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        user_group_name(user_id),
        {'type': 'broadcast_event', 'data': data},
    )
