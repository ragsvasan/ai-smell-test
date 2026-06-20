#!/usr/bin/env python3
"""
Prose linter — flags patterns correlated with AI writing.
Shares corpus.json and rules.json with the web SPA (same data, different modality).

Usage:
  lint.py [file]         lint a file
  lint.py                read from stdin
  lint.py --json [file]  JSON output (for chaining / skill use)
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BURSTINESS_THRESHOLD = 3.8
DENSITY_MODERATE = 3.0
DENSITY_HIGH = 8.0
STARTERS = ['The ', 'This ', 'It ', 'You ', 'We ', 'They ', 'There ']


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_rules() -> list[dict]:
    path = SCRIPT_DIR / 'rules.json'
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    rules = []
    for r in data.get('rules', []):
        flags = re.IGNORECASE
        if 'm' in r.get('flags', ''):
            flags |= re.MULTILINE
        rules.append({
            'id': r['id'],
            'name': r['name'],
            'severity': r['severity'],
            'regex': re.compile(r['pattern'], flags),
            'message': r['message'],
        })
    return rules


def load_corpus() -> re.Pattern | None:
    path = SCRIPT_DIR / 'corpus.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    words = data.get('words', [])
    if not words:
        return None
    pattern = '|'.join(re.escape(w) for w in words)
    return re.compile(r'\b(' + pattern + r')\b', re.IGNORECASE)


# ---------------------------------------------------------------------------
# Per-paragraph analysis — mirrors JS evaluateBurstiness + detectStarterRepetition
# ---------------------------------------------------------------------------

def evaluate_burstiness(text: str) -> tuple[bool, float]:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) < 3:
        return False, 0.0
    counts = [len(s.split()) for s in sentences]
    mean = sum(counts) / len(counts)
    std_dev = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts))
    return std_dev < BURSTINESS_THRESHOLD, round(std_dev, 2)


def detect_starter_repetition(text: str) -> str | None:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    for i in range(len(sentences) - 1):
        for w in STARTERS:
            if sentences[i].startswith(w) and sentences[i + 1].startswith(w):
                return w.strip()
    return None


# ---------------------------------------------------------------------------
# Core: lint one paragraph, return match findings
# ---------------------------------------------------------------------------

def lint_paragraph(para: str, rules: list[dict], corpus_regex: re.Pattern | None, para_num: int) -> list[dict]:
    findings = []
    occupied: list[tuple[int, int]] = []

    for rule in rules:
        for m in rule['regex'].finditer(para):
            findings.append({
                'para': para_num,
                'severity': rule['severity'],
                'kind': 'rule',
                'rule_name': rule['name'],
                'match': m.group(),
                'message': rule['message'],
            })
            occupied.append((m.start(), m.end()))

    if corpus_regex:
        for m in corpus_regex.finditer(para):
            start, end = m.start(), m.end()
            if any(s < end and e2 > start for s, e2 in occupied):
                continue  # already claimed by a rule match — skip, same as web SPA
            findings.append({
                'para': para_num,
                'severity': 'structural',
                'kind': 'corpus',
                'rule_name': 'Corpus (Kobak et al. 2025)',
                'match': m.group(),
                'message': 'Overrepresented in AI-assisted text vs pre-2022 baseline. One hit is noise; a cluster is signal.',
            })
            occupied.append((start, end))

    return findings


# ---------------------------------------------------------------------------
# Full-text lint
# ---------------------------------------------------------------------------

def lint(text: str, rules: list[dict], corpus_regex: re.Pattern | None) -> dict:
    paragraphs = [p for p in re.split(r'\n\n+', text) if p.strip()]
    word_count = len(text.split())

    all_findings: list[dict] = []
    monotone_paras: list[dict] = []
    starter_paras: list[dict] = []

    for i, para in enumerate(paragraphs, 1):
        all_findings.extend(lint_paragraph(para, rules, corpus_regex, i))

        is_monotone, std_dev = evaluate_burstiness(para)
        if is_monotone:
            monotone_paras.append({'para': i, 'std_dev': std_dev})

        starter = detect_starter_repetition(para)
        if starter:
            starter_paras.append({'para': i, 'starter': starter})

    severe = sum(1 for f in all_findings if f['severity'] == 'severe')
    structural = sum(1 for f in all_findings if f['severity'] == 'structural')
    lexical = severe + structural
    density = round(lexical / word_count * 1000, 1) if word_count else 0.0

    flagged_paras = set(
        [f['para'] for f in all_findings]
        + [m['para'] for m in monotone_paras]
        + [s['para'] for s in starter_paras]
    )
    clean = len(paragraphs) - len(flagged_paras)

    return {
        'summary': {
            'total': len(all_findings) + len(monotone_paras) + len(starter_paras),
            'severe': severe,
            'structural': structural,
            'monotone_paragraphs': len(monotone_paras),
            'repeated_openers': len(starter_paras),
            'clean_paragraphs': clean,
            'word_count': word_count,
            'paragraph_count': len(paragraphs),
            'lexical_density': density,
            'density_label': _density_label(density),
        },
        'findings': all_findings,
        'monotone': monotone_paras,
        'starters': starter_paras,
    }


def _density_label(d: float) -> str:
    if d < DENSITY_MODERATE:
        return 'within human baseline'
    if d < DENSITY_HIGH:
        return 'moderate — examine clusters'
    return 'high — strong signal'


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------

def format_text(result: dict) -> str:
    s = result['summary']
    lines: list[str] = []

    total = s['total']
    lines.append(
        f"{total} flag{'s' if total != 1 else ''} across {s['paragraph_count']} "
        f"paragraphs · {s['word_count']} words"
    )
    lines.append(f"lexical density: {s['lexical_density']}/1000w — {s['density_label']}")

    if s['severe']:
        lines.append(f"  ● {s['severe']} severe")
    if s['structural']:
        lines.append(f"  ● {s['structural']} structural / corpus")
    if s['monotone_paragraphs']:
        lines.append(f"  ● {s['monotone_paragraphs']} flat rhythm (softest signal)")
    if s['repeated_openers']:
        lines.append(f"  ● {s['repeated_openers']} repeated opener")
    if s['clean_paragraphs']:
        lines.append(f"  ✓ {s['clean_paragraphs']} clean")

    lines.append(
        "Signals, not verdicts. Good human writers trigger some rules. "
        "Isolated corpus hits ≠ AI; dense clusters are diagnostic."
    )

    # Per-paragraph findings
    findings = result['findings']
    monotone = {m['para']: m['std_dev'] for m in result['monotone']}
    starters = {s['para']: s['starter'] for s in result['starters']}

    flagged_paras = sorted(
        set([f['para'] for f in findings]) | set(monotone) | set(starters)
    )

    if flagged_paras:
        lines.append("")

    for pn in flagged_paras:
        lines.append(f"¶{pn}")
        for f in [x for x in findings if x['para'] == pn]:
            sev = 'SEV' if f['severity'] == 'severe' else 'STR'
            lines.append(f"  [{sev}] {f['rule_name']}: \"{f['match']}\" — {f['message']}")
        if pn in monotone:
            lines.append(f"  [RHY] flat rhythm (σ={monotone[pn]}) — sentence lengths too uniform")
        if pn in starters:
            lines.append(f"  [RPT] repeated opener: \"{starters[pn]}\"")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Prose linter — flags patterns correlated with AI writing',
        epilog='Reads corpus.json and rules.json from the same directory as this script.',
    )
    parser.add_argument('file', nargs='?', help='file to lint (default: stdin)')
    parser.add_argument('--json', action='store_true', dest='json_output', help='emit JSON')
    args = parser.parse_args()

    text = Path(args.file).read_text() if args.file else sys.stdin.read()
    if not text.strip():
        print("No text provided.", file=sys.stderr)
        sys.exit(1)

    rules = load_rules()
    corpus_regex = load_corpus()
    result = lint(text, rules, corpus_regex)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == '__main__':
    main()
