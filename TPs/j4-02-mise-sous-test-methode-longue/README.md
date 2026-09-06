# TP j4-02 — Mettre sous test une méthode longue

**Durée : 90 min — le TP central de la journée**

## Contexte

`depart/scolaire/bulletin.py` génère le bulletin trimestriel d'un élève.
**190 lignes** dans une seule fonction, huit ans d'histoire, quatre niveaux,
des options à bonus, deux formats d'export, aucun test.

Elle fonctionne. Elle est en production dans trois établissements. Vous devez y
ajouter le niveau « 2nde » et les absences justifiées pour la rentrée.

Lisez-la. Comptez les responsabilités : validation, moyennes par matière,
moyenne générale, bonus des options, mention, rang, absences, tendance,
appréciation, assemblage, export, affichage. **Douze.**

## Objectif

La démonter en six étapes, sans jamais changer un seul résultat.

## Règle absolue de ce TP

> **Vous ne corrigez aucun bug.**

Vous allez en trouver — il y en a au moins cinq. Notez-les dans
`depart/BUGS.md`. Un refactoring qui corrige des bugs en même temps est un
refactoring invérifiable : on ne sait plus si un test rougit à cause de la
transformation ou de la correction.

## Étapes

### Étape 1 — Le filet de sécurité (15 min)

Avant toute modification, il faut pouvoir détecter un changement de résultat.

**Copiez** `scolaire/bulletin.py` en `scolaire/bulletin_v1.py`. Vous garderez
les deux versions pendant tout le refactoring, et vous les comparerez :

```python
@pytest.mark.parametrize(
    ("classe", "precedente", "notes"),
    list(itertools.product(CLASSES, PRECEDENTES, NOTES)),
)
def test_les_deux_versions_donnent_le_meme_bulletin(classe, precedente, notes):
    donnees = eleve(classe=classe, moyenne_precedente=precedente, notes=notes)
    assert generer_bulletin(dict(donnees), "2026-T2") == generer_bulletin_v1(
        dict(donnees), "2026-T2"
    )
```

Avec 4 classes × 6 moyennes précédentes × 6 jeux de notes, vous obtenez
**144 cas** pour quinze lignes de code. C'est bien plus que ce que vous
écririez à la main, et c'est exactement le filet dont vous avez besoin.

Choisissez les jeux de notes pour couvrir les branches : une seule matière,
un avertissement, des options, des barèmes sur 10 et sur 50, une matière avec
une faute de frappe, une note absente.

> **🎯 Le point clé** : ce test compare deux implémentations. Il ne dit pas si
> le résultat est *juste* — il dit s'il a *changé*. C'est tout ce qu'on demande
> à un filet de refactoring.

### Étape 2 — Cartographier (10 min)

Annotez chaque bloc de la fonction avec trois informations :

| Bloc | Entrées | Sorties | Effet de bord |
|---|---|---|---|
| validation | `eleve`, `trimestre` | classe | lève |
| moyennes par matière | `notes` | moyennes, détail | `print` si verbose |
| … | | | |

Les blocs **sans effet de bord** sont ceux que vous extrairez en premier :
l'extraction y est mécanique et sans risque.

### Étape 3 — Extraire les fonctions pures (25 min)

Une à la fois. Après chacune : tests verts, commit.

Ordre suggéré, du plus simple au plus impliqué :

1. `mention(moyenne_finale) -> str`
2. `rang(moyenne_finale, moyennes_classe) -> int`
3. `tendance(moyenne_finale, precedente) -> str`
4. `analyser_trimestre(trimestre) -> Periode`
5. `moyenne_matiere(matiere, notes) -> MoyenneMatiere | None`
6. `moyenne_generale(moyennes) -> float` et `bonus_options(moyennes) -> float`
7. `compter_absences(absences) -> Absences`
8. `appreciation(mention, tendance, avertissement) -> str`

> Créez au passage `scolaire/modele.py` pour les constantes, les `dataclass` et
> les exceptions. Ce module ne doit **rien** importer du projet : c'est ce qui
> garantit l'absence de cycle. Faites dériver votre exception de `ValueError`,
> pour ne pas casser les appelants qui l'attrapent déjà.

### Étape 4 — Tester le noyau (15 min)

Les règles sont maintenant accessibles. Écrivez leurs tests unitaires — et
surtout leurs **bornes**, jusqu'ici hors d'atteinte :

- exactement 16,00 de moyenne : « Félicitations » ou « Compliments » ?
- exactement 10 en option : du bonus ou pas ?
- exactement 10 demi-journées d'absence : avertissement ou pas ?
- un écart de +0,50 avec le trimestre précédent : « en progrès » ?
- deux élèves à égalité : quel rang ?

Chacun de ces tests aurait exigé, avant, de construire un élève complet et de
lire une valeur au fond d'un dictionnaire de quinze clés. Plusieurs d'entre eux
vont vous surprendre : **ne corrigez pas**, notez dans `BUGS.md`, et écrivez le
test qui fige le comportement actuel, avec une docstring qui renvoie au bug.

### Étape 5 — Isoler les I/O (5 min)

Sortez l'export dans `scolaire/export.py`, et séparez la **sérialisation**
(pure) de l'**écriture** (I/O) :

```python
def en_json(bulletin: dict) -> str: ...  # pur, testable sans fichier
def exporter(bulletin, chemin, format_export): ...  # écrit
```

`generer_bulletin` ne doit plus écrire nulle part. Supprimez aussi le paramètre
`verbose` et ses `print` : l'affichage n'est pas la responsabilité d'un calcul.

### Étape 6 — Réduire l'orchestration (5 min, si le temps le permet)

Ce qui reste de `generer_bulletin` ne fait plus qu'appeler les autres et
assembler le dictionnaire final. Vous devriez être passé de 190 lignes à
environ 45.

Relancez le test d'équivalence une dernière fois.

## Critères de réussite

- Le test d'équivalence (144 cas au moins) est vert **à chaque commit**.
- `generer_bulletin` fait moins de 50 lignes et ne calcule plus rien elle-même.
- Chaque règle extraite a ses tests unitaires, bornes comprises.
- `generer_bulletin` n'écrit aucun fichier — un test le prouve.
- `BUGS.md` contient au moins **trois** bugs identifiés et **non corrigés**.

## Indice sur le premier bug

```python
precedente = eleve.get("moyenne_precedente", 0.0)
```

Que vaut la tendance d'un élève au premier trimestre, qui n'a donc pas de
moyenne précédente ?

## Discussion (10 min)

Comparez vos `BUGS.md`. Puis discutez de la suite : maintenant que les règles
sont isolées et testées, combien de temps prendrait la correction du bug n° 1 —
et combien aurait-elle pris avant ce refactoring ?

## Corrigé

`corrige/` — 4 modules, 242 tests (dont 163 d'équivalence), et un `BUGS.md`
de 7 entrées.

```bash
uv run pytest j4-02-mise-sous-test-methode-longue/corrige -q
```
