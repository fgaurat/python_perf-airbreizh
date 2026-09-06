"""Calculatrice de la ligne de commande interne.

    >>> calculer("3 + 4 * 2")
    11.0
    >>> calculer("racine(16) / (1 + 1)")
    2.0

Toute expression invalide ou tout calcul impossible lève une `ErreurCalcul`,
avec un message qui dit **où** et **pourquoi**. C'est à l'appelant — le script
de traitement par lots, par exemple — de décider s'il s'arrête ou s'il passe à
la ligne suivante.
"""

import math
from collections.abc import Callable

FONCTIONS: dict[str, Callable[[float], float]] = {"racine": math.sqrt, "log": math.log}


# --- Hiérarchie ---------------------------------------------------------------


class ErreurCalcul(Exception):
    """Racine des erreurs de la calculatrice."""


class ExpressionInvalide(ErreurCalcul):
    """L'expression est mal formée : elle ne peut pas être analysée."""


class FonctionInconnue(ExpressionInvalide):
    """Un identifiant ne correspond à aucune fonction connue."""


class OperationImpossible(ErreurCalcul):
    """L'expression est valide, mais le calcul n'a pas de résultat."""


class DivisionParZero(OperationImpossible):
    pass


class HorsDomaine(OperationImpossible):
    """Argument hors du domaine de définition d'une fonction."""


# --- Découpage ----------------------------------------------------------------


def decouper(expression: str) -> list[str]:
    """Découpe l'expression en jetons."""
    jetons: list[str] = []
    i = 0
    while i < len(expression):
        c = expression[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == "."):
                j += 1
            nombre = expression[i:j]
            if nombre.count(".") > 1 or nombre == ".":
                raise ExpressionInvalide(f"position {i} : nombre malformé {nombre!r}")
            jetons.append(nombre)
            i = j
        elif c.isalpha():
            j = i
            while j < len(expression) and expression[j].isalpha():
                j += 1
            jetons.append(expression[i:j])
            i = j
        elif c in "+-*/()":
            jetons.append(c)
            i += 1
        else:
            raise ExpressionInvalide(f"position {i} : caractère inattendu {c!r}")
    return jetons


# --- Analyse ------------------------------------------------------------------


class Analyseur:
    """Analyse récursive : expression → terme → facteur."""

    def __init__(self, jetons: list[str]) -> None:
        self.jetons = jetons
        self.position = 0

    def courant(self) -> str | None:
        return self.jetons[self.position] if self.position < len(self.jetons) else None

    def avancer(self) -> None:
        self.position += 1

    def attendre(self, jeton: str) -> None:
        if self.courant() != jeton:
            trouve = self.courant() or "fin de l'expression"
            message = f"jeton {self.position} : attendu {jeton!r}, trouvé {trouve!r}"
            raise ExpressionInvalide(message)
        self.avancer()

    def expression(self) -> float:
        valeur = self.terme()
        while self.courant() in ("+", "-"):
            operateur = self.courant()
            self.avancer()
            droite = self.terme()
            valeur = valeur + droite if operateur == "+" else valeur - droite
        return valeur

    def terme(self) -> float:
        valeur = self.facteur()
        while self.courant() in ("*", "/"):
            operateur = self.courant()
            self.avancer()
            droite = self.facteur()
            if operateur == "*":
                valeur = valeur * droite
            else:
                try:
                    valeur = valeur / droite
                except ZeroDivisionError as e:
                    raise DivisionParZero(f"{valeur:g} / 0") from e
        return valeur

    def facteur(self) -> float:
        jeton = self.courant()
        if jeton is None:
            raise ExpressionInvalide("fin de l'expression : attendu un nombre, une fonction ou '('")
        if jeton == "-":
            self.avancer()
            return -self.facteur()
        if jeton == "(":
            self.avancer()
            valeur = self.expression()
            self.attendre(")")
            return valeur
        if jeton.isalpha():
            return self.appel_de_fonction(jeton)
        if jeton in "+*/)":
            raise ExpressionInvalide(f"jeton {self.position} : opérande attendu, trouvé {jeton!r}")
        self.avancer()
        return float(jeton)

    def appel_de_fonction(self, nom: str) -> float:
        if nom not in FONCTIONS:
            raise FonctionInconnue(f"fonction inconnue {nom!r} (disponibles : {sorted(FONCTIONS)})")
        self.avancer()
        self.attendre("(")
        argument = self.expression()
        self.attendre(")")
        try:
            return FONCTIONS[nom](argument)
        except ValueError as e:
            raise HorsDomaine(f"{nom}({argument:g}) n'est pas défini") from e


def calculer(expression: str) -> float:
    """Évalue l'expression, ou lève une `ErreurCalcul` qui explique pourquoi c'est impossible."""
    if not expression.strip():
        raise ExpressionInvalide("expression vide")
    analyseur = Analyseur(decouper(expression))
    valeur = analyseur.expression()
    if (restant := analyseur.courant()) is not None:
        raise ExpressionInvalide(f"jeton {analyseur.position} : {restant!r} inattendu après la fin")
    return valeur


def main() -> None:
    while True:
        try:
            ligne = input("> ")
        except EOFError:
            break
        try:
            print(calculer(ligne))
        except ErreurCalcul as e:
            print(f"erreur : {e}")


if __name__ == "__main__":
    main()
