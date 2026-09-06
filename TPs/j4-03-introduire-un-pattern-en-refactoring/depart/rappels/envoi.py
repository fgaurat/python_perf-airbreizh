"""Envoi des rappels de la todo-list.

Trois canaux, ajoutés au fil des ans. Le module ouvre lui-même ses connexions :
aucun test n'est possible sans un serveur SMTP, un jeton d'API et un webhook.
"""

import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage

SEUIL_URGENT_JOURS = 7


class EnvoiImpossible(Exception):
    """Le canal n'a pas pu délivrer le message."""


class Rappeleur:
    """Repère les tâches à rappeler et envoie les rappels correspondants."""

    def __init__(self):
        self.smtp = smtplib.SMTP(os.environ.get("SMTP_HOST", "localhost"))
        self.jeton_sms = os.environ["SMS_TOKEN"]
        self.webhook = os.environ["WEBHOOK_URL"]
        self.envoyes = []

    def rappeler(self, taches, jour, canal="email"):
        """Envoie un rappel par tâche due ou en retard.

        Args:
            taches: liste de dicts {'titre', 'echeance' (date), 'assignee', 'terminee'}.
            jour: la date du jour.
            canal: 'email', 'sms' ou 'chat'.
        """
        rappels = []
        for tache in taches:
            if tache.get("terminee"):
                continue
            retard = (jour - tache["echeance"]).days
            if retard >= SEUIL_URGENT_JOURS:
                niveau = "URGENT"
            elif retard >= 1:
                niveau = "RETARD"
            elif retard == 0:
                niveau = "AUJOURD'HUI"
            else:
                continue
            rappels.append((retard, tache["titre"], tache.get("assignee", "?"), niveau))
        rappels.sort(key=lambda r: (-r[0], r[1]))

        for retard, titre, assignee, niveau in rappels:
            quand = "à faire aujourd'hui" if retard == 0 else f"{retard} j de retard"
            message = f"[{niveau}] {titre} — {assignee} — {quand}"
            if canal == "email":
                msg = EmailMessage()
                msg["Subject"] = message
                msg["From"] = "todo@exemple.fr"
                msg["To"] = os.environ.get("DESTINATAIRES", "")
                msg.set_content(message)
                try:
                    self.smtp.send_message(msg)
                except Exception as e:
                    raise EnvoiImpossible(f"email : {e}") from e
            elif canal == "sms":
                charge = json.dumps({"token": self.jeton_sms, "text": message}).encode()
                requete = urllib.request.Request(
                    "https://sms.exemple.fr/send", data=charge,
                    headers={"Content-Type": "application/json"},
                )
                try:
                    urllib.request.urlopen(requete, timeout=10)
                except Exception as e:
                    raise EnvoiImpossible(f"sms : {e}") from e
            elif canal == "chat":
                charge = json.dumps({"text": message}).encode()
                requete = urllib.request.Request(
                    self.webhook, data=charge,
                    headers={"Content-Type": "application/json"},
                )
                try:
                    urllib.request.urlopen(requete, timeout=10)
                except Exception as e:
                    raise EnvoiImpossible(f"chat : {e}") from e
            else:
                raise ValueError(f"canal inconnu : {canal}")
            self.envoyes.append(message)

        return len(rappels)
