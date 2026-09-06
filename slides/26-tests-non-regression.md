---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Tests de non-régression"
---

<!-- _class: lead -->

# 6. Tests de non-régression

*Transformer un incident en garantie permanente*

---

# Le bug est une spécification gratuite

Quand un bug remonte du terrain, vous avez déjà en main tout ce qui coûte cher
à produire :

- un **cas d'entrée réel** qui déclenche le problème ;
- un **résultat observé**, faux ;
- un **résultat attendu**, validé par quelqu'un.

C'est exactement le contenu d'un test. Il ne reste qu'à l'écrire — et le
transformer en garantie permanente au lieu d'une correction ponctuelle.

> **⚠️ Piège** : corriger sans écrire le test, c'est accepter que le même bug
> revienne au prochain refactoring — sans que personne ne s'en aperçoive.

---

# La séquence, dans l'ordre

```
   1. Reproduire        Écrire le test qui échoue AVANT de corriger.
      ↓                 S'il passe du premier coup, vous n'avez pas
                        reproduit le bug — vous en avez inventé un autre.

   2. Voir le rouge     La sortie du test doit correspondre à ce que
      ↓                 le terrain a observé.

   3. Corriger          Le minimum pour faire passer le test.
      ↓

   4. Voir le vert      La correction traite bien ce cas-là.
      ↓

   5. Élargir           Le bug était-il un cas particulier d'une
                        famille ? Ajouter les cas voisins.
```

L'ordre compte : écrire le test **après** la correction ne prouve rien, puisque
vous n'aurez jamais vu ce test échouer.

---

# Un exemple complet

Le support signale : *« les tâches dont le titre contient une apostrophe
n'apparaissent pas dans l'export »*.

```python
def test_titre_avec_apostrophe_est_conserve():
    """Bug #4231 — les titres type « Relire l'annexe » disparaissaient de l'export."""
    tache = Tache(id=1, titre="Relire l'annexe")

    lignes = exporter([tache])

    assert "Relire l'annexe" in lignes[0]
```

Trois éléments à ne pas négliger :

| Élément | Rôle |
|---|---|
| Le **numéro de ticket** en docstring | relie le test à l'historique de l'incident |
| Le **cas réel** (`Relire l'annexe`) | pas `"a'b"` — le vrai cas est plus parlant |
| Le nom du test | décrit le comportement, pas le bug |

---

# Élargir : le bug appartient-il à une famille ?

Un bug isolé est rare. Une apostrophe qui casse le formatage suggère une famille
entière de caractères mal gérés.

```python
@pytest.mark.parametrize(
    "titre",
    [
        "Relire l'annexe",       # apostrophe — le bug signalé
        "Mettre-à-jour",         # tiret
        "Écrire le bilan",       # accent en initiale
        'Lire "Python avancé"',  # guillemets
        "Bilan  Q3",             # double espace
    ],
)
def test_titres_speciaux_sont_conserves(titre):
    assert titre in exporter([Tache(id=1, titre=titre)])[0]
```

> **🎯 En pratique** : cinq minutes de plus, et vous corrigez quatre bugs qui
> n'ont pas encore été signalés. C'est le meilleur retour sur investissement de
> toute la journée.

---

# Tests de caractérisation : capturer l'existant

Sur du code legacy, vous n'avez pas de spécification. Vous avez un
**comportement observé**, et il faut le figer avant d'y toucher.

```python
def test_caracterisation_calcul_indice_v1():
    """Fige le comportement actuel — NON validé par le métier.

    Objectif : détecter tout changement pendant le refactoring.
    À revoir une fois la règle réellement spécifiée.
    """
    assert calculer_indice(RELEVE_REFERENCE) == pytest.approx(72.4)
```

La différence avec un test classique est **d'intention** :

| | Test unitaire | Test de caractérisation |
|---|---|---|
| Affirme | ce qui **doit** être | ce qui **est** |
| Source | la spécification | l'exécution du code actuel |
| Si le code est faux | le test est rouge | **le test fige le bug** |
| Durée de vie | permanente | jusqu'à spécification du besoin |

---

# Écrire un test de caractérisation quand on ignore la réponse

La technique est délibérément mécanique :

```python
def test_caracterisation():
    assert calculer_indice(RELEVE_REFERENCE) == 0     # valeur arbitraire
```

```bash
E   assert 72.4 == 0
```

Le message d'erreur **vous donne** la valeur actuelle. Vous la recopiez dans le
test, qui devient vert. Le filet de sécurité est posé.

> **⚠️ Piège** : ne présentez jamais un test de caractérisation comme une
> validation métier. Il documente un comportement, y compris ses bugs. La
> docstring doit le dire explicitement, sinon quelqu'un « corrigera » un jour un
> test qui protégeait en réalité un bug connu.

Nous approfondirons cette technique au Jour 4, sur du code de 300 lignes.

---

# Construire un filet avant de refactoriser

Avant de toucher à un composant existant, la question n'est pas
*« ai-je assez de tests ? »* mais :

> **Quels changements de comportement dois-je être certain de détecter ?**

| Niveau du filet | Ce qu'il détecte | Coût |
|---|---|---|
| Un test de bout en bout sur un jeu réel | tout écart global | faible |
| + des tests de caractérisation par fonction | l'endroit de l'écart | moyen |
| + des tests unitaires sur les règles métier | l'écart **et** sa cause | élevé |

En pratique, on construit **de haut en bas** : d'abord un test global qui rougit
si quoi que ce soit change, puis on descend en précision dans les zones qu'on
s'apprête à modifier.

---

# À retenir

> **1.** Un bug corrigé sans test est un bug qui reviendra. Écrivez le test
> **avant** la correction, pour l'avoir vu rouge.

> **2.** Élargissez systématiquement le cas signalé à sa famille : c'est là que
> se cachent les bugs pas encore remontés.

> **3.** Un test de caractérisation fige le comportement **actuel**, bugs
> compris. Sa docstring doit le dire, sous peine d'induire en erreur le
> prochain lecteur.
