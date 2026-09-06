---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Principes SOLID utiles en Python"
---

<!-- _class: lead -->

# 6. Principes SOLID utiles en Python

*Cinq principes, une seule intention*

---

# Cinq principes, un objectif commun

| | Principe | Ce qu'il demande |
|---|---|---|
| **S** | Single Responsibility | Une seule raison de changer par module |
| **O** | Open/Closed | Étendre sans modifier l'existant |
| **L** | Liskov Substitution | Un sous-type doit pouvoir remplacer son type |
| **I** | Interface Segregation | Ne pas imposer ce dont on n'a pas besoin |
| **D** | Dependency Inversion | Dépendre d'abstractions, pas de détails |

L'intention unique derrière les cinq :

> **Faire en sorte qu'un changement reste local.**

Les tests sont le meilleur détecteur de violation : quand un changement casse
des tests éloignés du code modifié, un de ces principes a été enfreint.

---

# S — Une seule raison de changer

Le principe le plus mal cité. Il ne dit pas « une classe ne fait qu'une chose »,
il dit :

> Un module doit avoir **une seule source de demandes de modification**.

```python
class RapportMensuel:
    def calculer_totaux(self): ...   # ← demandé par le métier
    def formater_html(self): ...     # ← demandé par la communication
    def envoyer(self): ...           # ← demandé par l'exploitation
```

Trois interlocuteurs différents modifient le même fichier. Chacun risque de
casser le travail des deux autres — et les tests de tout le monde.

Le découpage suit les **interlocuteurs**, pas les verbes.

---

# S — Jusqu'où découper ?

<div class="cols">
<div>

**Découpage utile**

```python
class CalculTotaux: ...
class RenduHTML: ...
class Expéditeur: ...
```

Trois fichiers, trois responsables,
trois suites de tests indépendantes.

</div>
<div>

**Découpage nuisible**

```python
class AdditionneurDeLignes: ...
class ArrondisseurDeTotaux: ...
class FormateurDeNombre: ...
class ValidateurDeFormat: ...
```

Douze fichiers pour cinquante lignes.
Comprendre le calcul exige d'ouvrir
quatre fichiers.

</div>
</div>

> **🎯 En pratique** : découpez quand vous avez **une raison observée** —
> deux interlocuteurs, deux rythmes de changement, ou un besoin de test isolé.
> Pas quand une méthode « fait deux choses » sur le papier.

---

# O — Ouvert à l'extension, fermé à la modification

Le symptôme d'une violation est facile à repérer : **ajouter un cas oblige à
rouvrir une fonction existante**, et donc à risquer de casser les cas déjà testés.

```python
def exporter(données, format):
    if format == "csv":
        ...
    elif format == "json":
        ...
    elif format == "xml":      # ← ajouté le mois dernier
        ...
    elif format == "parquet":  # ← à ajouter cette semaine
        ...
```

À chaque ajout : la fonction grossit, tous ses tests sont rejoués, et un `elif`
mal placé peut casser l'export CSV utilisé par quatre projets.

---

# O — En Python, un `dict` suffit souvent

<div class="cols">
<div>

**Registre explicite**

```python
EXPORTEURS = {
    "csv": exporter_csv,
    "json": exporter_json,
    "xml": exporter_xml,
}

def exporter(données, format: str) -> str:
    try:
        return EXPORTEURS[format](données)
    except KeyError:
        raise FormatInconnu(format) from None
```

Ajouter Parquet = écrire une fonction
+ une ligne dans le dictionnaire.
`exporter` n'est jamais rouverte.

</div>
<div>

**Ce que ça change pour les tests**

```python
@pytest.mark.parametrize("format", EXPORTEURS)
def test_tous_les_formats(format, données):
    assert exporter(données, format)
```

Le test couvre automatiquement
les formats futurs.

Chaque exporteur se teste seul,
sans passer par `exporter`.

</div>
</div>

---

# L — Un sous-type ne doit pas piéger l'appelant

Liskov, en pratique : **une sous-classe ne doit pas être plus exigeante ni moins
généreuse que sa classe de base**.

```python
class SourceMesures:
    def lire(self, jour: date) -> list[Mesure]:
        """Retourne les mesures du jour, éventuellement vide."""

class SourceAPI(SourceMesures):
    def lire(self, jour: date) -> list[Mesure]:
        if jour > date.today():
            raise ValueError("date future")     # ← nouvelle exigence
        ...
```

Tout code écrit contre `SourceMesures` fonctionne — jusqu'au jour où on lui
passe une `SourceAPI`.

> **🎯 En pratique** : le test qui protège de cela est un **test de contrat**,
> rejoué sur chaque implémentation. Nous en écrirons un au Jour 3.

---

# I — Ne pas imposer ce dont on n'a pas besoin

<div class="cols">
<div>

**Interface trop grosse**

```python
class SourceDonnées(Protocol):
    def lire(self, jour): ...
    def écrire(self, mesures): ...
    def supprimer(self, id): ...
    def statistiques(self): ...
```

Un calcul en lecture seule doit fournir
**quatre** méthodes dans son fake, dont
trois qu'il n'appellera jamais.

</div>
<div>

**Interfaces étroites**

```python
class Lecteur(Protocol):
    def lire(self, jour: date) -> list[Mesure]: ...

class Écrivain(Protocol):
    def écrire(self, mesures: list[Mesure]) -> None: ...
```

Le fake du test fait deux lignes.

Et la signature de la fonction
**documente** qu'elle ne modifie rien.

</div>
</div>

C'est le principe SOLID le plus directement rentable pour les tests : il divise
la taille des doubles de test par le nombre de méthodes inutiles.

---

# D — L'abstraction, c'est souvent juste un paramètre

<div class="cols">
<div>

**Dépendance vers un détail**

```python
class Analyse:
    def __init__(self):
        self.source = ClientAPIProd()   # détail
```

`Analyse` (haut niveau, métier) dépend
d'un client HTTP (bas niveau, technique).

</div>
<div>

**Dépendance inversée**

```python
class Analyse:
    def __init__(self, source: Lecteur):
        self.source = source            # abstraction
```

`Analyse` ne dépend plus que d'un
contrat. C'est l'appelant qui choisit
l'implémentation.

</div>
</div>

En Python, l'inversion de dépendance ne demande **ni conteneur, ni framework,
ni fichier XML**. Elle demande de déplacer une instanciation du constructeur
vers l'appelant.

```python
analyse = Analyse(source=ClientAPIProd())     # production
analyse = Analyse(source=SourceEnMémoire(mesures_de_test))  # test
```

---

# Les limites de SOLID en Python

SOLID a été formulé pour des langages à typage statique et héritage obligatoire.
Python en absorbe une partie gratuitement :

| Principe | Ce que Python offre déjà |
|---|---|
| **O** | Fonctions de première classe, `dict` de dispatch |
| **L** | Duck typing : pas de hiérarchie imposée |
| **I** | `Protocol` structurel, sans héritage |
| **D** | Un paramètre suffit, pas de conteneur d'injection |

Les dérives à éviter :

- une interface par classe, systématiquement ;
- des classes d'une seule méthode partout ;
- une usine à fabriquer les usines ;
- l'application de SOLID à un script de 40 lignes.

> **⚠️ Piège** : le sur-design est aussi coûteux que le sous-design, et bien
> plus difficile à défaire — parce qu'il a l'air sérieux.

---

# À retenir

> **1.** Les cinq principes servent un seul objectif : **qu'un changement reste
> local**. Vos tests vous diront quand il ne l'est pas.

> **2.** Les deux qui rapportent le plus, tout de suite : **DIP** (recevoir ses
> dépendances) et **ISP** (interfaces étroites). Les deux réduisent
> immédiatement l'effort de test.

> **3.** Appliquez un principe quand vous avez **observé** le problème qu'il
> résout — jamais par anticipation.
