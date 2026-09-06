"""Rend `src/` importable sans installation.

Dans la pipeline, c'est `uv sync` qui installe le package — ce fichier n'existe
que pour permettre de lancer les tests depuis le dépôt sans étape préalable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
