import json
import os
import urllib.request


TOKEN = os.environ["GITHUB_TOKEN"]
USER = os.environ["GITHUB_ACTOR"]

QUERY = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}
"""

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-readme-activity-generator",
    },
)

with urllib.request.urlopen(request) as response:
    payload = json.load(response)

calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"][-53:]
total = calendar["totalContributions"]

WIDTH, HEIGHT = 1200, 340
LEFT, TOP = 42, 139
CELL, GAP = 14, 5
STEP = CELL + GAP


def level(count):
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


colors = ["#232326", "#333142", "#484266", "#6459A8", "#8B7CFF"]
cells = []
index = 0

for x, week in enumerate(weeks):
    for day in week["contributionDays"]:
        y = day["weekday"]
        count = day["contributionCount"]
        color = colors[level(count)]
        delay = min(index * 0.004, 0.85)
        cells.append(
            '<rect class="cell" x="{}" y="{}" width="{}" height="{}" rx="2" fill="{}" '
            'style="animation-delay:{:.3f}s"><title>{}: {} contributions</title></rect>'.format(
                LEFT + x * STEP,
                TOP + y * STEP,
                CELL,
                CELL,
                color,
                delay,
                day["date"],
                count,
            )
        )
        index += 1

svg = """<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="activity-bg" x1="24" y1="10" x2="1168" y2="332" gradientUnits="userSpaceOnUse">
    <stop stop-color="#111113"/>
    <stop offset="1" stop-color="#080809"/>
  </linearGradient>
</defs>
<style>
  .cell {{ opacity: 0; animation: reveal .35s ease-out forwards; }}
  @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .cell {{ animation: none; opacity: 1; }} }}
</style>

<rect x="1" y="1" width="1198" height="338" rx="16" fill="url(#activity-bg)"/>
<rect x="1" y="1" width="1198" height="338" rx="16" stroke="#FFFFFF" stroke-opacity=".13"/>
<path d="M42 108H1158" stroke="#FFFFFF" stroke-opacity=".1"/>

<g font-family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif">
  <text x="42" y="47" fill="#8B7CFF" font-size="10" font-weight="700" letter-spacing="1.8">ACTIVITY  /  LIVE</text>
  <text x="42" y="82" fill="#FAFAFA" font-size="23" font-weight="620" letter-spacing="-.7">Work, in public.</text>

  <text x="1158" y="49" fill="#71717A" font-size="10" font-weight="700" letter-spacing="1.5" text-anchor="end">CONTRIBUTIONS / LAST YEAR</text>
  <text x="1158" y="83" fill="#FAFAFA" font-size="27" font-weight="620" text-anchor="end">{total:,}</text>

  <text x="42" y="309" fill="#71717A" font-size="10" font-weight="700" letter-spacing="1.2">QUIET</text>
  <rect x="89" y="298" width="11" height="11" rx="2" fill="{c0}"/>
  <rect x="106" y="298" width="11" height="11" rx="2" fill="{c1}"/>
  <rect x="123" y="298" width="11" height="11" rx="2" fill="{c2}"/>
  <rect x="140" y="298" width="11" height="11" rx="2" fill="{c3}"/>
  <rect x="157" y="298" width="11" height="11" rx="2" fill="{c4}"/>
  <text x="181" y="309" fill="#71717A" font-size="10" font-weight="700" letter-spacing="1.2">ACTIVE</text>
</g>

<g>{cells}</g>
</svg>""".format(
    width=WIDTH,
    height=HEIGHT,
    total=total,
    c0=colors[0],
    c1=colors[1],
    c2=colors[2],
    c3=colors[3],
    c4=colors[4],
    cells="".join(cells),
)

os.makedirs("assets", exist_ok=True)
with open("assets/activity.svg", "w", encoding="utf-8") as file:
    file.write(svg)
