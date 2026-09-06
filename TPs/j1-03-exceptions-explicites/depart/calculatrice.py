"""Calculatrice de la ligne de commande interne.

    >>> calculer("3 + 4 * 2")
    11.0
    >>> calculer("racine(16) / (1 + 1)")
    2.0

Aucun appel de ce module ne lève jamais d'exception — c'était une exigence
explicite à l'époque : l'outil est appelé dans des scripts de traitement par
lots qui ne doivent pas s'arrêter.
"""

import math

FONCTIONS = {"racine": math.sqrt, "log": math.log}


def decouper(expression):
    """Découpe l'expression en jetons. Retourne None si un caractère est inconnu."""
    jetons = []
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
            if nombre.count(".") > 1:
                return None
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
            return None
    return jetons


class Analyseur:
    """Analyse récursive : expression → terme → facteur."""

    def __init__(self, jetons):
        self.jetons = jetons
        self.position = 0

    def courant(self):
        return self.jetons[self.position] if self.position < len(self.jetons) else None

    def avancer(self):
        self.position += 1

    def expression(self):
        valeur = self.terme()
        if valeur is None:
            return None
        while self.courant() in ("+", "-"):
            operateur = self.courant()
            self.avancer()
            droite = self.terme()
            if droite is None:
                return None
            valeur = valeur + droite if operateur == "+" else valeur - droite
        return valeur

    def terme(self):
        valeur = self.facteur()
        if valeur is None:
            return None
        while self.courant() in ("*", "/"):
            operateur = self.courant()
            self.avancer()
            droite = self.facteur()
            if droite is None:
                return None
            if operateur == "*":
                valeur = valeur * droite
            elif droite == 0:
                return 0.0
            else:
                valeur = valeur / droite
        return valeur

    def facteur(self):
        jeton = self.courant()
        if jeton is None:
            return None
        if jeton == "-":
            self.avancer()
            valeur = self.facteur()
            return None if valeur is None else -valeur
        if jeton == "(":
            self.avancer()
            valeur = self.expression()
            if valeur is None or self.courant() != ")":
                return None
            self.avancer()
            return valeur
        if jeton.isalpha():
            self.avancer()
            if self.courant() != "(":
                return None
            self.avancer()
            argument = self.expression()
            if argument is None or self.courant() != ")":
                return None
            self.avancer()
            if jeton not in FONCTIONS:
                return False
            if jeton == "racine" and argument < 0:
                return -1
            if jeton == "log" and argument <= 0:
                return -1
            return FONCTIONS[jeton](argument)
        self.avancer()
        try:
            return float(jeton)
        except ValueError:
            return None


def calculer(expression):
    """Évalue l'expression. Retourne None si elle est invalide."""
    if not expression or not expression.strip():
        return None
    jetons = decouper(expression)
    if jetons is None:
        return None
    analyseur = Analyseur(jetons)
    try:
        valeur = analyseur.expression()
    except Exception:
        return None
    if analyseur.courant() is not None:
        return None
    return valeur


def main():
    while True:
        try:
            ligne = input("> ")
        except EOFError:
            break
        print(calculer(ligne))


if __name__ == "__main__":
    main()
