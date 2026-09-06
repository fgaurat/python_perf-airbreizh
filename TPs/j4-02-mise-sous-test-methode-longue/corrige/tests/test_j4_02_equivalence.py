"""Équivalence entre l'ancienne implémentation et la nouvelle.

C'est le filet de sécurité du refactoring : les deux versions cohabitent le
temps de la transformation, et ce test compare leurs sorties sur un large
échantillon. Il sera supprimé quand `bulletin_v1.py` le sera.
"""

import itertools

import pytest
from fabrique_j4_02 import eleve
from scolaire.bulletin import generer_bulletin
from scolaire.bulletin_v1 import generer_bulletin as generer_bulletin_v1

CLASSES = ["6e", "5e", "4e", "3e"]
PRECEDENTES = [5.0, 11.9, 13.0, 13.4, 16.0, 19.5]
NOTES = [
    {"maths": [{"valeur": 20}]},  # une seule matière
    {"maths": [{"valeur": 4}], "francais": [{"valeur": 6}]},  # avertissement
    eleve()["notes"],  # le jeu de référence
    {**eleve()["notes"], "latin": [{"valeur": 17}], "grec": [{"valeur": 19}]},  # options
    {"maths": [{"valeur": 9, "sur": 10, "coef": 3}, {"valeur": 45, "sur": 50}]},  # barèmes
    {**eleve()["notes"], "math": [{"valeur": 2}], "arts": [{"valeur": None}]},  # typo, note absente
]


@pytest.mark.parametrize(
    ("classe", "precedente", "notes"),
    list(itertools.product(CLASSES, PRECEDENTES, NOTES)),
)
def test_les_deux_versions_donnent_le_meme_bulletin(classe, precedente, notes):
    """144 combinaisons — bien plus que ce qu'on écrirait à la main."""
    donnees = eleve(classe=classe, moyenne_precedente=precedente, notes=notes)
    assert generer_bulletin(dict(donnees), "2026-T2") == generer_bulletin_v1(
        dict(donnees), "2026-T2"
    )


@pytest.mark.parametrize(
    "absences",
    [
        [],
        ["2026-01-05"],
        ["2026-01-05"] * 10,
        ["2026-01-05"] * 11,
        [{"date": "2026-01-05", "justifiee": True}] * 11,
    ],
)
def test_equivalence_sur_les_absences(absences):
    donnees = eleve(absences=absences)
    assert generer_bulletin(dict(donnees), "2026-T1") == generer_bulletin_v1(
        dict(donnees), "2026-T1"
    )


@pytest.mark.parametrize("autres", [[], [13.0], [14.05], [14.05, 14.05], [20.0, 0.0]])
def test_equivalence_sur_le_rang(autres):
    donnees = eleve(moyennes_classe=autres)
    assert generer_bulletin(dict(donnees), "2026-T3") == generer_bulletin_v1(
        dict(donnees), "2026-T3"
    )


def test_equivalence_sans_moyenne_precedente():
    """Inclut le bug n° 1 : l'absence de moyenne précédente vaut 0 dans les deux versions."""
    donnees = eleve()
    del donnees["moyenne_precedente"]
    assert generer_bulletin(dict(donnees), "2026-T1") == generer_bulletin_v1(
        dict(donnees), "2026-T1"
    )


@pytest.mark.parametrize(
    ("donnees", "trimestre"),
    [
        (eleve(id=""), "2026-T1"),
        (eleve(classe="CM2"), "2026-T1"),
        (eleve(), "2026-T4"),
        (eleve(), "2026-01"),
        (eleve(), "1999-T1"),
        (eleve(notes={}), "2026-T1"),
        (eleve(notes={"maths": [{"valeur": -1}]}), "2026-T1"),
        (eleve(notes={"maths": [{"valeur": 10, "sur": 0}]}), "2026-T1"),
    ],
)
def test_equivalence_sur_les_erreurs(donnees, trimestre):
    with pytest.raises(ValueError) as v1:
        generer_bulletin_v1(dict(donnees), trimestre)
    with pytest.raises(ValueError) as v2:
        generer_bulletin(dict(donnees), trimestre)
    assert str(v1.value) == str(v2.value)
