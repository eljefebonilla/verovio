#!/usr/bin/env python3
"""Generate only Glow Chant resources with fontTools (no FontForge dependency)."""
import argparse
import base64
import hashlib
import io
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts/GlowChant"
DATA = ROOT / "data"
FAMILY = "Glow Chant"
PS_NAME = "GlowChant-Regular"
DERIVATION = "Glow Chant, a Modified Version under the OFL, converted and subset for Verovio by Parish Glow, 2026"
COPYRIGHT = "Copyright (c) 2021, Florian Kretlow and Ben Byram-Wigfield. " + DERIVATION
PINS = {
    "OFL.txt": "eae3dd8a95b13bed17e147ab40b2411ac693d9c7a74b284c03e1bdbb530b55b0",
    "Sebastian.otf": "0b4a3b12ce575ccd19650be4810ffb292679226ddf472de5aaf44cf06129d347",
    "Sebastian.json": "afc32e693f2ed12b8e68277b9101b598f77f76bf035c1581e4dbacf5bad0d270",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def check_names(font):
    for name in font["name"].names:
        assert "sebastian" not in name.toUnicode().lower(), name.toUnicode()
    top = font["CFF "].cff.topDictIndex[0]
    assert font["CFF "].cff.fontNames == [PS_NAME]
    for key in ("FamilyName", "FullName", "Copyright", "Notice", "Weight"):
        assert "sebastian" not in str(getattr(top, key, "")).lower(), key
    assert top.FamilyName == FAMILY


def bootstrap(source):
    """Rename the complete pinned source; original bytes remain outside this tree."""
    for name, expected in PINS.items():
        assert sha((source / name).read_bytes()) == expected, name
    font = TTFont(source / "Sebastian.otf", recalcTimestamp=False)
    names = {0: COPYRIGHT, 1: FAMILY, 2: "Regular", 3: "GlowChant-Regular;1.350;ParishGlow2026",
             4: FAMILY + " Regular", 6: PS_NAME, 16: FAMILY, 17: "Regular"}
    for row in font["name"].names:
        if row.nameID in names:
            row.string = names[row.nameID].encode(row.getEncoding())
    for nid in (16, 17):
        font["name"].setName(names[nid], nid, 3, 1, 0x409)
    cff = font["CFF "].cff
    cff.fontNames = [PS_NAME]
    top = cff.topDictIndex[0]
    top.FamilyName, top.FullName, top.Copyright = FAMILY, FAMILY + " Regular", COPYRIGHT
    if hasattr(top, "Notice"):
        top.Notice = COPYRIGHT
    check_names(font)
    font.save(FONT / "GlowChant.otf")
    meta = json.loads((source / "Sebastian.json").read_text())
    meta["fontName"] = FAMILY
    # Upstream uses null for three unavailable boxes; omit those optional entries.
    meta["glyphBBoxes"] = {k: v for k, v in meta["glyphBBoxes"].items() if v is not None}
    write_json(FONT / "glowchant_metadata.json", meta)
    (FONT / "OFL.txt").write_bytes((source / "OFL.txt").read_bytes() + ("\n" + DERIVATION + "\n").encode())
    write_json(FONT / "provenance.json", {
        "family": FAMILY, "resourceId": "GlowChant", "postScriptName": PS_NAME,
        "version": "1.350", "derivation": DERIVATION,
        "sourceRepository": "https://github.com/fkretlow/sebastian",
        "sourceCommit": "cb6a92e73476b1d009dcf7b941549b74e151252d",
        "sourceFiles": [{"sha256": h, "url": "https://github.com/fkretlow/sebastian/blob/cb6a92e73476b1d009dcf7b941549b74e151252d/fonts/" + n} for n, h in PINS.items()],
        "renamedFontSha256": sha((FONT / "GlowChant.otf").read_bytes()),
        "licenseSha256": sha((FONT / "OFL.txt").read_bytes()),
        "metadataOmittedNullBoxes": ["dynamicCombinedSeparatorSpace", "arrowBlackDownRight", "noteheadNull"],
        "generator": "fontTools 4.60.2; Brotli 1.2.0; generate_glow_chant.py",
    })


def numeric_metadata(meta):
    for name, width in meta.get("glyphAdvanceWidths", {}).items():
        assert isinstance(width, (int, float)) and math.isfinite(width), name
    for section in ("glyphBBoxes", "glyphsWithAnchors"):
        for name, points in meta[section].items():
            for key, value in points.items():
                assert len(value) == 2 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in value), (name, key)


def generate():
    font = TTFont(FONT / "GlowChant.otf", recalcTimestamp=False)
    check_names(font)
    meta = json.loads((FONT / "glowchant_metadata.json").read_text())
    assert meta["fontName"] == FAMILY
    numeric_metadata(meta)
    provenance = json.loads((FONT / "provenance.json").read_text())
    assert sha((FONT / "GlowChant.otf").read_bytes()) == provenance["renamedFontSha256"]
    assert sha((FONT / "OFL.txt").read_bytes()) == provenance["licenseSha256"]
    supported = {int(g.get("glyph-code"), 16): g.get("smufl-name") for g in ET.parse(ROOT / "fonts/supported.xml").findall(".//glyph")}
    cmap, glyphs, units = font.getBestCmap(), font.getGlyphSet(), font["head"].unitsPerEm
    present = {c: cmap[c] for c in sorted(supported) if c in cmap}
    resource = DATA / "GlowChant"
    resource.mkdir(parents=True, exist_ok=True)
    bounds = ET.Element("bounding-boxes", {"font-family": FAMILY, "units-per-em": str(units)})
    svg = ET.Element("svg", {"xmlns": "http://www.w3.org/2000/svg"})
    ET.SubElement(svg, "metadata").text = COPYRIGHT + "; SIL Open Font License 1.1; see OFL.txt"
    full = ET.SubElement(ET.SubElement(svg, "defs"), "font", {"id": PS_NAME, "horiz-adv-x": "0"})
    ET.SubElement(full, "font-face", {"font-family": FAMILY, "units-per-em": str(units), "font-style": "normal"})
    paths = {}
    for code, name in sorted(cmap.items()):
        if code < 32 and code not in (9, 10, 13):
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        path = pen.getCommands()
        paths[code] = path
        ET.SubElement(full, "glyph", {"glyph-name": "space" if code == 32 else f"uni{code:04X}",
                      "unicode": chr(code), "horiz-adv-x": str(glyphs[name].width), "d": path})
    ET.ElementTree(svg).write(FONT / "GlowChant.svg", encoding="utf-8", xml_declaration=True)
    for code, name in present.items():
        label = f"{code:04X}"
        group = ET.Element("g", {"id": label})
        if paths[code]:
            ET.SubElement(group, "path", {"transform": "scale(1,-1)", "d": paths[code]})
        ET.ElementTree(group).write(resource / (label + ".xml"), encoding="utf-8")
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        x0, y0, x1, y1 = pen.bounds or (0, 0, 0, 0)
        row = ET.SubElement(bounds, "g", {"c": label, "n": supported[code], "x": str(round(x0, 2)), "y": str(round(y0, 2)),
                          "w": str(round(x1-x0, 2)), "h": str(round(y1-y0, 2)), "h-a-x": str(glyphs[name].width)})
        for anchor, (x, y) in meta["glyphsWithAnchors"].get(supported[code], {}).items():
            ET.SubElement(row, "a", {"n": anchor, "x": str(round(x, 2)), "y": str(round(y, 2))})
    ET.indent(bounds)
    ET.ElementTree(bounds).write(DATA / "GlowChant.xml", encoding="utf-8", xml_declaration=True)
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.recalc_timestamp = False
    options.canonical_order = True
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=present)
    worker.subset(font)
    check_names(font)
    font.flavor = "woff2"
    output = io.BytesIO()
    font.save(output)
    woff = output.getvalue()
    check_names(TTFont(io.BytesIO(woff)))
    # GlowChant is Verovio's resource alias; the actual font family remains Glow Chant.
    css = "/* " + COPYRIGHT + " */\n@font-face {\n  font-family: 'GlowChant';\n  src: url(data:application/font-woff2;charset=utf-8;base64," + base64.b64encode(woff).decode() + ") format('woff2');\n  font-weight: normal;\n  font-style: normal;\n}\n"
    (DATA / "GlowChant.css").write_text(css)
    (resource / "OFL.txt").write_bytes((FONT / "OFL.txt").read_bytes())
    (resource / "provenance.json").write_bytes((FONT / "provenance.json").read_bytes())
    report = {"family": FAMILY, "resourceId": "GlowChant", "unitsPerEm": units,
              "supported": len(supported), "present": len(present), "missing": [{"code": f"{c:04X}", "name": supported[c]} for c in sorted(supported.keys()-present.keys())],
              "woff2Sha256": sha(woff), "metadataValidated": True, "reservedNameAbsentFromFontNames": True,
              "boundary": "Missing glyphs use the existing fallback. Slurs, lyric connectors and modern tick barlines are engine geometry, not these glyphs."}
    write_json(resource / "coverage.json", report)
    print(f"PASS GlowChant resources={len(present)}/{len(supported)} family={FAMILY} missing={len(report['missing'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Optional initial import of the three hash-pinned upstream receipt files")
    args = parser.parse_args()
    FONT.mkdir(parents=True, exist_ok=True)
    if args.source_dir:
        bootstrap(args.source_dir)
    generate()
