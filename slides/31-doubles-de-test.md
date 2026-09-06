---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Comprendre les doubles de test"
---

<!-- _class: lead -->

# 1. Comprendre les doubles de test

*Cinq objets différents, souvent appelés « mock » par erreur*

---

# Un double de test remplace une dépendance réelle

Le mot « mock » sert couramment à désigner cinq objets distincts, dont les
usages n'ont rien à voir. Les distinguer change la façon dont on écrit ses tests.

| Double | Ce qu'il fait | On l'utilise pour |
|---|---|---|
| **Dummy** | rien — il occupe une place | satisfaire une signature |
| **Stub** | renvoie une réponse figée | fournir une entrée au test |
| **Fake** | une vraie implémentation, simplifiée | remplacer une infrastructure |
| **Mock** | enregistre les appels **et** les vérifie | vérifier qu'un appel a eu lieu |
| **Spy** | enregistre les appels, sans exiger | observer sans contraindre |

> La distinction utile tient en une question :
> **est-ce que je vérifie un résultat, ou une interaction ?**

---

# Dummy, Stub, Fake

<div class="cols">
<div>

**Dummy** — jamais utilisé

```python
def test_creation_sans_notification():
    rapport = Rapport(notificateur=None)
    assert rapport.titre == "Janvier"
```

**Stub** — une réponse figée

```python
class SourceFigee:
    def lire(self, jour):
        return [Mesure(8, 12.4)]

def test_moyenne():
    analyse = Analyse(SourceFigee())
    assert analyse.moyenne(JOUR) == 12.4
```

</div>
<div>

**Fake** — une vraie implémentation

```python
class DepotEnMemoire:
    def __init__(self):
        self._par_id = {}

    def enregistrer(self, mesure):
        self._par_id[mesure.id] = mesure

    def par_id(self, id):
        return self._par_id.get(id)
```

Il **fonctionne** : on peut écrire,
relire, compter. Il ne persiste
simplement rien sur disque.

</div>
</div>

---

# Mock et Spy

<div class="cols">
<div>

**Mock** — vérifie l'interaction

```python
def test_alerte_envoyee():
    notif = Mock()

    rappeler(taches_en_retard, notif)

    notif.envoyer.assert_called_once_with(
        "3 tâches en retard"
    )
```

L'objet du test est **l'appel**,
pas une valeur de retour.

</div>
<div>

**Spy** — observe sans exiger

```python
class NotificateurEspion:
    def __init__(self):
        self.envoyes = []

    def envoyer(self, message):
        self.envoyes.append(message)


def test_un_seul_rappel_par_personne():
    espion = NotificateurEspion()
    rappeler(taches, espion)
    assert len(espion.envoyes) == 1
```

</div>
</div>

Un spy écrit à la main est souvent **plus lisible** qu'un `Mock`, et son message
d'échec est meilleur : `assert 3 == 1` plutôt que `Expected 'envoyer' to be called once`.

---

# Vérifier un résultat ou vérifier une interaction

C'est la décision qui structure tout le reste.

<div class="cols">
<div>

**Test d'état** — préférable

```python
def test_moyenne_horaire():
    assert moyenne([10, 20]) == 15
```

Vérifie **ce que le code produit**.
Insensible à la façon dont il s'y prend.

Survit au refactoring.

</div>
<div>

**Test d'interaction** — parfois nécessaire

```python
def test_le_cache_evite_un_second_appel():
    source = Mock()
    source.lire.return_value = []
    cache = Cache(source)

    cache.lire(JOUR)
    cache.lire(JOUR)

    assert source.lire.call_count == 1
```

Vérifie **comment** le code s'y prend.
Casse dès qu'on change la mécanique.

</div>
</div>

> **🎯 En pratique** : testez l'interaction seulement quand l'interaction **est**
> le comportement — un envoi de mail, une écriture en base, un appel facturé.

---

# Quand un mock est justifié

| Situation | Pourquoi le mock est le bon outil |
|---|---|
| L'effet est **hors du système** | Envoyer un mail, publier un message, appeler une API payante — il n'y a pas d'état à vérifier chez soi |
| L'appel doit **ne pas** avoir lieu | « en mode simulation, rien n'est écrit » se vérifie avec `assert_not_called` |
| La dépendance est **lente ou instable** | Un service distant qui répond en 3 s, ou pas |
| Il faut **simuler une panne** | Provoquer un timeout ou un HTTP 500 à la demande |
| Le nombre d'appels **est** la règle | Un cache, une limitation de débit, une reprise sur erreur |

Dans les cinq cas, ce qu'on veut vérifier **est** l'interaction. Le mock n'est
pas un contournement : c'est l'outil adapté.

---

# Quand éviter un mock

| Situation | À faire à la place |
|---|---|
| Tester un calcul pur | Rien — appelez la fonction |
| Remplacer un objet de valeur | Construisez le vrai objet, il est gratuit |
| Remplacer un dépôt de données | Écrivez un **fake en mémoire**, réutilisable |
| Contourner un constructeur trop lourd | **Injectez** la dépendance (Jour 1, chapitre 6) |
| Mocker une classe que vous possédez | Extrayez une interface étroite, et faites-en un fake |

> **⚠️ Piège** : si vous devez mocker trois objets pour tester une fonction,
> le problème n'est pas le mocking. C'est que la fonction a trois dépendances
> qu'elle ne devrait pas avoir.

---

# Le danger des tests sur-mockés

```python
def test_generer_rapport():
    source = Mock()
    source.lire.return_value = [Mock(valeur=10), Mock(valeur=20)]
    formateur = Mock()
    formateur.formater.return_value = "..."
    ecrivain = Mock()

    generer(source, formateur, ecrivain)

    ecrivain.ecrire.assert_called_once()
```

Ce test est vert. Que prouve-t-il ?

- que `generer` appelle `ecrire` — donc que le code appelle ce qu'il appelle ;
- **rien** sur la moyenne, le format produit, ni le contenu écrit ;
- il resterait vert si la moyenne devenait fausse.

> Un test entièrement mocké teste **le graphe d'appels**, c'est-à-dire un miroir
> du code de production. Il se casse au moindre refactoring et ne détecte aucun
> bug de calcul.

---

# Tester les frontières du système

Représentez votre librairie comme un noyau entouré d'une frontière :

```
   ┌──────────────────────── frontière ────────────────────────┐
   │                                                           │
   │    fichiers      base de données      API HTTP     horloge│
   │        ▲                ▲                 ▲           ▲   │
   │        │  adapters      │                 │           │   │
   │   ┌────┴────────────────┴─────────────────┴───────────┴──┐│
   │   │                                                      ││
   │   │      NOYAU MÉTIER — fonctions pures, objets de        ││
   │   │      valeur, règles de gestion. Aucun double requis.  ││
   │   └───────────────────────────────────────────────────────┘│
   └───────────────────────────────────────────────────────────┘
```

| Zone | Comment on la teste |
|---|---|
| **Noyau** | tests unitaires directs — aucun double |
| **Adapters** | quelques tests d'intégration contre la vraie ressource |
| **Franchissement** | fakes ou mocks, selon qu'on vérifie un état ou un appel |

**Plus le noyau est gros, moins vous aurez besoin de doubles.**

---

# L'ordre de préférence

Quand une dépendance doit être remplacée, essayez dans cet ordre :

1. **Rien** — la dépendance est-elle vraiment nécessaire ? Un calcul pur n'en a pas.
2. **L'objet réel** — un objet de valeur, une `dataclass`, une liste : gratuits.
3. **Un fake** — une implémentation simplifiée, écrite une fois, réutilisée partout.
4. **Un stub** — trois lignes, quand une seule réponse figée suffit.
5. **Un mock** — seulement si l'**interaction** est ce qu'on veut vérifier.

> **🎯 En pratique** : dans une librairie bien découpée, la majorité des tests
> se situent aux niveaux 1 et 2. Le niveau 5 reste minoritaire — et c'est un bon
> indicateur de conception.

---

# À retenir

> **1.** Cinq doubles, deux familles : ceux qui **fournissent une entrée**
> (dummy, stub, fake) et ceux qui **vérifient une sortie d'interaction**
> (mock, spy).

> **2.** Préférez systématiquement vérifier un **résultat**. Vérifiez une
> interaction seulement quand l'interaction est le comportement attendu.

> **3.** Un besoin de mock complexe est un signal de conception : la dépendance
> est mal isolée, ou la fonction en a trop.
