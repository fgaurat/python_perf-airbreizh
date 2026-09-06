"""Le vocabulaire du métier : un montant dans une devise, et les erreurs possibles."""

from dataclasses import dataclass


class ErreurDevises(Exception):
    """Racine des erreurs du module."""


class SourceIndisponible(ErreurDevises):
    """La source de taux ne répond pas."""


class DonneesInvalides(ErreurDevises):
    """La source a répondu, mais pas dans le format attendu."""


class DeviseInconnue(ErreurDevises):
    """Aucun taux n'existe pour cette devise."""


@dataclass(frozen=True)
class Montant:
    valeur: float
    devise: str

    def __post_init__(self) -> None:
        if len(self.devise) != 3 or not self.devise.isupper():
            raise DeviseInconnue(f"code de devise invalide : {self.devise!r} (attendu 3 lettres)")
