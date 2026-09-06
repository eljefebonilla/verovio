---
agent: codex-gpt-6-astra
date: 2026-09-05
source-session: NA
---

# Glow Chant

Glow Chant is derived from Sebastian 1.350 (OFL, by Florian Kretlow and Ben
Byram-Wigfield). It is a Modified Version, converted and subset for Verovio by
Parish Glow, 2026. It is an optional font, not a change to the engine default.
The family is **Glow Chant**, resource id **GlowChant**, and PostScript name
**GlowChant-Regular**. The original reserved name is retained only in source
attribution and the original license notice, never in font name fields.

`provenance.json` records the upstream commit, exact source URLs and hashes.
`OFL.txt` carries the complete original notice/license and the derivative line.
Both are also included in `data/GlowChant/`, which the Emscripten build embeds.
Applications distributing the module must also preserve its accessible notice.

Regenerate this font only, from the engine root:

```sh
python3 fonts/generate_glow_chant.py
```

Dependencies: fontTools 4.60.2 and Brotli 1.2.0. An isolated environment may use
`fonts/GlowChant/requirements.txt`. No FontForge or svgpathtools is required.
The targeted script implements the existing SVG path / bounding-box / embedded
CSS resource format with fontTools SVGPathPen, BoundsPen and WOFF2 subsetting.
It leaves all other fonts and shared SMuFL definitions untouched. The renamed
complete OTF is the reproducible source; CSS contains a supported-glyph subset.
The CSS family `GlowChant` is the engine's resource alias for Glow Chant.

For an initial import only, `--source-dir <directory>` accepts the three original
upstream files specified in the script's exact hash guards. Those originals are
not added to this source tree. Font name/CFF fields are renamed before saving.
Three upstream null optional bounding-box entries are omitted from the derived
metadata and disclosed in provenance. All rendered glyph bounds are computed
from the actual outlines; anchors use the existing two-decimal resource format.

`data/GlowChant/coverage.json` discloses direct coverage: 412 of 650 supported
codepoints. Missing glyphs use the existing engine fallback. In particular, this
does not claim complete square-chant or mensural coverage. Modern slurs, lyric
connectors and the opt-in short breath tick are drawn by the engine, not selected
from the similarly named chant glyphs.

The old-font preservation proof compares existing resource bytes, and separately
renders each accepted font with identical inputs/options. A controlled-version
module is for parity tests only. Distribute only the real source-version build.
