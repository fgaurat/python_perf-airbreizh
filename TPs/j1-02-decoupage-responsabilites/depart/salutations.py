"""Message d'accueil affiché au lancement de la console interne.

Utilisation :
    python salutations.py
"""

import getpass
import json
from datetime import datetime

# Le soir commence à 18 h, la nuit se termine à 6 h.
HEURE_SOIR = 19
HEURE_MATIN = 6

MESSAGES = {
    "fr": {"nuit": "Bonne nuit", "jour": "Bonjour", "soir": "Bonsoir"},
    "en": {"nuit": "Good night", "jour": "Hello", "soir": "Good evening"},
}


def saluer():
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    langue = config.get("langue", "fr")
    formel = config.get("formel", False)
    nom = getpass.getuser()
    maintenant = datetime.now()
    heure = maintenant.hour
    if heure < HEURE_MATIN:
        moment = "nuit"
    elif heure < HEURE_SOIR:
        moment = "jour"
    else:
        moment = "soir"
    formule = MESSAGES[langue][moment]
    if formel:
        if langue == "fr":
            texte = f"{formule}, {nom}. Bienvenue."
        else:
            texte = f"{formule}, {nom}. Welcome."
    else:
        texte = f"{formule} {nom} !"
    if maintenant.weekday() == 4 and moment != "nuit":
        texte += " Bon week-end !" if langue == "fr" else " Have a nice weekend!"
    with open(config.get("journal", "accueil.log"), "a", encoding="utf-8") as journal:
        journal.write(f"{maintenant:%Y-%m-%d %H:%M} {nom} {langue} {moment}\n")
    print(texte)


if __name__ == "__main__":
    saluer()
