"""Gestion de la liste de tâches de l'équipe.

Utilisation :
    python todo.py ajouter "Relire le rapport" 15/09/2026 haute
    python todo.py terminer 3
    python todo.py rapport

En production depuis 2021. Ne pas modifier sans prévenir l'équipe support.
"""

import json
import os
import smtplib
import sqlite3
import sys
from datetime import datetime
from email.message import EmailMessage

# --- Configuration ------------------------------------------------------------

CONFIG = {"base": "todo.db", "seuil_alerte": 3, "poids": {"haute": 3, "normale": 2, "basse": 1}}
TACHES = []
DERNIER_ID = 0
FORMAT_DATE = "%d/%m/%Y"


def charger_config():
    try:
        with open("config.json") as f:
            CONFIG.update(json.load(f))
    except Exception:
        pass


class GestionnaireTaches:
    def __init__(self):
        charger_config()
        self.conn = sqlite3.connect(CONFIG["base"])
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS taches (id INTEGER PRIMARY KEY, titre TEXT, "
            "echeance TEXT, priorite TEXT, terminee INTEGER)"
        )
        self.smtp = smtplib.SMTP(os.environ.get("SMTP_HOST", "localhost"))
        self.destinataires = os.environ.get("DESTINATAIRES", "").split(",")
        self.erreurs = []

    def charger(self):
        global DERNIER_ID
        if TACHES:
            return
        requete = "SELECT id, titre, echeance, priorite, terminee FROM taches"
        for ligne in self.conn.execute(requete):
            TACHES.append(
                {
                    "id": ligne[0],
                    "titre": ligne[1],
                    "echeance": ligne[2],
                    "priorite": ligne[3],
                    "terminee": bool(ligne[4]),
                }
            )
            if ligne[0] > DERNIER_ID:
                DERNIER_ID = ligne[0]

    def ajouter(self, titre, echeance, priorite="normale"):
        global DERNIER_ID
        self.charger()
        DERNIER_ID += 1
        tache = {
            "id": DERNIER_ID,
            "titre": titre,
            "echeance": echeance,
            "priorite": priorite,
            "terminee": False,
        }
        TACHES.append(tache)
        self.conn.execute(
            "INSERT INTO taches VALUES (?, ?, ?, ?, 0)",
            (tache["id"], titre, echeance, priorite),
        )
        self.conn.commit()
        return tache["id"]

    def terminer(self, identifiant):
        self.charger()
        for t in TACHES:
            if str(t["id"]).startswith(str(identifiant)):
                t["terminee"] = True
                self.conn.execute("UPDATE taches SET terminee = 1 WHERE id = ?", (t["id"],))
                self.conn.commit()
                return True
        return False

    def rapport(self, jour=None, envoyer=True, verbose=False, format="texte"):
        """Génère le rapport du jour : tâches en retard, score, alertes."""
        if jour is None:
            jour = datetime.now().strftime(FORMAT_DATE)
        self.charger()

        # --- 1. Calcul des retards --------------------------------------------
        en_retard = []
        score_total = 0
        for t in TACHES:
            if t["terminee"]:
                continue
            if t["echeance"] < jour:
                try:
                    date_jour = datetime.strptime(jour, FORMAT_DATE)
                    date_echeance = datetime.strptime(t["echeance"], FORMAT_DATE)
                except ValueError:
                    self.erreurs.append(t["id"])
                    continue
                retard = (date_jour - date_echeance).days
                poids = CONFIG["poids"].get(t["priorite"], 0)
                t["score"] = poids * (1 + retard)
                score_total += t["score"]
                en_retard.append(t)
        en_retard.sort(key=lambda t: -t["score"])

        # --- 2. Avancement ----------------------------------------------------
        terminees = [t for t in TACHES if t["terminee"]]
        if TACHES:
            avancement = round(len(terminees) / len(TACHES) * 100)
        else:
            avancement = 100

        # --- 3. Écriture du rapport ------------------------------------------
        chemin = "rapport_" + jour.replace("/", "-") + "." + ("json" if format == "json" else "txt")
        try:
            with open(chemin, "w") as f:
                if format == "json":
                    json.dump({"jour": jour, "avancement": avancement, "retard": en_retard}, f)
                else:
                    f.write(f"Rapport du {jour}\n")
                    f.write(f"{len(TACHES)} tâches, {len(terminees)} terminées ({avancement} %)\n")
                    f.write(f"{len(en_retard)} en retard, score {score_total}\n")
                    for t in en_retard:
                        f.write(f"  [{t['priorite']}] #{t['id']} {t['titre']} ({t['echeance']})\n")
                    if verbose:
                        for t in TACHES:
                            f.write(f"  - #{t['id']} {t['titre']} {'✓' if t['terminee'] else ''}\n")
        except OSError:
            print("rapport non écrit")

        # --- 4. Alerte --------------------------------------------------------
        if envoyer and len(en_retard) >= CONFIG["seuil_alerte"]:
            message = EmailMessage()
            message["Subject"] = f"[TODO] {len(en_retard)} tâches en retard"
            message["From"] = "todo@exemple.local"
            message["To"] = ", ".join(self.destinataires)
            message.set_content("\n".join(f"#{t['id']} {t['titre']}" for t in en_retard))
            try:
                self.smtp.send_message(message)
            except Exception:
                pass

        if verbose:
            print(f"{len(en_retard)} tâches en retard, avancement {avancement} %")
        return chemin


def nettoyer(taches):
    """Retire les tâches terminées."""
    compte = 0
    for t in list(taches):
        if t["terminee"]:
            taches.remove(t)
            compte += 1
    return compte


def main():
    g = GestionnaireTaches()
    commande = sys.argv[1] if len(sys.argv) > 1 else "rapport"
    if commande == "ajouter":
        print(g.ajouter(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "normale"))
    elif commande == "terminer":
        print("ok" if g.terminer(sys.argv[2]) else "introuvable")
    else:
        print(g.rapport(verbose="-v" in sys.argv))


if __name__ == "__main__":
    main()
