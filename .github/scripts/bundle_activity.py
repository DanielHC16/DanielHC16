"""Bundle the generated activity assets into the README's local image paths.

Run after download_stats.py and the snake generator. For a local preview without
running Actions, --published reads the existing public contribution snake instead.
"""
import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from download_stats import PALETTES, SVG_NS, fetch_svg, normalize_card, recolor_cached

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"


def write_telemetry_pair(theme):
    """Embed both real cards on one exact 900px grid with a 12px middle gap."""
    suffix = "-light" if theme == "light" else ""
    cards = []
    for prefix, filename in (("stats", f"github-stats{suffix}.svg"), ("streak", f"github-streak{suffix}.svg")):
        card = ET.fromstring((ASSETS / filename).read_text(encoding="utf-8"))
        ids = {node.get("id"): f"{prefix}-{node.get('id')}" for node in card.iter() if node.get("id")}
        for node in card.iter():
            for key, value in list(node.attrib.items()):
                if key == "id":
                    node.set(key, ids[value])
                elif key.endswith("href") and value.startswith("#"):
                    node.set(key, "#" + ids.get(value[1:], value[1:]))
                else:
                    for old, new in ids.items():
                        value = value.replace(f"url(#{old})", f"url(#{new})")
                    node.set(key, value)
            if node.tag == f"{{{SVG_NS}}}style" and node.text:
                for old, new in ids.items():
                    node.text = node.text.replace(f"url(#{old})", f"url(#{new})")
        card.set("x", "0" if prefix == "stats" else "456")
        card.set("y", "0")
        card.set("width", "444")
        card.set("height", "175")
        cards.append(card)
    root = ET.Element(f"{{{SVG_NS}}}svg", {"width": "900", "height": "175", "viewBox": "0 0 900 175", "role": "img", "aria-labelledby": "telemetry-title"})
    ET.SubElement(root, f"{{{SVG_NS}}}title", {"id": "telemetry-title"}).text = "Daniel Camacho's GitHub statistics and contribution streak"
    root.extend(cards)
    (ASSETS / f"github-telemetry{suffix}.svg").write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")


def theme_snake(content, theme):
    dark = theme == "dark"
    p = PALETTES[theme]
    colors = ["2a2a2a", "48484a", "7c7c80", "aeaeb2", "e5e5ea"] if dark else ["e0e0e0", "d1d1d6", "8a8a8a", "636366", "1a1a1a"]
    variables = {"cb": p["border"], "cs": p["accent"], "ce": p["background"]}
    variables.update({f"c{i}": color for i, color in enumerate(colors)})
    for name, color in variables.items():
        content = re.sub(r"--" + name + r":[^;}]+", f"--{name}:#{color}", content)
    # The generator's eaten-cell progress strip reads as an unrelated stray line
    # below the contribution grid. Keep the graph and snake, remove that strip.
    content = re.sub(r'<rect\b[^>]*class="u(?:\s[^\"]*)?"[^>]*/>', '', content)
    content = content.replace('viewBox="-16 -32 880 192"', 'viewBox="-16 -32 880 160"')
    content = content.replace('height="192"', 'height="160"', 1)
    reduced = "@media(prefers-reduced-motion:reduce){*{animation:none!important}}"
    if reduced not in content:
        content = content.replace("</svg>", f"<style>{reduced}</style></svg>")
    return center_contribution_grid(content)


def center_contribution_grid(content):
    """Center the fixed contribution cells, independent of the snake's motion."""
    root = ET.fromstring(content)
    cells = [node for node in root.iter(f"{{{SVG_NS}}}rect") if "c" in node.get("class", "").split()]
    if not cells:
        raise ValueError("Contribution SVG has no grid cells to center")
    styles = " ".join(node.text or "" for node in root.iter(f"{{{SVG_NS}}}style"))
    cell_style = re.search(r"\.c\s*\{([^}]+)\}", styles)
    declarations = cell_style[1] if cell_style else ""

    def extent(cell, name):
        value = cell.get(name)
        if value is None:
            match = re.search(r"(?:^|;)\s*" + name + r"\s*:\s*([\d.]+)px", declarations)
            if not match:
                raise ValueError(f"Contribution cell has no {name}")
            value = match[1]
        return float(value.removesuffix("px"))

    left = min(float(cell.get("x", "0")) for cell in cells)
    top = min(float(cell.get("y", "0")) for cell in cells)
    right = max(float(cell.get("x", "0")) + extent(cell, "width") for cell in cells)
    bottom = max(float(cell.get("y", "0")) + extent(cell, "height") for cell in cells)
    padding = (900 - (right - left)) / 2
    canvas_height = (bottom - top) + 2 * padding
    dx = padding - left
    dy = padding - top
    wrapper = next((node for node in root if node.get("data-profile-grid") == "centered"), None)
    if wrapper is None:
        wrapper = ET.Element(f"{{{SVG_NS}}}g", {"data-profile-grid": "centered"})
        metadata = {"style", "defs", "title", "desc", "metadata"}
        for child in list(root):
            if child.tag.rsplit("}", 1)[-1] not in metadata:
                root.remove(child)
                wrapper.append(child)
        root.append(wrapper)
    wrapper.set("transform", f"translate({dx:g} {dy:g})")
    root.set("width", "900")
    root.set("height", f"{canvas_height:g}")
    root.set("viewBox", f"0 0 900 {canvas_height:g}")
    return ET.tostring(root, encoding="unicode")


def main(published=False, stats_only=False):
    ASSETS.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        suffix = "-light" if theme == "light" else ""
        for card in ("github-stats", "github-streak"):
            name = f"{card}{suffix}.svg"
            if published:
                content = fetch_svg(f"https://raw.githubusercontent.com/DanielHC16/DanielHC16/output/{card}.svg")
                content = recolor_cached(content, theme, source_is_dark=True)
            else:
                content = normalize_card((DIST/name).read_text(encoding="utf-8"))
            (ASSETS/name).write_text(content, encoding="utf-8")

        if stats_only:
            continue
        name = "github-contribution-grid-snake" + ("-dark" if theme == "dark" else "") + ".svg"
        content = fetch_svg(f"https://raw.githubusercontent.com/DanielHC16/DanielHC16/output/{name}") if published else (DIST/name).read_text(encoding="utf-8")
        (ASSETS/name).write_text(theme_snake(content, theme), encoding="utf-8")
    for theme in ("dark", "light"):
        write_telemetry_pair(theme)
    print(f"Bundled {6 if stats_only else 8} themed activity images from real GitHub data.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", action="store_true", help="Recolor existing published data for local review")
    parser.add_argument("--stats-only", action="store_true", help="Refresh only the four displayed telemetry cards")
    args = parser.parse_args()
    main(args.published, args.stats_only)
