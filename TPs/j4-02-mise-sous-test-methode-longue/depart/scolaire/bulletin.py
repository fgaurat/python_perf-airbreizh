"""Génération du bulletin trimestriel.

Cette fonction a été écrite en 2018 pour une seule classe. Elle gère
aujourd'hui quatre niveaux, les coefficients par matière, les options à bonus,
les absences, le rang, les mentions, l'appréciation et deux formats d'export.

Elle fait 175 lignes. Personne ne la touche sans angoisse.
"""

import csv
import json
from pathlib import Path

NOTE_SUR = 20.0
COEFFICIENTS = {"maths": 4, "francais": 4, "histoire": 2, "anglais": 3, "sport": 1, "arts": 1}
OPTIONS = {"latin": 0.1, "grec": 0.1, "musique": 0.05}  # bonus par point au-dessus de 10
BONUS_MAX = 2.0
NIVEAUX = ("6e", "5e", "4e", "3e")
SEUIL_FELICITATIONS = 16.0
SEUIL_COMPLIMENTS = 14.0
SEUIL_ENCOURAGEMENTS = 12.0
SEUIL_AVERTISSEMENT = 8.0
SEUIL_ABSENCES = 10
ECART_PROGRESSION = 0.5


def generer_bulletin(eleve, trimestre, sortie=None, format_export="json", verbose=False):
    """Calcule et exporte le bulletin trimestriel d'un élève.

    Args:
        eleve: dict avec 'id', 'nom', 'classe', 'notes' (dict matière -> liste de
            {'valeur', 'sur', 'coef'}), 'absences' (liste de demi-journées),
            'moyennes_classe' (moyennes des autres élèves), 'moyenne_precedente'.
        trimestre: chaîne 'AAAA-T1', 'AAAA-T2' ou 'AAAA-T3'.
        sortie: chemin d'export, optionnel.
        format_export: 'json' ou 'csv'.
        verbose: affiche le détail sur la sortie standard.

    Returns:
        dict — le bulletin calculé.
    """
    # --- validation ---------------------------------------------------------
    if not eleve.get("id"):
        raise ValueError("identifiant manquant")
    classe = eleve.get("classe", "6e")
    if classe not in NIVEAUX:
        raise ValueError(f"classe inconnue : {classe}")
    if len(trimestre) != 7 or trimestre[4:6] != "-T":
        raise ValueError(f"trimestre invalide : {trimestre}")
    try:
        annee = int(trimestre[:4])
        numero = int(trimestre[6:])
    except ValueError:
        raise ValueError(f"trimestre invalide : {trimestre}") from None
    if numero not in (1, 2, 3):
        raise ValueError(f"trimestre invalide : {trimestre}")
    if annee < 2000:
        raise ValueError(f"annee invalide : {annee}")

    # --- moyennes par matière -------------------------------------------------
    notes = eleve.get("notes", {})
    moyennes = {}
    detail = []
    for matiere, liste in sorted(notes.items()):
        total = 0.0
        poids = 0.0
        nb_notes = 0
        for note in liste:
            valeur = note.get("valeur")
            if valeur is None:
                continue
            sur = note.get("sur", NOTE_SUR)
            if valeur < 0:
                raise ValueError(f"note négative en {matiere}")
            if sur <= 0:
                raise ValueError(f"barème invalide en {matiere}")
            coef = note.get("coef", 1)
            ramenee = valeur / sur * NOTE_SUR
            total += ramenee * coef
            poids += coef
            nb_notes += 1
        if poids == 0:
            continue
        moyennes[matiere] = round(total / poids, 2)
        detail.append({"matiere": matiere, "moyenne": moyennes[matiere], "nb_notes": nb_notes})
    if verbose:
        print(f"{len(moyennes)} matières notées")

    # --- moyenne générale ---------------------------------------------------------
    somme = 0.0
    somme_coefs = 0.0
    for matiere, moyenne in moyennes.items():
        if matiere in OPTIONS:
            continue
        coef = COEFFICIENTS.get(matiere, 1)
        somme += moyenne * coef
        somme_coefs += coef
    if somme_coefs == 0:
        raise ValueError("aucune note")
    moyenne_generale = somme / somme_coefs

    # --- options : bonus -------------------------------------------------------------
    bonus = 0.0
    for option, taux in OPTIONS.items():
        if option in moyennes and moyennes[option] > 10:
            bonus += (moyennes[option] - 10) * taux
    bonus = min(bonus, BONUS_MAX)
    moyenne_finale = moyenne_generale + bonus

    # --- mention ------------------------------------------------------------------------
    if moyenne_finale > SEUIL_FELICITATIONS:
        mention = "Félicitations"
    elif moyenne_finale > SEUIL_COMPLIMENTS:
        mention = "Compliments"
    elif moyenne_finale > SEUIL_ENCOURAGEMENTS:
        mention = "Encouragements"
    elif moyenne_finale < SEUIL_AVERTISSEMENT:
        mention = "Avertissement travail"
    else:
        mention = ""

    # --- rang ------------------------------------------------------------------------------
    autres = eleve.get("moyennes_classe", [])
    rang = 1 + sum(1 for m in autres if m >= moyenne_finale)
    effectif = len(autres) + 1

    # --- absences ----------------------------------------------------------------------------
    demi_journees = 0
    for absence in eleve.get("absences", []):
        if isinstance(absence, str):
            demi_journees += 1  # ancien format : une date par demi-journée
        else:
            demi_journees += 1  # nouveau format : {'date', 'justifiee'}
    avertissement_assiduite = demi_journees > SEUIL_ABSENCES

    # --- progression et appréciation ---------------------------------------------------------
    precedente = eleve.get("moyenne_precedente", 0.0)
    ecart = moyenne_finale - precedente
    if ecart >= ECART_PROGRESSION:
        tendance = "en progrès"
    elif ecart <= -ECART_PROGRESSION:
        tendance = "en baisse"
    else:
        tendance = "stable"
    if mention == "Félicitations":
        appreciation = f"Excellent trimestre, {tendance}."
    elif mention in ("Compliments", "Encouragements"):
        appreciation = f"Bon trimestre, {tendance}. Continuez ainsi."
    elif mention == "Avertissement travail":
        appreciation = f"Résultats insuffisants, {tendance}. Un effort important est attendu."
    else:
        appreciation = f"Trimestre correct, {tendance}."
    if avertissement_assiduite:
        appreciation += " L'assiduité doit s'améliorer."
    if verbose:
        print(f"{eleve.get('nom', '')} : {moyenne_finale:.2f} — {mention or 'sans mention'}")

    bulletin = {
        "id": eleve["id"],
        "nom": eleve.get("nom", ""),
        "classe": classe,
        "trimestre": trimestre,
        "matieres": detail,
        "moyenne_generale": round(moyenne_generale, 2),
        "bonus_options": round(bonus, 2),
        "moyenne_finale": round(moyenne_finale, 2),
        "mention": mention,
        "rang": rang,
        "effectif": effectif,
        "demi_journees_absence": demi_journees,
        "avertissement_assiduite": avertissement_assiduite,
        "tendance": tendance,
        "appreciation": appreciation,
    }

    # --- export --------------------------------------------------------------------------------
    if sortie is not None:
        chemin = Path(sortie)
        if format_export == "json":
            chemin.write_text(json.dumps(bulletin, indent=2, ensure_ascii=False), encoding="utf-8")
        elif format_export == "csv":
            plats = {k: v for k, v in bulletin.items() if not isinstance(v, (dict, list))}
            with chemin.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(plats))
                w.writeheader()
                w.writerow(plats)
        else:
            raise ValueError(f"format inconnu : {format_export}")
        if verbose:
            print(f"export {format_export} vers {chemin}")

    return bulletin
