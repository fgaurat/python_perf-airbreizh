# TP j4-03 — Faire émerger un pattern par petites transformations

**Durée : 60 min**

## Contexte

`depart/rappels/envoi.py` repère les tâches dues ou en retard de la todo-list
et envoie un rappel par tâche sur trois canaux : courriel, SMS, messagerie
d'équipe.

Deux problèmes, visibles dès le constructeur :

```python
def __init__(self):
    self.smtp = smtplib.SMTP(os.environ.get("SMTP_HOST", "localhost"))
    self.jeton_sms = os.environ["SMS_TOKEN"]
    self.webhook = os.environ["WEBHOOK_URL"]
```

**Instancier `Rappeleur` dans un test ouvre une connexion SMTP** et exige deux
variables d'environnement. Aucun test n'est possible — pas même sur la règle
qui décide du niveau d'un rappel, qui est pourtant du calcul pur.

Et `rappeler` mêle cette règle à une cascade de `if canal == …` de trente lignes.

## Objectif

Rendre le module testable par **quatre transformations successives**, chacune
validée par les tests. Le nom du pattern n'apparaîtra qu'à la fin.

## La règle du TP

> Après **chaque** transformation : tests verts, puis commit.

Si vous êtes rouge plus de dix minutes, revenez au dernier commit et
recommencez avec un pas plus petit.

## Étapes

### Transformation 1 — Extraire la règle pure (15 min)

Le bloc qui décide du niveau d'un rappel ne fait aucune I/O. Sortez-le :

```python
def detecter(taches: Iterable[Mapping], jour: date) -> list[Rappel]: ...
```

Créez `rappels/modele.py` pour `Rappel`, `Niveau` et le seuil.

> Vous venez de rendre testable la partie qui porte le risque métier — **avant**
> d'avoir touché à la moindre connexion. Écrivez tout de suite ses tests, y
> compris les bornes : exactement 0 jour, exactement 7 jours, et la veille.

Tests verts → commit.

### Transformation 2 — Une classe par canal (15 min)

Chaque branche du `if canal == …` devient une classe avec une méthode
`envoyer(rappel)`. Le corps de la branche est déplacé tel quel — **ne le
réécrivez pas**.

```python
class CanalSMS:
    def __init__(self, jeton: str, transport=poster_json): ...
    def envoyer(self, rappel: Rappel) -> None: ...
```

Rendez le transport HTTP injectable au passage : c'est une couture, elle ne
change rien en production.

Tests verts → commit.

### Transformation 3 — Injecter le canal (10 min)

`Rappeleur.__init__` ne construit plus rien. Il **reçoit** un canal :

```python
class Rappeleur:
    def __init__(self, canal: Canal):
        self._canal = canal
```

La cascade de `if` disparaît de `rappeler`, qui se réduit à une boucle.

Déclarez le contrat que doivent remplir les canaux :

```python
class Canal(Protocol):
    def envoyer(self, rappel: Rappel) -> None: ...
```

Tests verts → commit.

### Transformation 4 — Une fabrique pour la configuration (10 min)

Le code qui lit l'environnement et ouvre les connexions doit bien vivre quelque
part. Rassemblez-le dans `rappels/fabrique.py` :

```python
CANAUX = {"email": creer_email, "sms": creer_sms, "chat": creer_chat}


def creer_canal(nom: str, env=os.environ) -> Canal: ...
```

C'est désormais le **seul** fichier du projet qui lit `os.environ` — et comme
`env` est un paramètre, la fabrique elle-même se teste avec un dictionnaire.

Tests verts → commit.

### Les tests devenus possibles (10 min)

Écrivez maintenant ce que vous ne pouviez pas écrire il y a une heure :

- les bornes de la règle (0 jour, 6 jours, 7 jours) et l'ordre de tri ;
- ce qui est réellement posté par le canal SMS (URL, jeton, texte) ;
- la traduction d'un timeout réseau en `EnvoiImpossible`, cause conservée ;
- un canal maison fourni par un consommateur, sans modifier le module ;
- que `os.environ` n'apparaît que dans `fabrique.py`.

Utilisez un **espion** (`CanalEspion`) plutôt qu'un `Mock` : le message d'échec
sera plus lisible.

## Comment s'appellent les patterns que vous venez d'écrire ?

Ne répondez qu'à la fin. Relisez votre code, puis nommez-les :

| Ce que vous avez fait | Le nom |
|---|---|
| Une classe par canal, interchangeables derrière un contrat | ? |
| Le `Protocol Canal` | ? |
| `Rappeleur` reçoit son canal au lieu de le construire | ? |
| `creer_canal(nom)` centralise la construction | ? |

> **🎯 Le point du TP** : vous n'avez appliqué aucun pattern. Vous avez résolu
> quatre problèmes concrets, et les patterns sont apparus. C'est le seul ordre
> qui fonctionne — et c'est celui que vous pourrez reproduire sur votre code.

## Critères de réussite

- Aucun test n'ouvre de connexion ni ne lit `os.environ`.
- `Rappeleur.__init__` ne construit aucune dépendance.
- `rappeler` ne contient plus aucun `if` sur le canal.
- `os.environ` n'apparaît que dans `fabrique.py` — un test le prouve.
- Un test prouve qu'un consommateur peut ajouter son propre canal.

## Corrigé

`corrige/` — 6 modules, 27 tests.

```bash
uv run pytest j4-03-introduire-un-pattern-en-refactoring/corrige -v
```
