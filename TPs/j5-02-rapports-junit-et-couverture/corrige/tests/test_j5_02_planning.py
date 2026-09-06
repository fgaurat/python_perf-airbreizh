"""Tests du planning — les six d'origine, puis ceux écrits en suivant la colonne « Missing »."""

from datetime import date

import pytest

from todolist.planning import (
    SCORE_MAX,
    EtiquetteInconnue,
    PrioriteInvalide,
    Tache,
    bonus_etiquette,
    poids_priorite,
    resume,
    retard,
    score,
    trier,
)

JOUR = date(2026, 9, 15)

# --- Les six tests d'origine, inchangés -----------------------------------------------


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


# --- Lignes « bonus_etiquette » : quatre tests ----------------------------------------


@pytest.mark.parametrize(("etiquette", "attendu"), [("URGENT", 3), ("CLIENT", 2), ("INTERNE", 0)])
def test_bonus_etiquette(etiquette, attendu):
    assert bonus_etiquette(etiquette) == attendu


def test_bonus_etiquette_ignore_la_casse():
    assert bonus_etiquette("urgent") == bonus_etiquette("Urgent") == 3


def test_etiquette_inconnue_liste_les_etiquettes():
    with pytest.raises(
        EtiquetteInconnue, match=r"'vip' — connues : \['CLIENT', 'INTERNE', 'URGENT'\]"
    ):
        bonus_etiquette("vip")


# --- Ligne « points += bonus » : le test qui a révélé le bug --------------------------


def test_l_etiquette_s_ajoute_a_la_priorite():
    """Bug trouvé en écrivant ce test : « = » au lieu de « += ».

    Une tâche haute (3) étiquetée client (2) scorait 2 : l'étiquette écrasait la
    priorité. Les tâches urgentes des clients passaient derrière les tâches
    internes basses en retard d'un jour.
    """
    assert score(Tache(1, "X", JOUR, priorite="haute", etiquette="client"), JOUR) == 5


@pytest.mark.parametrize(
    ("priorite", "etiquette", "retard_jours", "attendu"),
    [
        ("basse", None, 0, 1),
        ("basse", "interne", 0, 1),
        ("normale", "client", 0, 4),
        ("haute", "urgent", 0, 6),
        ("basse", "urgent", 2, 6),
        ("haute", "client", 3, 8),
    ],
)
def test_score_cumule_les_trois_sources(priorite, etiquette, retard_jours, attendu):
    echeance = date(2026, 9, 15 - retard_jours)
    assert score(Tache(1, "X", echeance, priorite=priorite, etiquette=etiquette), JOUR) == attendu


# --- Ligne « min(points, SCORE_MAX) » : le plafond ------------------------------------


def test_le_score_est_plafonne():
    tache = Tache(1, "X", date(2026, 9, 1), priorite="haute", etiquette="urgent")  # 3 + 3 + 14
    assert score(tache, JOUR) == SCORE_MAX == 10


def test_exactement_au_plafond():
    tache = Tache(1, "X", date(2026, 9, 11), priorite="haute", etiquette="urgent")  # 3 + 3 + 4
    assert score(tache, JOUR) == 10


# --- Le tri, aux bornes ---------------------------------------------------------------


def test_trier_a_score_egal_par_echeance_puis_id():
    taches = [
        Tache(3, "C", date(2026, 9, 20)),
        Tache(1, "A", date(2026, 9, 20)),
        Tache(2, "B", date(2026, 9, 18)),
    ]
    assert [t.id for t in trier(taches, JOUR)] == [2, 1, 3]


def test_trier_liste_vide():
    assert trier([], JOUR) == []


def test_trier_ne_modifie_pas_la_liste():
    taches = [Tache(1, "A", date(2026, 9, 20)), Tache(2, "B", date(2026, 9, 10))]
    trier(taches, JOUR)
    assert [t.id for t in taches] == [1, 2]


# --- resume ---------------------------------------------------------------------------


def test_resume():
    taches = [
        Tache(1, "Ranger", date(2026, 9, 20), priorite="basse"),
        Tache(2, "Livrer", date(2026, 9, 12), priorite="haute", etiquette="client"),
    ]
    assert resume(taches, JOUR) == ["[ 8] Livrer (retard 3 j)", "[ 1] Ranger"]


def test_resume_vide():
    assert resume([], JOUR) == []


# --- retard, aux bornes ---------------------------------------------------------------


def test_retard_le_jour_meme():
    assert retard(Tache(1, "X", JOUR), JOUR) == 0


def test_retard_d_un_jour():
    assert retard(Tache(1, "X", date(2026, 9, 14)), JOUR) == 1
