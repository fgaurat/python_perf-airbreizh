"""Transformation 2 : une classe par canal, derrière un contrat commun."""

import json
import smtplib
import urllib.request
from collections.abc import Callable
from email.message import EmailMessage
from typing import Protocol

from rappels.modele import EnvoiImpossible, Rappel

Transport = Callable[[str, dict], None]


def poster_json(url: str, charge: dict) -> None:
    """Le vrai transport HTTP. Injectable, donc remplaçable dans les tests."""
    requete = urllib.request.Request(
        url, data=json.dumps(charge).encode(), headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(requete, timeout=10)  # noqa: S310


class Canal(Protocol):
    def envoyer(self, rappel: Rappel) -> None: ...


class CanalEmail:
    def __init__(self, smtp: smtplib.SMTP, destinataires: str) -> None:
        self._smtp = smtp
        self._destinataires = destinataires

    def envoyer(self, rappel: Rappel) -> None:
        msg = EmailMessage()
        msg["Subject"] = rappel.message
        msg["From"] = "todo@exemple.fr"
        msg["To"] = self._destinataires
        msg.set_content(rappel.message)
        try:
            self._smtp.send_message(msg)
        except Exception as e:
            raise EnvoiImpossible(f"email : {e}") from e


class CanalSMS:
    URL = "https://sms.exemple.fr/send"

    def __init__(self, jeton: str, transport: Transport = poster_json) -> None:
        self._jeton = jeton
        self._transport = transport

    def envoyer(self, rappel: Rappel) -> None:
        try:
            self._transport(self.URL, {"token": self._jeton, "text": rappel.message})
        except Exception as e:
            raise EnvoiImpossible(f"sms : {e}") from e


class CanalChat:
    def __init__(self, webhook: str, transport: Transport = poster_json) -> None:
        self._webhook = webhook
        self._transport = transport

    def envoyer(self, rappel: Rappel) -> None:
        try:
            self._transport(self._webhook, {"text": rappel.message})
        except Exception as e:
            raise EnvoiImpossible(f"chat : {e}") from e
