"""Export du bulletin : la sérialisation est pure, l'écriture est à part."""

import csv
import io
import json
from pathlib import Path

from scolaire.modele import ErreurBulletin


def en_json(bulletin: dict) -> str:
    return json.dumps(bulletin, indent=2, ensure_ascii=False)


def en_csv(bulletin: dict) -> str:
    """Une ligne, colonnes scalaires seulement (les listes et dicts sont omis)."""
    plats = {k: v for k, v in bulletin.items() if not isinstance(v, dict | list)}
    tampon = io.StringIO()
    ecrivain = csv.DictWriter(tampon, fieldnames=list(plats), lineterminator="\r\n")
    ecrivain.writeheader()
    ecrivain.writerow(plats)
    return tampon.getvalue()


FORMATS = {"json": en_json, "csv": en_csv}


def exporter(bulletin: dict, chemin: Path, format_export: str = "json") -> Path:
    try:
        serialiser = FORMATS[format_export]
    except KeyError:
        raise ErreurBulletin(f"format inconnu : {format_export}") from None
    chemin = Path(chemin)
    chemin.write_text(serialiser(bulletin), encoding="utf-8", newline="")
    return chemin
