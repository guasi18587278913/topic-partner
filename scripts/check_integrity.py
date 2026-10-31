#!/usr/bin/env python3
"""Check source traceability and resource links; this is not a quality score."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from lookup import ROOT, read_rows, source_refs

def main():
    errors = []
    index = read_rows(ROOT / 'references/source-index.jsonl')
    originals = read_rows(ROOT / 'references/method-originals.jsonl')
    coverage = json.loads((ROOT / 'references/coverage.json').read_text())
    by_slug = {p['slug']: p for p in index}
    for row in index:
        for source in row.get('editorial_notes', {}).get('sources', []):
            if source not in by_slug:
                errors.append(f'unregistered editorial source: {row["slug"]} -> {source}')
    if len(by_slug) != len(index):
        errors.append('duplicate source slugs')
    if len({p['slug'] for p in originals}) != len(originals):
        errors.append('duplicate snapshot slugs')
    for p in originals:
        s = p['slug']
        if s not in by_slug:
            errors.append(f'unregistered snapshot: {s}')
            continue
        digest = hashlib.sha256(p['compiled_truth'].encode()).hexdigest()
        if digest != p['body_sha256'] or digest != by_slug[s]['body_sha256']:
            errors.append(f'body fingerprint mismatch: {s}')
        if p['wiki_content_hash'] != by_slug[s]['wiki_content_hash']:
            errors.append(f'Wiki fingerprint mismatch: {s}')
        if by_slug[s]['disposition'] == 'excluded':
            errors.append(f'excluded method packed as an active snapshot: {s}')
        refs = source_refs(p)
        if refs != p.get('source_refs', []) or refs != by_slug[s].get('source_refs', []):
            errors.append(f'source edge list mismatch: {s}')
        for ref in refs:
            if ref not in by_slug:
                errors.append(f'unregistered snapshot source edge: {s} -> {ref}')
    expected = {r['slug'] for r in index if r['type'] in {'method','formula'}
                and r['disposition'] != 'excluded' and r['retrieved_body']}
    if expected != {p['slug'] for p in originals}:
        errors.append('an included retrieved method/formula snapshot was lost or added')
    if coverage['registered_candidates'] != len(index):
        errors.append('candidate count mismatch')
    if coverage['local_unabridged_snapshots'] != len(originals):
        errors.append('snapshot count mismatch')
    if coverage['dispositions'] != dict(Counter(r['disposition'] for r in index)):
        errors.append('disposition count mismatch')
    if coverage.get('unknown_source_edges'):
        errors.extend(f'unknown source edge in corpus: {s}' for s in coverage['unknown_source_edges'])
    wiki_pattern = re.compile(r'(?:sources|methods|cases|formulas|workflows|concepts|catalogs|rules)/[a-zA-Z0-9_./-]+')
    file_links = 0
    wiki_refs = set()
    markdown = [ROOT/'SKILL.md', *(ROOT/'references').glob('*.md')]
    for p in markdown:
        body = p.read_text()
        if '[TODO' in body:
            errors.append(f'unfinished scaffold: {p.name}')
        for target in re.findall(r'\]\(([^)]+)\)', body):
            if '://' in target or target.startswith('#'):
                continue
            relative = target.split('#',1)[0]
            if relative and not (p.parent/relative).is_file():
                errors.append(f'broken file link: {p.name} -> {target}')
            file_links += 1
        for slug in wiki_pattern.findall(body):
            if slug.endswith('/'):
                continue
            slug = slug.rstrip('.')
            wiki_refs.add(slug)
            if slug not in by_slug:
                errors.append(f'unknown Wiki reference: {p.name} -> {slug}')
    result = {'status': 'passed' if not errors else 'failed',
              'sources': len(index), 'snapshots': len(originals),
              'markdown_files': len(markdown), 'local_links': file_links,
              'explicit_wiki_refs': len(wiki_refs), 'errors': errors,
              'limitation': 'Integrity only; does not prove creative quality or platform performance.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
