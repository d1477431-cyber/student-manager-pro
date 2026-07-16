from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'filiere', 'niveau', 'statut', 'date_ajout')
    search_fields = ('matricule', 'nom', 'prenom', 'email', 'telephone')
    list_filter = ('statut', 'filiere', 'niveau')
