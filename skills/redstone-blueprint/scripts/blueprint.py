#!/usr/bin/env python3
"""Plans pour Redstone Planner : construire, vérifier, afficher.

Utilisation en ligne de commande :
  python3 blueprint.py check plan.json      vérifie le plan (erreurs et avertissements)
  python3 blueprint.py show plan.json       dessine chaque couche en texte
  python3 blueprint.py fix plan.json [out]  corrige ce qui peut l'être sans risque
  python3 blueprint.py find chêne           cherche un bloc Minecraft par son nom

Utilisation comme bibliothèque :
  from blueprint import Plan
  p = Plan("Levier vers lampe")
  p.add("lever", 0, 0, 0, f="D")
  p.line("dust", (1, 0, 0), (4, 0, 0))
  p.add("lamp", 5, 0, 0)
  p.save("levier-lampe.json")          # vérifie avant d'écrire

Aucune dépendance : Python 3.8 ou plus.
"""
import json
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
MAXY, HALF = 32, 512

# Directions : N = -z, E = +x, S = +z, O (ouest) = -x, U = haut, D = bas
N, E, S, O, U, D = range(6)
DIRS = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
OPP = [2, 3, 0, 1, 5, 4]
DIR_NAMES = {'n': N, 'nord': N, 'north': N, 'e': E, 'est': E, 'east': E, 's': S, 'sud': S, 'south': S,
             'o': O, 'w': O, 'ouest': O, 'west': O, 'u': U, 'haut': U, 'up': U, 'd': D, 'bas': D, 'down': D}
DIR_LABEL = ['nord', 'est', 'sud', 'ouest', 'haut', 'bas']

# Types de base du planificateur : orientation, support nécessaire, dessus plein, côtés pleins, conduit le signal
#   rot : h4 = N/E/S/O, all6 = 6 directions, att6 = accroché (6), att5 = accroché sauf plafond, axis = 0 (N-S) ou 1 (E-O)
#   needs : floor = un dessus plein en dessous ; dust = idem ou une trémie ; att = le bloc dans la direction f
BASE = {
    'lever':        dict(rot='att6', needs='att', fr='Levier'),
    'button_stone': dict(rot='att6', needs='att', fr='Bouton en pierre'),
    'button_wood':  dict(rot='att6', needs='att', fr='Bouton en bois (chêne)'),
    'plate':        dict(needs='floor', fr='Plaque de pression'),
    'rblock':       dict(top=1, side=1, fr='Bloc de redstone'),
    'torch':        dict(rot='att5', needs='att', fr='Torche de redstone'),
    'daylight':     dict(fr='Capteur de lumière du jour'),
    'dust':         dict(needs='dust', fr='Poudre de redstone'),
    'repeater':     dict(rot='h4', needs='floor', fr='Répéteur'),
    'comparator':   dict(rot='h4', needs='floor', fr='Comparateur'),
    'observer':     dict(rot='all6', top=1, side=1, fr='Observateur'),
    'hopper':       dict(fr='Trémie'),
    'command':      dict(top=1, side=1, cond=1, fr='Bloc de commande'),
    'lamp':         dict(top=1, side=1, cond=1, fr='Lampe de redstone'),
    'piston':       dict(rot='all6', top=1, side=1, fr='Piston'),
    'sticky':       dict(rot='all6', top=1, side=1, fr='Piston collant'),
    'note':         dict(top=1, side=1, cond=1, fr='Bloc musical'),
    'rail':         dict(rot='axis', needs='floor', fr='Rail propulseur'),
    'trapdoor':     dict(rot='h4', fr='Trappe en fer'),
    'door':         dict(rot='h4', needs='floor', fr='Porte en fer (bas)'),
    'solid':        dict(top=1, side=1, cond=1, fr='Bloc solide (pierre)'),
    'glass':        dict(top=1, fr='Verre'),
    'obsidian':     dict(top=1, side=1, cond=1, fr='Obsidienne'),
    'piston_head':  dict(rot='all6', fr='Tête de piston'),
    'door_top':     dict(rot='h4', fr='Porte (haut)'),
}
CLASS = {
    'cube': dict(top=1, side=1, cond=1), 'cubefix': dict(top=1, side=1, cond=1),
    'clear': dict(top=1), 'clearfix': dict(top=1),
    'plant': dict(needs='floor'), 'flat': dict(needs='floor'),
    'slab': {}, 'stairs': dict(rot='h4'), 'post': {}, 'misc': {}, 'miscfix': {}, 'miscbreak': {},
}
# Bloc Minecraft que représente chaque type de base (ces id ne sont pas dans le catalogue mc:)
MC_OF_BASE = {'lever': 'lever', 'button_stone': 'stone_button', 'button_wood': 'oak_button', 'plate': 'stone_pressure_plate',
              'rblock': 'redstone_block', 'torch': 'redstone_torch', 'daylight': 'daylight_detector', 'dust': 'redstone_wire',
              'repeater': 'repeater', 'comparator': 'comparator', 'observer': 'observer', 'hopper': 'hopper',
              'command': 'command_block', 'lamp': 'redstone_lamp', 'piston': 'piston', 'sticky': 'sticky_piston',
              'note': 'note_block', 'rail': 'powered_rail', 'trapdoor': 'iron_trapdoor', 'door': 'iron_door', 'solid': 'stone',
              'glass': 'glass', 'obsidian': 'obsidian'}
BASE_OF_MC = {v: k for k, v in MC_OF_BASE.items()}
BASE_OF_MC.update({'redstone_wall_torch': 'torch', 'piston_head': 'piston_head', 'moving_piston': 'piston'})
ROT_OK = {'h4': {0, 1, 2, 3}, 'all6': set(range(6)), 'att6': set(range(6)), 'att5': {0, 1, 2, 3, 5}, 'axis': {0, 1}}
KEYS = ['t', 'x', 'y', 'z', 'f', 'on', 'lvl', 'd', 'm', 'p', 'ext', 'dot', 'lock', 'burnt', 'sticky', 'id']
REDSTONE = {'lever', 'button_stone', 'button_wood', 'plate', 'rblock', 'torch', 'daylight', 'dust', 'repeater',
            'comparator', 'observer', 'hopper'}
OUTPUTS = {'lamp', 'piston', 'sticky', 'note', 'door', 'trapdoor', 'rail', 'command'}

_BLOCS = None


def blocs():
    """Catalogue : id Minecraft -> [famille, nom français, catégorie, (type de base pour les variantes)]"""
    global _BLOCS
    if _BLOCS is None:
        with open(os.path.join(HERE, 'blocs.json'), encoding='utf-8') as fh:
            _BLOCS = json.load(fh)
    return _BLOCS


def props(t):
    """Propriétés de comportement d'un type (base ou mc:<id>), None s'il est inconnu."""
    if t in BASE:
        return BASE[t]
    if isinstance(t, str) and t.startswith('mc:'):
        info = blocs().get(t[3:])
        if info and len(info) < 4:
            return dict(CLASS[info[0]], fr=info[1], cls=info[0])
    return None


def parse_dir(f):
    if f is None:
        return None
    if isinstance(f, bool):
        raise ValueError(f'direction invalide : {f!r}')
    if isinstance(f, int):
        return f
    key = str(f).strip().lower()
    if key.isdigit():
        return int(key)
    if key not in DIR_NAMES:
        raise ValueError(f'direction inconnue : {f!r} (N, E, S, O, U, D)')
    return DIR_NAMES[key]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------
class Plan:
    """Un plan en cours de construction. Les positions sont uniques : poser sur une case occupée la remplace."""

    def __init__(self, name=None, description=None, time=6000, day_cycle=False):
        self.name, self.description = name, description
        self.settings = {'burnout': True, 'qc': True, 'time': time, 'dayCycle': day_cycle}
        self.cells = {}

    # -- poser --
    def add(self, t, x, y, z, f=None, **kw):
        if t in DEFAULT_F and f is None:
            f = DEFAULT_F[t]
        b = {'t': t, 'x': int(x), 'y': int(y), 'z': int(z), 'f': parse_dir(f) or 0}
        for k, v in kw.items():
            if k not in KEYS:
                raise ValueError(f'propriété inconnue : {k}')
            if v is None or v is False or v == 0:
                continue
            b[k] = 1 if v is True else v
        if b['t'] == 'repeater':
            b['d'] = int(kw.get('d') or 1)
        self.cells[(b['x'], b['y'], b['z'])] = b
        return self

    def remove(self, x, y, z):
        self.cells.pop((x, y, z), None)
        return self

    def get(self, x, y, z):
        return self.cells.get((x, y, z))

    def line(self, t, a, b, f=None, **kw):
        """Ligne droite (ou diagonale régulière) de a à b inclus."""
        dx, dy, dz = (b[i] - a[i] for i in range(3))
        n = max(abs(dx), abs(dy), abs(dz))
        for i in range(n + 1):
            k = i / n if n else 0
            self.add(t, round(a[0] + dx * k), round(a[1] + dy * k), round(a[2] + dz * k), f, **kw)
        return self

    def fill(self, t, a, b, f=None, hollow=False, walls=False, **kw):
        """Remplit le pavé entre les coins a et b (inclus).
        hollow=True : seulement l'enveloppe, sol et plafond compris (comme /fill … hollow).
        walls=True : seulement les murs verticaux, sans sol ni plafond (un contour sur une seule couche)."""
        xs = range(min(a[0], b[0]), max(a[0], b[0]) + 1)
        ys = range(min(a[1], b[1]), max(a[1], b[1]) + 1)
        zs = range(min(a[2], b[2]), max(a[2], b[2]) + 1)
        for x in xs:
            for y in ys:
                for z in zs:
                    edge_x, edge_z = x in (xs[0], xs[-1]), z in (zs[0], zs[-1])
                    if walls and not (edge_x or edge_z):
                        continue
                    if hollow and not (edge_x or edge_z or y in (ys[0], ys[-1])):
                        continue
                    self.add(t, x, y, z, f, **kw)
        return self

    def door(self, x, y, z, f='S', id=None, on=False):
        """Porte de deux blocs (bas + haut). id = variante en bois/cuivre, ex. 'oak_door'."""
        kw = {'id': id, 'on': on}
        self.add('door', x, y, z, f, **kw)
        self.add('door_top', x, y + 1, z, f, **kw)
        return self

    def piston(self, x, y, z, f, sticky=False, ext=False):
        """Piston (collant ou non). ext=True ajoute la tête devant lui."""
        f = parse_dir(f)
        self.add('sticky' if sticky else 'piston', x, y, z, f, ext=ext)
        if ext:
            d = DIRS[f]
            self.add('piston_head', x + d[0], y + d[1], z + d[2], f, sticky=sticky)
        return self

    def include(self, other, dx=0, dy=0, dz=0, turns=0):
        """Copie un autre plan (Plan, dict ou chemin .json), tourné de turns quarts de tour (sens horaire vu du dessus) puis décalé."""
        if isinstance(other, str):
            with open(other, encoding='utf-8') as fh:
                other = json.load(fh)
        blocks = other.blocks() if isinstance(other, Plan) else other['blocks']
        for b in blocks:
            b = dict(b)
            x, z = b['x'], b['z']
            for _ in range(turns % 4):
                x, z = -z, x
                b['f'] = rotate_f(b, b.get('f', 0))
            b['x'], b['y'], b['z'] = x + dx, b['y'] + dy, z + dz
            self.cells[(b['x'], b['y'], b['z'])] = b
        return self

    # -- sortie --
    def blocks(self):
        return sorted(self.cells.values(), key=lambda b: (b['y'], b['z'], b['x']))

    def to_dict(self):
        out = {'format': 'redstone-planner', 'version': 1}
        if self.name:
            out['name'] = self.name
        if self.description:
            out['description'] = self.description
        out['settings'] = self.settings
        out['blocks'] = self.blocks()
        return out

    def check(self):
        return check(self.to_dict())

    def save(self, path, strict=True):
        data = self.to_dict()
        errors, warnings = check(data)
        report(errors, warnings, path)
        if errors and strict:
            raise SystemExit(f'{len(errors)} erreur(s) : plan non écrit. Corrige-les ou appelle save(path, strict=False).')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(dumps(data))
        return path

    def show(self):
        return show(self.to_dict())


DEFAULT_F = {'repeater': E, 'comparator': E, 'piston': E, 'sticky': E, 'observer': O, 'torch': D, 'lever': D,
             'button_stone': D, 'button_wood': D, 'rail': 1, 'trapdoor': N, 'door': S, 'door_top': S}


def rotate_f(b, f):
    """Nouvelle orientation après un quart de tour horaire (vu du dessus)."""
    p = props(b['t']) or {}
    rot = p.get('rot')
    if rot == 'axis':
        return 1 - f
    if rot and f < 4:
        return (f + 1) % 4
    return f


def dumps(data):
    """JSON lisible : un bloc par ligne."""
    head = {k: v for k, v in data.items() if k != 'blocks'}
    lines = ['{']
    for k, v in head.items():
        lines.append(f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},')
    lines.append('  "blocks": [')
    bl = data.get('blocks', [])
    for i, b in enumerate(bl):
        lines.append('    ' + json.dumps(b, ensure_ascii=False, separators=(',', ':')) + (',' if i < len(bl) - 1 else ''))
    lines += ['  ]', '}']
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# Vérification : mêmes règles que le planificateur
# ---------------------------------------------------------------------------
def check(data):
    errors, warnings = [], []
    if not isinstance(data, dict) or not isinstance(data.get('blocks'), list):
        return ['Le fichier doit être un objet JSON avec une liste "blocks".'], []
    if data.get('format') != 'redstone-planner':
        warnings.append('Ajoute "format": "redstone-planner" et "version": 1 en tête du fichier.')
    world = {}
    for i, b in enumerate(data['blocks']):
        where = f'bloc n°{i + 1}'
        if not isinstance(b, dict):
            errors.append(f'{where} : ce n’est pas un objet.')
            continue
        t = b.get('t')
        p = props(t)
        if p is None:
            if isinstance(t, str) and t.startswith('mc:') and t[3:] in BASE_OF_MC:
                errors.append(f'{where} : {t} est un type de base du planificateur. Écris "t": "{BASE_OF_MC[t[3:]]}".')
            elif isinstance(t, str) and t.startswith('mc:') and t[3:] in blocs():
                base = blocs()[t[3:]][3]
                errors.append(f'{where} : "{t}" est une variante de composant. Écris "t": "{base}", "id": "{t[3:]}".')
            else:
                errors.append(f'{where} : type inconnu {t!r} (le planificateur l’ignorerait). Cherche-le avec : blueprint.py find …')
            continue
        bad = [k for k in ('x', 'y', 'z') if not isinstance(b.get(k), int) or isinstance(b.get(k), bool)]
        if bad:
            errors.append(f'{where} ({t}) : {", ".join(bad)} doit être un entier.')
            continue
        x, y, z = b['x'], b['y'], b['z']
        where = f'{t} en ({x}, {y}, {z})'
        if not (-HALF <= x < HALF and -HALF <= z < HALF and 0 <= y < MAXY):
            errors.append(f'{where} : hors limites (x et z de -512 à 511, y de 0 à 31).')
            continue
        if (x, y, z) in world:
            errors.append(f'{where} : case déjà occupée par {world[(x, y, z)]["t"]} (un seul bloc par case).')
        unknown = [k for k in b if k not in KEYS]
        if unknown:
            warnings.append(f'{where} : propriété(s) ignorée(s) {unknown}.')
        f = b.get('f', 0)
        rot = p.get('rot')
        if not isinstance(f, int) or isinstance(f, bool):
            errors.append(f'{where} : "f" doit être un entier (0 à 5).')
        elif rot and f not in ROT_OK[rot]:
            msg = 'une torche ne s’accroche pas au plafond' if rot == 'att5' and f == U else f'orientation f={f} impossible ({rot})'
            errors.append(f'{where} : {msg}.')
        if t == 'repeater' and b.get('d', 1) not in (1, 2, 3, 4):
            errors.append(f'{where} : délai "d" de 1 à 4.')
        if t == 'note' and not (0 <= b.get('p', 0) <= 24):
            errors.append(f'{where} : hauteur "p" de 0 à 24.')
        if 'lvl' in b and not (0 <= b['lvl'] <= 15):
            errors.append(f'{where} : "lvl" de 0 à 15.')
        if 'id' in b and BASE_OF_MC.get(b['id']) == (lo_t := ('door' if t == 'door_top' else t)):
            warnings.append(f'{where} : "id": "{b["id"]}" est déjà le bloc par défaut de {lo_t}, tu peux le retirer.')
        elif 'id' in b:
            info = blocs().get(b['id'])
            if not info:
                errors.append(f'{where} : id Minecraft inconnu {b["id"]!r}.')
            elif t != 'door_top' and (len(info) < 4 or info[3] != t):
                want = info[3] if len(info) > 3 else None
                errors.append(f'{where} : l’id {b["id"]!r} ne va pas avec le type {t!r}'
                              + (f' (il faut "t": "{want}").' if want else f' (écris plutôt "t": "mc:{b["id"]}" sans "id").'))
        world[(x, y, z)] = b

    get = world.get

    def has(b, key):
        return bool(b) and bool((props(b['t']) or {}).get(key))

    def top_ok(x, y, z, dust):
        if y < 0:
            return True                                  # le sol du monde
        b = get((x, y, z))
        return has(b, 'top') or (dust and bool(b) and b['t'] == 'hopper')

    def soil(x, y, z):
        b = get((x, y, z))
        return bool(b) and b['t'] in ('mc:farmland', 'mc:dirt_path')

    for (x, y, z), b in world.items():
        t, p, f = b['t'], props(b['t']), b.get('f', 0)
        where = f'{t} en ({x}, {y}, {z})'
        needs = p.get('needs')
        if t == 'door_top':
            lo = get((x, y - 1, z))
            if not lo or lo['t'] != 'door':
                errors.append(f'{where} : il manque le bas de la porte ("door") juste en dessous.')
            elif lo.get('f', 0) != f or lo.get('id') != b.get('id'):
                errors.append(f'{where} : même "f" et même "id" que le bas de la porte, s’il te plaît.')
            continue
        if t == 'door':
            up = get((x, y + 1, z))
            if not up or up['t'] != 'door_top':
                errors.append(f'{where} : une porte fait deux blocs. Ajoute {{"t":"door_top","x":{x},"y":{y + 1},"z":{z},"f":{f}'
                              + (f',"id":"{b["id"]}"' if b.get('id') else '') + '}.')
        if t == 'piston_head':
            d = DIRS[f]
            pb = get((x - d[0], y - d[1], z - d[2]))
            if not pb or pb['t'] not in ('piston', 'sticky') or not pb.get('ext') or pb.get('f', 0) != f:
                errors.append(f'{where} : une tête de piston n’existe que devant un piston sorti ("ext": 1) de même "f".')
            continue
        if t in ('piston', 'sticky') and b.get('ext'):
            d = DIRS[f]
            h = get((x + d[0], y + d[1], z + d[2]))
            if not h or h['t'] != 'piston_head' or h.get('f', 0) != f:
                errors.append(f'{where} : piston sorti sans sa tête ("piston_head") devant lui. Le plus simple : piston rentré, sans "ext".')
        if needs == 'floor':
            ok = top_ok(x, y - 1, z, False) or (p.get('cls') == 'plant' and soil(x, y - 1, z))
            if not ok:
                under = get((x, y - 1, z))
                errors.append(f'{where} : il lui faut un bloc plein dessous (y={y - 1} : {under["t"] if under else "vide"}).')
        elif needs == 'dust':
            if not top_ok(x, y - 1, z, True):
                under = get((x, y - 1, z))
                errors.append(f'{where} : la poudre doit reposer sur un bloc plein, du verre, une trémie ou le sol y=0 '
                              f'(dessous : {under["t"] if under else "vide"}).')
        elif needs == 'att':
            if f == D:
                if not top_ok(x, y - 1, z, False):
                    errors.append(f'{where} : posé au sol (f=5) mais rien de plein en dessous.')
            else:
                d = DIRS[f]
                s = get((x + d[0], y + d[1], z + d[2]))
                if not has(s, 'side'):
                    errors.append(f'{where} : accroché vers le {DIR_LABEL[f]} (f={f}) à '
                                  f'{s["t"] if s else "rien"} ; il faut un bloc plein et opaque à cet endroit.')

    # Avertissements de logique (heuristiques, pas des règles du jeu)
    def neighbours(x, y, z):
        for d in DIRS:
            yield get((x + d[0], y + d[1], z + d[2]))

    for (x, y, z), b in world.items():
        t = b['t']
        where = f'{t} en ({x}, {y}, {z})'
        if t == 'dust':
            near = [n for n in neighbours(x, y, z) if n and n['t'] in REDSTONE | OUTPUTS | {'solid', 'rblock'}]
            diag = any(get((x + d[0], y + k, z + d[2])) and get((x + d[0], y + k, z + d[2]))['t'] == 'dust'
                       for d in DIRS[:4] for k in (-1, 1))
            if not near and not diag and not has(get((x, y - 1, z)), 'cond'):
                warnings.append(f'{where} : poudre isolée, reliée à rien.')
        if t in ('repeater', 'comparator'):
            d = DIRS[b.get('f', 0)]
            if not get((x + d[0], y, z + d[2])):
                warnings.append(f'{where} : sa sortie (côté {DIR_LABEL[b.get("f", 0)]}) donne sur le vide. Vérifie "f" : c’est la direction de SORTIE.')
            if not get((x - d[0], y, z - d[2])) and t == 'repeater':
                warnings.append(f'{where} : rien derrière lui (côté {DIR_LABEL[OPP[b.get("f", 0)]]}), donc pas d’entrée.')
        if t in OUTPUTS:
            around = [n for n in neighbours(x, y, z) if n]
            if t == 'door':
                top = get((x, y + 1, z))
                around += [n for n in neighbours(x, y + 1, z) if n and n is not b] if top else []
            pistons = any(get((x + d[0] * k, y + d[1] * k, z + d[2] * k)) and get((x + d[0] * k, y + d[1] * k, z + d[2] * k))['t'] in ('piston', 'sticky')
                          for d in DIRS for k in (2, 3))
            if not pistons and not any(n['t'] in REDSTONE or has(n, 'cond') for n in around):
                warnings.append(f'{where} : aucun composant ni bloc conducteur à côté, il ne sera jamais activé.')
    return errors, warnings


def report(errors, warnings, label='plan'):
    for e in errors:
        print('ERREUR  ' + e)
    for w in warnings:
        print('attention  ' + w)
    if not errors and not warnings:
        print(f'{label} : OK, aucun problème trouvé.')
    elif not errors:
        print(f'{label} : valide ({len(warnings)} avertissement(s) à relire).')
    else:
        print(f'{label} : {len(errors)} erreur(s), {len(warnings)} avertissement(s).')


# ---------------------------------------------------------------------------
# Affichage texte : une grille par couche, nord en haut, x vers la droite
# ---------------------------------------------------------------------------
ARROW = '^>v<ud'
SYM = {'solid': '#', 'glass': 'g', 'obsidian': 'X', 'dust': '+', 'lamp': 'L', 'lever': 'l', 'button_stone': 'b',
       'button_wood': 'b', 'plate': '_', 'torch': 't', 'repeater': 'R', 'comparator': 'C', 'observer': 'o',
       'piston': 'P', 'sticky': 'S', 'piston_head': 'h', 'rblock': 'r', 'daylight': 'j', 'hopper': 'H',
       'command': 'c', 'note': 'n', 'rail': '=', 'trapdoor': 'T', 'door': 'D', 'door_top': 'D'}


def show(data):
    bl = [b for b in data['blocks'] if isinstance(b, dict) and isinstance(b.get('x'), int)]
    if not bl:
        return '(plan vide)'
    x0, x1 = min(b['x'] for b in bl), max(b['x'] for b in bl)
    z0, z1 = min(b['z'] for b in bl), max(b['z'] for b in bl)
    letters, legend_mc = iter('abdefikmpqsuvwxyzABEFGIJKMNOQUVWYZ0123456789'), {}
    out = []
    for y in sorted({b['y'] for b in bl}):
        layer = {(b['x'], b['z']): b for b in bl if b['y'] == y}
        used = {}
        out.append(f'--- couche y={y}   (x de {x0} à {x1} vers la droite, z de {z0} à {z1} vers le bas, nord en haut)')
        out.append('   x ' + ''.join(f'{abs(x) % 10} ' for x in range(x0, x1 + 1)).rstrip())
        for z in range(z0, z1 + 1):
            row = ''
            for x in range(x0, x1 + 1):
                b = layer.get((x, z))
                if not b:
                    row += '. '
                    continue
                t = b['t']
                if t in SYM:
                    s = SYM[t]
                else:
                    if t not in legend_mc:
                        legend_mc[t] = next(letters, '?')
                    s = legend_mc[t]
                used[s] = t + (f' ({b["id"]})' if b.get('id') else '')
                p = props(t) or {}
                if t == 'dust':
                    s2 = '*' if b.get('on') else ' '
                elif p.get('rot') == 'axis':
                    s2 = '|' if b.get('f', 0) == 0 else '-'
                elif p.get('rot'):
                    s2 = ARROW[b.get('f', 0)]
                else:
                    s2 = '*' if b.get('on') else ' '
                row += s + s2
            out.append(f'{z:>4} ' + row.rstrip())
        out.append('     ' + '  '.join(f'{s}={t}' for s, t in sorted(used.items())))
    out.append('Flèches : ^ nord, > est, v sud, < ouest, u haut, d bas (sortie des répéteurs/comparateurs, poussée des pistons, '
               'face observée de l’observateur, bloc support des torches/leviers/boutons). * = allumé.')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Corrections sûres
# ---------------------------------------------------------------------------
def fix(data):
    notes = []
    data.setdefault('format', 'redstone-planner')
    data.setdefault('version', 1)
    cells = {}
    for b in data['blocks']:
        t = b.get('t')
        if isinstance(t, str) and t.startswith('mc:') and props(t) is None and t[3:] in blocs():
            b['t'], b['id'] = blocs()[t[3:]][3], t[3:]
            notes.append(f'{t} -> "t": "{b["t"]}", "id": "{b["id"]}"')
        if isinstance(t, str) and t.startswith('mc:') and t[3:] in BASE_OF_MC:
            b['t'] = BASE_OF_MC[t[3:]]
            notes.append(f'{t} -> "t": "{b["t"]}"')
        if b.get('id') and BASE_OF_MC.get(b['id']) == ('door' if b.get('t') == 'door_top' else b.get('t')):
            notes.append(f'"id": "{b.pop("id")}" retiré (bloc par défaut)')
        if 'f' not in b:
            b['f'] = DEFAULT_F.get(b.get('t'), 0)
        elif isinstance(b['f'], str):
            b['f'] = parse_dir(b['f'])
        key = (b.get('x'), b.get('y'), b.get('z'))
        if key in cells:
            notes.append(f'doublon retiré en {key} ({cells[key]["t"]} remplacé par {b.get("t")})')
        cells[key] = b
    for (x, y, z), b in list(cells.items()):
        if b.get('t') == 'door' and (x, y + 1, z) not in cells and y + 1 < MAXY:
            top = {'t': 'door_top', 'x': x, 'y': y + 1, 'z': z, 'f': b.get('f', S)}
            if b.get('id'):
                top['id'] = b['id']
            cells[(x, y + 1, z)] = top
            notes.append(f'moitié haute ajoutée à la porte en ({x}, {y}, {z})')
    data['blocks'] = sorted(cells.values(), key=lambda b: (b.get('y', 0), b.get('z', 0), b.get('x', 0)))
    return data, notes


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')


def find(words):
    """Cherche par id ou nom français, sans tenir compte des accents. Les mots entiers passent en premier."""
    import re
    q = [fold(w) for w in words]
    hits = []

    def score(text):
        toks = re.split(r'[^a-z0-9]+', fold(text))
        sc = 0
        for w in q:
            if w not in fold(text):
                return None
            sc += 3 if w in toks else 2 if any(t.startswith(w) for t in toks) else 1
        return sc

    for k, v in BASE.items():
        if k in ('piston_head', 'door_top'):
            continue
        sc = score(k + ' ' + MC_OF_BASE.get(k, '').replace('_', ' ') + ' ' + v['fr'])
        if sc is not None:
            hits.append((sc + 1, f'"t":"{k}"', 'base', v['fr']))
    for k, v in blocs().items():
        sc = score(k.replace('_', ' ') + ' ' + v[1])
        if sc is not None:
            how = f'"t":"{v[3]}","id":"{k}"' if len(v) > 3 else f'"t":"mc:{k}"'
            hits.append((sc, how, v[0], v[1]))
    hits.sort(key=lambda h: (-h[0], len(h[1])))
    return [f'{h[1]:<44} {h[2]:<9} {h[3]}' for h in hits]


def main(argv):
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__)
        return 0
    cmd, args = argv[1], argv[2:]
    if cmd == 'find':
        hits = find(args)
        print('\n'.join(hits[:80]) if hits else 'Aucun bloc trouvé.')
        if len(hits) > 80:
            print(f'… {len(hits) - 80} de plus : précise la recherche.')
        return 0
    if not args:
        print('Indique le fichier du plan.')
        return 2
    with open(args[0], encoding='utf-8') as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as e:
            print(f'ERREUR  JSON invalide : {e}')
            return 1
    if cmd == 'check':
        errors, warnings = check(data)
        report(errors, warnings, args[0])
        return 1 if errors else 0
    if cmd == 'show':
        print(show(data))
        return 0
    if cmd == 'fix':
        data, notes = fix(data)
        out = args[1] if len(args) > 1 else args[0]
        with open(out, 'w', encoding='utf-8') as fh:
            fh.write(dumps(data))
        print('\n'.join(notes) if notes else 'Rien à corriger automatiquement.')
        errors, warnings = check(data)
        report(errors, warnings, out)
        return 1 if errors else 0
    print(f'Commande inconnue : {cmd}')
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
