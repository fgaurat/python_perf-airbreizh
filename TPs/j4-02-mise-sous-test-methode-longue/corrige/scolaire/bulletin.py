"""Génération du bulletin trimestriel — version découpée.

`generer_bulletin` n'écrit plus rien et ne calcule plus rien : elle appelle les
règles de `regles.py` et assemble le dictionnaire. L'export est dans `export.py`.
"""

from pathlib import Path

from scolaire import regles
from scolaire.export import exporter


def generer_bulletin(
    eleve: dict, trimestre: str, sortie: str | Path | None = None, format_export: str = "json"
) -> dict:
    classe = regles.valider_eleve(eleve)
    regles.analyser_trimestre(trimestre)

    matieres = regles.moyennes_par_matiere(eleve.get("notes", {}))
    moyennes = {m.matiere: m.moyenne for m in matieres}
    generale = regles.moyenne_generale(moyennes)
    bonus = regles.bonus_options(moyennes)
    finale = generale + bonus

    la_mention = regles.mention(finale)
    absences = regles.compter_absences(eleve.get("absences", []))
    la_tendance = regles.tendance(finale, eleve.get("moyenne_precedente", 0.0))
    autres = eleve.get("moyennes_classe", [])

    bulletin = {
        "id": eleve["id"],
        "nom": eleve.get("nom", ""),
        "classe": classe,
        "trimestre": trimestre,
        "matieres": [
            {"matiere": m.matiere, "moyenne": m.moyenne, "nb_notes": m.nb_notes} for m in matieres
        ],
        "moyenne_generale": round(generale, 2),
        "bonus_options": round(bonus, 2),
        "moyenne_finale": round(finale, 2),
        "mention": la_mention,
        "rang": regles.rang(finale, autres),
        "effectif": len(autres) + 1,
        "demi_journees_absence": absences.demi_journees,
        "avertissement_assiduite": absences.avertissement,
        "tendance": la_tendance,
        "appreciation": regles.appreciation(la_mention, la_tendance, absences.avertissement),
    }
    if sortie is not None:
        exporter(bulletin, Path(sortie), format_export)
    return bulletin
