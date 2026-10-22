# Redstone : les règles du simulateur (Java Edition)

Le planificateur simule la redstone tick par tick, comme Minecraft Java. Ces règles sont celles que le plan doit respecter pour marcher dans le planificateur **et** dans le jeu.

## Sommaire
1. Puissance et conduction
2. Poudre
3. Composants et délais
4. Pistons
5. Pièges fréquents
6. Recettes (avec l'exemple vérifié à copier)

---

## 1. Puissance et conduction

- Un signal a une puissance de 0 à 15. Les sources donnent 15, sauf le capteur de lumière et le comparateur, dont la sortie varie.
- **Bloc conducteur** : un bloc plein et opaque (`solid`, `lamp`, `obsidian`, `note`, `command`, ou un bloc `mc:` de famille `cube` / `cubefix`). Il peut être alimenté de deux façons :
  - **fortement**, par un levier ou un bouton fixé dessus, une torche juste **en dessous**, ou un répéteur ou comparateur qui pointe dedans. Il alimente alors tout ce qui le touche, poudre comprise ;
  - **faiblement**, par de la poudre qui pointe dedans ou posée dessus. Il n'alimente alors que les composants voisins (répéteur, comparateur, torche accrochée, lampe, piston, porte…), **pas la poudre**.
- **Ne conduisent pas** : verre et blocs `clear`, bloc de redstone, observateur, piston, trémie, dalles, escaliers, blocs `misc`.

## 2. Poudre

- Perd 1 de puissance par bloc. Au-delà de 15 blocs, mets un répéteur.
- Se relie toute seule à ses voisins : poudre, composants, et poudre un bloc plus haut ou plus bas en escalier.
  - Deux lignes parallèles **collées** fusionnent. Laisse au moins une case vide entre deux fils indépendants.
- Monter d'un bloc en escalier ne marche que si **aucun bloc opaque** n'est posé au-dessus de la poudre du bas : il couperait la diagonale.
  - Sur du verre, le signal monte mais ne redescend pas.
- La poudre alimente le bloc **sur lequel** elle est posée et le bloc **vers lequel** elle pointe. Une ligne qui se termine face à une lampe l'allume. Une poudre posée **à côté** d'une lampe sans pointer vers elle ne l'allume pas, sauf en bout de ligne.

## 3. Composants et délais

1 tick de redstone = 0,1 s.

| Composant | Délai | À retenir |
|---|---|---|
| torche | 1 tick | Inverse le signal de son support. Grille si elle s'éteint 8 fois en 3 s (`burnout`), puis se rallume plus tard. |
| répéteur | `d` = 1 à 4 ticks | Remet à 15. Diode : de l'arrière vers l'avant seulement. Allonge une impulsion plus courte que son délai. Verrouillé si un répéteur ou comparateur allumé pointe dans son flanc. |
| comparateur | 1 tick | **Comparaison** : sortie = arrière si arrière ≥ côté, sinon 0. **Soustraction** (`m: 1`) : arrière − côté. Les côtés acceptent seulement poudre, bloc de redstone, répéteur, comparateur et observateur. |
| lampe | 0 à l'allumage, 2 ticks à l'extinction | |
| observateur | 1 tick, puis impulsion de 1 tick | Voit un **changement d'état** du bloc devant sa face : lampe, poudre, piston qui bouge, bloc posé ou cassé. Il ne voit pas l'alimentation d'un bloc opaque. Alimente fortement le bloc derrière lui. |
| bouton | 10 ticks (pierre), 15 (bois) | |
| capteur de lumière | — | Puissance selon l'heure (`settings.time`). `m: 1` le rend actif la nuit. |

Une horloge est une boucle avec un nombre **impair** d'inversions. Sa période vaut 2 × la somme des délais de la boucle.

## 4. Pistons

- Un piston pousse jusqu'à 12 blocs. Il **ne peut pas** pousser l'obsidienne, la trémie, le bloc de commande, le capteur de lumière, un piston sorti ni les blocs `cubefix` / `clearfix` / `miscfix`.
- Il **casse** les blocs fragiles devant lui : poudre, torches, répéteurs, comparateurs, leviers, boutons, plaques, rails, portes, plantes, blocs `flat` et `miscbreak`.
- Sa **face avant n'est pas une entrée**. On l'alimente par l'arrière, un côté, le dessus ou le dessous, ou par un bloc conducteur alimenté qui le touche.
- **Quasi-connectivité** (Java) : un piston s'active aussi si la case juste **au-dessus** de lui est alimentée, même s'il n'y a rien là.
- Le **piston collant** ramène le bloc en rentrant. Un bloc poussé met 1 tick à arriver.

## 5. Pièges fréquents

1. **Mauvais `f` sur un répéteur** : `f` est la direction de **sortie**. Pour un signal qui va de l'ouest vers l'est, `f = 1`.
2. **Torche qui s'auto-éteint** : une torche accrochée à un bloc que sa propre sortie alimente forme une horloge involontaire qui grille.
3. **Poudre collée à un autre fil** : deux fils côte à côte se mélangent. Sépare-les, ou isole-les avec des répéteurs.
4. **Composant sans support** : de la poudre ou un répéteur posé dans le vide, ou une torche accrochée à du verre. Le script `check` les trouve tous.
5. **Lampe alimentée par erreur** : un bloc conducteur fortement alimenté à côté d'une lampe l'allume.
6. **Entrée de piston par l'avant** : ça ne marche pas. Passe par l'arrière ou un côté.
7. **Signal trop faible** après plus de 15 poudres : il manque un répéteur.
8. **Porte sans moitié haute** ou **piston sorti sans tête** : le bloc disparaît au chargement.

## 6. Recettes (avec l'exemple vérifié à copier)

Les fichiers sont dans `assets/exemples/`. Chacun a été testé dans le simulateur : copie, décale (`Plan.include`), puis adapte.

| Besoin | Principe | Exemple |
|---|---|---|
| allumer une lampe | levier → poudre → lampe | `levier-lampe.json` |
| aller loin | un répéteur tous les 15 blocs | `ligne-longue.json` |
| monter | poudre en escalier sur des blocs pleins | `escalier-redstone.json` |
| monter vite | alterner bloc et torche posée dessus (2 inversions = même signal) | `tour-de-torches.json` |
| NON | bloc alimenté + torche accrochée au bloc | `porte-non.json` |
| OU | deux fils qui se rejoignent | `porte-ou.json` |
| ET | une torche sur chaque bloc d'entrée, fil reliant les torches, torche de sortie | `porte-et.json` |
| NON-ET / NON-OU | variantes | `porte-non-et.json`, `porte-non-ou.json` |
| XOR / XNOR | deux comparateurs en soustraction | `porte-xor.json`, `porte-xnor.json` |
| horloge réglable | torche + 2 répéteurs en boucle | `horloge-repeteurs.json` |
| mémoire 1 bit | bascule RS (2 torches) | `bascule-rs.json` |
| mémoire avec verrou | répéteur verrouillé par le flanc | `verrou-repeteur.json` |
| bouton → interrupteur | bascule T maître-esclave | `bascule-t.json` |
| détecter un changement | observateur qui regarde le bloc | `detecteur-changement.json` |
| lire un conteneur | comparateur derrière une trémie | `seuil-tremie.json` |
| lampadaire de nuit | capteur de lumière + torche | `lampadaire-automatique.json` |
| porte en fer | bouton de chaque côté | `porte-fer-boutons.json` |
| porte cachée | 4 pistons collants, torches | `porte-secrete-2x2.json` |
| piston qui coupe un fil | piston devant de la poudre | `piston-casse-poudre.json` |
| interrupteur à pistons | piston collant + bloc de redstone | `interrupteur-bloc-redstone.json` |
| calcul | demi-additionneur, additionneur complet | `demi-additionneur.json`, `additionneur-complet.json` |
| compter | compteur binaire 3 bits | `compteur-3-bits.json` |
| à éviter | horloge trop rapide qui grille | `horloge-trop-rapide.json` |

`assets/exemples/_index.md` décrit chaque exemple : ses entrées, ses sorties et sa taille.
