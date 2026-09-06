---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Design patterns, SOLID et mocking"
---

<!-- _class: lead -->

# 6. Design patterns, SOLID et mocking

*Trois sujets, une seule idée*

---

# Le fil qui relie les trois

| | Ce que ça dit | Effet sur les tests |
|---|---|---|
| **SOLID** | dépendez d'abstractions, gardez les interfaces étroites | il devient **possible** de substituer |
| **Patterns** | voici les formes concrètes que prend cette substitution | il devient **simple** de substituer |
| **Doubles** | voici quoi mettre à la place | on **exerce** la substitution |

Autrement dit :

> Le mocking n'est pas une compétence de test. C'est la **conséquence** d'une
> décision de conception prise bien avant, quand quelqu'un a choisi de recevoir
> une dépendance plutôt que de la construire.

---

# Une meilleure conception réduit le besoin de mocks

Le même besoin — tester une règle métier qui dépend d'une base — selon la
qualité de la conception :

| Conception | Test |
|---|---|
| La classe ouvre sa connexion | `patch("module.sqlite3.connect")` + un `Mock` de curseur + des `fetchall` figés |
| La connexion est injectée | un `sqlite3.connect(":memory:")` réel |
| Un Repository est injecté | un fake en mémoire de dix lignes |
| La règle est une fonction pure | une liste et un `assert` |

Le volume de code de test décroît à chaque ligne. Et surtout : **la dernière
version teste la règle métier, les précédentes testent le plomberie**.

> **🎯 En pratique** : quand un test devient pénible à écrire, remontez d'une
> ligne dans ce tableau plutôt que de sortir un outil plus puissant.

---

# Comment un pattern peut compliquer inutilement

Le pattern mal choisi produit exactement l'effet inverse.

<div class="cols">
<div>

**Sur-design**

```python
class ValidateurFactory:
    def creer(self, type_): ...

class AbstractValidateur(ABC):
    @abstractmethod
    def valider(self, v): ...

class ValidateurPositif(AbstractValidateur):
    def valider(self, v): return v > 0
```

Trois classes, un fichier, une usine —
pour tester `v > 0`.

</div>
<div>

**Suffisant**

```python
def est_positif(valeur: float) -> bool:
    return valeur > 0
```

Testable en une ligne, lisible sans
contexte, remplaçable le jour où un
deuxième cas apparaîtra.

</div>
</div>

> **⚠️ Piège** : un pattern ajouté « au cas où » crée des points de substitution
> que personne n'exerce. Ce sont des interfaces mortes — du coût de maintenance
> sans contrepartie.

---

# Le test comme révélateur de conception

Ce que la difficulté d'écriture d'un test vous dit du code :

| Symptôme dans le test | Ce que ça révèle | Correctif |
|---|---|---|
| Trois `patch` pour un test | trop de dépendances | découper la fonction |
| Un `Mock` dont on configure 5 attributs | interface trop grosse | **ISP** : interfaces étroites |
| Un `patch` sur un chemin de module | dépendance non injectée | **DIP** : injecter |
| Le test connaît des attributs privés | on teste l'implémentation | tester le comportement |
| 40 lignes de préparation | l'objet construit ses dépendances | injection + fixtures |
| Le test casse à chaque refactoring | test d'interaction là où un test d'état suffirait | assertion sur le résultat |

> Aucune ligne de ce tableau ne se corrige dans le test. **Toutes** se corrigent
> dans le code de production.

---

# À retenir

> **1.** SOLID rend la substitution possible, les patterns la rendent simple,
> les doubles l'exercent. C'est une seule chaîne, pas trois sujets.

> **2.** Quand un test devient pénible, améliorez la **conception** plutôt que
> l'outillage de test. Le tableau des symptômes vous dit quoi changer.

> **3.** Un pattern qui ne rend aucun test possible ne rend service à personne.
