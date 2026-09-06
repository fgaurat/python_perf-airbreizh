---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Les design patterns comme outils de conception"
---

<!-- _class: lead -->

# 4. Introduction aux design patterns

*Reconnaître un problème, pas réciter un catalogue*

---

# Un pattern est un nom donné à une solution récurrente

Les patterns n'ont pas été inventés : ils ont été **observés**. Des équipes
différentes, sur des projets sans rapport, résolvaient les mêmes problèmes de
la même façon. Quelqu'un a fini par leur donner des noms.

Un pattern comporte donc toujours trois parties :

| Partie | Question |
|---|---|
| **Le problème** | Quelle douleur ressent-on ? |
| **La solution** | Quelle structure la soulage ? |
| **Les conséquences** | Qu'est-ce que ça coûte ? |

> On enseigne presque toujours la deuxième. C'est la **première** qui est
> utile au quotidien, et la **troisième** qui évite les catastrophes.

---

# Connaître un pattern ≠ reconnaître le problème

Deux façons opposées d'utiliser un catalogue de patterns :

<div class="cols">
<div>

**Partir de la solution** ❌

*« On va mettre une Factory ici, ça fera propre. »*

Résultat classique : une classe
`FactoryProvider` qui fabrique un objet
unique, dans un seul cas d'usage,
appelée depuis un seul endroit.

Complexité ajoutée : réelle.
Problème résolu : aucun.

</div>
<div>

**Partir du problème** ✓

*« Cette classe teste le type de fichier
à cinq endroits différents, et il faut
en ajouter un sixième. »*

→ le problème est un **choix
d'implémentation dispersé**.

→ le pattern qui y répond s'appelle
Factory. On lui donne son nom après,
pas avant.

</div>
</div>

---

<!-- _class: dense -->

# En Python, la solution est souvent plus simple qu'en Java

Beaucoup de patterns du catalogue classique compensent des limitations que
Python n'a pas : les fonctions sont des objets, les classes aussi, et un `dict`
fait office de table de dispatch.

<div class="cols">
<div>

**Strategy « à la Java »**

```python
class Strategie(ABC):
    @abstractmethod
    def calculer(self, x): ...

class Lineaire(Strategie):
    def calculer(self, x): return x

class Quadratique(Strategie):
    def calculer(self, x): return x ** 2
```

</div>
<div>

**Strategy en Python**

```python
def lineaire(x): return x
def quadratique(x): return x ** 2

STRATEGIES = {
    "lineaire": lineaire,
    "quadratique": quadratique,
}
```

Même découplage, même testabilité,
un tiers du code.

</div>
</div>

> **🎯 En pratique** : passez à la version « classes » quand la stratégie a
> besoin d'un état, de plusieurs méthodes, ou d'une configuration propre.

---

# Les problèmes récurrents dans une librairie Python

Cinq situations que vous rencontrerez dans vos propres codes :

1. **La création d'un objet est complexe** — il faut lire une configuration,
   choisir un type, brancher trois dépendances… et ce code est dupliqué partout.
2. **Le code dépend d'une source externe** — base, API, fichier — et rien ne
   peut être testé sans elle.
3. **L'algorithme dépend du contexte** — une cascade de `if` sur un mode, un
   format d'export, un type de client.
4. **Le code est trop couplé pour être testé** — la classe construit elle-même
   tout ce dont elle a besoin.
5. **Le workflow métier est difficile à faire évoluer** — les mêmes six étapes
   se répètent dans huit fonctions, avec des variantes.

---

# Du problème vers le pattern

| Le problème que vous vivez | Le nom de la solution |
|---|---|
| « Je ne peux pas tester sans la base / l'API » | **Adapter**, **Repository** |
| « J'ai une cascade de `if` sur un mode de calcul » | **Strategy** |
| « Ce code de création est dupliqué à six endroits » | **Factory** |
| « L'appelant doit connaître cinq classes pour faire une chose » | **Facade** |
| « Cette classe construit elle-même ses dépendances » | **Dependency Injection** |
| « Les mêmes étapes se répètent avec des variantes » | **Template Method** |

Ce tableau se lit **de gauche à droite**. Jamais dans l'autre sens.

---

# Le catalogue de la formation

Sept patterns, choisis parce qu'ils servent tous la même cause — **réduire le
couplage et rendre le code testable** :

| Pattern | En une phrase | Vu au |
|---|---|---|
| **Adapter** | Traduire une interface externe en une interface qui vous convient | J3 |
| **Strategy** | Rendre un algorithme interchangeable | J3 |
| **Factory** | Centraliser la décision « quel objet créer » | J3 |
| **Repository** | Cacher totalement l'origine des données | J3 |
| **Facade** | Offrir une porte d'entrée simple à un sous-système complexe | J3 |
| **Dependency Injection** | Recevoir ses dépendances au lieu de les créer | J1 → J3 |
| **Template Method** | Figer le squelette d'un workflow, laisser varier les étapes | J3 |

---

# Pour situer le vocabulaire : les trois familles classiques

Le catalogue historique (*Gang of Four*, 1994) range les patterns en trois
familles. Nos sept s'y placent ainsi :

| Famille | Question posée | Nos patterns |
|---|---|---|
| **Créationnels** | *comment l'objet est-il construit ?* | Factory, Dependency Injection |
| **Structurels** | *comment les objets s'assemblent-ils ?* | Adapter, Facade, Repository |
| **Comportementaux** | *comment le comportement varie-t-il ?* | Strategy, Template Method |

> La classification aide à s'y retrouver dans un catalogue. Elle ne dit rien
> de **quand** utiliser un pattern — c'est le tableau problème → pattern de la
> slide précédente qui sert à cela.

Repository n'est pas dans le catalogue de 1994 : il vient du *Domain-Driven
Design* (2003). Il est structurel par nature, et c'est le plus utilisé des sept
dans les librairies qui accèdent à des données.

---

# Ce que les patterns ont en commun

Regardez la colonne du milieu du tableau précédent. Tous font la même chose :

> Ils **introduisent un point de substitution** là où le code était soudé.

Or un point de substitution, c'est exactement ce dont un test a besoin :
un endroit où glisser un objet simple, prévisible, en mémoire.

```
   Sans pattern              Avec pattern
   ┌─────────┐               ┌─────────┐
   │ Métier  │               │ Métier  │
   └────┬────┘               └────┬────┘
        │ soudé                   │ ── interface ──┐
        ▼                         ▼                ▼
   ┌─────────┐               ┌─────────┐     ┌──────────┐
   │ API HTTP│               │ API HTTP│     │  Fake    │  ← le test
   └─────────┘               └─────────┘     └──────────┘
```

C'est pour cette raison que les patterns arrivent au Jour 3, entre le mocking
et le refactoring : ce sont les **alternatives à un mock compliqué**.

---

# À retenir

> **1.** Un pattern se reconnaît par son **problème**, jamais par sa structure.
> Si vous ne savez pas nommer la douleur, n'appliquez pas le remède.

> **2.** En Python, la première solution à essayer est une fonction, un `dict`
> ou un paramètre. Le pattern « à classes » vient quand cela ne suffit plus.

> **3.** Tous les patterns de cette formation créent un **point de
> substitution** — c'est ce qui les rend utiles aux tests.
