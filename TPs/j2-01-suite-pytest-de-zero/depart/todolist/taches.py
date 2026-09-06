"""Liste de tâches partagée : ajout, clôture, tri et filtrage.

Utilisé par la ligne de commande `todo`, le widget du tableau de bord et
l'export hebdomadaire.

Règles de saisie d'un titre (voir `normaliser_titre`) :

- les espaces en début et fin sont ignorés ;
- les espaces internes multiples sont réduits à un seul ;
- la première lettre est mise en majuscule, le reste est conservé tel quel.

Un titre est refusé s'il est vide après normalisation ou s'il dépasse
`TITRE_MAX` caractères.
"""

from dataclasses import dataclass, replace
from enum import Enum

TITRE_MAX = 80


class ErreurTodo(Exception):
    """Racine des erreurs du module."""


class TitreInvalide(ErreurTodo):
    """Titre vide ou trop long."""


class TacheIntrouvable(ErreurTodo):
    """Aucune tâche ne porte cet identifiant."""


class TacheDejaTerminee(ErreurTodo):
    """On ne termine pas deux fois la même tâche."""


class Priorite(Enum):
    BASSE = 1
    NORMALE = 2
    HAUTE = 3


@dataclass(frozen=True)
class Tache:
    id: int
    titre: str
    priorite: Priorite = Priorite.NORMALE
    terminee: bool = False


def normaliser_titre(titre: str) -> str:
    """Applique les trois tolérances de saisie, puis valide la longueur.

    >>> normaliser_titre("  relire   le rapport ")
    'Relire le rapport'
    """
    propre = " ".join(titre.split())
    if not propre:
        raise TitreInvalide("titre vide")
    if len(propre) > TITRE_MAX:
        raise TitreInvalide(f"titre trop long : {len(propre)} caractères (maximum {TITRE_MAX})")
    return propre[0].upper() + propre[1:]


class TodoList:
    """Une liste de tâches en mémoire, aux identifiants croissants et jamais réutilisés."""

    def __init__(self) -> None:
        self._taches: dict[int, Tache] = {}
        self._prochain_id = 1

    def __len__(self) -> int:
        return len(self._taches)

    def ajouter(self, titre: str, priorite: Priorite = Priorite.NORMALE) -> Tache:
        tache = Tache(self._prochain_id, normaliser_titre(titre), priorite)
        self._taches[tache.id] = tache
        self._prochain_id += 1
        return tache

    def terminer(self, identifiant: int) -> Tache:
        if identifiant not in self._taches:
            raise TacheIntrouvable(f"aucune tâche n°{identifiant}")
        tache = self._taches[identifiant]
        if tache.terminee:
            raise TacheDejaTerminee(f"la tâche n°{identifiant} est déjà terminée")
        self._taches[identifiant] = replace(tache, terminee=True)
        return self._taches[identifiant]

    def lister(self) -> list[Tache]:
        """Toutes les tâches, priorité haute d'abord, puis par ordre d'ajout."""
        return sorted(self._taches.values(), key=lambda t: (-t.priorite.value, t.id))

    def filtrer(
        self, *, terminee: bool | None = None, priorite: Priorite | None = None
    ) -> list[Tache]:
        """Sous-ensemble de `lister()` ; un critère à `None` n'est pas appliqué."""
        return [
            t
            for t in self.lister()
            if (terminee is None or t.terminee == terminee)
            and (priorite is None or t.priorite == priorite)
        ]
