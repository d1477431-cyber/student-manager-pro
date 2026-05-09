# 📖 Guide Complet - ESGIS Manager PRO

## 🎯 Vue d'Ensemble

ESGIS Manager PRO est une application moderne de **gestion des étudiants** avec interface élégante, fonctionnalités complètes et design professionnel.

---

## 🚀 **DÉMARRAGE RAPIDE**

### Installation des dépendances
```bash
pip install pillow matplotlib reportlab opencv-python
```

### Lancer l'application
```bash
python gestionnaire.py
```

### Écran de connexion
- **Utilisateur** : `dodo`
- **Mot de passe** : `dodo`

> 💡 Les identifiants peuvent être modifiés dans le code (ligne ~120)

---

## 🎨 **INTERFACE PRINCIPALE**

### 1️⃣ Sidebar (Gauche)
**Navigation principale** avec 6 options :

| Bouton | Fonction | Icône |
|--------|----------|-------|
| Tableau de bord | Vue d'ensemble des stats | 📊 |
| Gestion Étudiants | Ajouter/Modifier/Supprimer | 👥 |
| Exporter CSV | Télécharger les données | 📊 |
| Sauvegarder | Backup JSON | 💾 |
| Thème | Basculer Sombre/Clair | 🌓 |
| Déconnexion | Retour à l'écran login | 🚪 |

### 2️⃣ Zone Principale (Droite)
**Contenu dynamique** qui change selon votre sélection

---

## 📊 **TABLEAU DE BORD**

### Cartes Statistiques
Affichent 3 métriques clés :
- **Total Étudiants** : Nombre total d'inscrits
- **Moyenne Générale** : Moyenne de toutes les notes
- **Meilleure Note** : La plus haute note enregistrée

### Graphiques
**Répartition par Mention** (Pie Chart)
- Excellent (≥18) 🟢
- Très bien (16-17) 🟣
- Bien (14-15) 🔵
- Assez bien (12-13) 🟠
- Passable (10-11) 🟡
- Insuffisant (<10) 🔴

**Top 5 Étudiants** (Bar Chart)
- Montre les 5 meilleurs étudiants
- Valeurs affichées sur les barres
- Légende avec noms des prénoms

---

## 👥 **GESTION DES ÉTUDIANTS**

### ➕ Ajouter un Étudiant

#### Formulaire - Section 1 : Infos Personnelles
| Champ | Type | Validation |
|-------|------|-----------|
| Matricule | Nombre entier | Obligatoire, unique |
| Nom | Texte | Obligatoire, >0 chars |
| Prénom | Texte | Obligatoire, >0 chars |
| Email | Email | Optionnel |
| Statut | Menu | Actif / Suspendu |
| Téléphone | Texte | Optionnel |
| Âge | Nombre | Obligatoire, 15-40 ans |

#### Formulaire - Section 2 : Photo
- Cliquez **📷 Choisir...** pour sélectionner une photo
- Formats supportés : PNG, JPG, JPEG, GIF, BMP
- Aperçu en direct (130x130 px)
- Photo sauvegardée dans le dossier `/photos`

#### Formulaire - Section 3 : Évaluation
- **Nombre de notes** : Optionnel (informatif)
- **Notes** : Séparées par des virgules
  - Ex: `15.5, 16, 14.5, 17, 18`
  - Validation : 0-20 uniquement
  - Moyenne calculée automatiquement

#### Boutons d'Action
- **➕ Ajouter** : Créer un nouvel étudiant (vert)
- **🔄 Réinitialiser** : Vider tous les champs (gris)

### ✏️ Modifier un Étudiant

1. Cliquez sur l'étudiant dans la liste
2. Cliquez **✏️ Modifier** ou faites un clic-droit
3. Modifiez les champs souhaités
4. Le matricule est **bloqué** en modification
5. Cliquez **💾 Enregistrer** (le bouton change)

### 🗑️ Supprimer un Étudiant

1. Sélectionnez l'étudiant dans la liste
2. Cliquez **🗑️ Supprimer**
3. Confirmez dans la fenêtre de dialogue
4. Données supprimées définitivement

### 🔍 Recherche

- Tapez dans **🔍 Rechercher...**
- Filtre en temps réel sur :
  - Nom de l'étudiant
  - Prénom
  - Matricule
- Résultats affichés instantanément

### 📧 Envoyer Email

1. Sélectionnez un étudiant (doit avoir un email)
2. Cliquez **📧 Email**
3. Votre client mail s'ouvre automatiquement
4. Email pré-rempli avec objet

---

## 📋 **LISTE DES ÉTUDIANTS**

### Colonnes Affichées
| Colonne | Contenu | Largeur |
|---------|---------|--------|
| Matricule | ID unique | 85px |
| Nom | Nom de famille | 95px |
| Prénom | Prénom | 95px |
| Âge | Âge en années | 55px |
| Moyenne | Note moyenne/20 | 85px |
| Appréciation | Mention (Excellent, Bien...) | 110px |

### Couleurs Dynamiques
Les lignes se colorent selon la moyenne :
- 🟢 **Excellent** : Vert (#27ae60) si ≥16
- 🔵 **Bon** : Cyan (#38BDF8) si 14-15
- 🟡 **Moyen** : Orange (#FBBF24) si 10-13
- 🔴 **Faible** : Rouge (#F87171) si <10

### Interactions
- **Clic gauche** : Sélectionner l'étudiant
- **Clic droit** : Menu contextuel avec 3 options
  - ✏️ Modifier
  - 📧 Envoyer Email
  - 🗑️ Supprimer
- **Double-clic sur colonne** : Trier par cette colonne

### Barre de Statut (Bas)
Affiche en temps réel :
- **Total** : Nombre total d'étudiants
- **Affichés** : Nombre après filtre
- **Moyenne générale** : Moyenne de la sélection

---

## 💾 **GESTION DES DONNÉES**

### Base de Données SQLite
- Fichier : `etudiants.db`
- Créé automatiquement au 1er lancement
- Stocke : Matricule, Infos, Notes, Photos, Dates

### Export CSV
1. Cliquez **📊 Exporter CSV** dans la sidebar
2. Choisissez l'emplacement et le nom
3. Fichier créé avec colonnes :
   - Matricule, Nom, Prénom, Email, Téléphone
   - Âge, Notes, Moyenne, Appréciation, Date

### Sauvegarder
1. Cliquez **💾 Sauvegarder** dans la sidebar
2. Crée un backup `etudiants.json`
3. Contient toutes les données (pour sécurité)

### Photos
- Stockées dans le dossier `/photos`
- Nommage : `{matricule}.{extension}`
  - Exemple : `2023001.jpg`
- Format : Auto-redimensionné 130x130 px

### Migration des Données
À la 1ère utilisation :
- Si JSON existant → Import automatique dans SQLite
- Aucune donnée perdue
- Migration confirmée par message

---

## 🌓 **THÈMES**

### Mode Sombre (Par Défaut)
- Fond : Bleu minuit (#0F172A)
- Texte : Gris clair (#CBD5E1)
- Accent : Cyan électrique (#38BDF8)
- Panneaux : Gris ardoise (#1E293B)

**Avantages** :
- 👁️ Réduit la fatigue oculaire
- 🌙 Idéal pour utilisation nocturne
- 💼 Aspect professionnel moderne

### Mode Clair
- Fond : Gris clair (#F1F5F9)
- Texte : Gris foncé (#334155)
- Accent : Cyan clair (#0EA5E9)
- Panneaux : Blanc pur (#FFFFFF)

**Avantages** :
- ☀️ Meilleure lisibilité en lumière naturelle
- 📑 Aspect classique/bureautique
- 👔 Format traditionnel

### Basculer les Thèmes
1. Cliquez **🌓 Thème** dans la sidebar
2. Interface remise à jour instantanément
3. Préférence sauvegardée par session

---

## ⌨️ **RACCOURCIS CLAVIER**

| Raccourci | Action |
|-----------|--------|
| `Enter` | Se connecter (écran login) |
| `Enter` | Ajouter étudiant (dans form) |
| `Tab` | Passer au champ suivant |
| `Shift+Tab` | Champ précédent |
| `Ctrl+A` | Sélectionner tout (text fields) |

---

## 🐛 **DÉPANNAGE**

### ❌ Erreur : "Impossible de charger l'image"
- ✅ Vérifiez le format (PNG, JPG, JPEG, GIF, BMP)
- ✅ Vérifiez que le fichier n'est pas corrompu
- ✅ Essayez une autre image

### ❌ Erreur : "Ce matricule existe déjà"
- ✅ Sélectionnez l'étudiant et modifiez (pas nouveau)
- ✅ Changez le matricule pour un nouveau

### ❌ Notes invalides
- ✅ Utilisez des nombres entre 0 et 20
- ✅ Séparez par des virgules
- ✅ Exemple correct : `15, 16.5, 14`

### ❌ Erreur Base de Données
- ✅ Supprimez `etudiants.db` pour réinitialiser
- ✅ Assurez-vous d'avoir les permissions d'écriture
- ✅ Vérifiez que SQLite3 est installé

### ❌ Interface floue (Windows)
- ✅ Code gère le DPI automatiquement
- ✅ Si problème : Changez de thème
- ✅ Redémarrez l'application

---

## 📊 **STATISTIQUES CALCULÉES**

### Moyenne
```
Moyenne = Somme des notes / Nombre de notes
Exemple : (15+16+14) / 3 = 15.00
```

### Appréciations
```
≥18 → ⭐ Excellent
16-17 → ✨ Très bien
14-15 → 👍 Bien
12-13 → ✓ Assez bien
10-11 → 👌 Passable
<10 → ❌ Insuffisant
```

### Répartition (Pie Chart)
- Compte le nombre d'étudiants par catégorie
- Affiche pourcentage et légende
- Couleurs = appréciations

---

## 💡 **BONNES PRATIQUES**

✅ **Sauvegardez régulièrement** → Cliquez 💾 Sauvegarder
✅ **Exportez les données** → CSV pour analyse Excel
✅ **Vérifiez les emails** → Avant d'envoyer des messages
✅ **Utilisez des photos** → Meilleure identification
✅ **Organisez les matricules** → Format cohérent (2023001, etc)
✅ **Mettez à jour les notes** → Régulièrement

❌ **Évitez** : Supprimer sans confirmer
❌ **Évitez** : Notes incorrectes (>20)
❌ **Évitez** : Matricules dupliqués
❌ **Évitez** : Laisser des champs vides (sauf Email/Tél)

---

## 🔐 **SÉCURITÉ**

- **Authentification** : Login obligatoire au démarrage
- **Base de Données** : SQLite (local, sécurisé)
- **Photos** : Stockées localement dans `/photos`
- **Backup** : JSON créé via 💾 Sauvegarder
- **Pas de cloud** : Données 100% locales

---

## ⚙️ **CONFIGURATION AVANCÉE**

### Modifier les Identifiants de Connexion
Fichier : `gestionnaire.py` (ligne ~120)
```python
if user == "dodo" and password == "dodo":
    # Changez "dodo" par vos identifiants
```

### Modifier la Couleur d'Accent
Fichier : `gestionnaire.py` (ligne ~80)
```python
"accent": "#38BDF8",  # Changez le code hex
```

### Changer la Validation d'Âge
Fichier : `gestionnaire.py` (ligne ~850)
```python
if age < 15 or age > 40:  # Modifiez 15 et 40
```

---

## 📞 **SUPPORT**

Pour toute question ou amélioration :
- Consultez les logs dans le terminal
- Vérifiez les fichiers temporaires : `*.db`, `*.json`
- Réinstallez les dépendances : `pip install -r requirements.txt`

---

**Manager PRO** - Conçu pour la gestion efficace et moderne 🎓

*Version 2.0 PRO - Mai 2026*
