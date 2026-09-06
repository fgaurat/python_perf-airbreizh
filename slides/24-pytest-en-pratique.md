---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — pytest en pratique"
---

<!-- _class: lead -->

# 4. pytest en pratique

*Les fonctionnalités qui servent tous les jours*

---

# Le premier test

Aucune classe à hériter, aucune méthode `setUp`, aucun `assertEqual`.

```python
# tests/unitaires/test_calculs.py
from mesures.calculs import moyenne

def test_moyenne_de_trois_valeurs():
    assert moyenne([10.0, 20.0, 30.0]) == 20.0
```

```bash
$ pytest
tests/unitaires/test_calculs.py .                                  [100%]
1 passed in 0.01s
```

Une fonction, un `assert`. pytest découvre le reste par convention :
fichiers `test_*.py`, fonctions `test_*`.

---

# L'introspection des assertions

Le simple `assert` de Python suffit, parce que pytest **réécrit** l'expression
pour vous montrer les valeurs intermédiaires en cas d'échec.

```
    def test_moyenne_de_trois_valeurs():
>       assert moyenne([10.0, 20.0, 30.0]) == 20.0
E       assert 21.5 == 20.0
E        +  where 21.5 = moyenne([10.0, 20.0, 30.0])
```

Sur des structures, la comparaison est détaillée automatiquement :

```
E       AssertionError: assert {'haute': 12, 'basse': 8} == {'haute': 12, 'basse': 9}
E         Common items: {'haute': 12}
E         Differing items: {'basse': 8} != {'basse': 9}
```

> **⚠️ Piège** : `assert resultat_est_valide` où la variable est un booléen déjà
> calculé n'affiche que `assert False`. Assertez sur des **valeurs**.

---

# Lancer pytest : les options qui servent

| Commande | Usage |
|---|---|
| `pytest` | tout |
| `pytest tests/unitaires` | un dossier |
| `pytest tests/test_calculs.py::test_moyenne` | un test précis |
| `pytest -k "moyenne and not vide"` | par motif sur le nom |
| `pytest -m "not integration"` | par marqueur |
| `pytest -x` | s'arrêter au premier échec |
| `pytest --lf` | rejouer uniquement les derniers échecs |
| `pytest --ff` | rejouer les échecs **d'abord**, puis le reste |
| `pytest -q` / `-v` | sortie compacte / détaillée |
| `pytest --durations=10` | les 10 tests les plus lents |

> **🎯 En pratique** : la boucle de travail réelle est
> `pytest --lf -x -q` — on ne rejoue que ce qui était rouge, et on s'arrête au premier.

---

# Comparer des flottants : `pytest.approx`

`0.1 + 0.2 == 0.3` est faux en virgule flottante. Sur du code scientifique,
c'est la première source de tests faussement rouges.

<div class="cols">
<div>

**Fragile**

```python
assert moyenne([0.1, 0.2]) == 0.15000000000000002
```

**Correct**

```python
assert moyenne([0.1, 0.2]) == pytest.approx(0.15)
```

</div>
<div>

**Tolérance explicite**

```python
# tolérance relative de 1 %
assert x == pytest.approx(12.4, rel=1e-2)

# tolérance absolue
assert x == pytest.approx(0.0, abs=1e-9)
```

**Sur des structures**

```python
assert resultats == pytest.approx([1.0, 2.0])
assert stats == pytest.approx({"moy": 1.0})
```

</div>
</div>

> `approx` accepte listes, tuples, dictionnaires et tableaux `numpy`.

---

# Tester les exceptions

```python
def test_serie_vide_est_refusee():
    with pytest.raises(SerieVide):
        moyenne([])
```

Le test échoue si **aucune** exception n'est levée, ou si c'est une autre.

Vérifier aussi le **message**, avec `match` (une expression régulière) :

```python
def test_le_message_nomme_le_parametre_fautif():
    with pytest.raises(ParametreInvalide, match=r"taille_fenetre = 511"):
        valider({"taille_fenetre": 511})
```

Inspecter l'exception elle-même :

```python
def test_la_cause_est_conservee():
    with pytest.raises(ParametresIllisibles) as info:
        charger(chemin_casse)
    assert isinstance(info.value.__cause__, json.JSONDecodeError)
```

---

# `pytest.raises` — les erreurs classiques

<div class="cols">
<div>

**Bloc trop large** ❌

```python
with pytest.raises(SerieVide):
    donnees = preparer()      # peut lever
    moyenne(donnees)          # ce qu'on teste
```

Si `preparer()` lève `SerieVide`, le test
passe pour la mauvaise raison.

**Ciblé** ✓

```python
donnees = preparer()
with pytest.raises(SerieVide):
    moyenne(donnees)
```

</div>
<div>

**Trop générique** ❌

```python
with pytest.raises(Exception):
    moyenne([])
```

Un `TypeError` accidentel ferait
passer le test.

**Précis** ✓

```python
with pytest.raises(SerieVide, match="vide"):
    moyenne([])
```

</div>
</div>

> **⚠️ Piège** : `pytest.raises(ValueError)` attrape aussi ses sous-classes.
> Pour vos exceptions métier, c'est un avantage — à condition que la hiérarchie
> soit voulue.

---

# Les fixtures : préparer sans dupliquer

Une fixture est une fonction décorée dont le **nom** devient un paramètre de test.
pytest la résout automatiquement.

```python
@pytest.fixture
def grille() -> GrilleTarifaire:
    """Grille de référence utilisée par la plupart des tests."""
    return GrilleTarifaire(prix_hp=0.25, prix_hc=0.20, abonnement=12.60)


def test_facture_heures_pleines(grille):
    assert grille.montant(hp=100, hc=0) == pytest.approx(25.0)


def test_facture_heures_creuses(grille):
    assert grille.montant(hp=0, hc=100) == pytest.approx(20.0)
```

Chaque test reçoit une instance **fraîche** : pas d'état partagé entre tests,
donc pas de dépendance à l'ordre d'exécution.

---

# Fixtures : nettoyage avec `yield`

Ce qui est écrit après le `yield` s'exécute à la fin du test, **même s'il échoue**.

```python
@pytest.fixture
def base_temporaire(tmp_path):
    connexion = sqlite3.connect(tmp_path / "test.db")
    connexion.execute("CREATE TABLE mesures (id INTEGER, valeur REAL)")
    yield connexion              # ← le test s'exécute ici
    connexion.close()            # ← toujours exécuté
```

C'est l'équivalent de `setUp` / `tearDown`, en une seule fonction lisible.

> **🎯 En pratique** : pour un fichier ou un dossier temporaire, n'écrivez pas
> de fixture — `tmp_path` fait déjà le travail, et le nettoyage aussi.

---

# Pourquoi le nettoyage s'exécute même en cas d'échec

La fixture `yield` est un **gestionnaire de contexte** : c'est le mécanisme de
`with`, que vous utilisez déjà pour les fichiers.

<div class="cols">
<div>

**Ce que fait `with`**

```python
with open(chemin) as f:      # __enter__
    traiter(f)
                             # __exit__ — même si
                             # traiter() a levé
```

Le fichier est fermé quoi qu'il arrive :
retour normal, exception, `return`.

</div>
<div>

**Le vôtre, en trois lignes**

```python
from contextlib import contextmanager

@contextmanager
def connexion_temporaire(dsn):
    conn = connect(dsn)
    try:
        yield conn           # ← le bloc with
    finally:
        conn.close()         # ← toujours exécuté
```

</div>
</div>

> **🎯 En pratique** : une fixture `yield` et un `@contextmanager` s'écrivent
> pareil. Écrivez le second dans votre librairie — vos consommateurs l'utiliseront
> avec `with`, et vos tests l'utiliseront comme fixture. Une seule implémentation.

---

# Fixtures : les portées (`scope`)

| Portée | Créée | Usage typique |
|---|---|---|
| `function` (défaut) | à chaque test | tout ce qui est modifiable |
| `class` | une fois par classe | rare |
| `module` | une fois par fichier | une connexion lente en lecture seule |
| `session` | une fois pour tout | un serveur de test, une image Docker |

```python
@pytest.fixture(scope="session")
def schema_reference() -> dict:
    """Chargé une seule fois : lecture seule, coûteux à construire."""
    return json.loads(Path("tests/donnees/schema.json").read_text())
```

> **⚠️ Piège** : une fixture de portée large qui retourne un objet **mutable**
> réintroduit exactement le problème d'état partagé que les fixtures évitent.
> Portée large ⇒ objet en lecture seule.

---

# Fixtures partagées et composées

Une fixture placée dans `conftest.py` est disponible dans tout le dossier, sans import.

```python
# tests/conftest.py
@pytest.fixture
def dossier_donnees() -> Path:
    return Path(__file__).parent / "donnees"


@pytest.fixture
def releve_minimal(dossier_donnees) -> list[Releve]:
    """Trois lignes couvrant une heure pleine, une creuse et une borne."""
    return lire_releve(dossier_donnees / "releve_minimal.csv")
```

Une fixture peut en demander d'autres : pytest construit le graphe et
n'instancie que ce qui est nécessaire au test en cours.

```bash
pytest --fixtures        # liste toutes les fixtures visibles, avec leur docstring
```

---

# La paramétrisation

Le même test, sur plusieurs jeux de données. C'est le mécanisme le plus rentable
de pytest sur du code de calcul.

<div class="cols">
<div>

**Sans** ❌

```python
def test_hc_22h():
    assert est_heure_creuse(22)

def test_hc_23h():
    assert est_heure_creuse(23)

def test_hc_3h():
    assert est_heure_creuse(3)
```

</div>
<div>

**Avec** ✓

```python
@pytest.mark.parametrize(
    "heure", [22, 23, 0, 3, 5]
)
def test_heures_creuses(heure):
    assert est_heure_creuse(heure)
```

</div>
</div>

Chaque valeur produit un **test distinct** : cinq lignes dans le rapport, cinq
échecs possibles indépendants. Ce n'est pas une boucle — une boucle s'arrête au
premier échec et cache les suivants.

---

# Paramétrisation : plusieurs arguments

```python
@pytest.mark.parametrize(
    ("hp", "hc", "attendu"),
    [
        (100.0,   0.0, 25.16),
        (  0.0, 100.0, 20.32),
        (  0.0,   0.0,  0.00),      # cas limite : aucune consommation
        (  0.5,   0.5,  0.22),      # arrondi au centime
    ],
)
def test_montant_de_consommation(hp, hc, attendu):
    assert montant(hp, hc) == pytest.approx(attendu, abs=0.005)
```

Le tableau se lit comme une **spécification** : chaque ligne est un cas métier,
avec son résultat de référence.

> **🎯 En pratique** : c'est le format idéal pour faire relire une règle de
> calcul par un expert métier qui ne lit pas Python. Il lit le tableau.

---

# Paramétrisation : noms de cas lisibles

Par défaut, pytest génère `test_montant[100.0-0.0-25.16]`. Sur des données
complexes, cela devient illisible.

```python
@pytest.mark.parametrize(
    ("entree", "attendu"),
    [
        pytest.param("12,4", 12.4, id="virgule_decimale"),
        pytest.param("12.4", 12.4, id="point_decimal"),
        pytest.param(" 12.4 ", 12.4, id="espaces_autour"),
        pytest.param("1 2 4", None, id="espaces_internes_refuses"),
    ],
)
def test_parser_valeur(entree, attendu):
    ...
```

```
tests/test_parsing.py::test_parser_valeur[virgule_decimale] PASSED
tests/test_parsing.py::test_parser_valeur[espaces_internes_refuses] FAILED
```

L'identifiant apparaît dans le rapport CI : il doit dire **quel cas métier** a cassé.

---

# Fichiers temporaires : `tmp_path`

`tmp_path` est une fixture native qui fournit un `Path` vers un dossier vide,
unique au test, supprimé ensuite.

```python
def test_ecriture_du_rapport(tmp_path):
    destination = tmp_path / "rapport.csv"

    ecrire_rapport(destination, [Mesure(8, 12.4)])

    lignes = destination.read_text().splitlines()
    assert lignes[0] == "heure,valeur"
    assert lignes[1] == "8,12.4"
```

| Fixture | Contenu |
|---|---|
| `tmp_path` | un `Path` vers un dossier vide, par test |
| `tmp_path_factory` | une fabrique, pour une fixture de portée `session` |

> **⚠️ Piège** : n'écrivez **jamais** dans le dossier du projet depuis un test.
> Les tests deviennent dépendants de l'ordre, et polluent le dépôt Git.

---

# Marqueurs

Trois usages, du plus ponctuel au plus structurant :

```python
@pytest.mark.skip(reason="fonctionnalité retirée en v2")
def test_ancien_format(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="chemins POSIX")
def test_permissions(): ...

@pytest.mark.xfail(reason="bug #4231, corrigé en v1.4", strict=True)
def test_arrondi_a_la_borne(): ...
```

`xfail` avec `strict=True` est particulièrement utile : le test **doit** échouer.
S'il se met à passer, la suite rougit — et vous savez que le bug est corrigé.

```python
@pytest.mark.integration          # marqueur maison, déclaré dans pyproject.toml
def test_lecture_reelle(): ...
```

> Déclarez toujours vos marqueurs maison dans `[tool.pytest.ini_options]`,
> sinon une faute de frappe passe inaperçue.

---

# Bonnes pratiques d'écriture

| Règle | Pourquoi |
|---|---|
| **Un test = un comportement** | Un échec désigne une cause, pas trois |
| **Pas de logique dans un test** | Un `if` dans un test est un bug potentiel non testé |
| **Pas de dépendance entre tests** | Chaque test doit passer seul et dans le désordre |
| **Nommer par le comportement** | Le nom est ce qu'on lit en CI |
| **Une assertion principale** | Plusieurs `assert` liés au même comportement : oui. Trois comportements : non. |
| **Des données minimales** | Trois lignes qui montrent le cas, pas 200 extraites de la production |

Vérification utile de temps en temps :

```bash
pytest --lf -x -q               # la boucle de travail : rejouer ce qui était rouge
pytest tests/unitaires -q       # la suite unitaire doit tenir en secondes
```

> Si votre suite unitaire dépasse **10 secondes**, elle contient des tests
> d'intégration mal étiquetés.

---

# À retenir

> **1.** `assert` simple, `pytest.approx` pour les flottants, `pytest.raises`
> avec `match` pour les erreurs. Ces trois-là couvrent 80 % des besoins.

> **2.** Les **fixtures** éliminent la duplication de préparation ; la
> **paramétrisation** transforme un tableau de cas métier en tests indépendants.

> **3.** `tmp_path` pour tout ce qui touche au disque. Un test qui écrit dans le
> projet est un test qui cassera les autres.
