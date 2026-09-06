---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Traiter les méthodes longues"
---

<!-- _class: lead -->

# 4. Traiter les méthodes longues

*Démonter 300 lignes sans rien casser*

---

# Pourquoi 300 lignes coûtent cher

Ce n'est pas une question de goût. Trois coûts mesurables :

| Coût | Mécanisme |
|---|---|
| **Combinatoire** | 12 `if` imbriqués = jusqu'à 4 096 chemins. Vos tests en couvrent 5. |
| **Mémoire de travail** | on retient 5 à 7 éléments. Une méthode longue en manipule 40. |
| **Portée des variables** | une variable définie ligne 40 et relue ligne 280 : impossible de savoir ce qui l'a modifiée entre les deux |

Et un quatrième, propre aux librairies :

> Une méthode longue **ne peut pas être testée par morceaux**. Il faut fournir
> toutes ses dépendances pour vérifier une seule de ses règles — ce qui revient
> à monter un environnement de production pour tester une multiplication.

---

# Le seuil qui compte

Pas un nombre de lignes : le moment où **vous devez faire défiler** pour
comprendre le début.

Trois signaux plus fiables qu'un compteur :

| Signal | Ce qu'il révèle |
|---|---|
| Des **commentaires en bannière** (`# --- calcul ---`) | l'auteur a déjà identifié les blocs à extraire |
| Des **variables temporaires réutilisées** (`tmp`, `res`, `d`) | plusieurs traitements distincts partagent un espace |
| Des **paramètres booléens** | la méthode fait deux choses différentes selon l'appel |

> **🎯 En pratique** : les commentaires en bannière sont un cadeau. Quelqu'un a
> fait le travail d'analyse ; il n'a simplement pas fait l'extraction.

---

# La méthode, en six étapes

```
  1. Caractériser        un test de bout en bout sur un jeu réel
     ↓                   → « si je casse quelque chose, je le saurai »

  2. Cartographier       annoter les blocs : entrées, sorties, effets
     ↓

  3. Extraire les        les blocs SANS effet de bord d'abord
     fonctions pures     → chacun devient testable immédiatement
     ↓

  4. Tester le noyau     les règles métier, maintenant accessibles
     ↓

  5. Isoler les I/O      lecture au début, écriture à la fin
     ↓

  6. Réduire l'orchestration   la méthode d'origine ne fait plus qu'appeler
```

À chaque étape : tests verts, commit. Jamais deux étapes à la fois.

---

# Étape 2 — Cartographier avant de couper

Pour chaque bloc, trois questions, notées dans la marge :

| Question | Pourquoi elle compte |
|---|---|
| **Qu'entre-t-il ?** | ce seront les paramètres |
| **Qu'en sort-il ?** | ce sera le type de retour |
| **Que modifie-t-il en dehors ?** | s'il n'y a rien : bloc **pur**, extraction sans risque |

```python
def generer(self, jour):
    # bloc A — lit self.conn                    → I/O, à isoler en 5
    # bloc B — entrée: lignes / sortie: mesures → PUR, à extraire en 3
    # bloc C — entrée: mesures / sortie: indice → PUR, à extraire en 3
    # bloc D — écrit un fichier                 → I/O, à isoler en 5
    # bloc E — envoie un mail                   → effet externe, à injecter
```

> Le bloc C est celui qui porte le risque métier. C'est le premier à extraire
> et le premier à tester — pas le bloc A, qui est le plus visible.

---

# Étape 3 — Extraire les fonctions pures d'abord

<div class="cols">
<div>

**Avant — bloc C, ligne 74 à 100**

```python
def generer(self, jour):
    ...
    notes = []
    for p in SEUILS:
        if ligne.get(p) is not None:
            notes.append(ligne[p] / SEUILS[p])
    if notes:
        ligne["indice"] = round(
            min(100, max(notes) * 50), 1)
    else:
        ligne["indice"] = 0
    ...
```

</div>
<div>

**Après**

```python
def calculer_indice(
    moyennes: dict[str, float | None],
    seuils: dict[str, float],
) -> float | None:
    """Indice global, ou None si aucune mesure."""
    notes = [
        moyennes[p] / seuils[p]
        for p in seuils
        if moyennes.get(p) is not None
    ]
    if not notes:
        return None            # ← décision métier explicitée
    return round(min(100, max(notes) * 50), 1)
```

</div>
</div>

L'extraction a rendu visible une **décision métier cachée** : « pas de mesure »
valait `0`, c'est-à-dire la meilleure note possible. Ce n'était pas un choix.

---

# Étape 5 — Isoler les I/O aux extrémités

La forme cible d'un traitement, quelle que soit sa taille d'origine :

```python
def generer(self, jour: date, sortie: Path) -> Rapport:
    """Orchestration : lire, calculer, écrire. Rien d'autre."""
    mesures = self._depot.du_jour(jour)          # ← une lecture, au début
    resultats = analyser(mesures, self._seuils)  # ← tout le métier, pur
    ecrire_rapport(sortie, resultats)            # ← une écriture, à la fin
    return Rapport(jour, len(resultats))
```

```
   lecture  →  [ ============ métier pur ============ ]  →  écriture
   1 ligne         testable sans rien du tout              1 ligne
```

> **🎯 En pratique** : visez cette forme même quand vous ne l'atteindrez pas
> complètement. Chaque ligne de calcul qui remonte dans la zone centrale est une
> ligne devenue testable.

---

# Introduire un objet de configuration

Les méthodes longues accumulent les paramètres. Au-delà de quatre, regroupez.

<div class="cols">
<div>

**Avant**

```python
def generer(self, jour=None, format="csv",
            envoyer=True, verbose=False,
            seuil=None, destinataires=None,
            couverture=3, strict=False):
```

Huit paramètres, quatre booléens.
Tout appel est illisible :
`generer(j, "csv", False, True, ...)`

</div>
<div>

**Après**

```python
@dataclass(frozen=True)
class OptionsRapport:
    format: str = "csv"
    envoyer: bool = True
    seuil: float | None = None
    destinataires: tuple[str, ...] = ()


def generer(self, jour: date,
            options: OptionsRapport = OptionsRapport()):
```

</div>
</div>

Le test devient explicite : `OptionsRapport(envoyer=False, seuil=25.0)`.
Et le jour où une option s'ajoute, **aucune signature ne change**.

---

# Vérifier la non-régression à chaque étape

Le filet posé à l'étape 1 doit être **exécuté après chaque transformation** —
pas à la fin.

```bash
# La boucle, littéralement :
uv run pytest tests/caracterisation -q && git commit -am "extrait calculer_indice"
```

Trois protections complémentaires :

| Protection | Détecte |
|---|---|
| Le test de caractérisation | tout changement de résultat |
| `git diff` avant commit | les modifications non intentionnelles |
| Comparer ancienne et nouvelle version | les écarts sur des entrées variées |

```python
def test_equivalence_ancienne_nouvelle():
    """Le temps du refactoring, on garde les deux et on les compare."""
    for releve in JEUX_DE_TEST:
        assert nouvelle(releve) == pytest.approx(ancienne(releve))
```

La dernière technique est particulièrement efficace sur du calcul scientifique.

---

# À retenir

> **1.** Extrayez les blocs **purs en premier** : ils deviennent testables
> immédiatement et sans risque, et ce sont eux qui portent le risque métier.

> **2.** Un commentaire en bannière est un nom de fonction en attente. Le travail
> d'analyse a déjà été fait par quelqu'un.

> **3.** L'extraction révèle des **décisions métier cachées** — c'est souvent le
> bénéfice principal, avant même la testabilité.
