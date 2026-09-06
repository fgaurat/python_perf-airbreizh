---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Tester les accès externes"
---

<!-- _class: lead -->

# 4. Tester les accès externes

*Bases, fichiers, APIs, flux : la stratégie avant l'outil*

---

# Le problème commun

Base de données, fichier, API HTTP, flux temps réel, données distantes : ces
dépendances partagent quatre propriétés qui les rendent hostiles aux tests.

| Propriété | Conséquence |
|---|---|
| **Lentes** | la suite passe de 2 s à 4 min, on cesse de la lancer |
| **Indisponibles** | rouge le lundi matin, vert le mardi, sans changement de code |
| **Partagées** | deux tests concurrents se marchent dessus |
| **Difficiles à mettre en panne** | on ne teste jamais le chemin d'erreur |

> La bonne question n'est pas « comment mocker ma base ? » mais
> **« quelle part de mon code a réellement besoin de la base ? »**

Dans un module bien découpé, la réponse est : quelques dizaines de lignes.

---

# La stratégie : séparer avant de simuler

```
   AVANT                              APRÈS

   ┌──────────────────┐               ┌──────────────────┐
   │  calcul          │               │  calcul métier   │  ← testé sans rien
   │  + requête SQL   │               └────────┬─────────┘
   │  + parsing       │                        │ interface
   │  + écriture      │               ┌────────┴─────────┐
   └──────────────────┘               │  adapter SQL     │  ← testé contre
   il faut une base pour              └──────────────────┘     une vraie base,
   tester la moindre formule                                   une fois
```

| Ce qu'on teste | Comment | Combien de tests |
|---|---|---|
| Le calcul métier | directement, en mémoire | des dizaines |
| L'adapter | contre la vraie ressource | quelques-uns |
| Le branchement | un fake en mémoire | quelques-uns |

---

# Les sept stratégies disponibles

| Stratégie | Principe | Quand |
|---|---|---|
| **Séparer métier / I/O** | extraire une fonction pure | **toujours, en premier** |
| **Injection de dépendance** | recevoir la ressource en paramètre | dès que possible |
| **Adapter** | traduire l'API externe en une interface à vous | API tierce, format exotique |
| **Repository** | cacher totalement l'origine des données | accès à des données persistées |
| **Service** | regrouper l'orchestration d'un cas d'usage derrière une fonction ou une classe | plusieurs adapters à coordonner |
| **Fake en mémoire** | une implémentation simplifiée mais réelle | pour tester tout ce qui consomme |
| **Fichier / base de test** | une vraie ressource, minuscule et jetable | pour tester l'adapter lui-même |

Les deux premières ne coûtent rien et suppriment la majorité du besoin de
doubles. Les patterns viennent après, quand elles ne suffisent plus.

---

# Cas 1 — Les fichiers

C'est le plus simple, et pourtant celui qu'on mocke le plus inutilement.

<div class="cols">
<div>

**Sur-mocké** ❌

```python
@patch("builtins.open", mock_open(read_data="a,b\n1,2"))
def test_lire():
    assert lire("x.csv") == [{"a": "1", "b": "2"}]
```

Fragile, illisible, et ne teste ni
l'encodage, ni les fins de ligne,
ni les fichiers absents.

</div>
<div>

**Avec un vrai fichier** ✓

```python
def test_lire(tmp_path):
    chemin = tmp_path / "x.csv"
    chemin.write_text("a,b\n1,2\n", encoding="utf-8")
    assert lire(chemin) == [{"a": "1", "b": "2"}]
```

`tmp_path` est rapide (quelques
millisecondes), isolé, et teste
le **vrai** comportement.

</div>
</div>

> **🎯 En pratique** : ne mockez jamais le système de fichiers. Utilisez
> `tmp_path`. Et faites que vos fonctions acceptent un `Path` — ou mieux, un
> objet fichier déjà ouvert, ce qui les rend testables avec `io.StringIO`.

---

# Cas 2 — Les bases de données

Trois niveaux, du moins au plus coûteux :

```python
# 1. Le métier ne connaît pas la base — c'est ici que sont les règles
def en_retard(taches: list[Tache], jour: date) -> list[str]:
    return sorted(t.titre for t in taches if not t.terminee and t.echeance < jour)
```

```python
# 2. Un Repository cache l'origine ; le test fournit un fake en mémoire
class DepotEnMemoire:
    def __init__(self, taches): self._taches = taches
    def du_projet(self, projet): return [t for t in self._taches if t.projet == projet]
```

```python
# 3. L'adapter réel est testé contre une vraie base — SQLite en mémoire
@pytest.fixture
def base():
    connexion = sqlite3.connect(":memory:")
    connexion.executescript(SCHEMA)
    yield connexion
    connexion.close()
```

> SQLite en mémoire s'ouvre en moins d'une milliseconde. Pour du PostgreSQL,
> une image jetable en CI joue le même rôle — quelques tests, pas des centaines.

---

# Cas 3 — Les APIs HTTP

<div class="cols">
<div>

**Ce qu'il faut éviter**

```python
def recuperer(projet):
    r = requests.get(f"{URL}/{projet}")
    return [t["titre"] for t in r.json()["taches"]]
```

Le parsing, l'URL et le transport sont
soudés. Tester le parsing exige de
mocker `requests`.

</div>
<div>

**Séparer transport et interprétation**

```python
def interpreter(charge: dict) -> list[str]:
    """Fonction pure — testable sans réseau."""
    if "taches" not in charge:
        raise ReponseInvalide(charge)
    return [t["titre"] for t in charge["taches"]]


def recuperer(projet, client):
    return interpreter(client.get(f"/{projet}"))
```

</div>
</div>

`interpreter` concentre tout ce qui peut mal tourner — clé absente, type
inattendu, liste vide — et se teste avec des dictionnaires écrits à la main.

Il ne reste alors qu'à mocker le **transport**, dont le comportement est simple :
il répond, ou il échoue.

---

# Cas 4 — Sources distantes et flux

Pour des données volumineuses issues d'un producteur externe (référentiels publics, flux d'événements, exports d'un autre système) :

| Ce qu'on veut vérifier | Comment |
|---|---|
| Le **format** attendu est bien géré | un extrait de 5 lignes, versionné dans `tests/donnees/` |
| Un format **inattendu** est détecté | un extrait volontairement corrompu |
| Le **volume** ne casse rien | un test marqué `lent`, exclu de la boucle rapide |
| Le producteur **a changé son format** | un test d'intégration réel, joué une fois par jour en CI |

> **⚠️ Piège** : le dernier point est le seul que les doubles ne couvrent
> **jamais**. Un fake reproduit ce que vous *croyez* que le service renvoie.
> Prévoyez au moins un test qui parle au vrai service, isolé dans un stage CI
> séparé pour ne pas bloquer les développeurs quand le fournisseur est en panne.

---

# Le test de contrat : garder fake et réel alignés

Un fake dérive avec le temps. Un test de contrat écrit **une seule fois** et
rejoué sur les deux implémentations empêche cette dérive.

```python
class ContratDepot:
    """Tests que toute implémentation de Depot doit satisfaire."""

    def test_relit_ce_qui_a_ete_ecrit(self, depot):
        depot.enregistrer(Tache(1, "Déployer"))
        assert depot.par_id(1) == Tache(1, "Déployer")

    def test_identifiant_inconnu(self, depot):
        with pytest.raises(TacheInconnue):
            depot.par_id(42)


class TestDepotEnMemoire(ContratDepot):
    @pytest.fixture
    def depot(self): return DepotEnMemoire()


class TestDepotSQLite(ContratDepot):
    @pytest.fixture
    def depot(self, base): return DepotSQLite(base)
```

Les mêmes assertions s'exécutent deux fois. Si le fake ment, la comparaison le révèle.

---

# À retenir

> **1.** Avant de choisir un outil de simulation, **déplacez la frontière** :
> une fonction pure extraite est une fonction qui n'a plus besoin de double.

> **2.** Ne mockez jamais le système de fichiers — `tmp_path` est plus simple,
> plus rapide et plus fidèle.

> **3.** Un fake finit toujours par diverger du réel. Un **test de contrat**
> rejoué sur les deux implémentations est la seule protection.
