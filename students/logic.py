import ast


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