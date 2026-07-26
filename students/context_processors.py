from .models import Notification, CustomUser


def notifications(request):
    """Ajoute le nombre de notifications non lues à tous les templates"""
    if request.user.is_authenticated:
        try:
            current_user = CustomUser.objects.get(username=request.user.username)
            notifications_non_lues = Notification.objects.filter(
                destinataire=current_user, lu=False
            ).count()
        except CustomUser.DoesNotExist:
            notifications_non_lues = 0
    else:
        notifications_non_lues = 0
    return {
        'notifications_non_lues': notifications_non_lues,
    }