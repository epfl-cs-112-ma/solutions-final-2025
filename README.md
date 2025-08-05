# Final 2025

[Énoncé](https://epfl-cs-112-ma.github.io/series/12-final-2025.html)

Il y avait deux grandes façons de modéliser les quantités et ressources d'une corporation.
Soit comme une "paire de dictionnaires" ; soit comme un "dictionnaire de paires".

Dans la première variante, on a quelque chose comme

```python
class Corporation:
    amounts: dict[ResourceKind, int]
    productions: dict[ResourceKind, int]
```

Dans la seconde variante, on a plutôt

```python
class Resource:
    amount: int
    production: int

class Corporation:
    resources: dict[ResourceKind, Resource]
```

Ces deux designs donnent lieu a des codes assez différents pour l'ensemble des questions.
C'est pourquoi nous proposons deux implémentations complètes, dans deux fichiers séparés.

---

Certaines copies ont modélisé les forêts comme un type de ressource, qui a toujours une production de 0.
C'était un modèle acceptable, mais que nous ne proposons pas dans cette solution.
Il n'apporte aucune réelle opportunité de factorisation.

---

Pour les actions des cartes, on s'attendait vraiment à utiliser une hiérarchie avec une classe abstraite, dotée d'une méthode abstraite pour effectuer l'action.
L'indication "mais votre conception doit supporter l'ajout d'actions spéciales dans le futur" suggérait fortement cette approche.
Il y avait une unique *opération* (exécuter l'action) mais l'ensemble des *types* d'actions allait évoluer.
C'était d'ailleurs très similaire aux actions des interrupteurs dans le projet, mais également aux mouvements des monstres, ou aux effets du clic souris en fonction de l'arme active.
Les deux solutions proposées utilisent donc ce design.
Malheureusement, très peu de copies ont reconnu ce motif de design.

Pour les prérequis, le design idéal utilise un ADT.
Ici, les manipulations nécessaires dans la question 8 suggéraient fortement que c'était la meilleure stratégie.
C'était aussi renforcé par l'indication "On peut supposer qu'il y aura, dans le futur, d'autres bizarreries telles que celle décrite à la question 8".
En effet, il y aura donc de nombreuses *opérations* à appliquer sur un ensemble fixe de types de prérequis.
Cependant, de nombreuses copies ont utilisé de manière assez efficace une hiérarchie de classe non-ADT (bien que ne permettant pas de garantir l'exhaustivité des transformations pour la question 8).

Dans la solution 1, nous utilisons un ADT.
Dans la solution 2, nous utilisons une hiérarchie de classes.

Beaucoup trop de copies ont représenté actions et prérequis avec un unique attribut `str` (ou s'en approchant).
L'énoncé précisait que ce n'était pas la bonne approche, et pour cause, cela rendait toutes les autres questions beaucoup plus difficiles (et donc longues !) que nécessaire.

---

Finalement, pour la décomposition des chaînes d'actions, il était soit possible d'utiliser `str.split`, soit une expression régulière.
Les deux approches, bien appliquées, étaient équivalentes.
La solution 1 utilise `str.split`, tandis que la solution 2 utilise `re.compile`.

---

L'encapsulation n'a pas été évaluée dans cet examen.
Selon les questions, nous avons parfois été très peu regardant sur l'usage de `Final` ou de dataclass `frozen`.
