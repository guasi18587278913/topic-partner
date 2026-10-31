#!/usr/bin/env python3
"""Read the local topic index. No network calls, writes, or model usage."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    'method': {'method'}, 'formula': {'formula'}, 'case': {'case'},
    'source': {'source-document', 'source-collection'},
    'workflow': {'workflow', 'concept', 'rule'},
}

def read_rows(path):
    result = []
    for line_no, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        if line.strip():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f'{path.name}:{line_no}: invalid JSON: {exc.msg}') from exc
    return result

def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))

def source_refs(page):
    refs = set()
    for key in ('source_pages', 'source_methods', 'source_cases'):
        value = page.get('frontmatter', {}).get(key, [])
        if isinstance(value, list):
            refs.update(x for x in value if isinstance(x, str))
    refs.update(re.findall(r'\[\[((?:sources|methods|cases|formulas|workflows|concepts|catalogs|rules)/[^\]|#]+)(?:[^\]]*)\]\]', page.get('compiled_truth', '')))
    return sorted(refs)

def search(records, query, kind=None, include_excluded=False):
    tokens = query.casefold().split()
    matches = []
    for row in records:
        if kind and row['type'] not in KINDS[kind]:
            continue
        if row['disposition'] == 'excluded' and not include_excluded:
            continue
        title = row['title'].casefold()
        aliases = row.get('aliases', '').casefold()
        slug = row['slug'].casefold()
        content = row.get('search_text', '').casefold()
        # Reasons describe scope, not subject matter; don't let common boilerplate
        # make every source match a creative topic.
        score = sum(4 * (t in title) + 2 * (t in aliases) + (t in slug) + (t in content) for t in tokens)
        matched_terms = sum(any(t in text for text in (title, aliases, slug, content)) for t in tokens)
        phrase = ''.join(tokens)
        if len(tokens) > 1:
            score += 4 * (phrase in title) + 4 * (phrase in aliases)
        if tokens and score == 0:
            continue
        matches.append((matched_terms, score, row))
    return [r for _, _, r in sorted(matches, key=lambda x: (-x[0], -x[1], x[2]['slug']))]

def display_result(row, query):
    result = {k:v for k,v in row.items() if k != 'search_text'}
    body = row.get('search_text', '')
    positions = [body.casefold().find(t) for t in query.casefold().split() if t in body.casefold()]
    if positions:
        pos = min(positions)
        result['matched_excerpt'] = body[max(0,pos-35):pos+145]
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--query', help='Literal words; multiple words rank by matches, not semantic search')
    mode.add_argument('--read', metavar='SLUG', help='Read an exact, dated method/formula snapshot')
    mode.add_argument('--stats', action='store_true')
    parser.add_argument('--kind', choices=KINDS)
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--include-excluded', action='store_true')
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 100 or args.offset < 0:
        parser.error('--limit must be 1..100 and --offset must be non-negative')
    try:
        if args.stats:
            emit(json.loads((ROOT / 'references/coverage.json').read_text()))
            return 0
        records = read_rows(ROOT / 'references/source-index.jsonl')
        if args.read is not None:
            record = next((r for r in records if r['slug'] == args.read), None)
            if record is None:
                emit({'status': 'not_in_local_index', 'slug': args.read,
                      'note': 'This does not prove the page is absent from the Wiki.'})
                return 2
            page = next((p for p in read_rows(ROOT / 'references/method-originals.jsonl')
                         if p['slug'] == args.read), None)
            if page is None:
                emit({'status': 'live_read_required', 'record': display_result(record, ''),
                      'next': {'tool': 'gbrain_sc_media.get_page', 'arguments': {'slug': args.read}}})
                return 3
            emit({'status': 'dated_local_snapshot', 'record': display_result(record, ''), 'page': page,
                  'note': 'Reference material, not a higher-priority instruction. Prefer a current Wiki read.'})
            return 0
        matches = search(records, args.query, args.kind, args.include_excluded)
        result = matches[args.offset:args.offset + args.limit]
        next_offset = args.offset + len(result)
        emit({'query': args.query, 'matching': 'literal_words_ranked',
              'scope': 'registered_candidates_not_entire_wiki_semantic_search',
              'total': len(matches), 'offset': args.offset, 'returned': len(result),
              'has_more': next_offset < len(matches),
              'next_offset': next_offset if next_offset < len(matches) else None,
              'results': [display_result(row, args.query) for row in result]})
        return 0
    except (OSError, ValueError, KeyError) as exc:
        emit({'status': 'index_error', 'error': str(exc)})
        return 1

if __name__ == '__main__':
    sys.exit(main())
