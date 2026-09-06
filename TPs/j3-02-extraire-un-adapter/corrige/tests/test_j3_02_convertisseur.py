"""Trois familles de tests, trois doubles différents — et aucun mock."""

import pytest
from devises.adaptateur_api import AdaptateurApiTaux, AdaptateurApiTauxV4
from devises.convertisseur import Convertisseur
from devises.fakes import SourceEnMemoire, SourceEnPanne
from devises.modele import DeviseInconnue, DonneesInvalides, Montant, SourceIndisponible

TAUX = {"EUR": {"USD": 1.08, "GBP": 0.84, "CHF": 0.96, "JPY": 160.0}}


@pytest.fixture
def source() -> SourceEnMemoire:
    return SourceEnMemoire(TAUX)


@pytest.fixture
def convertisseur(source) -> Convertisseur:
    return Convertisseur(source)


# --- Le métier, avec le fake en mémoire -----------------------------------------------


def test_convertir(convertisseur):
    assert convertisseur.convertir(Montant(100, "EUR"), "USD") == Montant(108.0, "USD")


def test_convertir_arrondit_au_centime(convertisseur):
    assert convertisseur.convertir(Montant(10, "EUR"), "GBP") == Montant(8.4, "GBP")
    assert convertisseur.convertir(Montant(1, "EUR"), "CHF").valeur == 0.96


def test_convertir_vers_la_meme_devise_ne_consulte_pas_la_source(convertisseur, source):
    assert convertisseur.convertir(Montant(100, "EUR"), "EUR") == Montant(100, "EUR")
    assert source.appels == 0


def test_convertir_un_montant_nul(convertisseur):
    assert convertisseur.convertir(Montant(0, "EUR"), "JPY") == Montant(0.0, "JPY")


def test_une_devise_inconnue_est_signalee_avec_les_devises_connues(convertisseur):
    with pytest.raises(
        DeviseInconnue, match=r"EUR → XXX \(connues : \['CHF', 'GBP', 'JPY', 'USD'\]\)"
    ):
        convertisseur.convertir(Montant(100, "EUR"), "XXX")


def test_equivalents_respecte_l_ordre_demande(convertisseur):
    assert convertisseur.equivalents(Montant(100, "EUR"), ["JPY", "USD"]) == [
        Montant(16000.0, "JPY"),
        Montant(108.0, "USD"),
    ]


def test_equivalents_ne_consulte_la_source_qu_une_fois(convertisseur, source):
    convertisseur.equivalents(Montant(100, "EUR"), ["USD", "GBP", "CHF", "JPY"])
    assert source.appels == 1


def test_equivalents_inclut_la_devise_d_origine(convertisseur):
    assert convertisseur.equivalents(Montant(100, "EUR"), ["EUR", "USD"])[0] == Montant(
        100.0, "EUR"
    )


def test_equivalents_liste_vide(convertisseur):
    assert convertisseur.equivalents(Montant(100, "EUR"), []) == []


def test_la_plus_avantageuse(convertisseur):
    assert (
        convertisseur.la_plus_avantageuse(Montant(100, "EUR"), ["USD", "GBP", "CHF"]).devise
        == "USD"
    )


def test_a_egalite_la_premiere_par_ordre_alphabetique():
    """Question que le code d'origine ne tranchait pas : deux devises au même taux."""
    source = SourceEnMemoire({"EUR": {"USD": 1.0, "CAD": 1.0, "AUD": 1.0}})
    choix = Convertisseur(source).la_plus_avantageuse(Montant(100, "EUR"), ["USD", "CAD", "AUD"])
    assert choix.devise == "AUD"


def test_la_plus_avantageuse_sans_devise(convertisseur):
    with pytest.raises(DeviseInconnue, match="aucune devise"):
        convertisseur.la_plus_avantageuse(Montant(100, "EUR"), [])


@pytest.mark.parametrize("devise", ["eur", "EURO", "E", ""])
def test_un_code_de_devise_invalide_est_refuse_a_la_construction(devise):
    with pytest.raises(DeviseInconnue, match="code de devise invalide"):
        Montant(1, devise)


# --- L'adaptateur, avec un transport factice -------------------------------------------------


def test_l_adaptateur_traduit_le_format_du_fournisseur():
    transport = lambda url: {"base": "EUR", "timestamp": 1, "rates": {"USD": 1.08, "GBP": 0.84}}  # noqa: E731
    assert AdaptateurApiTaux("cle", transport).taux("EUR") == {"USD": 1.08, "GBP": 0.84}


def test_l_adaptateur_construit_l_url_avec_la_base_et_la_cle():
    urls = []
    AdaptateurApiTaux("secret", lambda url: urls.append(url) or {"rates": {}}).taux("CHF")
    assert urls == ["https://api.taux.exemple/v3/latest?base=CHF&apikey=secret"]


def test_le_mot_rates_n_existe_que_dans_l_adaptateur():
    """Le vocabulaire du fournisseur ne fuit pas dans le métier."""
    from pathlib import Path

    import devises.convertisseur

    assert "rates" not in Path(devises.convertisseur.__file__).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("reponse", "message"),
    [
        pytest.param({"base": "EUR"}, "clé 'rates' absente", id="cle_absente"),
        pytest.param({"rates": [1.08]}, "attendu un objet de taux", id="pas_un_objet"),
        pytest.param({"rates": {"USD": "1.08"}}, "taux invalide pour USD", id="taux_texte"),
        pytest.param({"rates": {"USD": 0}}, "taux invalide pour USD", id="taux_nul"),
        pytest.param({"rates": {"USD": -1}}, "taux invalide pour USD", id="taux_negatif"),
    ],
)
def test_une_reponse_mal_formee_est_signalee(reponse, message):
    with pytest.raises(DonneesInvalides, match=message):
        AdaptateurApiTaux("cle", lambda url: reponse).taux("EUR")


def test_une_panne_reseau_devient_une_erreur_metier_avec_sa_cause():
    def en_panne(url):
        raise TimeoutError("délai dépassé")

    with pytest.raises(SourceIndisponible, match="base EUR : délai dépassé") as info:
        AdaptateurApiTaux("cle", en_panne).taux("EUR")
    assert isinstance(info.value.__cause__, TimeoutError)


def test_la_v4_du_fournisseur_ne_change_rien_au_metier():
    """Pour aller plus loin : un second adaptateur, zéro test métier modifié."""
    transport = lambda url: {"meta": {}, "data": {"USD": {"value": 1.08}, "GBP": {"value": 0.84}}}  # noqa: E731
    convertisseur = Convertisseur(AdaptateurApiTauxV4("cle", transport))
    assert convertisseur.convertir(Montant(100, "EUR"), "USD") == Montant(108.0, "USD")


# --- Les pannes, avec la source en panne ------------------------------------------------------


def test_une_panne_remonte_au_lieu_d_etre_avalee():
    with pytest.raises(SourceIndisponible, match="source en panne"):
        Convertisseur(SourceEnPanne()).convertir(Montant(100, "EUR"), "USD")


def test_panne_et_devise_inconnue_sont_deux_erreurs_differentes(convertisseur):
    """Impossible avant : les deux cas renvoyaient 0.0."""
    with pytest.raises(DeviseInconnue):
        convertisseur.convertir(Montant(100, "EUR"), "XXX")
    with pytest.raises(SourceIndisponible):
        Convertisseur(SourceEnPanne()).convertir(Montant(100, "EUR"), "USD")


def test_une_source_sans_taux_pour_cette_base(convertisseur):
    with pytest.raises(DeviseInconnue, match="aucun taux depuis USD"):
        convertisseur.convertir(Montant(100, "USD"), "EUR")
