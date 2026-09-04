from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
import datetime

# Extensions autorisées pour les pièces jointes d'annonces : uniquement des formats
# non exécutables et non interprétables par un navigateur (pas de .html/.svg/.js)
# afin d'éviter le stockage/service de contenu pouvant déclencher du XSS stocké.
ALLOWED_ATTACHMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif']

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 Mo : Django n'impose aucune limite par defaut
# sur les fichiers uploades (DATA_UPLOAD_MAX_MEMORY_SIZE ne s'applique pas aux
# fichiers) - sans ca, un upload repete de fichiers volumineux epuise le
# stockage Supabase/la bande passante (DoS applicatif a faible effort).


def validate_file_size(value):
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"Le fichier ne doit pas dépasser {MAX_UPLOAD_SIZE // (1024 * 1024)} Mo.")

# Modèle pour les utilisateurs (étend le modèle User de Django)
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Administrateur'),
        ('Secrétaire', 'Secrétaire'),
        ('Professeur', 'Professeur'),
    ]
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('pending', "En attente d'approbation"),
    ]
    THEME_CHOICES = [
        ('dark', 'Sombre'), ('light', 'Clair'), ('nature', 'Nature'),
        ('amethyst', 'Améthyste'), ('sunset', 'Sunset'), ('forest', 'Forêt'),
        ('sahara', 'Sahara'), ('coffee', 'Coffee'), ('ocean', 'Océan'),
        ('rose', 'Rose'), ('aurora', 'Aurora'), ('cobalt', 'Cobalt'),
        ('cyber', 'Cyber'), ('midnight_gold', 'Midnight Gold'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Professeur')
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='dark')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    login_attempts = models.IntegerField(default=0, help_text="Tentatives de connexion échouées consécutives")
    locked_until = models.DateTimeField(blank=True, null=True, help_text="Verrouillage jusqu'à cette date")
    must_change_password = models.BooleanField(default=True, help_text="Forcer le changement de mot de passe à la prochaine connexion")
    password_changed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        permissions = [
            ("can_view_finances", "Peut voir les données financières"),
            ("can_manage_users", "Peut gérer les utilisateurs"),
            ("can_delete_student", "Peut supprimer des étudiants"),
            ("can_export_data", "Peut exporter les données"),
            ("can_view_logs", "Peut voir le journal d'audit"),
            ("can_add_student", "Peut ajouter un étudiant"),
            ("can_generate_documents", "Peut générer bulletins et cartes d'étudiant"),
            ("can_manage_schedule", "Peut créer/modifier l'emploi du temps"),
        ]

    def __str__(self):
        return self.username

    def can_login(self):
        """Vérifie si l'utilisateur est autorisé à se connecter."""
        if self.status == 'pending':
            return False, "⏳ Votre inscription est en attente d'approbation par l'administrateur."

        if self.status == 'inactive':
            return False, "❌ Ce compte est désactivé. Contactez l'administrateur."

        if self.is_locked():
            remaining = int((self.locked_until - timezone.now()).total_seconds() / 60)
            return False, f"🔒 Compte verrouillé. Réessayez dans {remaining} minute(s)."
            
        return True, ""


    def is_locked(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['login_attempts', 'locked_until'])

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = timezone.now() + datetime.timedelta(minutes=15)
        self.save(update_fields=['login_attempts', 'locked_until'])

    def has_permission(self, perm):
        """Vérifie les permissions par rôle"""
        # L'admin a toutes les permissions
        if self.role == 'Admin':
            return True
        
        # Vérifie les permissions natives de Django assignées au groupe/rôle
        if self.has_perm(f'students.{perm}'):
            return True

        # Logique de secours basée sur le rôle (peut être conservée ou migrée)
        # Le Professeur ne peut pas ajouter d'étudiant, importer/exporter des données,
        # générer bulletins/cartes ou modifier l'emploi du temps — il peut en revanche
        # consulter le classement, les statistiques et son emploi du temps.
        permissions_map = {
            'can_view_finances': ['Admin', 'Secrétaire'],
            'can_export_data': ['Admin', 'Secrétaire'],
            'can_add_student': ['Admin', 'Secrétaire'],
            'can_generate_documents': ['Admin', 'Secrétaire'],
            'can_manage_schedule': ['Admin'],
        }
        allowed_roles = permissions_map.get(perm, [])
        return self.role in allowed_roles


class Student(models.Model):
    STATUS_CHOICES = [
        ('Actif', 'Actif'),
        ('Suspendu', 'Suspendu'),
    ]

    matricule = models.CharField(max_length=50, primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    photo = models.ImageField(
        upload_to='photos/', blank=True, null=True,
        validators=[validate_file_size],
    )
    date_ajout = models.DateTimeField(default=timezone.now)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Actif')
    filiere = models.CharField(max_length=100, blank=True, null=True)
    niveau = models.CharField(max_length=10, blank=True, null=True)
    frais_scolarite = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)

    class Meta:
        db_table = 'etudiants'
        ordering = ['-matricule']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.matricule})"

    @staticmethod
    def with_totals(queryset=None):
        """Annote chaque étudiant du queryset avec `total_paye_annot`, calculé
        en une seule requête SQL (Sum + JOIN), au lieu d'appeler total_paye()
        (une requête par étudiant) dans une boucle Python — évite l'anti-pattern
        N+1, coûteux avec une base distante (ex. Supabase)."""
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        qs = queryset if queryset is not None else Student.objects.all()
        # order_by explicite : l'agrégation (GROUP BY implicite) peut faire perdre
        # l'ordre par défaut du modèle (Meta.ordering), Django avertit sinon que
        # la pagination peut devenir incohérente d'une page à l'autre.
        return qs.annotate(total_paye_annot=Coalesce(Sum('paiements__montant'), Decimal('0.00'))).order_by('-matricule')

    def get_moyenne(self):
        notes = self.notes.all()
        if notes:
            return float(sum(n.valeur for n in notes)) / notes.count()
        return 0.0

    def get_appreciation(self):
        moyenne = self.get_moyenne()
        if moyenne >= 18: return "Excellent"
        elif moyenne >= 16: return "Très bien"
        elif moyenne >= 14: return "Bien"
        elif moyenne >= 12: return "Assez bien"
        elif moyenne >= 10: return "Passable"
        else: return "Insuffisant"

    def total_paye(self):
        return Payment.objects.filter(student=self).aggregate(total=models.Sum('montant'))['total'] or Decimal('0.00')

    def solde_restant(self):
        return self.frais_scolarite - self.total_paye()

    def statut_paiement(self):
        total = self.total_paye()
        if total >= self.frais_scolarite:
            return "À jour"
        elif total >= self.frais_scolarite * Decimal('0.5'):
            return "Partiel"
        else:
            return "En retard"

    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        initials = f"{self.prenom[0]}{self.nom[0]}".upper() if self.prenom and self.nom else "?"
        colors = ['#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669', '#d97706', '#dc2626']
        color = colors[hash(self.matricule or '') % len(colors)]
        return f"https://ui-avatars.com/api/?name={initials}&background={color[1:]}&color=fff&size=128&bold=true"


class Note(models.Model):
    """Modèle dédié pour les notes, remplaçant le champ JSON"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notes')
    valeur = models.DecimalField(max_digits=4, decimal_places=2, help_text="Note sur 20")
    matiere = models.CharField(max_length=100, blank=True, default='Générale')
    date_enregistrement = models.DateTimeField(default=timezone.now)
    semestre = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        ordering = ['-date_enregistrement']
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"{self.student.matricule} - {self.matiere}: {self.valeur}/20"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.valeur < 0 or self.valeur > 20:
            raise ValidationError("La note doit être comprise entre 0 et 20.")


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    type_paiement = models.CharField(max_length=50, default='Espèces')
    commentaire = models.TextField(blank=True, null=True)
    numero_recu = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.numero_recu:
            today = timezone.now()
            count = Payment.objects.filter(date_paiement__date=today).count() + 1
            self.numero_recu = f"REC-{today.strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement #{self.numero_recu} - {self.montant} FCFA pour {self.student.matricule}"


class Echeance(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('en_retard', 'En retard'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='echeances')
    numero_tranche = models.IntegerField(help_text="Numéro de la tranche (1, 2, 3...)")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField(blank=True, null=True)
    notification_envoyee = models.BooleanField(default=False)

    class Meta:
        ordering = ['student', 'numero_tranche']
        unique_together = ['student', 'numero_tranche']

    def __str__(self):
        return f"Tranche {self.numero_tranche} - {self.student.matricule} - {self.montant} FCFA"

    def jours_restants(self):
        if self.date_echeance:
            delta = (self.date_echeance - timezone.now().date()).days
            return delta
        return 0

    def est_en_retard(self):
        return self.statut != 'payee' and self.date_echeance < timezone.now().date()


class Log(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.username} - {self.event}: {self.details}"


class Absence(models.Model):
    STATUT_CHOICES = [('absent', 'Absent'), ('present', 'Présent'), ('retard', 'Retard')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='absences')
    date = models.DateField(default=timezone.now)
    matiere = models.CharField(max_length=100, blank=True, default='')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='absent')
    justifiee = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True, null=True)
    enregistre_par = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.matricule} - {self.date} - {self.statut}"


class Cours(models.Model):
    JOURS = [('Lundi','Lundi'),('Mardi','Mardi'),('Mercredi','Mercredi'),
             ('Jeudi','Jeudi'),('Vendredi','Vendredi'),('Samedi','Samedi')]
    filiere = models.CharField(max_length=100)
    niveau = models.CharField(max_length=10)
    matiere = models.CharField(max_length=100)
    professeur = models.CharField(max_length=100, blank=True, default='')
    jour = models.CharField(max_length=10, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['jour', 'heure_debut']

    def __str__(self):
        return f"{self.matiere} - {self.filiere}/{self.niveau} - {self.jour}"


class Message(models.Model):
    expediteur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages_recus')
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.expediteur} → {self.destinataire} : {self.sujet}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('paiment', 'Paiement'),
        ('message', 'Message'),
        ('annonce', 'Annonce'),
        ('absence', 'Absence'),
        ('echeance', 'Échéance'),
        ('systeme', 'Système'),
    ]
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='systeme')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=300, blank=True, null=True)
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.type}] {self.titre} - {self.destinataire.username}"


class Annonce(models.Model):
    CATEGORIE_CHOICES = [
        ('info', 'Information'),
        ('academique', 'Académique'),
        ('evenement', 'Événement'),
        ('urgence', 'Urgence'),
        ('administratif', 'Administratif'),
    ]
    auteur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='annonces')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='info')
    date_publication = models.DateTimeField(default=timezone.now)
    est_publiee = models.BooleanField(default=True)
    fichier_joint = models.FileField(
        upload_to='annonces/', blank=True, null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_ATTACHMENT_EXTENSIONS),
            validate_file_size,
        ],
    )

    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'

    def __str__(self):
        return f"{self.titre} - {self.auteur.username} ({self.date_publication.strftime('%d/%m/%Y')})"
