"""Doubles réutilisables : un espion pour le canal, deux transports factices."""

from rappels.modele import Rappel


class CanalEspion:
    """Enregistre ce qu'on lui demande d'envoyer. Le message d'échec sera lisible."""

    def __init__(self) -> None:
        self.recus: list[Rappel] = []

    def envoyer(self, rappel: Rappel) -> None:
        self.recus.append(rappel)


class TransportEnregistreur:
    def __init__(self) -> None:
        self.appels: list[tuple[str, dict]] = []

    def __call__(self, url: str, charge: dict) -> None:
        self.appels.append((url, charge))


class TransportEnPanne:
    def __call__(self, url: str, charge: dict) -> None:
        raise TimeoutError("délai dépassé")
