"""Moteur de la calculatrice de bureau — module historique.

Écrit il y a six ans pour évaluer « 2 + 2 ». Gère aujourd'hui les fonctions,
la mémoire (M+, MR, MC), le pourcentage, les degrés et les radians, la
précision d'affichage et un journal sur disque. Modifié par neuf personnes.
Fonctionne. Aucun test. Personne ne le refactorise.
"""

import math
import re
from pathlib import Path

PRECISION_DEFAUT = 4
MODES = ("degres", "radians")
JETON = re.compile(r"\d+(?:\.\d+)?|[A-Za-z_]+|[-+*/^%()]")
FONCTIONS = {"sqrt", "sin", "cos", "tan", "log", "ln", "abs"}
CONSTANTES = {"pi": math.pi, "e": math.e}


class ErreurCalcul(Exception):
    """L'expression ne peut pas être évaluée."""


class Calculatrice:
    """Une calculatrice avec mémoire, mode angulaire et journal optionnel."""

    def __init__(self, precision=PRECISION_DEFAUT, mode="degres", journal=None):
        if mode not in MODES:
            raise ValueError(f"mode inconnu : {mode}")
        self.precision = precision
        self.mode = mode
        self.memoire = 0.0
        self.derniere_valeur = 0.0
        self.journal = Path(journal) if journal else None
        self.nb_calculs = 0

    # --- mémoire --------------------------------------------------------------
    def memoire_plus(self):
        self.memoire += self.derniere_valeur

    def memoire_rappel(self):
        return self.memoire

    def memoire_effacer(self):
        self.memoire = 0.0

    # --- évaluation ------------------------------------------------------------
    def calculer(self, expression, verbose=False):
        """Évalue une expression et retourne le résultat arrondi."""
        if not expression or not expression.strip():
            raise ErreurCalcul("expression vide")
        jetons = JETON.findall(expression)
        if "".join(jetons).replace(" ", "") != expression.replace(" ", ""):
            raise ErreurCalcul(f"caractère inattendu dans : {expression!r}")

        # --- substitutions ---------------------------------------------------
        traduits = []
        for jeton in jetons:
            if jeton == "MR":
                traduits.append(repr(self.memoire))
            elif jeton == "ans":
                traduits.append(repr(self.derniere_valeur))
            elif jeton in CONSTANTES:
                traduits.append(repr(CONSTANTES[jeton]))
            elif jeton == "^":
                traduits.append("**")
            elif jeton == "%":
                traduits.append("/100")
            elif jeton in FONCTIONS:
                traduits.append(f"_f_{jeton}")
            elif re.fullmatch(r"[A-Za-z_]+", jeton):
                raise ErreurCalcul(f"identifiant inconnu : {jeton}")
            else:
                traduits.append(jeton)
        code = " ".join(traduits)

        # --- environnement d'évaluation ---------------------------------------
        def angle(x):
            return math.radians(x) if self.mode == "degres" else x

        environnement = {
            "__builtins__": {},
            "_f_sqrt": math.sqrt,
            "_f_sin": lambda x: math.sin(angle(x)),
            "_f_cos": lambda x: math.cos(angle(x)),
            "_f_tan": lambda x: math.tan(angle(x)),
            "_f_log": math.log10,
            "_f_ln": math.log,
            "_f_abs": abs,
        }
        try:
            valeur = eval(code, environnement)  # noqa: S307 — historique, à remplacer un jour
        except ZeroDivisionError:
            raise ErreurCalcul("division par zéro") from None
        except (SyntaxError, TypeError, ValueError, OverflowError) as e:
            raise ErreurCalcul(f"expression invalide : {expression!r} ({e})") from e
        if isinstance(valeur, complex):
            raise ErreurCalcul("résultat complexe")

        # --- résultat --------------------------------------------------------------
        resultat = round(float(valeur), self.precision)
        self.derniere_valeur = resultat
        self.nb_calculs += 1
        if self.journal is not None:
            with self.journal.open("a", encoding="utf-8") as f:
                f.write(f"{expression} = {resultat}\n")
        if verbose:
            print(f"{expression} = {resultat}")
        return resultat

    def formater(self, valeur):
        """Affichage : entier si possible, sinon précision courante."""
        if float(valeur).is_integer():
            return str(int(valeur))
        return f"{valeur:.{self.precision}f}".rstrip("0")
