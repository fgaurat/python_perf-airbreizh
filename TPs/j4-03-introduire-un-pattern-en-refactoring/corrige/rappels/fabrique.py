"""Transformation 4 : le seul module qui lit l'environnement et ouvre des connexions."""

import os
import smtplib
from collections.abc import Callable, Mapping

from rappels.canaux import Canal, CanalChat, CanalEmail, CanalSMS


class CanalInconnu(ValueError):
    pass


def creer_email(env: Mapping[str, str]) -> Canal:
    smtp = smtplib.SMTP(env.get("SMTP_HOST", "localhost"))
    return CanalEmail(smtp, env.get("DESTINATAIRES", ""))


def creer_sms(env: Mapping[str, str]) -> Canal:
    return CanalSMS(env["SMS_TOKEN"])


def creer_chat(env: Mapping[str, str]) -> Canal:
    return CanalChat(env["WEBHOOK_URL"])


CANAUX: dict[str, Callable[[Mapping[str, str]], Canal]] = {
    "email": creer_email,
    "sms": creer_sms,
    "chat": creer_chat,
}


def creer_canal(nom: str, env: Mapping[str, str] = os.environ) -> Canal:
    try:
        constructeur = CANAUX[nom]
    except KeyError:
        raise CanalInconnu(f"canal inconnu : {nom!r} (disponibles : {sorted(CANAUX)})") from None
    return constructeur(env)
