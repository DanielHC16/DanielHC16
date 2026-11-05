"""Export looping README GIFs from the editable SVG sources.

Optional authoring dependencies: pip install pillow playwright
Then: python -m playwright install chromium
Run: python .github/scripts/render_readme_gifs.py
Use --encode-only after capturing the same frame sheets with browser tooling.
"""
import argparse
import math
import re
import threading
import xml.etree.ElementTree as ET
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
FRAMES = ROOT / ".preview" / "animation-sheets"
def design_sources():
    sources = []
    for part, version in (("divider", "v3"), ("footer", "v4"), ("header", "v5")):
        for theme in ("dark", "light"):
            source = ASSETS / f"nier-{part}-{version}-{theme}.svg"
            if source.is_file():
                sources.append((source.stem, source.name, int(ET.parse(source).getroot().get("height"))))
    return sources


DESIGN = design_sources()
def activity_sources():
    sources = []
    for theme in ("dark", "light"):
        filename = "github-contribution-grid-snake" + ("-dark" if theme == "dark" else "") + ".svg"
        height = int(ET.parse(ASSETS / filename).getroot().get("height"))
        sources.append((f"nier-contributions-v3-{theme}", filename, height))
    return sources


ACTIVITY = activity_sources()


def scene_settings(scene):
    if scene == "design":
        if len(DESIGN) != 6:
            raise FileNotFoundError("Rebuild the six animated SVG sources before exporting GIFs.")
        return DESIGN, 12000, 96
    svg = (ASSETS / ACTIVITY[0][1]).read_text(encoding="utf-8")
    match = re.search(r"animation:[^;]*?(\d+)ms", svg)
    duration = int(match[1]) if match else 71700
    # 50ms frames avoid the visible stepping of the previous 6fps export.
    # Preserve the source duration and route rather than speeding up the snake.
    return ACTIVITY, duration, math.ceil(duration / (1000 / 20))


def render(scene):
    from playwright.sync_api import sync_playwright

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    items, duration, count = scene_settings(scene)
    target = FRAMES / scene
    target.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 900, "height": sum(item[2] for item in items)}, device_scale_factor=1, reduced_motion="no-preference")
            origin = f"http://127.0.0.1:{server.server_port}"
            # Keep the parent and SVG frames on the same local origin. Loading
            # local frames from about:blank can produce blocked-frame images.
            page.goto(origin)
            html = '<style>html,body{margin:0;padding:0}iframe{display:block;border:0;width:900px}</style>'
            html += ''.join(f'<iframe src="{origin}/assets/{source}" height="{height}"></iframe>' for _, source, height in items)
            page.set_content(html, wait_until="networkidle")
            children = [frame for frame in page.frames if frame != page.main_frame]
            for frame, (name, _, _) in zip(children, items):
                if not frame.locator("svg").count():
                    raise RuntimeError(f"SVG frame did not load: {name}")
                frame.evaluate("color => { const root=document.documentElement; root.style.width='100%'; root.style.height='100%'; root.style.background=color; }", "#1a1a1a" if name.endswith("dark") else "#fafafa")
            for index in range(count):
                moment = index * duration / count
                for frame in children:
                    frame.evaluate("ms => { for(const a of document.getAnimations()){a.pause();a.currentTime=ms;} }", moment)
                page.screenshot(path=str(target / f"frame-{index:04}.png"), animations="allow")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


def encode(scene):
    items, duration, count = scene_settings(scene)
    paths = [FRAMES / scene / f"frame-{index:04}.png" for index in range(count)]
    missing = next((path for path in paths if not path.is_file()), None)
    if missing:
        raise FileNotFoundError(f"Missing frame sheet: {missing}")
    durations = [round((i+1)*duration/count/10)*10 - round(i*duration/count/10)*10 for i in range(count)]
    top = 0
    for name, _, height in items:
        frames = []
        palette = None
        for path in paths:
            with Image.open(path) as sheet:
                crop = sheet.crop((0, top, 900, top+height)).convert("RGB")
                if palette is None:
                    palette = crop.quantize(colors=256)
                frames.append(crop.quantize(palette=palette, dither=Image.Dither.NONE))
        target = ASSETS / f"{name}.gif"
        frames[0].save(target, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=1, optimize=True)
        with Image.open(target) as result:
            if result.n_frames < 2:
                raise RuntimeError(f"Export is static: {target}")
        top += height
        print(f"Exported {name}.gif ({count} source frames, {duration/1000:g}s loop)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encode-only", action="store_true")
    parser.add_argument("--scene", choices=("design", "activity", "all"), default="all")
    args = parser.parse_args()
    for scene in (("design", "activity") if args.scene == "all" else (args.scene,)):
        if not args.encode_only:
            render(scene)
        encode(scene)
