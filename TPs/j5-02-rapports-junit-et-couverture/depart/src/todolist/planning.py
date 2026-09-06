"""Score et tri des tâches.

Quatre règles, ajoutées au fil des versions. Trois sont testées.
"""

from dataclasses import dataclass
from datetime import date

POIDS_PRIORITE = [("haute", 3), ("normale", 2), ("basse", 1)]
BONUS_ETIQUETTE = {"URGENT": 3, "CLIENT": 2, "INTERNE": 0}
BONUS_RETARD_PAR_JOUR = 1
SCORE_MAX = 10


class ErreurPlanning(Exception):
    """Racine des erreurs du module."""


class PrioriteInvalide(ErreurPlanning):
    pass


class EtiquetteInconnue(ErreurPlanning):
    pass


@dataclass(frozen=True)
class Tache:
    id: int
    titre: str
    echeance: date
    priorite: str = "normale"
    etiquette: str | None = None

    def __post_init__(self) -> None:
        if self.priorite not in dict(POIDS_PRIORITE):
            raise PrioriteInvalide(f"priorité inconnue : {self.priorite!r}")


def poids_priorite(priorite: str) -> int:
    """Poids d'une priorité : haute 3, normale 2, basse 1."""
    for nom, poids in POIDS_PRIORITE:
        if priorite == nom:
            return poids
    return 0


def retard(tache: Tache, jour: date) -> int:
    """Jours de retard, jamais négatif."""
    return max(0, (jour - tache.echeance).days)


def bonus_etiquette(etiquette: str) -> int:
    """Bonus d'une étiquette, insensible à la casse.

    Raises:
        EtiquetteInconnue: l'étiquette n'existe pas.
    """
    try:
        return BONUS_ETIQUETTE[etiquette.upper()]
    except KeyError:
        raise EtiquetteInconnue(f"{etiquette!r} — connues : {sorted(BONUS_ETIQUETTE)}") from None


def score(tache: Tache, jour: date) -> int:
    """Score d'une tâche : priorité + étiquette + un point par jour de retard, plafonné à 10."""
    points = poids_priorite(tache.priorite)
    if tache.etiquette is not None:
        points = bonus_etiquette(tache.etiquette)
    points += retard(tache, jour) * BONUS_RETARD_PAR_JOUR
    return min(points, SCORE_MAX)


def trier(taches: list[Tache], jour: date) -> list[Tache]:
    """Du score le plus élevé au plus faible ; à égalité, la plus ancienne échéance d'abord."""
    return sorted(taches, key=lambda t: (-score(t, jour), t.echeance, t.id))


def resume(taches: list[Tache], jour: date) -> list[str]:
    """Une ligne par tâche, dans l'ordre du tri : score, titre, retard éventuel."""
    lignes = []
    for tache in trier(taches, jour):
        jours = retard(tache, jour)
        suffixe = f" (retard {jours} j)" if jours else ""
        lignes.append(f"[{score(tache, jour):2d}] {tache.titre}{suffixe}")
    return lignes
