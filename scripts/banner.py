#!/usr/bin/env python3
"""Draw the Vesper profile banner (desktop + phone) from assets/palette.json."""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'assets/palette.json').read_text())
FONT = 'Inter,Segoe UI,Helvetica Neue,Arial,sans-serif'
MONO = 'JetBrains Mono,SF Mono,Menlo,Consolas,monospace'


def star(cx, cy, r, fill, cls='', extra=''):
    """Four-point sparkle, like the shell's workspace stars."""
    k = r * 0.28
    d = (f'M{cx} {cy - r}Q{cx + k} {cy - k} {cx + r} {cy}Q{cx + k} {cy + k} {cx} {cy + r}'
         f'Q{cx - k} {cy + k} {cx - r} {cy}Q{cx - k} {cy - k} {cx} {cy - r}Z')
    return f'<path class="{cls}" d="{d}" fill="{fill}" {extra}/>'


def island(cx, w, h, rs=22):
    """The hanging island: flush with the top edge, concave shoulders, round bottom."""
    x0, x1, rb = cx - w / 2, cx + w / 2, h / 2
    return (f'M{x0 - rs} 0A{rs} {rs} 0 0 1 {x0} {rs}V{h - rb}A{rb} {rb} 0 0 0 {x0 + rb} {h}'
            f'H{x1 - rb}A{rb} {rb} 0 0 0 {x1} {h - rb}V{rs}A{rs} {rs} 0 0 1 {x1 + rs} 0Z')


def banner(width, height, mobile):
    rnd = random.Random(7)
    s = 0.5 if mobile else 1.0           # phone layout is drawn at half scale, then enlarged
    moon = (width * (0.74 if mobile else 0.79), height * (0.47 if mobile else 0.5), 78 if mobile else 92)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">rize — vibecoder from poland</title>',
             '<desc id="desc">A night sky in lavender and violet: a crescent moon, a small constellation, '
             'and a rounded island hanging from the top edge with the name rize. Stars twinkle softly; '
             'reduced-motion settings keep them still.</desc>',
             '<defs>',
             f'<clipPath id="card"><rect width="{width}" height="{height}" rx="28"/></clipPath>',
             f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#000"/>'
             f'<stop offset=".35" stop-color="{P["surface_lowest"]}"/><stop offset="1" stop-color="{P["background"]}"/></linearGradient>',
             f'<radialGradient id="glow"><stop stop-color="{P["accent"]}" stop-opacity=".30"/>'
             f'<stop offset=".45" stop-color="{P["accent"]}" stop-opacity=".08"/><stop offset="1" stop-color="{P["accent"]}" stop-opacity="0"/></radialGradient>',
             f'<radialGradient id="haze" cx=".2" cy="1" r=".9"><stop stop-color="{P["tertiary"]}" stop-opacity=".16"/>'
             f'<stop offset="1" stop-color="{P["tertiary"]}" stop-opacity="0"/></radialGradient>',
             f'<linearGradient id="isle" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#000"/>'
             f'<stop offset="1" stop-color="{P["surface"]}"/></linearGradient>',
             f'<linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{P["accent"]}"/>'
             f'<stop offset="1" stop-color="{P["tertiary"]}"/></linearGradient>',
             f'<mask id="crescent"><circle cx="{moon[0]}" cy="{moon[1]}" r="{moon[2]}" fill="#fff"/>'
             f'<circle cx="{moon[0] + moon[2] * 0.42}" cy="{moon[1] - moon[2] * 0.3}" r="{moon[2] * 0.86}" fill="#000"/></mask>',
             '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>',
             '</defs>',
             '<style>'
             '.tw{animation:tw 7s ease-in-out infinite alternate}.tw2{animation-duration:11s;animation-delay:-4s}'
             '.tw3{animation-duration:5s;animation-delay:-2s}'
             '@keyframes tw{from{opacity:.25}to{opacity:.95}}'
             '.cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}'
             '.breathe{animation:br 9s ease-in-out infinite alternate;transform-origin:center;transform-box:fill-box}'
             '@keyframes br{from{opacity:.75}to{opacity:1}}'
             '@media (prefers-reduced-motion:reduce){.tw,.cur,.breathe{animation:none}}'
             '</style>',
             '<g clip-path="url(#card)">',
             f'<rect width="{width}" height="{height}" fill="url(#sky)"/>',
             f'<rect width="{width}" height="{height}" fill="url(#haze)"/>',
             f'<circle cx="{moon[0]}" cy="{moon[1]}" r="{moon[2] * 3.2}" fill="url(#glow)" class="breathe"/>']

    # field of stars
    for i in range(70 if mobile else 140):
        x, y = rnd.uniform(0, width), rnd.uniform(0, height) ** 1.15 / height ** 0.15
        if math.dist((x, y), moon[:2]) < moon[2] * 1.35:
            continue
        r = rnd.choice((0.6, 0.8, 0.8, 1.0, 1.2, 1.5))
        cls = 'tw ' + rnd.choice(('', 'tw2', 'tw3'))
        color = rnd.choice((P['text'], P['text'], P['muted'], P['accent'], P['tertiary']))
        parts.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity=".7"/>')

    # the moon
    mx, my, mr = moon
    parts += [f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{P["accent"]}" opacity=".55" mask="url(#crescent)" filter="url(#soft)"/>',
              f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{P["moon"]}" mask="url(#crescent)"/>']

    # constellation (the workspace indicator, writ large)
    pts = ([(0.10, 0.62), (0.18, 0.50), (0.27, 0.56), (0.35, 0.44), (0.30, 0.30), (0.42, 0.36), (0.48, 0.26)] if not mobile else
           [(0.08, 0.66), (0.17, 0.55), (0.27, 0.61), (0.36, 0.50), (0.31, 0.38), (0.44, 0.43), (0.52, 0.34)])
    pts = [(width * a, height * b) for a, b in pts]
    path = 'M' + 'L'.join(f'{x:.0f} {y:.0f}' for x, y in pts[:5]) + f'M{pts[3][0]:.0f} {pts[3][1]:.0f}L{pts[5][0]:.0f} {pts[5][1]:.0f}L{pts[6][0]:.0f} {pts[6][1]:.0f}'
    parts.append(f'<path d="{path}" fill="none" stroke="url(#line)" stroke-width="{1.4 if not mobile else 1.6}" stroke-opacity=".45" stroke-linecap="round" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(pts):
        big = i in (3, 6)
        r = (13 if big else 8) * (1.1 if mobile else 1)
        col = P['accent'] if i % 2 == 0 else P['tertiary']
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * 1.6:.0f}" fill="{col}" opacity=".18" filter="url(#soft)"/>')
        parts.append(star(round(x), round(y), r, P['moon'] if big else col, 'tw' + (' tw2' if i % 3 == 0 else ' tw3' if i % 3 == 1 else '')))

    # the island, hanging from the top edge
    w, h = (560, 84) if mobile else (600, 78)
    cx = width / 2
    parts += [f'<path d="{island(cx, w, h)}" fill="url(#isle)"/>',
              f'<path d="{island(cx, w, h)}" fill="none" stroke="{P["text"]}" stroke-opacity=".07"/>']
    gx = cx - w / 2 + 44
    gy = h / 2
    parts += [f'<circle cx="{gx}" cy="{gy}" r="21" fill="{P["accent"]}" fill-opacity=".18"/>',
              star(gx, gy, 11, P['accent']),
              f'<text x="{gx + 38}" y="{gy + 10}" font-family="{FONT}" font-size="{30 if mobile else 29}" font-weight="700" fill="{P["text"]}">rize</text>',
              f'<text x="{gx + (114 if mobile else 110)}" y="{gy + 9}" font-family="{FONT}" font-size="{22 if mobile else 21}" fill="{P["muted"]}">vibecoder from poland</text>',
              f'<circle cx="{cx + w / 2 - 36}" cy="{gy}" r="6" fill="{P["success"]}"/>',
              f'<circle cx="{cx + w / 2 - 36}" cy="{gy}" r="11" fill="{P["success"]}" opacity=".18" class="tw tw3"/>']

    # a prompt, because it's probably happening in a terminal
    px, py = (40, height - 46) if mobile else (56, height - 54)
    fs = 24 if mobile else 22
    parts += [f'<text x="{px}" y="{py}" font-family="{MONO}" font-size="{fs}" fill="{P["accent"]}" font-weight="700">~</text>',
              f'<text x="{px + fs * 1.1}" y="{py}" font-family="{MONO}" font-size="{fs}" fill="{P["accent"]}">❯</text>',
              f'<text x="{px + fs * 2.4}" y="{py}" font-family="{MONO}" font-size="{fs}" fill="{P["muted"]}">building whatever i\'m into</text>',
              f'<rect class="cur" x="{px + fs * 2.4 + fs * 0.6 * 27}" y="{py - fs * 0.8}" width="{fs * 0.55:.0f}" height="{fs * 0.95:.0f}" rx="2" fill="{P["accent"]}"/>']

    parts += ['</g>', f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="28" fill="none" stroke="{P["text"]}" stroke-opacity=".06"/>', '</svg>']
    return '\n'.join(parts) + '\n'


if __name__ == '__main__':
    (ROOT / 'assets/banner.svg').write_text(banner(1440, 600, False))
    (ROOT / 'assets/banner-mobile.svg').write_text(banner(720, 560, True))
    print('Drew the banner.')
