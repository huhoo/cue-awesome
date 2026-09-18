# Contributing (cue-awesome)

**[中文](CONTRIBUTING.md) · [English](CONTRIBUTING.en.md)**

Different people and different agent sessions add skills to this repo, so the rules live in files and CI — not in verbal agreement.

---

## 0. Three hard lines (violations are rejected outright)

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
| `README.md` | for humans: purpose, limits, onboarding, dependencies |

Optional: `scripts/`, `references/`, `assets/`, `examples/`, `CHANGELOG.md`, `manifest.yaml`, `README.en.md`.

### Frontmatter fields

| Field | Required | Notes |
|---|---|---|
| `name` | ✅ | **must equal the directory name** — the linter checks it |
| `description` | ✅ | purpose + trigger words. **Write trigger words in both Chinese and English** — with Chinese-only triggers, English users can never trigger the skill |
| `version` | ✅ | `x.y.z`. Either top-level `version:` or `metadata.version:`, **not both and not inconsistent** |
| `license` | recommended | MIT |
| `slug` / `displayName` / `summary` / `tags` / `metadata` | optional | for marketplace publishing; `agent_created: true` marks agent-generated skills |

Example trigger words (both languages):

```
Triggers: 竞品分析 / 竞品简报 / 这个市场要不要进; competitive analysis / competitor comparison / battlecard
```

---

## 3. Modifying an existing skill

- **Bump the version**: bug fix → patch (`0.1.0`→`0.1.1`); new capability or changed flow → minor (`0.1.0`→`0.2.0`); breaking refactors in the 0.x range also go minor.
- **Keep translations in sync**: the `version` in `SKILL.md` and `SKILL.zh-CN.md`, and in `README.md` and `README.en.md`, must match — the linter checks this.
- **CHANGELOG**: if the skill has one, its newest entry must equal the `SKILL.md` `version` (a mismatch is only a warning, but please align it).
- **Scripts**: everything under `scripts/` must run with `--help`; zero network requests by default (unless networking is the skill's purpose).
- **Bilingual rules** are in [`docs/i18n.md`](docs/i18n.md): extension-less = canonical, `.en` / `.zh-CN` = translation, edit one and you edit the other.

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
