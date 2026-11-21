"""Rewrite only the content between <!-- brief:start --> / <!-- brief:end --> markers in README.md."""

import json
import sys
from html import escape

from render import LINKS, ROOT, STACK, STATS, ops

README = ROOT / "README.md"


def img(name, alt, width="100%", ext="svg"):
    return f'<img src="./assets/{name}.{ext}" alt="{escape(alt)}" width="{width}" align="top">'


def pairs(items):
    """Half-width pieces two per row. Must touch with zero whitespace between them."""
    return ["".join(items[i:i + 2]) for i in range(0, len(items), 2)]


def linked(url, image):
    return f'<a href="{url}">{image}</a>' if url else image


def brief(stats):
    links = "".join(linked(url, img(name, label, "20%")) for name, _, label, url in LINKS)
    cards = [
        linked(url, img(f"op-{i + 1}", f"{title}: {desc}", "50%"))
        for i, (title, desc, _, url) in enumerate(ops(stats))
    ]
    hero_row = (
        img("cat_idle", "3D Blue-Eyed Persian Cat Operative (Idle Animation)", "45.71%", ext="gif")
        + img("header_loadout", "Loadout // Tech Stack", "54.29%")
    )
    return "\n".join([
        '<div align="center">',
        img("header_top", "PROFILE — Sadman Yasar Sayem, Codec 140.85"),
        hero_row,
        links,
        img("record", f"Live Telemetry: {stats.get('followers', 0):,} followers, {stats.get('stars', 0):,} stars, "
                      f"{stats.get('prs_merged', 0):,} PRs merged, {stats.get('contributions_all_time', 0):,} commits (incl. private)"),
        img("city", "Soliton Radar: 52-Week Activity Matrix"),
        *pairs(cards),
        img("stack", "Equipment / Tech Stack: " + "; ".join(f"{k}: {v}" for k, v in STACK)),
        img("footer", "Codec 140.85 // Auto-synced daily by GitHub Actions."),
        "</div>",
    ])


def replace_zone(text, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        sys.exit(f"README.md must contain exactly one {start} and one {end}")
    head, rest = text.split(start)
    _, tail = rest.split(end)
    return f"{head}{start}\n{content}\n{end}{tail}"


def main():
    stats = json.loads(STATS.read_text())
    README.write_text(replace_zone(README.read_text(), "brief", brief(stats)))


if __name__ == "__main__":
    main()
