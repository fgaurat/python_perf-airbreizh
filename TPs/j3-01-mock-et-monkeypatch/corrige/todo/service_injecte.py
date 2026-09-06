"""Version 3 : les dépendances sont des paramètres, avec des défauts de production.

`taches_en_retard("site-web")` se comporte exactement comme dans `service.py`.
Dans un test, on passe un transport et une horloge factices — sans `patch`,
sans `monkeypatch`, sans chaîne de module.
"""

from collections.abc import Callable
from datetime import date

from todo.service import ServiceIndisponible, interpreter, url_base
from todo.transport import get as get_reel

Transport = Callable[[str], dict]
Horloge = Callable[[], date]


def taches_en_retard(
    projet: str,
    transport: Transport = get_reel,
    url: str | None = None,
    horloge: Horloge = date.today,
) -> list[str]:
    base = url_base() if url is None else url.rstrip("/")
    try:
        charge = transport(f"{base}/projets/{projet}/taches")
    except OSError as e:
        raise ServiceIndisponible(f"projet {projet} : {e}") from e
    return interpreter(charge, horloge())
