---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Le rôle des tests dans une librairie partagée"
---

<!-- _class: lead -->

# 1. Le rôle des tests dans une librairie partagée

*Ce qu'un test protège, et de quoi*

---

# Pourquoi tester une librairie interne

Une application a un utilisateur qui se plaint. Une librairie a **N projets qui
ne se plaignent pas** — parce qu'ils ne savent pas encore que le résultat a changé.

| | Application | Librairie |
|---|---|---|
| Qui détecte la régression ? | l'utilisateur, vite | un autre projet, des mois plus tard |
| Coût de la correction | un correctif | un correctif × N mises à jour |
| Qui connaît le comportement attendu ? | l'équipe | **personne — sauf les tests** |

> Dans une librairie, la suite de tests est le seul endroit où le comportement
> attendu est écrit **de manière exécutable**. La documentation, elle, vieillit
> en silence.

---

# Trois natures de défaut, trois coûts

| | Bug visible | Bug silencieux | Régression |
|---|---|---|---|
| **Symptôme** | exception, plantage | résultat faux, plausible | ce qui marchait ne marche plus |
| **Découverte** | immédiate | tardive, par hasard | lors d'une mise à jour |
| **Coût** | faible | **très élevé** | élevé, et politique |
| **Détecté par** | à peu près n'importe quoi | un test de calcul ciblé | une suite de tests existante |

Les deux dernières colonnes justifient à elles seules l'effort de test dans une
librairie. La première n'a jamais eu besoin de tests pour être trouvée.

> **🎯 En pratique** : ne dimensionnez pas votre effort de test sur les bugs
> visibles. Ils se signalent tout seuls.

---

# Unitaire, intégration, fonctionnel

| | Périmètre | Dépendances réelles | Durée | Ce qu'il prouve |
|---|---|---|---|---|
| **Unitaire** | une fonction, une classe | aucune | µs | *le calcul est juste* |
| **Intégration** | un composant + une frontière | une (base, fichier, API) | ms-s | *le branchement fonctionne* |
| **Fonctionnel** | la chaîne complète | toutes | s-min | *l'ensemble produit le bon résultat* |

Les trois sont utiles et **ne se remplacent pas** :

- 200 tests unitaires ne garantissent pas que votre requête SQL est correcte ;
- un test fonctionnel vert ne dit pas *laquelle* de vos 40 formules est juste.

---

# La pyramide, et ce qu'elle veut vraiment dire

```
              ╱╲          fonctionnels     quelques-uns    lents, fragiles
             ╱  ╲                                          diagnostic faible
            ╱────╲
           ╱      ╲       intégration      quelques dizaines
          ╱        ╲
         ╱──────────╲
        ╱            ╲    unitaires        des centaines   rapides, stables
       ╱______________╲                                    diagnostic précis
```

La forme n'est pas un dogme esthétique. Elle découle d'un arbitrage :

> Plus un test est haut, plus il **couvre** de code — et moins il **localise**
> la panne. Un test fonctionnel rouge dit « quelque chose est cassé ».
> Un test unitaire rouge dit « la ligne 34 de `calculer_indice` ».

Sur du code scientifique, la base de la pyramide est souvent la seule partie
rentable à construire en premier.

---

# Tester le comportement, pas l'implémentation

<div class="cols">
<div>

**Test lié à l'implémentation** ❌

```python
def test_calcul():
    c = Calculateur()
    c._preparer()
    assert c._cache == {}
    c._appliquer_coefficient(2)
    assert c._resultat_intermediaire == 2
```

Renommer `_cache` casse le test.
Le comportement, lui, n'a pas changé.

</div>
<div>

**Test lié au comportement** ✓

```python
def test_calcul():
    assert Calculateur().calculer(2) == 4
```

Toute réécriture interne est libre,
tant que `calculer(2)` vaut 4.

C'est **exactement** ce dont vous avez
besoin pour refactoriser au Jour 4.

</div>
</div>

> **⚠️ Piège** : un test qui casse à chaque refactoring, alors que rien de
> visible n'a changé, ne protège rien. Il **empêche** l'amélioration du code.

---

# Le test comme contrat exécutable

Chaque test énonce une clause du contrat de votre librairie :

```python
def test_indice_est_nul_en_absence_de_mesure():
    """Sans mesure exploitable, l'indice est indéterminé — pas zéro."""
    assert calculer_indice([]) is None
```

Ce test dit trois choses à vos consommateurs :

1. cette situation **est prévue** (elle n'est pas un oubli) ;
2. voici ce qui est retourné (`None`, pas `0`, pas une exception) ;
3. si quelqu'un change cela un jour, **il le fera sciemment** — le test rougira.

> Le nom du test fait partie du contrat. `test_cas_3` ne documente rien.
> `test_indice_est_nul_en_absence_de_mesure` remplace un paragraphe.

---

# Ce qu'il faut tester au-delà du cas nominal

Le cas qui marche est le plus facile à écrire, et le moins utile : c'est celui
que vous avez déjà vérifié à la main.

| Catégorie | Exemples concrets |
|---|---|
| **Bornes** | 0, 1, la valeur du seuil, le seuil ± 1, la dernière heure du jour |
| **Vide** | liste vide, chaîne vide, fichier de 0 octet, `None` |
| **Volume** | un seul élément, deux, beaucoup |
| **Invalide** | type inattendu, valeur négative, date future, encodage exotique |
| **Erreurs attendues** | l'exception métier est-elle bien levée, avec le bon message ? |

Sur les slides du Jour 1, quatre des six bugs silencieux du TP j1-01 étaient
dans cette colonne de droite. Aucun n'était dans le cas nominal.

---

# Un test qui échoue doit vous dire quoi faire

Comparez deux échecs pour le même bug :

<div class="cols">
<div>

**Diagnostic faible**

```
FAILED test_pipeline
AssertionError: assert False
```

Il faut ouvrir le test, lire 40 lignes,
et lancer un débogueur.

</div>
<div>

**Diagnostic immédiat**

```
FAILED test_conversion_mg_vers_ug
assert 12.4 == 12400.0
 +  where 12.4 = normaliser(12.4, 'mg/m3')
```

Le nom donne la règle métier fautive.
L'assertion donne l'entrée et l'écart.

</div>
</div>

Trois pratiques suffisent : **un test = un comportement**, un nom qui décrit ce
comportement, et une assertion sur une valeur — pas sur un booléen déjà calculé.

---

# À retenir

> **1.** Dans une librairie, la suite de tests est le seul endroit où le
> comportement attendu est écrit de façon exécutable — et donc le seul qui ne
> mente pas.

> **2.** Testez le **comportement** observable. Un test qui connaît les
> attributs privés bloque le refactoring au lieu de le protéger.

> **3.** L'effort se concentre sur les bugs silencieux et les régressions :
> bornes, cas vides, entrées invalides, erreurs attendues.
