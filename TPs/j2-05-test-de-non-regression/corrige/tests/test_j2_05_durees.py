"""Tests du module de durées.

Les huit tests de départ sont conservés **à l'identique** (première section).
Tout ce qui suit a été ajouté à partir du ticket #2291.
"""

import pytest
from temps.durees import DureeInvalide, DureeNegative, analyser, formater, total

# --- Les huit tests d'origine, inchangés -------------------------------------------------


def test_zero():
    assert formater(0) == "0 s"


def test_secondes():
    assert formater(5) == "5 s"


def test_minutes_et_secondes():
    assert formater(65) == "1 min 05 s"


def test_une_heure():
    assert formater(3600) == "1 h"


def test_heures_minutes_secondes():
    assert formater(3725) == "1 h 02 min 05 s"


def test_presque_un_jour():
    assert formater(86399) == "23 h 59 min 59 s"


def test_analyser():
    assert analyser("1 h 02 min 05 s") == 3725


def test_total():
    assert total(["1 h", "30 min", "45 s"]) == "1 h 30 min 45 s"


# --- 1. Le test de non-régression ------------------------------------------------------------


def test_26_heures_ne_deviennent_pas_2_heures():
    """Bug #2291 — `time.gmtime` repassait à zéro toutes les 24 h."""
    assert formater(94500) == "26 h 15 min"


def test_le_symptome_exact_du_ticket():
    """Bug #2291 — le tableau de bord affichait « 2 h 15 min » pour le job `consolidation`."""
    assert formater(94500) != "2 h 15 min"


# --- 2. La famille du bug : tout ce qui dépasse 24 h --------------------------------------------


@pytest.mark.parametrize(
    ("secondes", "attendu"),
    [
        pytest.param(86400, "24 h", id="exactement_un_jour"),
        pytest.param(86401, "24 h 01 s", id="un_jour_et_une_seconde"),
        pytest.param(90000, "25 h", id="l_exemple_de_la_docstring"),
        pytest.param(172800, "48 h", id="deux_jours"),
        pytest.param(360000, "100 h", id="trois_chiffres"),
        pytest.param(604800, "168 h", id="une_semaine"),
        pytest.param(31536000, "8760 h", id="une_annee"),
    ],
)
def test_les_heures_ne_sont_pas_bornees(secondes, attendu):
    assert formater(secondes) == attendu


@pytest.mark.parametrize("secondes", [0, 59, 60, 3599, 3600, 86399, 86400, 90061, 1_000_000])
def test_aller_retour(secondes):
    """La propriété qui aurait attrapé le bug : `analyser(formater(n)) == n` pour tout n."""
    assert analyser(formater(secondes)) == secondes


@pytest.mark.parametrize(
    ("textes", "attendu"),
    [
        pytest.param(["12 h", "12 h"], "24 h", id="la_somme_franchit_24_h"),
        pytest.param(["23 h 59 min 59 s", "1 s"], "24 h", id="a_la_seconde_pres"),
        pytest.param(["100 h", "100 h"], "200 h", id="grands_totaux"),
    ],
)
def test_total_au_dela_d_un_jour(textes, attendu):
    assert total(textes) == attendu


# --- 3. Le bug qu'on découvre en élargissant -----------------------------------------------------


@pytest.mark.parametrize("secondes", [-1, -5, -86400], ids=["-1", "-5", "-1_jour"])
def test_une_duree_negative_est_refusee(secondes):
    """Le code de départ renvoyait « 23 h 59 min 59 s » pour -1 : gmtime remontait au 31/12/1969."""
    with pytest.raises(DureeNegative, match=f"{secondes} s"):
        formater(secondes)


# --- 4. Le format, cas par cas ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("secondes", "attendu"),
    [
        pytest.param(59, "59 s", id="derniere_seconde"),
        pytest.param(60, "1 min", id="minute_ronde"),
        pytest.param(600, "10 min", id="dix_minutes"),
        pytest.param(3605, "1 h 05 s", id="minutes_nulles_omises"),
        pytest.param(3660, "1 h 01 min", id="secondes_nulles_omises"),
        pytest.param(36000, "10 h", id="dix_heures"),
    ],
)
def test_les_unites_nulles_sont_omises(secondes, attendu):
    assert formater(secondes) == attendu


def test_la_premiere_unite_n_a_pas_de_zero_initial():
    assert formater(65).startswith("1 min")
    assert formater(3725).startswith("1 h")


def test_les_unites_suivantes_sont_sur_deux_chiffres():
    assert formater(3725) == "1 h 02 min 05 s"
    assert formater(7200 + 60 * 9 + 9) == "2 h 09 min 09 s"


# --- 5. analyser ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        ("0 s", 0),
        ("45 s", 45),
        ("1 min", 60),
        ("1 min 05 s", 65),
        ("1 h", 3600),
        ("26 h 15 min", 94500),
        ("  1 h   02 min  05 s  ", 3725),
        ("100 h", 360000),
    ],
)
def test_analyser_accepte_toutes_les_formes_produites(texte, attendu):
    assert analyser(texte) == attendu


@pytest.mark.parametrize(
    "texte",
    ["", "   ", "1h", "1 heure", "5 s 1 min", "1 h 2 min 3", "-1 h", "1 h 60 minutes"],
    ids=[
        "vide",
        "blancs",
        "sans_espace",
        "unite_longue",
        "desordre",
        "sans_unite",
        "negatif",
        "minutes",
    ],
)
def test_analyser_refuse_les_formes_inconnues(texte):
    with pytest.raises(DureeInvalide, match="durée illisible"):
        analyser(texte)
