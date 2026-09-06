---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Refactoring sécurisé"
---

<!-- _class: lead -->

# 3. Refactoring sécurisé

*Changer la structure sans changer le comportement*

---

# Refactoring ou réécriture ?

| | Refactoring | Réécriture |
|---|---|---|
| Comportement | **inchangé, à chaque étape** | reconstruit |
| Durée d'une étape | minutes | semaines |
| Le code compile et passe | **en permanence** | à la fin, on espère |
| Réversible | oui, à tout moment | non |
| Livrable intermédiaire | oui | aucun |
| Risque | maîtrisé | **maximal** |

> Une réécriture est un projet qui promet de retrouver dans un an les
> fonctionnalités d'aujourd'hui — y compris celles que personne n'a documentées,
> et que seuls les utilisateurs connaissent.

Le refactoring n'est pas plus lent. Il est simplement **livrable en continu**.

---

# La règle de sécurité

```
   1. Les tests sont verts
   2. UNE transformation                    ← une seule, mécanique
   3. Les tests sont verts
   4. Commit
   5. Retour en 2
```

Ce qui rend la méthode sûre, ce n'est pas la prudence : c'est la **taille du
pas**. Quand le pas dure deux minutes, une erreur coûte deux minutes.

| Signal d'alarme | Ce qu'il faut faire |
|---|---|
| « Je vais tout casser et je recolle après » | revenir au dernier commit |
| Rouge depuis plus de 10 minutes | `git stash`, recommencer plus petit |
| Trois transformations en même temps | les défaire, les refaire une par une |
| « Tant que j'y suis, je corrige ce bug » | **non** — c'est un autre commit |

> **⚠️ Piège** : corriger un bug pendant un refactoring rend impossible de
> savoir si les tests ont rougi à cause du refactoring ou de la correction.

---

# Le catalogue utile

Sept transformations couvrent l'essentiel du travail quotidien :

| Transformation | Symptôme traité |
|---|---|
| **Extraire une fonction** | un bloc de code avec un commentaire au-dessus |
| **Extraire une classe** | un groupe de champs et de méthodes qui vont ensemble |
| **Introduire un objet paramètre** | les mêmes 3 arguments partout |
| **Remplacer une conditionnelle par un dispatch** | une cascade de `elif` |
| **Supprimer une duplication** | le même bloc à trois endroits |
| **Rendre une fonction pure** | une fonction qui lit ou écrit un état global |
| **Clarifier les erreurs** | un `return None`, un code de retour `-1`, un `except: pass` |

Les trois premières sont réalisables **automatiquement** par votre éditeur
(VS Code, PyCharm) — donc sans risque de faute de frappe.

---

# Extraire une fonction — le geste de base

<div class="cols">
<div>

**Avant**

```python
def traiter(montants):
    ...
    # normaliser les unités
    normalises = []
    for m in montants:
        if m.unite == "centimes":
            normalises.append(m.valeur / 100)
        else:
            normalises.append(m.valeur)
    ...
```

</div>
<div>

**Après**

```python
def en_euros(montants) -> list[float]:
    """Convertit tous les montants en euros."""
    return [
        m.valeur / 100 if m.unite == "centimes" else m.valeur
        for m in montants
    ]


def traiter(mesures):
    ...
    normalisees = en_microgrammes(mesures)
    ...
```

</div>
</div>

> **🎯 Le signal** : un commentaire qui décrit ce que fait le bloc suivant est
> presque toujours un **nom de fonction en attente**. Le commentaire disparaît,
> le nom le remplace, et le bloc devient testable seul.

---

# Introduire un objet paramètre

<div class="cols">
<div>

**Avant**

```python
def frais(poids, distance, mode): ...
def delai(poids, distance, mode): ...
def suivi(poids, distance): ...
def assurance(poids, distance, valeur): ...
```

Les mêmes deux valeurs voyagent
partout, sans jamais être validées
ensemble.

</div>
<div>

**Après**

```python
@dataclass(frozen=True)
class Colis:
    poids_kg: float
    distance_km: float

    def __post_init__(self):
        if self.poids_kg < 0:
            raise ColisInvalide(...)


def frais(colis: Colis, mode: str): ...
def delai(colis: Colis, mode: str): ...
```

</div>
</div>

Trois bénéfices immédiats : la validation est faite **une fois**, les signatures
raccourcissent, et les tests construisent un objet nommé plutôt que d'aligner
des nombres anonymes.

---

# Remplacer une conditionnelle par un dispatch

C'est le refactoring qui transforme un `elif` interminable en code ouvert à
l'extension — et chaque branche devient testable seule.

```python
# Avant : rouvrir la fonction à chaque nouveau cas
if type_ == "csv":   ...
elif type_ == "json": ...
elif type_ == "xml":  ...

# Après : ajouter une entrée, ne jamais rouvrir le dispatch
LECTEURS = {"csv": lire_csv, "json": lire_json, "xml": lire_xml}

def lire(chemin: Path, type_: str) -> list[dict]:
    try:
        return LECTEURS[type_](chemin)
    except KeyError:
        raise FormatInconnu(type_) from None
```

> **⚠️ Piège** : ne faites cette transformation que s'il y a **au moins trois
> branches** et qu'une quatrième est prévisible. Pour deux branches stables, le
> `if` est plus lisible.

---

# Rendre une fonction pure

C'est le refactoring qui rapporte le plus en testabilité, pour le moins d'effort.

<div class="cols">
<div>

**Avant**

```python
SEUIL = 50.0
_journal = []

def est_en_alerte(valeur):
    global SEUIL
    _journal.append(valeur)       # effet
    return valeur > SEUIL         # état global
```

Le résultat dépend d'un état invisible,
et l'appel modifie le monde.

</div>
<div>

**Après**

```python
def est_en_alerte(valeur: float, seuil: float = 50.0) -> bool:
    """Vrai si la valeur dépasse strictement le seuil."""
    return valeur > seuil
```

Testable en une ligne, pour n'importe
quel seuil, dans n'importe quel ordre.

La journalisation remonte chez
l'appelant, où elle est visible.

</div>
</div>

---

# Introduire un pattern pendant un refactoring

Un pattern ne s'introduit pas d'un bloc. Il **apparaît** au terme d'une suite de
petites transformations, chacune validée par les tests :

```
  1. Extraire une fonction par branche du `elif`     ← tests verts
  2. Mettre les fonctions dans un dict               ← tests verts
  3. Remplacer le `elif` par un accès au dict        ← tests verts
                    ↓
            c'est un Strategy
```

```
  1. Ajouter un paramètre `depot=None` (couture)     ← tests verts
  2. Extraire les requêtes SQL dans une classe       ← tests verts
  3. Déclarer un Protocol décrivant ses méthodes     ← tests verts
  4. Écrire un fake en mémoire                       ← nouveaux tests possibles
                    ↓
            c'est un Repository
```

> **🎯 En pratique** : si vous ne pouvez pas nommer le problème que le pattern
> résout **avant** de commencer, ne commencez pas. Le nom du pattern se met à la
> fin, dans le message de commit — pas au début, dans un plan d'architecture.

---

# Ce que le refactoring ne doit jamais faire

| Interdit pendant un refactoring | Pourquoi |
|---|---|
| Corriger un bug | on ne saura plus ce qui a fait rougir |
| Ajouter une fonctionnalité | idem, et le commit devient irrelisible |
| Changer une signature publique | ce n'est plus du refactoring, c'est une rupture d'API |
| Modifier un test pour le faire passer | c'est l'aveu que le comportement a changé |
| Reformater tout le fichier | le diff devient illisible en revue |

> **La règle absolue** : si un test rougit pendant un refactoring, **le
> refactoring est faux**. Ne modifiez pas le test — annulez la transformation.

C'est le seul moment du développement où cette règle est sans exception.

---

# À retenir

> **1.** Refactoring = comportement inchangé **à chaque étape**, avec un livrable
> possible en permanence. Ce n'est pas une réécriture menée prudemment.

> **2.** La sécurité vient de la **taille du pas**, pas de la prudence. Deux
> minutes par transformation, un commit à chaque vert.

> **3.** Un test qui rougit pendant un refactoring condamne le refactoring,
> jamais le test.
