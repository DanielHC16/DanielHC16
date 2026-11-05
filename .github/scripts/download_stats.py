"""Download themed cards; preserve cached stats during provider outages."""
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode

PALETTES = {
    "dark": {"background": "1a1a1a", "foreground": "fafafa", "accent": "c7c7cc", "muted": "aeaeb2", "border": "48484a"},
    "light": {"background": "fafafa", "foreground": "1a1a1a", "accent": "636366", "muted": "636366", "border": "e0e0e0"},
}
STATS_MIRRORS = [
    "https://github-readme-stats.vercel.app/api",
    "https://github-readme-stats-eight-theta.vercel.app/api",
    "https://github-readme-stats.sigma-axis.vercel.app/api",
]
URLS = {}
for theme, palette in PALETTES.items():
    suffix = "-light" if theme == "light" else ""
    stats = urlencode({
        "username": "DanielHC16", "show_icons": "true", "locale": "en",
        "hide_border": "false", "border_radius": 0, "disable_animations": "true",
        "custom_title": "My GitHub Stats", "bg_color": palette["background"],
        "title_color": palette["foreground"], "text_color": palette["foreground"],
        "icon_color": palette["accent"], "ring_color": palette["accent"],
        "border_color": palette["border"],
    })
    streak = urlencode({
        "user": "DanielHC16", "locale": "en", "mode": "daily",
        "hide_border": "false", "border_radius": 0, "disable_animations": "true",
        "date_format": "[Y.]n.j", "background": palette["background"],
        "border": palette["border"], "stroke": palette["border"],
        "ring": palette["accent"], "fire": palette["accent"],
        "currStreakNum": palette["foreground"], "sideNums": palette["foreground"],
        "currStreakLabel": palette["accent"], "sideLabels": palette["accent"],
        "dates": palette["muted"],
    })
    URLS[f"github-stats{suffix}.svg"] = [f"{url}?{stats}" for url in STATS_MIRRORS]
    URLS[f"github-streak{suffix}.svg"] = [f"https://streak-stats.demolab.com?{streak}"]

MAX_RETRIES = 3
RETRY_DELAY = 5
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def fetch_svg(url):
    request = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
    with urllib.request.urlopen(request, timeout=10) as response:
        content = response.read().decode("utf-8")
    if ET.fromstring(content).tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Response is not an SVG document")
    return content


def normalize_card(content):
    """Keep cached/fresh metrics visible and center the grade on its ring."""
    root = ET.fromstring(content)
    final_rank = re.search(r"@keyframes rankAnimation.*?to\s*{\s*stroke-dashoffset:\s*([\d.]+)", content, re.S)
    static = '*{animation:none!important}.stagger,[style*="animation"]{opacity:1!important}'
    if final_rank:
        static += f'.rank-circle{{stroke-dashoffset:{final_rank[1]}!important}}'

    # Earlier cards can contain this override inside nested icon SVGs. Keep a
    # single root-level override, making repeated fallback normalization stable.
    for parent in root.iter():
        for child in list(parent):
            if child.tag == f"{{{SVG_NS}}}style" and (
                child.get("data-profile-style") == "static" or (child.text or "").startswith('*{animation:none!important}.stagger')
            ):
                parent.remove(child)
    style = ET.SubElement(root, f"{{{SVG_NS}}}style", {"data-profile-style": "static"})
    style.text = static

    for rect in root.iter(f"{{{SVG_NS}}}rect"):
        if "rx" in rect.attrib:
            rect.set("rx", "0")

    for group in root.iter(f"{{{SVG_NS}}}g"):
        if group.get("data-testid") != "rank-circle":
            continue
        circle = next((node for node in group.iter(f"{{{SVG_NS}}}circle") if "rank-circle-rim" in node.get("class", "").split()), None)
        if circle is None:
            continue
        for rank in group.iter(f"{{{SVG_NS}}}g"):
            if "rank-text" not in rank.get("class", "").split():
                continue
            rank.attrib.pop("transform", None)
            rank.set("style", "transform:none!important;animation:none!important")
            for label in rank.iter(f"{{{SVG_NS}}}text"):
                label.set("x", circle.get("cx", "0"))
                label.set("y", circle.get("cy", "0"))
                label.set("text-anchor", "middle")
                label.set("dominant-baseline", "central")
                label.set("alignment-baseline", "central")
                label.attrib.pop("dx", None)
                label.attrib.pop("dy", None)
    return ET.tostring(root, encoding="unicode")


def validate_metric_card(content, filename):
    """An API error can itself be valid SVG; do not replace metrics with it."""
    root = ET.fromstring(content)
    if filename.startswith("github-stats"):
        valid = any(node.get("data-testid") == "main-card-body" for node in root.iter())
    else:
        labels = " ".join(root.itertext())
        valid = "Current Streak" in labels and "Total Contributions" in labels
    if not valid:
        raise ValueError(f"Provider returned an error card instead of {filename}")


def recolor_cached(content, theme, source_is_dark=False):
    palette = PALETTES[theme]
    # Migrate the original green cards without changing their numbers or labels.
    colors = {
        "0a0f0b": palette["background"], "68b587": palette["accent"],
        "b7d364": palette["foreground"], "abd200": palette["accent"],
        "e4e2e2": palette["border"],
    }
    if source_is_dark and theme == "light":
        colors.update({PALETTES["dark"][key]: value for key, value in palette.items()})
    content = re.sub(r"#([0-9a-fA-F]{6})\b", lambda match: "#" + colors.get(match[1].lower(), match[1]), content)
    # Square the card rectangles without changing the fire icon's ellipse mask.
    content = re.sub(r"(<rect\b[^>]*\brx=)([\"'])[^\"']*\2", r'\g<1>"0"', content)
    return normalize_card(content)


def placeholder(theme):
    p = PALETTES[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
      <rect x=".5" y=".5" width="494" height="194" fill="#{p['background']}" stroke="#{p['border']}"/>
      <text x="247.5" y="87" font-family="monospace" font-size="14" fill="#{p['foreground']}" text-anchor="middle">GitHub stats temporarily unavailable.</text>
      <text x="247.5" y="113" font-family="monospace" font-size="11" fill="#{p['muted']}" text-anchor="middle">The next scheduled update will retry.</text>
    </svg>'''


def download_file(filename, url_list):
    print(f"Downloading {filename}...")
    dist = Path("dist")
    dist.mkdir(exist_ok=True)
    target = dist / filename
    theme = "light" if "-light" in filename else "dark"
    for url in url_list:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                content = fetch_svg(url)
                validate_metric_card(content, filename)
                target.write_text(recolor_cached(content, theme), encoding="utf-8")
                print(f"Downloaded {filename}.")
                return True
            except Exception as error:
                print(f"{filename}, attempt {attempt}/{MAX_RETRIES}: {error}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

    # A first light-theme run can recolor the existing dark card if its light
    # counterpart is not live yet. The previous published data stays visible.
    candidates = [filename]
    if theme == "light":
        candidates.append(filename.replace("-light", ""))
    for cached_name in candidates:
        try:
            content = fetch_svg(f"https://raw.githubusercontent.com/DanielHC16/DanielHC16/output/{cached_name}")
            validate_metric_card(content, filename)
            content = recolor_cached(content, theme, source_is_dark="-light" not in cached_name)
            target.write_text(content, encoding="utf-8")
            print(f"Restored {filename} from the last published card.")
            return True
        except Exception as error:
            print(f"Cache unavailable for {cached_name}: {error}")

    target.write_text(placeholder(theme), encoding="utf-8")
    print(f"Created a themed placeholder for {filename}.")
    return True


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda item: download_file(*item), URLS.items()))
