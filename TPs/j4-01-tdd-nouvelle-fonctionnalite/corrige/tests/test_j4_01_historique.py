"""Tests du bourgeon, dans l'ordre des cycles TDD. Aucun n'a besoin du moteur."""

import pytest
from bureau.historique import CAPACITE_DEFAUT, Entree, Historique, HistoriqueVide

# --- Cycle 1 — enregistrer puis relire ---------------------------------------------------


def test_enregistrer_retourne_l_entree():
    assert Historique().enregistrer("2 + 2", 4.0) == Entree("2 + 2", 4.0)


def test_derniers_rend_les_entrees_de_la_plus_ancienne_a_la_plus_recente():
    h = Historique()
    h.enregistrer("1 + 1", 2.0)
    h.enregistrer("2 + 2", 4.0)
    assert h.derniers() == [Entree("1 + 1", 2.0), Entree("2 + 2", 4.0)]


def test_un_historique_neuf_est_vide():
    h = Historique()
    assert len(h) == 0
    assert h.derniers() == []
    assert h.courant is None


# --- Cycle 2 — la capacité ----------------------------------------------------------------
# Décision : « les 10 derniers » = capacité 10, la 11e entrée évince la plus ancienne.


def test_la_capacite_par_defaut_est_dix():
    assert Historique().capacite == CAPACITE_DEFAUT == 10


def test_la_onzieme_entree_evince_la_plus_ancienne():
    h = Historique(capacite=10)
    for i in range(11):
        h.enregistrer(str(i), float(i))
    assert len(h) == 10
    assert h.derniers()[0] == Entree("1", 1.0)


def test_a_capacite_exacte_rien_n_est_evince():
    h = Historique(capacite=3)
    for i in range(3):
        h.enregistrer(str(i), float(i))
    assert [e.expression for e in h.derniers()] == ["0", "1", "2"]


@pytest.mark.parametrize("capacite", [0, -1])
def test_une_capacite_nulle_ou_negative_est_refusee(capacite):
    with pytest.raises(ValueError, match=f"capacite = {capacite}"):
        Historique(capacite=capacite)


# --- Cycle 3 — annuler ----------------------------------------------------------------------
# Décision : annuler à vide est une erreur, pas un None silencieux.


def test_annuler_retire_et_retourne_la_derniere_entree():
    h = Historique()
    h.enregistrer("1 + 1", 2.0)
    h.enregistrer("2 + 2", 4.0)
    assert h.annuler() == Entree("2 + 2", 4.0)
    assert h.courant == Entree("1 + 1", 2.0)


def test_annuler_jusqu_a_vide():
    h = Historique()
    h.enregistrer("1 + 1", 2.0)
    h.annuler()
    assert h.courant is None
    assert len(h) == 0


def test_annuler_a_vide_est_une_erreur():
    with pytest.raises(HistoriqueVide, match="rien à annuler"):
        Historique().annuler()


# --- Cycle 4 — rétablir ---------------------------------------------------------------------
# Décision : undo/redo classique — un nouveau calcul efface ce qui pouvait être rétabli.


def test_retablir_remet_la_derniere_entree_annulee():
    h = Historique()
    h.enregistrer("2 + 2", 4.0)
    h.annuler()
    assert h.retablir() == Entree("2 + 2", 4.0)
    assert h.courant == Entree("2 + 2", 4.0)


def test_annuler_deux_fois_puis_retablir_deux_fois_conserve_l_ordre():
    h = Historique()
    h.enregistrer("a", 1.0)
    h.enregistrer("b", 2.0)
    h.annuler()
    h.annuler()
    h.retablir()
    h.retablir()
    assert [e.expression for e in h.derniers()] == ["a", "b"]


def test_retablir_sans_annulation_prealable_est_une_erreur():
    h = Historique()
    h.enregistrer("2 + 2", 4.0)
    with pytest.raises(HistoriqueVide, match="rien à rétablir"):
        h.retablir()


def test_un_nouveau_calcul_apres_annulation_efface_le_retablissement():
    h = Historique()
    h.enregistrer("a", 1.0)
    h.annuler()
    h.enregistrer("b", 2.0)
    with pytest.raises(HistoriqueVide):
        h.retablir()


# --- Cycle 5 — derniers(n) ----------------------------------------------------------------------


def test_derniers_n_limite_le_nombre():
    h = Historique()
    for i in range(5):
        h.enregistrer(str(i), float(i))
    assert [e.expression for e in h.derniers(2)] == ["3", "4"]


def test_derniers_n_plus_grand_que_l_historique():
    h = Historique()
    h.enregistrer("a", 1.0)
    assert len(h.derniers(100)) == 1


def test_derniers_zero():
    h = Historique()
    h.enregistrer("a", 1.0)
    assert h.derniers(0) == []


def test_derniers_negatif_est_une_erreur():
    with pytest.raises(ValueError, match="n = -1"):
        Historique().derniers(-1)


def test_derniers_rend_une_copie():
    h = Historique()
    h.enregistrer("a", 1.0)
    h.derniers().clear()
    assert len(h) == 1
