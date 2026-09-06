# Bugs identifiés pendant le refactoring — non corrigés

Un refactoring ne corrige pas de bug : sinon, on ne sait plus si un test rougit
à cause de la transformation ou de la correction. Ces bugs sont donc **figés par
les tests** et documentés ici, pour être traités séparément.

## 1. Sans moyenne précédente, l'élève est toujours « en progrès »

```python
precedente = eleve.get("moyenne_precedente", 0.0)
```

Au premier trimestre, il n'y a pas de moyenne précédente. La valeur par défaut
`0.0` donne un écart toujours positif : toute appréciation du T1 dit « en
progrès », y compris pour un élève à 4 de moyenne.

*Correctif attendu* : `None` par défaut, et une tendance « première évaluation ».
*Test qui fige le comportement actuel* :
`test_sans_moyenne_precedente_l_eleve_est_toujours_en_progres`.

## 2. « À partir de 16 » est codé comme « strictement plus de 16 »

```python
if moyenne_finale > SEUIL_FELICITATIONS:
```

Le règlement intérieur dit « Félicitations à partir de 16 ». Un élève à 16,00
tout rond reçoit « Compliments ». Même écart pour 14 et 12. La borne basse, en
revanche, est cohérente (`< 8`).

*Test qui fige le comportement actuel* : `test_mention_aux_bornes`.

## 3. Une note supérieure à son barème est acceptée

Une note saisie à 25/20, ou 12/10, produit une moyenne au-dessus de 20 sans
qu'aucune exception ne soit levée. Les notes négatives sont refusées, les notes
trop grandes non — l'asymétrie est le signe d'un oubli.

*Test qui fige le comportement actuel* :
`test_une_note_au_dessus_du_bareme_est_acceptee`.

## 4. Une matière inconnue compte coefficient 1, silencieusement

```python
coef = COEFFICIENTS.get(matiere, 1)
```

Une faute de frappe dans le fichier de saisie — `math` au lieu de `maths` —
transforme une matière à coefficient 4 en matière à coefficient 1. La moyenne
générale est fausse et personne n'est prévenu.

*Correctif attendu* : une erreur explicite listant les matières connues.
*Test qui fige le comportement actuel* :
`test_une_matiere_inconnue_compte_coefficient_un`.

## 5. Les ex aequo sont classés derrière

```python
rang = 1 + sum(1 for m in autres if m >= moyenne_finale)
```

Deux élèves à 14,00 devraient être premiers ex aequo. Avec `>=`, chacun compte
l'autre comme devant lui : les deux sont classés seconds, et personne n'est
premier.

*Test qui fige le comportement actuel* : `test_rang_ex_aequo`.

## 6. Les absences justifiées sont comptées

Le nouveau format d'absence porte un drapeau `justifiee`, ajouté il y a deux
ans. Il n'a jamais été lu : les deux branches du `if isinstance(...)` font
exactement la même chose. Un élève hospitalisé quinze jours reçoit un
avertissement d'assiduité.

*Test qui fige le comportement actuel* : `test_les_absences_justifiees_comptent`.

## 7. Le bonus des options n'est pas plafonné à 20

`moyenne_finale = moyenne_generale + bonus` peut dépasser 20. Un élève à 19,5
avec deux options à 20 obtient 21,5. Le bulletin l'affiche tel quel.
