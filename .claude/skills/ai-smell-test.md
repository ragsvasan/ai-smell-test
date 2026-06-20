# Skill: ai-smell-test

Lint prose for AI-writing patterns using the prose linter.

## How to invoke

`/ai-smell-test [file-path or inline text]`

Examples:
- `/ai-smell-test draft.md` — lint a file
- `/ai-smell-test` — you will paste text, then Claude lints it
- `/ai-smell-test --json draft.md` — JSON output for further processing

## What you do

1. If the user provided a file path, run:
   ```
   python3 <repo-root>/lint.py <file-path>
   ```
   where `<repo-root>` is the directory containing `lint.py` (same dir as `corpus.json` and `rules.json`).

2. If the user provided inline text (no file path), write it to a temp file and run lint.py on it, then delete the temp file.

3. If no argument at all, ask the user to paste the text they want linted, then proceed as in step 2.

4. Print the output verbatim. Do not summarise, reword, or editorialize the findings — the linter output is the response.

5. After the output, offer one optional follow-up: "Want me to rewrite any of the flagged paragraphs?" — but only if there were findings. If the text is clean, say nothing extra.

## Finding codes

- `[SEV]` — severe: strong AI signal (throat-clearing, grandiosity puffery)
- `[STR]` — structural / corpus: LLM padding terms or Kobak et al. 2025 excess-vocabulary words
- `[RHY]` — flat rhythm: sentence-length std dev below 3.8 (softest signal — can be human style)
- `[RPT]` — repeated sentence opener

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

You also need `lint.py`, `corpus.json`, and `rules.json` somewhere accessible. Set the path by editing the curl'd skill file and hardcoding the repo path, or clone the repo and point to it.
