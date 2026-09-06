"""Historique des calculs — le bourgeon, écrit en TDD à côté du moteur.

Ne connaît ni le moteur, ni la mémoire, ni le journal : une pile d'entrées,
une pile d'annulations, une capacité.
"""

from collections import deque
from dataclasses import dataclass

CAPACITE_DEFAUT = 10


class HistoriqueVide(Exception):
    """Rien à annuler, ou rien à rétablir."""


@dataclass(frozen=True)
class Entree:
    expression: str
    resultat: float


class Historique:
    def __init__(self, capacite: int = CAPACITE_DEFAUT) -> None:
        if capacite < 1:
            raise ValueError(f"capacite = {capacite} : attendu >= 1")
        self._entrees: deque[Entree] = deque(maxlen=capacite)
        self._annulees: list[Entree] = []
        self.capacite = capacite

    def __len__(self) -> int:
        return len(self._entrees)

    @property
    def courant(self) -> Entree | None:
        """La dernière entrée non annulée, ou None."""
        return self._entrees[-1] if self._entrees else None

    def enregistrer(self, expression: str, resultat: float) -> Entree:
        """Ajoute une entrée. Tout ce qui avait été annulé ne peut plus être rétabli."""
        entree = Entree(expression, resultat)
        self._entrees.append(entree)
        self._annulees.clear()
        return entree

    def annuler(self) -> Entree:
        """Retire la dernière entrée et la retourne."""
        if not self._entrees:
            raise HistoriqueVide("rien à annuler")
        entree = self._entrees.pop()
        self._annulees.append(entree)
        return entree

    def retablir(self) -> Entree:
        """Remet la dernière entrée annulée."""
        if not self._annulees:
            raise HistoriqueVide("rien à rétablir")
        entree = self._annulees.pop()
        self._entrees.append(entree)
        return entree

    def derniers(self, n: int = CAPACITE_DEFAUT) -> list[Entree]:
        """Les `n` entrées les plus récentes, de la plus ancienne à la plus récente."""
        if n < 0:
            raise ValueError(f"n = {n} : attendu >= 0")
        return list(self._entrees)[-n:] if n else []
