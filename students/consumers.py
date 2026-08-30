import json

from channels.generic.websocket import AsyncWebsocketConsumer


def user_group_name(user_id):
    """Nom du groupe Channels dédié à un utilisateur (une entrée par destinataire)."""
    return f'user_{user_id}'


class MessagingConsumer(AsyncWebsocketConsumer):
    """
    Un WebSocket par utilisateur connecté, pour la diffusion en temps réel des
    nouveaux messages internes (et, potentiellement, d'autres notifications).

    Le navigateur ouvre une connexion sur /ws/messagerie/ dès qu'un utilisateur
    est authentifié (voir base.html). Le serveur pousse un événement JSON dès
    qu'un nouveau message est créé pour lui (voir views.messagerie_view).
    """

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close()
            return
        self.group_name = user_group_name(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Appelé quand une vue Django envoie un événement au groupe de cet utilisateur
    # (type: 'broadcast_event' — voir students/realtime.py)
    async def broadcast_event(self, event):
        await self.send(text_data=json.dumps(event['data']))
