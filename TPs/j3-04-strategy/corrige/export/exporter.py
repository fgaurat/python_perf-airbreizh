"""Export de la todo-list : un formateur par format, un registre, un point d'entrée.

Ajouter un format = écrire une fonction et l'inscrire dans `FORMATS`.
`exporter` n'a plus jamais à être rouverte.
"""

import csv
import io
import json
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Tache:
    titre: str
    priorite: str = "normale"
    terminee: bool = False


class ErreurExport(Exception):
    """Racine des erreurs d'export."""


class FormatInconnu(ErreurExport):
    pass


Formateur = Callable[[list[Tache]], str]


# --- Un formateur par format : chacun rend des lignes, sans saut de ligne final -------------


def en_texte(taches: list[Tache]) -> str:
    lignes = [f"{len(taches)} tâches"]
    lignes += [f"[{'x' if t.terminee else ' '}] {t.titre} ({t.priorite})" for t in taches]
    return "\n".join(lignes)


def en_csv(taches: list[Tache]) -> str:
    tampon = io.StringIO()
    ecrivain = csv.writer(tampon, delimiter=";", lineterminator="\n")
    ecrivain.writerow(["titre", "priorite", "terminee"])
    ecrivain.writerows([t.titre, t.priorite, int(t.terminee)] for t in taches)
    return tampon.getvalue().rstrip("\n")


def en_json(taches: list[Tache]) -> str:
    donnees = [{"titre": t.titre, "priorite": t.priorite, "terminee": t.terminee} for t in taches]
    return json.dumps(donnees, ensure_ascii=False, indent=2)


def en_json_compact(taches: list[Tache]) -> str:
    donnees = [{"titre": t.titre, "priorite": t.priorite, "terminee": t.terminee} for t in taches]
    return json.dumps(donnees, ensure_ascii=False, separators=(",", ":"))


def en_markdown(taches: list[Tache]) -> str:
    lignes = ["| Titre | Priorité | Fait |", "|---|---|---|"]
    for t in taches:
        titre = t.titre.replace("|", "\\|")
        lignes.append(f"| {titre} | {t.priorite} | {'✓' if t.terminee else ''} |")
    return "\n".join(lignes)


# --- Le registre et le point d'entrée ---------------------------------------------------------

FORMATS: dict[str, Formateur] = {
    "texte": en_texte,
    "csv": en_csv,
    "json": en_json,
    "json-compact": en_json_compact,
    "markdown": en_markdown,
}


def exporter_avec(taches: list[Tache], formateur: Formateur) -> str:
    """Le saut de ligne final est ajouté ici, une seule fois, pour tous les formats."""
    return formateur(taches) + "\n"


def exporter(taches: list[Tache], format: str = "texte") -> str:
    try:
        formateur = FORMATS[format]
    except KeyError:
        raise FormatInconnu(f"{format!r} — formats disponibles : {sorted(FORMATS)}") from None
    return exporter_avec(taches, formateur)
