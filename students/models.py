from django.db import models
from django.utils import timezone


class Student(models.Model):
    matricule = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    age = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    photo = models.CharField(max_length=500, blank=True)
    date_ajout = models.DateTimeField(default=timezone.now)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    statut = models.CharField(max_length=50, default='Actif')
    filiere = models.CharField(max_length=200, blank=True)
    niveau = models.CharField(max_length=200, blank=True)
    frais_scolarite = models.FloatField(default=500000)

    class Meta:
        db_table = 'etudiants'
        managed = False
        ordering = ['-date_ajout']

    def notes_list(self):
        return [note.strip() for note in self.note.split(',') if note.strip()]

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"
