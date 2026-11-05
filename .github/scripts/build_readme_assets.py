"""Build the original D-16 profile artwork (standard library, offline).

Run: python .github/scripts/build_readme_assets.py
Animated SVG sources use a twelve-second loop; README GIF exports are rendered from
these sources. Theme-specific filenames prevent cached artwork in IDE previews.
"""
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2] / "assets"
PALETTES = {
    "dark": {"bg": "#1a1a1a", "surface": "#252525", "fg": "#fafafa", "accent": "#c7c7cc", "muted": "#aeaeb2", "border": "#48484a", "selected": "#c7c7cc", "selected_text": "#1a1a1a", "c1": "#ffffff", "c2": "#e5e5ea", "c3": "#aeaeb2", "c4": "#7c7c80", "c5": "#e5e5ea", "c6": "#c7c7cc"},
    "light": {"bg": "#fafafa", "surface": "#ffffff", "fg": "#1a1a1a", "accent": "#636366", "muted": "#636366", "border": "#d1d1d6", "selected": "#48484a", "selected_text": "#fafafa", "c1": "#7c7c80", "c2": "#636366", "c3": "#3a3a3c", "c4": "#1c1c1e", "c5": "#7c7c80", "c6": "#48484a"},
}
STACK = [
    ("01", "LANGUAGES", ["Java", "Python", "JavaScript", "TypeScript", "C"]),
    ("02", "FRAMEWORKS", ["Spring", "Express", "Node.js", "React", "Next.js", "Tailwind CSS", "NestJS"]),
    ("03", "DATABASES", ["MySQL", "PostgreSQL", "MongoDB", "Firebase"]),
    ("04", "PLATFORMS", ["Git", "AWS", "GCP", "Linux", "Vercel"]),
]
ANIMATION = """
@keyframes orbit{to{transform:rotate(360deg)}}
@keyframes counter-orbit{to{transform:rotate(-360deg)}}
@keyframes slow-pulse{0%,100%{opacity:.45}50%{opacity:1}}
@keyframes cube-assembly{0%,10%,100%{transform:translate(var(--dx),var(--dy));opacity:.35}36%,66%{transform:translate(0,0);opacity:1}90%{transform:translate(var(--dx),var(--dy));opacity:.35}}
.cube-face{animation:cube-assembly 12s cubic-bezier(.22,1,.36,1) infinite}
.orbit{animation:orbit 12s linear infinite}
.counter-orbit{animation:counter-orbit 12s linear infinite}
.slow-pulse{animation:slow-pulse 4s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def text(x, y, value, size=12, css="", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{css}" {extra}>{escape(value)}</text>'


def write(name, w, h, theme, title, desc, body, defs=""):
    palette = PALETTES[theme]
    tokens = ";".join(f"--{key}:{value}" for key, value in palette.items())
    style = f''':root{{{tokens}}}
text{{font-family:'Segoe UI',Arial,sans-serif;fill:var(--fg)}}
.mono{{font-family:'Consolas','Courier New',monospace;letter-spacing:1.5px}}
.muted{{fill:var(--muted)}}.selected-text{{fill:var(--selected_text)}}
.line{{fill:none;stroke:var(--border);stroke-width:1}}.accent-line{{fill:none;stroke:var(--accent);stroke-width:1}}
.chrome{{fill:url(#chrome)}}{ANIMATION}'''
    chrome = '<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">' + ''.join(f'<stop offset="{stop}%" stop-color="var(--c{i})"/>' for i, stop in enumerate((0,35,49,51,70,100),1)) + '</linearGradient>'
    doc = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs><style>{style}</style>{chrome}{defs}</defs>
<rect width="{w}" height="{h}" fill="var(--bg)"/>{body}</svg>\n'''
    (ASSETS / f"nier-{name}-{theme}.svg").write_text(doc, encoding="utf-8")


def diamond(cx, cy, radius=5, blink=False):
    css = ' class="blink"' if blink else ''
    return f'<path{css} d="M{cx} {cy-radius}l{radius} {radius}l-{radius} {radius}l-{radius}-{radius}Z" fill="var(--accent)"/>'


def header(theme):
    body = '<path class="line" d="M24 18H876 M24 180H876"/>'
    body += text(24,44,"GITHUB / PERSONAL ARCHIVE",10,"mono muted")
    body += text(876,44,"D-16",11,"mono muted",'text-anchor="end"')
    body += text(24,105,"Daniel Camacho",47,"chrome",'font-weight="400" letter-spacing="-.5"')
    body += text(26,134,"SOFTWARE ENGINEER",12,"mono muted")
    body += text(26,163,"BUILD. LEARN. ITERATE.",10,"mono muted")
    body += '<g transform="translate(796 103)" aria-hidden="true">'
    body += '<g fill="var(--border)"><rect x="-66" y="-47" width="2" height="2"/><rect x="64" y="-47" width="2" height="2"/><rect x="-66" y="62" width="2" height="2"/><rect x="64" y="62" width="2" height="2"/></g>'
    faces = [
        ("M0-38 38-16 0 6Z",12,-16,.04),
        ("M0-38 0 6-38-16Z",-12,-16,.07),
        ("M-38-16 0 6-38 28Z",-18,0,.03),
        ("M0 6 0 50-38 28Z",-12,14,.05),
        ("M0 6 38-16 38 28Z",18,0,.1),
        ("M0 6 38 28 0 50Z",12,14,.08),
    ]
    for i,(path,dx,dy,fill) in enumerate(faces):
        body += f'<g class="cube-face" style="--dx:{dx}px;--dy:{dy}px;animation-delay:{-i*.25}s"><path d="{path}" fill="var(--accent)" fill-opacity="{fill}" stroke="var(--accent)" stroke-width="1"/></g>'
    body += '</g>'
    write("header-v5",900,192,theme,"Daniel Camacho / Software Engineer","Static Daniel Camacho typography and D-16 side label. Six triangular faces assemble into an original isometric cube, pause, and unfold on a twelve-second loop. No header orbit, ring, sheen, scanning line, or blinking text.",body)


def stack(theme):
    body = ''
    for i,(number,category,items) in enumerate(STACK):
        y=42+i*53
        body += f'<rect x="24" y="{y-18}" width="29" height="26" fill="var(--surface)"/>'
        body += text(38.5,y,number,10,"mono muted",'text-anchor="middle"')
        body += text(65,y,category,11,"mono muted")
        body += text(218,y,"   \u00b7   ".join(items),15.5,extra='xml:space="preserve" style="white-space:pre"')
        if i<3: body += f'<path class="line" d="M218 {y+26}H876" stroke-opacity=".55"/>'
    write("stack-v4",900,240,theme,"Technical loadout",". ".join(category+": "+", ".join(items) for _,category,items in STACK),body)


BIO = "A dedicated Software Engineer specializing in Backend Development, with diverse experience in software development and a strong passion for problem solving. I love turning complex challenges into elegant, efficient solutions that make a real difference."


def intro(theme, mobile=False):
    lines = [
        "A dedicated Software Engineer specializing in Backend Development, with diverse experience in software",
        "development and a strong passion for problem solving. I love turning complex challenges into elegant,",
        "efficient solutions that make a real difference.",
    ]
    if mobile:
        from textwrap import wrap
        lines = wrap(BIO, width=46)
    assert " ".join(lines) == BIO
    width,height = (420,280) if mobile else (900,208)
    right,bottom = width-12,height-12
    body = f'<rect x="12.5" y="12.5" width="{width-25}" height="{height-25}" class="line"/>'
    body += f'<path class="accent-line" d="M12 26V12h14 M{right-14} 12h14v14 M12 {bottom-14}v14h14 M{right-14} {bottom}h14v-14"/>'
    body += '<rect x="28" y="4" width="174" height="17" fill="var(--bg)"/>'
    body += text(36,16,"01 / PERSONAL RECORD",9,"mono muted")
    greeting_y, body_y = (69,107) if mobile else (67,105)
    body += text(36,greeting_y,"What's up? I'm Daniel.",21,extra='font-weight="600"')
    for i,line in enumerate(lines):
        size=16 if mobile else 17
        baseline=body_y+i*(24 if mobile else 26)
        if "Backend Development" in line:
            before,after=line.split("Backend Development",1)
            body += f'<text x="36" y="{baseline}" font-size="{size}">{escape(before)}<tspan font-weight="600">Backend Development</tspan>{escape(after)}</text>'
        else:
            body += text(36,baseline,line,size)
    write("intro-mobile-v5" if mobile else "intro-v5",width,height,theme,"What's up? I'm Daniel.",BIO,body)


def divider(theme):
    body = '<path class="line" d="M24 16H419 M481 16H876 M24 20H419 M481 20H876"/>'
    body += '<g class="slow-pulse"><path class="accent-line" d="M450 9 463 18 450 27 437 18Z"/>'
    body += '<path d="M450 15 454 18 450 21 446 18Z" fill="var(--accent)"/></g>'
    write("divider-v3",900,36,theme,"Section break","Stationary double hairlines and a centered diamond with a slow four-second pulse.",body)


def section(theme, name, number, label):
    body = text(450,14,number,9,"mono muted",'text-anchor="middle"')
    body += text(450,37,label,14,"mono",'text-anchor="middle"')
    body += '<path class="line" d="M333 22h-10v20h10 M567 22h10v20h-10"/>'
    write("section-"+name+"-v3",900,56,theme,label,"A centered, numbered technical section title framed by short geometric brackets; its section divider is a separate image.",body)


def footer(theme):
    body = '<path class="line" d="M24 12H876 M24 128H876"/>'
    body += text(24,50,"END OF RECORD / CONTINUE THE CONVERSATION",10,"mono muted")
    body += text(24,84,"LET'S CONNECT, CODE, AND CREATE THE FUTURE.",18,extra='font-weight="300" letter-spacing=".5"')
    body += '<g transform="translate(816 70)"><path class="line" d="M0-34 34 0 0 34-34 0Z M0-23 23 0 0 23-23 0Z M0-12 12 0 0 12-12 0Z"/>'
    body += '<g class="orbit"><circle r="39" class="accent-line" stroke-dasharray="13 13 2 13"/><circle cy="-39" r="2.5" fill="var(--accent)"/></g>'
    body += '<g class="counter-orbit"><path class="accent-line" d="M0-29A29 29 0 0 1 29 0"/></g>'
    body += '<path class="slow-pulse" d="M0-4 4 0 0 4-4 0Z" fill="var(--accent)"/></g>'
    write("footer-v4",900,140,theme,"Let's connect, code, and create the future.","An original NieR-inspired geometric signoff: concentric diamonds, counter-rotating segmented rings on a twelve-second loop, and a slow four-second center pulse. No repeated identity labels.",body)


def portfolio(theme):
    body = '<rect x=".5" y=".5" width="899" height="59" fill="var(--surface)" stroke="var(--border)"/>'
    body += '<path class="accent-line" d="M.5 12V.5H12 M888 .5h11.5V12 M.5 48v11.5H12 M888 59.5h11.5V48"/>'
    body += text(24,35,"01",11,"mono muted")
    body += '<path class="line" d="M61 18V42 M87 30H304 M596 30H813"/>'
    body += text(450,36,"VIEW PORTFOLIO",16,"mono",'text-anchor="middle"')
    body += '<path class="accent-line" d="M852 16 866 30 852 44 838 30Z M846 30h12 M853 25l5 5-5 5"/>'
    write("link-portfolio-v2",900,60,theme,"View my portfolio","A full-width portfolio link with registration corners, balanced rules, and a geometric arrow.",body)


def button(theme, name, label, index, selected=False):
    fill='var(--selected)' if selected else 'var(--surface)'
    css='mono selected-text' if selected else 'mono'
    body=f'<rect x=".5" y=".5" width="159" height="35" fill="{fill}" stroke="var(--accent)" stroke-opacity=".8"/>'
    body+=text(11,22,index,9,css)
    body+=f'<path d="M32 8V28" stroke="'+('var(--selected_text)' if selected else 'var(--border)')+'"/>'
    body+=text(43,23,label,11,css)
    body+=text(147,22,"›",15,css,'text-anchor="middle"')
    write("link-"+name,160,36,theme,label,"Open Daniel's "+label.lower()+".",body)


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in PALETTES:
        header(theme)
        stack(theme)
        intro(theme)
        intro(theme,mobile=True)
        divider(theme)
        footer(theme)
        section(theme,"loadout","01","TECHNICAL LOADOUT")
        section(theme,"telemetry","02","GITHUB TELEMETRY")
        section(theme,"contributions","03","CONTRIBUTION FIELD")
        portfolio(theme)
        for index,(name,label) in enumerate((("facebook","FACEBOOK"),("instagram","INSTAGRAM"),("linkedin","LINKEDIN"),("email","EMAIL")),2):
            button(theme,name,label,f"0{index}")
    print("Built 28 profile SVG sources; the header cube assembly and footer geometry loop every twelve seconds.")


if __name__=="__main__":
    main()
