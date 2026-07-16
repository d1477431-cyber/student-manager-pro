from django import forms


class StudentForm(forms.Form):
    matricule = forms.IntegerField(label='Matricule')
    nom = forms.CharField(label='Nom', max_length=200)
    prenom = forms.CharField(label='Prénom', max_length=200)
    age = forms.IntegerField(label='Âge', required=False)
    note = forms.CharField(label='Notes', required=False, widget=forms.Textarea)
    filiere = forms.CharField(label='Filière', required=False, max_length=200)
    niveau = forms.CharField(label='Niveau', required=False, max_length=200)
    email = forms.EmailField(label='Email', required=False)
    telephone = forms.CharField(label='Téléphone', required=False, max_length=50)
    statut = forms.ChoiceField(label='Statut', choices=[('Actif', 'Actif'), ('Suspendu', 'Suspendu')])
    frais_scolarite = forms.FloatField(label='Frais de scolarité', required=False, initial=500000)
