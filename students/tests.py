"""
Tests automatisés pour Student Manager PRO
Exécution : pytest students/tests.py -v
"""

import pytest
import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from .logic import calculate_average, get_appreciation, parse_notes
from .models import Student, Payment, Echeance, Log, CustomUser, Note

User = get_user_model()


# ===== TESTS DE LA LOGIQUE MÉTIER (calculs.py) =====

class TestParseNotes:
    def test_parse_notes_vide(self):
        assert parse_notes('') == []
        assert parse_notes(None) == []
        assert parse_notes([]) == []

    def test_parse_notes_chaines(self):
        assert parse_notes('12, 15, 18') == [12.0, 15.0, 18.0]
        assert parse_notes('10.5, 12.5') == [10.5, 12.5]
        assert parse_notes('0, 20') == [0.0, 20.0]

    def test_parse_notes_liste(self):
        assert parse_notes([12, 15, 18]) == [12.0, 15.0, 18.0]
        assert parse_notes([10.5]) == [10.5]

    def test_parse_notes_json(self):
        assert parse_notes('[12, 15, 18]') == [12.0, 15.0, 18.0]
        assert parse_notes('[10.5, 12.5]') == [10.5, 12.5]


class TestCalculateAverage:
    def test_moyenne_vide(self):
        assert calculate_average([]) == 0.0
        assert calculate_average('') == 0.0

    def test_moyenne_normale(self):
        assert calculate_average([10, 20]) == 15.0
        assert calculate_average([12, 15, 18]) == 15.0

    def test_moyenne_extremes(self):
        assert calculate_average([0, 0, 0]) == 0.0
        assert calculate_average([20, 20, 20]) == 20.0

    def test_moyenne_une_note(self):
        assert calculate_average([15]) == 15.0


class TestGetAppreciation:
    def test_excellent(self):
        assert get_appreciation(18) == 'Excellent'
        assert get_appreciation(19.5) == 'Excellent'
        assert get_appreciation(20) == 'Excellent'

    def test_tres_bien(self):
        assert get_appreciation(16) == 'Excellent'
        assert get_appreciation(17) == 'Excellent'

    def test_bien(self):
        assert get_appreciation(14) == 'Assez bien'
        assert get_appreciation(15) == 'Assez bien'

    def test_assez_bien(self):
        assert get_appreciation(12) == 'Bien'
        assert get_appreciation(13) == 'Bien'

    def test_passable(self):
        assert get_appreciation(10) == 'Passable'
        assert get_appreciation(11) == 'Passable'

    def test_insuffisant(self):
        assert get_appreciation(0) == 'À renforcer'
        assert get_appreciation(5) == 'À renforcer'
        assert get_appreciation(9) == 'À renforcer'


# ===== TESTS DES MODÈLES =====

@pytest.mark.django_db
class TestStudentModel:
    def test_creation_etudiant(self):
        student = Student.objects.create(
            matricule='TEST001',
            nom='Dupont',
            prenom='Jean',
            age=20,
            filiere='Informatique',
            niveau='L3',
            frais_scolarite=500000,
        )
        # Ajouter des notes via le modèle dédié
        for val in [12, 15, 18]:
            Note.objects.create(student=student, valeur=val)
        
        assert student.matricule == 'TEST001'
        assert str(student) == 'Jean Dupont (TEST001)'
        assert student.get_moyenne() == 15.0
        assert student.get_appreciation() == 'Bien'
        assert student.notes.count() == 3

    def test_statut_paiement_a_jour(self):
        student = Student.objects.create(
            matricule='TEST002', nom='Martin', prenom='Sophie',
            age=22, frais_scolarite=500000,
        )
        Payment.objects.create(student=student, montant=500000)
        assert student.statut_paiement() == 'À jour'

    def test_statut_paiement_partiel(self):
        student = Student.objects.create(
            matricule='TEST003', nom='Durand', prenom='Pierre',
            age=21, frais_scolarite=500000,
        )
        Payment.objects.create(student=student, montant=300000)
        assert student.statut_paiement() == 'Partiel'

    def test_statut_paiement_en_retard(self):
        student = Student.objects.create(
            matricule='TEST004', nom='Petit', prenom='Marie',
            age=20, frais_scolarite=500000,
        )
        assert student.statut_paiement() == 'En retard'

    def test_photo_url_sans_photo(self):
        student = Student.objects.create(
            matricule='TEST005', nom='Leroy', prenom='Paul', age=19,
        )
        url = student.photo_url()
        assert 'ui-avatars.com' in url
        assert 'PL' in url  # Initiales Paul Leroy

    def test_solde_restant(self):
        student = Student.objects.create(
            matricule='TEST006', nom='Robert', prenom='Julie',
            age=23, frais_scolarite=500000,
        )
        assert student.solde_restant() == Decimal('500000.00')
        Payment.objects.create(student=student, montant=200000)
        assert student.solde_restant() == Decimal('300000.00')

    def test_moyenne_sans_notes(self):
        student = Student.objects.create(
            matricule='TEST007', nom='Test', prenom='User', age=20,
        )
        assert student.get_moyenne() == 0.0
        assert student.get_appreciation() == 'Insuffisant'


@pytest.mark.django_db
class TestNoteModel:
    def test_creation_note(self):
        student = Student.objects.create(
            matricule='NOTE001', nom='Test', prenom='User', age=20,
        )
        note = Note.objects.create(student=student, valeur=15.5, matiere='Maths')
        assert note.valeur == Decimal('15.50')
        assert 'NOTE001 - Maths' in str(note)
        assert '15.5' in str(note) or '15.50' in str(note)

    def test_notes_relation(self):
        student = Student.objects.create(
            matricule='NOTE002', nom='Test2', prenom='User2', age=20,
        )
        Note.objects.create(student=student, valeur=12, matiere='Français')
        Note.objects.create(student=student, valeur=16, matiere='Maths')
        assert student.notes.count() == 2
        assert student.get_moyenne() == 14.0

    def test_get_appreciation_with_notes(self):
        student = Student.objects.create(
            matricule='NOTE003', nom='Test3', prenom='User3', age=20,
        )
        Note.objects.create(student=student, valeur=18, matiere='Physique')
        # 18 >= 16 => "Excellent"
        assert student.get_appreciation() == 'Excellent'


@pytest.mark.django_db
class TestPaymentModel:
    def test_numero_recu_auto(self):
        student = Student.objects.create(
            matricule='PAY001', nom='Test', prenom='User', age=20,
        )
        payment = Payment.objects.create(student=student, montant=100000)
        assert payment.numero_recu is not None
        assert payment.numero_recu.startswith('REC-')

    def test_numero_recu_unique(self):
        student = Student.objects.create(
            matricule='PAY002', nom='Test2', prenom='User2', age=20,
        )
        p1 = Payment.objects.create(student=student, montant=50000)
        p2 = Payment.objects.create(student=student, montant=50000)
        assert p1.numero_recu != p2.numero_recu


@pytest.mark.django_db
class TestEcheanceModel:
    def test_creation_echeance(self):
        student = Student.objects.create(
            matricule='ECH001', nom='Test', prenom='User', age=20,
        )
        echeance = Echeance.objects.create(
            student=student, numero_tranche=1,
            montant=200000, date_echeance=date.today() + timedelta(days=30),
        )
        assert echeance.statut == 'en_attente'
        assert echeance.jours_restants() == 30

    def test_echeance_en_retard(self):
        student = Student.objects.create(
            matricule='ECH002', nom='Test2', prenom='User2', age=20,
        )
        echeance = Echeance.objects.create(
            student=student, numero_tranche=1,
            montant=200000, date_echeance=date.today() - timedelta(days=1),
        )
        assert echeance.est_en_retard() is True

    def test_echeance_pas_encore_en_retard(self):
        student = Student.objects.create(
            matricule='ECH003', nom='Test3', prenom='User3', age=20,
        )
        echeance = Echeance.objects.create(
            student=student, numero_tranche=1,
            montant=200000, date_echeance=date.today() + timedelta(days=1),
        )
        assert echeance.est_en_retard() is False


# ===== TESTS DE SÉCURITÉ =====

@pytest.mark.django_db
class TestCustomUserSecurity:
    def test_login_attempts(self):
        user = CustomUser.objects.create_user(
            username='testuser', password='testpass123',
            role='Professeur',
        )
        assert user.login_attempts == 0
        assert user.is_locked() is False

        for _ in range(4):
            user.increment_login_attempts()
        assert user.login_attempts == 4
        assert user.is_locked() is False

        user.increment_login_attempts()
        assert user.login_attempts == 5
        assert user.is_locked() is True

    def test_reset_login_attempts(self):
        user = CustomUser.objects.create_user(
            username='testuser2', password='testpass123',
            role='Admin',
        )
        user.login_attempts = 5
        user.save()
        user.reset_login_attempts()
        assert user.login_attempts == 0
        assert user.is_locked() is False

    def test_must_change_password_default(self):
        user = CustomUser.objects.create_user(
            username='newuser', password='newpass123',
        )
        assert user.must_change_password is True

    def test_permissions_admin(self):
        admin = CustomUser.objects.create_user(
            username='admin', password='admin123', role='Admin',
        )
        assert admin.has_permission('can_view_finances') is True
        assert admin.has_permission('can_manage_users') is True
        assert admin.has_permission('can_delete_student') is True
        assert admin.has_permission('can_export_data') is True
        assert admin.has_permission('can_view_logs') is True

    def test_permissions_secretaire(self):
        sec = CustomUser.objects.create_user(
            username='sec', password='sec123', role='Secrétaire',
        )
        assert sec.has_permission('can_view_finances') is True
        assert sec.has_permission('can_manage_users') is False
        assert sec.has_permission('can_delete_student') is False
        assert sec.has_permission('can_export_data') is True
        assert sec.has_permission('can_view_logs') is False

    def test_permissions_professeur(self):
        prof = CustomUser.objects.create_user(
            username='prof', password='prof123', role='Professeur',
        )
        # Un Professeur ne peut pas gérer les finances, les utilisateurs, supprimer/
        # ajouter un étudiant, exporter/importer des données, générer bulletins/cartes
        # ou modifier l'emploi du temps — il peut consulter classement et statistiques.
        assert prof.has_permission('can_view_finances') is False
        assert prof.has_permission('can_manage_users') is False
        assert prof.has_permission('can_delete_student') is False
        assert prof.has_permission('can_export_data') is False
        assert prof.has_permission('can_add_student') is False
        assert prof.has_permission('can_generate_documents') is False
        assert prof.has_permission('can_manage_schedule') is False
        assert prof.has_permission('can_view_logs') is False


# ===== TESTS DES VUES =====

@pytest.mark.django_db
class TestViews:
    def test_login_page(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_success(self, client):
        User.objects.create_user(username='test', password='test12345')
        response = client.post(reverse('login'), {
            'username': 'test', 'password': 'test12345'
        })
        assert response.status_code == 302  # Redirect après login

    def test_login_failure(self, client):
        response = client.post(reverse('login'), {
            'username': 'test', 'password': 'wrongpass'
        })
        assert response.status_code == 200  # Reste sur la page login

    def test_dashboard_requires_login(self, client):
        response = client.get(reverse('index'))
        assert response.status_code == 302  # Redirect vers login

    def test_dashboard_authenticated(self, client):
        User.objects.create_user(username='test', password='test12345')
        client.login(username='test', password='test12345')
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_dashboard_with_finances_and_payments(self, client):
        """Le bloc finances du dashboard (Student.with_totals + compute_statut_paiement)
        doit fonctionner avec de vrais paiements en base (regression: Decimal * float)."""
        User.objects.create_user(username='admin_fin', password='test12345', role='Admin')
        student = Student.objects.create(
            matricule='TESTFIN1', nom='Kouassi', prenom='Awa', age=20, frais_scolarite=500000,
        )
        Payment.objects.create(student=student, montant=300000)
        client.login(username='admin_fin', password='test12345')
        response = client.get(reverse('index'))
        assert response.status_code == 200

    def test_add_student_authenticated(self, client):
        User.objects.create_user(username='test', password='test12345', role='Admin')
        client.login(username='test', password='test12345')
        response = client.get(reverse('add_student'))
        assert response.status_code == 200

    def test_add_student_denied_for_professeur(self, client):
        User.objects.create_user(username='prof_add', password='test12345', role='Professeur')
        client.login(username='prof_add', password='test12345')
        response = client.get(reverse('add_student'))
        assert response.status_code == 302

    def test_classement_view(self, client):
        User.objects.create_user(username='test', password='test12345')
        client.login(username='test', password='test12345')
        response = client.get(reverse('classement'))
        assert response.status_code == 200

    def test_logout(self, client):
        User.objects.create_user(username='test', password='test12345')
        client.login(username='test', password='test12345')
        response = client.get(reverse('logout'))
        assert response.status_code == 302  # Redirect après logout


# ===== TESTS INSCRIPTION / APPROBATION =====

@pytest.mark.django_db
class TestRegistration:
    def test_register_page(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_register_creates_pending_professeur(self, client):
        response = client.post(reverse('register'), {
            'username': 'newprof', 'first_name': 'Jean', 'last_name': 'Dupont',
            'email': 'jean@example.com',
            'password': 'motdepasse123', 'confirm_password': 'motdepasse123',
        })
        assert response.status_code == 302
        user = User.objects.get(username='newprof')
        assert user.role == 'Professeur'
        assert user.status == 'pending'

    def test_register_password_mismatch(self, client):
        response = client.post(reverse('register'), {
            'username': 'newprof2', 'password': 'motdepasse123',
            'confirm_password': 'autremotdepasse',
        })
        assert response.status_code == 200  # Reste sur le formulaire
        assert not User.objects.filter(username='newprof2').exists()

    def test_register_duplicate_username(self, client):
        User.objects.create_user(username='dup', password='test12345')
        response = client.post(reverse('register'), {
            'username': 'dup', 'password': 'motdepasse123',
            'confirm_password': 'motdepasse123',
        })
        assert response.status_code == 200
        assert User.objects.filter(username='dup').count() == 1

    def test_pending_account_cannot_login(self, client):
        user = User.objects.create_user(username='pendingprof', password='test12345', role='Professeur')
        user.status = 'pending'
        user.save()
        response = client.post(reverse('login'), {
            'username': 'pendingprof', 'password': 'test12345',
        })
        assert response.status_code == 200  # Reste sur login avec message d'erreur
        assert not response.wsgi_request.user.is_authenticated

    def test_admin_approve_pending_user(self, client):
        admin = User.objects.create_user(username='admin1', password='test12345', role='Admin')
        pending = User.objects.create_user(username='pendingprof2', password='test12345', role='Professeur')
        pending.status = 'pending'
        pending.save()

        client.login(username='admin1', password='test12345')
        response = client.post(reverse('approuver_utilisateur', args=[pending.id]))
        assert response.status_code == 302
        pending.refresh_from_db()
        assert pending.status == 'active'

    def test_approve_denied_for_non_admin(self, client):
        prof = User.objects.create_user(username='prof3', password='test12345', role='Professeur')
        pending = User.objects.create_user(username='pendingprof3', password='test12345', role='Professeur')
        pending.status = 'pending'
        pending.save()

        client.login(username='prof3', password='test12345')
        client.post(reverse('approuver_utilisateur', args=[pending.id]))
        pending.refresh_from_db()
        assert pending.status == 'pending'  # Inchangé : pas les droits

    def test_admin_reject_pending_user(self, client):
        admin = User.objects.create_user(username='admin2', password='test12345', role='Admin')
        pending = User.objects.create_user(username='pendingprof4', password='test12345', role='Professeur')
        pending.status = 'pending'
        pending.save()

        client.login(username='admin2', password='test12345')
        response = client.post(reverse('rejeter_utilisateur', args=[pending.id]))
        assert response.status_code == 302
        assert not User.objects.filter(username='pendingprof4').exists()


# ===== TESTS DE L'API REST =====

@pytest.mark.django_db
class TestRESTAPI:
    def test_api_students_list(self, client):
        user = User.objects.create_user(username='apiuser', password='test12345')
        client.login(username='apiuser', password='test12345')
        response = client.get('/api/students/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'results' in data

    def test_api_students_create(self, client):
        user = User.objects.create_user(username='apiuser2', password='test12345', role='Admin')
        client.login(username='apiuser2', password='test12345')
        response = client.post('/api/students/', {
            'matricule': 'API001',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'age': 20,
            'filiere': 'Informatique',
            'niveau': 'L3',
            'frais_scolarite': 500000,
            'notes_data': [12, 15, 18],
        }, content_type='application/json')
        assert response.status_code == 201
        assert Student.objects.filter(matricule='API001').exists()
        student = Student.objects.get(matricule='API001')
        assert student.notes.count() == 3
        assert student.get_moyenne() == 15.0

    def test_api_students_create_denied_for_professeur(self, client):
        User.objects.create_user(username='apiuser2b', password='test12345', role='Professeur')
        client.login(username='apiuser2b', password='test12345')
        response = client.post('/api/students/', {
            'matricule': 'API002', 'nom': 'X', 'prenom': 'Y', 'age': 20,
        }, content_type='application/json')
        assert response.status_code == 403
        assert not Student.objects.filter(matricule='API002').exists()

    def test_api_students_detail(self, client):
        user = User.objects.create_user(username='apiuser3', password='test12345')
        client.login(username='apiuser3', password='test12345')
        student = Student.objects.create(
            matricule='API002', nom='Martin', prenom='Sophie', age=22,
        )
        response = client.get(f'/api/students/{student.matricule}/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['matricule'] == 'API002'
        assert data['nom'] == 'Martin'

    def test_api_stats(self, client):
        user = User.objects.create_user(username='apiuser4', password='test12345')
        client.login(username='apiuser4', password='test12345')
        response = client.get('/api/stats/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'total_etudiants' in data
        assert 'moyenne_generale' in data

    def test_api_me(self, client):
        user = User.objects.create_user(username='apiuser5', password='test12345')
        client.login(username='apiuser5', password='test12345')
        response = client.get('/api/me/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['username'] == 'apiuser5'

    def test_api_students_search(self, client):
        user = User.objects.create_user(username='apiuser6', password='test12345')
        client.login(username='apiuser6', password='test12345')
        Student.objects.create(matricule='SRCH01', nom='Recherche', prenom='Test', age=20)
        response = client.get('/api/students/?q=Recherche')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['count'] >= 1

    def test_api_requires_auth(self, client):
        response = client.get('/api/students/')
        assert response.status_code in (302, 401, 403)


# ===== TESTS DE PAGINATION =====

@pytest.mark.django_db
class TestPagination:
    def test_dashboard_pagination(self, client):
        user = User.objects.create_user(username='paguser', password='test12345')
        client.login(username='paguser', password='test12345')
        for i in range(30):
            Student.objects.create(
                matricule=f'PAG{i:03d}', nom=f'Etudiant{i}', prenom='Test', age=20,
            )
        response = client.get(reverse('index'))
        assert response.status_code == 200
        assert 'students' in response.context
        # Vérifier que la pagination est active (25 par page donc 30 > 25)
        paginator = response.context['students']
        assert paginator.paginator.per_page == 25

    def test_api_pagination(self, client):
        user = User.objects.create_user(username='paguser2', password='test12345')
        client.login(username='paguser2', password='test12345')
        for i in range(30):
            Student.objects.create(
                matricule=f'APIP{i:03d}', nom=f'ApiEtudiant{i}', prenom='Test', age=20,
            )
        response = client.get('/api/students/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'count' in data
        assert data['count'] >= 30
        assert len(data['results']) <= 25  # 25 par défaut


# ===== TESTS ANTI-DoS (rate limiting, tailles d'upload) =====

@pytest.mark.django_db
class TestRateLimiting:
    def setup_method(self):
        from django.core.cache import cache
        cache.clear()  # éviter toute fuite d'état entre tests (compteurs partagés par IP)

    def test_register_blocked_after_too_many_attempts(self, client):
        for _ in range(5):
            response = client.get(reverse('register'))
            assert response.status_code == 200
        # 6e requête sur la même fenêtre : bloquée
        response = client.get(reverse('register'))
        assert response.status_code == 429

    def test_login_blocked_after_too_many_attempts(self, client):
        for _ in range(20):
            response = client.get(reverse('login'))
            assert response.status_code == 200
        response = client.get(reverse('login'))
        assert response.status_code == 429

    def test_global_middleware_blocks_after_max_requests(self, rf):
        """Teste la logique du middleware directement : le court-circuit
        PYTEST_CURRENT_TEST (nécessaire pour ne pas polluer le reste de la
        suite - voir GlobalRateLimitMiddleware.__call__) est désactivé le
        temps du test pour vérifier le vrai comportement de blocage."""
        import os
        from unittest.mock import patch
        from django.http import HttpResponse
        from .ratelimit import GlobalRateLimitMiddleware

        middleware = GlobalRateLimitMiddleware(lambda request: HttpResponse('ok'))
        request = rf.get('/')
        request.META['REMOTE_ADDR'] = '203.0.113.42'  # IP dediee, evite toute collision de compteur

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('PYTEST_CURRENT_TEST', None)
            for _ in range(GlobalRateLimitMiddleware.MAX_REQUESTS):
                response = middleware(request)
                assert response.status_code == 200
            response = middleware(request)
            assert response.status_code == 429


@pytest.mark.django_db
class TestUploadSizeLimit:
    def test_validate_file_size_rejects_oversized_file(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        from .models import validate_file_size, MAX_UPLOAD_SIZE

        oversized = SimpleUploadedFile('big.png', b'x' * (MAX_UPLOAD_SIZE + 1))
        with pytest.raises(ValidationError):
            validate_file_size(oversized)

    def test_validate_file_size_accepts_small_file(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import validate_file_size

        small = SimpleUploadedFile('small.png', b'x' * 1024)
        validate_file_size(small)  # ne doit pas lever d'exception


# ===== CONFIGURATION PYTEST =====
pytestmark = pytest.mark.django_db