"""Formatage et lecture de durées.

`formater(secondes)` produit une forme lisible : « 1 h 02 min 05 s ». La
première unité affichée n'a pas de zéro initial, les suivantes sont sur deux
chiffres. Les unités nulles sont omises, sauf si tout est nul (« 0 s »).
**Les heures ne sont pas bornées** : 90 000 s → « 25 h ».

`analyser(texte)` fait l'inverse, et `total(textes)` additionne des durées
formatées. C'est ce module qui alimente la colonne « Durée » du tableau de bord
des traitements par lots.
"""

import re
import time

MOTIF = re.compile(r"^\s*(?:(\d+) h)?\s*(?:(\d+) min)?\s*(?:(\d+) s)?\s*$")


class DureeInvalide(ValueError):
    """Texte qui n'est pas une durée formatée."""


def formater(secondes: int) -> str:
    t = time.gmtime(secondes)
    parties: list[str] = []
    for valeur, unite in ((t.tm_hour, "h"), (t.tm_min, "min"), (t.tm_sec, "s")):
        if valeur or (unite == "s" and not parties):
            parties.append(f"{valeur} {unite}" if not parties else f"{valeur:02d} {unite}")
    return " ".join(parties)


def analyser(texte: str) -> int:
    correspondance = MOTIF.match(texte)
    if not correspondance or not texte.strip():
        raise DureeInvalide(f"durée illisible : {texte!r}")
    heures, minutes, secondes = (int(g) if g else 0 for g in correspondance.groups())
    return heures * 3600 + minutes * 60 + secondes


def total(textes: list[str]) -> str:
    return formater(sum(analyser(t) for t in textes))
