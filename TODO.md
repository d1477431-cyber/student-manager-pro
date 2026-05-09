# TODO — Transformer gestionnaire en logiciel PRO (Tkinter)

## Étape 1 — Préparer l’architecture
- [ ] Créer un dossier `gestionnaire_pro/`.
- [ ] Ajouter une structure de packages: `ui/`, `core/`, `config/`.

## Étape 2 — Extraire la logique métier
- [ ] Créer `core/db.py` avec `StudentRepository` (init DB, charger, CRUD, migration JSON->SQLite, sauvegarde JSON).
- [ ] Créer `core/validation.py` avec `StudentValidator` (notes 0..20, age 15..40, parsing notes, format matricule).
- [ ] Créer `core/calculs.py` (moyenne, mention/appréciation, top 5).

## Étape 3 — Isoler le thème & constantes
- [ ] Créer `config/theme.py` (palette dark/light) + éventuellement persistance du thème.

## Étape 4 — Réorganiser l’UI
- [ ] Créer `ui/login_window.py` (LoginWindow).
- [ ] Créer `ui/main_app.py` (GestionEtudiantsApp) qui orchestre pages et widgets.
- [ ] Créer `ui/pages/dashboard.py` + `ui/pages/gestion.py`.

## Étape 5 — Compatibilité & entrée programme
- [ ] Ajouter `gestionnaire_pro/__main__.py` pour lancer l’app.
- [ ] Modifier `gestionnaire.py` en wrapper qui lance `gestionnaire_pro.__main__` (comportement identique).
- [ ] Mettre à jour `GestionEtudiants.spec` si nécessaire.

## Étape 6 — QA
- [ ] Tester: login, ajout/modif/suppression, photo, recherche, tri, menu contextuel, export CSV, dashboard graphs, toggle thème.
- [ ] Corriger les régressions.

