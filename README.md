# ai-smell-test

A prose linter that flags writing patterns statistically overrepresented in AI-generated text.

Two modalities, one corpus:
- **Web SPA** — interactive, highlights flagged spans inline
- **CLI** (`lint.py`) — headless, pipeable, JSON output for chaining

**Philosophy:** signals, not verdicts. Lexical density matters more than presence. A single "moreover" in a 2000-word essay is noise; fifteen corpus hits in 300 words is a cluster worth examining. Good human writers trigger some rules.

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
# 1. Clone the repo
git clone https://github.com/ragsvasan/ai-smell-test ~/ai-smell-test

# 2. Install the skill globally
curl -fsSL https://raw.githubusercontent.com/ragsvasan/ai-smell-test/main/.claude/skills/ai-smell-test.md \
  -o ~/.claude/skills/ai-smell-test.md
```

Then in any Claude Code session:
```
/ai-smell-test path/to/draft.md
```

---

## Extending

**Add corpus words:** edit `corpus.json` → add to the `words` array. Both the web SPA and CLI pick up changes on reload/next run.

**Add rules:** edit `rules.json` → add an object with `id`, `name`, `severity` (`severe` or `structural`), `pattern` (JS-compatible regex string), `flags`, and `message`. The same file drives both modalities.

---

## License

MIT — see [LICENSE](LICENSE).
