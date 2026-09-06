---
agent: codex-gpt-6-astra
date: 2026-09-06
source-session: NA
---

# Direct MusicXML sound tempos

The eight original fixtures are retained byte-for-byte from the Row20a receipt.
They isolate direct measure-child tempo import, initial first-position behavior,
direction-wrapped nonduplication, and the separate whole-measure tempo limitation.
Three additional negative controls contain no direct tempo sounds: initial92 is
wrapped in a direction, and the later direct sound is removed where applicable.
The direction120 control, metronome50 control and tempo-free control retain their
raw input bytes for baseline/candidate comparison.

Run from the engine root:

```sh
node tools/test-musicxml-sound-tempo.mjs --module /absolute/module.mjs --wrapper /absolute/verovio.mjs --output /absolute/results
```

First run the baseline with `--expect-baseline`. Pass its results to the candidate
with `--baseline-output /absolute/baseline-results`. The runner compares exact raw
`getMEI({ignoreHeader:true})` bytes and raw timemap JSON for the true negative
controls. No IDs, music attributes or timemap values are removed or rewritten.
Full MEI is also retained and hashed; its generated date/version header differs.

The imported direct Tempo has midi.bpm and a cursor-derived tstamp, with no text
or metronome children to print. The existing initial scoreDef shortcut retains
its exact first-part/first-positional-measure event; the same event is not added
again. Direction sound, tuning and navigation continue through their old routes.

This fixes only omitted direct-sound import. A beat4 tempo still affects the whole
measure in the existing timemap mechanism, and the last tempo declaration still
wins within that mechanism. Conflicting simultaneous source values remain a
source-policy question. Neither is resolved or silently accepted by this test.
