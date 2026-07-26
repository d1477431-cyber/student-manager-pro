# 🎓 Student Manager PRO

Application web professionnelle de gestion des étudiants — développée avec **Django 6**, **MySQL/SQLite**, **REST API**, et une interface moderne responsive.

## 🚀 Fonctionnalités

| Module | Description |
|---|---|
| **Dashboard** | Tableau de bord avec statistiques en temps réel, graphiques (Matplotlib), vue paginée |
| **Gestion Étudiants** | Ajout, modification, suppression, photo, notes, moyenne automatique |
| **Paiements** | Suivi financier, reçus PDF (ReportLab), échéances, rappels email |
| **Absences** | Enregistrement des absences avec/sans justification |
| **Emploi du temps** | Planning interactif des cours par filière et niveau |
| **Messagerie interne** | Communication entre utilisateurs de l'application |
| **Classement** | Classement des étudiants par moyenne avec filtres |
| **Import/Export CSV** | Importation par fichier CSV, export CSV et Excel (openpyxl) |
| **Utilisateurs & Rôles** | Multi-utilisateurs avec permissions granulaires |
| **Journal d'audit** | Logs détaillés de toutes les actions |
| **API REST** | API complète avec authentification JWT (djangorestframework) |
| **Thème clair/sombre** | Basculement en un clic avec persistance localStorage |

## 🖥️ Aperçu de l'interface

- **Sidebar** : Navigation entre sections avec indicateur actif (barre verticale + fond teinté), icônes SVG Lucide-style, profil utilisateur avec menu déroulant
- **Topbar** : Barre de recherche globale (Ctrl+K), titre de page, bouton thème clair/sombre
- **Responsive** : Sidebar en drawer sur mobile avec overlay — hamburger pour l'ouvrir

## ⚙️ Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/d1477431-cyber/gestion-des-etudiant.git
cd application web
```

### 2. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement
```bash
# Copier le fichier .env.example en .env et ajuster si besoin
# Par défaut : SQLite, pas de configuration supplémentaire nécessaire
```

### 5. Initialiser la base de données
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

Rendez-vous sur **http://127.0.0.1:8000**

## 🔐 Accès

- Créez un superutilisateur avec `python manage.py createsuperuser`
- Connectez-vous sur la page de login
- L'interface d'administration est accessible sur `/admin/`

## 🗄️ Base de données

- **Par défaut (développement)** : SQLite (`etudiants.db`) — aucune configuration requise
- **Recommandé (production)** : PostgreSQL — définissez `DATABASE_URL` dans `.env` :
  ```
  DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/student_manager
  ```
- **Alternative** : MySQL — définissez `DATABASE_URL` dans `.env` :
  ```
  DATABASE_URL=mysql://user:password@localhost/nom_base
  ```

> 💡 **Conseil** : Pour la production, utilisez PostgreSQL. Il suffit de décommenter la ligne `DATABASE_URL` dans le fichier `.env` avec les bons identifiants. Aucune modification de code n'est nécessaire grâce à `dj-database-url`.

## 🧪 Tests

```bash
pytest
```

## 🧩 Dépendances principales

- **Django 6.x** — Framework web
- **Django REST Framework** — API REST + JWT
- **Pillow** — Gestion des photos
- **python-dotenv** — Configuration
- **openpyxl** — Export Excel *(optionnel)*
- **ReportLab** — PDF reçus/bulletins *(optionnel)*
- **Matplotlib** — Graphiques statistiques *(optionnel)*
- **psycopg2-binary** — Support PostgreSQL *(recommandé pour la production)*
- **mysql-connector-python** — Support MySQL *(optionnel)*

## 📄 Licence

Projet pédagogique — MIT