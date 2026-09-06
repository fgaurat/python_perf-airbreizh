"""Les règles, une par une, et surtout leurs bornes — hors d'atteinte avant le découpage.

Plusieurs tests figent un comportement documenté dans BUGS.md : ils disent ce
que le code FAIT, pas ce qu'il devrait faire.
"""

import pytest
from scolaire.modele import BONUS_MAX, Absences, ErreurBulletin, MoyenneMatiere, Periode
from scolaire.regles import (
    analyser_trimestre,
    appreciation,
    bonus_options,
    compter_absences,
    mention,
    moyenne_generale,
    moyenne_matiere,
    moyennes_par_matiere,
    rang,
    tendance,
    valider_eleve,
)

# --- analyser_trimestre ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("texte", "attendu"), [("2026-T1", Periode(2026, 1)), ("2000-T3", Periode(2000, 3))]
)
def test_analyser_trimestre(texte, attendu):
    assert analyser_trimestre(texte) == attendu


@pytest.mark.parametrize(
    "texte", ["2026-T4", "2026-T0", "2026-01", "26-T1", "2026T1", "AAAA-T1", "2026-TX", ""]
)
def test_trimestre_invalide(texte):
    with pytest.raises(ErreurBulletin, match="trimestre invalide"):
        analyser_trimestre(texte)


def test_annee_avant_2000():
    with pytest.raises(ErreurBulletin, match="annee invalide : 1999"):
        analyser_trimestre("1999-T1")


# --- valider_eleve --------------------------------------------------------------------


def test_la_classe_par_defaut_est_la_sixieme():
    assert valider_eleve({"id": "E1"}) == "6e"


@pytest.mark.parametrize("eleve", [{}, {"id": ""}, {"id": None}])
def test_identifiant_manquant(eleve):
    with pytest.raises(ErreurBulletin, match="identifiant manquant"):
        valider_eleve(eleve)


def test_classe_inconnue():
    with pytest.raises(ErreurBulletin, match="classe inconnue : CM2"):
        valider_eleve({"id": "E1", "classe": "CM2"})


# --- moyenne_matiere ------------------------------------------------------------------


def test_moyenne_simple():
    assert moyenne_matiere("maths", [{"valeur": 10}, {"valeur": 15}]) == MoyenneMatiere(
        "maths", 12.5, 2
    )


def test_les_coefficients_ponderent():
    assert moyenne_matiere("maths", [{"valeur": 10}, {"valeur": 16, "coef": 2}]).moyenne == 14.0


@pytest.mark.parametrize(
    ("valeur", "sur", "attendu"), [(9, 10, 18.0), (45, 50, 18.0), (18, 20, 18.0)]
)
def test_les_bareme_sont_ramenes_sur_vingt(valeur, sur, attendu):
    assert moyenne_matiere("x", [{"valeur": valeur, "sur": sur}]).moyenne == attendu


def test_une_note_absente_est_ignoree():
    assert moyenne_matiere("x", [{"valeur": None}, {"valeur": 12}]) == MoyenneMatiere("x", 12.0, 1)


def test_aucune_note_exploitable_donne_none():
    assert moyenne_matiere("x", []) is None
    assert moyenne_matiere("x", [{"valeur": None}]) is None


def test_la_moyenne_est_arrondie_au_centieme():
    assert moyenne_matiere("x", [{"valeur": 10}, {"valeur": 11}, {"valeur": 11}]).moyenne == 10.67


def test_note_negative():
    with pytest.raises(ErreurBulletin, match="note négative en maths"):
        moyenne_matiere("maths", [{"valeur": -1}])


@pytest.mark.parametrize("sur", [0, -10])
def test_bareme_invalide(sur):
    with pytest.raises(ErreurBulletin, match="barème invalide en maths"):
        moyenne_matiere("maths", [{"valeur": 5, "sur": sur}])


def test_une_note_au_dessus_du_bareme_est_acceptee():
    """BUGS.md n° 3 — figé : 25/20 donne une moyenne de 25."""
    assert moyenne_matiere("x", [{"valeur": 25}]).moyenne == 25.0


def test_moyennes_par_matiere_trie_et_filtre():
    notes = {"sport": [{"valeur": 18}], "arts": [], "maths": [{"valeur": 10}]}
    assert [m.matiere for m in moyennes_par_matiere(notes)] == ["maths", "sport"]


# --- moyenne_generale -----------------------------------------------------------------


def test_moyenne_generale_ponderee():
    assert moyenne_generale({"maths": 10.0, "sport": 20.0}) == pytest.approx(12.0)  # (40 + 20) / 5


def test_les_options_ne_comptent_pas_dans_la_moyenne_generale():
    assert moyenne_generale({"maths": 10.0, "latin": 20.0}) == 10.0


def test_une_matiere_inconnue_compte_coefficient_un():
    """BUGS.md n° 4 — figé : « math » (sans s) vaut 1 au lieu de 4."""
    assert moyenne_generale({"maths": 10.0, "math": 20.0}) == pytest.approx(12.0)


def test_aucune_matiere():
    with pytest.raises(ErreurBulletin, match="aucune note"):
        moyenne_generale({})


def test_seulement_des_options_est_une_erreur():
    with pytest.raises(ErreurBulletin, match="aucune note"):
        moyenne_generale({"latin": 15.0})


# --- bonus_options --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("moyennes", "attendu"),
    [
        ({}, 0.0),
        ({"latin": 10.0}, 0.0),
        ({"latin": 9.0}, 0.0),
        ({"latin": 15.0}, 0.5),
        ({"musique": 20.0}, 0.5),
        ({"latin": 20.0, "grec": 20.0}, 2.0),
        ({"latin": 20.0, "grec": 20.0, "musique": 20.0}, BONUS_MAX),
    ],
    ids=[
        "aucune",
        "exactement_dix",
        "sous_dix",
        "latin_15",
        "musique_20",
        "deux_options",
        "plafond",
    ],
)
def test_bonus_options(moyennes, attendu):
    assert bonus_options(moyennes) == pytest.approx(attendu)


# --- mention : les bornes -------------------------------------------------------------


@pytest.mark.parametrize(
    ("moyenne", "attendue"),
    [
        (16.01, "Félicitations"),
        (16.0, "Compliments"),
        (14.01, "Compliments"),
        (14.0, "Encouragements"),
        (12.01, "Encouragements"),
        (12.0, ""),
        (8.0, ""),
        (7.99, "Avertissement travail"),
        (0.0, "Avertissement travail"),
        (22.0, "Félicitations"),
    ],
)
def test_mention_aux_bornes(moyenne, attendue):
    """BUGS.md n° 2 — figé : 16 tout rond donne « Compliments » et non « Félicitations »."""
    assert mention(moyenne) == attendue


# --- rang -----------------------------------------------------------------------------


def test_rang_premier():
    assert rang(15.0, [12.0, 13.0]) == 1


def test_rang_dernier():
    assert rang(10.0, [12.0, 13.0]) == 3


def test_rang_seul():
    assert rang(10.0, []) == 1


def test_rang_ex_aequo():
    """BUGS.md n° 5 — figé : à égalité, l'élève est classé derrière son ex aequo."""
    assert rang(14.0, [14.0]) == 2


# --- absences -------------------------------------------------------------------------


@pytest.mark.parametrize(("nombre", "avertissement"), [(0, False), (10, False), (11, True)])
def test_compter_absences_seuil(nombre, avertissement):
    assert compter_absences(["2026-01-05"] * nombre) == Absences(nombre, avertissement)


def test_les_absences_justifiees_comptent():
    """BUGS.md n° 6 — figé : le drapeau `justifiee` est ignoré."""
    assert compter_absences([{"date": "2026-01-05", "justifiee": True}]).demi_journees == 1


# --- tendance et appréciation ---------------------------------------------------------


@pytest.mark.parametrize(
    ("finale", "precedente", "attendue"),
    [
        (13.5, 13.0, "en progrès"),
        (13.49, 13.0, "stable"),
        (12.5, 13.0, "en baisse"),
        (12.51, 13.0, "stable"),
    ],
)
def test_tendance_aux_bornes(finale, precedente, attendue):
    assert tendance(finale, precedente) == attendue


@pytest.mark.parametrize(
    ("la_mention", "assiduite", "attendu"),
    [
        ("Félicitations", False, "Excellent trimestre, stable."),
        ("Compliments", False, "Bon trimestre, stable. Continuez ainsi."),
        ("Encouragements", False, "Bon trimestre, stable. Continuez ainsi."),
        ("", False, "Trimestre correct, stable."),
        (
            "Avertissement travail",
            False,
            "Résultats insuffisants, stable. Un effort important est attendu.",
        ),
        ("", True, "Trimestre correct, stable. L'assiduité doit s'améliorer."),
    ],
)
def test_appreciation(la_mention, assiduite, attendu):
    assert appreciation(la_mention, "stable", assiduite) == attendu
