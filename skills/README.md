# Skill « redstone-blueprint »

Ce skill permet à Claude, dans n'importe quelle conversation, d'écrire des plans pour Redstone Planner sans avoir besoin de `redstone-planner.html`. Il produit des fichiers JSON prêts à importer (« … » → « Importer… »).

Contenu :
- `SKILL.md` : la démarche et l'essentiel du format ;
- `references/` : le format complet, les règles de redstone et le catalogue des 1 109 blocs ;
- `assets/exemples/` : 26 circuits testés dans le simulateur ;
- `scripts/blueprint.py` : une bibliothèque Python pour construire un plan, plus les commandes `check`, `show`, `fix` et `find`.

## Installation

- **claude.ai / application Claude** : Paramètres → Capacités → Skills → « Importer un skill », puis choisir `redstone-blueprint.skill` (c'est un zip).
- **Claude Code** : copier le dossier `redstone-blueprint/` dans `~/.claude/skills/` (pour tous les projets) ou dans `.claude/skills/` d'un projet.

Ensuite, il suffit de demander par exemple : « Fais-moi un plan redstone d'une porte à pistons 2×2 qui s'ouvre avec une plaque de pression. »
