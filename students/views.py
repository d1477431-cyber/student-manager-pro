from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import StudentForm
from .models import Student


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie.')
            return redirect('index')
        messages.error(request, 'Identifiant ou mot de passe invalide.')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')


@login_required
def index(request):
    students = Student.objects.all()
    return render(request, 'students/index.html', {'students': students})


@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            if Student.objects.filter(matricule=form.cleaned_data['matricule']).exists():
                messages.error(request, 'Ce matricule existe déjà.')
            else:
                Student.objects.create(
                    matricule=form.cleaned_data['matricule'],
                    nom=form.cleaned_data['nom'],
                    prenom=form.cleaned_data['prenom'],
                    age=form.cleaned_data['age'],
                    note=form.cleaned_data['note'],
                    date_ajout=timezone.now(),
                    email=form.cleaned_data['email'],
                    telephone=form.cleaned_data['telephone'],
                    statut=form.cleaned_data['statut'],
                    filiere=form.cleaned_data['filiere'],
                    niveau=form.cleaned_data['niveau'],
                    frais_scolarite=form.cleaned_data['frais_scolarite'] or 0.0,
                )
                messages.success(request, 'Étudiant ajouté avec succès.')
                return redirect('index')
    else:
        form = StudentForm()

    return render(request, 'students/add_student.html', {'form': form})


@login_required
def edit_student(request, matricule):
    student = get_object_or_404(Student, matricule=matricule)
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            Student.objects.filter(matricule=student.matricule).update(
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                age=form.cleaned_data['age'],
                note=form.cleaned_data['note'],
                email=form.cleaned_data['email'],
                telephone=form.cleaned_data['telephone'],
                statut=form.cleaned_data['statut'],
                filiere=form.cleaned_data['filiere'],
                niveau=form.cleaned_data['niveau'],
                frais_scolarite=form.cleaned_data['frais_scolarite'] or 0.0,
            )
            messages.success(request, 'Étudiant modifié avec succès.')
            return redirect('index')
    else:
        form = StudentForm(initial={
            'matricule': student.matricule,
            'nom': student.nom,
            'prenom': student.prenom,
            'age': student.age,
            'note': student.note,
            'filiere': student.filiere,
            'niveau': student.niveau,
            'email': student.email,
            'telephone': student.telephone,
            'statut': student.statut,
            'frais_scolarite': student.frais_scolarite,
        })

    return render(request, 'students/edit_student.html', {'form': form, 'student': student})


@login_required
def delete_student(request, matricule):
    if request.method == 'POST':
        student = get_object_or_404(Student, matricule=matricule)
        student.delete()
        messages.success(request, 'Étudiant supprimé.')
    return redirect('index')


def add_student(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        age = request.POST.get('age', '').strip()
        notes = request.POST.get('notes', '').strip()
        filiere = request.POST.get('filiere', '').strip()
        niveau = request.POST.get('niveau', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        statut = request.POST.get('statut', 'Actif').strip()
        frais = request.POST.get('frais_scolarite', '500000').strip()

        if not matricule or not nom or not prenom:
            messages.error(request, 'Le matricule, le nom et le prénom sont obligatoires.')
            return redirect('add_student')

        try:
            matricule_value = int(matricule)
        except ValueError:
            messages.error(request, 'Le matricule doit être un nombre entier.')
            return redirect('add_student')

        try:
            age_value = int(age) if age else None
        except ValueError:
            messages.error(request, 'L\'âge doit être un nombre entier.')
            return redirect('add_student')

        try:
            frais_value = float(frais) if frais else 0.0
        except ValueError:
            messages.error(request, 'Les frais doivent être un nombre valide.')
            return redirect('add_student')

        if Student.objects.filter(matricule=matricule_value).exists():
            messages.error(request, 'Ce matricule existe déjà.')
            return redirect('add_student')

        Student.objects.create(
            matricule=matricule_value,
            nom=nom,
            prenom=prenom,
            age=age_value,
            note=notes,
            date_ajout=timezone.now(),
            email=email,
            telephone=telephone,
            statut=statut,
            filiere=filiere,
            niveau=niveau,
            frais_scolarite=frais_value,
        )
        messages.success(request, 'Étudiant ajouté avec succès.')
        return redirect('index')

    return render(request, 'students/add_student.html')


def delete_student(request, matricule):
    if request.method == 'POST':
        student = get_object_or_404(Student, matricule=matricule)
        student.delete()
        messages.success(request, 'Étudiant supprimé.')
    return redirect('index')
