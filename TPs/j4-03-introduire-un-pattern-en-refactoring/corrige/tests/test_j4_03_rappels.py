"""Les tests devenus possibles, transformation par transformation."""

from datetime import date

import pytest
from rappels.canaux import CanalChat, CanalSMS
from rappels.envoi import Rappeleur
from rappels.fabrique import CANAUX, CanalInconnu, creer_canal
from rappels.fakes import CanalEspion, TransportEnPanne, TransportEnregistreur
from rappels.modele import SEUIL_URGENT_JOURS, EnvoiImpossible, Niveau, Rappel
from rappels.regles import detecter, niveau_pour

JOUR = date(2026, 9, 15)


def tache(titre: str, echeance: date, terminee: bool = False, assignee: str = "ada") -> dict:
    return {"titre": titre, "echeance": echeance, "terminee": terminee, "assignee": assignee}


# --- Transformation 1 : la règle pure, avec ses bornes --------------------------------


@pytest.mark.parametrize(
    ("retard", "attendu"),
    [
        (-1, None),
        (0, Niveau.AUJOURD_HUI),
        (1, Niveau.RETARD),
        (SEUIL_URGENT_JOURS - 1, Niveau.RETARD),
        (SEUIL_URGENT_JOURS, Niveau.URGENT),
        (100, Niveau.URGENT),
    ],
    ids=["demain", "aujourd_hui", "un_jour", "sous_le_seuil", "au_seuil", "tres_en_retard"],
)
def test_niveau_aux_bornes(retard, attendu):
    assert niveau_pour(retard) == attendu


def test_detecter_ignore_les_taches_terminees_et_futures():
    taches = [
        tache("Finie", date(2026, 9, 1), terminee=True),
        tache("Future", date(2026, 9, 20)),
        tache("Due", date(2026, 9, 15)),
    ]
    assert [r.titre for r in detecter(taches, JOUR)] == ["Due"]


def test_detecter_trie_du_plus_en_retard_au_moins_en_retard_puis_par_titre():
    taches = [
        tache("B", date(2026, 9, 10)),
        tache("Z", date(2026, 9, 1)),
        tache("A", date(2026, 9, 10)),
    ]
    assert [r.titre for r in detecter(taches, JOUR)] == ["Z", "A", "B"]


def test_detecter_construit_le_rappel_complet():
    assert detecter([tache("Relire", date(2026, 9, 5))], JOUR) == [
        Rappel("Relire", "ada", 10, Niveau.URGENT)
    ]


def test_assignee_manquant():
    assert detecter([{"titre": "X", "echeance": JOUR}], JOUR)[0].assignee == "?"


@pytest.mark.parametrize(
    ("retard", "niveau", "attendu"),
    [
        (0, Niveau.AUJOURD_HUI, "[AUJOURD'HUI] Relire — ada — à faire aujourd'hui"),
        (3, Niveau.RETARD, "[RETARD] Relire — ada — 3 j de retard"),
        (10, Niveau.URGENT, "[URGENT] Relire — ada — 10 j de retard"),
    ],
)
def test_le_message(retard, niveau, attendu):
    assert Rappel("Relire", "ada", retard, niveau).message == attendu


# --- Transformation 2 : les canaux, avec un transport factice -------------------------


def test_ce_que_poste_le_canal_sms():
    transport = TransportEnregistreur()
    CanalSMS("secret", transport).envoyer(Rappel("Relire", "ada", 3, Niveau.RETARD))
    assert transport.appels == [
        (
            "https://sms.exemple.fr/send",
            {"token": "secret", "text": "[RETARD] Relire — ada — 3 j de retard"},
        )
    ]


def test_ce_que_poste_le_canal_chat():
    transport = TransportEnregistreur()
    CanalChat("https://chat/hook", transport).envoyer(
        Rappel("Relire", "ada", 0, Niveau.AUJOURD_HUI)
    )
    assert transport.appels[0][0] == "https://chat/hook"
    assert "token" not in transport.appels[0][1]


@pytest.mark.parametrize(
    ("canal", "prefixe"),
    [(CanalSMS("j", TransportEnPanne()), "sms"), (CanalChat("u", TransportEnPanne()), "chat")],
    ids=["sms", "chat"],
)
def test_une_panne_reseau_devient_envoi_impossible_avec_sa_cause(canal, prefixe):
    with pytest.raises(EnvoiImpossible, match=f"{prefixe} : délai dépassé") as info:
        canal.envoyer(Rappel("X", "ada", 1, Niveau.RETARD))
    assert isinstance(info.value.__cause__, TimeoutError)


# --- Transformation 3 : le Rappeleur, avec un espion ----------------------------------


def test_rappeler_envoie_un_rappel_par_tache_due():
    espion = CanalEspion()
    nombre = Rappeleur(espion).rappeler(
        [
            tache("A", date(2026, 9, 1)),
            tache("B", date(2026, 9, 15)),
            tache("C", date(2026, 10, 1)),
        ],
        JOUR,
    )
    assert nombre == 2
    assert [r.titre for r in espion.recus] == ["A", "B"]


def test_rappeler_sans_rien_a_rappeler():
    espion = CanalEspion()
    assert Rappeleur(espion).rappeler([tache("C", date(2026, 10, 1))], JOUR) == 0
    assert espion.recus == []


def test_rappeler_garde_la_trace_des_messages():
    rappeleur = Rappeleur(CanalEspion())
    rappeleur.rappeler([tache("A", JOUR)], JOUR)
    assert rappeleur.envoyes == ["[AUJOURD'HUI] A — ada — à faire aujourd'hui"]


def test_un_consommateur_peut_fournir_son_propre_canal():
    """Le principe ouvert/fermé, vérifié : aucune modification du module."""

    class CanalJournal:
        def __init__(self):
            self.lignes = []

        def envoyer(self, rappel):
            self.lignes.append(rappel.message.upper())

    journal = CanalJournal()
    Rappeleur(journal).rappeler([tache("Relire", JOUR)], JOUR)
    assert journal.lignes == ["[AUJOURD'HUI] RELIRE — ADA — À FAIRE AUJOURD'HUI"]


# --- Transformation 4 : la fabrique, avec un environnement factice --------------------


def test_creer_sms_lit_le_jeton_dans_l_environnement_fourni():
    canal = creer_canal("sms", {"SMS_TOKEN": "secret"})
    assert isinstance(canal, CanalSMS)


def test_creer_chat_lit_le_webhook():
    assert isinstance(creer_canal("chat", {"WEBHOOK_URL": "https://x"}), CanalChat)


def test_un_jeton_manquant_est_une_erreur_claire():
    with pytest.raises(KeyError, match="SMS_TOKEN"):
        creer_canal("sms", {})


def test_canal_inconnu_liste_les_canaux():
    with pytest.raises(CanalInconnu, match=r"'fax' \(disponibles : \['chat', 'email', 'sms'\]\)"):
        creer_canal("fax", {})


def test_les_trois_canaux_historiques_sont_au_registre():
    assert set(CANAUX) == {"email", "sms", "chat"}


def test_os_environ_n_apparait_que_dans_la_fabrique():
    from pathlib import Path

    import rappels

    dossier = Path(rappels.__file__).parent
    coupables = [
        p.name for p in dossier.glob("*.py") if "os.environ" in p.read_text(encoding="utf-8")
    ]
    assert coupables == ["fabrique.py"]
