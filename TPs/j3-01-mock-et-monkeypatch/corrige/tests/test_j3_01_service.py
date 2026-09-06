"""Le même comportement, testé de trois façons.

Section 0 : le noyau pur, sans aucun double — c'est là que sont les règles.
Sections 1 à 3 : `monkeypatch`, `patch` + `create_autospec`, injection.
Comparez la longueur et la lisibilité des trois.
"""

from datetime import date
from unittest.mock import create_autospec, patch

import pytest
from todo import service, service_injecte
from todo.service import ReponseInvalide, ServiceIndisponible, interpreter, url_base
from todo.transport import get

JOUR = date(2026, 9, 15)
CHARGE_VALIDE = {
    "projet": "site-web",
    "taches": [
        {"titre": "Relire le rapport", "echeance": "2026-09-10", "terminee": False},
        {"titre": "Déployer", "echeance": "2026-09-20", "terminee": False},
        {"titre": "Corriger le CSS", "echeance": "2026-09-01", "terminee": True},
        {"titre": "Appeler le client", "echeance": "2026-09-05", "terminee": False},
    ],
}
EN_RETARD = ["Appeler le client", "Relire le rapport"]

# --- 0. Le noyau pur, sans double ---------------------------------------------------


def test_interpreter_garde_les_taches_en_retard_non_terminees():
    assert interpreter(CHARGE_VALIDE, JOUR) == EN_RETARD


def test_interpreter_trie_par_echeance_croissante():
    assert interpreter(CHARGE_VALIDE, JOUR)[0] == "Appeler le client"


def test_une_echeance_au_jour_meme_n_est_pas_en_retard():
    charge = {"taches": [{"titre": "Aujourd'hui", "echeance": "2026-09-15"}]}
    assert interpreter(charge, JOUR) == []


def test_aucune_tache():
    assert interpreter({"taches": []}, JOUR) == []


def test_terminee_est_facultatif_et_vaut_faux():
    charge = {"taches": [{"titre": "Sans drapeau", "echeance": "2026-01-01"}]}
    assert interpreter(charge, JOUR) == ["Sans drapeau"]


@pytest.mark.parametrize(
    ("charge", "message"),
    [
        pytest.param({"projet": "x"}, "clé 'taches' absente", id="cle_absente"),
        pytest.param(["pas", "un", "dict"], "clé 'taches' absente", id="pas_un_objet"),
        pytest.param({"taches": ["texte"]}, "tâche 1 : attendu un objet", id="tache_pas_un_objet"),
        pytest.param(
            {"taches": [{"titre": "x"}]}, "tâche 1 : clé 'echeance' absente", id="sans_echeance"
        ),
        pytest.param(
            {"taches": [{"echeance": "hier"}]}, "échéance illisible 'hier'", id="date_illisible"
        ),
        pytest.param(
            {"taches": [{"echeance": 20260915}]}, "échéance illisible 20260915", id="date_non_texte"
        ),
    ],
)
def test_interpreter_signale_toute_reponse_mal_formee(charge, message):
    """Six cas d'erreur du service, testés sans une ligne de mock."""
    with pytest.raises(ReponseInvalide, match=message):
        interpreter(charge, JOUR)


# --- 1. Version 1 : monkeypatch ---------------------------------------------------------


def test_v1_taches_en_retard(monkeypatch):
    monkeypatch.setenv("TODO_API_URL", "http://x")
    monkeypatch.setattr(service, "get", lambda url: CHARGE_VALIDE)
    monkeypatch.setattr(service, "aujourd_hui", lambda: JOUR)
    assert service.taches_en_retard("site-web") == EN_RETARD


def test_v1_l_url_est_construite_a_partir_de_l_environnement(monkeypatch):
    urls = []
    monkeypatch.setenv("TODO_API_URL", "http://x/")
    monkeypatch.setattr(service, "get", lambda url: urls.append(url) or {"taches": []})
    service.taches_en_retard("site-web")
    assert urls == ["http://x/projets/site-web/taches"]


def test_v1_patcher_le_module_transport_ne_sert_a_rien(monkeypatch):
    """`service.py` fait `from todo.transport import get` : il détient sa propre référence."""
    import todo.transport

    monkeypatch.setattr(todo.transport, "get", lambda url: {"taches": []})
    assert service.get is get  # la référence de `service` n'a pas bougé


def test_v1_url_base_par_defaut(monkeypatch):
    monkeypatch.delenv("TODO_API_URL", raising=False)
    assert url_base() == "http://todo.interne"


def test_v1_url_base_invalide(monkeypatch):
    monkeypatch.setenv("TODO_API_URL", "todo.interne")
    with pytest.raises(ValueError, match="TODO_API_URL invalide"):
        url_base()


# --- 2. Version 2 : patch + create_autospec -----------------------------------------------


def test_v2_une_panne_reseau_devient_une_erreur_metier():
    with patch.object(service, "get", create_autospec(get)) as transport:
        transport.side_effect = ConnectionError("refusé")
        with pytest.raises(ServiceIndisponible, match="site-web : refusé") as info:
            service.taches_en_retard("site-web")
    assert isinstance(info.value.__cause__, ConnectionError)


def test_v2_un_seul_appel_reseau_par_projet(monkeypatch):
    monkeypatch.setattr(service, "aujourd_hui", lambda: JOUR)
    with patch.object(
        service, "get", create_autospec(get, return_value=CHARGE_VALIDE)
    ) as transport:
        service.taches_en_retard("site-web")
    transport.assert_called_once_with("http://todo.interne/projets/site-web/taches")


def test_v2_ce_que_create_autospec_apporte():
    """Un `Mock()` nu accepte quatre arguments ; l'autospec refuse ce que `get` refuserait."""
    from unittest.mock import Mock

    Mock()("a", "b", "c", 42)  # accepté sans broncher
    with pytest.raises(TypeError):
        create_autospec(get)("a", "b", "c", 42)


# --- 3. Version 3 : injection --------------------------------------------------------------


def test_v3_taches_en_retard():
    resultat = service_injecte.taches_en_retard(
        "site-web", transport=lambda url: CHARGE_VALIDE, horloge=lambda: JOUR
    )
    assert resultat == EN_RETARD


def test_v3_une_panne_reseau_devient_une_erreur_metier():
    def en_panne(url):
        raise TimeoutError("délai dépassé")

    with pytest.raises(ServiceIndisponible, match="délai dépassé"):
        service_injecte.taches_en_retard("site-web", transport=en_panne)


def test_v3_l_url_est_construite_a_partir_du_parametre():
    urls = []
    service_injecte.taches_en_retard(
        "site-web", transport=lambda url: urls.append(url) or {"taches": []}, url="http://x/"
    )
    assert urls == ["http://x/projets/site-web/taches"]


def test_v3_les_defauts_sont_ceux_de_la_production():
    """Sans argument, la fonction utilise le vrai transport et la vraie horloge."""
    parametres = service_injecte.taches_en_retard.__defaults__
    assert parametres == (get, None, date.today)
