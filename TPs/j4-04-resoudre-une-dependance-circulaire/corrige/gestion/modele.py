"""Objets de valeur, constantes et exceptions. N'importe rien du projet."""

from dataclasses import dataclass
from datetime import date

DELAI_ALERTE_JOURS = 3


class ErreurGestion(Exception):
    """Racine des erreurs du package."""


class ProjetInconnu(ErreurGestion):
    """Aucun projet ne porte ce nom."""


@dataclass(frozen=True)
class Projet:
    nom: str
    archive: bool = False


@dataclass(frozen=True)
class Tache:
    id: int
    titre: str
    projet: str
    echeance: date
    terminee: bool = False

    def est_en_retard(self, jour: date) -> bool:
        return not self.terminee and self.echeance < jour

    def est_a_surveiller(self, jour: date, delai: int = DELAI_ALERTE_JOURS) -> bool:
        """Non terminée et due dans moins de `delai` jours (ou déjà passée)."""
        return not self.terminee and (self.echeance - jour).days < delai
