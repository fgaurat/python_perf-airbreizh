#!/usr/bin/env python3
"""Construit le support complet de la formation Python avancé (qualité, TDD, CI/CD).

1. Concatène les chapitres slides/NN-*.md en un seul fichier Marp
   (le frontmatter de chaque chapitre est remplacé par une directive
   <!-- header: ... --> pour conserver l'en-tête par chapitre).
2. Optionnel (--check) : mesure chaque slide dans Chrome headless et
   signale celles dont le contenu déborde de la zone visible.
3. Génère le PDF via Marp CLI (npx @marp-team/marp-cli).

Usage :
    python3 build.py            # concatène + PDF
    python3 build.py --check    # concatène + contrôle de débordement + PDF
                                #   (PDF annulé si une slide déborde)
    python3 build.py --no-pdf   # concatène seulement
    python3 build.py --html     # concatène + HTML (aperçu rapide)
"""

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
SLIDES_DIR = ROOT / "slides"
OUTPUT_MD = SLIDES_DIR / "python-avance-complet.md"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADER_LINE = re.compile(r'^header:\s*"(.*)"\s*$', re.MULTILINE)

GLOBAL_FRONTMATTER = """\
---
marp: true
theme: your-theme
paginate: true
title: "Python avancé — Qualité, TDD, Design patterns, CI/CD"
header: "Python avancé — Qualité, TDD, CI/CD"
---
"""

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# Script injecté dans le HTML : mesure chaque <section> et dépose le
# rapport dans un attribut du <body>, récupéré ensuite via --dump-dom.
MEASURE_SCRIPT = """
<script>
window.addEventListener('load', () => {
  const sections = [...document.querySelectorAll('svg[data-marpit-svg] > foreignObject > section')];
  const report = sections.map((s, i) => {
    const overflow = s.scrollHeight - s.clientHeight;
    if (overflow <= 4) return null;                      // tolérance de 4px
    const title = (s.querySelector('h1')?.textContent || '(sans titre)').trim();
    return {page: i + 1, overflow, title};
  }).filter(Boolean);
  document.body.setAttribute('data-overflow-report',
    JSON.stringify({total: sections.length, report}));
});
</script>
"""


def concat() -> Path:
    """Assemble les chapitres et écrit le markdown combiné."""
    chapters = sorted(SLIDES_DIR.glob("[0-9][0-9]-*.md"))
    if not chapters:
        sys.exit(f"Aucun chapitre trouvé dans {SLIDES_DIR}")

    parts = []
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        m = FRONTMATTER.match(text)
        if not m:
            sys.exit(f"{chapter.name} : frontmatter introuvable")
        front, body = m.group(1), text[m.end():].strip()

        hm = HEADER_LINE.search(front)
        header = hm.group(1) if hm else "Python avancé — Qualité, TDD, CI/CD"
        parts.append(f'<!-- header: "{header}" -->\n\n{body}')
        print(f"  + {chapter.name}")

    combined = GLOBAL_FRONTMATTER + "\n" + "\n\n---\n\n".join(parts) + "\n"
    OUTPUT_MD.write_text(combined, encoding="utf-8")

    n_slides = combined.count("\n---\n") + 1
    print(f"→ {OUTPUT_MD.relative_to(ROOT)} : {len(chapters)} chapitres, {n_slides} slides")
    return OUTPUT_MD


def render(md_file: Path, fmt: str) -> Path:
    """Convertit le markdown combiné avec Marp CLI."""
    output = md_file.with_suffix(f".{fmt}")
    cmd = [
        "npx", "-y", "@marp-team/marp-cli@latest",
        md_file.name,
        "--theme-set", str(ROOT / "your-theme.css"), str(ROOT / "gradient-blue.css"),
        "--allow-local-files",
        "--html",                       # autorise les <div> de mise en colonnes
        f"--{fmt}",
        "-o", output.name,
    ]
    print(f"→ Marp : génération de {output.name}…")
    subprocess.run(cmd, cwd=SLIDES_DIR, check=True)
    size_mb = output.stat().st_size / 1_000_000
    print(f"✓ {output.relative_to(ROOT)} ({size_mb:.1f} Mo)")
    return output


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    sys.exit("Chrome/Chromium introuvable — impossible de faire le contrôle --check")


def check_overflow(md_file: Path) -> bool:
    """Rend le HTML, mesure chaque slide dans Chrome headless.

    Renvoie True si tout tient, False si au moins une slide déborde.
    """
    html_file = render(md_file, "html")

    # Copie temporaire avec le script de mesure injecté
    content = html_file.read_text(encoding="utf-8")
    content = content.replace("</body>", MEASURE_SCRIPT + "</body>")
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", dir=SLIDES_DIR, delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        dump = subprocess.run(
            [find_chrome(), "--headless=new", "--disable-gpu",
             "--virtual-time-budget=5000", "--dump-dom", tmp_path.as_uri()],
            capture_output=True, text=True, check=True, timeout=120,
        ).stdout
    finally:
        tmp_path.unlink(missing_ok=True)

    m = re.search(r'data-overflow-report="([^"]*)"', dump)
    if not m:
        sys.exit("Rapport de mesure introuvable dans la sortie Chrome")
    data = json.loads(html.unescape(m.group(1)))

    print(f"→ Contrôle de débordement : {data['total']} slides mesurées")
    if not data["report"]:
        print("✓ Aucune slide ne déborde")
        return True

    print(f"✗ {len(data['report'])} slide(s) en débordement :")
    for item in sorted(data["report"], key=lambda x: -x["overflow"]):
        print(f"    page {item['page']:>3} — {item['overflow']:>4}px de trop — {item['title']}")
    print("  Pistes : <!-- _class: dense -->, scinder en 1/2 - 2/2, ou grille 2-3 colonnes.")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="mesure les slides et bloque le PDF si l'une déborde")
    parser.add_argument("--no-pdf", action="store_true",
                        help="concatène seulement, sans générer le PDF")
    parser.add_argument("--html", action="store_true",
                        help="génère aussi la version HTML")
    args = parser.parse_args()

    md_file = concat()

    if args.check and not check_overflow(md_file):
        sys.exit(1)                       # débordements → pas de PDF

    if args.html and not args.check:      # --check a déjà produit le HTML
        render(md_file, "html")
    if not args.no_pdf:
        render(md_file, "pdf")


if __name__ == "__main__":
    main()
