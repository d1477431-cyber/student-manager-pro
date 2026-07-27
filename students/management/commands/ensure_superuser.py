from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class Command(BaseCommand):
    help = "Crée le superutilisateur par défaut s'il n'existe pas"

    def handle(self, *args, **options):
        username = 'dodo'
        password = 'dodo'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create(
                username=username,
                password=make_password(password),
                role='Admin',
                status='active',
                is_superuser=True,
                is_staff=True,
                is_active=True,
                must_change_password=False,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Superutilisateur '{username}' créé avec succès"))
        else:
            user = User.objects.get(username=username)
            user.password = make_password(password)
            user.role = 'Admin'
            user.status = 'active'
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.must_change_password = False
            user.login_attempts = 0
            user.locked_until = None
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Mot de passe du superutilisateur '{username}' réinitialisé"))