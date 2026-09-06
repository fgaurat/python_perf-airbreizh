"""Conversion entre entiers et chiffres romains.

Décisions prises pendant les cycles TDD (voir le fichier de tests) :

- notation soustractive canonique : 4 → IV, jamais IIII ;
- domaine [1, 3999] : pas de zéro, pas de négatif, pas de barre au-dessus ;
- `arabe` est strict sur la forme canonique (IIII est refusé) mais tolère la
  casse et les espaces autour.
"""

MINIMUM = 1
MAXIMUM = 3999

TABLE: list[tuple[int, str]] = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]


class ErreurRomain(Exception):
    """Racine des erreurs de conversion."""


class HorsBornes(ErreurRomain):
    """Entier en dehors de [1, 3999]."""


class RomainInvalide(ErreurRomain):
    """Chaîne qui n'est pas un nombre romain canonique."""


def romain(n: int) -> str:
    """Écrit `n` en chiffres romains : romain(1994) == 'MCMXCIV'."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"attendu un int, reçu {type(n).__name__}")
    if not MINIMUM <= n <= MAXIMUM:
        raise HorsBornes(f"{n} : attendu entre {MINIMUM} et {MAXIMUM}")
    morceaux = []
    for valeur, symbole in TABLE:
        compte, n = divmod(n, valeur)
        morceaux.append(symbole * compte)
    return "".join(morceaux)


def arabe(texte: str) -> int:
    """Lit un nombre romain canonique : arabe('MCMXCIV') == 1994."""
    propre = texte.strip().upper()
    if not propre:
        raise RomainInvalide("chaîne vide")
    reste, total = propre, 0
    for valeur, symbole in TABLE:
        while reste.startswith(symbole):
            total += valeur
            reste = reste[len(symbole) :]
    if reste:
        position = len(propre) - len(reste)
        raise RomainInvalide(f"{texte!r} : symbole inattendu {reste[0]!r} en position {position}")
    if total > MAXIMUM:
        raise RomainInvalide(f"{texte!r} vaut {total}, au-delà de {MAXIMUM}")
    if romain(total) != propre:
        raise RomainInvalide(f"{texte!r} n'est pas la forme canonique de {total} ({romain(total)})")
    return total
