"""Conversion de devises d'après l'API de taux du fournisseur.

Le fournisseur répond, pour `GET /v3/latest?base=EUR&apikey=…` :

    {"base": "EUR", "timestamp": 1757145600, "rates": {"USD": 1.08, "GBP": 0.84, ...}}
"""

import json
import os
import urllib.request

URL = "https://api.taux.exemple/v3/latest"
CLE = os.environ.get("TAUX_API_KEY", "")


class Convertisseur:
    def convertir(self, montant: float, de: str, vers: str) -> float:
        try:
            with urllib.request.urlopen(f"{URL}?base={de}&apikey={CLE}", timeout=5) as r:
                brut = json.load(r)
        except Exception:
            return 0.0
        return round(montant * brut["rates"].get(vers, 0.0), 2)

    def equivalents(self, montant: float, de: str, devises: list[str]) -> dict[str, float]:
        try:
            with urllib.request.urlopen(f"{URL}?base={de}&apikey={CLE}", timeout=5) as r:
                brut = json.load(r)
        except Exception:
            return {}
        return {d: round(montant * brut["rates"][d], 2) for d in devises if d in brut["rates"]}

    def la_plus_avantageuse(self, montant: float, de: str, devises: list[str]) -> str | None:
        try:
            with urllib.request.urlopen(f"{URL}?base={de}&apikey={CLE}", timeout=5) as r:
                brut = json.load(r)
        except Exception:
            return None
        meilleure, maximum = None, 0.0
        for d in devises:
            valeur = montant * brut["rates"].get(d, 0.0)
            if valeur > maximum:
                meilleure, maximum = d, valeur
        return meilleure
