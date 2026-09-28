# Quote input: lower the extraction burden

The host still extracts semantics. `prepare` only binds exact quotes to evidence and copies supplied text; it never parses a URL, calls a model or proves support.

Start with [quote-draft.json](../assets/demo/quote-draft.json). All entities, definitions, scopes and assertion fields follow [knowledge-contract.md](knowledge-contract.md). Assertion `claim_kind` defaults to `reported` during `prepare`; any explicit other value is rejected. Source `sha256` may be omitted; the tool calculates it. Supplied hashes must match. Replace each evidence locator with:

```json
{"source_id":"source:r1","quote":"Exact parsed text, including whitespace.","role":"value_and_scope"}
```

The quote must occur exactly once. If repeated, include more context or add `"occurrence": 2` (1-based). Do not select an arbitrary occurrence merely to make validation pass. Unicode offsets are computed in UTF-8 bytes. Actual source page spans are reused only when they contain the entire quote; otherwise a text-range locator is emitted. Declared page/range overrides cannot disagree with the match.

```sh
python3 scripts/ontology.py prepare assets/demo/quote-draft.json --out /path/to/work/prepared
python3 scripts/ontology.py build /path/to/work/prepared/input.json --out /path/to/work/v1
```

`prepare` creates a new directory with `input.json` and immutable text copies. It preserves source metadata, validates the full schema and rejects traversal, changed hashes, missing/ambiguous quotes and injected review acceptance. It never overwrites an output directory.

For a financial table include separate evidence for row, unit/period headers and relevant footnotes. The shortest unique string is not always enough semantic evidence. Prefer precise rows plus headers over quoting a whole report. `query --with-evidence` and briefs return up to 400 characters per evidence range; `truncated: true` means consult the complete snapshot before relying on omitted qualifiers.
