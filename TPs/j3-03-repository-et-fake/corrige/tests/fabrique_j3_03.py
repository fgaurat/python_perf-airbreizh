"""Aides pour construire des tâches en une ligne dans les tests."""

from datetime import date

from suivi.modele import Tache

JOUR = date(2026, 9, 15)


def tache(id_: int, titre: str, **champs) -> Tache:
    """Une tâche avec des valeurs par défaut sensées, pour écrire des tests courts."""
    valeurs = {
        "projet": "site-web",
        "assignee": "ada",
        "creee_le": date(2026, 9, 1),
        "echeance": date(2026, 9, 30),
        "terminee": False,
    }
    valeurs.update(champs)
    return Tache(id_, titre, **valeurs)  # type: ignore[arg-type]
