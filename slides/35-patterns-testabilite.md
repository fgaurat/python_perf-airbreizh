---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Les design patterns au service de la testabilité"
---

<!-- _class: lead -->

# 5. Application des design patterns à la testabilité

*Sept patterns, une même grille de lecture*

---

# La grille de lecture

Pour chacun des sept patterns, quatre questions dans le même ordre :

| | |
|---|---|
| **1. Le problème** | quelle douleur concrète ? |
| **2. La transformation** | qu'est-ce qui change dans le code ? |
| **3. Le test rendu possible** | qu'est-ce qu'on peut vérifier qu'on ne pouvait pas ? |
| **4. Quand s'abstenir** | dans quel cas le pattern coûte plus qu'il ne rapporte ? |

> La quatrième question est celle qu'on ne pose jamais. Elle est pourtant la
> plus utile : elle vous évitera d'appliquer six patterns à un module de
> 80 lignes.

---

<!-- _class: dense -->

# Adapter — traduire une interface externe

**Problème** : votre code métier parle le langage d'une bibliothèque tierce.
Le jour où elle change — ou qu'il faut la tester — tout le code est concerné.

<div class="cols">
<div>

**Avant**

```python
class Convertisseur:
    def convertir(self, montant, de, vers):
        r = requests.get(
            f"{URL}/v3/latest",
            params={"base": de, "apikey": CLE},
            timeout=30,
        )
        rates = r.json()["rates"]
        return round(montant * rates[vers], 2)
```

Le vocabulaire du fournisseur (`rates`,
`base`, `apikey`) a envahi le métier.

</div>
<div>

**Après**

```python
class SourceTaux(Protocol):
    def taux(self, base: str) -> dict[str, float]: ...


class AdaptateurApiTaux:
    """Traduit l'API du fournisseur en dict de taux."""

    def __init__(self, client): self._client = client

    def taux(self, base):
        brut = self._client.get("/v3/latest", base=base)
        return {d: float(v) for d, v in brut["rates"].items()}


class Convertisseur:
    def __init__(self, source: SourceTaux):
        self._source = source
```

</div>
</div>

---

# Adapter — ce que le test devient

<div class="cols">
<div>

**Le métier, sans réseau**

```python
class SourceFigee:
    def taux(self, base):
        return {"USD": 1.08, "GBP": 0.84}


def test_convertir():
    conv = Convertisseur(SourceFigee())
    assert conv.convertir(100, "EUR", "USD") == 108.0
```

Zéro mock, zéro patch, zéro réseau.

</div>
<div>

**L'adapter, isolément**

```python
def test_traduction_du_format_fournisseur():
    client = create_autospec(ClientHTTP)
    client.get.return_value = {
        "base": "EUR", "rates": {"USD": 1.08}
    }

    taux = AdaptateurApiTaux(client).taux("EUR")

    assert taux == {"USD": 1.08}
```

</div>
</div>

**Quand s'abstenir** : quand la bibliothèque tierce est déjà stable, simple, et
que son vocabulaire est le vôtre. Adapter `json.loads` n'a aucun intérêt.

> **🎯 Le signe qu'il faut un Adapter** : le nom d'un fournisseur ou d'un format
> apparaît dans votre code métier.

---

<!-- _class: dense -->

# Strategy — rendre un algorithme interchangeable

**Problème** : une cascade de `if` sur un mode de calcul. Chaque nouveau mode
rouvre la fonction et met en danger les cas déjà testés.

<div class="cols">
<div>

**Avant**

```python
def exporter(taches, format="texte"):
    if format == "texte":
        ...
    elif format == "csv":
        ...
    elif format == "markdown":
        ...
    else:
        raise ValueError(format)
```

Tester l'export Markdown exige de
passer par `exporter`, donc par la
cascade.

</div>
<div>

**Après — en Python, un dict de fonctions**

```python
def en_texte(taches: list[Tache]) -> str: ...
def en_csv(taches: list[Tache]) -> str: ...
def en_markdown(taches: list[Tache]) -> str: ...

FORMATS = {
    "texte": en_texte,
    "csv": en_csv,
    "markdown": en_markdown,
}

def exporter(taches, format="texte"):
    try:
        return FORMATS[format](taches)
    except KeyError:
        raise FormatInconnu(format) from None
```

</div>
</div>

---

# Strategy — ce que le test devient

```python
@pytest.mark.parametrize("nom", FORMATS)           # ← couvre les futurs ajouts
def test_tout_format_contient_les_titres(nom):
    assert "Déployer" in exporter([Tache("Déployer")], nom)


def test_markdown_directement():
    """Chaque stratégie se teste seule, sans passer par le dispatch."""
    assert en_markdown([]).startswith("| Titre |")


def test_strategie_maison():
    """Le code appelant peut injecter sa propre stratégie."""
    assert exporter_avec([Tache("A")], lambda t: str(len(t))) == "1"
```

**Quand s'abstenir** : deux branches stables qui ne bougeront pas. Un `if`
lisible vaut mieux qu'un registre.

> **Passez aux classes** quand la stratégie a besoin d'un **état** (des
> paramètres de configuration) ou de **plusieurs méthodes**. Sinon, une fonction
> suffit — et se teste plus facilement.

---

<!-- _class: dense -->

# Factory — centraliser la décision de création

**Problème** : le code qui décide *quel* objet construire est dupliqué à six
endroits. Ajouter un type oblige à retrouver les six.

<div class="cols">
<div>

**Avant, dans six modules**

```python
if cfg["type"] == "csv":
    source = SourceCSV(cfg["chemin"])
elif cfg["type"] == "api":
    source = SourceAPI(cfg["url"], cfg["cle"])
elif cfg["type"] == "sql":
    source = SourceSQL(connect(cfg["dsn"]))
```

</div>
<div>

**Après, à un seul endroit**

```python
CONSTRUCTEURS = {
    "csv": lambda c: SourceCSV(Path(c["chemin"])),
    "api": lambda c: SourceAPI(c["url"], c["cle"]),
    "sql": lambda c: SourceSQL(connect(c["dsn"])),
}

def creer_source(cfg: dict) -> SourceTaches:
    """Construit la source décrite par la configuration."""
    try:
        return CONSTRUCTEURS[cfg["type"]](cfg)
    except KeyError as e:
        raise TypeDeSourceInconnu(cfg.get("type")) from e
```

</div>
</div>

Le test devient possible **parce que la décision est isolée** : on vérifie le
choix sans construire de vraie connexion.

```python
def test_choix_du_type():
    assert isinstance(creer_source({"type": "csv", "chemin": "x"}), SourceCSV)
```

**Quand s'abstenir** : un seul type, ou une construction d'une ligne.
`Factory` pour fabriquer une `dataclass` est du bruit.

---

<!-- _class: dense -->

# Repository — cacher l'origine des données

**Problème** : le SQL est éparpillé dans le métier. Impossible de tester une
règle de gestion sans base.

<div class="cols">
<div>

**Avant**

```python
class Rapport:
    def surcharges(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT assignee, COUNT(*) FROM taches "
            "WHERE terminee = 0 GROUP BY assignee "
            "HAVING COUNT(*) > ?", (SEUIL,))
        return [r[0] for r in cur.fetchall()]
```

La règle métier (« plus de tâches
que le seuil ») est **dans le SQL**.

</div>
<div>

**Après**

```python
class DepotTaches(Protocol):
    def toutes(self) -> list[Tache]: ...


class Rapport:
    def __init__(self, depot: DepotTaches):
        self._depot = depot

    def surcharges(self, seuil=SEUIL):
        restantes = [t for t in self._depot.toutes() if not t.terminee]
        charges = Counter(t.assignee for t in restantes)
        return sorted(p for p, n in charges.items() if n > seuil)
```

</div>
</div>

La règle est remontée dans du Python testable. Le dépôt ne fait plus que
**fournir des données**.

---

# Repository — ce que le test devient

<div class="cols">
<div>

**Le fake, écrit une fois**

```python
class DepotEnMemoire:
    def __init__(self, taches=()):
        self._taches = list(taches)

    def toutes(self):
        return list(self._taches)
```

Dix lignes, réutilisables dans tous
les tests du projet.

</div>
<div>

**Le métier, sans base**

```python
def test_seuil_strict():
    """Exactement au seuil, on n'est pas surchargé."""
    depot = DepotEnMemoire(
        [Tache(f"A{i}", assignee="ada") for i in range(SEUIL)]
        + [Tache(f"Z{i}", assignee="zoe") for i in range(SEUIL + 1)]
    )

    assert Rapport(depot).surcharges() == ["zoe"]
```

</div>
</div>

Ce test de borne était **impossible** avec la version SQL sans peupler une base.

**Quand s'abstenir** : un script qui fait deux requêtes. Le Repository se
justifie quand plusieurs règles métier consomment les mêmes données.

---

<!-- _class: dense -->

# Facade — une porte d'entrée simple

**Problème** : pour accomplir une tâche courante, l'appelant doit connaître cinq
classes et leur ordre d'assemblage.

<div class="cols">
<div>

**Avant, chez chaque consommateur**

```python
cfg = charger_config(chemin)
depot = creer_source(cfg["source"])
regles = Rapport(depot, cfg["seuils"])
rendu = FORMATS[cfg["format"]]
notif = creer_notificateur(cfg["notif"])
resultats = regles.hebdomadaire(jour)
notif.envoyer(rendu(resultats))
```

Sept lignes recopiées dans quatre projets.
Une évolution interne les casse tous.

</div>
<div>

**Après**

```python
class Rapports:
    """Point d'entrée unique de la librairie."""

    def __init__(self, cfg: Configuration):
        self._regles = Rapport(creer_source(cfg.source), cfg.seuils)
        self._rendu = FORMATS[cfg.format]
        self._notif = creer_notificateur(cfg.notif)

    def hebdomadaire(self, jour: date) -> None:
        resultats = self._regles.hebdomadaire(jour)
        self._notif.envoyer(self._rendu(resultats))
```

</div>
</div>

**Attention** : une facade **ne rend rien testable par elle-même**. Elle protège
vos consommateurs de vos réorganisations internes. Elle se teste avec un ou deux
tests de bout en bout, pas plus — les détails sont testés en dessous.

---

# Dependency Injection — les trois formes

C'est moins un pattern qu'une discipline : **ne construisez pas ce que vous
pouvez recevoir**.

| Forme | Code | Quand |
|---|---|---|
| **Par constructeur** | `def __init__(self, depot: DepotTaches)` | dépendance utilisée par plusieurs méthodes |
| **Par paramètre** | `def calculer(valeurs, horloge=datetime.now)` | dépendance ponctuelle, avec un défaut sensé |
| **Par assemblage** | tout est construit dans `main()` / le point d'entrée | pour l'application complète |

```python
# Le point d'entrée est le SEUL endroit qui connaît les implémentations réelles
def main() -> None:
    depot = DepotSQLite(sqlite3.connect(DSN))
    notif = NotificateurSMTP(SMTP_HOST)
    Rappels(depot, notif).executer(date.today())
```

> En Python, **aucun conteneur d'injection n'est nécessaire**. Les frameworks de
> DI répondent à des contraintes de langages statiques que Python n'a pas.

---

<!-- _class: dense -->

# Template Method — figer un squelette

**Problème** : le même enchaînement d'étapes est recopié dans plusieurs
traitements, avec deux ou trois variantes.

<div class="cols">
<div>

**Le squelette**

```python
class Traitement(ABC):
    """Squelette commun : ne pas surcharger `executer`."""

    def executer(self, jour: date) -> Rapport:
        brut = self.charger(jour)
        valide = self.valider(brut)       # commun
        resultat = self.calculer(valide)  # varie
        return self.formater(resultat)    # varie

    def valider(self, brut):              # commun, surchargeable
        return [t for t in brut if t.titre.strip()]

    @abstractmethod
    def charger(self, jour): ...
    @abstractmethod
    def calculer(self, taches): ...
    @abstractmethod
    def formater(self, resultat): ...
```

</div>
<div>

**Le test du squelette, une fois**

```python
class TraitementFactice(Traitement):
    def charger(self, jour):
        return [Tache("Déployer"), Tache("   ")]
    def calculer(self, taches):
        return len(taches)
    def formater(self, r):
        return Rapport(r)


def test_la_validation_precede_le_calcul():
    """Les titres vides sont écartés avant `calculer`."""
    assert TraitementFactice().executer(JOUR).contenu == 1
```

</div>
</div>

**Quand s'abstenir** : deux implémentations seulement, ou des étapes qui varient
trop. L'héritage rend le flot difficile à suivre — préférez alors composer avec
des Strategy injectées.

---

# Template Method ou Strategy ?

Les deux rendent un comportement variable. La différence est structurelle :

| | Template Method | Strategy |
|---|---|---|
| Mécanisme | **héritage** | **composition** |
| Ce qui varie | des étapes dans un flot figé | un algorithme entier |
| Nombre de points de variation | plusieurs | un |
| Changeable à l'exécution | non | **oui** |
| Testabilité | il faut une sous-classe | on passe une fonction |

```python
# Souvent préférable en Python : le squelette devient une fonction
def executer(jour, charger, calculer, formater, valider=valider_par_defaut):
    return formater(calculer(valider(charger(jour))))
```

> **🎯 En pratique** : essayez d'abord la version « fonction avec des callables
> injectés ». Passez à la classe abstraite si l'état partagé entre étapes le
> justifie.

---

# Le pattern améliore-t-il vraiment le code ?

Trois questions, à poser **avant** d'introduire un pattern :

| Question | Si la réponse est non |
|---|---|
| Le problème s'est-il **déjà** produit ? | attendez qu'il se produise |
| Y a-t-il **au moins deux** cas réels ? | une seule implémentation ne justifie pas une abstraction |
| Le code devient-il plus **facile à tester** ? | c'est probablement du sur-design |

Signes de sur-design à repérer en relecture :

- une interface avec une seule implémentation, et aucun double de test ;
- une factory qui construit un seul type ;
- une hiérarchie de trois classes pour trente lignes de logique ;
- des noms qui parlent de la solution (`AbstractHandlerFactory`) plutôt que du
  domaine (`GrilleTarifaire`).

> **⚠️ Piège** : le sur-design se défend mal en relecture, parce qu'il a l'air
> compétent. Le critère objectif reste le même : **combien de tests étaient
> impossibles avant, et sont possibles maintenant ?**

---

# À retenir

> **1.** Les sept patterns font tous la même chose : ils **introduisent un point
> de substitution**. C'est ce point qui rend le test possible.

> **2.** En Python, la version « fonction, `dict` ou paramètre » suffit souvent.
> Passez aux classes quand il y a un **état** ou plusieurs méthodes.

> **3.** Le critère d'adoption n'est pas l'élégance : c'est le nombre de tests
> qui deviennent possibles. Si aucun ne le devient, n'introduisez pas le pattern.
