import ast
from decimal import Decimal


def parse_notes(value):
    """Convertit une chaîne de notes en liste de floats (pour compatibilité)"""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [float(item) for item in value]

    text = str(value).strip()
    if not text:
        return []

    if text.startswith('[') and text.endswith(']'):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, (list, tuple)):
                return [float(item) for item in parsed]
        except (ValueError, SyntaxError):
            pass

    return [float(part.strip()) for part in text.replace('[', '').replace(']', '').split(',') if part.strip()]


def calculate_average(notes):
    """Calcule la moyenne à partir d'une liste de notes (compatibilité)"""
    values = parse_notes(notes)
    return sum(values) / len(values) if values else 0.0


def compute_statut_paiement(total_paye, frais_scolarite):
    """Même logique que Student.statut_paiement(), mais à partir de valeurs déjà
    calculées (ex. via une annotation ORM en une seule requête) pour éviter
    l'anti-pattern N+1 quand on traite une liste d'étudiants."""
    if total_paye >= frais_scolarite:
        return "À jour"
    if total_paye >= frais_scolarite * Decimal('0.5'):
        return "Partiel"
    return "En retard"


def get_appreciation(moyenne):
    if moyenne >= 16:
        return 'Excellent'
    if moyenne >= 14:
        return 'Assez bien'
    if moyenne >= 12:
        return 'Bien'
    if moyenne >= 10:
        return 'Passable'
    return 'À renforcer'


def sanitize_cell(value):
    """Neutralise l'injection de formule CSV/Excel (CWE-1236).

    Si la valeur est une chaîne commençant par un caractère qu'Excel/LibreOffice
    interprète comme un début de formule (=, +, -, @, tabulation, retour chariot),
    on la préfixe d'une apostrophe pour forcer son interprétation en texte brut.
    """
    if isinstance(value, str) and value[:1] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + value
    return value