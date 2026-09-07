# TP 05 : Adapter

**Durée : 45 min**

## Contexte

`depart/salut/salutation.py` est un hello world qui dit « Bonjour », « Bon
après-midi » ou « Bonsoir » selon l'heure, lue sur une API HTTP publique.

```bash
cd depart
python main.py
python -m pytest
```

## Objectif

Rendre `saluer` testable sans réseau et sans dépendre de l'heure qu'il est,
en isolant l'API derrière un Adapter.

## Étapes

### 1. Le test impossible (5 min)

`tests/test_salutation.py` contient un test. Il est vert le matin, rouge
l'après-midi, et rouge sans réseau. Il n'est jamais fiable.

Deux problèmes sont mêlés dans quinze lignes : un calcul (quelle formule pour
quelle heure) et un accès externe (quelle heure il est). Le calcul est trivial
à tester. L'accès externe ne l'est pas. Tant qu'ils sont dans la même
fonction, le test hérite du pire des deux.

### 2. Séparer le calcul (10 min)

Extrayez la partie pure :

```python
def formule(heure: int) -> str: ...
```

Testez-la avec un `parametrize` sur les frontières : 0, 11, 12, 17, 18, 23.
Puis 24 et -1 : que devrait-il se passer ? Décidez, écrivez le test, faites-le
passer.

Le hello world est déjà couvert aux trois quarts, sans réseau.

### 3. Nommer ce qui reste (5 min)

Ce qui reste dans `saluer` : ouvrir une URL, parser du JSON, découper une
chaîne de date. Le format de réponse d'un site tiers est écrit dans le code
métier. Si l'API change de format, ou si on préfère lire l'heure système,
c'est `saluer` qu'on modifie.

Posez la question dans l'autre sens : de quoi `saluer` a-t-il besoin ? D'un
entier entre 0 et 23. Rien d'autre.

### 4. L'Adapter (15 min)

Écrivez l'interface dont le métier a besoin, dans `salut/horloges.py` :

```python
class Horloge(Protocol):
    def heure(self) -> int: ...
```

Puis les adaptateurs, qui traduisent une source concrète vers cette interface :

- `HorlogeTimeApi` : le code d'appel HTTP et de parsing, déplacé tel quel ;
- `HorlogeSysteme` : `datetime.now().hour`, pour tourner sans réseau.

`saluer(nom, horloge)` reçoit l'horloge (TP 03). `main.py` choisit laquelle.

### 5. Deux niveaux de test (10 min)

`saluer` se teste avec une fausse horloge de trois lignes, qui renvoie l'heure
qu'on lui a donnée. Écrivez-le.

`HorlogeTimeApi` se teste une seule fois, avec un mock de `urlopen` :

```python
from unittest.mock import patch, MagicMock

def test_horloge_timeapi_lit_l_heure():
    reponse = MagicMock()
    reponse.read.return_value = b'{"hour": 14, "minute": 32}'
    reponse.__enter__.return_value = reponse
    with patch("salut.horloges.urlopen", return_value=reponse):
        assert HorlogeTimeApi().heure() == 14
```

Patchez là où le nom est *utilisé* (`salut.horloges.urlopen`), pas là où il
est défini. Ajoutez un test pour une réponse mal formée : l'adaptateur doit
lever une exception à vous, pas un `KeyError`.

## Critères de réussite

- `python -m pytest` est vert, sans réseau, à n'importe quelle heure.
- `salutation.py` n'importe ni `json` ni `urllib`.
- Un seul test utilise `patch`, et il ne teste que l'adaptateur.
- `python main.py` fonctionne hors ligne.

## Discussion (5 min)

L'Adapter et l'injection de dépendance vont ensemble : l'un définit la forme
attendue, l'autre permet de la fournir. Sans l'Adapter, on aurait mocké
`urlopen` dans chaque test de `saluer`, et chaque test aurait connu le format
JSON de l'API.

Sur-design : une seule source, jamais de test, jamais de changement. Ça n'arrive
pas souvent.

## Corrigé

```bash
cd corrige
python -m pytest -v
python main.py
```
