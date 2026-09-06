"""Carnet d'adresses persisté en JSON, avec sauvegardes tournantes.

Le carnet est un fichier `carnet.json` contenant une liste de contacts. Avant
chaque modification importante, `sauvegarder` décale les copies existantes
(`carnet.json.1` → `.2` → `.3` → …) puis copie le carnet courant en `.1`.
`purger_sauvegardes` supprime les copies les plus anciennes au-delà d'un
nombre à conserver.
"""

import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path


class ErreurCarnet(Exception):
    """Racine des erreurs du carnet."""


class FichierCorrompu(ErreurCarnet):
    """Le fichier existe mais son contenu n'est pas un carnet valide."""


class ContactExistant(ErreurCarnet):
    """Un contact porte déjà cette adresse e-mail."""


@dataclass(frozen=True)
class Contact:
    nom: str
    email: str
    telephone: str = ""


def lire(chemin: Path) -> list[Contact]:
    """Charge le carnet. Un fichier absent ou vide est un carnet vide."""
    if not chemin.exists():
        return []
    texte = chemin.read_text(encoding="utf-8")
    if not texte.strip():
        return []
    try:
        brut = json.loads(texte)
    except json.JSONDecodeError as e:
        raise FichierCorrompu(f"{chemin.name} ligne {e.lineno} : {e.msg}") from e
    if not isinstance(brut, list):
        raise FichierCorrompu(f"{chemin.name} : attendu une liste, trouvé {type(brut).__name__}")
    contacts = []
    for indice, element in enumerate(brut, start=1):
        try:
            contacts.append(Contact(**element))
        except TypeError as e:
            raise FichierCorrompu(f"{chemin.name} contact {indice} : {e}") from e
    return contacts


def ecrire(chemin: Path, contacts: list[Contact]) -> None:
    """Remplace le carnet par la liste donnée."""
    donnees = [asdict(c) for c in contacts]
    chemin.write_text(json.dumps(donnees, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ajouter(chemin: Path, contact: Contact) -> list[Contact]:
    """Ajoute un contact et réécrit le carnet. L'e-mail est unique, quelle que soit sa casse."""
    contacts = lire(chemin)
    if any(c.email.lower() == contact.email.lower() for c in contacts):
        raise ContactExistant(f"un contact a déjà l'adresse {contact.email}")
    contacts.append(contact)
    ecrire(chemin, contacts)
    return contacts


def sauvegardes(chemin: Path) -> list[Path]:
    """Les copies `carnet.json.N` existantes, de la plus récente (.1) à la plus ancienne."""
    motif = re.compile(re.escape(chemin.name) + r"\.(\d+)$")
    numerotees = []
    for candidat in chemin.parent.iterdir():
        if correspondance := motif.match(candidat.name):
            numerotees.append((int(correspondance.group(1)), candidat))
    return [p for _, p in sorted(numerotees)]


def sauvegarder(chemin: Path) -> Path:
    """Décale les copies existantes d'un cran, puis copie le carnet courant en `.1`."""
    for copie in reversed(sauvegardes(chemin)):
        numero = int(copie.suffix[1:])
        copie.rename(chemin.with_name(f"{chemin.name}.{numero + 1}"))
    destination = chemin.with_name(f"{chemin.name}.1")
    shutil.copyfile(chemin, destination)
    return destination


def purger_sauvegardes(chemin: Path, garder: int) -> list[Path]:
    """Supprime les copies au-delà des `garder` plus récentes. Retourne les chemins supprimés."""
    if garder < 0:
        raise ValueError(f"garder = {garder} : attendu >= 0")
    supprimees = sauvegardes(chemin)[garder:]
    for copie in supprimees:
        copie.unlink()
    return supprimees
