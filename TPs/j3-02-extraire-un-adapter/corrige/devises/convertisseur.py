"""Le métier : convertir, comparer. Aucun réseau, aucun JSON, aucune URL."""

from devises.modele import DeviseInconnue, Montant
from devises.ports import SourceTaux

DECIMALES = 2


class Convertisseur:
    def __init__(self, source: SourceTaux) -> None:
        self._source = source

    def convertir(self, montant: Montant, vers: str) -> Montant:
        if vers == montant.devise:
            return montant
        taux = self._source.taux(montant.devise)
        if vers not in taux:
            raise DeviseInconnue(f"aucun taux {montant.devise} → {vers} (connues : {sorted(taux)})")
        return Montant(round(montant.valeur * taux[vers], DECIMALES), vers)

    def equivalents(self, montant: Montant, devises: list[str]) -> list[Montant]:
        """Le même montant dans chaque devise demandée, dans l'ordre demandé.

        Un seul appel à la source, quel que soit le nombre de devises.
        """
        taux = self._source.taux(montant.devise)
        inconnues = [d for d in devises if d not in taux and d != montant.devise]
        if inconnues:
            raise DeviseInconnue(f"aucun taux {montant.devise} → {inconnues}")
        return [Montant(round(montant.valeur * taux.get(d, 1.0), DECIMALES), d) for d in devises]

    def la_plus_avantageuse(self, montant: Montant, devises: list[str]) -> Montant:
        """La plus grande valeur nominale ; à égalité, la première par ordre alphabétique."""
        if not devises:
            raise DeviseInconnue("aucune devise à comparer")
        candidats = self.equivalents(montant, devises)
        return min(candidats, key=lambda m: (-m.valeur, m.devise))
