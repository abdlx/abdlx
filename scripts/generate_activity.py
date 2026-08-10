import json
import os
import urllib.request

TOKEN = os.environ["GITHUB_TOKEN"]
USER = os.environ["GITHUB_ACTOR"]

query = """
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

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-readme-activity-generator",
    },
)

with urllib.request.urlopen(req) as response:
    payload = json.load(response)

calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"][-53:]
total = calendar["totalContributions"]

W, H = 1200, 360
LEFT, TOP = 46, 132
CELL, GAP = 15, 5
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

colors = ["#232428", "#183C5A", "#1C5F8E", "#2484C6", "#64B5FF"]
cells = []
idx = 0

for x, week in enumerate(weeks):
    for day in week["contributionDays"]:
        y = day["weekday"]
        count = day["contributionCount"]
        lv = level(count)
        delay = (idx % 53) * 0.035
        cells.append(
            '<rect class="cell" x="{}" y="{}" width="{}" height="{}" rx="4" fill="{}" '
            'style="animation-delay:{:.2f}s"><title>{}: {} contributions</title></rect>'.format(
                LEFT + x * STEP, TOP + y * STEP, CELL, CELL, colors[lv], delay, day["date"], count
            )
        )
        idx += 1

svg = """<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#151619"/>
    <stop offset="1" stop-color="#0B0C0E"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
    <stop stop-color="#64B5FF" stop-opacity="0"/>
    <stop offset=".5" stop-color="#64B5FF" stop-opacity=".24"/>
    <stop offset="1" stop-color="#64B5FF" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="panel"><rect x="1" y="1" width="1198" height="358" rx="34"/></clipPath>
</defs>

<style>
.cell {{
  transform-box: fill-box;
  transform-origin: center;
  animation: breathe 3.2s ease-in-out infinite;
}}
@keyframes breathe {{
  0%, 100% {{ opacity: .78; transform: scale(.96); }}
  50% {{ opacity: 1; transform: scale(1); }}
}}
.scan {{
  animation: sweep 6s ease-in-out infinite;
}}
@keyframes sweep {{
  0% {{ transform: translateX(-260px); opacity:0; }}
  12% {{ opacity:1; }}
  55% {{ opacity:1; }}
  72%,100% {{ transform: translateX(1240px); opacity:0; }}
}}
</style>

<rect x="1" y="1" width="1198" height="358" rx="34" fill="url(#bg)"/>
<rect x="1" y="1" width="1198" height="358" rx="34" stroke="#FFFFFF" stroke-opacity=".10"/>

<g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif">
  <text x="46" y="60" fill="white" font-size="26" font-weight="700" letter-spacing="-0.6">Activity</text>
  <text x="46" y="89" fill="#85868B" font-size="15">A live view of the work.</text>

  <g transform="translate(944 42)">
    <rect width="210" height="48" rx="24" fill="#FFFFFF" fill-opacity=".05"/>
    <text x="18" y="21" fill="#73747A" font-size="11" font-weight="700" letter-spacing="1.1">CONTRIBUTIONS</text>
    <text x="18" y="39" fill="#E8E8EA" font-size="17" font-weight="700">{total:,}</text>
  </g>

  <text x="46" y="311" fill="#73747A" font-size="12">Less</text>
  <rect x="84" y="299" width="13" height="13" rx="4" fill="{c0}"/>
  <rect x="103" y="299" width="13" height="13" rx="4" fill="{c1}"/>
  <rect x="122" y="299" width="13" height="13" rx="4" fill="{c2}"/>
  <rect x="141" y="299" width="13" height="13" rx="4" fill="{c3}"/>
  <rect x="160" y="299" width="13" height="13" rx="4" fill="{c4}"/>
  <text x="181" y="311" fill="#73747A" font-size="12">More</text>
</g>

<g>{cells}</g>
<g clip-path="url(#panel)">
  <rect class="scan" x="-260" y="118" width="180" height="166" rx="32" fill="url(#scan)"/>
</g>
</svg>""".format(
    W=W, H=H, total=total,
    c0=colors[0], c1=colors[1], c2=colors[2], c3=colors[3], c4=colors[4],
    cells="".join(cells)
)

os.makedirs("assets", exist_ok=True)
with open("assets/activity.svg", "w", encoding="utf-8") as f:
    f.write(svg)
