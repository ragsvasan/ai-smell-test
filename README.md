# ai-smell-test

**An explainable prose-quality lens that runs on your own machine.** It shows you *which phrases* in your writing read as machine-generated, and *why* — so you can fix them.

Not "is this AI" — **"where does my writing sound like a machine, and why?"**

Two modalities, one corpus:
- **Web SPA** — interactive, highlights flagged spans inline
- **CLI** (`lint.py`) — headless, pipeable, JSON output for chaining

## What this is — and isn't

It is **not a detector** and **not a humanizer**. Those are different jobs, and this tool is deliberately neither:

| | What it does | This tool |
|---|---|---|
| **Detectors** (GPTZero, Grammarly's detector) | Output a probability verdict — "98% AI" | ✗ — gives no verdict, no score |
| **Humanizers** (Grubby, Dripwriter, Duey, Typeflo, Comet) | Rewrite text to *evade* detectors | ✗ — never rewrites for you |
| **ai-smell-test** | Surface span-level evidence with a reason, for a human to act on | ✓ |

**Why it's built this way:**

- **Explainable, not a black box.** A detector tells a student "98% AI" with no recourse. This shows the *evidence* — every flagged span, the rule that caught it, and why — and leaves the judgment to you.
- **Local, private, free, no account.** Paste a draft; nothing leaves your machine. Every SaaS competitor ingests your text. If you can't paste a confidential draft into a website, this is the point.
- **For writers who want to sound less like a machine** — to write *better*, not to cheat a detector. Same person who'd hire an editor; opposite intent from a humanizer user.
- **Transparent, forkable rules.** The entire detection logic is `corpus.json` + `rules.json` — auditable and editable. No competitor lets you see, let alone tune, theirs.

**What it deliberately does not try to do:** win a detection-accuracy benchmark, or beat "humanizer" tools. Both are adversarial arms races against a published ruleset, and a transparent open-source tool can't win them. Its lane is human-in-the-loop revision, which doesn't overlap with the evasion race at all.

**Philosophy:** signals, not verdicts. Lexical density matters more than presence. A single "moreover" in a 2000-word essay is noise; fifteen corpus hits in 300 words is a cluster worth examining. Good human writers trigger some rules.

> ⚠️ The static ruleset decays as model output styles shift. What keeps it useful is the community-editable corpus — PRs to `corpus.json` and `rules.json` are the lifeblood, not a benchmark score.

---

## Corpus

Excess-vocabulary word list from [Kobak et al. 2025, *Science Advances*](https://www.science.org/doi/10.1126/sciadv.adq5686) — words statistically overrepresented in AI-assisted text vs. pre-2022 human baseline. Style-only terms; common stopwords removed. Stored in `corpus.json` — edit freely to tune for your domain.

## Rules

Six structural rules in `rules.json`:

| Rule | Severity | What it catches |
|---|---|---|
| Meta-Announcement | severe | Throat-clearing openers ("it is important to note that", "let's dive in") |
| Grandiosity Puffery | severe | Scope inflation ("transformative", "groundbreaking", "paradigm shift") |
| PNAS Corpus Markers | structural | LLM padding terms ("robust", "leverage", "facilitate", "nuanced") |
| Formulaic Transition | structural | Sentence-opening connectives ("Furthermore,", "Moreover,", "In conclusion,") |
| Hedge Stack | structural | Doubled qualifiers ("may potentially", "could possibly") |
| Symmetrical Contrast | structural | Manufactured binary framing ("not just X, but also Y") |

Plus two paragraph-level signals:
- **Flat rhythm** — sentence-length std dev below 3.8 (labeled "softest signal"; can be human style)
- **Repeated opener** — consecutive sentences starting with the same word

---

## Web SPA

```bash
./start.sh        # serves on http://localhost:3131
./stop.sh
```

Paste or upload a draft. Flagged spans are highlighted inline. Navigate between paragraphs with `j`/`k`. Lexical density (`flags per 1000 words`) is shown in the header.

---

## CLI

Requires Python 3.10+. No dependencies beyond the standard library.

```bash
# Lint a file
python3 lint.py draft.md

# From stdin
cat draft.md | python3 lint.py

# JSON output (for chaining / scripting)
python3 lint.py --json draft.md
```

### Output format

```
19 flags across 3 paragraphs · 79 words
lexical density: 227.8/1000w — high — strong signal
  ● 7 severe
  ● 11 structural / corpus
  ...

¶1
  [SEV] Meta-Announcement: "It is important to note that" — AI throat clearing. ...
  [STR] PNAS Corpus Markers: "leverages" — High-probability LLM padding term ...
  [STR] Corpus (Kobak et al. 2025): "integration" — Overrepresented in AI-assisted text ...
```

Finding codes: `[SEV]` severe · `[STR]` structural/corpus · `[RHY]` flat rhythm · `[RPT]` repeated opener

### Density thresholds

| Density | Label |
|---|---|
| < 3 / 1000w | within human baseline |
| 3–8 / 1000w | moderate — examine clusters |
| > 8 / 1000w | high — strong signal |

---

## Claude Code skill

Use `/ai-smell-test` as a slash command inside any Claude Code session.

**Install:**

```bash
# 1. Clone the repo (lint.py, corpus.json, rules.json live here)
git clone https://github.com/ragsvasan/ai-smell-test ~/ai-smell-test

# 2. Install the skill globally (skills must be a directory with SKILL.md inside)
mkdir -p ~/.claude/skills/ai-smell-test
curl -fsSL https://raw.githubusercontent.com/ragsvasan/ai-smell-test/main/.claude/skills/ai-smell-test/SKILL.md \
  -o ~/.claude/skills/ai-smell-test/SKILL.md
```

Then in any Claude Code session:
```
/ai-smell-test path/to/draft.md
/ai-smell-test --html draft.md    # annotated HTML export to send to a writer
/ai-smell-test --json draft.md    # structured JSON for scripting
```

---

## Extending

**Add corpus words:** edit `corpus.json` → add to the `words` array. Both the web SPA and CLI pick up changes on reload/next run.

**Add rules:** edit `rules.json` → add an object with `id`, `name`, `severity` (`severe` or `structural`), `pattern` (JS-compatible regex string), `flags`, and `message`. The same file drives both modalities.

---

## License

MIT — see [LICENSE](LICENSE).
