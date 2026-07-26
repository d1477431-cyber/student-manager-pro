from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('export/csv/', views.export_students_csv, name='export_students_csv'),
    path('export/excel/', views.export_students_excel, name='export_students_excel'),
    path('', views.index, name='index'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<str:matricule>/', views.edit_student, name='edit_student'),
    path('delete/<str:matricule>/', views.delete_student, name='delete_student'),
    # Paiements
    path('paiements/', views.paiements_view, name='paiements'),
    path('paiements/enregistrer/', views.enregistrer_paiement, name='enregistrer_paiement'),
    path('paiements/recu/<int:payment_id>/', views.generer_recu_pdf, name='generer_recu_pdf'),
    path('paiements/rappels/', views.envoyer_rappels_email, name='envoyer_rappels_email'),
    # Échéances
    path('echeances/generer/<str:matricule>/', views.generer_echeances, name='generer_echeances'),
    # Logs
    path('logs/', views.logs_view, name='logs'),
    # Utilisateurs
    path('utilisateurs/', views.utilisateurs_view, name='utilisateurs'),
    # Bulletins
    path('bulletins/', views.bulletins_list, name='bulletins_list'),
    path('bulletin/<str:matricule>/apercu/', views.bulletin_preview, name='bulletin_preview'),
    path('bulletin/<str:matricule>/', views.bulletin_pdf, name='bulletin_pdf'),
    path('carte/<str:matricule>/apercu/', views.carte_preview, name='carte_preview'),
    path('carte/<str:matricule>/', views.carte_etudiant_pdf, name='carte_etudiant_pdf'),
    # Stats académiques
    path('stats/', views.stats_avancees, name='stats_avancees'),
    # Rapports financiers
    path('rapports-financiers/', views.rapports_financiers, name='rapports_financiers'),
    # Absences
    path('absences/', views.absences_view, name='absences'),
    path('absences/supprimer/<int:absence_id>/', views.supprimer_absence, name='supprimer_absence'),
    # Emploi du temps
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    # Annonces
    path('annonces/', views.annonces_view, name='annonces'),
    path('annonces/supprimer/<int:annonce_id>/', views.supprimer_annonce, name='supprimer_annonce'),
    # Messagerie
    path('messagerie/', views.messagerie_view, name='messagerie'),
    path('messagerie/<int:message_id>/', views.lire_message, name='lire_message'),
    # Import CSV
    path('import-csv/', views.import_csv, name='import_csv'),
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/marquer-lu/<int:notification_id>/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/tout-marquer-lu/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    # Classement
    path('classement/', views.classement_view, name='classement'),
]
