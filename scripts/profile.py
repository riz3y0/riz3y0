#!/usr/bin/env python3
"""Render the live profile panels (stats HUD and contribution calendar) from public GitHub data.

Runs in GitHub Actions every day; only the standard library and the `gh` CLI are needed.
"""
import datetime as dt
import json
import subprocess

from pixel import PALETTE as P, notched, paint, save, svg, text, text_width

LOGIN = 'riz3y0'
SCALE = 5
QUERY = '''query($login:String!, $cursor:String) {
 user(login:$login) {
  followers { totalCount }
  repositories(first:100,after:$cursor,privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false) {
   totalCount nodes { stargazerCount }
   pageInfo { hasNextPage endCursor }
  }
  contributionsCollection {
   contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
  }
 }
}'''
SHADES = [P['navy'], P['deep'], P['sky'], P['light'], P['white']]


def fetch():
    cursor, stars = None, 0
    while True:
        payload = {'query': QUERY, 'variables': {'login': LOGIN, 'cursor': cursor}}
        result = subprocess.run(['gh', 'api', 'graphql', '--input', '-'], input=json.dumps(payload),
                                capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        if response.get('errors'):
            raise RuntimeError(f'GitHub returned errors: {response["errors"]}')
        user = response['data']['user']
        repos = user['repositories']
        stars += sum(r['stargazerCount'] for r in repos['nodes'])
        if not repos['pageInfo']['hasNextPage']:
            return user, stars
        cursor = repos['pageInfo']['endCursor']


def panel(w, h):
    return [f'<path fill="{P["deep"]}" d="{notched(w, h, 3)}"/>',
            f'<path fill="{P["ink"]}" transform="translate(1 1)" d="{notched(w - 2, h - 2, 2)}"/>']


def score(n, x, y):
    """Arcade-style number: padded to 4 digits, the padding zeros dimmed."""
    digits = f'{n:04d}'
    lead = len(digits) - len(str(n)) if n else 3
    return [text(digits[:lead], x, y, P['navy'], scale=2), text(digits[lead:], x + lead * 12, y, P['white'], scale=2)]


def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime('UPDATED %d %b %Y').upper()


def stats(user, stars, mobile):
    total = user['contributionsCollection']['contributionCalendar']['totalContributions']
    metrics = [('REPOS', user['repositories']['totalCount']), ('STARS', stars),
               ('FOLLOWERS', user['followers']['totalCount']), ('CONTRIBS', total)]
    w, h = (144, 80) if mobile else (240, 48)
    body = panel(w, h)
    widths = [max(text_width(label), 46) for label, _ in metrics]
    gap = (w - 24 - sum(widths)) / 3
    for i, (label, n) in enumerate(metrics):
        if mobile:
            x, y = 12 + (i % 2) * 70, 9 + (i // 2) * 30
        else:
            x, y = round(12 + sum(widths[:i]) + gap * i), 9
        if (not mobile and i) or (mobile and i % 2):
            dots = {(x - (6 if mobile else round(gap / 2) + 1), yy) for yy in range(y, y + 24, 2)}
            body.append(paint(dots, P['navy']))
        body.append(text(label, x, y, P['light']))
        body += score(n, x, y + 11)
    foot = stamp() if mobile else stamp() + ' · PUBLIC REPOS · PAST YEAR'
    body.append(text(foot, 12, h - 10, P['sky'], font='small'))
    desc = ', '.join(f'{n} {label.lower()}' for label, n in metrics)
    save('stats-mobile.svg' if mobile else 'stats.svg',
         svg(w, h, SCALE, 'GitHub stats', f'{desc}. Contributions cover the past year; repositories exclude forks.', body))


def activity(user, mobile):
    calendar = user['contributionsCollection']['contributionCalendar']
    weeks = calendar['weeks'][-25:] if mobile else calendar['weeks']
    w, h = (144, 66) if mobile else (240, 58)
    left, top, step, cell = (13, 13, 5, 4) if mobile else (14, 13, 4, 3)
    days = [d for wk in weeks for d in wk['contributionDays']]
    highest = max([d['contributionCount'] for d in days] + [1])
    body = panel(w, h)
    css = ['@keyframes in{from{opacity:0}}', '@keyframes now{50%{fill:' + P['sun'] + '}}',
           f'.c{{animation:in .05s steps(1) both}}.now{{animation:now 1s steps(1) infinite}}']
    last_label = -99
    today = days[-1]['date'] if days else None
    for col, week in enumerate(weeks):
        cells = {}
        for day in week['contributionDays']:
            date = dt.date.fromisoformat(day['date'])
            row = (date.weekday() + 1) % 7
            n = day['contributionCount']
            level = min(4, 1 + n * 4 // (highest + 1)) if n else 0
            x, y = left + col * step, top + row * step
            if day['date'] == today:
                body.append(f'<rect class="now" x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{SHADES[level]}"/>')
                continue
            cells.setdefault(level, set()).update((x + a, y + b) for a in range(cell) for b in range(cell))
            if date.day <= 7 and row == 0 and col * step - last_label >= 14 and col < len(weeks) - 2:
                body.append(text(date.strftime('%b').upper(), x, top - 8, P['light'], font='small'))
                last_label = col * step
        body.append(f'<g class="c" style="animation-delay:{col * 0.03:.2f}s">' +
                    ''.join(paint(px, SHADES[lv]) for lv, px in sorted(cells.items())) + '</g>')
    for row, label in ((1, 'M'), (3, 'W'), (5, 'F')):
        body.append(text(label, 5, top + row * step - (1 if mobile else 1), P['light'], font='small'))
    shown = sum(d['contributionCount'] for d in days)
    foot_y = h - 10
    span = 'PAST 6 MONTHS' if mobile else 'PAST YEAR'
    body.append(text(f'{shown} CONTRIBUTIONS · {span}', left, foot_y, P['sky'], font='small'))
    if not mobile:
        lx = w - 12 - 5 * 4 - 3 - text_width('MORE', 'small')
        body.append(text('LESS', lx - 3 - text_width('LESS', 'small'), foot_y, P['sky'], font='small'))
        for i, color in enumerate(SHADES):
            body.append(f'<rect x="{lx + i * 4}" y="{foot_y + 1}" width="3" height="3" fill="{color}"/>')
        body.append(text('MORE', lx + 5 * 4 + 3, foot_y, P['sky'], font='small'))
    save('activity-mobile.svg' if mobile else 'activity.svg',
         svg(w, h, SCALE, 'GitHub activity',
             f'Contribution calendar for the {span.lower()}: {shown} contributions. Brighter squares mean busier days; '
             'today blinks.', body, ''.join(css)))


def main():
    user, stars = fetch()
    for mobile in (False, True):
        stats(user, stars, mobile)
        activity(user, mobile)
    print('Updated the stats and activity panels.')


if __name__ == '__main__':
    main()
