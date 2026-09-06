---
agent: codex-gpt-6-astra
date: 2026-09-06
source-session: NA
---

# MusicXML importer regression fixtures

Run from the engine root with the built ESM module and matching toolkit wrapper:

```sh
node tools/test-musicxml-importer.mjs --module /absolute/module.mjs --wrapper /absolute/verovio.mjs
```

`--output /absolute/report.json` saves the measured result. `--expect-baseline`
requires the voice-switch and pitch-alter fixtures to fail and the cross-staff
fixture to pass, for reproducing the original importer defects.

The fixtures check a voice change without backup and the next measure's onset;
explicit and omitted alter values, across voices/octaves and within one voice;
same-voice cross-staff chord/container preservation; and the supported ±0.5 and
±1.5 gestural accidental mappings. Written accidentals remain visual data and
ordinary sounding pitch uses alter, defaulting to zero. Numeric voice handling
is unchanged. The measure-local written-glyph compatibility cache is scoped by
source pitch name, source octave and voice; key-signature defaults are separate.

This does not certify arbitrary decimal alterations or custom tuning. The
existing converter cannot represent every decimal and warns for unsupported
values. Explicit custom-tuning glyph precedence remains compatible with the
existing engine. Carried glyphs are reused only for a known matching sounding
alteration. Existing key-signature octave-specific metadata behavior is outside
these two fixes. No tempo interpretation is changed.
