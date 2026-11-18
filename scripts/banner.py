#!/usr/bin/env python3
"""Draw the 8-bit sky banner (desktop + phone) and the pixel section headings.

Run it after changing the palette or the layout; the result is committed. Only the standard library is needed.
"""
import math
import random

from pixel import PALETTE as P, dilate, notched, paint, save, shift, svg, text, text_pixels, text_width

SCALE = 5  # real pixels per logical pixel


def sky(w, h, bands):
    """Flat colour bands with a three-row dither between each pair, like an old console gradient."""
    defs, body = [], []
    for i, (y, color) in enumerate(bands):
        end = bands[i + 1][0] if i + 1 < len(bands) else h
        body.append(f'<rect y="{y}" width="{w}" height="{end - y}" fill="{color}"/>')
    for i in range(1, len(bands)):
        (y, b), a = bands[i], bands[i - 1][1]
        for name, color, cells in ((f'q{i}', b, '<rect width="1" height="1"/><rect x="2" y="1" width="1" height="1"/>'),
                                   (f'h{i}', b, '<rect width="1" height="1"/><rect x="1" y="1" width="1" height="1"/>'),
                                   (f'r{i}', a, '<rect width="1" height="1"/><rect x="2" y="1" width="1" height="1"/>')):
            pw = 4 if name[0] in 'qr' else 2
            defs.append(f'<pattern id="{name}" width="{pw}" height="2" patternUnits="userSpaceOnUse" fill="{color}">{cells}</pattern>')
        body += [f'<rect y="{y - 2}" width="{w}" height="1" fill="url(#q{i})"/>',
                 f'<rect y="{y - 1}" width="{w}" height="1" fill="url(#h{i})"/>',
                 f'<rect y="{y}" width="{w}" height="1" fill="url(#r{i})"/>']
    return defs, body


PUFFS = {  # (x, radius) of each puff along a flat bottom
    's': [(3, 2.5), (8, 3.5), (13, 2.5)],
    'm': [(4, 3.5), (10.5, 4.5), (17, 4), (22.5, 3)],
    'l': [(5, 4), (12, 5.5), (19.5, 6), (27, 4.5), (32.5, 3.5)],
}


def cloud(x, base, kind):
    """A cloud of round puffs sitting on a flat bottom at row `base`. Returns (body, shade) pixel sets."""
    puffs = PUFFS[kind]
    pix = set()
    for cx, r in puffs:
        cy = -r + 0.5
        for py in range(int(cy - r) - 1, 0):
            for px in range(int(cx - r) - 1, int(cx + r) + 2):
                if (px + .5 - cx) ** 2 + (py + .5 - cy) ** 2 <= r * r + 0.5:
                    pix.add((px, py))
    for py in range(-3, 0):
        for px in range(int(puffs[0][0]), int(puffs[-1][0]) + 1):
            pix.add((px, py))
    shade = {(px, py) for px, py in pix if py == -1 or (px + 1, py + 1) not in pix or (px, py + 2) not in pix}
    return shift(pix - shade, x, base), shift(shade, x, base)


def wrap_layer(name, w, elements, seconds):
    """A layer that drifts left forever: drawn three times side by side, moved one pixel per step."""
    return [f'<g id="{name}">{"".join(elements)}</g>',
            f'<use href="#{name}" x="{-w}"/><use href="#{name}" x="{w}"/>'], \
        f'.{name}{{animation:drift{w} {seconds}s steps({w}) infinite}}'


def layer(name, w, clouds, colors, seconds):
    parts = []
    for x, base, kind in clouds:
        body, shade = cloud(x, base, kind)
        parts += [paint(body, colors[0]), paint(shade, colors[1])]
    inner, css = wrap_layer(name, w, parts, seconds)
    return [f'<g class="{name}">', *inner, '</g>'], css


def sea(name, w, h, top, rise, seed, colors, seconds):
    """A periodic bank of cloud tops along the bottom edge."""
    rnd = random.Random(seed)
    bumps = []
    x = 0.0
    while x < w:
        r = rnd.uniform(rise * 0.5, rise)
        bumps.append((x, top + rise, r))
        x += r * rnd.uniform(1.4, 1.9)
    pix = set()
    for py in range(top - 1, h):
        for px in range(w):
            if py >= top + rise or any(min(abs(px + .5 - cx), w - abs(px + .5 - cx)) ** 2 + (py + .5 - cy) ** 2 <= r * r
                                       for cx, cy, r in bumps):
                pix.add((px, py))
    edge = {(px, py) for px, py in pix if (px, py - 1) not in pix}
    rim = {(px, py + 1) for px, py in edge} & pix
    inner, css = wrap_layer(name, w, [paint(pix - edge - rim, colors[0]), paint(rim, colors[1]), paint(edge, colors[2])], seconds)
    return [f'<g class="{name}">', *inner, '</g>'], css


def sun(cx, cy, r):
    body = {(x, y) for x in range(cx - r - 1, cx + r + 2) for y in range(cy - r - 1, cy + r + 2)
            if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r}
    shade = {(x, y) for x, y in body if (x - cx) + (y - cy) > r * 0.55 and (x + 1, y + 1) not in body or
             ((x - cx) + (y - cy) > r * 0.9)}
    glint = {(cx - r // 2 + dx, cy - r // 2 + dy) for dx, dy in ((0, 0), (1, 0), (0, 1))}
    rays_a, rays_b = set(), set()
    for k in range(8):
        a = k * math.pi / 4
        for d in (r + 2, r + 3):
            p = (round(cx - .5 + math.cos(a) * d), round(cy - .5 + math.sin(a) * d))
            (rays_a if k % 2 == 0 else rays_b).add(p)
    return [paint(body - shade - glint, P['sun']), paint(shade, P['sunshade']), paint(glint, P['white']),
            f'<g class="ray">{paint(rays_a, P["sun"])}</g>', f'<g class="ray alt">{paint(rays_b, P["sun"])}</g>']


BIRD_UP = ['#.....#', '.##.##.', '...#...']
BIRD_DOWN = ['.......', '.##.##.', '#..#..#']


def bird(x, y, delay, seconds, span):
    frames = []
    for i, rows in enumerate((BIRD_UP, BIRD_DOWN)):
        pix = {(x + c, y + r) for r, row in enumerate(rows) for c, b in enumerate(row) if b == '#'}
        frames.append(f'<g class="flap{" alt" if i else ""}">{paint(pix, P["navy"])}</g>')
    return [f'<g class="fly" style="animation-duration:{seconds}s;animation-delay:{delay}s;animation-timing-function:steps({span})">',
            '<g class="bob">', *frames, '</g></g>']


BALLOON_HALF = [2, 4, 5, 6, 6, 6, 6, 6, 5, 5, 4, 3, 2, 1]


def balloon(x, y):
    """A striped hot-air balloon, the one warm thing in the sky. It bobs; its basket hangs below."""
    cx = 6
    env = {(cx + dx, r) for r, hw in enumerate(BALLOON_HALF) for dx in range(-hw, hw + 1)}
    coral, white = set(), set()
    for px, py in env:
        u = (px - cx) / (BALLOON_HALF[py] + .5)
        (coral if abs(u) < 0.3 or abs(u) > 0.72 else white).add((px, py))
    shade = {(px, py) for px, py in env if (px + 1, py) not in env or (px, py + 1) not in env}
    glint = {(cx - 3, 2), (cx - 4, 3), (cx - 4, 4)}
    outline = dilate(env) - env
    n = len(BALLOON_HALF)
    ropes = {(cx - 1, n), (cx + 1, n), (cx - 1, n + 1), (cx + 1, n + 1)}
    basket = {(cx + dx, n + 2 + dy) for dx in (-1, 0, 1) for dy in (0, 1)}
    parts = [paint(outline | dilate(basket) - basket, P['ink']),
             paint(coral - shade - glint, P['coral']), paint(white - shade - glint, P['white']),
             paint(shade & coral, '#d94f45'), paint(shade & white, P['pale']), paint(glint, P['white']),
             paint(ropes, P['ink']), paint(basket, P['sunshade'])]
    return [f'<g transform="translate({x} {y})"><g class="float">', *parts, '</g></g>']


def twinkle(x, y, delay):
    arms = {(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)}
    return f'<g class="tw" style="animation-delay:{delay}s">{paint({(x, y)}, P["white"])}{paint(arms, P["pale"])}</g>'


def title(word, x, y, scale):
    """Each letter is its own group so it can hop; the shadow stays on the ground."""
    shadow, letters = set(), []
    cx = x
    for i, ch in enumerate(word):
        fill = text_pixels(ch, cx, y, scale=scale)
        outline = dilate(fill)
        shadow |= shift(outline, 2, 2)
        lower = {(a, b) for a, b in fill if b >= y + 4 * scale}
        letters.append(f'<g class="hop" style="animation-delay:{i * 0.14:.2f}s">'
                       f'{paint(outline - fill, P["ink"])}{paint(fill - lower, P["white"])}{paint(lower, P["pale"])}</g>')
        cx += text_width(ch, scale=scale) + scale
    return [paint(shadow, P['navy']), *letters]


def frame(w, h, n=3):
    """The 1-pixel ink border just inside the notched corners."""
    def inside(x, y):
        for cx, cy in ((x, y), (w - 1 - x, y), (x, h - 1 - y), (w - 1 - x, h - 1 - y)):
            if cy < n and cx < n - cy:
                return False
        return 0 <= x < w and 0 <= y < h
    border = {(x, y) for x in range(w) for y in range(h) if inside(x, y) and
              not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    return paint(border, P['ink'])


def banner(mobile):
    w, h = (144, 96) if mobile else (240, 72)
    bands = [(0, P['deep']), (h // 4, P['sky']), (h // 2, P['light'])]
    defs, body = sky(w, h, bands)
    css = [f'@keyframes drift{w}{{to{{transform:translateX(-{w}px)}}}}',
           f'@keyframes fly{{from{{transform:translateX(-10px)}}to{{transform:translateX({w + 4}px)}}}}',
           '.fly{animation:fly 30s infinite both}',
           '@keyframes bob{50%{transform:translateY(-1px)}}.bob{animation:bob 1.2s steps(1) infinite}',
           '@keyframes blink{50%{opacity:0}}',
           '.flap{animation:blink .5s steps(1) infinite}.flap.alt{animation-delay:-.25s}',
           '.ray{animation:blink 2s steps(1) infinite}.ray.alt{animation-delay:-1s}',
           '@keyframes tw{0%,60%,100%{opacity:0}70%,90%{opacity:1}}.tw{opacity:0;animation:tw 4s steps(1) infinite}',
           '@keyframes hop{0%,3%,100%{transform:translateY(0)}1.5%{transform:translateY(-2px)}}',
           '.hop{animation:hop 7s steps(1) infinite}',
           '@keyframes float{0%,100%{transform:translateY(0)}25%,75%{transform:translateY(-1px)}50%{transform:translateY(-2px)}}',
           '.float{animation:float 6s steps(1) infinite}']

    if mobile:
        body += sun(124, 15, 7)
        far = [(6, 12, 's'), (56, 8, 's'), (96, 30, 's')]
        mid = [(24, 22, 'm'), (98, 50, 'm')]
        near = [(-4, 62, 'l'), (74, 70, 'l')]
    else:
        body += sun(208, 17, 8)
        far = [(16, 10, 's'), (80, 13, 's'), (140, 8, 's'), (178, 34, 's')]
        mid = [(104, 27, 'm'), (162, 48, 'm'), (44, 38, 'm')]
        near = [(126, 42, 'l'), (200, 54, 'l')]
    for name, clouds, colors, secs in (('far', far, (P['pale'], P['light']), 360),
                                       ('mid', mid, (P['white'], P['pale']), 200),
                                       ('near', near, (P['white'], P['pale']), 110)):
        part, rule = layer(name, w, clouds, colors, secs)
        body += part
        css.append(rule)

    if mobile:
        body += balloon(10, 4)
        body += bird(0, 34, 2, 22, 75) + bird(0, 40, 9, 26, 75)
        body += [twinkle(14, 4, 0.5), twinkle(70, 9, 2.1), twinkle(104, 3, 3.3)]
        body += title('rize', (w - text_width('rize', scale=5)) // 2, 28, 5)
        sea_top = 78
    else:
        body += balloon(168, 24)
        body += bird(0, 20, 1, 30, 125) + bird(0, 26, 12, 36, 125)
        body += [twinkle(12, 5, 0.4), twinkle(70, 3, 1.9), twinkle(122, 10, 3.1), twinkle(186, 5, 2.6)]
        body += title('rize', 14, 10, 5)
        sea_top = 56

    back, rule1 = sea('seab', w, h, sea_top - 2, 9, 3, (P['pale'], P['pale'], P['white']), 260)
    front, rule2 = sea('seaf', w, h, sea_top + 5, 8, 11, (P['white'], P['pale'], P['white']), 150)
    css += [rule1, rule2]
    body += back + front

    clip = f'<clipPath id="c"><path d="{notched(w, h, 3)}"/></clipPath>'
    content = [f'<defs>{clip}{"".join(defs)}</defs>', '<g clip-path="url(#c)">', *body, '</g>', frame(w, h)]
    out = svg(w, h, SCALE, 'rize',
              'An 8-bit daytime sky in shades of blue: a blinking pixel sun, clouds drifting at three speeds, '
              'two birds flying past and a bank of clouds along the bottom. The name rize stands in big '
              'lowercase pixel letters that hop one after another.',
              content, ''.join(css))
    save('banner-mobile.svg' if mobile else 'banner.svg', out)


def heading(word):
    """A small pixel tag used as a section heading."""
    label = word.upper()
    tw = text_width(label)
    w, h = tw + 18, 13
    body = [f'<path fill="{P["deep"]}" d="{notched(w, h, 2)}"/>',
            text('▸', 4, 3, P['sun']), text(label, 11, 3, P['white'])]
    save(f'h-{word}.svg', svg(w, h, 4, word, f'Section heading: {word}.', body))


if __name__ == '__main__':
    banner(False)
    banner(True)
    for word in ('stats', 'activity', 'projects', 'loadout'):
        heading(word)
    print('Drew the banner and headings.')
