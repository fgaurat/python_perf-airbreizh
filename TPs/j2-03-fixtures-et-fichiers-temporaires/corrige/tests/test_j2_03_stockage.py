"""Tests du carnet d'adresses.

Chaque test reçoit son propre `tmp_path`. La suite passe dans n'importe quel
ordre, deux fois de suite, et ne laisse aucun fichier derrière elle.
"""

from pathlib import Path

import pytest
from carnet.stockage import (
    Contact,
    ContactExistant,
    FichierCorrompu,
    ajouter,
    ecrire,
    lire,
    purger_sauvegardes,
    sauvegarder,
    sauvegardes,
)

# --- 1. Écrire puis lire -------------------------------------------------------------


def test_ecrire_puis_lire(tmp_path: Path):
    chemin = tmp_path / "carnet.json"
    contacts = [Contact("Ada Lovelace", "ada@exemple.org")]
    ecrire(chemin, contacts)
    assert lire(chemin) == contacts


def test_ecrire_puis_lire_avec_les_fixtures(carnet_rempli, contacts):
    assert lire(carnet_rempli) == contacts


def test_ecrire_remplace_le_contenu(carnet_rempli):
    ecrire(carnet_rempli, [Contact("Seule", "seule@exemple.org")])
    assert [c.nom for c in lire(carnet_rempli)] == ["Seule"]


def test_le_fichier_est_lisible_par_un_humain(carnet_rempli):
    texte = carnet_rempli.read_text(encoding="utf-8")
    assert '"nom": "Ada Lovelace"' in texte
    assert "\\u" not in texte  # ensure_ascii=False : les accents restent lisibles


# --- 2. Les cas limites de lecture -------------------------------------------------------


def test_lire_un_fichier_absent_donne_un_carnet_vide(carnet):
    assert not carnet.exists()
    assert lire(carnet) == []


def test_lire_un_fichier_vide_donne_un_carnet_vide(carnet):
    carnet.write_text("")
    assert lire(carnet) == []


def test_lire_une_liste_vide(carnet):
    ecrire(carnet, [])
    assert lire(carnet) == []


def test_un_json_invalide_indique_la_ligne(carnet):
    carnet.write_text('[\n  {"nom": "Ada", "email": "ada@exemple.org"},\n  {"nom" "Alan"}\n]')
    with pytest.raises(FichierCorrompu, match="carnet.json ligne 3"):
        lire(carnet)


def test_un_json_qui_n_est_pas_une_liste(carnet):
    carnet.write_text('{"nom": "Ada", "email": "ada@exemple.org"}')
    with pytest.raises(FichierCorrompu, match="attendu une liste, trouvé dict"):
        lire(carnet)


def test_un_contact_sans_email_indique_sa_position(carnet):
    carnet.write_text('[{"nom": "Ada", "email": "ada@exemple.org"}, {"nom": "Alan"}]')
    with pytest.raises(FichierCorrompu, match="contact 2 : .*email"):
        lire(carnet)


def test_un_contact_avec_une_cle_inconnue(carnet):
    carnet.write_text('[{"nom": "Ada", "email": "ada@exemple.org", "age": 36}]')
    with pytest.raises(FichierCorrompu, match="contact 1 : .*age"):
        lire(carnet)


# --- 3. Ajouter ----------------------------------------------------------------------------


def test_ajouter_dans_un_carnet_inexistant_le_cree(carnet):
    ajouter(carnet, Contact("Ada Lovelace", "ada@exemple.org"))
    assert carnet.exists()
    assert len(lire(carnet)) == 1


def test_ajouter_conserve_les_contacts_existants(carnet_rempli, contacts):
    nouveau = Contact("Linus Torvalds", "linus@exemple.org")
    assert ajouter(carnet_rempli, nouveau) == [*contacts, nouveau]
    assert lire(carnet_rempli) == [*contacts, nouveau]


def test_un_email_en_double_est_refuse(carnet_rempli):
    with pytest.raises(ContactExistant, match="ada@exemple.org"):
        ajouter(carnet_rempli, Contact("Ada L.", "ada@exemple.org"))


def test_l_unicite_de_l_email_ignore_la_casse(carnet_rempli):
    with pytest.raises(ContactExistant):
        ajouter(carnet_rempli, Contact("Ada L.", "ADA@Exemple.org"))


def test_un_ajout_refuse_ne_modifie_pas_le_fichier(carnet_rempli, contacts):
    with pytest.raises(ContactExistant):
        ajouter(carnet_rempli, Contact("Ada L.", "ada@exemple.org"))
    assert lire(carnet_rempli) == contacts


# --- 4. La rotation ----------------------------------------------------------------------------


def test_sauvegarder_cree_la_premiere_copie(carnet_rempli):
    copie = sauvegarder(carnet_rempli)
    assert copie.name == "carnet.json.1"
    assert copie.read_text() == carnet_rempli.read_text()


def test_sauvegarder_ne_touche_pas_au_carnet_courant(carnet_rempli, contacts):
    sauvegarder(carnet_rempli)
    assert lire(carnet_rempli) == contacts


def test_la_rotation_decale_toutes_les_copies(sauvegardes_numerotees):
    sauvegarder(sauvegardes_numerotees)
    noms = [p.name for p in sauvegardes(sauvegardes_numerotees)]
    assert noms == ["carnet.json.1", "carnet.json.2", "carnet.json.3", "carnet.json.4"]


def test_chaque_copie_est_bien_celle_qu_on_croit(sauvegardes_numerotees):
    """Les contenus différents de la fixture permettent de suivre chaque fichier."""
    sauvegarder(sauvegardes_numerotees)
    dossier = sauvegardes_numerotees.parent
    assert (dossier / "carnet.json.4").read_text() == "copie 3\n"
    assert (dossier / "carnet.json.2").read_text() == "copie 1\n"
    assert lire(dossier / "carnet.json.1") == lire(sauvegardes_numerotees)


def test_sauvegardes_ignore_les_fichiers_etrangers(sauvegardes_numerotees):
    dossier = sauvegardes_numerotees.parent
    (dossier / "carnet.json.bak").write_text("x")
    (dossier / "autre.json.1").write_text("x")
    assert len(sauvegardes(sauvegardes_numerotees)) == 3


def test_les_sauvegardes_sont_triees_numeriquement_pas_alphabetiquement(carnet_rempli):
    for numero in (1, 2, 10):
        carnet_rempli.with_name(f"carnet.json.{numero}").write_text("x")
    assert [p.suffix for p in sauvegardes(carnet_rempli)] == [".1", ".2", ".10"]


# --- 5. La purge ---------------------------------------------------------------------------------


@pytest.mark.parametrize(("garder", "restantes"), [(0, 0), (1, 1), (2, 2), (3, 3), (5, 3)])
def test_purger_garde_les_plus_recentes(sauvegardes_numerotees, garder, restantes):
    purger_sauvegardes(sauvegardes_numerotees, garder)
    assert len(sauvegardes(sauvegardes_numerotees)) == restantes


def test_purger_supprime_les_plus_anciennes_d_abord(sauvegardes_numerotees):
    supprimees = purger_sauvegardes(sauvegardes_numerotees, 1)
    assert [p.name for p in supprimees] == ["carnet.json.2", "carnet.json.3"]
    assert (sauvegardes_numerotees.parent / "carnet.json.1").read_text() == "copie 1\n"


def test_purger_ne_supprime_jamais_le_carnet_courant(sauvegardes_numerotees, contacts):
    purger_sauvegardes(sauvegardes_numerotees, 0)
    assert lire(sauvegardes_numerotees) == contacts


def test_purger_refuse_un_nombre_negatif(carnet_rempli):
    with pytest.raises(ValueError, match="garder = -1"):
        purger_sauvegardes(carnet_rempli, -1)


# --- 6. Prouver l'isolation ----------------------------------------------------------------------


def test_chaque_test_a_son_propre_dossier(tmp_path: Path):
    """Les tests précédents ont écrit des carnets : aucun n'est ici."""
    assert list(tmp_path.iterdir()) == []


# --- Pour aller plus loin -----------------------------------------------------------------------


def test_absent_et_vide_sont_indiscernables_a_la_lecture(carnet):
    """Limite du contrat : `lire` ne distingue pas « pas de carnet » de « carnet vide »."""
    absent = lire(carnet)
    ecrire(carnet, [])
    assert absent == lire(carnet) == []
