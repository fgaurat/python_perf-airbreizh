---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Identifier le code difficile à tester"
---

<!-- _class: lead -->

# 5. Identifier le code difficile à tester

*Six symptômes, et ce qu'ils révèlent*

---

# L'heuristique de base

Avant de lire du code, posez-vous une seule question :

> **De quoi ai-je besoin pour vérifier que cette fonction est juste ?**

| Réponse | Diagnostic |
|---|---|
| « Trois valeurs et un `assert` » | Le code est bien découpé |
| « Un fichier temporaire » | Acceptable, mais l'I/O n'est pas isolée |
| « Une base de données » | Le métier est mélangé à la persistance |
| « Le réseau et un jeton d'API » | La frontière du système n'est pas matérialisée |
| « Tout l'environnement de production » | Il n'y a pas de composant, juste un programme |

Aucune de ces réponses ne parle de tests. Elles parlent toutes de **conception**.

---

# Symptôme 1 — La méthode longue

Une méthode de 300 lignes contient typiquement 12 décisions imbriquées, donc
plusieurs milliers de chemins d'exécution possibles.

Conséquences mesurables :

- On ne peut pas la tester : on ne peut atteindre qu'une poignée de chemins.
- On ne peut pas la lire : elle ne tient pas dans un écran ni dans une tête.
- On ne peut pas la modifier : personne ne sait ce que touche un changement.
- Elle est **toujours** en train de faire plusieurs choses — sinon elle serait courte.

> **🎯 En pratique** : le seuil d'alerte utile n'est pas un nombre de lignes,
> c'est le moment où vous devez **faire défiler** pour comprendre le début.

Nous la démonterons méthodiquement au Jour 4.

---

# Symptôme 2 — Calcul et I/O mélangés

<div class="cols">
<div>

**Avant — intestable sans fichiers**

```python
def traiter(chemin_in, chemin_out):
    with open(chemin_in) as f:
        lignes = list(csv.DictReader(f))
    total = 0.0
    for l in lignes:
        v = float(l["valeur"])
        if v > 0:
            total += v * 1.15
    with open(chemin_out, "w") as f:
        f.write(f"{total:.2f}\n")
```

Tester la formule `* 1.15` exige
d'écrire un CSV et de relire un fichier.

</div>
<div>

**Après — le cœur est une fonction pure**

```python
def corriger(valeurs: list[float]) -> float:
    return sum(v * 1.15 for v in valeurs if v > 0)


def lire(chemin: Path) -> list[float]:
    with chemin.open() as f:
        return [float(l["valeur"])
                for l in csv.DictReader(f)]


def traiter(chemin_in: Path, chemin_out: Path) -> None:
    total = corriger(lire(chemin_in))
    chemin_out.write_text(f"{total:.2f}\n")
```

</div>
</div>

`corriger` se teste en une ligne. Et c'est elle qui porte le risque métier.

---

# Symptôme 3 — Accès direct à une ressource externe

```python
class Avancement:
    def calculer(self, projet: str) -> float:
        r = requests.get(f"https://api.example.org/projets/{projet}")
        taches = r.json()["taches"]
        return sum(t["terminee"] for t in taches) / len(taches)
```

Trois problèmes en quatre lignes :

| Problème | Conséquence sur le test |
|---|---|
| L'URL est en dur | Impossible de pointer ailleurs |
| `requests` est appelé directement | Il faut mocker au niveau du module |
| Le parsing et le calcul sont mélangés | On ne peut pas tester la moyenne seule |

Ce code **peut** se tester avec des mocks. Il sera plus simple de le tester
après l'avoir découpé (Jour 3, *Adapter*).

---

# Symptôme 4 — L'objet qui construit ses dépendances

<div class="cols">
<div>

**Avant**

```python
class GénérateurRapport:
    def __init__(self):
        self.db = psycopg2.connect(DSN)
        self.cache = Redis(host="prod-01")
        self.mailer = SMTP("smtp.interne")
```

Instancier cet objet dans un test ouvre
trois connexions réseau.

Il n'existe **aucun moyen** de le tester
sans infrastructure : le constructeur ne
laisse aucune prise.

</div>
<div>

**Après**

```python
class GénérateurRapport:
    def __init__(self, source: SourceMesures,
                 notif: Notificateur):
        self.source = source
        self.notif = notif
```

Le test fournit deux objets de dix lignes.

Bonus : le constructeur **documente**
les dépendances réelles de la classe,
qui étaient jusque-là invisibles.

</div>
</div>

> **⚠️ Piège** : ce symptôme est le plus fréquent et le plus coûteux, parce
> qu'il est contagieux — un objet non injectable rend non testable tout ce qui l'utilise.

---

# Symptôme 5 — Variables globales et état partagé

```python
_CONFIG = {}          # rempli au premier appel, quelque part

def calculer(x):
    if not _CONFIG:
        _CONFIG.update(json.loads(Path("config.json").read_text()))
    return x * _CONFIG["facteur"]
```

Les tests deviennent **dépendants de leur ordre d'exécution** :

- le premier test remplit `_CONFIG` ;
- le deuxième hérite de la valeur du premier ;
- lancé seul, le deuxième échoue ; lancé après le premier, il passe.

C'est le symptôme le plus démoralisant, parce qu'il produit des tests
« qui échouent une fois sur trois » et qu'on finit par ignorer.

**Correctif** : passer la configuration en paramètre, ou la charger une fois au
point d'entrée et la transmettre explicitement.

---

# Symptôme 6 — Dépendances circulaires

```python
# mesures.py
from rapports import formater      # ← rapports importe mesures

# rapports.py
from mesures import Mesure         # ← mesures importe rapports
```

Symptômes typiques : `ImportError: cannot import name …`, imports placés au
milieu d'une fonction « pour que ça marche », ordre d'import qui compte.

Ce que cela signifie en réalité :

> Deux modules qui s'importent mutuellement **sont un seul module** qui n'a pas
> été découpé au bon endroit.

Impossible de tester l'un sans charger l'autre — donc impossible de tester une
partie du système isolément. Traité en détail au Jour 4.

---

# Grille de diagnostic

À utiliser sur votre propre code, cette semaine :

| Question | Si oui → |
|---|---|
| Dois-je faire défiler pour lire la fonction ? | Découper (J4) |
| La fonction ouvre-t-elle un fichier **et** calcule-t-elle ? | Extraire une fonction pure |
| Le constructeur ouvre-t-il une connexion ? | Injecter la dépendance |
| Y a-t-il un état modifiable au niveau du module ? | Passer en paramètre |
| Deux modules s'importent-ils mutuellement ? | Extraire un troisième module |
| Le nom contient-il « et », « manager », « utils », « process » ? | Chercher les responsabilités cachées |

> **🎯 En pratique** : trois « oui » sur la même fonction suffisent à en faire
> une bonne candidate pour le premier refactoring de votre équipe.

---

# À retenir

> **1.** « De quoi ai-je besoin pour tester ceci ? » est un diagnostic de
> conception déguisé en question de test.

> **2.** Le symptôme le plus rentable à corriger est l'objet qui construit ses
> propres dépendances : il contamine tout ce qui l'utilise.

> **3.** Ces symptômes ne sont pas des fautes de goût. Chacun a un coût
> mesurable en temps de correction et en bugs silencieux.
