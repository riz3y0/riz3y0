#!/usr/bin/env python3
"""Render profile panels from public GitHub data. Only the standard library is needed."""
import datetime as dt
import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PALETTE = json.loads((ROOT/'assets/palette.json').read_text())
QUERY = '''query($login:String!, $cursor:String) {
 user(login:$login) {
  login followers { totalCount }
  repositories(first:100,after:$cursor,privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false) {
   totalCount nodes { name stargazerCount }
   pageInfo { hasNextPage endCursor }
  }
  contributionsCollection {
   contributionCalendar {
    totalContributions weeks { contributionDays { date contributionCount } }
   }
  }
 }
}'''


def fetch():
    cursor, stars = None, 0
    while True:
        payload = {'query':QUERY,'variables':{'login':'riz3y0','cursor':cursor}}
        result = subprocess.run(['gh','api','graphql','--input','-'],input=json.dumps(payload),capture_output=True,text=True,check=True)
        response = json.loads(result.stdout)
        if response.get('errors'):
            raise RuntimeError('GitHub did not return complete profile data')
        user = response['data']['user']
        repos = user['repositories']
        stars += sum(repo['stargazerCount'] for repo in repos['nodes'])
        if not repos['pageInfo']['hasNextPage']:
            break
        cursor = repos['pageInfo']['endCursor']
    return user, stars


def text(x,y,content,size=24,fill=None,weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{fill or PALETTE["text"]}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(content))}</text>'


def base(width,height,title,description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description)}</desc>',
            f'<path fill="{PALETTE["background"]}" d="M0 0H{width}V{height}H0Z"/>',
            '<g font-family="Inter,Segoe UI,Arial,sans-serif">']


def save(name,parts):
    (ROOT/'assets'/name).write_text('\n'.join(parts+['</g></svg>'])+'\n')


def status(user,stars,mobile=False):
    metrics = [('repositories',user['repositories']['totalCount']),('stars',stars),('followers',user['followers']['totalCount']),('contributions',user['contributionsCollection']['contributionCalendar']['totalContributions'])]
    width,height = (720,364) if mobile else (1200,204)
    svg = base(width,height,'GitHub overview',', '.join(f'{n} {k}' for k,n in metrics)+'. Contributions cover the past year; repositories exclude forks.')
    for i,(label,number) in enumerate(metrics):
        x = 38 + (i%2)*350 if mobile else 42+i*296
        y = 72 + (i//2)*140 if mobile else 87
        svg.extend([text(x,y,f'{number:,}',54,PALETTE['accent'],600),text(x,y+39,label,27,PALETTE['muted'])])
        if (i%2 if mobile else i)<(1 if mobile else 3):
            end_y = y+39
            svg.append(f'<path d="M{x+(307 if mobile else 254)} {y-40}V{end_y}" stroke="{PALETTE["outline"]}"/>')
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%d %b %Y').lower()
    svg.append(text(38 if mobile else 42,height-27,'updated '+stamp+' · public activity',23 if mobile else 20,PALETTE['muted']))
    save('github-status'+('-mobile' if mobile else '')+'.svg',svg)


def blend(a,b,ratio):
    rgb=lambda c:tuple(bytes.fromhex(c[1:]))
    return '#'+''.join(f'{round(x+(y-x)*ratio):02x}' for x,y in zip(rgb(a),rgb(b)))


def activity(user,mobile=False):
    calendar = user['contributionsCollection']['contributionCalendar']
    weeks = calendar['weeks'][-26:] if mobile else calendar['weeks']
    width,height = (720,342) if mobile else (1200,302)
    left,top,step,cell = (63,76,24,19) if mobile else (69,70,20,15)
    counts = [d['contributionCount'] for w in weeks for d in w['contributionDays']]
    highest = max(counts or [1]) or 1
    shades = [PALETTE['surface']] + [blend(PALETTE['outline'],PALETTE['accent'],r) for r in (.2,.45,.7,1)]
    label = 'past six months' if mobile else 'past year'
    svg = base(width,height,'GitHub activity',f'Contribution calendar for the {label}, from GitHub. {sum(counts)} contributions shown.')
    previous_month = None
    for column,week in enumerate(weeks):
        for day in week['contributionDays']:
            date = dt.date.fromisoformat(day['date'])
            row = (date.weekday()+1)%7
            amount = day['contributionCount']
            level = min(4,max(1,round(amount/highest*3)+1)) if amount else 0
            x,y = left+column*step,top+row*step
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{shades[level]}"><title>{date}: {amount} contributions</title></rect>')
            if date.day<=7 and date.month != previous_month and column<len(weeks)-2:
                svg.append(text(x,top-23,date.strftime('%b').lower(),24 if mobile else 21,PALETTE['muted']))
                previous_month = date.month
    for row,label_day in [(1,'M'),(3,'W'),(5,'F')]:
        svg.append(text(24,top+row*step+cell-1,label_day,20 if mobile else 18,PALETTE['muted']))
    bottom = height-31
    svg.append(text(left,bottom,label,23 if mobile else 20,PALETTE['muted']))
    legend_x = width-224
    svg.append(text(legend_x-16,bottom,'less',21 if mobile else 19,PALETTE['muted'],anchor='end'))
    for index,color in enumerate(shades):
        svg.append(f'<rect x="{legend_x+index*23}" y="{bottom-17}" width="17" height="17" fill="{color}"/>')
    svg.append(text(legend_x+125,bottom,'more',21 if mobile else 19,PALETTE['muted']))
    save('github-activity'+('-mobile' if mobile else '')+'.svg',svg)


def main():
    user, stars = fetch()
    for mobile in (False,True):
        status(user,stars,mobile)
        activity(user,mobile)
    print('Updated public GitHub status and contribution panels.')


if __name__ == '__main__':
    main()
