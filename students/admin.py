from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Payment, Log

class CustomUserAdmin(UserAdmin):
    # Ajoute 'role', 'theme', 'status' à l'affichage et aux filtres
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'status')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role', 'status')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'theme', 'status')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'theme', 'status')}),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'filiere', 'niveau', 'statut', 'date_ajout')
    search_fields = ('matricule', 'nom', 'prenom', 'email', 'telephone')
    list_filter = ('statut', 'filiere', 'niveau')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Payment)
admin.site.register(Log)
