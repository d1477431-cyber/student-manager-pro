from django import forms
from .models import Student

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