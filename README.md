# Redstone Planner

**Dessine tes circuits de redstone avant de les construire dans Minecraft.**
*Plan, simulate and export Minecraft redstone builds, in a single HTML file.*

Redstone Planner est un planificateur de redstone pour Minecraft. Tu poses tes blocs sur une grille, couche par couche, et le circuit **fonctionne tout de suite**, tick par tick, comme dans Minecraft Java. Quand le plan marche, tu l'exportes et tu le retrouves bloc pour bloc dans ton monde, en Java comme en Bedrock.

Tout tient dans **un seul fichier** : [`redstone-planner.html`](redstone-planner.html). Pas d'installation, pas de serveur, pas de compte.

---

## L'idée

Construire de la redstone directement en jeu, c'est beaucoup d'essais et d'erreurs : un répéteur dans le mauvais sens, une poudre qui ne tient pas, un piston qui casse le fil d'à côté… Redstone Planner sert de **brouillon** :

1. **Dessiner** : poser, tourner et régler les blocs à la souris, en 2D, en 3D ou à la première personne.
2. **Tester** : la simulation tourne en direct. Tu actionnes les leviers et tu vois le signal circuler.
3. **Comprendre** : des leçons guidées, du levier jusqu'au compteur binaire, et une analyse par Claude qui repère les erreurs.
4. **Construire** : export en schéma Litematica, structure, WorldEdit, commandes ou monde Bedrock prêt à ouvrir.

## Ce qu'il sait faire

### Simulation fidèle à Minecraft Java
- Poudre, répéteurs (délais, verrouillage), comparateurs (comparaison, soustraction, lecture des trémies), torches (avec grillage), observateurs, pistons et pistons collants (12 blocs, blocs inamovibles, poudre cassée), quasi-connectivité.
- Leviers, boutons, plaques, capteur de lumière du jour (cycle jour/nuit), lampes, blocs musicaux, rails, portes et trappes.
- **Distributeurs et droppers avec leur contenu** : poudre d'os (les cornichons de mer poussent et se répandent sur le corail), seaux d'eau et de lave, flèches, TNT…
- Les blocs sans support cassent, comme dans le jeu.

### Tous les blocs
Les **1 109 blocs posables** de Minecraft Java (bois, pierre, laine, verre, plantes, cultures, décoration…), avec leurs noms français officiels.

### Trois vues
- **2D**, couche par couche, avec les niveaux de puissance.
- **3D** isométrique : rotation libre au clic droit, zoom à la molette, pose de blocs directement dans la vue.
- **Joueur**, à la première personne : marcher, sauter, voler, s'accroupir (C), sprinter (Maj), casser et poser comme dans Minecraft.

### Import et export
| Format | Export | Import |
|---|---|---|
| Litematica `.litematic` | ✓ | ✓ |
| Structure vanilla `.nbt` | ✓ | ✓ |
| WorldEdit / Sponge `.schem` | ✓ | ✓ |
| Commandes `.mcfunction` (et datapack `.zip`) | ✓ | ✓ |
| Monde Bedrock `.mcworld` | ✓ | ✓ |
| Monde Java (dossier ou `.zip`) | — | ✓ |
| JSON du planificateur | ✓ | ✓ |

À l'import d'un monde, le planificateur trouve tout seul les circuits de redstone qu'il contient.

### Pour apprendre
- **Bibliothèque** de 27 circuits prêts à l'emploi : portes logiques (ET, OU, XOR…), horloges, bascules RS et T, portes à pistons, additionneurs, compteur binaire…
- **18 leçons** sur 6 niveaux, avec des défis vérifiés automatiquement.
- **Analyse par Claude** : il lit le plan, explique comment le signal circule, repère les erreurs et propose des corrections applicables en un clic. Cette fonction ne marche que dans claude.ai.

### Pratique
Sélection de zone sur plusieurs couches (appui long), copier, couper, coller, rotation, annuler/rétablir, liste de matériaux, image PNG, sauvegarde automatique.

## Utiliser le planificateur

- **Dans un navigateur** : télécharge [`redstone-planner.html`](redstone-planner.html) et ouvre-le. Chrome, Edge, Firefox et Safari fonctionnent, sur ordinateur comme sur téléphone.
- **Sous Windows**, en application : le dossier [`desktop/`](desktop) fabrique `RedstonePlanner.exe`, qui ouvre le planificateur dans sa propre fenêtre et garde tes circuits d'un lancement à l'autre.
  ```sh
  cd desktop && ./build.sh      # nécessite Go 1.21 ou plus
  ```

## Faire des plans avec n'importe quelle conversation Claude

Le dossier [`skills/`](skills) contient le skill **redstone-blueprint**. Une fois installé, Claude sait écrire des plans pour le planificateur dans n'importe quelle conversation, sans avoir besoin du fichier HTML. Il connaît le format, les règles de la redstone et les 1 109 blocs, s'appuie sur 26 circuits vérifiés et contrôle le plan avant de te le donner.

- **claude.ai** : Paramètres → Capacités → Skills → importer [`skills/redstone-blueprint.skill`](skills/redstone-blueprint.skill).
- **Claude Code** : copier `skills/redstone-blueprint/` dans `~/.claude/skills/`.

Ensuite, demande par exemple : *« Fais-moi un plan redstone d'une porte à pistons 2×2 qui s'ouvre avec une plaque de pression. »* Importe le fichier obtenu avec « … » → « Importer… ».

## Le format des plans

Un plan est un simple fichier JSON, facile à écrire à la main ou par programme :

```json
{
  "format": "redstone-planner", "version": 1,
  "blocks": [
    {"t":"lever", "x":0, "y":0, "z":0, "f":5},
    {"t":"dust",  "x":1, "y":0, "z":0, "f":0},
    {"t":"dust",  "x":2, "y":0, "z":0, "f":0},
    {"t":"lamp",  "x":3, "y":0, "z":0, "f":0}
  ]
}
```

`x` va vers l'est, `z` vers le sud et `y` vers le haut. `f` donne l'orientation : 0 nord, 1 est, 2 sud, 3 ouest, 4 haut, 5 bas. La référence complète est dans [`skills/redstone-blueprint/references/format.md`](skills/redstone-blueprint/references/format.md).

## Organisation du dépôt

```
redstone-planner.html          le planificateur complet (un seul fichier)
desktop/                       lanceur Windows (.exe)
skills/redstone-blueprint/     skill Claude : format, règles, catalogue, exemples, script de vérification
skills/redstone-blueprint.skill  le même skill, prêt à importer
```

---

Redstone Planner n'est ni affilié à Mojang ni à Microsoft. *Minecraft* est une marque de Mojang AB.
