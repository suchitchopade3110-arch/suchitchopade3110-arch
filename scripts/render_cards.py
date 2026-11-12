#!/usr/bin/env python3
"""Render the animated SVG cards for the profile README.

Reads   data/profile.json        (all the words: name, jobs, kit, links)
        data/contributions.json  (written by scripts/fetch_contributions.py)
Writes  cards/<name>-light.svg and cards/<name>-dark.svg, plus README.md

    python scripts/render_cards.py            # animated cards
    STATIC=1 python scripts/render_cards.py   # end state, for screenshots

Standard library only. Each SVG carries its own fonts (base64) and CSS,
because GitHub shows README images sandboxed: no scripts, no outside requests.
"""
import base64
import datetime as dt
import json
import os
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
CARDS = ROOT / ("preview" if STATIC else "cards")  # static renders never overwrite the real cards

P = json.loads((ROOT / "data" / "profile.json").read_text())
C = json.loads((ROOT / "data" / "contributions.json").read_text())
_portrait = ROOT / "data" / "portrait.json"  # optional, made by scripts/make_portrait.py
PORTRAIT = json.loads(_portrait.read_text()) if _portrait.exists() else None

THEMES = {
    "light": dict(paper="#F4F0E6", panel="#ECE7DA", ink="#15140F", mute="#6E685B",
                  rule="#D5CEBD", red="#C8321E", gold="#A8842A", cell="#E2DCCD"),
    "dark": dict(paper="#0F0F0D", panel="#171714", ink="#EEE9DD", mute="#8F897B",
                 rule="#2C2B25", red="#F2553A", gold="#D9B65A", cell="#1E1D19"),
}

FONTS = {
    "display": ("Display", "400", "normal"),
    "mono-400": ("Mono", "400", "normal"),
    "mono-500": ("Mono", "500", "normal"),
    "serif-italic": ("Serif", "400", "italic"),
}
_font_cache = {}


def font_face(key):
    if key not in _font_cache:
        fam, weight, style = FONTS[key]
        b64 = base64.b64encode((ROOT / "fonts" / f"{key}.woff2").read_bytes()).decode()
        _font_cache[key] = (
            f"@font-face{{font-family:'{fam}';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return _font_cache[key]


BASE_CSS = """
.d{font-family:'Display',Impact,'Arial Narrow',sans-serif}
.m{font-family:'Mono',ui-monospace,Menlo,Consolas,monospace;font-weight:400}
.mb{font-family:'Mono',ui-monospace,Menlo,Consolas,monospace;font-weight:500}
.s{font-family:'Serif',Georgia,serif;font-style:italic}
.ink{fill:var(--ink)}.mute{fill:var(--mute)}.red{fill:var(--red)}.gold{fill:var(--gold)}
.ls{letter-spacing:.14em}
.fb{transform-box:fill-box}
@keyframes rise{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes growy{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.18)}100%{opacity:1;transform:scale(1)}}
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:.15}}
@keyframes tick{0%,100%{opacity:1}}
@keyframes sweep{0%,72%{transform:translateX(-140%) skewX(-18deg)}100%{transform:translateX(260%) skewX(-18deg)}}
.rise{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}
.fade{animation:fade .6s ease both}
.growx{animation:growx .9s cubic-bezier(.2,.8,.2,1) both;transform-origin:left center;transform-box:fill-box}
.growy{animation:growy .8s cubic-bezier(.2,.8,.2,1) both;transform-origin:center bottom;transform-box:fill-box}
.pop{animation:pop .45s cubic-bezier(.2,.8,.2,1) both;transform-origin:center;transform-box:fill-box}
.blink{animation:blink 1.6s steps(1) infinite}
.frame{opacity:0;animation:tick .055s linear}  /* no fill: each frame drops back to hidden when its slot ends */
.shine{transform:translateX(-140%) skewX(-18deg)}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
if STATIC:
    BASE_CSS += "*{animation:none!important}\n"


def svg(w, h, t, body, fonts, css="", label=""):
    """Wrap a card body: background, theme variables, fonts, shared CSS."""
    th = THEMES[t]
    variables = ";".join(f"--{k}:{v}" for k, v in th.items())
    faces = "".join(font_face(f) for f in fonts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>"
        f"<style>{faces}svg{{{variables}}}{BASE_CSS}{css}</style>"
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="{th["paper"]}" stroke="{th["rule"]}" stroke-width="2"/>'
        f"{body}</svg>"
    )


def d(seconds):
    return f'style="animation-delay:{seconds:.2f}s"'


def arrow(x, y, size=12, cls="mute", diag=False):
    """Small arrow drawn as a path, so no font needs to carry the glyph."""
    s = size
    if diag:
        p = f"M{x} {y + s}L{x + s} {y}M{x + s * .3} {y}H{x + s}V{y + s * .7}"
    else:
        p = f"M{x} {y}H{x + s}M{x + s * .55} {y - s * .4}L{x + s} {y}L{x + s * .55} {y + s * .4}"
    stroke = {"mute": "var(--mute)", "ink": "var(--ink)", "red": "var(--red)"}[cls]
    return f'<path d="{p}" fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'


def header(left, right_text, w, delay=0.0, live=False):
    """Top strip shared by the wide cards: file label, status, drawn rule."""
    dot = f'<circle class="red {"blink" if live else ""}" cx="{w - 60}" cy="43" r="5"/>' if live else ""
    rx = w - 76 if live else w - 56
    return (
        f'<text class="mb mute ls fade" {d(delay)} x="56" y="48" font-size="15">{escape(left)}</text>'
        f'<g class="fade" {d(delay + .1)}><text class="mb ink ls" x="{rx}" y="48" font-size="15" text-anchor="end">{escape(right_text)}</text>{dot}</g>'
        f'<rect class="growx" {d(delay + .15)} x="56" y="66" width="{w - 112}" height="2" fill="var(--ink)"/>'
    )


# ───────────────────────────── hero ─────────────────────────────

CLAIMS = [
    ("01", "source matches the retrieved passage", True, "0.97"),
    ("02", "figure agrees with the dataset", True, "0.93"),
    ("03", "date stated with no evidence", False, "0.31"),
    ("04", "conclusion follows from 01 and 02", True, "0.88"),
]


def portrait_panel(t, css):
    """Right side of the hero: the photo redrawn as a dot grid, revealed row by row, then stamped."""
    px, py, pw, ph = 640, 104, 504, 372
    cols, rows = PORTRAIT["cols"], PORTRAIT["rows"]
    c = min((pw - 24) / (cols + .5), (ph - 12) / rows)
    ox, oy = px + (pw - c * (cols + .5)) / 2, py + ph - c * rows  # sit on the bottom edge
    by_row = {}
    for i, j, l in PORTRAIT["cells"]:
        v = (1 - l / 100) ** .9 if t == "light" else (l / 100) ** .8  # ink follows shadow on paper, light on black
        x = ox + (i + (1 if j % 2 else .5)) * c
        by_row.setdefault(j, []).append(f'<circle cx="{x:.1f}" cy="{oy + (j + .5) * c:.1f}" r="{c * (.08 + .46 * v):.2f}"/>')
    css += [
        f"@keyframes scan{{0%{{transform:translateY(0);opacity:0}}6%{{opacity:.85}}60%{{opacity:.85}}"
        f"66%,100%{{transform:translateY({ph - 16}px);opacity:0}}}}",
        ".scan{opacity:0;animation:scan 7s linear 1.2s infinite}",
        "@keyframes slam{0%{opacity:0;transform:rotate(-9deg) scale(2.6)}60%{opacity:1;transform:rotate(-9deg) scale(.94)}"
        "100%{opacity:1;transform:rotate(-9deg) scale(1)}}",
        ".st{transform:rotate(-9deg);transform-origin:center;transform-box:fill-box;animation:slam .5s cubic-bezier(.3,1.4,.5,1) 2.4s both}",
    ]
    out = [
        f'<clipPath id="pp"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10"/></clipPath>',
        f'<rect class="fade" {d(.5)} x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="var(--panel)" stroke="var(--rule)" stroke-width="1.5"/>',
        '<g clip-path="url(#pp)" fill="var(--ink)">',
    ]
    for j in sorted(by_row):
        out.append(f'<g class="fade" style="animation-duration:.35s;animation-delay:{.8 + j * .022:.2f}s">{"".join(by_row[j])}</g>')
    out.append(f'<rect class="scan" x="{px}" y="{py + 8}" width="{pw}" height="2" fill="var(--red)"/></g>')
    out.append(
        f'<g class="fade" {d(.7)}><text class="mb mute ls" x="{px + 22}" y="{py + 34}" font-size="13">SUBJECT</text>'
        f'<text class="mb mute ls" x="{px + pw - 22}" y="{py + 34}" font-size="13" text-anchor="end">FILE {P["file_no"]}</text></g>'
        f'<g class="st"><rect x="{px + pw - 186}" y="{py + ph - 70}" width="166" height="50" rx="6" fill="var(--panel)" stroke="var(--red)" stroke-width="3"/>'
        f'<text class="d red" x="{px + pw - 103}" y="{py + ph - 33}" font-size="33" text-anchor="middle" letter-spacing=".06em">VERIFIED</text></g>'
    )
    return out


def hero(t):
    w, h = 1200, 540
    loop = 11.0  # seconds for the verification panel cycle

    def lk(name, start, kind="fade"):
        """Keyframes for one element in the looping panel: appear at `start` seconds, clear before the loop ends."""
        a = start / loop * 100
        b = a + (2.2 if kind == "fade" else 3.0)
        if kind == "stamp":
            return (f"@keyframes {name}{{0%,{a:.1f}%{{opacity:0;transform:rotate(-9deg) scale(2.6)}}"
                    f"{b:.1f}%{{opacity:1;transform:rotate(-9deg) scale(.94)}}"
                    f"{b + 1.2:.1f}%,93%{{opacity:1;transform:rotate(-9deg) scale(1)}}"
                    f"97%,100%{{opacity:0;transform:rotate(-9deg) scale(1)}}}}")
        if kind == "wipe":
            return (f"@keyframes {name}{{0%,{a:.1f}%{{transform:scaleX(0)}}{b + 3:.1f}%,93%{{transform:scaleX(1)}}"
                    f"97%,100%{{transform:scaleX(1);opacity:0}}}}")
        return f"@keyframes {name}{{0%,{a:.1f}%{{opacity:0}}{b:.1f}%,93%{{opacity:1}}97%,100%{{opacity:0}}}}"

    css = [
        "@keyframes scan{0%,8%{transform:translateY(0);opacity:0}12%{opacity:.9}52%{opacity:.9}"
        "56%,100%{transform:translateY(212px);opacity:0}}",
        f".scan{{animation:scan {loop}s linear infinite}}",
        "@keyframes run{0%{transform:translateX(0)}100%{transform:translateX(1088px)}}",
        ".run{animation:run 5.5s cubic-bezier(.6,0,.4,1) infinite}",
        ".shine{animation:sweep 6s ease-in-out 2s infinite;transform-box:fill-box}",
    ]

    # left column: the name
    left = [
        header(f"CASE FILE NO. {P['file_no']}  //  {P['role']}  ·  {P['location']}", P["status"], w, 0, live=True),
        f'<text class="d ink rise" {d(.25)} x="52" y="222" font-size="150">{P["first"]}</text>',
        '<clipPath id="ln"><text class="d" x="52" y="362" font-size="150">' + P["last"] + "</text></clipPath>",
        f'<g class="rise" {d(.4)}><text class="d red" x="52" y="362" font-size="150">{P["last"]}</text>'
        '<g clip-path="url(#ln)"><rect class="shine" x="52" y="230" width="150" height="150" fill="var(--paper)" opacity=".55"/></g></g>',
    ]
    for i, line in enumerate(P["tagline"]):
        left.append(f'<text class="s ink rise" {d(.6 + i * .12)} x="56" y="{412 + i * 36}" font-size="31">{escape(line)}</text>')

    if PORTRAIT and P.get("hero_panel", "portrait") == "portrait":
        panel = portrait_panel(t, css)
    else:
        # right column: claim-level verification, looping (set "hero_panel": "claims" in profile.json)
        px, py, pw, ph = 640, 104, 504, 372
        panel = [
            f'<rect class="fade" {d(.5)} x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="var(--panel)" stroke="var(--rule)" stroke-width="1.5"/>',
            f'<g class="fade" {d(.7)}><text class="mb mute ls" x="{px + 24}" y="{py + 38}" font-size="13">EXHIBIT A</text>'
            f'<text class="mb ink ls" x="{px + pw - 24}" y="{py + 38}" font-size="13" text-anchor="end">CLAIM-LEVEL VERIFICATION</text>'
            f'<line x1="{px + 24}" y1="{py + 54}" x2="{px + pw - 24}" y2="{py + 54}" stroke="var(--rule)" stroke-width="1.5" stroke-dasharray="3 5"/></g>',
        ]
        ry0 = py + 96
        for i, (num, text, ok, score) in enumerate(CLAIMS):
            y = ry0 + i * 53
            t_row, t_mark = 1.0 + i * .45, 3.0 + i * .55
            css += [lk(f"r{i}", t_row), lk(f"k{i}", t_mark), f".r{i}{{animation:r{i} {loop}s linear infinite}}",
                    f".k{i}{{animation:k{i} {loop}s linear infinite}}"]
            col = "var(--ink)" if ok else "var(--red)"
            mark = (f'<path d="M{px + pw - 104} {y - 6}l6 6 11-13" fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
                    if ok else
                    f'<path d="M{px + pw - 103} {y - 12}l13 13m0-13l-13 13" fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>')
            strike = ""
            if not ok:
                css += [lk(f"x{i}", t_mark, "wipe"),
                        f".x{i}{{animation:x{i} {loop}s linear infinite;transform-origin:left center;transform-box:fill-box}}"]
                strike = f'<rect class="x{i}" x="{px + 62}" y="{y - 6}" width="{len(text) * 9.02:.0f}" height="2" fill="var(--red)"/>'
            panel.append(
                f'<g class="r{i}"><text class="mb mute" x="{px + 24}" y="{y}" font-size="15">{num}</text>'
                f'<text class="m ink" x="{px + 62}" y="{y}" font-size="15">{escape(text)}</text></g>{strike}'
                f'<g class="k{i}">{mark}<text class="mb" x="{px + pw - 24}" y="{y}" font-size="15" text-anchor="end" fill="{col}">{score}</text></g>'
                f'<line x1="{px + 24}" y1="{y + 20}" x2="{px + pw - 24}" y2="{y + 20}" stroke="var(--rule)" stroke-width="1"/>'
            )
        panel.append(f'<rect class="scan" x="{px + 14}" y="{ry0 - 24}" width="{pw - 28}" height="2" fill="var(--red)" opacity="0"/>')

        fy = py + ph - 34
        css += [lk("vd", 5.6), f".vd{{animation:vd {loop}s linear infinite}}", lk("st", 6.3, "stamp"),
                f".st{{animation:st {loop}s cubic-bezier(.3,1.4,.5,1) infinite;transform-origin:center;transform-box:fill-box}}",
                ".stbase{transform:rotate(-9deg);transform-origin:center;transform-box:fill-box}"]
        panel.append(
            f'<g class="vd"><text class="mb mute ls" x="{px + 24}" y="{fy}" font-size="13">VERDICT</text>'
            f'<text class="mb ink ls" x="{px + 110}" y="{fy}" font-size="13">SHIP 3  ·  HOLD 1</text></g>'
            f'<g class="stbase st"><rect x="{px + pw - 190}" y="{fy - 38}" width="166" height="50" rx="6" fill="var(--panel)" stroke="var(--red)" stroke-width="3"/>'
            f'<text class="d red" x="{px + pw - 107}" y="{fy - 1}" font-size="33" text-anchor="middle" letter-spacing=".06em">VERIFIED</text></g>'
        )

    # bottom strip: the pipeline, with a runner
    by = 510
    steps = P["pipeline"]
    seg = (w - 112) / len(steps)
    strip = [f'<line class="fade" {d(1.0)} x1="56" y1="{by - 26}" x2="{w - 56}" y2="{by - 26}" stroke="var(--rule)" stroke-width="2"/>',
             f'<circle class="run" cx="56" cy="{by - 26}" r="4.5" fill="var(--red)"/>']
    for i, sname in enumerate(steps):
        x = 56 + i * seg
        strip.append(f'<g class="rise" {d(1.05 + i * .1)}><rect x="{x}" y="{by - 31}" width="2" height="10" fill="var(--ink)"/>'
                     f'<text class="mb mute" x="{x}" y="{by}" font-size="14">0{i + 1}</text>'
                     f'<text class="mb ink ls" x="{x + 30}" y="{by}" font-size="14">{sname}</text></g>')

    label = f'{P["first"].title()} {P["last"].title()}. {" ".join(P["tagline"])} {P["role"].title()}, {P["location"].title()}.'
    return svg(w, h, t, "".join(left + panel + strip), FONTS, "".join(css), label)


# ───────────────────────────── job tiles ─────────────────────────────

def job(t, i, j):
    w, h = 400, 300
    base = i % 3 * .12
    acc = {"red": "var(--red)", "gold": "var(--gold)", "ink": "var(--ink)"}[j["accent"]]
    lines = textwrap.wrap(j["desc"], 31)[:3]
    css = ("@keyframes swing{0%{opacity:0;transform:translateY(34px) rotate(2.5deg)}"
           "60%{opacity:1;transform:translateY(-5px) rotate(-.6deg)}100%{opacity:1;transform:none}}"
           ".swing{animation:swing .9s cubic-bezier(.2,.8,.2,1) both;transform-origin:left bottom}"
           "@keyframes ring{0%{transform:scale(1);opacity:.7}100%{transform:scale(4.4);opacity:0}}"
           f".ring{{animation:ring 2.6s ease-out {1.2 + base:.2f}s infinite;transform-origin:center;transform-box:fill-box}}"
           f".shine{{animation:sweep 7s ease-in-out {2 + i * .5:.1f}s infinite;transform-box:fill-box}}")
    body = [
        f'<g class="swing" {d(base)}>',
        f'<rect class="growy" {d(base + .3)} x="1" y="40" width="7" height="220" fill="{acc}"/>',
        f'<text class="mb mute ls" x="34" y="52" font-size="15">JOB 0{i + 1}</text>',
        f'<circle cx="{w - 40}" cy="46" r="5" fill="{acc}"/><circle class="ring" cx="{w - 40}" cy="46" r="5" fill="none" stroke="{acc}" stroke-width="1.5" opacity="0"/>',
        f'<text class="mb ink ls" x="{w - 56}" y="52" font-size="13" text-anchor="end">{escape(j["status"])}</text>',
        f'<clipPath id="n"><text class="d" x="33" y="128" font-size="60">{escape(j["name"])}</text></clipPath>',
        f'<text class="d ink" x="33" y="128" font-size="60">{escape(j["name"])}</text>',
        '<g clip-path="url(#n)"><rect class="shine" x="33" y="70" width="70" height="70" fill="' + acc + '" opacity=".9"/></g>',
    ]
    for k, line in enumerate(lines):
        body.append(f'<text class="m ink fade" {d(base + .45 + k * .1)} x="34" y="{172 + k * 25}" font-size="17">{escape(line)}</text>')
    body += [
        f'<line x1="34" y1="250" x2="{w - 34}" y2="250" stroke="var(--rule)" stroke-width="1.5"/>',
        f'<text class="m mute fade" {d(base + .8)} x="34" y="276" font-size="14">{escape(j["stack"])}</text>',
        f'<g class="fade" {d(base + .9)}>{arrow(w - 48, 262, 13, "ink", diag=True)}</g>',
        "</g>",
    ]
    return svg(w, h, t, "".join(body), ["display", "mono-400", "mono-500"], css, f'{j["name"]}: {j["desc"]} Built with {j["stack"]}.')


# ───────────────────────────── activity ─────────────────────────────

def activity_stats():
    days = {dt.date.fromisoformat(k): v for k, v in C["days"].items()}
    end = dt.date.fromisoformat(C["fetched"])
    start = end - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    cal = []
    cur = start
    while cur <= end:
        cal.append((cur, days.get(cur, 0)))
        cur += dt.timedelta(days=1)
    total = C.get("total") or sum(v for _, v in cal)
    best_streak = run = 0
    for _, v in cal:
        run = run + 1 if v else 0
        best_streak = max(best_streak, run)
    busiest = max(cal, key=lambda x: x[1])
    months = {}
    for day, v in cal:
        months[(day.year, day.month)] = months.get((day.year, day.month), 0) + v
    months = sorted(months.items())[-12:]
    return dict(cal=cal, total=total, streak=best_streak, busiest=busiest,
                active=sum(1 for _, v in cal if v), months=months, start=start, end=end)


def activity(t):
    w, h = 1200, 500
    s = activity_stats()
    body = [header("ACTIVITY LOG  //  LAST 12 MONTHS", f"UPDATED {s['end'].strftime('%d %b %Y').upper()}", w)]

    # count-up total: CSS cannot change text, so stack frames and flash each one in turn
    n, total = 20, s["total"]
    for k in range(n):
        val = round(total * (1 - (1 - (k + 1) / (n + 1)) ** 3))
        body.append(f'<text class="d ink frame" {d(.4 + k * .055)} x="54" y="196" font-size="124">{val:,}</text>')
    body.append(f'<text class="d ink fade" style="animation-duration:.01s;animation-delay:{.4 + n * .055:.2f}s" x="54" y="196" font-size="124">{total:,}</text>')
    body.append(f'<text class="mb mute ls fade" {d(.5)} x="58" y="228" font-size="15">CONTRIBUTIONS</text>')

    facts = [("LONGEST STREAK", f"{s['streak']} DAYS"),
             ("BUSIEST DAY", f"{s['busiest'][1]}  ·  {s['busiest'][0].strftime('%d %b').upper()}"),
             ("ACTIVE DAYS", f"{s['active']}")]
    for k, (name, val) in enumerate(facts):
        y = 292 + k * 62
        body.append(f'<g class="rise" {d(.7 + k * .12)}><text class="mb mute ls" x="58" y="{y}" font-size="13">{name}</text>'
                    f'<text class="d ink" x="58" y="{y + 32}" font-size="30" letter-spacing=".03em">{val}</text>'
                    f'<line x1="58" y1="{y + 44}" x2="290" y2="{y + 44}" stroke="var(--rule)" stroke-width="1.5"/></g>')

    # contribution grid: squares pop in, sweeping left to right
    gx, gy, pitch, cell = 356, 112, 14.9, 11.5
    nonzero = sorted(v for _, v in s["cal"] if v)
    q = [nonzero[int(len(nonzero) * f)] for f in (.25, .5, .75)] if nonzero else [1, 2, 3]
    last_month = None
    for idx, (day, v) in enumerate(s["cal"]):
        col, row = idx // 7, idx % 7
        x, y = gx + col * pitch, gy + row * pitch
        if row == 0 and day.month != last_month and day.day <= 7 or (idx == 0):
            if col < 51:
                body.append(f'<text class="m mute fade" {d(.3 + col * .02)} x="{x:.1f}" y="{gy - 12}" font-size="13">{day.strftime("%b").upper()}</text>')
            last_month = day.month
        if v == 0:
            body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="var(--cell)"/>')
            continue
        level = 1 + sum(v > t_ for t_ in q)
        is_top = day == s["busiest"][0]
        fill = "var(--red)" if is_top else "var(--ink)"
        op = 1 if is_top else (.3, .5, .75, 1)[level - 1]
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="var(--cell)"/>'
                    f'<rect class="pop" {d(.5 + col * .022 + row * .012)} x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{fill}" fill-opacity="{op}"/>')

    # monthly bars: one bar per month, best month in red with its value
    bx, by, bw, bh = 356, 452, 788, 170
    months = s["months"]
    top = max(v for _, v in months) or 1
    slot = bw / len(months)
    body.append(f'<text class="mb mute ls fade" {d(1.2)} x="{bx}" y="{by - bh - 26}" font-size="13">BY MONTH</text>')
    body.append(f'<line x1="{bx}" y1="{by}" x2="{bx + bw}" y2="{by}" stroke="var(--ink)" stroke-width="2"/>')
    for k, ((yy, mm), v) in enumerate(months):
        x = bx + k * slot
        bar_h = max(3, v / top * (bh - 28))
        best = v == top
        fill = "var(--red)" if best else "var(--ink)"
        body.append(f'<rect class="growy" {d(1.3 + k * .06)} x="{x + 8:.1f}" y="{by - bar_h:.1f}" width="{slot - 16:.1f}" height="{bar_h:.1f}" rx="3" fill="{fill}" fill-opacity="{1 if best else .82}"/>')
        body.append(f'<text class="m mute" x="{x + slot / 2:.1f}" y="{by + 22}" font-size="13" text-anchor="middle">{dt.date(yy, mm, 1).strftime("%b").upper()}</text>')
        cls = "mb red pop" if best else "m mute fade"
        body.append(f'<text class="{cls}" {d(2.1 + k * .06)} x="{x + slot / 2:.1f}" y="{by - bar_h - 9:.1f}" font-size="{16 if best else 13}" text-anchor="middle">{v}</text>')

    label = (f"{total} contributions in the last 12 months. Longest streak {s['streak']} days, "
             f"busiest day {s['busiest'][1]} contributions on {s['busiest'][0].strftime('%d %B %Y')}.")
    return svg(w, h, t, "".join(body), ["display", "mono-400", "mono-500"], "", label)


# ───────────────────────────── kit ─────────────────────────────

def kit(t):
    w, h = 1200, 372
    body = [header("THE KIT  //  TOOLS FOR THE JOB", f"{sum(len(i) for _, i in P['kit'])} ITEMS", w)]
    colw = (w - 112) / len(P["kit"])
    for ci, (name, items) in enumerate(P["kit"]):
        x = 56 + ci * colw
        t0 = .3 + ci * .14
        body.append(f'<text class="d ink rise" {d(t0)} x="{x}" y="120" font-size="32" letter-spacing=".04em">{escape(name)}</text>')
        body.append(f'<rect class="growx" {d(t0 + .15)} x="{x}" y="134" width="{colw - 28}" height="3" fill="{"var(--red)" if ci == 0 else "var(--ink)"}"/>')
        for k, item in enumerate(items):
            y = 170 + k * 27
            body.append(f'<g class="rise" {d(t0 + .25 + k * .06)}><text class="m mute" x="{x}" y="{y}" font-size="13">{k + 1:02d}</text>'
                        f'<text class="m ink" x="{x + 32}" y="{y}" font-size="16">{escape(item)}</text></g>')
    label = "Toolkit. " + " ".join(f"{n}: {', '.join(i)}." for n, i in P["kit"])
    return svg(w, h, t, "".join(body), ["display", "mono-400", "mono-500"], "", label)


# ───────────────────────────── record ─────────────────────────────

def record(t):
    w, h = 1200, 250
    body = [header("ON THE RECORD", "EVIDENCE, NOT CLAIMS", w)]
    colw = (w - 112) / len(P["record"])
    for i, (kind, big, lines) in enumerate(P["record"]):
        x = 56 + i * colw
        t0 = .3 + i * .14
        body.append(f'<g class="rise" {d(t0)}>'
                    f'<text class="mb {"red" if i < 2 else "mute"} ls" x="{x}" y="112" font-size="13">{escape(kind)}</text>'
                    f'<text class="d ink" x="{x}" y="160" font-size="{44 if len(big) < 8 else 33}" letter-spacing=".02em">{escape(big)}</text>'
                    + "".join(f'<text class="m mute" x="{x}" y="{190 + k * 21}" font-size="13">{escape(l)}</text>' for k, l in enumerate(lines))
                    + "</g>")
        if i:
            body.append(f'<rect class="growy" {d(t0)} x="{x - 22}" y="96" width="1.5" height="120" fill="var(--rule)"/>')
    label = "Record. " + " ".join(f"{b.title()}, {', '.join(l)}." for _, b, l in P["record"])
    return svg(w, h, t, "".join(body), ["display", "mono-400", "mono-500"], "", label)


# ───────────────────────────── link buttons ─────────────────────────────

def link(t, i, l):
    w, h = 400, 110
    css = ("@keyframes nudge{0%,80%,100%{transform:none}90%{transform:translate(4px,-4px)}}"
           f".nudge{{animation:nudge 4s ease-in-out {1 + i * .4:.1f}s infinite}}")
    body = (f'<g class="rise" {d(i * .1)}><text class="d ink" x="34" y="72" font-size="44" letter-spacing=".04em">{escape(l["label"])}</text>'
            f'<g class="nudge">{arrow(w - 62, 42, 22, "red", diag=True)}</g></g>')
    return svg(w, h, t, body, ["display"], css, l["label"].title())


# ───────────────────────────── README ─────────────────────────────

def pic(name, width, alt, href=None):
    img = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./cards/{name}-dark.svg">'
           f'<img src="./cards/{name}-light.svg" width="{width}" alt="{escape(alt)}"></picture>')
    return f'<a href="{href}">{img}</a>' if href else img


def readme():
    s = activity_stats()
    name = f'{P["first"].title()} {P["last"].title()}'
    jobs = [pic(f'job-{j["slug"]}', "32.5%", f'{j["name"]}: {j["desc"]}', j["url"]) for j in P["jobs"]]
    links = [pic(f'link-{l["slug"]}', "24.3%", l["label"].title(), l["url"]) for l in P["links"]]
    rows = ["\n".join(jobs[k:k + 3]) for k in range(0, len(jobs), 3)]
    return "\n\n".join([
        "<!-- Every block below is an animated SVG from scripts/render_cards.py. Edit data/profile.json, not this file. -->",
        pic("hero", "100%", f'{name}. {" ".join(P["tagline"])}'),
        *rows,
        pic("activity", "100%", f'{s["total"]} contributions in the last 12 months'),
        pic("kit", "100%", "Toolkit: " + ", ".join(n for n, _ in P["kit"])),
        pic("record", "100%", "Awards, role and education"),
        "\n".join(links),
    ]) + "\n"


def main():
    CARDS.mkdir(exist_ok=True)
    out = {}
    for t in THEMES:
        out[f"hero-{t}"] = hero(t)
        out[f"activity-{t}"] = activity(t)
        out[f"kit-{t}"] = kit(t)
        out[f"record-{t}"] = record(t)
        for i, j in enumerate(P["jobs"]):
            out[f'job-{j["slug"]}-{t}'] = job(t, i, j)
        for i, l in enumerate(P["links"]):
            out[f'link-{l["slug"]}-{t}'] = link(t, i, l)
    for name, text in out.items():
        (CARDS / f"{name}.svg").write_text(text)
    if not STATIC:
        (ROOT / "README.md").write_text(readme())
    print(f"rendered {len(out)} cards{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()
