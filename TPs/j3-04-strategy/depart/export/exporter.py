"""Export de la todo-list.

Historique, lisible dans la cascade ci-dessous : le format texte au départ, puis
CSV pour le tableur du service, puis JSON pour l'interface web, puis Markdown
pour le wiki, puis les options `entete` et `compact` réclamées par deux équipes.
"""

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Tache:
    titre: str
    priorite: str = "normale"
    terminee: bool = False


def exporter(taches: list[Tache], format: str = "texte", entete: bool = True, compact: bool = False) -> str:
    if format == "texte":
        lignes = [f"[{'x' if t.terminee else ' '}] {t.titre} ({t.priorite})" for t in taches]
        if entete:
            lignes.insert(0, f"{len(taches)} tâches")
        return "\n".join(lignes) + "\n"
    elif format == "csv":
        lignes = []
        if entete:
            lignes.append("titre;priorite;terminee")
        for t in taches:
            lignes.append(f"{t.titre};{t.priorite};{int(t.terminee)}")
        return "\n".join(lignes) + "\n"
    elif format == "json":
        donnees = [{"titre": t.titre, "priorite": t.priorite, "terminee": t.terminee} for t in taches]
        if compact:
            return json.dumps(donnees, ensure_ascii=False, separators=(",", ":")) + "\n"
        return json.dumps(donnees, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        lignes = ["| Titre | Priorité | Fait |", "|---|---|---|"] if entete else []
        for t in taches:
            lignes.append(f"| {t.titre} | {t.priorite} | {'✓' if t.terminee else ''} |")
        return "\n".join(lignes) + "\n"
    else:
        raise ValueError(format)
