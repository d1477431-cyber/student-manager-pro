# Liste globale pour stocker les étudiants
etudiants = []

def ajouter_etudiant():
    print("\n--- AJOUTER UN ÉTUDIANT ---")
    nom = input("Nom : ")
    prenom = input("Prénom : ")
    
    # Saisie des notes
    notes_str = input("Entrez les notes (séparées par des virgules, ex: 12, 15.5) : ")
    notes = []
    if notes_str:
        try:
            # On convertit chaque note en nombre
            for n in notes_str.split(','):
                notes.append(float(n.strip()))
        except ValueError:
            print("Erreur : Certaines notes ne sont pas valides.")
    
    # Création du dictionnaire étudiant
    etudiant = {
        "nom": nom,
        "prenom": prenom,
        "notes": notes
    }
    
    # Ajout à la liste
    etudiants.append(etudiant)
    print(f"Étudiant {nom} {prenom} ajouté avec succès !")

def afficher_etudiants():
    print("\n--- LISTE DES ÉTUDIANTS ---")
    if not etudiants:
        print("Aucun étudiant dans la liste.")
        return

    for i, e in enumerate(etudiants, 1):
        nom_complet = f"{e['nom']} {e['prenom']}"
        notes = e['notes']
        
        if notes:
            moyenne = sum(notes) / len(notes)
            print(f"{i}. {nom_complet} | Notes: {notes} | Moyenne: {moyenne:.2f}")
        else:
            print(f"{i}. {nom_complet} | Pas de notes")

def menu():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1. Ajouter un étudiant")
        print("2. Afficher la liste")
        print("3. Quitter")
        
        choix = input("Votre choix : ")
        
        if choix == "1":
            ajouter_etudiant()
        elif choix == "2":
            afficher_etudiants()
        elif choix == "3":
            print("Au revoir !")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    menu()