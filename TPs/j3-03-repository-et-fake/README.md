# TP j3-03 — Repository, fake et test de contrat

**Durée : 60 min**

## Contexte

`depart/suivi/rapport.py` produit le rapport hebdomadaire de la todo-list
d'équipe : tâches en retard, avancement d'un projet, personnes surchargées,
tâches dormantes.

Les quatre règles métier sont écrites **en SQL** :

```python
cur.execute("SELECT titre FROM taches WHERE terminee = 0 AND echeance < ? ...")
```

Conséquences :

- personne ne peut relire la règle sans lire du SQL ;
- tester « une échéance exactement au jour du rapport » exige d'insérer une
  ligne en base ;
- `avancement` renvoie `0` pour un projet **inconnu** — indiscernable d'un
  projet où rien n'est fait ;
- `avancement` doit traiter le `NULL` que `SUM()` renvoie sur une table vide.

## Objectif

Remonter les règles métier hors du SQL, puis garantir que le fake de test reste
fidèle à la base réelle.

## Étapes

### 1. Le modèle (10 min)

`suivi/modele.py` : une `@dataclass(frozen=True) Tache` avec de **vraies**
dates (`date`, pas `str`) et un vrai booléen, plus deux méthodes qui portent
les règles élémentaires :

```python
def est_en_retard(self, jour: date) -> bool: ...


def est_dormante(self, jour: date, jours: int = 30) -> bool: ...
```

Ajoutez `ErreurTodo`, `TacheInconnue` et `ProjetInconnu`.

### 2. Le contrat (5 min)

`suivi/ports.py` : un `Protocol DepotTaches` avec **deux méthodes
seulement** — `toutes()` et `par_id()`.

> Pourquoi pas une méthode `en_retard()` dans le dépôt ? Parce que ce serait
> remettre la règle métier dans la couche d'accès aux données.

### 3. Les deux implémentations (15 min)

- `depot_sqlite.py` — le seul fichier contenant du SQL. Il lit des lignes et
  construit des `Tache` : c'est lui qui convertit `"2026-09-01"` en `date` et
  `1` en `True`. **Aucune règle métier.**
- `depot_memoire.py` — un **fake** : un dictionnaire indexé par identifiant.

### 4. Le métier (10 min)

Réécrivez `Rapport` : il reçoit un `DepotTaches` et n'écrit plus une ligne de
SQL. Les quatre règles deviennent des compréhensions de listes.

Profitez-en pour corriger le `return 0` de `avancement`.

### 5. Le test de contrat (10 min)

C'est le cœur du TP. Un fake **dérive** avec le temps : il finit par se comporter
différemment de la vraie base, et vos tests deviennent des mensonges.

Écrivez les assertions **une seule fois**, puis rejouez-les sur les deux
implémentations :

```python
class ContratDepotTaches:
    def test_par_id_retrouve_une_tache(self, depot):
        assert depot.par_id(2).titre == "Déployer"

    def test_par_id_inconnu(self, depot):
        with pytest.raises(TacheInconnue):
            depot.par_id(42)


class TestDepotEnMemoire(ContratDepotTaches):
    @pytest.fixture
    def depot(self, depot_memoire):
        return depot_memoire


class TestDepotSqlite(ContratDepotTaches):
    @pytest.fixture
    def depot(self, depot_sqlite):
        return depot_sqlite
```

Sept assertions écrites, quatorze tests exécutés. Vérifiez en particulier les
**types** : le fake rend des `date`, la base doit en rendre aussi.

> Pour la fixture SQLite, utilisez `sqlite3.connect(":memory:")` : la base est
> créée et détruite en quelques microsecondes, pour chaque test.

### 6. Les tests métier (10 min)

Sur le fake uniquement. Écrivez en particulier les **bornes**, impossibles à
tester commodément avant :

- une échéance **exactement** au jour du rapport ;
- une personne avec **exactement** le nombre de tâches du seuil ;
- une tâche créée il y a **exactement** trente jours ;
- un dépôt vide ;
- un projet inconnu.

## Critères de réussite

- Le mot `SELECT` n'apparaît que dans `depot_sqlite.py` — écrivez le test.
- Les assertions du contrat sont écrites **une fois** et exécutées **deux fois**.
- Un test prouve qu'une tâche due aujourd'hui n'est pas en retard.
- `avancement("inexistant")` lève au lieu de renvoyer `0`.
- Les tests métier s'exécutent sans base de données.

## Pour aller plus loin

Introduisez volontairement une divergence dans le fake — par exemple, faites-lui
renvoyer `None` au lieu de lever `TacheInconnue`, ou stocker l'échéance en
`str`. Quel test rougit ? Et dans quelle classe ?

C'est exactement ce qui se produit dans la vraie vie, six mois plus tard, quand
quelqu'un « simplifie » le fake.

## Corrigé

`corrige/` — 5 modules, 31 tests (dont 14 issus des 7 assertions du contrat).

```bash
uv run pytest j3-03-repository-et-fake/corrige -v
```
