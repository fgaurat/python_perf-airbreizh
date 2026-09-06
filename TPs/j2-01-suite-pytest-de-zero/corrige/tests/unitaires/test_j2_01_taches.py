"""Tests de la liste de tâches.

Lisez la sortie de `pytest --collect-only -q` : la liste des noms doit se lire
comme la spécification du module.
"""

import pytest
from todolist.taches import (
    TITRE_MAX,
    ErreurTodo,
    Priorite,
    Tache,
    TacheDejaTerminee,
    TacheIntrouvable,
    TitreInvalide,
    TodoList,
    normaliser_titre,
)

# --- Le cas nominal -------------------------------------------------------------


def test_ajouter_retourne_la_tache_creee():
    liste = TodoList()
    assert liste.ajouter("Relire le rapport") == Tache(1, "Relire le rapport")


def test_les_identifiants_sont_croissants():
    liste = TodoList()
    assert [liste.ajouter(t).id for t in ["A", "B", "C"]] == [1, 2, 3]


def test_les_identifiants_ne_sont_jamais_reutilises():
    liste = TodoList()
    liste.ajouter("A")
    liste.terminer(1)
    assert liste.ajouter("B").id == 2


def test_la_priorite_par_defaut_est_normale():
    assert TodoList().ajouter("A").priorite is Priorite.NORMALE


def test_len_compte_toutes_les_taches_terminees_ou_non(liste_garnie):
    liste_garnie.terminer(1)
    assert len(liste_garnie) == 3


# --- La normalisation des titres -------------------------------------------------


@pytest.mark.parametrize(
    ("saisi", "attendu"),
    [
        pytest.param("  Relire le rapport  ", "Relire le rapport", id="espaces_autour"),
        pytest.param("Relire   le\trapport", "Relire le rapport", id="espaces_internes"),
        pytest.param("relire le rapport", "Relire le rapport", id="premiere_lettre"),
        pytest.param("relire le RAPPORT", "Relire le RAPPORT", id="le_reste_est_conserve"),
        pytest.param("  relire   le rapport ", "Relire le rapport", id="les_trois_a_la_fois"),
    ],
)
def test_normaliser_titre(saisi, attendu):
    assert normaliser_titre(saisi) == attendu


def test_normaliser_est_idempotent():
    une_fois = normaliser_titre("  relire   le rapport ")
    assert normaliser_titre(une_fois) == une_fois


def test_un_titre_a_la_longueur_maximale_est_accepte():
    assert len(normaliser_titre("a" * TITRE_MAX)) == TITRE_MAX


def test_ajouter_normalise_le_titre():
    assert TodoList().ajouter("  relire   le rapport ").titre == "Relire le rapport"


def test_toutes_les_donnees_de_reference_sont_acceptees(titres_valides):
    liste = TodoList()
    for titre in titres_valides:
        assert liste.ajouter(titre).titre == titre


# --- L'ordre ------------------------------------------------------------------------


def test_lister_met_la_priorite_haute_en_premier(liste_garnie):
    assert [t.priorite for t in liste_garnie.lister()] == [
        Priorite.HAUTE,
        Priorite.NORMALE,
        Priorite.BASSE,
    ]


def test_a_priorite_egale_lister_respecte_l_ordre_d_ajout():
    liste = TodoList()
    for titre in ["C", "A", "B"]:
        liste.ajouter(titre)
    assert [t.titre for t in liste.lister()] == ["C", "A", "B"]


def test_lister_une_liste_vide():
    assert TodoList().lister() == []


# --- Terminer -----------------------------------------------------------------------


def test_terminer_retourne_la_tache_mise_a_jour(liste_garnie):
    tache = liste_garnie.terminer(2)
    assert tache.terminee is True
    assert tache.titre == "Relire le rapport"


def test_terminer_ne_modifie_pas_l_objet_d_origine():
    liste = TodoList()
    avant = liste.ajouter("A")
    liste.terminer(1)
    assert avant.terminee is False


def test_terminer_est_visible_dans_lister(liste_garnie):
    liste_garnie.terminer(2)
    assert [t.terminee for t in liste_garnie.lister()] == [True, False, False]


# --- Filtrer ------------------------------------------------------------------------


def test_filtrer_sans_critere_equivaut_a_lister(liste_garnie):
    assert liste_garnie.filtrer() == liste_garnie.lister()


def test_filtrer_les_taches_restantes(liste_garnie):
    liste_garnie.terminer(2)
    assert [t.id for t in liste_garnie.filtrer(terminee=False)] == [3, 1]


def test_filtrer_les_taches_terminees(liste_garnie):
    liste_garnie.terminer(2)
    assert [t.id for t in liste_garnie.filtrer(terminee=True)] == [2]


@pytest.mark.parametrize(
    ("priorite", "ids"),
    [(Priorite.HAUTE, [2]), (Priorite.NORMALE, [3]), (Priorite.BASSE, [1])],
    ids=["haute", "normale", "basse"],
)
def test_filtrer_par_priorite(liste_garnie, priorite, ids):
    assert [t.id for t in liste_garnie.filtrer(priorite=priorite)] == ids


def test_filtrer_combine_les_criteres(liste_garnie):
    liste_garnie.terminer(2)
    assert liste_garnie.filtrer(terminee=False, priorite=Priorite.HAUTE) == []


# --- Les erreurs attendues ----------------------------------------------------------


@pytest.mark.parametrize("titre", ["", "   ", "\t\n"], ids=["vide", "espaces", "blancs"])
def test_un_titre_vide_est_refuse(titre):
    with pytest.raises(TitreInvalide, match="titre vide"):
        normaliser_titre(titre)


def test_un_titre_trop_long_est_refuse_avec_les_deux_longueurs():
    with pytest.raises(TitreInvalide, match=r"81 caractères \(maximum 80\)"):
        normaliser_titre("a" * (TITRE_MAX + 1))


def test_terminer_une_tache_inconnue():
    with pytest.raises(TacheIntrouvable, match="aucune tâche n°42"):
        TodoList().terminer(42)


def test_terminer_deux_fois_la_meme_tache(liste_garnie):
    liste_garnie.terminer(1)
    with pytest.raises(TacheDejaTerminee, match="n°1 est déjà terminée"):
        liste_garnie.terminer(1)


def test_un_titre_invalide_n_ajoute_rien():
    liste = TodoList()
    with pytest.raises(TitreInvalide):
        liste.ajouter("   ")
    assert len(liste) == 0


def test_toutes_les_erreurs_derivent_d_une_racine_commune():
    for exc in (TitreInvalide, TacheIntrouvable, TacheDejaTerminee):
        assert issubclass(exc, ErreurTodo)


# --- Pour aller plus loin -----------------------------------------------------------


def test_la_longueur_est_verifiee_apres_normalisation():
    """Comportement actuel : 121 caractères saisis, 79 après normalisation → accepté."""
    saisi = "  " + "   ".join("mot" for _ in range(20)) + "  "
    assert len(saisi) == 121
    assert len(normaliser_titre(saisi)) == 79
