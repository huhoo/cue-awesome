# Contributing (cue-awesome)

**[中文](CONTRIBUTING.md) · [English](CONTRIBUTING.en.md)**

Different people and different agent sessions add skills to this repo, so the rules live in files and CI — not in verbal agreement.

---

## 0. Three hard lines (violations are rejected outright)

### Public-face hygiene (hard pre-listing gate, added 2026-10-10)

**A published package is a finished product for users, not a construction log.** Five kinds of process telemetry are banned from every public face (`SKILL*.md`, `README*.md`, `assets/`, `references/`; CHANGELOG.md follows items 1/3/4/5):
1. ticket ids (M1xx, PR# and other internal serials);
2. dangling workspace paths (`verify/`, `logs/`, `dispatch/`, BOARD) - pointers inside a package must be package-relative and the target file must actually exist;
3. build-state language ("evidence ticket in transit", "awaiting the ledger", "pending Owner ruling");
4. internal timestamps ("not established as of 2026-xx-xx") - state the boundary itself ("this skill does not search academic databases"), not when it was measured;
5. provenance narration in product faces ("demand basis = the 311K-listed rival skill", "measured by M18x") - that belongs to internal accounts; the product states conclusions only (what it does, what it does not, what is authoritative - e.g. "audio/video: local short clips/slices supported, full-length video not; defer to the channel response").
Standard: capability sentences stated directly, links followable, attribution kept internal. Violations block publication, same tier as the wording red lines. **History is not rewritten** (trace-preservation): CHANGELOG entries added from this rule's effective date must comply; existing entries get cleaned when their file next takes a version slot - hygiene never burns a slot on its own. Product faces (SKILL/README/assets/references) are cleaned in full, not deferred.

**Remediation notes never reproduce banned wording (an extension of the five bans)**: when recording a cleanup, a correction, or a probe's key list, do not copy a banned phrase onto any public surface — including the CHANGELOG. Use a reference that cannot match (e.g. "the comparison phrases listed on that ticket"). The word list lives only in tickets and internal ledgers. A correction means a new entry stating that an earlier entry reproduced the wording and is now rewritten as a reference, with the facts preserved in that new entry and the internal ledger — it is not erasing history. "History is never rewritten" guards against false narratives; it never protects a red-line phrase left on a public page.


**Run the shipment, not the repo (last gate before listing, added 2026-10-12)**: every public sentence such as "ships with its own guard fixtures", "run `--selftest`" or "see `fixtures/…`" is a promise about the user's machine. **Green in the repository is not green in the artifact** - if the packaging exclusion list drops the sample directory, that capability sentence fails on the user's side. Three checks, run against the **unpacked artifact**: (1) every package-relative pointer made in a product face must actually exist inside the artifact; (2) if the artifact exposes a self-test entry point, it must be executed inside the unpacked copy and exit 0; (3) when the exclusion list conflicts with a capability claim, **trim the sample set - never delete the claim** (within the package size ceiling). Repo-level linters cannot see files missing from a zip, so these checks belong in a machine gate at the artifact layer, not in anyone's memory.


**Two inputs, two gates (wording settled, added 2026-10-12)**: one and the same pointer is judged by two different gates over two different inputs, **and the two verdicts may differ without either being a contradiction** -

- **The repository gate** asks whether a pointer in a product face exists **in the work tree**, and checks the five bans. A cross-package reference resolves here, so it passes.
- **The shipment gate** asks whether that same pointer exists **in the unpacked artifact**, plus a real run of the self-test entry, plus size measured in zip bytes. A pointer that resolves in the work tree but is absent from the artifact reads red there.

Two runnable commands, not pseudocode:

```bash
python3 scripts/check_public_hygiene.py            # repo: five bans plus pointer resolution across all product faces (exit 1 on ERROR)
python3 scripts/check_shipment.py --repo-scan .    # artifact side: build each zip per the packing recipe, unpack, run the three checks (a trimmed sample dir reads red - which is the point)
```

The fully-shipped verdict (samples included) runs once you have the zip from the release side, against either the unpacked directory or the zip itself:

```bash
unzip -q <pkg>.zip -d <unpacked-dir>
python3 scripts/check_shipment.py <unpacked-dir> --pkg <pkg>   # directory input: size is not judged, one WARN is recorded
python3 scripts/check_shipment.py <pkg>.zip                    # zip input: size is judged, in zip bytes
```

**Rule: whenever you report "passed / red / the nth one is green", name the input shape** (repository work tree vs unpacked artifact vs the copy downloaded back from the channel). When the two gates disagree, compare inputs before comparing verdicts, and **never relay one gate's green as the other gate's green**. Work-tree bytes, self-built zip bytes and channel-returned zip bytes are **three different measures and must not be quoted interchangeably** - the exclusion list and the compression shape both differ.

**One boundary: formats the channel refuses belong to the build exclusion list, and you must not smuggle a refused format into the package just to make a pointer resolve.** The fix is to rewrite that sentence as text, or point it at something the artifact genuinely carries - editing the exclusion list to talk the gate into green moves the promise somewhere the user cannot see.


1. **No secrets or personal data**: tokens, API keys, `.env`, private keys, internal domains, internal addresses, undesensitized client or natural-person information.
2. **No build artifacts**: `dist/`, `build/`, `*.zip`, `__pycache__/`, `*.pyc`.
3. **No fabricated sources**: every factual statement and external link must carry a verifiable source. If you cannot find one, leave it empty — never invent a URL.

Also: **do not `git add .`**. Run `git status` and look at each entry — that is how local artifacts get committed.

---

## 1. Repo structure

```
cue-awesome/
├── README.md / README.zh-CN.md      collection overview (English canonical)
├── CONTRIBUTING.md / .en.md         this file
├── LICENSE.md  NOTICE.md
├── docs/                            repo-level docs (i18n spec, …)
├── scripts/check_skills.py          repo-wide linter
├── .github/                         PR / issue templates + CI
└── <skill-name>/                    one directory per skill
```

**Rule: a top-level directory containing `SKILL.md` is a skill.** Adding a skill means adding a top-level directory — no registry to update. `docs/`, `scripts/` and `.github/` are not skills.

---

## 2. Adding a skill

Directory name = the `name` in frontmatter (lowercase, hyphenated, e.g. `competitive-brief`).

### Required files

| File | Purpose |
|---|---|
| `SKILL.md` | main instructions, must carry YAML frontmatter |
| `README.md` | for users: purpose, limits, onboarding, dependencies |

Optional: `scripts/`, `references/`, `assets/`, `examples/`, `CHANGELOG.md`, `manifest.yaml`, `README.en.md`.

### Frontmatter fields

| Field | Required | Notes |
|---|---|---|
| `name` | ✅ | **must equal the directory name** — the linter checks it |
| `description` | ✅ | purpose + trigger words. **Both Chinese and English entry points must be understandable** — but do not pad trigger words just to have English (reviewer ruling 2026-09-28: the `Triggers:` tail block is not mandatory; add real English keywords only when genuinely needed, each backed by in-package evidence, within the C-36 length cap). Where English coverage falls short, an honest README note like "name the skill directly" is acceptable |
| `version` | ✅ | `x.y.z`. **Top-level `version:` only** — a nested `metadata.version:` is a lint ERROR (flat parsers let the last line silently overwrite the real version; K-11 lesson) |
| `license` | recommended | MIT |
| `slug` / `displayName` / `summary` / `tags` / `metadata` | optional | for marketplace publishing; `agent_created: true` marks agent-generated skills |

Example trigger words (both languages):

```
Triggers: 竞品分析 / 竞品简报 / 这个市场要不要进; competitive analysis / competitor comparison / battlecard
```

### The four door questions (listing gate for new skills and renames, added 2026-10-09)

1. **Does the name carry value**: `displayName` must state "what it does for you + why to trust it" (example: `公告事件速读卡·关键数逐字带出处`);
2. **Is the blurb real**: `summary` ≤80 and `description` ≤300, lengths **measured by script** (wc -m style; no counting by hand);
3. **Any un-measured numbers**: names, blurbs and descriptions must not cite timings, hit-rates or growth figures no run has measured yet (allowed after measurement, with the ticket as source);
4. **Can it work on open**: the README's first section gives a verb-level first action (civil's door-frame standard), not an adjective pile.

---

## 3. Modifying an existing skill

- **Bump the version**: bug fix → patch (`0.1.0`→`0.1.1`); new capability or changed flow → minor (`0.1.0`→`0.2.0`); breaking refactors in the 0.x range also go minor.
- **Keep translations in sync**: the `version` in `SKILL.md` and `SKILL.zh-CN.md`, and in `README.md` and `README.en.md`, must match — the linter checks this.
- **CHANGELOG**: if the skill has one, its newest entry must equal the `SKILL.md` `version` (a mismatch is only a warning, but please align it).
- **Scripts**: everything under `scripts/` must run with `--help`; zero network requests by default (unless networking is the skill's purpose).
- **Bilingual rules** are in [`docs/i18n.md`](docs/i18n.md): extension-less = canonical, `.en` / `.zh-CN` = translation, edit one and you edit the other.
- **Replacing a release asset**: the target asset name in `gh release upload --clobber` comes from the uploaded file's basename — the file name must match the registered asset name exactly; a mis-named upload silently adds a junk asset while the old one stays live. After any replacement, re-download the asset and confirm its sha256 equals the local build — checking only the SKILL.md version line will not catch stale bytes being served. Delete any accidentally attached asset (`DELETE releases/assets/<id>`) before closing the task.

---

## 4. Commit convention

Conventional Commits, with the skill directory as scope:

```
<type>(<skill-name>): <short summary>

body: explain WHY, not WHAT (the diff already shows the what)
```

| type | use for |
|---|---|
| `feat` | new skill, new capability |
| `fix` | bug fix |
| `docs` | docs, README, specs |
| `i18n` | bilingual files |
| `refactor` | restructuring without behaviour change |
| `test` / `chore` | tests, misc |

Examples:

```
feat(competitive-brief): add source-credibility tiers to the evidence chain
fix(journal-draft): resolve image paths when invoked from another cwd
i18n(journal-draft): add English README
docs(repo): add contributing guide and skill linter
refactor(repo): move top-level content into subdirectories
```

Rules: **one commit per concern** — changes to two skills are two commits. Repo-wide changes use `repo` or omit the scope.

---

## 5. PR rules

**Branch names**: `skill/<name>` · `fix/<name>-<point>` · `docs/<topic>` · `i18n/<name>`

**PR title**: same format as a commit title (`type(scope): summary`).

**Checklist**:

- Ran `python scripts/check_skills.py` with **0 errors** (CI runs it too; red does not merge)
- New skill: one-line purpose, trigger words, dependencies, how to verify
- Changed skill: version bumped + CHANGELOG entry
- Bilingual files synced
- No secrets, no local absolute paths, no build artifacts
- **One skill per PR**; repo-wide changes get their own PR

**Merge**: squash merge, PR title becomes the final commit title; keep `main` linear (rebase, no merge commits).

---

## 6. Automated gates

```bash
python scripts/check_skills.py            # lint the whole repo
python scripts/check_skills.py --strict   # warnings fail too
```

Checks: directory name == `name` · `version` present and x.y.z · `description`/`summary` non-empty · README present · bilingual pairs complete with matching frontmatter · CHANGELOG version aligned · no nested `.git` · no secret files · no build artifacts.

CI: `.github/workflows/skill-lint.yml` runs on every push / PR (errors fail, warnings only report).

---

## 7. What does not belong here

- A directory of ideas with no `SKILL.md` (open an issue proposal first)
- Secrets, tokens, personal data, internal domains
- Fabricated source links, undesensitized client or personal information (see `journal-draft/NOTICE.md` for the desensitization pattern)
- Straight copies of other people's skills (if adapted, state the source and license)

> **The template itself must pass the gate** (reported by 4.1 after testing): phrasing like "the word list lives only in tickets and internal ledgers" re-triggers the scan — both English and Chinese forms of that process word are in the banned-work-status list. Working substitutes: refer to a removed clause as "that clause described a third party's data-source requirements", and describe the key list as living only in internal reconciliation records. (This file keeps 5 self-scan findings because the rule definitions must cite the banned patterns themselves — a known exception, escalated separately. This commit also corrects an earlier one: its message cited a nonexistent hash prefix "9f0…" for the previous commit, which is actually `def3c78` — an identifier written without assertion.)