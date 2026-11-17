"""Pixel drawing for the profile: two bitmap fonts and SVG output where one unit is one pixel.

Every image is drawn on a grid of logical pixels (the SVG viewBox) and scaled up with crisp edges,
so nothing depends on fonts installed on the viewer's machine.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE = json.loads((ROOT / 'assets/palette.json').read_text())

# 5x7 font: uppercase, digits, a few symbols. Rows top to bottom, '#' = ink.
BIG = {
 'A': '.###. #...# #...# ##### #...# #...# #...#', 'B': '####. #...# #...# ####. #...# #...# ####.',
 'C': '.###. #...# #.... #.... #.... #...# .###.', 'D': '####. #...# #...# #...# #...# #...# ####.',
 'E': '##### #.... #.... ####. #.... #.... #####', 'F': '##### #.... #.... ####. #.... #.... #....',
 'G': '.###. #...# #.... #.### #...# #...# .####', 'H': '#...# #...# #...# ##### #...# #...# #...#',
 'I': '.###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.', 'J': '..### ...#. ...#. ...#. ...#. #..#. .##..',
 'K': '#...# #..#. #.#.. ##... #.#.. #..#. #...#', 'L': '#.... #.... #.... #.... #.... #.... #####',
 'M': '#...# ##.## #.#.# #.#.# #...# #...# #...#', 'N': '#...# #...# ##..# #.#.# #..## #...# #...#',
 'O': '.###. #...# #...# #...# #...# #...# .###.', 'P': '####. #...# #...# ####. #.... #.... #....',
 'Q': '.###. #...# #...# #...# #.#.# #..#. .##.#', 'R': '####. #...# #...# ####. #.#.. #..#. #...#',
 'S': '.#### #.... #.... .###. ....# ....# ####.', 'T': '##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..',
 'U': '#...# #...# #...# #...# #...# #...# .###.', 'V': '#...# #...# #...# #...# #...# .#.#. ..#..',
 'W': '#...# #...# #...# #.#.# #.#.# #.#.# .#.#.', 'X': '#...# #...# .#.#. ..#.. .#.#. #...# #...#',
 'Y': '#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..', 'Z': '##### ....# ...#. ..#.. .#... #.... #####',
 '0': '.###. #...# #..## #.#.# ##..# #...# .###.', '1': '..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.',
 '2': '.###. #...# ....# ...#. ..#.. .#... #####', '3': '##### ...#. ..#.. ...#. ....# #...# .###.',
 '4': '...#. ..##. .#.#. #..#. ##### ...#. ...#.', '5': '##### #.... ####. ....# ....# #...# .###.',
 '6': '..##. .#... #.... ####. #...# #...# .###.', '7': '##### ....# ...#. ..#.. .#... .#... .#...',
 '8': '.###. #...# #...# .###. #...# #...# .###.', '9': '.###. #...# #...# .#### ....# ...#. .##..',
 '.': '. . . . . . #', ',': '.. .. .. .. .. .# #.', ':': '. . # . . # .', "'": '# # . . . . .',
 '!': '# # # # # . #', '?': '.###. #...# ....# ...#. ..#.. ..... ..#..', '-': '... ... ... ### ... ... ...',
 '+': '..... ..#.. ..#.. ##### ..#.. ..#.. .....', '/': '....# ...#. ...#. ..#.. .#... .#... #....',
 '·': '.. .. .. ## ## .. ..', '(': '.# #. #. #. #. #. .#', ')': '#. .# .# .# .# .# #.',
 '&': '.##.. #..#. #.#.. .#... #.#.# #..#. .##.#', '#': '.#.#. ##### .#.#. .#.#. .#.#. ##### .#.#.',
 '>': '#... .#.. ..#. ...# ..#. .#.. #...', '<': '...# ..#. .#.. #... .#.. ..#. ...#',
 '_': '..... ..... ..... ..... ..... ..... #####', '=': '..... ..... ##### ..... ##### ..... .....',
 '@': '.###. #...# #.### #.#.# #.### #.... .####', '*': '..... #.#.# .###. ##### .###. #.#.# .....',
 '→': '..... ..#.. ...#. ##### ...#. ..#.. .....', '♥': '..... .#.#. ##### ##### .###. ..#.. .....',
 '▸': '#... ##.. ###. #### ###. ##.. #...', ' ': '... ... ... ... ... ... ...',
}

# 3x5 font for small captions.
SMALL = {
 'A': '.#. #.# ### #.# #.#', 'B': '##. #.# ##. #.# ##.', 'C': '.## #.. #.. #.. .##', 'D': '##. #.# #.# #.# ##.',
 'E': '### #.. ##. #.. ###', 'F': '### #.. ##. #.. #..', 'G': '.## #.. #.# #.# .##', 'H': '#.# #.# ### #.# #.#',
 'I': '### .#. .#. .#. ###', 'J': '..# ..# ..# #.# .#.', 'K': '#.# #.# ##. #.# #.#', 'L': '#.. #.. #.. #.. ###',
 'M': '#.# ### ### #.# #.#', 'N': '##. #.# #.# #.# #.#', 'O': '.#. #.# #.# #.# .#.', 'P': '##. #.# ##. #.. #..',
 'Q': '.#. #.# #.# ##. .##', 'R': '##. #.# ##. #.# #.#', 'S': '.## #.. .#. ..# ##.', 'T': '### .#. .#. .#. .#.',
 'U': '#.# #.# #.# #.# ###', 'V': '#.# #.# #.# #.# .#.', 'W': '#.# #.# ### ### #.#', 'X': '#.# #.# .#. #.# #.#',
 'Y': '#.# #.# .#. .#. .#.', 'Z': '### ..# .#. #.. ###',
 '0': '### #.# #.# #.# ###', '1': '.#. ##. .#. .#. ###', '2': '##. ..# .#. #.. ###', '3': '##. ..# .#. ..# ##.',
 '4': '#.# #.# ### ..# ..#', '5': '### #.. ##. ..# ##.', '6': '.## #.. ### #.# ###', '7': '### ..# .#. .#. .#.',
 '8': '### #.# ### #.# ###', '9': '### #.# ### ..# ##.',
 '.': '. . . . #', ':': '. # . # .', '·': '. . # . .', '-': '... ... ### ... ...', '/': '..# ..# .#. #.. #..',
 ',': '. . . # #', "'": '# # . . .', '!': '# # # . #', '+': '... .#. ### .#. ...', ' ': '.. .. .. .. ..',
}

FONTS = {'big': BIG, 'small': SMALL}


def glyph(ch, font='big'):
    table = FONTS[font]
    return (table.get(ch.upper()) or table['?' if '?' in table else ' ']).split()


def text_width(s, font='big', scale=1):
    widths = [len(glyph(c, font)[0]) for c in s]
    return (sum(widths) + max(len(widths) - 1, 0)) * scale


def text_pixels(s, x, y, font='big', scale=1):
    """Set of (x, y) logical pixels covered by s, top-left at (x, y)."""
    out = set()
    for ch in s:
        rows = glyph(ch, font)
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == '#':
                    for dy in range(scale):
                        for dx in range(scale):
                            out.add((x + c * scale + dx, y + r * scale + dy))
        x += (len(rows[0]) + 1) * scale
    return out


def dilate(pixels, n=1):
    out = set(pixels)
    for _ in range(n):
        out |= {(x + dx, y + dy) for x, y in out for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    return out


def shift(pixels, dx, dy):
    return {(x + dx, y + dy) for x, y in pixels}


def path_d(pixels):
    """Horizontal runs as one compact path: M x y h w v 1 h -w z."""
    rows = {}
    for x, y in pixels:
        rows.setdefault(y, []).append(x)
    parts = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            parts.append(f'M{start} {y}h{prev - start + 1}v1h-{prev - start + 1}z')
            if x is not None:
                start = prev = x
    return ''.join(parts)


def paint(pixels, color, extra=''):
    if not pixels:
        return ''
    return f'<path fill="{color}" d="{path_d(pixels)}"{extra}/>'


def text(s, x, y, color, font='big', scale=1, extra=''):
    return paint(text_pixels(s, x, y, font, scale), color, extra)


def notched(w, h, n=2):
    """Rectangle with stepped 8-bit corners, n pixels deep."""
    d = f'M{n} 0H{w - n}'
    for i in range(1, n + 1):
        d += f'V{i}H{w - n + i}'
    d += f'V{h - n}'
    for i in range(1, n + 1):
        d += f'H{w - i}V{h - n + i}'
    d += f'H{n}'
    for i in range(1, n + 1):
        d += f'V{h - i}H{n - i}'
    d += f'V{n}'
    for i in range(1, n + 1):
        d += f'H{i}V{n - i}'
    return d + 'Z'


def svg(w, h, scale, title, desc, body, style=''):
    return '\n'.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale}" height="{h * scale}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-labelledby="t d">',
        f'<title id="t">{html.escape(title)}</title><desc id="d">{html.escape(desc)}</desc>',
        f'<style>{style}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>' if style else '',
        *body,
        '</svg>', ''])


def save(name, content):
    (ROOT / 'assets' / name).write_text(content)
