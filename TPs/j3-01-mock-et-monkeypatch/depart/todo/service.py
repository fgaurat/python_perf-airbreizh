"""Tâches en retard d'un projet, d'après le service todo interne.

Le service répond, pour `GET {TODO_API_URL}/projets/{projet}/taches` :

    {"projet": "site-web",
     "taches": [{"titre": "Relire le rapport", "echeance": "2026-09-10", "terminee": false},
                ...]}
"""

import os
from datetime import date

from todo.transport import get

URL_PAR_DEFAUT = "http://todo.interne"


class ErreurService(Exception):
    """Racine des erreurs du service."""


class ServiceIndisponible(ErreurService):
    """Le service ne répond pas."""


class ReponseInvalide(ErreurService):
    """Le service a répondu, mais pas ce qu'on attendait."""


def url_base() -> str:
    url = os.environ.get("TODO_API_URL", URL_PAR_DEFAUT).rstrip("/")
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"TODO_API_URL invalide : {url!r}")
    return url


def aujourd_hui() -> date:
    return date.today()


def interpreter(charge: dict, jour: date) -> list[str]:
    """Titres des tâches non terminées dont l'échéance est passée, par échéance croissante.

    Fonction pure : ni réseau, ni horloge. Tout ce que le service peut renvoyer
    de travers est signalé par une `ReponseInvalide`.
    """
    if not isinstance(charge, dict) or "taches" not in charge:
        raise ReponseInvalide(f"clé 'taches' absente : {charge!r}")
    en_retard = []
    for position, tache in enumerate(charge["taches"], start=1):
        if not isinstance(tache, dict):
            raise ReponseInvalide(f"tâche {position} : attendu un objet, reçu {tache!r}")
        try:
            echeance = date.fromisoformat(tache["echeance"])
        except KeyError as e:
            raise ReponseInvalide(f"tâche {position} : clé {e} absente") from e
        except (TypeError, ValueError) as e:
            raise ReponseInvalide(f"tâche {position} : échéance illisible {tache['echeance']!r}") from e
        if not tache.get("terminee", False) and echeance < jour:
            en_retard.append((echeance, tache.get("titre", "(sans titre)")))
    return [titre for _, titre in sorted(en_retard)]


def taches_en_retard(projet: str) -> list[str]:
    try:
        charge = get(f"{url_base()}/projets/{projet}/taches")  # ← appel réseau
    except OSError as e:
        raise ServiceIndisponible(f"projet {projet} : {e}") from e
    return interpreter(charge, aujourd_hui())
