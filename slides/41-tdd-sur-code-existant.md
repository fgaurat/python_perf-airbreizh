---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Approfondir le TDD sur du code existant"
---

<!-- _class: lead -->

# 1. Approfondir le TDD sur du code existant

*Le cycle ne change pas — le point de départ, si*

---

# Code neuf, code existant : la même boucle, un autre problème

| | Code neuf | Code existant |
|---|---|---|
| Point de départ | une page blanche | 4 000 lignes qui tournent en production |
| La question | *que doit faire ce code ?* | *que fait-il déjà, exactement ?* |
| Le premier obstacle | choisir l'interface | **réussir à instancier l'objet** |
| Le risque principal | mal concevoir | **casser sans s'en apercevoir** |
| Le premier test | décrit une intention | **capture un comportement** |

> Le cycle Red / Green / Refactor reste identique. Ce qui change, c'est qu'avant
> de pouvoir écrire le premier test, il faut souvent **modifier le code** — et
> qu'on n'a pas encore de filet pour le faire.

C'est le paradoxe du legacy, et il a des solutions mécaniques.

---

# Le dilemme du legacy

```
   Pour modifier en sécurité       Pour écrire un test
   il faut des tests               il faut pouvoir instancier
            │                                │
            └───────────► ◄──────────────────┘
                  et pour instancier
                 il faut modifier le code
```

Trois façons d'en sortir, par ordre de risque croissant :

| Sortie | Principe | Risque |
|---|---|---|
| **Bourgeon** (*sprout*) | écrire le neuf à côté, en TDD, sans toucher à l'existant | quasi nul |
| **Enveloppe** (*wrap*) | encadrer l'existant sans le modifier | faible |
| **Couture** (*seam*) | créer un point d'insertion par une modification minimale | modéré, à faire à petits pas |

---

# La couture : le plus petit changement qui rend testable

Une **couture** est un endroit où l'on peut changer le comportement du programme
sans modifier le code à cet endroit.

<div class="cols">
<div>

**Aucune couture**

```python
class Rapport:
    def __init__(self):
        self.db = connect(DSN)     # soudé
```

Impossible d'instancier sans base.

</div>
<div>

**Une couture, en une ligne**

```python
class Rapport:
    def __init__(self, db=None):
        self.db = db or connect(DSN)
```

Le comportement en production est
**identique**. Les tests peuvent
désormais passer un fake.

</div>
</div>

> **🎯 En pratique** : c'est la modification la plus rentable du legacy. Elle
> tient en une ligne, ne change rien pour les appelants existants, et transforme
> un module intestable en module testable.

À terme, on supprimera le `or connect(DSN)` — mais pas au premier jour.

---

# Bourgeon : écrire le neuf à côté

On vous demande d'ajouter une règle dans une méthode de 300 lignes. **N'écrivez
pas la règle dedans.**

<div class="cols">
<div>

**1. La nouvelle règle, en TDD, à part**

```python
def doit_etre_signale(mesure: Mesure) -> bool:
    """Nouvelle règle métier, écrite en TDD."""
    return mesure.valeur > SEUIL and mesure.validee
```

Testée à fond, isolément, sans avoir
lu les 300 lignes.

</div>
<div>

**2. Un seul appel dans l'existant**

```python
    # … 187 lignes plus haut …
    if doit_etre_signale(mesure):     # ← la seule ligne ajoutée
        signalements.append(mesure)
    # … 112 lignes plus bas …
```

Le risque de régression se limite à
**une ligne**.

</div>
</div>

Le code de 300 lignes n'a pas été amélioré — mais il n'a pas empiré, et la
partie neuve est correcte. C'est un progrès net, obtenu en une heure.

---

# Enveloppe : encadrer sans modifier

Quand la nouvelle fonctionnalité doit s'exécuter **avant ou après** l'existant,
sans s'y insérer :

```python
def generer_rapport(jour):          # ← méthode existante, inchangée
    ...


def generer_rapport_avec_journal(jour):     # ← enveloppe, écrite en TDD
    """Génère le rapport et consigne l'opération."""
    debut = horloge()
    resultat = generer_rapport(jour)
    journaliser(jour, duree=horloge() - debut)
    return resultat
```

L'ancien code n'est pas relu, pas modifié, pas mis en danger.

> **⚠️ Piège** : bourgeon et enveloppe laissent la dette en place. Ce sont des
> techniques de **survie**, à utiliser quand le délai ne permet pas mieux — pas
> une stratégie à long terme. Notez la dette quelque part.

---

# Caractériser avant de modifier

Quand il faut vraiment entrer dans le code existant, on commence par **figer ce
qu'il fait**, sans se demander si c'est juste.

```python
def test_caracterisation_calcul_v1():
    """Fige le comportement actuel — NON validé par le métier.

    Objectif : détecter tout changement pendant le refactoring.
    """
    assert calculer(RELEVE_REFERENCE) == pytest.approx(72.4)
```

La technique pour trouver la valeur, quand personne ne la connaît :

```python
assert calculer(RELEVE_REFERENCE) == 0        # valeur volontairement fausse
```

```
E   assert 72.4 == 0
```

Le message d'erreur **vous donne** la réponse. Vous la recopiez. Le filet est posé.

---

# Le piège du test de caractérisation

Un test de caractérisation **fige les bugs autant que les comportements
corrects**. C'est voulu — mais il faut que ce soit dit.

<div class="cols">
<div>

**Dangereux**

```python
def test_calculer():
    assert calculer(RELEVE) == 72.4
```

Six mois plus tard, quelqu'un
« corrige » ce test parce que la
valeur lui semble fausse. Il avait
raison : elle l'était. Et il vient
de supprimer la seule trace du bug.

</div>
<div>

**Honnête**

```python
def test_caracterisation_calculer():
    """Comportement OBSERVÉ au 2026-09-04.

    Non validé par le métier. La valeur 72.4
    inclut potentiellement le bug #4231
    (arrondi appliqué deux fois).
    À revoir après spécification.
    """
    assert calculer(RELEVE) == pytest.approx(72.4)
```

</div>
</div>

> **🎯 En pratique** : nommez ces tests `test_caracterisation_*` et datez la
> docstring. La distinction avec un vrai test unitaire doit sauter aux yeux.

---

# Le cas du calcul scientifique

Sur un calcul numérique, la valeur de référence est souvent inconnue, ou
dépendante de la plateforme. Testez alors des **propriétés**, pas des valeurs.

| Type de propriété | Exemple d'assertion |
|---|---|
| **Bornes** | `0 <= indice <= 100` |
| **Monotonie** | `f(x) <= f(y)` dès que `x <= y` |
| **Conservation** | `sum(parts) == total` |
| **Symétrie** | `distance(a, b) == distance(b, a)` |
| **Invariance** | permuter l'ordre d'entrée ne change pas la moyenne |
| **Cas dégénéré connu** | `f(0) == 0`, `f(constante) == constante` |
| **Cohérence entre méthodes** | la version rapide donne la même chose que la version lente |

> La dernière ligne est particulièrement utile en refactoring de code
> scientifique : gardez l'ancienne implémentation, et testez que la nouvelle lui
> est équivalente à `1e-9` près sur mille entrées aléatoires **à graine fixe**.

---

# Pour aller plus loin : générer les cas, pas les écrire

Tester une propriété sur cinq valeurs choisies à la main laisse passer la
sixième. **Hypothesis** génère les entrées, cherche les contre-exemples, et
réduit celui qu'il trouve au cas minimal.

```python
from hypothesis import given, strategies as st

@given(
    montant=st.integers(min_value=0, max_value=10_000_000),
    poids=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=20),
)
def test_la_somme_des_parts_egale_toujours_le_montant(montant, poids):
    assert sum(repartir(montant, poids)) == montant
```

Une centaine d'exécutions par défaut, avec des cas qu'on n'aurait pas pensé à
écrire : un seul bénéficiaire, vingt poids identiques, un montant de 1 centime.

> **🎯 En pratique** : c'est l'outil naturel des propriétés de la slide
> précédente — bornes, monotonie, conservation, symétrie. Sur du calcul
> scientifique, il trouve les cas dégénérés que les jeux de référence oublient.
> `uv add --dev hypothesis`, et rien d'autre à installer.

---

# Combiner les trois natures de test

Sur une base existante, les trois se complètent — dans cet ordre de construction :

```
  1. Un test de bout en bout        « quelque chose a changé »
     sur un jeu réel                 ← posé en premier, coût minimal
              ↓
  2. Des tests de caractérisation   « le changement est dans cette fonction »
     par fonction touchée            ← posés avant chaque refactoring
              ↓
  3. Des tests unitaires            « le changement est cette règle, à cette ligne »
     sur les règles extraites        ← écrits au fur et à mesure de l'extraction
```

Chaque niveau **remplace progressivement** le précédent : une fois la règle
extraite et testée unitairement, le test de caractérisation correspondant peut
être supprimé.

> **⚠️ Piège** : garder les trois niveaux indéfiniment produit une suite lente
> et redondante. Les tests de caractérisation sont un **échafaudage**.

---

# À retenir

> **1.** Sur du legacy, le premier obstacle n'est pas d'écrire le test, c'est de
> **pouvoir instancier**. Une couture — un paramètre avec valeur par défaut —
> lève ce blocage en une ligne, sans changer la production.

> **2.** Bourgeon et enveloppe permettent d'écrire du neuf en TDD **sans
> toucher** à l'existant. Le risque de régression se limite à une ligne d'appel.

> **3.** Un test de caractérisation fige les bugs avec le reste. Nommez-le et
> datez-le pour que personne ne le confonde avec une validation métier.
