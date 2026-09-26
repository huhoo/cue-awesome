# competitive-brief

**[中文](README.md) · [English](README.en.md)**

Run a competitive analysis around one decision question, and ship a brief backed by an evidence chain.

```
+brief "Should we enter the compliance-tool market for North American small and mid-size law firms"
  → define the decision, who to compare, and how deep to go
  → omni-reader collects the material, cue-research deep-researches and cross-verifies
  → every claim is labeled fact / inference / opinion
  → delivered: conclusion + traceability + what you still need to confirm yourself
```

## In one sentence

The core is not the process — it's the **evidence table**. Every substantive claim goes into the evidence table before it reaches the brief. If a dimension can't be filled in the table, it doesn't appear in the brief.

## Full spec

[`SKILL.md`](SKILL.md) — evidence table definition, constraints, brief rendering rules.

## Live example

[`examples/competitive-test/`](examples/competitive-test/) — a 5-person team evaluating alternatives to Cursor:
- [Evidence table](examples/competitive-test/evidence-table.md) (23 rows, 87% fact)
- [Brief](examples/competitive-test/brief.md)

Sources verified via omni-reader parsing cursor.com/pricing, claude.com/pricing, and GitHub READMEs.

## Dependencies (recommended)

- `cue-omni-reader`: parse web pages / PDFs / audio / video → extract text into evidence table
- `cue-research`: cross-verify, deep research

Both are free. The skill still runs without them, with reduced capability.

## Version

The `SKILL.md` frontmatter `version` is the single source of truth; see [`CHANGELOG.md`](CHANGELOG.md) for history.
