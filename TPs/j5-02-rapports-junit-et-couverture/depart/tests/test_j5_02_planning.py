"""Tests existants du planning.

Ils passent tous. La couverture est incomplète — c'est le sujet du TP.
"""

from datetime import date

import pytest

from todolist.planning import PrioriteInvalide, Tache, poids_priorite, retard, score, trier

JOUR = date(2026, 9, 15)


@pytest.mark.parametrize(("priorite", "attendu"), [("haute", 3), ("normale", 2), ("basse", 1)])
def test_poids_priorite(priorite, attendu):
    assert poids_priorite(priorite) == attendu


def test_priorite_invalide():
    with pytest.raises(PrioriteInvalide):
        Tache(1, "X", JOUR, priorite="critique")


def test_retard():
    assert retard(Tache(1, "X", date(2026, 9, 10)), JOUR) == 5


def test_pas_de_retard_avant_l_echeance():
    assert retard(Tache(1, "X", date(2026, 9, 20)), JOUR) == 0


def test_score_sans_etiquette():
    assert score(Tache(1, "X", date(2026, 9, 13), priorite="haute"), JOUR) == 5


def test_trier():
    taches = [
        Tache(1, "Basse", date(2026, 9, 20), priorite="basse"),
        Tache(2, "Haute", date(2026, 9, 20), priorite="haute"),
        Tache(3, "En retard", date(2026, 9, 10), priorite="basse"),
    ]
    assert [t.id for t in trier(taches, JOUR)] == [3, 2, 1]
