#!/usr/bin/env python3
"""Draw the loadout panel (an 8-bit inventory) and the footer (a plane towing a thank-you banner).

Static art like the banner: run it after a change and commit the result. Standard library only.
"""
from banner import layer, sea, sky
from pixel import PALETTE as P, notched, paint, save, svg, text, text_width

SCALE = 5
CORAL_DARK = '#d94f45'


def sprite(rows, x, y, colors, scale=1):
    """Pixel art from strings: each character is a colour key, '.' is empty."""
    sets = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != '.':
                sets.setdefault(ch, set()).update((x + c * scale + dx, y + r * scale + dy)
                                                  for dx in range(scale) for dy in range(scale))
    return ''.join(paint(px, colors[ch]) for ch, px in sets.items())


# Rust's crab. Two frames: claws open, claws shut.
CRAB_BODY = [
    '................',
    '................',
    '................',
    '.k............k.',
    '..k..........k..',
    '..k.########.k..',
    '...##########...',
    '..###wk##wk###..',
    '.####kk##kk####.',
    '.######kk######.',
    '..############..',
    '..ssssssssssss..',
    '.s.s.s....s.s.s.',
]
CRAB_OPEN = ['#.#..........#.#', '###..........###', '.#............#.']
CRAB_SHUT = ['.#............#.', '##............##', '.#............#.']
CRAB_COLORS = {'#': P['coral'], 's': CORAL_DARK, 'k': P['ink'], 'w': P['white']}

# A gopher of our own: big eyes, buck teeth, round belly.
GOPHER = [
    '.ll........ll.',
    'lssllllllllssl',
    '.llllllllllll.',
    'lwwwllllllwwwl',
    'wwwkwllllwwwkw',
    'wwkkwllllwwkkw',
    'lwwwllkkllwwwl',
    'llllllwwllllll',
    'lllllpwwplllll',
    'llllppppppllll',
    'llllppppppllll',
    '.llllppppllll.',
    '.ssllllllllss.',
    '..ss......ss..',
]
GOPHER_SHUT = ['llllllllllllll', 'lkkkllllllkkkl', 'llllllllllllll']
GOPHER_COLORS = {'l': P['light'], 's': P['sky'], 'w': P['white'], 'k': P['ink'], 'p': P['pale']}

CARTS = [('C', P['light'], P['ink']), ('C++', P['sky'], P['ink']), ('ZIG', P['sunshade'], P['ink']),
         ('PY', P['sun'], P['ink']), ('TS', P['deep'], P['white'])]


def slot(x, y, w, h):
    return f'<path fill="{P["navy"]}" transform="translate({x} {y})" d="{notched(w, h, 2)}"/>'


def crab(x, y):
    colors = CRAB_COLORS
    return [sprite(CRAB_BODY, x, y, colors, 2),
            f'<g class="snap">{sprite(CRAB_OPEN, x, y, colors, 2)}</g>',
            f'<g class="snap alt">{sprite(CRAB_SHUT, x, y, colors, 2)}</g>']


def gopher(x, y):
    lids = {(x + c * 2 + dx, y + (r + 3) * 2 + dy) for r, row in enumerate(GOPHER_SHUT)
            for c, ch in enumerate(row) for dx in (0, 1) for dy in (0, 1) if ch == 'l'}
    lashes = {(x + c * 2 + dx, y + (r + 3) * 2 + dy) for r, row in enumerate(GOPHER_SHUT)
              for c, ch in enumerate(row) for dx in (0, 1) for dy in (0, 1) if ch == 'k'}
    return [sprite(GOPHER, x, y, GOPHER_COLORS, 2),
            f'<g class="blink">{paint(lids, P["light"])}{paint(lashes, P["ink"])}</g>']


def cartridge(x, y, label, color, ink, delay):
    w, h = 22, 22
    body = [f'<g class="cart" style="animation-delay:{delay}s">',
            f'<path fill="{P["deep"]}" transform="translate({x} {y})" d="{notched(w, h - 3, 1)}"/>',
            f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="{h - 5}" fill="{P["navy"]}"/>',
            paint({(x + 3 + i * 2, y + 2) for i in range(9)}, P['deep']),
            f'<rect x="{x + 1}" y="{y + 4}" width="{w - 2}" height="11" fill="{color}"/>',
            text(label, x + (w - text_width(label)) // 2, y + 6, ink),
            paint({(x + 3 + i * 2, y + h - 3 + d) for i in range(9) for d in (0, 1)}, P['sun']),
            '</g>']
    return body


def monitor(x, y, w=96, h=50):
    """Niri's scrolling columns, Vesper's island on top, a terminal with a blinking cursor."""
    out = [f'<path fill="{P["deep"]}" transform="translate({x} {y})" d="{notched(w, h, 2)}"/>',
           f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{h - 4}" fill="{P["navy"]}"/>']
    sx, sy, sw = x + 2, y + 2, w - 4
    out.append(f'<rect x="{sx + sw // 2 - 8}" y="{sy}" width="16" height="3" fill="{P["ink"]}"/>')
    out.append(paint({(sx + sw // 2 + 4, sy + 1)}, P['sun']))
    # column 1: the focused terminal
    tx, ty, tw, th = sx + 2, sy + 5, sw * 9 // 20, h - 11
    out += [f'<rect x="{tx - 1}" y="{ty - 1}" width="{tw + 2}" height="{th + 2}" fill="{P["light"]}"/>',
            f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{P["ink"]}"/>']
    lines = [(P['sun'], 2, P['light'], 16), (P['sky'], 26, None, 0), (P['sky'], 18, None, 0), (P['sky'], 30, None, 0),
             (P['sun'], 2, P['light'], 11), (P['pale'], 24, None, 0), (P['pale'], 14, None, 0), (P['sun'], 2, None, 0)]
    for i, (c1, l1, c2, l2) in enumerate(lines):
        ly = ty + 2 + i * 4
        out.append(f'<rect x="{tx + 2}" y="{ly}" width="{l1}" height="2" fill="{c1}"/>')
        if c2:
            out.append(f'<rect x="{tx + 5}" y="{ly}" width="{l2}" height="2" fill="{c2}"/>')
    out.append(f'<rect class="cur" x="{tx + 5}" y="{ty + 2 + (len(lines) - 1) * 4}" width="2" height="2" fill="{P["white"]}"/>')
    # column 2: a page; column 3 runs off the edge, as niri's do
    px_, pw = tx + tw + 3, sw * 3 // 10
    out += [f'<rect x="{px_}" y="{ty}" width="{pw}" height="{th}" fill="{P["pale"]}"/>',
            f'<rect x="{px_ + 2}" y="{ty + 2}" width="{pw - 4}" height="5" fill="{P["sky"]}"/>',
            *[f'<rect x="{px_ + 2}" y="{ty + 9 + i * 4}" width="{pw - 4 - (i % 2) * 5}" height="2" fill="{P["light"]}"/>'
              for i in range((th - 11) // 4)]]
    cx = px_ + pw + 2
    out += [f'<rect x="{cx}" y="{ty}" width="{sx + sw - cx}" height="{th}" fill="{P["deep"]}"/>',
            f'<rect x="{cx + 2}" y="{ty + 3}" width="{sx + sw - cx - 2}" height="2" fill="{P["sky"]}"/>']
    out += [f'<rect x="{x + w // 2 - 4}" y="{y + h}" width="8" height="4" fill="{P["deep"]}"/>',
            f'<rect x="{x + w // 2 - 12}" y="{y + h + 4}" width="24" height="2" fill="{P["deep"]}"/>']
    return out


def loadout(mobile):
    css = ('@keyframes blink{50%{opacity:0}}.snap{animation:blink 1.6s steps(1) infinite}.snap.alt{animation-delay:-.8s}'
           '@keyframes lid{0%,92%,100%{opacity:0}94%,98%{opacity:1}}.blink{opacity:0;animation:lid 4s steps(1) infinite}'
           '.cur{animation:blink 1s steps(1) infinite}'
           '@keyframes pick{0%,8%,100%{transform:translateY(0)}2%,6%{transform:translateY(-2px)}}'
           '.cart{animation:pick 6s steps(1) infinite}')
    if mobile:
        w, h = 144, 218
        main_y, also_y = 8, 72
        slots, slot_w = [(12, 'RUST'), (76, 'GO')], 56
        carts_x, cart_gap = 12, 24
        rig_label, rig, notes_x, notes_y = (12, 112), (22, 120, 100, 52), None, 186
    else:
        w, h = 240, 112
        main_y, also_y = 8, 70
        slots, slot_w = [(12, 'RUST'), (66, 'GO')], 50
        carts_x, cart_gap = 12, 23
        rig_label, rig, notes_x, notes_y = (134, 8), (134, 16, 94, 50), 134, 78
    body = [f'<path fill="{P["deep"]}" d="{notched(w, h, 3)}"/>',
            f'<path fill="{P["ink"]}" transform="translate(1 1)" d="{notched(w - 2, h - 2, 2)}"/>']

    body.append(text('MAIN', 12, main_y, P['light'], font='small'))
    for i, (sx, name) in enumerate(slots):
        sy = main_y + 8
        body.append(slot(sx, sy, slot_w, 36))
        if name == 'RUST':
            body += crab(sx + (slot_w - 32) // 2, sy + 4)
        else:
            body += gopher(sx + (slot_w - 28) // 2, sy + 4)
        body.append(text(name, sx + (slot_w - text_width(name)) // 2, sy + 40, P['white']))

    body.append(text('ALSO', 12, also_y, P['light'], font='small'))
    for i, (label, color, ink) in enumerate(CARTS):
        body += cartridge(carts_x + i * cart_gap, also_y + 8, label, color, ink, i * 1.2)

    body.append(text('RIG', *rig_label, P['light'], font='small'))
    body += monitor(*rig)
    notes = ['CACHYOS · NIRI', 'VESPER, MY OWN SHELL', 'FOOT · FISH · YAZI', 'NEOVIM · ZED']
    for i, line in enumerate(notes):
        lx = (w - text_width(line, 'small')) // 2 if notes_x is None else notes_x
        body.append(text(line, lx, notes_y + i * 8, P['pale'] if i % 2 == 0 else P['sky'], font='small'))

    save('loadout-mobile.svg' if mobile else 'loadout.svg',
         svg(w, h, SCALE, 'loadout',
             'An 8-bit inventory. Main: Rust, shown as a coral crab snapping its claws, and Go, shown as a blue '
             'gopher that blinks. Also: game cartridges labelled C, C++, Zig, Python and TypeScript. Rig: a pixel '
             'monitor with niri scrolling columns and a terminal; CachyOS, niri, Vesper (my own shell), foot, '
             'fish, yazi, neovim and zed.', body, css))


PLANE = [
    '..............kkk.',
    '.....kkk.....kwck.',
    '...kkpppkkkkkkwck.',
    '..kwwwwwwwwwwwwwk.',
    '.kwwccccccccwwwk..',
    '.kwwwwwwwwwwwwk...',
    '..kkkkkkkkkkkk....',
    '.....k....k.......',
    '....kkk..kkk......',
]
PLANE_COLORS = {'k': P['ink'], 'w': P['white'], 'c': P['coral'], 'p': P['light']}


def footer(mobile):
    w, h = (144, 44) if mobile else (240, 40)
    defs, body = sky(w, h, [(0, P['sky']), (h // 2, P['light'])])
    css = [f'@keyframes drift{w}{{to{{transform:translateX(-{w}px)}}}}']
    part, rule = layer('fl', w, [(20, 14, 's'), (110, 18, 's'), (180, 12, 's')] if not mobile else
                       [(10, 14, 's'), (90, 18, 's')], (P['pale'], P['light']), 300)
    body += part
    css.append(rule)

    msg = 'THANKS FOR VISITING ♥' if not mobile else 'THANKS FOR VISITING'
    bw = text_width(msg) + 8
    plane_w = len(PLANE[0])
    rope = 6
    tow_w = plane_w + rope + bw
    tow = [sprite(PLANE, 0, 0, PLANE_COLORS),
           f'<rect x="{plane_w}" y="4" width="{rope}" height="1" fill="{P["ink"]}"/>',
           f'<rect x="{plane_w + rope}" y="0" width="{bw}" height="11" fill="{P["ink"]}"/>',
           f'<rect x="{plane_w + rope + 1}" y="1" width="{bw - 2}" height="9" fill="{P["white"]}"/>',
           text(msg, plane_w + rope + 4, 2, P['ink'])]
    prop = f'<rect class="prop" x="0" y="2" width="1" height="5" fill="{P["ink"]}"/>'
    travel = w + tow_w + 8
    body.append(f'<g class="tow"><g class="bob">{"".join(tow)}{prop}</g></g>')
    css += [f'@keyframes tow{{from{{transform:translate({w + 4}px,8px)}}to{{transform:translate({-tow_w - 4}px,8px)}}}}',
            f'.tow{{transform:translate({w + 4}px,8px);animation:tow {travel // 10}s steps({travel}) infinite}}',
            '@keyframes bob{50%{transform:translateY(1px)}}.bob{animation:bob 1.4s steps(1) infinite}',
            '@keyframes blink{50%{opacity:0}}.prop{animation:blink .2s steps(1) infinite}']

    back, r1 = sea('fsb', w, h, h - 14, 8, 5, (P['pale'], P['pale'], P['white']), 260)
    front, r2 = sea('fsf', w, h, h - 8, 6, 9, (P['white'], P['pale'], P['white']), 150)
    body += back + front
    css += [r1, r2]
    clip = f'<clipPath id="c"><path d="{notched(w, h, 3)}"/></clipPath>'
    out = svg(w, h, SCALE, 'thanks for visiting',
              'A little coral plane flies across an 8-bit sky over a bank of clouds, towing a banner that says '
              'thanks for visiting.', [f'<defs>{clip}{"".join(defs)}</defs>', '<g clip-path="url(#c)">', *body, '</g>'],
              ''.join(css))
    save('footer-mobile.svg' if mobile else 'footer.svg', out)


if __name__ == '__main__':
    for mobile in (False, True):
        loadout(mobile)
        footer(mobile)
    print('Drew the loadout and the footer.')
