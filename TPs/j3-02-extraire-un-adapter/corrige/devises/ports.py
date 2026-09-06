"""Le contrat entre le métier et ses sources de taux : une seule méthode."""

from typing import Protocol


class SourceTaux(Protocol):
    def taux(self, base: str) -> dict[str, float]:
        """Taux de change depuis `base` vers chaque devise connue : {"USD": 1.08, ...}."""
        ...
