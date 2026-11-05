Original NieR-inspired profile artwork using Daniel's branding-v1 grayscale / chrome
palette. Daniel Camacho remains the primary header title, with D-16 only at the side.
Header wording stays fixed while six triangular faces assemble into an isometric
cube, hold, and unfold. Section headings have their own centered bracket design;
the separate dividers keep their lines still and pulse slowly at the center. The footer
uses concentric diamonds and segmented rings, without repeated identity labels.

The introduction is a dedicated SVG panel with desktop and mobile compositions, a
square perimeter, corner registration brackets and a personal-record tab. It retains
Daniel's complete original paragraph and its emphasis. The technical loadout
uses taller rows and preserved SVG whitespace for visible gaps between technologies.
The footer has a taller canvas so its caption and animated geometry have room.

The layout uses a 900px canvas. Telemetry is one self-contained SVG containing two
444px cards separated by a 12px gutter, so its outer edges exactly match the full-width
footer. Source cards are embedded as SVG elements, with isolated IDs and no external
image requests. Rank text is centered on the actual ring coordinates.

The README embeds GIFs for header / divider / footer / contributions and static SVGs
for the introduction, centered headings, technical stack, buttons and telemetry. The
header cube assembly and footer geometry loop every twelve seconds, with slow footer
pulses. BUILD. LEARN. ITERATE. does not
blink, type or fade. The source SVGs retain reduced-motion behavior.

Rebuild decorative SVGs with Python's standard library:

```sh
python .github/scripts/build_readme_assets.py
```

Re-export GIFs with the optional authoring dependencies:

```sh
python -m pip install pillow playwright
python -m playwright install chromium
python .github/scripts/render_readme_gifs.py
```

Automatic telemetry refresh
---------------------------

After publishing, Generate Assets runs at 00:00 and 12:00 UTC (08:00 and 20:00 Manila)
and supports manual runs. It downloads fresh stats and streak cards, normalizes their
colors / geometry, and rebuilds both full-width telemetry variants. It updates exactly
six generated SVGs on the default branch: four source cards and the two displayed pairs.
Unchanged images create no commit. API error artwork is rejected, cached metrics provide
an outage fallback, concurrency is serialized, and pushes never force.

This scheduled update is configured for the requested automatic daily telemetry.
The workflow uses the repository's existing Actions write permission; branch rules must
permit those generated image updates.

Contribution snapshot
---------------------

The existing workflow still publishes fresh contribution SVGs to the output branch.
The README's contribution GIF is a local snapshot with its complete loop and without
the unrelated bottom progress strip. Refresh the snapshot separately when desired:

```sh
python .github/scripts/bundle_activity.py --published
python .github/scripts/render_readme_gifs.py --scene activity
```

The contribution canvas is calculated from the grid's actual cell bounds. The current
900×164 snapshot has exactly 28px between the fixed grid and each of the four edges;
the snake retains its original motion inside that centered coordinate system.

Refresh only local telemetry source cards and displayed pairs from the output branch:

```sh
python .github/scripts/bundle_activity.py --published --stats-only
```

The inspiration folder stays ignored. None of the reference README's artwork or game
assets is copied.

Every README item uses a centered div wrapper without paragraph margins, including
all three dividers, the portfolio link and the badge row. Only the normal image
baseline gap remains between adjacent blocks for a compact, consistent layout.
Contribution GIFs are sampled at 20fps (50ms frames), preserving the original
71.7-second loop and centered grid while reducing visible stepping.
