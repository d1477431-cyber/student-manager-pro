from django.utils import timezone

from .models import Notification, CustomUser, Message, Echeance, Absence


def notifications(request):
    """Ajoute les compteurs (badges sidebar) à tous les templates.

    Chaque compteur reste à 0 si rien n'est en attente — c'est au template
    de masquer le badge dans ce cas (voir `hidden` dans base.html).
    """
    notifications_non_lues = 0
    unread_messages = 0
    paiements_en_retard = 0
    absences_du_jour = 0
    if request.user.is_authenticated:
        try:
            current_user = CustomUser.objects.get(username=request.user.username)
            notifications_non_lues = Notification.objects.filter(
                destinataire=current_user, lu=False
            ).count()
            unread_messages = Message.objects.filter(
                destinataire=current_user, lu=False
            ).count()
            # Étudiants ayant au moins une échéance de paiement en retard
            paiements_en_retard = Echeance.objects.filter(
                statut__in=['en_attente', 'en_retard'],
                date_echeance__lt=timezone.now().date(),
            ).values('student').distinct().count()
            # Absences non justifiées enregistrées aujourd'hui
            absences_du_jour = Absence.objects.filter(
                statut='absent', justifiee=False, date=timezone.now().date(),
            ).count()
        except CustomUser.DoesNotExist:
            pass
    return {
        'notifications_non_lues': notifications_non_lues,
        'unread_messages': unread_messages,
        'paiements_en_retard': paiements_en_retard,
        'absences_du_jour': absences_du_jour,
    }
