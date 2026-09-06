# TP j4-04 — Résoudre une dépendance circulaire

**Durée : 45 min**

## Contexte

`depart/gestion/` est un mini-package de todo-list par projets : trois
modules, moins de cent lignes. Il ne s'importe même pas :

```bash
cd j4-04-resoudre-une-dependance-circulaire/depart
python -c "import gestion.taches"
```

```
ImportError: cannot import name 'en_titre' from partially initialized module
'gestion.affichage' (most likely due to a circular import)
```

## Objectif

Diagnostiquer le cycle, le casser par une architecture en couches, puis
**verrouiller** cette architecture pour qu'elle ne puisse plus être enfreinte.

## Étapes

### 1. Cartographier le cycle (5 min)

Relevez tous les `import` du package et dessinez le graphe.

| Module | importe |
|---|---|
| `taches` | |
| `projets` | |
| `affichage` | |

Combien de cycles distincts trouvez-vous ? (il y en a plus d'un)

### 2. Identifier la cause (5 min)

Pour chaque flèche, demandez-vous : **est-elle légitime ?**

Deux questions guident le diagnostic :

- pourquoi `Tache` a-t-elle besoin de connaître le catalogue des projets ?
- pourquoi `Tache` a-t-elle besoin de savoir se mettre en forme ?

```python
@dataclass
class Tache:
    def peut_etre_terminee(self, projets) -> bool:
        return not self.terminee and est_actif(projets, self.projet)

    def ligne(self) -> str:
        return en_ligne(self)
```

> C'est la cause la plus fréquente en pratique : un objet métier à qui l'on a
> ajouté, au fil du temps, la capacité de s'afficher, de se sauvegarder et de
> s'envoyer. Il finit par dépendre de tout le projet — et tout le projet dépend
> de lui.

Troisième flèche à examiner : `affichage` importe `DELAI_ALERTE_JOURS` depuis
`projets`. Une constante vit-elle au bon endroit ?

### 3. Extraire le module de base (10 min)

Créez `gestion/modele.py` contenant `Tache`, `Projet`, les constantes et les
exceptions. Ce module **n'importe rien du projet** — c'est ce qui rend un cycle
structurellement impossible.

Retirez `peut_etre_terminee()` et `ligne()` de la classe. Elles deviennent des
fonctions dans les modules qui en portent la responsabilité. Ce que `Tache`
garde, c'est son comportement **métier** : `est_en_retard(jour)`, par exemple.

Profitez-en pour remplacer le `dict` de projet par une `Projet` immuable.

### 4. Créer le service applicatif (10 min)

Il reste un besoin réel : produire un résumé qui combine les projets **et** la
mise en forme. Ce besoin ne doit vivre ni dans `projets`, ni dans `affichage`
— sinon le cycle réapparaît.

Il vit dans une couche **au-dessus** des deux :

```python
# gestion/service.py
from gestion import affichage, projets


def resume(catalogue, taches, jour) -> list[str]: ...
```

Vous devriez obtenir :

```
        service
        ▲     ▲
   projets  affichage
        ▲     ▲
        modele          ← n'importe rien
```

### 5. Verrouiller l'architecture (10 min)

Un schéma dans un wiki se périme. Un contrat exécutable, non.

Créez `.importlinter` à la racine du dossier :

```ini
[importlinter]
root_package = gestion

[importlinter:contract:couches]
name = Architecture en couches — les imports ne vont que vers le bas
type = layers
layers =
    gestion.service
    gestion.projets | gestion.affichage
    gestion.modele
```

```bash
uv run lint-imports
```

> Le `|` déclare deux modules **au même niveau** : ils peuvent tous deux
> importer `modele`, mais **pas** s'importer l'un l'autre. C'est précisément
> ce qui empêche le cycle de revenir.

Vérifiez que le contrat échoue si vous le violez : ajoutez temporairement
`from gestion.affichage import en_titre` dans `projets.py`, relancez, puis
retirez-le.

### 6. Tester chaque couche isolément (5 min)

Écrivez au moins un test par couche. Constatez qu'un test de `affichage` n'a
besoin d'aucun catalogue, et qu'un test de `modele` n'importe rien d'autre.

## Critères de réussite

- `python -c "import gestion.taches"` — pardon, **`import gestion.service`** —
  fonctionne.
- `gestion/modele.py` ne contient aucun `import gestion` — un test le prouve.
- `uv run lint-imports` affiche `Contracts: 1 kept, 0 broken`.
- Vous avez vérifié que le contrat **échoue** quand on le viole.
- Chaque couche a ses tests.

## Pour aller plus loin

Que se passe-t-il si une tâche est rattachée à un projet absent du catalogue ?
Le code d'origine l'ignorait purement et simplement : `resume` ne l'affichait
nulle part. Remplacez ce silence par une exception métier explicite, levée par
le service.

## Discussion (5 min)

Le contrat `.importlinter` fait 9 lignes. Où le brancheriez-vous pour qu'il
protège réellement l'équipe ?

> Réponse demain matin : dans la pipeline GitLab, au stage `qualité`. Une
> merge request qui réintroduit un cycle échoue avant d'être relue.

## Corrigé

`corrige/` — 4 modules, 21 tests (dont un qui exécute `lint-imports`), et un
contrat `import-linter` qui passe.

```bash
uv run pytest j4-04-resoudre-une-dependance-circulaire/corrige -v
cd j4-04-resoudre-une-dependance-circulaire/corrige && uv run lint-imports
```
