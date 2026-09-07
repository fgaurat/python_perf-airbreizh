# TP 01 : premiers tests pytest sur Rectangle, Cercle et Carre

**Durée : 45 min**

## Contexte

`depart/geo/` reprend les classes du tp1 (`Rectangle`, `Carre`, `Cercle`,
`CalcGeo`), rangées dans un package. Elles n'ont aucun test, à part le premier
que vous trouverez dans `depart/tests/test_rectangle.py`.

Aujourd'hui on les a fait tourner à la main dans `main.py` et on a regardé le
résultat. Le but du TP est de remplacer ce `print` par des tests qui restent.

## Objectif

Mettre en place la structure de tests d'un package, puis écrire une suite qui
documente le comportement réel des classes : cas nominaux, erreurs attendues,
cas limites. Plusieurs de ces cas limites révèlent des bugs ou des décisions
jamais prises.

## Étapes

### 1. La mécanique (5 min)

```bash
cd depart
python -m pytest -v
```

Un test collecté, un test vert. Regardez sa structure Arrange / Act / Assert.
Le fichier `conftest.py` vide à la racine est ce qui permet l'import de `geo`.

Ajoutez trois tests dans `test_rectangle.py` :

- `__eq__` : deux rectangles de mêmes dimensions sont égaux ;
- `build_from_str("2;3")` construit bien un `Rectangle(2, 3)` ;
- le setter `longueur` modifie la surface.

Faites échouer volontairement un test pour voir comment pytest affiche
la différence entre attendu et obtenu.

### 2. Paramétrer (10 min)

Vous allez vouloir tester la surface pour plusieurs dimensions. Pas trois
fonctions `test_surface_1`, `_2`, `_3` : une seule, paramétrée.

```python
import pytest

@pytest.mark.parametrize(
    ("longueur", "largeur", "attendue"),
    [
        pytest.param(2, 3, 6, id="entiers"),
        pytest.param(0, 3, 0, id="largeur_nulle"),
        pytest.param(2.5, 2, 5.0, id="flottant"),
    ],
)
def test_surface(longueur, largeur, attendue):
    assert Rectangle(longueur, largeur).surface == attendue
```

Regardez le rendu avec `python -m pytest -v` puis `--collect-only -q`.

Créez `tests/test_cercle.py`. La surface d'un cercle de rayon 1 vaut `math.pi`.
Celle d'un rayon 2 vaut `12.566370614359172`. Écrivez le test avec le nombre
en dur, puis avec `pytest.approx(4 * math.pi)`. Lequel préférez-vous relire
dans six mois ?

### 3. Les erreurs attendues (10 min)

Le setter `longueur` refuse une valeur négative. Testez-le :

```python
def test_longueur_negative_refusee():
    r = Rectangle(2, 3)
    with pytest.raises(Exception):
        r.longueur = -1
```

Ce test est vert. Il est aussi presque inutile : `pytest.raises(Exception)`
accepte n'importe quelle erreur, y compris une faute de frappe dans le setter.
Essayez : remplacez `raise Exception("Hooooo!")` par `raise Exceptio(...)`.
Le test reste vert.

Créez `geo/erreurs.py` avec une exception métier `DimensionInvalide(ValueError)`,
utilisez-la dans le setter, et resserrez le test avec `pytest.raises(DimensionInvalide)`
et `match=`.

Puis posez-vous les questions suivantes, et répondez-y par des tests :

- `Rectangle(-2, 3)` est-il refusé ? (regardez `__init__` : il n'appelle pas le setter)
- et `r.largeur = -1` ?
- et une longueur de `0` ? C'est une décision, pas une évidence : prenez-la, écrivez-la.

### 4. Les cas limites qui posent des questions (10 min)

Écrivez un test pour chacune de ces situations. Certaines vont vous obliger
à décider d'un comportement, puis à modifier le code.

| Situation | Question |
|---|---|
| `Rectangle.build_from_str("2 ; 3")` | espaces tolérés ou erreur ? |
| `Rectangle.build_from_str("2;3;4")` | erreur brute `TypeError` ou `DimensionInvalide` avec un message clair ? |
| `Rectangle.build_from_str("a;b")` | idem avec `ValueError` |
| `Carre(2) == Rectangle(2, 2)` | vrai aujourd'hui. Est-ce voulu ? |
| `c = Carre(2); c.cote = 5` | `c.surface` vaut-il 25 ? |
| `{Rectangle(2, 3)}` | un rectangle peut-il aller dans un `set` ? Pourquoi ? |

Pour `Carre == Rectangle`, il n'y a pas de bonne réponse. Choisissez, et
laissez le test documenter le choix.

### 5. L'état global (5 min)

Écrivez ce test dans `test_rectangle.py` :

```python
def test_compteur():
    Rectangle(1, 1)
    Rectangle(1, 1)
    assert Rectangle.get_cpt() == 2
```

Lancez-le seul : `python -m pytest -k compteur`. Puis toute la suite.
Puis en le plaçant en premier dans le fichier, puis en dernier. Le résultat change.

Un test dont le résultat dépend des autres est un test qu'on ne peut plus
faire confiance. Deux issues :

- une fixture `autouse` qui remet `Rectangle._cpt` à zéro avant chaque test ;
- supprimer le compteur, qui ne sert à rien d'autre qu'à cette démonstration.

Faites la première dans le TP, on discutera de la seconde.

## Critères de réussite

- `python -m pytest` est vert, `-v` affiche des noms de tests lisibles.
- Au moins un test paramétré avec des `id=`.
- Aucun `pytest.raises(Exception)` : les erreurs attendues sont des exceptions métier.
- `Rectangle(-2, 3)` est refusé.
- Chaque ligne du tableau de l'étape 4 a son test, et le comportement choisi est écrit dans le nom du test.
- `test_compteur` passe quel que soit l'ordre d'exécution.

## Discussion (5 min)

Lesquels de ces tests auraient été inutiles ? Regardez le chapitre 2 du plan :
getters simples, détails d'implémentation. Faut-il tester `__str__` ? `__repr__` ?
`get_cpt()` ?

## Corrigé

```bash
cd corrige
python -m pytest -v
```
