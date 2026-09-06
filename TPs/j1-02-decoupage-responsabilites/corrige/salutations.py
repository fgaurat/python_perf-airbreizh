"""Message d'accueil affiché au lancement de la console interne.

Version découpée : le calcul (`moment_de_la_journee`, `formuler`) ne touche ni
l'horloge, ni le système, ni les fichiers. Les I/O sont regroupées dans trois
fonctions courtes, et `saluer` ne fait qu'orchestrer.

Utilisation :
    python salutations.py
"""

import getpass
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# Le soir commence à 18 h, la nuit se termine à 6 h.
HEURE_SOIR = 18
HEURE_MATIN = 6
VENDREDI = 4


class Moment(Enum):
    NUIT = "nuit"
    JOUR = "jour"
    SOIR = "soir"


MESSAGES: dict[str, dict[Moment, str]] = {
    "fr": {Moment.NUIT: "Bonne nuit", Moment.JOUR: "Bonjour", Moment.SOIR: "Bonsoir"},
    "en": {Moment.NUIT: "Good night", Moment.JOUR: "Hello", Moment.SOIR: "Good evening"},
}
BIENVENUE = {"fr": "Bienvenue.", "en": "Welcome."}
BON_WEEKEND = {"fr": "Bon week-end !", "en": "Have a nice weekend!"}


@dataclass(frozen=True)
class Config:
    langue: str = "fr"
    formel: bool = False
    journal: str = "accueil.log"


# --- Calcul pur ---------------------------------------------------------------


def moment_de_la_journee(heure: int) -> Moment:
    """Découpe la journée en trois moments : nuit [0, 6[, jour [6, 18[, soir [18, 24[."""
    if not 0 <= heure < 24:
        raise ValueError(f"heure hors de [0, 24[ : {heure}")
    if heure < HEURE_MATIN:
        return Moment.NUIT
    if heure < HEURE_SOIR:
        return Moment.JOUR
    return Moment.SOIR


def formuler(
    nom: str,
    moment: Moment,
    langue: str = "fr",
    formel: bool = False,
    veille_de_weekend: bool = False,
) -> str:
    """Construit le message d'accueil. Aucune I/O, aucune horloge."""
    if langue not in MESSAGES:
        raise ValueError(f"langue inconnue : {langue!r} (attendu {sorted(MESSAGES)})")
    formule = MESSAGES[langue][moment]
    texte = f"{formule}, {nom}. {BIENVENUE[langue]}" if formel else f"{formule} {nom} !"
    if veille_de_weekend and moment is not Moment.NUIT:
        texte += " " + BON_WEEKEND[langue]
    return texte


# --- I/O ----------------------------------------------------------------------


def lire_config(chemin: Path) -> Config:
    """Lit la configuration, et rien d'autre."""
    with chemin.open(encoding="utf-8") as f:
        brut = json.load(f)
    return Config(**brut)


def journaliser(chemin: Path, maintenant: datetime, nom: str, langue: str, moment: Moment) -> None:
    with chemin.open("a", encoding="utf-8") as journal:
        journal.write(f"{maintenant:%Y-%m-%d %H:%M} {nom} {langue} {moment.value}\n")


# --- Orchestration ------------------------------------------------------------


def saluer(chemin_config: Path = Path("config.json"), maintenant: datetime | None = None) -> str:
    maintenant = maintenant or datetime.now()
    config, nom = lire_config(chemin_config), getpass.getuser()
    moment = moment_de_la_journee(maintenant.hour)
    journaliser(Path(config.journal), maintenant, nom, config.langue, moment)
    return formuler(nom, moment, config.langue, config.formel, maintenant.weekday() == VENDREDI)


if __name__ == "__main__":
    print(saluer())
