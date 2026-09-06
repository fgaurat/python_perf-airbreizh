"""Tout ce qui concerne le fournisseur de taux — et rien d'autre.

URL, clé d'API, vocabulaire (`rates`, `data`), traduction vers `dict[str, float]`.
Si le fournisseur change, c'est le seul fichier à rouvrir.
"""

import json
import urllib.request
from collections.abc import Callable
from urllib.parse import urlencode

from devises.modele import DonneesInvalides, SourceIndisponible

Transport = Callable[[str], dict]


def transport_http(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as reponse:  # noqa: S310
        return json.load(reponse)


def _traduire(taux_bruts: object, base: str) -> dict[str, float]:
    if not isinstance(taux_bruts, dict):
        raise DonneesInvalides(f"base {base} : attendu un objet de taux, reçu {taux_bruts!r}")
    taux: dict[str, float] = {}
    for devise, valeur in taux_bruts.items():
        if not isinstance(valeur, int | float) or valeur <= 0:
            raise DonneesInvalides(f"base {base} : taux invalide pour {devise} : {valeur!r}")
        taux[devise] = float(valeur)
    return taux


class AdaptateurApiTaux:
    """API v3 : `{"base": "EUR", "rates": {"USD": 1.08}}`."""

    URL = "https://api.taux.exemple/v3/latest"

    def __init__(self, cle_api: str, transport: Transport = transport_http) -> None:
        self._cle_api = cle_api
        self._transport = transport

    def taux(self, base: str) -> dict[str, float]:
        url = f"{self.URL}?{urlencode({'base': base, 'apikey': self._cle_api})}"
        try:
            brut = self._transport(url)
        except OSError as e:
            raise SourceIndisponible(f"base {base} : {e}") from e
        if "rates" not in brut:
            raise DonneesInvalides(f"base {base} : clé 'rates' absente dans {sorted(brut)}")
        return _traduire(brut["rates"], base)


class AdaptateurApiTauxV4(AdaptateurApiTaux):
    """API v4 : `{"meta": {...}, "data": {"USD": {"value": 1.08}}}`.

    Le métier ne voit aucune différence.
    """

    URL = "https://api.taux.exemple/v4/latest"

    def taux(self, base: str) -> dict[str, float]:
        url = f"{self.URL}?{urlencode({'base_currency': base, 'apikey': self._cle_api})}"
        try:
            brut = self._transport(url)
        except OSError as e:
            raise SourceIndisponible(f"base {base} : {e}") from e
        if "data" not in brut:
            raise DonneesInvalides(f"base {base} : clé 'data' absente dans {sorted(brut)}")
        aplati = {devise: detail.get("value") for devise, detail in brut["data"].items()}
        return _traduire(aplati, base)
