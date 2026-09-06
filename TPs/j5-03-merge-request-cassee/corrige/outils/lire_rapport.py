"""Affiche un rapport JUnit comme le fait l'onglet « Tests » d'une merge request.

Usage :
    python outils/lire_rapport.py rapport.xml
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    chemin = Path(sys.argv[1] if len(sys.argv) > 1 else "rapport.xml")
    if not chemin.exists():
        sys.exit(f"✗ {chemin} introuvable — lancez d'abord pytest --junitxml={chemin}")

    racine = ET.parse(chemin).getroot()
    suites = racine.findall("testsuite") or [racine]

    total = echecs = erreurs = ignores = 0
    details: list[tuple[str, str, str]] = []

    for suite in suites:
        total += int(suite.get("tests", 0))
        echecs += int(suite.get("failures", 0))
        erreurs += int(suite.get("errors", 0))
        ignores += int(suite.get("skipped", 0))
        for cas in suite.findall("testcase"):
            for nature in ("failure", "error"):
                noeud = cas.find(nature)
                if noeud is not None:
                    details.append(
                        (cas.get("classname", ""), cas.get("name", ""), noeud.get("message", ""))
                    )

    print(f"\n{'═' * 72}")
    print(f"  {total} tests · {echecs} échec(s) · {erreurs} erreur(s) · {ignores} ignoré(s)")
    print("═" * 72)

    if not details:
        print("\n  ✓ Tous les tests passent.\n")
        return 0

    for classe, nom, message in details:
        print(f"\n  ✗ {nom}")
        print(f"    dans {classe}")
        premiere_ligne = message.strip().splitlines()[0] if message.strip() else "(sans message)"
        print(f"    {premiere_ligne[:200]}")

    print("\n  Pour reproduire en local :")
    print(f'    uv run --frozen pytest -k "{details[0][1]}" -x\n')
    return 1


if __name__ == "__main__":
    sys.exit(main())
