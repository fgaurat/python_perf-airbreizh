"""Exécute localement les jobs décrits dans un `.gitlab-ci.yml`.

Ce n'est pas un runner GitLab : il ne gère ni les artifacts, ni le cache, ni
les images Docker. Il fait une seule chose, et c'est celle qui compte pour
déboguer une pipeline : **exécuter les commandes des jobs, dans l'ordre des
stages, en respectant les codes de retour**.

Usage :
    python outils/simuler_pipeline.py [chemin/vers/.gitlab-ci.yml]
"""

import subprocess
import sys
from pathlib import Path

import yaml

CLES_RESERVEES = {
    "stages",
    "variables",
    "default",
    "image",
    "cache",
    "before_script",
    "after_script",
    "include",
    "workflow",
}


def charger(chemin: Path) -> dict:
    """Charge le fichier de pipeline.

    Raises:
        SystemExit: fichier absent ou YAML invalide.
    """
    if not chemin.exists():
        sys.exit(f"✗ {chemin} introuvable")
    try:
        contenu = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        sys.exit(f"✗ {chemin} : YAML invalide — {e}")
    if not isinstance(contenu, dict):
        sys.exit(f"✗ {chemin} : un objet YAML est attendu")
    return contenu


def jobs_par_stage(pipeline: dict) -> dict[str, list[tuple[str, dict]]]:
    """Regroupe les jobs par stage, dans l'ordre déclaré par `stages`."""
    stages = pipeline.get("stages", ["test"])
    groupes: dict[str, list[tuple[str, dict]]] = {stage: [] for stage in stages}
    for nom, corps in pipeline.items():
        if nom in CLES_RESERVEES or nom.startswith(".") or not isinstance(corps, dict):
            continue
        stage = corps.get("stage", "test")
        if stage not in groupes:
            groupes[stage] = []
        groupes[stage].append((nom, corps))
    return groupes


def commandes(pipeline: dict, corps: dict) -> list[str]:
    """Commandes d'un job : `before_script` global puis `script` du job."""
    defaut = pipeline.get("default", {})
    avant = corps.get("before_script", defaut.get("before_script", []))
    return list(avant) + list(corps.get("script", []))


def executer(nom: str, lignes: list[str], racine: Path) -> bool:
    """Exécute les commandes d'un job. Renvoie True si toutes réussissent."""
    print(f"\n  ┌─ job « {nom} »")
    for ligne in lignes:
        print(f"  │  $ {ligne}")
        resultat = subprocess.run(ligne, shell=True, cwd=racine, check=False)
        if resultat.returncode != 0:
            print(f"  └─ ✗ ÉCHEC (code {resultat.returncode})")
            return False
    print("  └─ ✓ OK")
    return True


def main() -> int:
    chemin = Path(sys.argv[1] if len(sys.argv) > 1 else ".gitlab-ci.yml")
    racine = chemin.resolve().parent
    pipeline = charger(chemin)
    groupes = jobs_par_stage(pipeline)

    if not any(groupes.values()):
        sys.exit("✗ aucun job trouvé — avez-vous déclaré `stages` et au moins un job ?")

    echecs = []
    for stage, jobs in groupes.items():
        if not jobs:
            continue
        print(f"\n═══ stage « {stage} » — {len(jobs)} job(s)")
        rouges = [
            nom for nom, corps in jobs if not executer(nom, commandes(pipeline, corps), racine)
        ]
        echecs.extend(rouges)
        if rouges:
            print(f"\n✗ stage « {stage} » en échec : {', '.join(rouges)}")
            print("  Les stages suivants ne sont pas exécutés (comme dans GitLab).")
            break

    print()
    if echecs:
        print(f"✗ PIPELINE EN ÉCHEC — {len(echecs)} job(s) : {', '.join(echecs)}")
        return 1
    print("✓ PIPELINE VERTE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
