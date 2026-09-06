---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Rappels POO orientés testabilité"
---

<!-- _class: lead -->

# 3. Rappels POO Python orientés testabilité

*Seulement les notions qui changent quelque chose aux tests*

---

# Une classe = une responsabilité = un axe de changement

La question n'est pas « combien de méthodes ? » mais :

> **Pour quelles raisons différentes ce fichier devra-t-il être modifié ?**

<div class="cols">
<div>

**Trois raisons de changer**

```python
class TraitementMesures:
    def lire_csv(self, chemin): ...
    def valider(self, lignes): ...
    def calculer_indice(self, lignes): ...
    def ecrire_rapport(self, chemin): ...
    def envoyer_mail(self, dest): ...
```

Le format change → on touche la classe.
La formule change → on touche la classe.
Le serveur SMTP change → on touche la classe.

</div>
<div>

**Une raison chacun**

```python
class LecteurMesuresCSV: ...   # format
class ValidateurMesures: ...   # règles
class CalculIndice: ...        # formule
class RapportMarkdown: ...     # rendu
class Notificateur: ...        # envoi
```

`CalculIndice` se teste sans fichier,
sans réseau, en trois lignes.

</div>
</div>

---

# Agrégation ou composition : qui crée quoi ?

<div class="cols">
<div>

**Composition — l'objet crée sa dépendance**

```python
class Rapport:
    def __init__(self, chemin_db: str):
        self.db = Connexion(chemin_db)  # ← ici
```

Pour tester `Rapport`, il faut une base.
La dépendance est **soudée**.

</div>
<div>

**Agrégation — la dépendance est fournie**

```python
class Rapport:
    def __init__(self, source: SourceMesures):
        self.source = source            # ← reçue
```

Pour tester, on fournit un objet
en mémoire. La dépendance est
**remplaçable**.

</div>
</div>

C'est l'idée la plus rentable de la journée, et elle tient en une ligne :

> **Ne construisez pas ce que vous pouvez recevoir.**

Nous la reverrons sous son nom savant au chapitre 6 : *injection de dépendance*.

---

# Le couplage, mesuré concrètement

Le couplage entre A et B, c'est **le nombre de choses que A doit savoir sur B**
pour fonctionner.

| Niveau | A connaît de B… | Testabilité |
|---|---|---|
| Fort | son type concret, qu'il instancie lui-même | ✗ il faut un vrai B |
| Moyen | son type concret, mais B est fourni | ~ il faut un vrai B, mais on choisit lequel |
| Faible | **une seule méthode**, quel que soit le type | ✓ trois lignes suffisent |

```python
# Couplage minimal : Rapport n'exige qu'une chose de sa source
class SourceMesures(Protocol):
    def lire(self, jour: date) -> list[Mesure]: ...
```

Un test fournit alors n'importe quel objet ayant une méthode `lire`.

---

# Loi de Déméter : ne parlez qu'à vos voisins

<div class="cols">
<div>

**Chaîne de points = couplage caché**

```python
ville = commande.client.adresse.ville.nom
```

Cette ligne dépend de **quatre** classes.
Toute modification de l'une des quatre
casse l'appelant.

Un test doit construire quatre objets
imbriqués pour vérifier une ligne d'adresse.

</div>
<div>

**Demander, ne pas fouiller**

```python
ville = commande.ville_de_livraison()
```

Une seule dépendance : `Commande`.

Le test fournit un objet avec une
méthode, et c'est tout.

</div>
</div>

> **⚠️ Piège** : cette règle vise les **objets**, pas les structures de données.
> `config["db"]["host"]` ou `df.loc[…].mean()` ne posent pas de problème.

---

# Encapsulation pragmatique en Python

Python n'a pas de `private`. Il a une **convention**, et elle suffit.

<div class="cols">
<div>

**À ne pas faire — du Java en Python**

```python
class Mesure:
    def __init__(self, valeur):
        self.__valeur = valeur

    def get_valeur(self):
        return self.__valeur

    def set_valeur(self, v):
        self.__valeur = v
```

Trois fois plus de code, zéro garantie
supplémentaire.

</div>
<div>

**Ce qui se fait**

```python
class Mesure:
    def __init__(self, valeur: float):
        self.valeur = valeur      # public, assumé
        self._cache = None        # interne

    @property
    def valeur_fahrenheit(self) -> float:
        return self.valeur * 9 / 5 + 32
```

`_` = « ceci peut changer sans préavis ».
`@property` = quand un calcul apparaît
derrière un attribut public.

</div>
</div>

**Pour les tests** : ce qui est préfixé `_` ne se teste pas directement.
Si vous en éprouvez le besoin, c'est que ce code mérite sa propre classe publique.

---

# Duck typing : l'interface implicite

En Python, un objet est acceptable s'il a les bonnes méthodes. Point.

```python
def exporter(destination, lignes: list[str]) -> None:
    for ligne in lignes:
        destination.write(ligne + "\n")
```

`destination` peut être un fichier, un `io.StringIO`, un socket, un objet maison.
La fonction ne demande rien d'autre qu'un `.write()`.

<div class="cols">
<div>

**Le test devient trivial**

```python
def test_exporter_ajoute_les_sauts_de_ligne():
    tampon = io.StringIO()
    exporter(tampon, ["a", "b"])
    assert tampon.getvalue() == "a\nb\n"
```

</div>
<div>

Aucun fichier temporaire.
Aucun mock.
Aucune configuration.

C'est le duck typing qui rend cela
possible, gratuitement.

</div>
</div>

---

# `ABC` ou `Protocol` : lequel choisir ?

<div class="cols">
<div>

**`ABC` — héritage explicite**

```python
class SourceMesures(ABC):
    @abstractmethod
    def lire(self, jour: date) -> list[Mesure]: ...

class SourceCSV(SourceMesures):  # doit hériter
    def lire(self, jour): ...
```

- Impose l'héritage
- Erreur à l'instanciation si incomplet
- Permet du code partagé dans la base

</div>
<div>

**`Protocol` — conformité structurelle**

```python
class SourceMesures(Protocol):
    def lire(self, jour: date) -> list[Mesure]: ...

class SourceCSV:                 # n'hérite de rien
    def lire(self, jour): ...
```

- Aucun héritage nécessaire
- Vérifié par `mypy`, pas à l'exécution
- Fonctionne sur du code que vous ne
  possédez pas

</div>
</div>

> **🎯 En pratique** : `Protocol` par défaut dans une librairie — il documente
> le contrat sans imposer de contrainte à vos consommateurs. `ABC` quand vous
> avez réellement du comportement commun à partager (voir *Template Method*, Jour 3).

---

# Quand une abstraction n'apporte rien

Une interface avec **une seule implémentation** et **aucun besoin de test double**
est du code mort déguisé en architecture.

<div class="cols">
<div>

**Sur-design**

```python
class CalculateurInterface(ABC):
    @abstractmethod
    def calculer(self, x: float) -> float: ...

class CalculateurStandard(CalculateurInterface):
    def calculer(self, x): return x * 1.2
```

</div>
<div>

**Suffisant**

```python
def calculer(x: float) -> float:
    return x * 1.2
```

Testable, lisible, remplaçable
le jour où un second cas apparaîtra.

</div>
</div>

> **⚠️ Piège** : « on pourrait en avoir besoin plus tard » n'est pas une raison.
> La deuxième implémentation est le bon moment pour créer l'abstraction — pas la première.

---

# Objets de valeur : `dataclass(frozen=True)`

Beaucoup de bugs viennent de dictionnaires trimballés entre couches, dont on ne
sait plus quelles clés sont garanties.

<div class="cols">
<div>

**Avant**

```python
t = {"titre": "Déployer", "prio": 2}
# ailleurs, 400 lignes plus loin
t["priorite"]      # KeyError
t["prio"] = 7      # personne ne vérifie
```

</div>
<div>

**Après**

```python
@dataclass(frozen=True)
class Tache:
    titre: str
    priorite: int = 2

    def __post_init__(self):
        if not 1 <= self.priorite <= 3:
            raise PrioriteInvalide(self.priorite)
```

</div>
</div>

Bénéfices immédiats : `mypy` détecte les fautes de frappe, l'objet est
immuable (donc sans effet de bord), la validation est faite **une seule fois**,
et `==` fonctionne — ce qui rend les assertions de test lisibles.

---

# Exceptions métier : dire ce qui s'est passé

<div class="cols">
<div>

**Avant**

```python
if seuil is None:
    return None
if not chemin.exists():
    return None
if not lignes:
    return None
```

L'appelant reçoit `None` et ne sait pas
laquelle des trois situations s'est produite.

</div>
<div>

**Après — une hiérarchie**

```python
class ErreurMesures(Exception):
    """Racine des erreurs de la librairie."""

class FichierMesuresIntrouvable(ErreurMesures): ...
class SérieVide(ErreurMesures): ...
class SeuilNonConfiguré(ErreurMesures): ...
```

</div>
</div>

Une **racine unique par librairie** permet à vos consommateurs d'écrire
`except ErreurMesures:` pour tout attraper, ou de cibler un cas précis —
sans jamais avoir à faire `except Exception`.

---

# Ne perdez jamais la cause : `raise … from`

<div class="cols">
<div>

**Sans `from` — la trace originale disparaît**

```python
try:
    données = json.loads(texte)
except ValueError:
    raise ConfigurationInvalide(chemin)
```

</div>
<div>

**Avec `from` — la cause est conservée**

```python
try:
    données = json.loads(texte)
except ValueError as e:
    raise ConfigurationInvalide(chemin) from e
```

La trace affiche alors :
`… ValueError: Expecting ',' delimiter: line 4`
`The above exception was the direct cause of…`

</div>
</div>

Et côté test, l'exception métier se vérifie précisément :

```python
def test_configuration_illisible():
    with pytest.raises(ConfigurationInvalide, match="seuil"):
        charger_seuil(chemin_sans_seuil)
```

---

# À retenir

> **1.** Ne construisez pas ce que vous pouvez recevoir. Une dépendance
> instanciée dans un `__init__` est une dépendance non testable.

> **2.** `Protocol` par défaut, `ABC` seulement quand il y a du comportement
> commun à partager. Une interface à une seule implémentation ne sert à rien.

> **3.** Une exception métier explicite, dérivée d'une racine propre à la
> librairie, remplace avantageusement tout `return None`.
