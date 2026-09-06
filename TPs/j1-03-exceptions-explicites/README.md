# TP j1-03 — Remplacer les erreurs silencieuses

**Durée : 30 min**

## Contexte

`depart/calculatrice.py` évalue des expressions arithmétiques :
`calculer("3 + 4 * 2")` renvoie `11.0`, `calculer("racine(16) / 2")` renvoie
`2.0`. Il est appelé par des scripts de traitement par lots qui lisent des
milliers de lignes de formules.

Lisez la docstring du module : *« Aucun appel de ce module ne lève jamais
d'exception — c'était une exigence explicite à l'époque : l'outil est appelé
dans des scripts qui ne doivent pas s'arrêter. »*

L'exigence a été respectée. Voici ce qu'elle a produit :

| Situation | Ce que renvoie `calculer` |
|---|---|
| Expression vide | `None` |
| Caractère inconnu (`3 $ 4`) | `None` |
| Nombre malformé (`3.4.5`) | `None` |
| Parenthèse non fermée (`(3 + 4`) | `None` |
| Opérateur sans opérande (`3 +`) | `None` |
| Jetons en trop (`3 4`) | `None` |
| Division par zéro (`10 / 0`) | `0.0` |
| Racine d'un négatif, log d'un nombre ≤ 0 | `-1` |
| Fonction inconnue (`sinus(1)`) | `False` |

Neuf causes différentes, trois valeurs de retour. **Le traitement par lots ne
s'arrête pas. Il produit des résultats faux.**

Pire : les sentinelles **participent au calcul**. Essayez :

```python
>>> calculer("10 / 0 + 5")
5.0
>>> calculer("racine(-4) + 10")
9.0
>>> calculer("sinus(1) + 3")
3.0
```

Et `calculer("log(1)")` renvoie `0.0` — un résultat juste, indiscernable d'une
division par zéro.

## Objectif

Rendre chaque échec explicite, sans perdre la cause d'origine.

## Étapes

1. **Construire la hiérarchie** (5 min). Une racine propre au module, et des
   exceptions filles pour chaque famille de problème :

   ```python
   class ErreurCalcul(Exception):
       """Racine des erreurs de la calculatrice."""


   class ExpressionInvalide(ErreurCalcul):
       """Mal formée : impossible à analyser."""


   class OperationImpossible(ErreurCalcul):
       """Bien formée, mais sans résultat : division par zéro, racine d'un négatif…"""
   ```

   > Pourquoi une racine ? Pour que le script de traitement par lots puisse
   > écrire `except ErreurCalcul` sans jamais recourir à `except Exception`.
   > Pourquoi deux branches ? Parce qu'il ne réagira pas de la même façon à
   > une faute de frappe et à une division par zéro.

2. **Reprendre `decouper`** (5 min). Remplacez les deux `return None` par une
   `ExpressionInvalide` dont le message contient **la position et le caractère
   fautif** :

   ```
   position 2 : caractère inattendu '$'
   ```

3. **Reprendre `Analyseur`** (10 min). Toutes les méthodes retournent
   désormais *toujours* un `float`. Supprimez chaque `if … is None: return None`
   — c'est le plus gros gain de lisibilité du TP. Pour la division par zéro,
   laissez Python lever, et traduisez :

   ```python
   try:
       valeur = valeur / droite
   except ZeroDivisionError as e:
       raise DivisionParZero(f"{valeur:g} / 0") from e
   ```

   Même chose pour `math.sqrt(-4)` et `math.log(0)`, qui lèvent un `ValueError`
   à traduire en `HorsDomaine`.

4. **Reprendre `calculer`** (5 min). Supprimez le `except Exception` et le
   `return None`. Annotez la signature : `calculer(expression: str) -> float`.
   Elle est désormais honnête.

5. **Reprendre `main`** (5 min). C'est **lui** qui attrape `ErreurCalcul`, pour
   afficher `erreur : …` et passer à la ligne suivante. Le module signale ;
   l'application décide.

## Critères de réussite

- Le module ne contient plus aucun `except Exception`, `return None`, `-1`
  ni `False` en cas d'erreur.
- Chaque `raise` à l'intérieur d'un `except` utilise `from`.
- Chacune des neuf situations du tableau ci-dessus produit un message
  **différent et lisible sans ouvrir le code**.
- `calculer("10 / 0 + 5")` lève une exception — il ne renvoie plus `5.0`.
- Un appelant peut attraper toutes vos erreurs avec un seul `except`.

## Discussion (5 min, en groupe)

L'exigence d'origine — « ne jamais lever d'exception » — n'était pas absurde :
elle protégeait un traitement par lots qui ne devait pas s'arrêter à la
première formule fausse.

Comment satisfaire ce besoin *réel* sans erreurs silencieuses ?

> Piste : ce n'est pas à la calculatrice de décider si une formule fausse doit
> interrompre le lot. C'est à la boucle du script — qui, elle, peut attraper
> `ErreurCalcul`, journaliser la ligne fautive avec son message, et poursuivre
> en connaissance de cause. **La librairie signale ; l'application décide.**

## Corrigé

`corrige/` — module et 30 tests.

```bash
uv run pytest j1-03-exceptions-explicites/corrige
```
