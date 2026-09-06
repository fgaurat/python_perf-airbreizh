"""Transport HTTP minimal : une URL entre, un dictionnaire sort."""

import json
import urllib.request


def get(url: str) -> dict:
    """Appel réseau réel. Lève `OSError` (ou une sous-classe) en cas de panne."""
    with urllib.request.urlopen(url, timeout=5) as reponse:  # noqa: S310
        return json.load(reponse)
