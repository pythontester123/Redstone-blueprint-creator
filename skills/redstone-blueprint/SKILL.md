---
name: redstone-blueprint
description: Crée des plans (blueprints) Minecraft au format JSON de Redstone Planner, prêts à importer, sans avoir besoin du fichier HTML du planificateur. Couvre circuits de redstone (portes logiques, horloges, mémoires, portes à pistons, additionneurs, compteurs, fermes, mécanismes) et constructions avec les 1 109 blocs posables de Minecraft Java. Utilise ce skill dès que l'utilisateur veut un plan, un schéma, un blueprint, un circuit ou une construction Minecraft/redstone à importer dans Redstone Planner, ou demande de « faire un plan redstone », « créer un circuit », « dessiner une porte à pistons », même s'il ne cite pas le planificateur ni le JSON. Also use for "redstone blueprint", "Minecraft schematic for Redstone Planner".
---

# Plans Redstone Planner

Redstone Planner est un planificateur de redstone pour Minecraft Java, dans un seul fichier HTML. Il simule les circuits, les montre en 2D, en 3D et à la première personne, et les exporte vers Minecraft (Java et Bedrock). Il importe des plans JSON : ce skill t'apprend à les écrire. L'utilisateur colle ensuite ton JSON dans le planificateur, ou choisit ton fichier, et le circuit apparaît et fonctionne.

Le planificateur est strict : un type inconnu disparaît, et un composant sans support (poudre dans le vide, torche accrochée à du verre) casse comme dans le jeu. L'utilisateur ne voit l'erreur qu'après l'import. **Vérifie donc toujours le plan avant de le livrer.**

## Démarche

1. **Comprendre le besoin.** Repère les entrées (leviers, boutons, plaques, capteur), les sorties (lampes, pistons, portes) et le comportement attendu. Ne pose une question que si le besoin est vraiment ambigu. Sinon, choisis une solution classique et dis-le.
2. **Partir d'un exemple vérifié.** `assets/exemples/_index.md` liste 26 circuits testés dans le simulateur : portes logiques, horloges, mémoires, pistons, additionneurs, compteur… Pars de l'exemple le plus proche plutôt que de tout réinventer : copie-le, décale-le, combine-le. `references/redstone.md` donne les règles du jeu et une table « besoin → exemple ».
3. **Dessiner couche par couche.** Fixe la direction du signal : de préférence de l'ouest vers l'est (x croissant), entrées à gauche, sorties à droite. Garde au moins une case entre deux fils indépendants. Mets la logique en `y = 0` ou `y = 1`, sur des blocs `solid`.
4. **Écrire le plan.** Le plus sûr est d'utiliser la bibliothèque Python `scripts/blueprint.py`, si tu peux exécuter du code. Sinon, écris le JSON à la main en suivant les règles ci-dessous.
5. **Vérifier**, avec `python3 scripts/blueprint.py check plan.json` puis `show plan.json`. Corrige toutes les erreurs. Relis chaque avertissement : il signale souvent un `f` inversé. Sans exécution de code, déroule la liste de contrôle à la fin de ce fichier.
6. **Livrer** le plan (voir « Livraison »).

## Le format en bref

```json
{
  "format": "redstone-planner", "version": 1,
  "name": "Porte NON", "description": "Levier activé : lampe éteinte.",
  "settings": {"burnout": true, "qc": true, "time": 6000, "dayCycle": false},
  "blocks": [
    {"t":"lever","x":0,"y":0,"z":0,"f":5},
    {"t":"dust","x":1,"y":0,"z":0,"f":0},
    {"t":"dust","x":2,"y":0,"z":0,"f":0},
    {"t":"solid","x":3,"y":0,"z":0,"f":0},
    {"t":"torch","x":4,"y":0,"z":0,"f":3},
    {"t":"dust","x":5,"y":0,"z":0,"f":0},
    {"t":"lamp","x":6,"y":0,"z":0,"f":0}
  ]
}
```

- **Repère** : `x` va vers l'est, `z` vers le sud (le nord est en `z` négatif), `y` est la hauteur (0 à 31). La couche `y = 0` repose sur le sol du monde, qui sert de support.
- **Directions de `f`** : 0 = nord, 1 = est, 2 = sud, 3 = ouest, 4 = haut, 5 = bas. `f` est toujours présent (0 si le bloc n'a pas d'orientation).
- **Booléens** : écris `1`, ou omets le champ.

### Types de base et sens de `f`

| `t` | Bloc | `f` veut dire |
|---|---|---|
| `lever`, `button_stone`, `button_wood` | levier, boutons | côté du **bloc qui le porte** (5 = au sol, 4 = au plafond, 0-3 = accroché au bloc voisin dans cette direction) |
| `torch` | torche de redstone | côté du **bloc support** (5 = posée dessus, 0-3 = accrochée sur le côté ; jamais 4) |
| `repeater` (`d` = délai 1-4) | répéteur | direction de **sortie** |
| `comparator` (`m: 1` = soustraction) | comparateur | direction de **sortie** |
| `observer` | observateur | direction de la **face qui observe** (il émet par l'arrière) |
| `piston`, `sticky` | pistons | direction de **poussée** |
| `rail` | rail propulseur | 0 = axe nord-sud, 1 = axe est-ouest |
| `door` + `door_top` | porte en fer (2 blocs) | 0-3. Les deux moitiés ont le même `f` |
| `trapdoor` | trappe en fer | 0-3 (`on: 1` = ouverte) |
| `dust`, `plate`, `lamp`, `rblock`, `note` (`p` 0-24), `hopper` (`lvl` 0-15), `daylight` (`m: 1` = nuit), `command` | — | 0 |
| `solid` (pierre, **conduit**), `glass` (verre, ne conduit pas), `obsidian` (conduit, inamovible) | blocs de construction | 0 |

**Tous les autres blocs Minecraft** s'écrivent `"t": "mc:<id>"`, par exemple `mc:oak_planks`, `mc:wheat`, `mc:white_wool` ou `mc:oak_stairs` (pour un escalier, `f` = côté haut). On les trouve avec `python3 scripts/blueprint.py find chêne` ou dans `references/blocs-minecraft.md`.

**Exception** : les variantes de composants (portes et trappes en bois ou en cuivre, boutons en bois, plaques de pression, rails déclencheurs) gardent leur type de base et ajoutent `id`. Exemple : `{"t":"door","id":"oak_door",...}` avec `{"t":"door_top","id":"oak_door",...}` au-dessus. N'écris jamais `mc:oak_door`.

Le détail de chaque champ et de chaque type est dans `references/format.md`.

### Supports : ce qui casse au chargement

- `dust` : un bloc plein, du verre ou une trémie dessous, ou `y = 0`.
- `repeater`, `comparator`, `rail`, `plate`, `door`, les plantes : un bloc à dessus plein dessous, ou `y = 0`. Les plantes acceptent aussi `mc:farmland` et `mc:dirt_path`.
- `torch`, `lever` et boutons avec `f = 5` : un bloc à dessus plein dessous. Avec `f = 0` à `4`, un bloc **plein et opaque** dans la direction `f` : `solid`, `lamp`, `obsidian`, `note`, `command`, `rblock`, `observer`, `piston` ou un `mc:` de famille `cube`. Le verre ne convient pas.
- `door` : toujours un `door_top` au-dessus.
- Piston sorti (`ext: 1`) : toujours sa `piston_head` devant. Le plus simple est de livrer les pistons rentrés.

## Écrire avec la bibliothèque Python

```python
import sys; sys.path.insert(0, "<dossier du skill>/scripts")
from blueprint import Plan

p = Plan("Porte ET", "Lampe allumée si les deux leviers sont activés.")
p.fill("solid", (1, 0, 1), (3, 0, 1))                 # pavé de blocs, coins inclus (walls=True : contour seul)
p.add("lever", 1, 0, 0, f="S"); p.add("lever", 3, 0, 0, f="S")   # accrochés au bloc au sud
p.add("torch", 1, 1, 1, f="D"); p.add("torch", 3, 1, 1, f="D")   # posées sur les blocs
p.add("dust", 2, 1, 1)
p.add("torch", 2, 0, 2, f="N")                          # accrochée au bloc au nord
p.line("dust", (2, 0, 3), (2, 0, 3)); p.add("lamp", 2, 0, 4)
p.door(6, 0, 0, f="S", id="oak_door")                   # porte de 2 blocs
p.piston(8, 0, 0, f="E", sticky=True)
p.include("<dossier du skill>/assets/exemples/porte-non.json", dx=0, dz=10, turns=0)  # réutiliser un exemple
print(p.show())                                         # dessin des couches
p.save("porte-et.json")                                 # vérifie, et refuse d'écrire s'il reste une erreur
```

- `f` accepte `"N"`, `"E"`, `"S"`, `"O"` (ou `"W"`), `"U"`, `"D"`, les noms français (`"nord"`…) ou les entiers 0 à 5.
- `include` peut tourner un exemple de `turns` quarts de tour, dans le sens horaire vu du dessus, en ajustant les orientations.

Commandes en ligne :
- `check` liste les erreurs et les avertissements ;
- `show` dessine chaque couche (nord en haut, `>` = vers l'est…) ;
- `fix` corrige automatiquement : moitiés de porte manquantes, `mc:oak_door` changé en `door` + `id`, champs `format` et `version` manquants ;
- `find` cherche un bloc.

## Livraison

- **Si tu peux créer des fichiers**, livre un fichier `.json` au nom parlant, par exemple `porte-et.json`.
- **Sinon**, donne le JSON complet dans **un seul** bloc de code `json`, sans commentaires (le JSON n'en accepte pas) et sans « … » : l'utilisateur le copie tel quel.
- Après le plan, ajoute quelques lignes pour l'utilisateur, dans sa langue :
  1. **Importer** : dans Redstone Planner, ouvrir le menu « … » puis « Importer… », et choisir le fichier ou coller le JSON dans la zone de texte.
  2. **Essayer** : quelles entrées actionner (clic sur un levier ou un bouton, avec leurs positions) et ce qui doit se passer.
  3. **Si quelque chose cloche** : le bouton « Analyser » du planificateur fait relire le plan par Claude, qui propose des corrections.
  4. **Exporter vers Minecraft** depuis le planificateur, en Java (`.litematic`, `.nbt`, `.schem`, `.mcfunction`) ou en Bedrock (`.mcworld`).
- Reste raisonnable sur la taille : un circuit tient en général en moins de 2 000 blocs et 32 couches. Pour une grosse construction, utilise `fill` avec `walls=True` (murs seuls) ou `hollow=True` (enveloppe avec sol et plafond).

## Liste de contrôle (sans exécution de code)

Avant de livrer un JSON écrit à la main, vérifie chaque point :
1. Chaque `dust`, `repeater`, `comparator`, `rail`, `plate`, `door` et chaque plante a un bloc plein juste en dessous (même x et z, y − 1), ou se trouve en `y = 0`.
2. Chaque torche, levier ou bouton avec `f` de 0 à 4 touche, dans la direction `f`, un bloc plein et opaque, jamais du verre.
3. Chaque répéteur ou comparateur a son `f` dans le sens du trajet du signal, de l'entrée vers la sortie.
4. Deux fils de poudre indépendants ne se touchent pas, même en diagonale d'un étage.
5. Chaque porte a son `door_top` (même `f`, même `id`) et aucun piston n'a `ext` sans sa tête.
6. Pas deux blocs à la même position, et les coordonnées sont des entiers dans les limites.
7. Tous les types existent (table ci-dessus, ou `mc:<id>` du catalogue).
8. Le JSON est valide : guillemets doubles, pas de virgule finale, pas de commentaires.
