---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Qualité logicielle appliquée aux librairies Python"
---

<!-- _class: lead -->

# 1. Qualité logicielle appliquée aux librairies Python

*Pourquoi une librairie n'est pas un gros script*

---

# Script, notebook, module, librairie

| | Durée de vie | Lecteurs | Consommateurs | Coût d'une erreur |
|---|---|---|---|---|
| **Script** | heures | 1 | 0 | on relance |
| **Notebook** | jours | 1-2 | 0 | on réexécute |
| **Module** | mois | l'équipe | 1 projet | on corrige |
| **Librairie** | **années** | **inconnus** | **N projets** | **N corrections** |

La différence n'est pas technique. C'est le **nombre de personnes et de codes
qui dépendent de vos choix**, et pendant combien de temps.

---

# Ce que ça change concrètement

Dans un script, une décision est réversible : vous êtes le seul concerné.

Dans une librairie, chaque élément public devient une **promesse** :

- le nom d'une fonction ;
- l'ordre et le nom de ses paramètres ;
- le type de ce qu'elle retourne ;
- ce qu'elle fait quand l'entrée est invalide ;
- l'unité dans laquelle elle exprime son résultat.

> Renommer un paramètre dans un script prend 10 secondes.
> Dans une librairie utilisée par 6 projets, c'est une négociation.

---

# Les problèmes classiques des librairies internes

<div class="cols">
<div>

1. Code difficile à comprendre
2. Effets de bord non annoncés
3. Fonctions ou méthodes trop longues
4. Dépendances implicites

</div>
<div>

5. Erreurs silencieuses
6. Absence de contrat clair
7. Modifications qui cassent d'autres codes

</div>
</div>

Aucun de ces problèmes n'est un problème de connaissance de Python.
Ce sont tous des problèmes de **conception** — et ils sont tous détectables.

---

# Effet de bord non annoncé

<div class="cols">
<div>

**Ce que fait la fonction**

```python
def valider(mesures: list[dict]) -> bool:
    for m in mesures:
        if m["valeur"] < 0:
            m["valeur"] = 0      # ← modifie
            m["corrige"] = True  # ← l'entrée
    return all("corrige" not in m
               for m in mesures)
```

</div>
<div>

**Ce que l'appelant croit**

```python
if valider(mesures):
    archiver(mesures)
else:
    # mesures est déjà modifié…
    signaler(mesures)
```

Le nom promet une vérification.
Le corps effectue une correction.

</div>
</div>

**Règle** : une fonction qui s'appelle `valider` ne modifie rien. Si elle
corrige, elle s'appelle `corriger` et **retourne** une nouvelle liste.

---

# Erreur silencieuse

<div class="cols">
<div>

**Avant**

```python
def charger_seuil(chemin):
    try:
        with open(chemin) as f:
            return json.load(f)["seuil"]
    except Exception:
        return 50   # valeur « par défaut »
```

Fichier absent, JSON invalide, clé
manquante, disque plein : le même 50.

</div>
<div>

**Après**

```python
class ConfigurationInvalide(Exception):
    """Configuration illisible ou incomplète."""


def charger_seuil(chemin: Path) -> float:
    try:
        données = json.loads(chemin.read_text())
    except OSError as e:
        raise ConfigurationInvalide(chemin) from e
    if "seuil" not in données:
        raise ConfigurationInvalide(
            f"{chemin} : clé 'seuil' absente")
    return float(données["seuil"])
```

</div>
</div>

Le premier code produit des résultats faux **sans jamais prévenir**.

---

# Le coût réel d'une erreur silencieuse

Un bug qui lève une exception coûte **une heure** : la trace pointe la ligne.

Un bug silencieux coûte **des semaines** :

1. les résultats sont légèrement faux pendant six mois ;
2. quelqu'un remarque une incohérence dans un rapport ;
3. on remonte la chaîne de traitement, projet par projet ;
4. on découvre la valeur par défaut ;
5. il faut recalculer et republier ce qui a été diffusé.

> **🎯 En pratique** : un `except Exception: pass` ou un `return None` en cas
> d'erreur est presque toujours une dette qui sera payée par quelqu'un d'autre.

---

# Absence de contrat clair

```python
def calculer(donnees, mode=1, flag=False, seuil=None):
    ...
```

Questions sans réponse : que contient `donnees` ? que valent les modes 2 et 3 ?
que se passe-t-il si `seuil` reste `None` ? l'appel modifie-t-il `donnees` ?

Un contrat, c'est la réunion de quatre éléments :

| Élément | Répond à |
|---|---|
| Signature typée | Qu'est-ce qui entre et qui sort ? |
| Docstring | Que fait la fonction, dans quelles unités ? |
| Exceptions déclarées | Que se passe-t-il quand ça se passe mal ? |
| **Tests** | Qu'est-ce qui est réellement garanti ? |

Les trois premiers peuvent mentir. Le quatrième, non.

---

# Ce que l'on cherche à sécuriser

| Ce qu'on sécurise | Exemple concret | Type de test |
|---|---|---|
| **Comportement métier** | une règle de gestion, un seuil de validité | unitaire |
| **Format de données** | colonnes attendues, unités, encodage | unitaire + schéma |
| **Calculs** | une formule, une agrégation, un arrondi | unitaire paramétré |
| **Compatibilité** | l'API publique du package ne change pas | non-régression |
| **Sources externes** | fichier, base, API distante | intégration |

Ces cinq lignes sont l'ordre de priorité que nous utiliserons au Jour 2 pour
décider **quoi tester en premier**.

---

# À retenir

> **1.** Une librairie se distingue d'un script par le nombre de codes qui
> dépendent d'elle et par la durée pendant laquelle ils en dépendent.

> **2.** Les problèmes classiques (effets de bord, erreurs silencieuses,
> absence de contrat) sont des problèmes de conception, pas de langage.

> **3.** Une erreur silencieuse coûte toujours plus cher qu'une exception :
> échouer bruyamment est un service rendu à l'appelant.
