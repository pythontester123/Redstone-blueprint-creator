# Exemples vérifiés

Chaque fichier a été chargé et testé dans le simulateur du planificateur (tables de vérité, horloges, mémoires). Les positions sont `(x, y, z)`.

| Fichier | Niveau | Ce que ça fait | Entrées | Sorties | Taille (x×y×z) |
|---|---|---|---|---|---|
| `levier-lampe.json` | 1 | **Levier → lampe** : Le circuit de base, plus un bouton qui passe par un répéteur. | levier (0,0,0), bouton (0,0,2) | lampe (4,0,0), lampe (4,0,2) | 5x1x3 (10 blocs) |
| `ligne-longue.json` | 1 | **Ligne longue** : Un répéteur tous les 15 blocs garde le signal à pleine puissance sur 34 blocs. | levier (0,0,0) | lampe (34,0,0) | 35x1x1 (35 blocs) |
| `escalier-redstone.json` | 2 | **Escalier de redstone** : La poudre monte d’un bloc à chaque marche tant qu’aucun bloc opaque ne la coupe par le dessus. | levier (0,0,0) | lampe (5,3,0) | 6x4x1 (12 blocs) |
| `tour-de-torches.json` | 2 | **Tour de torches** : Le signal monte en alternant blocs et torches. Deux inversions : la lampe du sommet suit le levier. | levier (-1,0,0) | lampe (0,4,0) | 2x5x1 (6 blocs) |
| `porte-non.json` | 2 | **Porte NON** : Une torche sur un bloc inverse le signal : levier activé, lampe éteinte. | levier (0,0,0) | lampe (6,0,0) | 7x1x1 (7 blocs) |
| `porte-ou.json` | 2 | **Porte OU** : Deux lignes qui se rejoignent : la lampe s’allume si au moins un levier est activé. | levier (0,0,0), levier (0,0,2) | lampe (5,0,1) | 6x1x3 (10 blocs) |
| `porte-et.json` | 2 | **Porte ET** : Lampe allumée si les deux leviers sont activés. Les deux torches d’entrée sont à l’étage Y 1. | levier (1,0,0), levier (3,0,0) | lampe (2,0,4) | 3x2x5 (11 blocs) |
| `porte-non-et.json` | 2 | **Porte NON-ET** : Deux inverseurs dont les sorties se rejoignent : la lampe s’éteint seulement si les deux leviers sont activés. | levier (0,0,0), levier (0,0,4) | lampe (6,0,2) | 7x1x5 (15 blocs) |
| `porte-non-ou.json` | 2 | **Porte NON-OU** : Une porte OU suivie d’une torche : la lampe est allumée seulement si aucun levier n’est activé. | levier (0,0,0), levier (0,0,2) | lampe (8,0,1) | 9x1x3 (13 blocs) |
| `porte-xor.json` | 5 | **Porte XOR** : Deux comparateurs en soustraction : la lampe s’allume si un seul levier est activé. | levier (0,0,3), levier (7,0,4) | lampe (11,0,4) | 12x1x6 (31 blocs) |
| `porte-xnor.json` | 5 | **Porte XNOR** : Une porte XOR suivie d’un inverseur : la lampe s’allume quand les deux leviers sont dans le même état. | levier (0,0,3), levier (7,0,4) | lampe (14,0,4) | 15x1x6 (34 blocs) |
| `horloge-repeteurs.json` | 3 | **Horloge à répéteurs** : Torche + 2 répéteurs : une période de 1 s. Active le levier pour l’arrêter. | levier (1,0,0) | lampe (5,0,1) | 5x1x4 (13 blocs) |
| `horloge-trop-rapide.json` | 3 | **Horloge trop rapide** : Une torche qui s’alimente elle-même grille après 8 extinctions, puis se rallume 8 s plus tard. | — | lampe (3,0,1) | 3x1x4 (9 blocs) |
| `bascule-rs.json` | 5 | **Bascule RS** : Deux torches qui s’alimentent l’une l’autre gardent un état. Bouton de droite : allume. Bouton de gauche : éteint. | bouton (0,0,3), bouton (6,0,3) | lampe (3,0,1) | 7x1x5 (16 blocs) |
| `verrou-repeteur.json` | 3 | **Verrou à répéteur** : Levier du haut : la donnée. Levier du bas : verrouille le répéteur, qui garde alors son état. | levier (0,0,1), levier (2,0,3) | lampe (4,0,1) | 5x1x3 (7 blocs) |
| `bascule-t.json` | 5 | **Bascule T (bouton)** : Chaque appui sur le bouton inverse la lampe. Deux répéteurs verrouillés forment une mémoire maître-esclave. | bouton (0,0,1) | lampe (9,0,4) | 10x1x7 (29 blocs) |
| `piston-casse-poudre.json` | 4 | **Piston qui casse la poudre** : En haut : levier derrière le piston, la poudre devant est cassée. En bas : le signal arrive par la face avant, le piston ne bouge pas (règle Java). | levier (0,0,0), levier (3,0,3) | piston (1,0,0), piston (1,0,3) | 4x1x4 (7 blocs) |
| `interrupteur-bloc-redstone.json` | 4 | **Interrupteur à bloc de redstone** : Le piston collant pousse le bloc de redstone contre la lampe, puis le ramène. | levier (0,0,0) | piston collant (1,0,0), lampe (4,0,0) | 5x1x1 (4 blocs) |
| `porte-fer-boutons.json` | 2 | **Porte en fer à boutons** : Un bouton de chaque côté alimente le bloc voisin de la porte, qui s’ouvre pendant 1 s. | bouton (0,0,0), bouton (2,0,2) | porte (1,0,1) | 3x3x3 (11 blocs) |
| `porte-secrete-2x2.json` | 4 | **Porte secrète 2×2** : Active le levier : les pistons collants rentrent et ouvrent le passage. Essaie la vue 3D. | levier (4,0,5) | piston collant (2,1,2), piston collant (7,1,2), piston collant (2,2,2), piston collant (7,2,2) | 10x4x4 (49 blocs) |
| `lampadaire-automatique.json` | 3 | **Lampadaire automatique** : Capteur de lumière + inverseur : les lampes s’allument la nuit. Active le cycle jour/nuit accéléré à gauche. | capteur (0,0,1) | lampe (4,0,0), lampe (7,0,1), lampe (4,0,2) | 8x1x3 (10 blocs) |
| `detecteur-changement.json` | 4 | **Détecteur de changement** : L’observateur regarde la lampe : chaque fois qu’elle change, il envoie une impulsion et le bloc musical joue. | levier (0,0,0) | lampe (2,0,0), bloc musical (5,0,0) | 6x1x1 (6 blocs) |
| `seuil-tremie.json` | 3 | **Seuil de remplissage** : Le comparateur lit la trémie (clic droit pour la remplir). La lampe s’allume à partir de 7/15. | trémie (0,0,0) | lampe (9,0,0) | 10x1x1 (10 blocs) |
| `demi-additionneur.json` | 6 | **Demi-additionneur** : Additionne deux bits. Lampe de droite : somme (A XOR B). Lampe du bas : retenue (A ET B). | levier (0,0,3), levier (7,0,4) | lampe (11,0,4), lampe (0,0,8) | 12x1x8 (38 blocs) |
| `additionneur-complet.json` | 6 | **Additionneur complet 1 bit** : A + B + retenue d’entrée. Deux demi-additionneurs et un OU sur les retenues. Lampe de droite : somme ; lampe du bas : retenue de sortie. | levier (0,0,3), levier (7,0,4), levier (18,0,4) | lampe (23,0,4), lampe (14,0,10) | 24x1x10 (93 blocs) |
| `compteur-3-bits.json` | 6 | **Compteur binaire 3 bits** : Chaque appui sur le bouton ajoute 1. Les lampes donnent le nombre en binaire, bit de poids faible à gauche (0 à 7). | bouton (0,0,1) | lampe (9,0,4), lampe (21,0,4), lampe (33,0,4) | 34x1x8 (113 blocs) |
