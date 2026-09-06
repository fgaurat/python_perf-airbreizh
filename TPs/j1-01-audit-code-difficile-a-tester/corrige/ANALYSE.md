# Corrigé — Analyse de `todo.py`

Ce n'est pas *la* bonne réponse, mais une analyse complète à comparer à la vôtre.

## 1. La question du test

| Règle métier à vérifier | Ce qu'il faudrait aujourd'hui |
|---|---|
| Une tâche est en retard si échéance < jour et non terminée | Une base SQLite peuplée, un serveur SMTP qui répond (sinon `__init__` échoue avant tout calcul), un répertoire accessible en écriture, puis **lire le fichier `rapport_….txt` produit** pour compter les lignes en retard. |
| `score = poids × (1 + jours de retard)` | Idem — la formule est ligne 115, au milieu d'une méthode de 66 lignes. Et le score n'apparaît que sous forme de **total** dans le fichier : impossible de vérifier le score d'une tâche seule. |
| Alerte à partir de 3 tâches en retard | Idem, **plus** intercepter ce que reçoit le serveur SMTP. |

Trois règles métier de une à deux lignes chacune. Aucune n'est atteignable sans
reconstituer un environnement complet. **C'est le diagnostic**, tout le reste
en découle.

## 2. Les sept symptômes

| Symptôme | Lignes | Détail |
|---|---|---|
| **Méthode trop longue** | 94-159 | `rapport` fait 66 lignes et enchaîne 4 responsabilités, matérialisées par les commentaires en bannière — des marqueurs de découpage que quelqu'un a vus sans les faire. |
| **Calcul et I/O mélangés** | 94-159 | Lecture SQL (via `charger`, 98), calcul (100-125), écriture fichier (127-143), envoi de mail (145-155), affichage (157-158) dans une seule méthode. |
| **Accès direct à une ressource externe** | 38, 43, 130 | `sqlite3.connect`, `smtplib.SMTP` et `open` sont appelés en dur, sans indirection. |
| **Objet qui construit ses dépendances** | 36-45 | `__init__` ouvre une base **et** une connexion SMTP. Instancier la classe dans un test ouvre deux connexions. |
| **État global mutable** | 21-23, 48, 53, 66-68, 76 | `CONFIG`, `TACHES`, `DERNIER_ID` sont modifiés par les méthodes : deux tests qui instancient `GestionnaireTaches` partagent la même liste. Ils deviennent dépendants de leur ordre d'exécution. |
| **Dépendance implicite** | 29, 43-44, 97, 128 | `config.json` lu dans le répertoire courant, `SMTP_HOST` et `DESTINATAIRES` lus dans l'environnement, `datetime.now()` pris en douce, rapport écrit dans le répertoire courant : rien dans les signatures ne les annonce. Le script se comporte différemment selon d'où, et quand, on le lance. |
| **Erreur silencieuse** | 31-32, 110-112, 142-143, 154-155 | Quatre occurrences — détaillées ci-dessous. |

Symptômes bonus, non demandés :

- **Paramètres drapeaux** (94) : `envoyer=True`, `verbose=False` — deux booléens
  qui signalent que la méthode fait plusieurs choses. `format="texte"` masque en
  outre le *builtin* `format`.
- **Cache jamais invalidé** (49-50) : `charger` ne relit la base que si `TACHES`
  est vide. Dans un processus qui vit longtemps, une tâche ajoutée par un autre
  poste n'apparaîtra jamais.
- **Effet de bord caché** (115) : `rapport` écrit `t["score"]` dans les
  dictionnaires partagés. Une tâche en retard hier garde son score une fois
  l'échéance repoussée.
- **Fonction au nom trompeur** (162-169) : `nettoyer` modifie son argument en
  place et retourne… un compte. Ni son nom ni son type de retour ne l'annoncent.

## 3. Les bugs silencieux

Par ordre de gravité :

1. **Les dates sont comparées comme des chaînes** (l. 106). `"05/10/2026" <
   "15/09/2026"` est **vrai** : une tâche due en octobre est déclarée en retard
   en septembre, avec un nombre de jours de retard **négatif**, donc un score
   négatif qui vient réduire le total. À l'inverse `"20/08/2026" <
   "15/09/2026"` est **faux** : une tâche en retard d'un mois n'est jamais
   signalée. La règle métier la plus importante du script est fausse, et rien
   ne le dit.

2. **Base vide = travail terminé** (l. 125). Quand il n'y a aucune tâche,
   l'avancement vaut 100 %. Une base neuve, ou un fichier de base au mauvais
   chemin (`CONFIG["base"]` vient de `config.json`), produit un rapport
   « 0 tâches, 0 terminées (100 %) » parfaitement rassurant.

3. **Une priorité inconnue pèse zéro** (l. 114). `"Haute"` avec une majuscule,
   ou `"urgente"`, donne `poids = 0`, donc un score nul : la tâche est classée
   **dernière** du rapport. C'est exactement l'inverse de l'intention de celui
   qui a tapé « urgente ». Notez que c'est précisément le point où l'évolution
   demandée (`critique`) devra s'insérer.

4. **`terminer` cherche par préfixe** (l. 87). `terminer("1")` marque la
   première tâche dont l'identifiant *commence par* 1 — si la tâche 1 n'est
   plus en tête de liste, ce sera la 10, la 11 ou la 100. Et `terminer("")`
   termine la première tâche de la liste. La méthode retourne `True` dans tous
   ces cas.

5. **Une échéance illisible fait disparaître la tâche** (l. 110-112). Le
   `continue` la retire des retards ; `self.erreurs` est rempli mais **jamais
   consulté**. Le rapport a l'air complet.

6. **Le rapport peut ne pas exister** (l. 142-143). Si l'écriture échoue, on
   affiche un message et on **retourne quand même le chemin**. L'appelant
   reçoit le nom d'un fichier qui n'existe pas.

7. **L'alerte peut ne jamais partir** (l. 154-155). `except Exception: pass`
   sur l'envoi du mail : le rapport est écrit, le code retourne normalement, et
   personne n'est prévenu des retards.

## 4. Un découpage possible

| Composant | Responsabilité unique | Pour le tester |
|---|---|---|
| `Tache` (`@dataclass(frozen=True)`) | Porter les données d'une tâche, avec une **vraie** `date` d'échéance et une priorité typée (`Enum`) | Rien : c'est une valeur |
| `est_en_retard(tache, jour: date) -> bool` | La règle du retard | Deux dates, un booléen |
| `score(tache, jour, poids) -> int` | La formule | Une tâche, une date, un dict |
| `calculer_bilan(taches, jour, config) -> Bilan` | Trier, totaliser, décider si l'alerte est due | Une liste de `Tache` en mémoire |
| `formater_texte(bilan) -> str`, `formater_json(bilan) -> str` | Produire le texte, **sans écrire** | Un `Bilan`, comparer une chaîne |
| `DepotTaches` (`Protocol` : `lister`, `ajouter`, `terminer`) + `DepotSqlite` | Persister | Le `Protocol` se remplace par une liste en mémoire ; `DepotSqlite` se teste à part avec `sqlite3.connect(":memory:")` |
| `Notificateur` (`Protocol` : `envoyer(sujet, corps)`) + `NotificateurSmtp` | Alerter | Un faux notificateur qui enregistre ce qu'on lui donne |
| `Config` (`@dataclass`) + `charger_config(chemin)` | Lire la configuration **une fois**, explicitement | Un fichier dans `tmp_path`, ou pas de fichier du tout |
| `generer_rapport(depot, notificateur, jour, config)` | Orchestrer les précédents en cinq lignes | Un dépôt en mémoire, un faux notificateur, une date fixe |

Ce découpage rend les trois règles métier de la section 1 testables en
**quelques lignes chacune**, sans base, sans mail, sans fichier, sans horloge.

## 5. Par où commencer

Par la règle du retard (l. 106), pour trois raisons :

- c'est le **risque métier** le plus élevé : elle est fausse aujourd'hui ;
- c'est la plus **simple à extraire** : deux dates en entrée, un booléen en sortie ;
- c'est le point d'entrée de l'évolution demandée : `critique` est une règle
  d'alerte qui dépend du retard.

L'ordre naturel est ensuite : `score`, puis `calculer_bilan`, puis les I/O. Les
tests de caractérisation (Jour 4) permettront de faire ce découpage sans casser
le comportement existant — **à l'exception du bug n° 1, qu'il faudra décider de
corriger, et documenter**.
