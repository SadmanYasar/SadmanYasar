"""Render data/stats.json into a Metal Gear Solid Survival Viewer SVG + 3D Idle Cat GIF suite."""

import base64
import io
import json
import math
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
FONTS = Path(__file__).parent / "fonts"
DATA = Path(__file__).parent / "data"
STATS = DATA / "stats.json"
MGS_CAT_3D = DATA / "mgs_cat_3d.jpg"

# Metal Gear Solid Tactical Olive / Codec Amber Palette
BG = "#11140E"
BG_DARK = "#0A0C08"
PANEL = "#1A1E15"
GRID = "#262C1F"
BORDER = "#4B533C"
TEXT = "#E6E4D5"
MUTED = "#8E967C"
CREAM_SEL = "#EAE2BE"
DARK_INK = "#11140E"
AMBER = "#E39856"
OLIVE = "#7D8760"
GREEN = "#88B86A"

W = 840

LINKS = [
    ("link-portfolio", "A", "PORTFOLIO", "https://www.sadmanyasar.site"),
    ("link-github", "B", "GITHUB", "https://github.com/SadmanYasar"),
    ("link-linkedin", "X", "LINKEDIN", "https://www.linkedin.com/in/sadman-yasar-sayem"),
    ("link-blog", "Y", "BLOG", "https://www.sadmanyasar.site"),
    ("link-email", "ST", "EMAIL", "mailto:sadmanyasarsayem@gmail.com"),
]

OPS_BRIEFS = {
    "arch-review-agent": "Multi-agent PR security & AST guardrail.",
    "3d-spritesheet-studio": "3D & webcam tracker to 2D spritesheets.",
    "agent-in-go": "Autonomous AI agent with tool calling in Go.",
    "3D-cat-art-museum": "Interactive 3D virtual gallery in Three.js.",
}

STACK = [
    ("LANGUAGES", "TypeScript, JavaScript, Python, Go, SQL (PostgreSQL)"),
    ("FRONTEND", "React, Next.js (App Router), React Native, Flutter, Three.js"),
    ("BACKEND", "Node.js, Express, REST APIs, GraphQL, PostgreSQL, MongoDB, Redis"),
    ("CLOUD/OPS", "AWS (SES, Lightsail), GCP (GKE), DigitalOcean, Docker, GH Actions"),
    ("AI/AGENTS", "LLM APIs, Prompt Design, AI Agents, RAG, Guardrails, Google ADK"),
]


def font_face(name, fname, text):
    f = TTFont(FONTS / fname, recalcTimestamp=False)
    opts = Options()
    try:
        import brotli  # noqa: F401
        opts.flavor = "woff2"
        mime = "font/woff2"
    except ImportError:
        mime = "font/ttf"
    opts.drop_tables += ["FFTM"]
    sub = Subsetter(opts)
    glyphs = (
        text
        + "┌┐└┘─│░▒▓█·•★⇄→✓<>/\\^_-+=()[]{}!?:;.,'\"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    )
    sub.populate(text=glyphs)
    sub.subset(f)
    buf = io.BytesIO()
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:{name};src:url(data:{mime};base64,{b64})}}"


def svg_wrap(w, h, body, text_sample=""):
    faces = "\n".join([
        font_face("display", "PlusJakartaSans-Bold.ttf", text_sample),
        font_face("sans", "PlusJakartaSans-Regular.ttf", text_sample),
        font_face("mono", "JetBrainsMono-Regular.ttf", text_sample),
    ])
    grid_pattern = f"""
<defs>
  <pattern id="mgsGrid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M 24 0 L 0 0 0 24" fill="none" stroke="{GRID}" stroke-width="0.8"/>
  </pattern>
</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="{BG}"/>
<rect x="0" y="0" width="{w}" height="{h}" fill="url(#mgsGrid)"/>
"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f"<style>{faces}</style>"
        f"{grid_pattern}{body}</svg>\n"
    )


def header_top():
    """Top HUD bar (840 x 76)."""
    body = f"""
  <text x="26" y="28" font-family="mono" font-size="11" fill="{TEXT}" letter-spacing="1.2">SADMAN</text>
  <rect x="26" y="34" width="160" height="7" fill="{CREAM_SEL}"/>
  <rect x="188" y="34" width="40" height="7" fill="{BORDER}"/>
  <rect x="26" y="45" width="120" height="4" fill="{OLIVE}"/>
  <rect x="26" y="56" width="18" height="8" fill="{OLIVE}"/>
  <text x="52" y="64" font-family="display" font-size="15" fill="{TEXT}" letter-spacing="1.5">PROFILE</text>

  <text x="814" y="28" text-anchor="end" font-family="mono" font-size="10.5" fill="{MUTED}">CODEC FREQ</text>
  <text x="814" y="48" text-anchor="end" font-family="display" font-size="18" fill="{AMBER}">140.15</text>
  <desc>La-Li-Lu-Le-Lo</desc>
  <line x1="26" y1="72" x2="814" y2="72" stroke="{BORDER}" stroke-width="1"/>
"""
    return svg_wrap(W, 76, body, text_sample="SADMAN PROFILE CODEC FREQ 140.15")


def build_cat_idle_gif(out_path):
    """Build a 420 x 360 looping idle animation GIF of the 3D MGS cat render."""
    base = Image.open(MGS_CAT_3D).convert("RGB")
    gw, gh = 420, 360
    # Crop inside outer MGS panel: left pad=26, right pad=10, top=4, bottom=14 -> inner 384 x 342
    iw, ih = 384, 342
    ix, iy = 26, 4
    base_fit = ImageOps.fit(base, (iw + 10, ih + 10), Image.Resampling.LANCZOS, centering=(0.5, 0.38))

    frames = []
    n_frames = 24
    for i in range(n_frames):
        t = (i / n_frames) * 2 * math.pi
        # Subtle idle breathing motion (vertical 2.5px + slight 1px sway)
        dy = int(round(2.5 * math.sin(t)))
        dx = int(round(1.0 * math.cos(t)))
        crop = base_fit.crop((5 + dx, 5 + dy, 5 + dx + iw, 5 + dy + ih))

        # Subtle warm breathing rim-light shimmer
        bright = 1.0 + 0.03 * math.sin(t)
        crop = ImageEnhance.Brightness(crop).enhance(bright)

        canvas = Image.new("RGB", (gw, gh), (17, 20, 14))
        draw = ImageDraw.Draw(canvas)
        # Subtle MGS background grid lines in outer padding
        for gx in range(0, gw, 24):
            draw.line([(gx, 0), (gx, gh)], fill=(38, 44, 31), width=1)
        for gy in range(0, gh, 24):
            draw.line([(0, gy), (gw, gy)], fill=(38, 44, 31), width=1)

        canvas.paste(crop, (ix, iy))
        # Crisp MGS border frame
        draw.rectangle([ix, iy, ix + iw - 1, iy + ih - 1], outline=(75, 83, 60), width=1)
        # Subtle tactical corner brackets & pulsing live indicator
        draw.line([(ix + 8, iy + 8), (ix + 22, iy + 8)], fill=(234, 226, 190), width=2)
        draw.line([(ix + 8, iy + 8), (ix + 8, iy + 22)], fill=(234, 226, 190), width=2)
        draw.line([(ix + iw - 23, iy + ih - 9), (ix + iw - 9, iy + ih - 9)], fill=(234, 226, 190), width=2)
        draw.line([(ix + iw - 9, iy + ih - 23), (ix + iw - 9, iy + ih - 9)], fill=(234, 226, 190), width=2)
        # Pulsing amber active dot
        dot_col = (227, 152, 86) if math.sin(t) > -0.2 else (130, 90, 50)
        draw.ellipse([ix + iw - 20, iy + 10, ix + iw - 12, iy + 18], fill=dot_col)

        frames.append(canvas.quantize(colors=128, method=Image.Quantize.MEDIANCUT))

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=75,
        loop=0,
        optimize=True,
    )


def header_loadout():
    """Right Loadout Pane (420 x 360) aligned flush 50/50 with cat_idle.gif (420 x 360)."""
    menu_items = [
        ("TYPESCRIPT / JAVASCRIPT", "PRIMARY ✓", True),
        ("REACT / NEXT.JS", "FRONTEND", False),
        ("NODE.JS / EXPRESS", "BACKEND", False),
        ("PYTHON / AI AGENTS", "AI / LLM", False),
        ("POSTGRESQL / MONGODB", "DATABASE", False),
        ("REACT NATIVE / FLUTTER", "MOBILE", False),
        ("DOCKER / KUBERNETES", "DEVOPS", False),
        ("AWS / GCP / DIGITALOCEAN", "CLOUD", False),
    ]
    rows_svg = [
        f'<rect x="8" y="4" width="386" height="26" fill="{CREAM_SEL}" stroke="{BORDER}" stroke-width="1"/>',
        f'<text x="201" y="21" text-anchor="middle" font-family="display" font-size="11.5" fill="{DARK_INK}" letter-spacing="1.5">LOADOUT // TECH STACK</text>',
    ]
    for i, (label, val, selected) in enumerate(menu_items):
        y = 38 + i * 39
        row_bg = CREAM_SEL if selected else PANEL
        txt_col = DARK_INK if selected else TEXT
        swatch_col = AMBER if selected else (GREEN if i % 2 == 0 else OLIVE)
        rows_svg.append(
            f'<rect x="8" y="{y}" width="386" height="33" fill="{row_bg}" stroke="{BORDER}" stroke-width="1"/>'
            f'<rect x="10" y="{y + 2}" width="52" height="29" fill="{swatch_col}"/>'
            f'<text x="36" y="{y + 21}" text-anchor="middle" font-family="mono" font-size="10" fill="{DARK_INK}">0{i + 1}</text>'
            f'<text x="72" y="{y + 21}" font-family="mono" font-size="12" fill="{txt_col}">{escape(label)}</text>'
            f'<text x="384" y="{y + 21}" text-anchor="end" font-family="mono" font-size="11.5" fill="{txt_col}">{escape(val)}</text>'
        )
    txt = "LOADOUT TECH STACK" + "".join(l + v for l, v, _ in menu_items)
    return svg_wrap(420, 360, "\n".join(rows_svg), text_sample=txt)


def nav_link(btn, label, accent):
    body = f"""
<rect x="6" y="10" width="156" height="36" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.2"/>
<circle cx="24" cy="28" r="9" fill="{CREAM_SEL}"/>
<text x="24" y="32" text-anchor="middle" font-family="display" font-size="10" fill="{DARK_INK}">{escape(btn)}</text>
<text x="94" y="32" text-anchor="middle" font-family="mono" font-size="11.5" fill="{TEXT}" letter-spacing="0.8">{escape(label)}</text>
<rect x="6" y="44" width="156" height="3" fill="{accent}"/>
"""
    return svg_wrap(168, 56, body, text_sample=btn + label)


def record(stats):
    items = [
        ("FOLLOWERS", f"{stats.get('followers', 0):,}", CREAM_SEL),
        ("REPO STARS", f"{stats.get('stars', 0):,}", AMBER),
        ("PRS MERGED", f"{stats.get('prs_merged', 0):,}", GREEN),
        ("COMMITS (INCL. PRIVATE)", f"{stats.get('contributions_all_time', 0):,}", TEXT),
    ]
    cols = []
    for i, (label, val, col) in enumerate(items):
        x = 26 + i * 199
        cols.append(
            f'<rect x="{x}" y="12" width="189" height="72" fill="{PANEL}" stroke="{BORDER}" stroke-width="1"/>'
            f'<rect x="{x}" y="12" width="189" height="4" fill="{OLIVE}"/>'
            f'<text x="{x + 14}" y="36" font-family="mono" font-size="10" fill="{MUTED}">{label}</text>'
            f'<text x="{x + 14}" y="68" font-family="display" font-size="26" fill="{col}">{val}</text>'
        )
    return svg_wrap(W, 96, "".join(cols), text_sample="".join(l + v for l, v, _ in items))


def data_end(stats):
    days = stats.get("contributions", {})
    return date.fromisoformat(max(days)) if days else date.today()


def radar(stats):
    days = stats.get("contributions", {})
    end = data_end(stats)
    first = end - timedelta(days=(end.weekday() + 1) % 7) - timedelta(weeks=52)
    grid = [[0] * 53 for _ in range(7)]
    total = 0
    counts = []
    for w in range(53):
        for d in range(7):
            day = first + timedelta(weeks=w, days=d)
            if day <= end:
                c = days.get(day.isoformat(), 0)
                grid[d][w] = c
                total += c
                if c:
                    counts.append(c)
    counts.sort()
    q1 = counts[int(len(counts) * 0.25)] if counts else 1
    q2 = counts[int(len(counts) * 0.50)] if counts else 2
    q3 = counts[int(len(counts) * 0.85)] if counts else 4

    rects = []
    ox, oy = 68, 54
    for d in range(7):
        for w in range(1, 53):
            c = grid[d][w]
            x = ox + (w - 1) * 14
            y = oy + d * 15
            if c == 0:
                fill = BG_DARK
            elif c <= q1:
                fill = "#2E3B25"
            elif c <= q2:
                fill = "#4F6B3A"
            elif c <= q3:
                fill = GREEN
            else:
                fill = AMBER
            rects.append(f'<rect x="{x}" y="{y}" width="11" height="11" fill="{fill}" stroke="{BG}" stroke-width="0.5"/>')

    day_labels = "".join(
        f'<text x="38" y="{oy + d * 15 + 9}" font-family="mono" font-size="9" fill="{MUTED}">{name}</text>'
        for d, name in enumerate(["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"])
    )
    body = f"""
<rect x="26" y="10" width="788" height="178" fill="{PANEL}" stroke="{BORDER}" stroke-width="1"/>
<text x="38" y="34" font-family="display" font-size="13" fill="{CREAM_SEL}" letter-spacing="1.2">SOLITON RADAR // 52-WEEK ACTIVITY</text>
<text x="798" y="34" text-anchor="end" font-family="mono" font-size="11" fill="{AMBER}">{total:,} CONTRIBUTIONS</text>
<line x1="26" y1="42" x2="814" y2="42" stroke="{BORDER}" stroke-width="1"/>
{day_labels}
{"".join(rects)}
<text x="38" y="176" font-family="mono" font-size="9.5" fill="{MUTED}">SIGNAL:  LOW <tspan fill="#2E3B25">■</tspan>  MED <tspan fill="#4F6B3A">■</tspan>  HIGH <tspan fill="{GREEN}">■</tspan>  PEAK <tspan fill="{AMBER}">■</tspan></text>
<text x="798" y="176" text-anchor="end" font-family="mono" font-size="8.5" fill="#23291C" letter-spacing="1.2">LA-LI-LU-LE-LO</text>
"""
    return svg_wrap(W, 200, body, text_sample=f"SOLITON RADAR 52-WEEK ACTIVITY {total} CONTRIBUTIONS SUNMONSIGNAL LA-LI-LU-LE-LO")


def ops(stats):
    by_name = {r["name"]: r for r in stats.get("repos", [])}
    out = []
    for r in stats.get("ops", []):
        live = by_name.get(r["name"], r)
        langs = " · ".join(live.get("languages", [])[:2]) or "Code"
        stars = live.get("stars", 0)
        desc = OPS_BRIEFS.get(r["name"], r["description"])
        out.append((r["name"], desc, f"★ {stars} · {langs}", r["url"]))
    return out


def op_card(title, desc, meta, idx):
    accent = AMBER if idx in (0, 3) else GREEN
    body = f"""
<rect x="14" y="8" width="392" height="88" fill="{PANEL}" stroke="{BORDER}" stroke-width="1"/>
<rect x="14" y="8" width="6" height="88" fill="{accent}"/>
<text x="30" y="30" font-family="display" font-size="14" fill="{CREAM_SEL}" letter-spacing="0.6">{escape(title.upper())}</text>
<text x="394" y="30" text-anchor="end" font-family="mono" font-size="10.5" fill="{accent}">{escape(meta)}</text>
<text x="30" y="54" font-family="sans" font-size="12.5" fill="{TEXT}">{escape(desc)}</text>
<text x="394" y="82" text-anchor="end" font-family="mono" font-size="10" fill="{MUTED}">[ A ] INSPECT REPO →</text>
"""
    return svg_wrap(420, 104, body, text_sample=title.upper() + meta + desc + "INSPECT REPO")


def stack():
    rows = [
        f'<rect x="26" y="10" width="788" height="160" fill="{PANEL}" stroke="{BORDER}" stroke-width="1"/>',
        f'<rect x="26" y="10" width="788" height="26" fill="{OLIVE}" fill-opacity="0.28"/>',
        f'<text x="40" y="28" font-family="display" font-size="12" fill="{CREAM_SEL}" letter-spacing="1.2">EQUIPMENT // TECH STACK</text>',
    ]
    for i, (cat, items) in enumerate(STACK):
        y = 56 + i * 23
        rows.append(
            f'<text x="40" y="{y}" font-family="mono" font-size="11" fill="{AMBER}">{escape(cat)}</text>'
            f'<text x="148" y="{y}" font-family="mono" font-size="11" fill="{TEXT}">{escape(items)}</text>'
        )
    return svg_wrap(W, 180, "\n".join(rows), text_sample="EQUIPMENT TECH STACK" + "".join(c + i for c, i in STACK))


def footer():
    msg = "CODEC 140.15 // AUTO-SYNCED DAILY BY GITHUB ACTIONS // GITHUB.COM/SADMANYASAR"
    body = f"""
<line x1="26" y1="8" x2="814" y2="8" stroke="{BORDER}" stroke-width="1"/>
<text x="420" y="32" text-anchor="middle" font-family="mono" font-size="10.5" fill="{MUTED}" letter-spacing="1">{msg}</text>
"""
    return svg_wrap(W, 48, body, text_sample=msg)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    stats = json.loads(STATS.read_text()) if STATS.exists() else {}

    (ASSETS / "header_top.svg").write_text(header_top())
    build_cat_idle_gif(ASSETS / "cat_idle.gif")
    (ASSETS / "header_loadout.svg").write_text(header_loadout())

    accents = [AMBER, GREEN, CREAM_SEL, AMBER, OLIVE]
    for (fname, btn, label, _), acc in zip(LINKS, accents):
        (ASSETS / f"{fname}.svg").write_text(nav_link(btn, label, acc))

    (ASSETS / "record.svg").write_text(record(stats))
    (ASSETS / "city.svg").write_text(radar(stats))
    for i, (title, desc, meta, _) in enumerate(ops(stats)):
        (ASSETS / f"op-{i + 1}.svg").write_text(op_card(title, desc, meta, i))

    (ASSETS / "stack.svg").write_text(stack())
    (ASSETS / "footer.svg").write_text(footer())


if __name__ == "__main__":
    main()
