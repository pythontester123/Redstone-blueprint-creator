# Format des plans Redstone Planner (référence complète)

## Sommaire
1. Structure du fichier
2. Repère, coordonnées et directions
3. Champs d'un bloc
4. Les types de base, un par un
5. Blocs Minecraft du catalogue (`mc:<id>`) et variantes (`id`)
6. Règles de support (ce qui casse au chargement)
7. Ce que le planificateur ignore ou recalcule

---

## 1. Structure du fichier

```json
{
  "format": "redstone-planner",
  "version": 1,
  "name": "Porte NON",
  "description": "Levier activé : lampe éteinte.",
  "settings": {"burnout": true, "qc": true, "time": 6000, "dayCycle": false},
  "blocks": [
    {"t":"lever","x":0,"y":0,"z":0,"f":5},
    {"t":"dust","x":1,"y":0,"z":0,"f":0}
  ]
}
```

- `blocks` est le seul champ obligatoire. Les autres sont recommandés.
- `name` et `description` ne sont pas lus par le planificateur. Ils servent au lecteur humain.
- `settings` contient quatre réglages :
  - `burnout` : les torches grillent si elles clignotent trop vite ;
  - `qc` : la quasi-connectivité des pistons, comme en Java ;
  - `time` : l'heure en ticks de jeu (0-23999 ; 6000 = midi, 18000 = minuit), utilisée par le capteur de lumière ;
  - `dayCycle` : `true` fait avancer l'heure.
- Écris un bloc par ligne : le fichier reste lisible et facile à corriger.

## 2. Repère, coordonnées et directions

- `x` va vers l'**est** et `z` vers le **sud**, comme dans Minecraft. Le nord correspond donc à `z` négatif.
- `y` est la hauteur. La couche `y = 0` repose sur le sol du monde : ce sol sert de support, donc de la poudre ou un répéteur en `y = 0` n'a pas besoin de bloc dessous.
- Limites : `x` et `z` vont de −512 à 511, `y` de 0 à 31. Un bloc hors limites est ignoré.
- Une seule case par position. Avec deux blocs au même endroit, le dernier gagne.
- Commence près de (0, 0, 0). Le planificateur recadre la vue tout seul.

`f` est un entier qui donne une direction :

| f | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| direction | nord (−z) | est (+x) | sud (+z) | ouest (−x) | haut (+y) | bas (−y) |
| lettre | N | E | S | O | U | D |

`f` est obligatoire dans le fichier. Mets `0` quand le bloc n'a pas d'orientation.

## 3. Champs d'un bloc

| Champ | Type | Sens |
|---|---|---|
| `t` | texte | type (section 4) ou `mc:<id>` (section 5) |
| `x`,`y`,`z` | entiers | position |
| `f` | 0-5 | orientation : son sens dépend du type (section 4) |
| `on` | 1 | état initial « actif » : levier baissé, trappe/porte ouverte, torche allumée, lampe allumée… |
| `d` | 1-4 | délai du répéteur en ticks de redstone (1 tick = 0,1 s) |
| `m` | 1 | comparateur en **soustraction**, ou capteur de lumière **inversé** (détecte la nuit) |
| `lvl` | 0-15 | trémie : niveau de remplissage lu par un comparateur. Pour la poudre, c'est la puissance (recalculée) |
| `p` | 0-24 | note du bloc musical |
| `ext` | 1 | piston sorti. Il faut alors une `piston_head` devant |
| `sticky` | 1 | tête de piston collant |
| `id` | texte | variante Minecraft d'un composant (ex. `oak_door`), voir section 5 |

Les booléens s'écrivent `1`. Omets un champ quand il est faux ou nul.

## 4. Les types de base, un par un

### Sources

| `t` | Bloc Minecraft | `f` | Notes |
|---|---|---|---|
| `lever` | levier | **côté du bloc qui le porte** : 5 = posé au sol, 4 = au plafond, 0-3 = accroché au bloc situé au nord, à l'est… | `on: 1` = activé. Alimente fortement le bloc qui le porte. |
| `button_stone` | bouton en pierre | comme le levier | Impulsion de 10 ticks (1 s). |
| `button_wood` | bouton en bois | comme le levier | Impulsion de 15 ticks. |
| `plate` | plaque de pression en pierre | 0 | Sur un bloc plein. Active tant qu'on marche dessus. |
| `rblock` | bloc de redstone | 0 | Source permanente de 15. Ne conduit pas, ne rend pas un bloc voisin conducteur. Poussable. |
| `torch` | torche de redstone | **côté du bloc support** : 5 = posée dessus, 0-3 = accrochée au bloc au nord, à l'est… (4 interdit) | S'éteint quand son support est alimenté. Alimente fortement le bloc **au-dessus** d'elle. |
| `daylight` | capteur de lumière du jour | 0 | Signal selon `settings.time`. `m: 1` = inversé. |

### Transmission

| `t` | Bloc Minecraft | `f` | Notes |
|---|---|---|---|
| `dust` | poudre de redstone | 0 | Sur un bloc plein, du verre, une trémie ou le sol `y = 0`. Perd 1 par bloc. Se relie seule aux voisins, et monte ou descend d'un bloc en escalier. |
| `repeater` | répéteur | **direction de SORTIE** (la flèche) | `d` = délai 1-4. Entrée à l'arrière (`f` opposé). Un répéteur ou comparateur allumé qui pointe dans son flanc le **verrouille**. |
| `comparator` | comparateur | **direction de SORTIE** | `m: 1` = soustraction. Entrée arrière, entrées latérales sur les deux flancs. Lit une trémie placée derrière lui. |
| `observer` | observateur | **direction de la face qui observe** | Émet une impulsion de 1 tick par l'**arrière** (côté opposé à `f`) quand le bloc observé change. |

### Sorties et mécanismes

| `t` | Bloc Minecraft | `f` | Notes |
|---|---|---|---|
| `lamp` | lampe de redstone | 0 | Bloc plein qui conduit. |
| `piston` / `sticky` | piston / piston collant | **direction de poussée** (0-5) | Ne s'active pas par sa face avant. Avec `ext: 1`, ajoute `{"t":"piston_head","f":<même f>, "sticky":1 si collant}` devant lui. Le plus simple : le laisser rentré. |
| `note` | bloc musical | 0 | `p` = note 0-24. |
| `rail` | rail propulseur | **0 = axe nord-sud, 1 = axe est-ouest** | Sur un bloc plein. |
| `trapdoor` | trappe en fer | 0-3 = côté de la charnière | `on: 1` = ouverte. N'a pas besoin de support. |
| `door` | porte en fer (bas) | 0-3, voir ci-dessous | Toujours avec `{"t":"door_top", même x/z, y+1, même f, même id}`. Sur un bloc plein. |
| `hopper` | trémie | 0 | `lvl` = remplissage 0-15. La poudre peut se poser dessus. Ne conduit pas. |
| `command` | bloc de commande | 0 | Bloc plein décoratif. La commande n'est pas simulée. |

Pour la porte, `f` est l'opposé du `facing` de Minecraft. Avec `f: 2` (sud), la porte vue en jeu « regarde » vers le nord, donc on la pose en se tenant au sud. Si l'orientation compte, aligne `f` sur celui d'une porte des exemples.

### Construction

| `t` | Bloc Minecraft | Notes |
|---|---|---|
| `solid` | pierre | Bloc plein **conducteur** : le bloc par défaut pour porter et transmettre le signal. |
| `glass` | verre | Porte la poudre et les torches posées dessus, mais **ne conduit pas**. Utile pour isoler. |
| `obsidian` | obsidienne | Conducteur, mais **impossible à pousser** : sert de butée aux pistons. |

### Parties générées (à écrire seulement en paire)

- `door_top` : le haut de la porte. Il prend le même `f` et le même `id` que le bas.
- `piston_head` : la tête d'un piston sorti. Il prend le même `f`, plus `sticky: 1` si le piston est collant.

## 5. Blocs Minecraft du catalogue (`mc:<id>`) et variantes (`id`)

Les 1 109 blocs posables de Minecraft Java sont disponibles. Leur liste complète est dans `references/blocs-minecraft.md`, et on peut aussi chercher avec `scripts/blueprint.py find <mot>`.

- **Bloc ordinaire** : `{"t":"mc:oak_planks","x":0,"y":0,"z":0,"f":0}`. Son comportement dépend de sa famille :

  | Famille | Comportement |
  |---|---|
  | `cube` / `cubefix` | conduit et porte poudre, répéteurs et torches |
  | `clear` | verre, feuilles… : porte la poudre mais ne conduit pas |
  | `slab` | dalle basse : ne porte rien |
  | `stairs` | `f` = côté haut de la marche |
  | `plant` | plante : il lui faut un sol plein, de la terre labourée (`mc:farmland`) ou un chemin (`mc:dirt_path`) |
  | `flat` | tapis, rails, nénuphar… : sur un bloc plein |
  | `post` | barrière, muret, vitre |
  | `misc` / `miscfix` / `miscbreak` | décoratifs |

- **Variante d'un composant redstone** (portes en bois ou en cuivre, trappes, boutons en bois, plaques de pression, rails déclencheurs) : écris le **type de base** avec `id`.
  - Exemple : `{"t":"door","id":"oak_door",...}` + `{"t":"door_top","id":"oak_door",...}`, ou `{"t":"button_wood","id":"birch_button",...}`.
  - N'écris jamais `"t":"mc:oak_door"` : le planificateur le chargerait comme un bloc inerte. Le script `fix` le corrige.
  - Les portes et trappes en bois (ou en cuivre) réagissent seulement aux **changements** de signal : elles s'ouvrent quand le signal arrive et se ferment quand il part. Elles gardent leur état de départ (`on`) tant que rien ne change, et s'ouvrent aussi à la main.
- Les blocs de base ont déjà leur type : pierre = `solid`, verre = `glass`, lampe = `lamp`, piston = `piston`, etc. N'écris pas `mc:stone` pour un bloc qui doit conduire : `solid` est plus clair. (`mc:stone` n'existe d'ailleurs pas dans le catalogue.)
- Eau et lave : `mc:water` et `mc:lava` (sources), posées comme des plantes.

## 6. Règles de support (ce qui casse au chargement)

Le planificateur et Minecraft cassent un bloc qui n'a pas de support. Ces règles ne souffrent pas d'exception :

| Bloc | Il lui faut |
|---|---|
| `dust` | dessous : bloc plein, verre, bloc `clear`, trémie, ou `y = 0` |
| `repeater`, `comparator`, `rail`, `plate`, `door`, plantes, blocs `flat` | dessous : un bloc à dessus plein (`solid`, `lamp`, `glass`, `obsidian`, `rblock`, `observer`, `piston`, `note`, `command`, `cube`, `clear`…) ou `y = 0`. Une plante accepte aussi la terre labourée et le chemin |
| `torch` (f = 5), `lever` / `button` (f = 5) | dessous : un bloc à dessus plein, ou `y = 0` |
| `torch` / `lever` / `button` (f = 0-4) | dans la direction `f` : un bloc **plein et opaque** (`solid`, `lamp`, `obsidian`, `rblock`, `observer`, `piston`, `note`, `command`, `cube`). Pas de verre, de dalle ni de trémie |
| `door` | `door_top` au-dessus avec le même `f` |
| `piston_head` | un piston sorti derrière elle, de même `f` |

La trémie ne porte que de la poudre. Le capteur de lumière, les dalles, les escaliers et les blocs `misc` ne portent rien.

## 7. Ce que le planificateur ignore ou recalcule

- Les états de la poudre, des lampes, des répéteurs et des comparateurs (`on`, `lvl`) sont recalculés au chargement. Les mettre ne sert à rien, sauf pour les **mémoires** (bascule RS, verrous), dont l'état de départ compte.
- Une torche sans `on` démarre éteinte, puis s'allume au premier tick si son support n'est pas alimenté. Dans une bascule RS, mets `on: 1` sur **une seule** des deux torches.
- Deux observateurs face à face (horloge) ne démarrent qu'avec une mise à jour : après l'import, il faut poser ou casser un bloc à côté, comme dans le jeu.
- Une propriété inconnue est ignorée. Un type inconnu fait disparaître le bloc.
