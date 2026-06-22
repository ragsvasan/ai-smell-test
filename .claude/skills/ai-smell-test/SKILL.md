# Skill: ai-smell-test

Lint prose for AI-writing patterns using the prose linter.

## How to invoke

`/ai-smell-test [flags] [file-path or inline text]`

Examples:
- `/ai-smell-test draft.md` — lint a file, terminal output
- `/ai-smell-test` — you will paste text, then Claude lints it
- `/ai-smell-test --json draft.md` — JSON output for further processing / chaining
- `/ai-smell-test --html draft.md` — produce a self-contained annotated HTML file to send to a writer

## What you do

1. If the user provided a file path, run:
   ```
   python3 <repo-root>/lint.py [flags] <file-path>
   ```
   where `<repo-root>` is the directory containing `lint.py` (same dir as `corpus.json` and `rules.json`).

2. If the user provided inline text (no file path), write it to a temp file and run lint.py on it, then delete the temp file.

3. If no argument at all, ask the user to paste the text they want linted, then proceed as in step 2.

4. Print the output verbatim. Do not summarise, reword, or editorialize the findings — the linter output is the response.

5. After the output, offer one optional follow-up:
   - If there were findings: "Want me to rewrite any of the flagged paragraphs?" or "Want an annotated HTML export to send to the writer? (`--html`)"
   - If the text is clean: say nothing extra.

## Flags

| Flag | Output |
|------|--------|
| *(none)* | Human-readable terminal text |
| `--json` | Structured JSON — use for chaining into other tools or scripts |
| `--html` | Self-contained HTML file with hover tooltips on flagged spans + findings list at the bottom. No CDN — renders offline and in email clients. Save with `> annotated-review.html` or pipe to a file. |

## Finding codes

Density-feeding (lexical):
- `[SEV]` — severe: strong AI signal (throat-clearing, grandiosity puffery)
- `[STR]` — structural / corpus: LLM padding terms or Kobak et al. 2025 excess-vocabulary words
- `[CRP]` — corpus-only hit: single word from the Kobak et al. 2025 excess-vocabulary list

Soft signals (flagged but **excluded from lexical density** — good human writers trip these):
- `[SFT]` — structural shape: "from X to Y" sweep, "not about X, it's about Y" antithesis, formulaic wrap-up openers
- `[PUN]` — paragraph-length uniformity: paragraph word-counts suspiciously even (document-level)
- `[RHY]` — flat rhythm: sentence-length std dev below 3.8 (softest signal — can be human style)
- `[RPT]` — repeated sentence opener

## Density thresholds

| Lexical density | Label |
|-----------------|-------|
| < 3 / 1000w | within human baseline |
| 3–8 / 1000w | moderate — examine clusters |
| > 8 / 1000w | high — strong signal |

## Installing globally

To use this skill in any project (not just this repo), copy the skill file:

```bash
cp .claude/skills/ai-smell-test.md ~/.claude/skills/ai-smell-test.md
```

Or fetch directly:

```bash
curl -fsSL https://raw.githubusercontent.com/ragsvasan/ai-smell-test/main/.claude/skills/ai-smell-test.md \
  -o ~/.claude/skills/ai-smell-test.md
```

You also need `lint.py`, `corpus.json`, and `rules.json` somewhere accessible. Clone the repo and point to it:

```bash
git clone https://github.com/ragsvasan/ai-smell-test ~/ai-smell-test
```

Then edit the skill file to set `<repo-root>` to `~/ai-smell-test`.
