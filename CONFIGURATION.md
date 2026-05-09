# ⚙️ Configuration Personnalisée - Manager PRO

## 📋 Personnalisation Avancée

Ce fichier explique comment customizer votre gestionnaire selon vos besoins.

---

## 🎨 **PERSONNALISER LES COULEURS**

### Localisation
Fichier : `gestionnaire.py`
Ligne : ~55-75 (dans la classe `GestionEtudiantsApp.__init__`)

### Structure des Thèmes
```python
self.themes = {
    "dark": {
        "bg_main": "#0F172A",      # Fond principal
        "bg_panel": "#1E293B",     # Fond des panneaux
        "bg_input": "#334155",     # Champs de saisie
        "bg_header": "#0F172A",    # En-têtes
        "fg_text": "#CBD5E1",      # Texte principal
        "fg_head": "#F8FAFC",      # Titres
        "accent": "#38BDF8",       # Couleur accentuée
        "success": "#4ADE80",      # Vert (validation)
        "warning": "#FBBF24",      # Orange (modification)
        "danger": "#F87171",       # Rouge (suppression)
        "border": "#475569"        # Bordures
    },
    "light": { ... }
}
```

### Code Couleurs Hex
```
Bleu : #0F172A, #1E293B, #334155, #38BDF8, #0EA5E9
Gris : #CBD5E1, #F8FAFC, #95a5a6, #bdc3c7
Vert : #27ae60, #2ecc71, #4ADE80, #86efac
Orange : #FBBF24, #fcd34d, #f39c12, #f1c40f
Rouge : #F87171, #fca5a5, #e74c3c, #ec7063
```

### Exemple : Changer l'Accent Principal
```python
# Avant (Cyan)
"accent": "#38BDF8",

# Après (Violet)
"accent": "#9b59b6",
```

---

## 👤 **MODIFIER LES IDENTIFIANTS DE CONNEXION**

### Localisation
Fichier : `gestionnaire.py`
Classe : `LoginWindow.login()` (ligne ~120)

### Code Original
```python
if user == "dodo" and password == "dodo":
    self.window.destroy()
    self.on_success()
else:
    messagebox.showerror("Erreur", "Identifiants incorrects\n")
```

### Modification Simple
```python
# Changer les identifiants
if user == "admin" and password == "admin2024":
    self.window.destroy()
    self.on_success()
```

### Modification Avancée (Multi-utilisateurs)
```python
# Dictionnaire d'utilisateurs
users = {
    "admin": "admin123",
    "manager": "manager456",
    "assistant": "assist789"
}

if user in users and password == users[user]:
    self.window.destroy()
    self.on_success()
else:
    messagebox.showerror("Erreur", "Identifiants incorrects")
```

---

## 📏 **AJUSTER LES DIMENSIONS**

### Fenêtre Principale
Fichier : `gestionnaire.py` (ligne ~120)
```python
self.root.geometry("1400x800")  # Largeur x Hauteur

# Propositions :
# - 1920x1080  # Full HD (grands écrans)
# - 1366x768   # Laptop standard
# - 1024x768   # Petit écran
```

### Sidebar
Fichier : `gestionnaire.py` (ligne ~250)
```python
sidebar = tk.Frame(main_container, bg=sidebar_bg, width=280)
# Augmentez 280 pour une sidebar plus large
# Baissez pour une sidebar plus étroite
```

### Formulaire Photo
Fichier : `gestionnaire.py` (ligne ~650)
```python
self.photo_canvas = tk.Canvas(photo_frame, width=130, height=130, ...)
# Changez 130 pour agrandir/réduire la photo
```

### Treeview (Liste Étudiants)
Fichier : `gestionnaire.py` (ligne ~350)
```python
rowheight=40,  # Hauteur des lignes (augmentez pour plus d'espace)
# Propositions : 30 (compact), 40 (normal), 50 (aéré)
```

---

## 🔤 **MODIFIER LES POLICES**

### Polices par Défaut
```python
("Segoe UI", 26, "bold")      # Grand titre (Tableau de bord)
("Segoe UI", 22, "bold")      # Titre page
("Segoe UI", 12, "bold")      # Sous-titre
("Segoe UI", 10)              # Texte normal
("Segoe UI", 9, "bold")       # Petit texte gras
("Courier", 10)               # Monospace (logs)
```

### Alternative : Arial
```python
# Remplacer partout "Segoe UI" par "Arial"
# Ou : "Times New Roman", "Calibri", "Verdana"
```

### Changer les Tailles
Fichier : `gestionnaire.py`

**Avant**
```python
tk.Label(header_frame, text="📊 Tableau de Bord", 
         font=("Segoe UI", 26, "bold"))
```

**Après** (plus petit)
```python
tk.Label(header_frame, text="📊 Tableau de Bord", 
         font=("Segoe UI", 22, "bold"))
```

---

## ✅ **MODIFIER LES VALIDATIONS**

### Âge
Fichier : `gestionnaire.py` (ligne ~850)
```python
# Original
if age < 15 or age > 40:
    messagebox.showerror("❌ Erreur", "L'âge doit être entre 15 et 40 ans")

# Modification
if age < 16 or age > 60:
    messagebox.showerror("❌ Erreur", "L'âge doit être entre 16 et 60 ans")
```

### Notes (Entre 0 et 20)
Fichier : `gestionnaire.py` (ligne ~880)
```python
# Original
if note < 0 or note > 20:

# Modification (0 à 100)
if note < 0 or note > 100:
```

### Matricule Unique
Fichier : `gestionnaire.py` (ligne ~825)
```python
# Vérification existante
for etudiant in self.etudiants:
    if etudiant["matricule"] == matricule:
        messagebox.showerror("❌ Erreur", "Ce matricule existe déjà")
        return
```

---

## 📊 **PERSONNALISER LES STATISTIQUES**

### Mentions (Appréciations)
Fichier : `gestionnaire.py` (ligne ~1065)
```python
# Original
def get_appreciation(self, moyenne):
    if moyenne >= 18:
        return "⭐ Excellent"
    elif moyenne >= 16:
        return "✨ Très bien"
    elif moyenne >= 14:
        return "👍 Bien"
    elif moyenne >= 12:
        return "✓ Assez bien"
    elif moyenne >= 10:
        return "👌 Passable"
    else:
        return "❌ Insuffisant"

# Personnalisé
def get_appreciation(self, moyenne):
    if moyenne >= 17:
        return "🏆 A - Excellent"
    elif moyenne >= 15:
        return "⭐ B - Très Bien"
    elif moyenne >= 13:
        return "👍 C - Bien"
    elif moyenne >= 11:
        return "✓ D - Acceptable"
    else:
        return "❌ F - Faible"
```

### Répartition du Pie Chart
Fichier : `gestionnaire.py` (ligne ~470)
```python
# Original
mentions = {"Excellent": 0, "Très bien": 0, "Bien": 0, ...}
for m in moyennes:
    if m >= 18: mentions["Excellent"] += 1
    elif m >= 16: mentions["Très bien"] += 1
    ...

# Personnalisé
mentions = {"A+ (20)": 0, "A (18-19)": 0, "B": 0, ...}
for m in moyennes:
    if m >= 19: mentions["A+ (20)"] += 1
    elif m >= 17: mentions["A (18-19)"] += 1
```

---

## 📁 **STRUCTURE DES FICHIERS**

### Arborescence Attendue
```
application reussi/
├── gestionnaire.py          # Application principale
├── etudiants.db            # Base de données SQLite (créée auto)
├── etudiants.json          # Backup JSON (optionnel)
├── photos/                 # Dossier des photos étudiants
│   ├── 2023001.jpg
│   ├── 2023002.png
│   └── ...
├── AMELIORATIONS_PRO.md    # Documentation améliorations
├── GUIDE_COMPLET.md        # Guide d'utilisation
└── CONFIGURATION.md        # Ce fichier
```

---

## 🔧 **AJOUTEZ DE NOUVELLES COLONNES**

### Ajouter "Classe" à la Base de Données

**Étape 1 : Modifier la création de table**
```python
# Fichier : gestionnaire.py, fonction init_db()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS etudiants (
        matricule INTEGER PRIMARY KEY,
        nom TEXT,
        prenom TEXT,
        age INTEGER,
        note TEXT,
        photo TEXT,
        date_ajout TEXT,
        email TEXT,
        telephone TEXT,
        classe TEXT          # ← AJOUTÉE
    )
""")
```

**Étape 2 : Ajouter le champ au formulaire**
```python
# Dans create_form()
tk.Label(inputs_frame, text="Classe:", font=("Segoe UI", 9, "bold"), 
        bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
self.classe_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), ...)
self.classe_entry.pack(anchor=tk.W, pady=(0, 12), ipady=6)
```

**Étape 3 : Ajouter au Treeview**
```python
# Dans create_gestion_view()
self.tree = ttk.Treeview(tree_container, 
    columns=("Matricule", "Nom", "Prénom", "Classe", "Âge", "Moyenne", "Appréciation"), 
    height=15, yscrollcommand=scrollbar.set)

self.tree.column("Classe", anchor=tk.CENTER, width=80)
self.tree.heading("Classe", text="Classe")
```

---

## 🌐 **IMPORTER/EXPORTER AVANCÉ**

### Export Excel (.xlsx)
```bash
pip install openpyxl
```

Ajouter à `gestionnaire.py` :
```python
def exporter_excel(self):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    
    # En-têtes
    headers = ['Matricule', 'Nom', 'Prénom', 'Email', 'Âge', 'Moyenne', 'Appréciation']
    ws.append(headers)
    
    # Données
    for etudiant in self.etudiants:
        notes = etudiant.get("note", [])
        moyenne = sum(notes) / len(notes) if notes else 0
        ws.append([
            etudiant['matricule'],
            etudiant['nom'],
            etudiant['prenom'],
            etudiant.get('email', ''),
            etudiant['age'],
            f"{moyenne:.2f}",
            self.get_appreciation(moyenne)
        ])
    
    path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if path:
        wb.save(path)
        self.show_toast("✅ Export Excel réussi")
```

---

## 🎬 **PERSONNALISER LES ANIMATIONS**

### Durée du Fade-in
Fichier : `gestionnaire.py` (ligne ~180)
```python
# Original (plus lent)
alpha += 0.08
self.window.after(10, fade_in, alpha)

# Rapide
alpha += 0.15
self.window.after(5, fade_in, alpha)

# Très lent
alpha += 0.02
self.window.after(20, fade_in, alpha)
```

### Toast (Notification)
Fichier : `gestionnaire.py` (ligne ~580)
```python
# Durée : 3000ms (3 secondes)
self.root.after(3000, fade_out)

# Modifier la durée
self.root.after(5000, fade_out)  # 5 secondes
```

---

## 🔐 **SÉCURITÉ RENFORCÉE**

### Chiffrer les Identifiants
```bash
pip install bcrypt
```

```python
import bcrypt

# Créer hash au démarrage
def hash_password(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())

# Vérifier au login
if bcrypt.checkpw(password.encode(), hashed_password):
    self.on_success()
```

---

## 📞 **CONTACTEZ L'ADMINISTRATEUR**

Pour des modifications plus complexes :
- Modifiez le code directement
- Testez en local avec `python gestionnaire.py`
- Vérifiez que les dépendances sont installées
- Consultez le GUIDE_COMPLET.md

---

**Dernière mise à jour** : Mai 2026
**Version** : 2.0 PRO
