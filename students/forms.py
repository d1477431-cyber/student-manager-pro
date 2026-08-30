from django import forms
from .models import Student, CustomUser

class StudentForm(forms.ModelForm):
    note_str = forms.CharField(
        label="Notes (séparées par des virgules)",
        help_text="Ex: 12, 15.5, 18",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '12, 15.5, 18'})
    )

    class Meta:
        model = Student
        fields = [
            'matricule', 'nom', 'prenom', 'age', 'photo',
            'email', 'telephone', 'statut', 'filiere', 'niveau',
            'frais_scolarite', 'note_str'
        ]

    def clean_note_str(self):
        notes_text = self.cleaned_data.get('note_str', '')
        if not notes_text:
            return []
        return [float(n.strip()) for n in notes_text.split(',') if n.strip()]


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe',
            'minlength': 8,
            'autocomplete': 'new-password'
        }),
        min_length=8,
        help_text="Minimum 8 caractères"
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre nouveau mot de passe',
            'autocomplete': 'new-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class RegisterForm(forms.Form):
    """Inscription d'un compte Professeur : reste en attente d'approbation admin."""
    username = forms.CharField(
        max_length=150, label="Identifiant",
        widget=forms.TextInput(attrs={'placeholder': 'Choisissez un identifiant', 'autofocus': True}),
    )
    first_name = forms.CharField(
        max_length=150, required=False, label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre prénom'}),
    )
    last_name = forms.CharField(
        max_length=150, required=False, label="Nom",
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom'}),
    )
    email = forms.EmailField(
        required=False, label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com'}),
    )
    password = forms.CharField(
        label="Mot de passe", min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'Minimum 8 caractères', 'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Retapez le mot de passe', 'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Cet identifiant est déjà utilisé.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data