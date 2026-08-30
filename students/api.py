"""
API REST pour Student Manager PRO
Utilise Django REST Framework
"""
from rest_framework import serializers, viewsets, permissions, routers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Student, CustomUser, Payment, Echeance, Absence, Cours, Message, Note, Log


# ===== PERMISSIONS =====
# L'API doit refléter les mêmes règles d'autorisation que les vues Django
# (@permission_required), pas seulement exiger une authentification.

class IsAuthenticatedRole(permissions.BasePermission):
    """Base : utilisateur authentifié (équivalent de @login_required)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class StudentAPIPermission(IsAuthenticatedRole):
    """Comme les vues web : tout utilisateur connecté peut lire/modifier (ex. saisir
    des notes), mais seul un rôle avec can_add_student peut créer un étudiant et
    seul un rôle avec can_delete_student peut le supprimer."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method == 'POST':
            return request.user.has_permission('can_add_student')
        if request.method == 'DELETE':
            return request.user.has_permission('can_delete_student')
        return True


class CanViewFinances(IsAuthenticatedRole):
    """Réservé aux rôles ayant can_view_finances (paiements, échéances)."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_permission('can_view_finances')


class CanManageUsers(IsAuthenticatedRole):
    """Réservé aux rôles ayant can_manage_users (gestion des utilisateurs)."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_permission('can_manage_users')


# ===== SERIALIZERS =====

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'valeur', 'matiere', 'date_enregistrement', 'semestre']


class StudentSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    moyenne = serializers.SerializerMethodField()
    appreciation = serializers.SerializerMethodField()
    total_paye = serializers.SerializerMethodField()
    solde_restant = serializers.SerializerMethodField()
    statut_paiement = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'matricule', 'nom', 'prenom', 'age', 'photo_url', 'date_ajout',
            'email', 'telephone', 'statut', 'filiere', 'niveau',
            'frais_scolarite', 'notes', 'moyenne', 'appreciation',
            'total_paye', 'solde_restant', 'statut_paiement',
        ]

    def get_moyenne(self, obj):
        return obj.get_moyenne()

    def get_appreciation(self, obj):
        return obj.get_appreciation()

    def get_total_paye(self, obj):
        return float(obj.total_paye())

    def get_solde_restant(self, obj):
        return float(obj.solde_restant())

    def get_statut_paiement(self, obj):
        return obj.statut_paiement()

    def get_photo_url(self, obj):
        return obj.photo_url()


class StudentWriteSerializer(serializers.ModelSerializer):
    notes_data = serializers.ListField(
        child=serializers.DecimalField(max_digits=4, decimal_places=2),
        write_only=True, required=False,
    )

    class Meta:
        model = Student
        fields = [
            'matricule', 'nom', 'prenom', 'age',
            'email', 'telephone', 'statut', 'filiere', 'niveau',
            'frais_scolarite', 'notes_data',
        ]

    def create(self, validated_data):
        notes_data = validated_data.pop('notes_data', [])
        student = Student.objects.create(**validated_data)
        for val in notes_data:
            Note.objects.create(student=student, valeur=val)
        return student

    def update(self, instance, validated_data):
        notes_data = validated_data.pop('notes_data', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if notes_data is not None:
            instance.notes.all().delete()
            for val in notes_data:
                Note.objects.create(student=instance, valeur=val)
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    student_nom = serializers.CharField(source='student.nom', read_only=True)
    student_prenom = serializers.CharField(source='student.prenom', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student_matricule', 'student_nom', 'student_prenom',
            'montant', 'date_paiement', 'type_paiement', 'numero_recu',
        ]


class EcheanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Echeance
        fields = '__all__'


class AbsenceSerializer(serializers.ModelSerializer):
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)

    class Meta:
        model = Absence
        fields = [
            'id', 'student_matricule', 'date', 'matiere',
            'statut', 'justifiee', 'commentaire',
        ]


class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'theme', 'status']
        read_only_fields = ['id']


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class StatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques (lecture seule)"""
    total_etudiants = serializers.IntegerField()
    actifs = serializers.IntegerField()
    suspendus = serializers.IntegerField()
    moyenne_generale = serializers.FloatField()
    taux_reussite = serializers.FloatField()
    total_scolarite = serializers.FloatField()
    total_encaisse = serializers.FloatField()
    total_dettes = serializers.FloatField()
    a_jour = serializers.IntegerField()
    en_retard = serializers.IntegerField()
    partiel = serializers.IntegerField()


# ===== PAGINATION =====

class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== VIEWSETS =====

class StudentViewSet(viewsets.ModelViewSet):
    """API CRUD pour les étudiants"""
    queryset = Student.objects.all().prefetch_related('notes')
    permission_classes = [StudentAPIPermission]
    pagination_class = StandardPagination
    lookup_field = 'matricule'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return StudentWriteSerializer
        return StudentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '')
        filiere = self.request.query_params.get('filiere', '')
        niveau = self.request.query_params.get('niveau', '')
        statut = self.request.query_params.get('statut', '')

        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(matricule__icontains=q)
            )
        if filiere:
            queryset = queryset.filter(filiere__iexact=filiere)
        if niveau:
            queryset = queryset.filter(niveau__iexact=niveau)
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """API lecture seule pour les paiements"""
    queryset = Payment.objects.all().select_related('student').order_by('-date_paiement')
    serializer_class = PaymentSerializer
    permission_classes = [CanViewFinances]
    pagination_class = StandardPagination


class EcheanceViewSet(viewsets.ReadOnlyModelViewSet):
    """API lecture seule pour les échéances"""
    queryset = Echeance.objects.all().select_related('student').order_by('date_echeance')
    serializer_class = EcheanceSerializer
    permission_classes = [CanViewFinances]


class AbsenceViewSet(viewsets.ModelViewSet):
    """API CRUD pour les absences"""
    queryset = Absence.objects.all().select_related('student').order_by('-date')
    serializer_class = AbsenceSerializer
    permission_classes = [IsAuthenticated]


class CoursViewSet(viewsets.ModelViewSet):
    """API CRUD pour les cours"""
    queryset = Cours.objects.all()
    serializer_class = CoursSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API lecture seule pour les utilisateurs"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CanManageUsers]


# ===== VUES FONCTIONS =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    """Endpoint pour les statistiques générales"""
    students = Student.objects.all()
    notes_all = []
    for s in students:
        s_notes = [float(n.valeur) for n in s.notes.all()]
        if s_notes:
            notes_all.append(sum(s_notes) / len(s_notes))

    total = students.count()
    actifs = students.filter(statut='Actif').count()
    suspendus = students.filter(statut='Suspendu').count()
    moyenne_generale = sum(notes_all) / len(notes_all) if notes_all else 0
    taux_reussite = round(sum(1 for m in notes_all if m >= 10) / len(notes_all) * 100, 1) if notes_all else 0

    total_scolarite = sum(float(s.frais_scolarite) for s in students)
    total_encaisse = sum(float(s.total_paye()) for s in students)

    data = {
        'total_etudiants': total,
        'actifs': actifs,
        'suspendus': suspendus,
        'moyenne_generale': round(moyenne_generale, 2),
        'taux_reussite': taux_reussite,
        'total_scolarite': total_scolarite,
        'total_encaisse': total_encaisse,
        'total_dettes': total_scolarite - total_encaisse,
        'a_jour': sum(1 for s in students if s.statut_paiement() == 'À jour'),
        'en_retard': sum(1 for s in students if s.statut_paiement() == 'En retard'),
        'partiel': sum(1 for s in students if s.statut_paiement() == 'Partiel'),
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """Endpoint pour les informations de l'utilisateur connecté"""
    user = request.user
    try:
        custom_user = CustomUser.objects.get(username=user.username)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': custom_user.role,
        'theme': custom_user.theme,
        'status': custom_user.status,
        'permissions': {
            'can_view_finances': custom_user.has_permission('can_view_finances'),
            'can_manage_users': custom_user.has_permission('can_manage_users'),
            'can_delete_student': custom_user.has_permission('can_delete_student'),
            'can_export_data': custom_user.has_permission('can_export_data'),
            'can_view_logs': custom_user.has_permission('can_view_logs'),
        }
    })


# ===== ROUTER =====

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'echeances', EcheanceViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'cours', CoursViewSet)
router.register(r'users', UserViewSet)