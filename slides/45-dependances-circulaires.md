---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Dépendances circulaires et architecture"
---

<!-- _class: lead -->

# 5. Dépendances circulaires et architecture

*Deux modules qui s'importent sont un module mal découpé*

---

# Le symptôme

```python
# taches.py
from affichage import en_ligne

# affichage.py
from taches import Tache
```

```
ImportError: cannot import name 'Tache' from partially initialized module
'taches' (most likely due to a circular import)
```

Les contournements qu'on voit dans le code réel :

| Contournement | Ce qu'il cache |
|---|---|
| `import` au milieu d'une fonction | le cycle est toujours là, il est juste différé |
| `if TYPE_CHECKING:` | le cycle n'existe qu'au typage — acceptable |
| Tout fusionner dans un gros module | le cycle devient invisible et permanent |
| Réordonner les imports jusqu'à ce que ça marche | fragile : le prochain import cassera tout |

---

# Ce qu'un cycle signifie vraiment

> Deux modules qui s'importent mutuellement **ne peuvent pas être compris
> séparément**, ni testés séparément, ni réutilisés séparément.

Ce sont donc, en pratique, **un seul module** — qui a été coupé au mauvais
endroit.

Conséquences concrètes sur les tests :

- importer `taches` charge `affichage`, qui charge le moteur de rendu, qui
  charge la configuration… : le test le plus simple traîne tout le paquet ;
- un test d'un module fait échouer l'autre ;
- impossible d'extraire un sous-ensemble du package pour un autre projet.

---

# Les quatre causes fréquentes

| Cause | Exemple typique |
|---|---|
| **Le module fourre-tout** | `utils.py` importe la moitié du projet, et tout le monde l'importe |
| **Objets métier ↔ services** | `Tache` appelle `ServiceAffichage` pour se formater |
| **Le module de constantes bavard** | `config.py` importe des classes pour typer ses valeurs |
| **Les imports de confort** | `__init__.py` réexporte tout, créant des cycles indirects |

> **Le cas le plus fréquent en pratique** : un objet métier qui « sait
> s'afficher », « sait se sauvegarder » et « sait s'envoyer ». Il dépend alors
> du rendu, de la persistance et du réseau — qui dépendent tous de lui.

---

# Détecter les cycles

```bash
# ruff — signale les imports dans les fonctions, symptôme fréquent
uv run ruff check --select PLC0415 .

# import-linter — déclare et vérifie une architecture en couches
uv pip install import-linter && uv run lint-imports
```

```ini
# .importlinter
[importlinter]
root_package = gestion

[importlinter:contract:couches]
name = Architecture en couches
type = layers
layers =
    gestion.service      # le plus haut
    gestion.projets | gestion.affichage
    gestion.modele       # le plus bas — ne dépend de rien
```

> **🎯 En pratique** : ce fichier vaut une documentation d'architecture, avec un
> avantage décisif — il **échoue en CI** quand quelqu'un enfreint la règle. Nous
> le brancherons demain dans la pipeline.

---

# Résolution 1 — Extraire un module commun

C'est la solution qui marche dans 80 % des cas.

<div class="cols">
<div>

**Avant — cycle**

```
  taches.py  ──────►  affichage.py
      ▲                     │
      └─────────────────────┘
```

`affichage` a besoin de `Tache`.
`taches` a besoin de `en_ligne`.

</div>
<div>

**Après — arbre**

```
        modele.py          (Tache)
        ▲        ▲
        │        │
   taches.py  affichage.py
```

Les deux dépendent d'un troisième
module qui, lui, ne dépend de rien.

</div>
</div>

> **La règle qui évite les cycles par construction** : les **objets de valeur**
> (`dataclass`, exceptions, constantes) vivent dans un module de base qui
> n'importe **rien** du projet. Tout le reste peut en dépendre.

---

# Résolution 2 — Inverser la dépendance

Quand le module bas niveau a besoin d'appeler le haut niveau.

<div class="cols">
<div>

**Avant**

```python
# rappels.py  (bas niveau)
from notifications import envoyer_rappel

class Rappels:
    def verifier(self, taches, jour):
        for t in taches:
            if t.est_en_retard(jour):
                envoyer_rappel(t)
```

`rappels` dépend de `notifications`.

</div>
<div>

**Après**

```python
# rappels.py — ne dépend plus de rien
class Notificateur(Protocol):
    def rappeler(self, tache: Tache) -> None: ...


class Rappels:
    def __init__(self, notif: Notificateur):
        self._notif = notif
```

Le Protocol est déclaré **du côté qui
l'utilise**. C'est ce qui inverse le sens
de la flèche.

</div>
</div>

Le point d'entrée assemble : `Rappels(NotificateurSMTP(...))`.

---

# Résolution 3 — Retirer le comportement de l'objet métier

<div class="cols">
<div>

**Avant — l'objet sait tout faire**

```python
# modele.py
from rendu import en_csv
from depot import sauver

@dataclass
class Tache:
    titre: str

    def to_csv(self): return en_csv(self)
    def sauver(self): sauver(self)
```

`modele` dépend de tout le projet.

</div>
<div>

**Après — l'objet ne sait que se décrire**

```python
# modele.py — n'importe rien
@dataclass(frozen=True)
class Tache:
    titre: str


# rendu.py
def en_csv(tache: Tache) -> str: ...

# depot.py
def sauver(tache: Tache) -> None: ...
```

</div>
</div>

Le sens des flèches s'inverse : ce sont les services qui connaissent le modèle,
jamais l'inverse.

> **⚠️ Piège** : « c'est de la POO, l'objet doit porter son comportement ».
> Il porte son comportement **métier** (`est_en_retard`, `est_a_surveiller`),
> pas sa sérialisation ni sa persistance.

---

# Récapitulatif des techniques

| Situation | Technique | Effort |
|---|---|---|
| Deux modules partagent des types | **extraire un module commun** | faible |
| Le bas niveau appelle le haut niveau | **inverser par un Protocol** | moyen |
| Un objet métier fait du rendu ou de l'I/O | **sortir le comportement** | moyen |
| Deux modules s'appellent en alternance | **service applicatif** au-dessus des deux | moyen |
| Un couplage ponctuel et rare | **passer la dépendance en paramètre** | très faible |
| Notification entre modules sans lien | **événements** — un module publie, l'autre écoute | élevé |

> **🎯 En pratique** : essayez les deux premières lignes avant tout le reste.
> Les événements sont une solution puissante et souvent surdimensionnée : ils
> remplacent un cycle visible par un couplage invisible.

---

# La cible : un graphe sans cycle

```
   ┌──────────────────────────────────────────────┐
   │  api / cli / points d'entrée                 │  assemble tout
   └────────────────────┬─────────────────────────┘
                        ▼
   ┌──────────────────────────────────────────────┐
   │  services — orchestration, workflows          │
   └────────────────────┬─────────────────────────┘
                        ▼
   ┌──────────────────────────────────────────────┐
   │  metier — règles pures, fonctions             │
   └────────────────────┬─────────────────────────┘
                        ▼
   ┌──────────────────────────────────────────────┐
   │  modele — dataclasses, exceptions, constantes │  n'importe RIEN
   └──────────────────────────────────────────────┘
```

Les flèches ne vont que **vers le bas**. Les adaptateurs (base, API, fichiers)
se branchent au niveau `services`, jamais dans `metier` ni `modele`.

---

# À retenir

> **1.** Un cycle d'import n'est pas un problème technique : c'est un découpage
> fait au mauvais endroit. Les contournements le masquent sans le régler.

> **2.** La solution la plus fréquente est la plus simple : **extraire un module
> de base** que tout le monde importe et qui n'importe rien.

> **3.** `import-linter` transforme votre schéma d'architecture en test
> exécutable. C'est la seule documentation d'architecture qui reste vraie.
